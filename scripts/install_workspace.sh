#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: scripts/install_workspace.sh /path/to/target-workspace" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_DIR="$SKILL_DIR/assets/workspace-template"
TARGET_DIR="$1"

if [[ ! -d "$TEMPLATE_DIR" ]]; then
  echo "Template directory not found: $TEMPLATE_DIR" >&2
  exit 1
fi

mkdir -p "$(dirname "$TARGET_DIR")"
TARGET_DIR="$(cd "$(dirname "$TARGET_DIR")" && pwd -P)/$(basename "$TARGET_DIR")"

if [[ -e "$TARGET_DIR" ]] && [[ -n "$(find "$TARGET_DIR" -mindepth 1 -maxdepth 1 2>/dev/null)" ]]; then
  echo "Target directory is not empty: $TARGET_DIR" >&2
  exit 1
fi

mkdir -p "$TARGET_DIR"

if command -v rsync >/dev/null 2>&1; then
  rsync -a --exclude='__pycache__/' --exclude='*.pyc' --exclude='.DS_Store' "$TEMPLATE_DIR"/ "$TARGET_DIR"/
else
  cp -R "$TEMPLATE_DIR"/. "$TARGET_DIR"
  find "$TARGET_DIR" \( -name '__pycache__' -type d -o -name '*.pyc' -type f -o -name '.DS_Store' -type f \) -prune -exec rm -rf {} + 2>/dev/null || true
fi

echo "Workspace installed at: $TARGET_DIR"
echo "Next steps:"
echo "1. cd \"$TARGET_DIR\""
echo "2. Start chat onboarding with the agent; no web server is required."
echo "3. Optional visual editor: run 'node config-server.mjs' and open http://127.0.0.1:8765/ when you want a page-based editor."
echo "Use the printed path above for follow-up commands on macOS."
