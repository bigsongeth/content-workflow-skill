#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: scripts/validate_workspace.sh /path/to/workspace" >&2
  exit 1
fi

WORKSPACE_INPUT="$1"
WORKSPACE_DIR="$WORKSPACE_INPUT"

if [[ ! -d "$WORKSPACE_DIR" ]]; then
  if [[ "$WORKSPACE_INPUT" == /private/tmp/* ]]; then
    ALT_PATH="/tmp/${WORKSPACE_INPUT#/private/tmp/}"
  elif [[ "$WORKSPACE_INPUT" == /tmp/* ]]; then
    ALT_PATH="/private/tmp/${WORKSPACE_INPUT#/tmp/}"
  else
    ALT_PATH=""
  fi

  if [[ -n "$ALT_PATH" ]] && [[ -d "$ALT_PATH" ]]; then
    WORKSPACE_DIR="$ALT_PATH"
  else
    echo "Workspace not found: $WORKSPACE_INPUT" >&2
    exit 1
  fi
fi

required_files=(
  "AGENTS.md"
  "USER.md"
  "config.example.yaml"
  "config.schema.json"
  "config-server.mjs"
  "config_loader.py"
  "ONBOARDING_FLOW.md"
  "ACTIVATION_AND_BILLING.md"
  "SKILL_RUNTIME_FLOW.md"
  "TEST_ONBOARDING.md"
  "知识结构/知识体系/README.md"
  "知识结构/竞品素材/README.md"
  "知识结构/热点素材/README.md"
  "知识结构/历史文章/README.md"
  "skills/content-hot-tracker/rebang_fetcher.py"
  "bibigpt-skill/skills/bibi/SKILL.md"
)

for rel in "${required_files[@]}"; do
  if [[ ! -e "$WORKSPACE_DIR/$rel" ]]; then
    echo "Missing required file: $rel" >&2
    exit 1
  fi
done

if [[ -f "$WORKSPACE_DIR/config.yaml" ]]; then
  echo "Unexpected runtime config present: $WORKSPACE_DIR/config.yaml" >&2
  exit 1
fi

echo "Structure check passed."

if python3 - <<'PY' >/dev/null 2>&1
import requests, yaml, jsonschema
PY
then
  output="$(PYTHONDONTWRITEBYTECODE=1 python3 "$WORKSPACE_DIR/skills/content-hot-tracker/rebang_fetcher.py" weibo 2>&1 || true)"
  if grep -q "Start chat onboarding first" <<<"$output"; then
    echo "Runtime smoke check passed."
  else
    echo "Runtime smoke check did not produce the expected onboarding prompt." >&2
    echo "$output" >&2
    exit 1
  fi
else
  echo "Skipped runtime smoke check because Python dependencies are not installed."
fi
