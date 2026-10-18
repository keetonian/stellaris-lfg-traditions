#!/usr/bin/env bash
# Copies mod/ into the Stellaris user mod folder and writes the launcher's .mod file,
# so the mod shows up in the Paradox launcher for local testing.
#
# By default this installs a LOCAL DEV copy, so it can't be confused with the Workshop version you're subscribed to:
#   - " [LOCAL DEV]" is appended to the mod name (in both the installed descriptor.mod and the launcher .mod file)
#   - remote_file_id is removed, so the launcher treats it as a separate mod from the Steam subscription
# mod/descriptor.mod in the repo is never changed, and scripts/publish.sh uploads from mod/, not from this copy.
#
# RELEASE=1 installs an exact copy (real name, remote_file_id kept). Use it only to upload with the launcher's "Upload mod".
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MOD_ROOT="${STELLARIS_MOD_DIR:-$HOME/Documents/Paradox Interactive/Stellaris/mod}"
MOD_NAME="lfg_traditions"
DEST="$MOD_ROOT/$MOD_NAME"
DEV_SUFFIX=" [LOCAL DEV]"

[ -d "$MOD_ROOT" ] || { echo "install.sh: Stellaris mod folder not found: $MOD_ROOT" >&2; exit 1; }

# Keep a remote_file_id the launcher wrote after a launcher upload, so we don't wipe it.
if [ -f "$DEST/descriptor.mod" ] && grep -q '^remote_file_id=' "$DEST/descriptor.mod" \
	&& ! grep -q '^remote_file_id=' "$REPO_DIR/mod/descriptor.mod"; then
	echo "install.sh: the installed descriptor has $(grep '^remote_file_id=' "$DEST/descriptor.mod")" >&2
	echo "install.sh: copy that line into mod/descriptor.mod first, then rerun." >&2
	exit 1
fi

# The descriptor as installed: dev-labelled and unlinked from Steam, unless RELEASE=1.
descriptor() {
	if [ "${RELEASE:-0}" = 1 ]; then
		cat "$REPO_DIR/mod/descriptor.mod"
	else
		sed -e '/^remote_file_id=/d' -e "s/^name=\"\(.*\)\"/name=\"\1$DEV_SUFFIX\"/" "$REPO_DIR/mod/descriptor.mod"
	fi
}

mkdir -p "$DEST"
rsync -a --delete --exclude '.DS_Store' "$REPO_DIR/mod/" "$DEST/"
descriptor > "$DEST/descriptor.mod"
{
	descriptor
	printf 'path="%s"\n' "$DEST"
} > "$MOD_ROOT/$MOD_NAME.mod"

echo "Installed $(sed -n 's/^name=//p' "$DEST/descriptor.mod") to $DEST"
echo "Launcher descriptor: $MOD_ROOT/$MOD_NAME.mod"
