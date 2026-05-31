# Testing

## Install

```bash
scripts/install_workspace.sh /path/to/test-workspace
```

On macOS, keep using the exact absolute path printed by the installer if it resolves `/tmp/...` to `/private/tmp/...`.

## Smoke Check

```bash
scripts/validate_workspace.sh /path/to/test-workspace
```

## Conversational Onboarding Test

Inside the installed workspace, confirm there is no real `config.yaml`. Then follow `references/chat-onboarding.md`:

1. Start with the standard opening message.
2. Ask the six fast onboarding questions one at a time.
3. Accept informal answers and map them into the config schema.
4. Summarize the proposed workflow in human language.
5. Ask for confirmation before writing files.
6. After confirmation, write `config.yaml`, rewrite `USER.md`, and create `memory/YYYY-MM-DD.md`.
7. Offer the next-step menu.

Use fake, non-sensitive user data during tests.

## Advanced Web Editor Test

Only run the server when testing the advanced editor path or when the user explicitly asks for it:

```bash
node config-server.mjs
```

Then open `http://127.0.0.1:8765/` and edit/save config.

## Pass Criteria

- conversational onboarding can complete without opening the web server
- proposed config is summarized before writing
- saving config creates `config.yaml`
- `USER.md` is rewritten from template into the current user's summary
- `memory/YYYY-MM-DD.md` is created
- installed workspace includes `知识结构/知识体系`, `知识结构/竞品素材`, `知识结构/热点素材`, and `知识结构/历史文章`
- skipped fields appear in `onboarding.missing_fields`
- visual editor remains available as an optional path
- `python3 skills/content-hot-tracker/rebang_fetcher.py weibo` runs after onboarding
