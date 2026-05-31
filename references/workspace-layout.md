# Workspace Layout

This skill ships a ready-to-copy workspace template in `assets/workspace-template/`.

## Included

- conversational onboarding instructions
- advanced local config editor and server
- config schema and loader
- anonymized `USER.md` template
- default `知识结构/` knowledge workspace
- memory scaffolding
- `content-hot-tracker`
- `bibi` workflow skill

## Expected First-Run State

- `config.example.yaml` exists
- `config.yaml` does not exist
- `USER.md` is still the anonymized example template
- `知识结构/` exists with `知识体系/`, `竞品素材/`, `热点素材/`, and `历史文章/`
- `memory/` contains only long-lived scaffolding such as `learnings/LEARNINGS.md`

## Runtime Expectations

- first-run users complete onboarding through chat by following `references/chat-onboarding.md`
- chat onboarding writes a real `config.yaml` after user confirmation
- the same save rewrites `USER.md`
- the same save creates `memory/YYYY-MM-DD.md`
- local storage defaults to `./知识结构` so users can start before they have a mature personal knowledge system
- `config-server.mjs` remains available for advanced editing, import/export, and debugging

## Onboarding Entry Points

Use chat onboarding when:

- no real `config.yaml` exists
- `config.yaml` exists but critical fields are missing
- the user asks to start onboarding, initialize the content workflow, configure the skill, restart setup, or test chat onboarding

Use the web config editor when:

- the user prefers a visual onboarding page
- the user asks for advanced editing
- the user wants to inspect the full config
- the user wants import/export YAML or JSON
- the user is debugging config structure
