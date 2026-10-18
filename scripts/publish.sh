#!/usr/bin/env bash
# Verifies mod/ and uploads it to the Steam Workshop with steamcmd (no Paradox launcher needed).
#
#   STEAM_USER=<steam login> scripts/publish.sh ["change note"]
#
# - First upload (no remote_file_id in mod/descriptor.mod) creates a new Workshop item, with
#   visibility PRIVATE unless VISIBILITY is set, and writes the new remote_file_id back into
#   mod/descriptor.mod (commit it).
# - Later uploads update that item. The Steam description is always replaced with workshop_description.txt
#   (SYNC_DESCRIPTION=0 to leave Steam's text alone); title/visibility are left alone unless VISIBILITY=... is given.
# - steamcmd asks for your password and Steam Guard code the first time, then caches the login.
#   Credentials are never stored by this repo.
#
# Env: STEAM_USER (required), VISIBILITY (0 public, 1 friends-only, 2 private, 3 unlisted),
#      SYNC_DESCRIPTION=0 (don't push workshop_description.txt), DRY_RUN=1 (stage + print VDF, no upload),
#      ALLOW_DIRTY=1 (skip the clean-git-tree check), STEAMCMD (path to steamcmd).
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
export MOD_DIR="${MOD_DIR:-$REPO_DIR/mod}"
DESCRIPTION_FILE="${DESCRIPTION_FILE:-$REPO_DIR/workshop_description.txt}"
D="$MOD_DIR/descriptor.mod"
APP_ID=281990
STEAMCMD="${STEAMCMD:-$(command -v steamcmd || true)}"

die() { echo "publish.sh: error: $*" >&2; exit 1; }
field() { { grep -E "^$1=" "$D" || true; } | head -1 | sed -E 's/^[^=]*="?([^"]*)"?.*/\1/' | tr -d '\r'; }
# steamcmd's VDF parser has no escape sequences: a `"` inside a value always ends the string
# (and `\"` doesn't help). So turn "pairs" into “typographic quotes” and any leftover `"` into ”.
vdf_value() { sed -e 's/"\([^"]*\)"/“\1”/g' -e 's/"/”/g'; }

[ "${DRY_RUN:-0}" = 1 ] || [ -n "${STEAM_USER:-}" ] || die "set STEAM_USER to your Steam login name"
[ "${DRY_RUN:-0}" = 1 ] || [ -n "$STEAMCMD" ] || die "steamcmd not found (macOS: brew install --cask steamcmd)"

# 1. Verify: tests + full static check, including checks that need the installed game and Giga.
#    (PUBLISH_SKIP_TESTS=1 is only for tests/test_publish.py, which would otherwise recurse.)
echo "== Verifying"
if [ "${PUBLISH_SKIP_TESTS:-0}" != 1 ]; then
	(cd "$REPO_DIR" && python3 -I -m unittest discover -s tests)
fi
python3 -I "$REPO_DIR/tools/check_mod.py" --mod "$MOD_DIR" --require-sources

# 2. Only publish committed content, so every Workshop version maps to a git commit.
if [ "${ALLOW_DIRTY:-0}" != 1 ] && [ -n "$(git -C "$REPO_DIR" status --porcelain -- mod)" ]; then
	die "mod/ has uncommitted changes; commit them first (or ALLOW_DIRTY=1)"
fi

# Steam rejects the whole update ("Invalid Parameter" at commit) if the description is over 8000 characters.
desc_chars="$(python3 -I -c 'import sys; print(len(open(sys.argv[1], encoding="utf-8").read()))' "$DESCRIPTION_FILE")"
if [ "$desc_chars" -gt "${STEAM_DESCRIPTION_LIMIT:-8000}" ]; then
	die "$DESCRIPTION_FILE is $desc_chars characters; Steam allows ${STEAM_DESCRIPTION_LIMIT:-8000}"
fi

file_id="$(field remote_file_id)"
version="$(field version)"
commit="$(git -C "$REPO_DIR" rev-parse --short HEAD 2>/dev/null || echo uncommitted)"
note="${1:-v$version ($commit)}"
if [ -z "$file_id" ]; then
	file_id=0
	VISIBILITY="${VISIBILITY:-2}"
	SYNC_DESCRIPTION=1
	echo "== No remote_file_id: this creates a NEW Workshop item (visibility $VISIBILITY)"
else
	echo "== Updating Workshop item $file_id"
fi

# 3. Stage a clean copy (exactly what verify checked, minus OS junk).
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
mkdir -p "$STAGE/content"
rsync -a --exclude '.DS_Store' "$MOD_DIR/" "$STAGE/content/"

VDF="$STAGE/item.vdf"
{
	echo '"workshopitem"'
	echo '{'
	printf '\t"appid"\t\t"%s"\n' "$APP_ID"
	printf '\t"publishedfileid"\t"%s"\n' "$file_id"
	printf '\t"contentfolder"\t"%s"\n' "$STAGE/content"
	printf '\t"previewfile"\t"%s"\n' "$STAGE/content/thumbnail.png"
	printf '\t"changenote"\t"%s"\n' "$(printf '%s' "$note" | vdf_value)"
	if [ "$file_id" = 0 ]; then
		printf '\t"title"\t\t"%s"\n' "$(field name | vdf_value)"
	fi
	if [ -n "${VISIBILITY:-}" ]; then
		printf '\t"visibility"\t"%s"\n' "$VISIBILITY"
	fi
	if [ "${SYNC_DESCRIPTION:-1}" = 1 ]; then
		printf '\t"description"\t"%s"\n' "$(vdf_value < "$DESCRIPTION_FILE")"
	fi
	echo '}'
} > "$VDF"

echo "== Staged content:"; (cd "$STAGE/content" && find . -type f | sort | sed 's/^/   /')
if [ "${DRY_RUN:-0}" = 1 ]; then
	echo "== DRY_RUN: would run steamcmd with:"; cat "$VDF"
	exit 0
fi

# 4. Upload. steamcmd writes the new publishedfileid back into the VDF on first creation.
echo "== Uploading with steamcmd as $STEAM_USER"
"$STEAMCMD" +login "$STEAM_USER" +workshop_build_item "$VDF" +quit

new_id="$(sed -nE 's/^[[:space:]]*"publishedfileid"[[:space:]]*"([0-9]+)".*/\1/p' "$VDF")"
[ -n "$new_id" ] && [ "$new_id" != 0 ] || die "upload did not report a Workshop item id; check steamcmd output above"

if [ "$file_id" = 0 ]; then
	printf 'remote_file_id="%s"\n' "$new_id" >> "$D"
	echo "== Created Workshop item $new_id; added remote_file_id to mod/descriptor.mod. Commit it."
	echo "   Then add Gigastructural Engineering as a Required item on the Workshop page."
fi
echo "== Done: https://steamcommunity.com/sharedfiles/filedetails/?id=$new_id"
