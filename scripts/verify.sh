#!/usr/bin/env bash
# Runs the test suite and the static mod check. Extra args go to tools/check_mod.py
# (e.g. --require-sources before a release, --snapshot-only to ignore the local modifiers.log).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -I -m unittest discover -s tests
python3 -I tools/check_mod.py "$@"
