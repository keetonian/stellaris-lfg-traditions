#!/usr/bin/env bash
# Copies mod/ into the Stellaris user mod folder and writes the launcher's .mod file,
# so the mod shows up in the Paradox launcher for local testing and uploading.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MOD_ROOT="${STELLARIS_MOD_DIR:-$HOME/Documents/Paradox Interactive/Stellaris/mod}"
MOD_NAME="lfg_traditions"
DEST="$MOD_ROOT/$MOD_NAME"

[ -d "$MOD_ROOT" ] || { echo "install.sh: Stellaris mod folder not found: $MOD_ROOT" >&2; exit 1; }

# Keep a remote_file_id the launcher wrote after an upload, so we don't wipe it.
if [ -f "$DEST/descriptor.mod" ] && grep -q '^remote_file_id=' "$DEST/descriptor.mod" \
	&& ! grep -q '^remote_file_id=' "$REPO_DIR/mod/descriptor.mod"; then
	echo "install.sh: the installed descriptor has $(grep '^remote_file_id=' "$DEST/descriptor.mod")" >&2
	echo "install.sh: copy that line into mod/descriptor.mod first, then rerun." >&2
	exit 1
fi

mkdir -p "$DEST"
rsync -a --delete --exclude '.DS_Store' "$REPO_DIR/mod/" "$DEST/"
{
	cat "$REPO_DIR/mod/descriptor.mod"
	printf 'path="%s"\n' "$DEST"
} > "$MOD_ROOT/$MOD_NAME.mod"

echo "Installed to $DEST"
echo "Launcher descriptor: $MOD_ROOT/$MOD_NAME.mod"
