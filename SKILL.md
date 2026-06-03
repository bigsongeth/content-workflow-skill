---
name: content-workflow-workspace-chat-onboarding
description: >
  Scaffold, validate, and test a reusable content-workflow workspace with
  conversational first-run onboarding for self-media/content operations.
  Use when the user wants to install a reusable content-operation skill package,
  create a clean workspace template for another agent, test chat onboarding,
  test first-run onboarding, or provision a repo that writes config.yaml,
  USER.md, and memory logs together. Triggers: "install this skill",
  "set up a content workflow workspace", "bootstrap onboarding",
  "test onboarding", "test chat onboarding", "make a clean agent-ready copy",
  "搭一个内容工作流 skill", "安装这个 skill", "测试 onboarding", "聊天式 onboarding",
  "给其他 Agent 一个干净副本".
---

# Content Workflow Workspace

This skill packages a reusable self-media/content-workflow workspace that supports:

- paid activation through a seller-controlled Content Workflow Gateway and customer Token
- context-aware conversational onboarding for user profile, account positioning, storage, workflow, and collaboration rules
- a default local `知识结构/` workspace for users who do not yet have their own knowledge system
- advanced local config editing through `config-server.mjs`
- config-driven runtime behavior
- synchronized writes to `config.yaml`, `USER.md`, and `memory/YYYY-MM-DD.md`
- bundled content skills such as hot-topic tracking and video summarization

## Default Onboarding Mode

Use **chat onboarding first**. Do not start the web config server by default.

When the installed workspace has no real `config.yaml`, or `config.yaml` is missing critical fields, guide the user through `references/chat-onboarding.md` before running user-dependent content workflows.

During onboarding, briefly mention that a visual onboarding/config editor is available for users who prefer a page-based editor, but do not require it. Start `node config-server.mjs` only when the user explicitly asks to open the editor, inspect full YAML, import/export config, or debug advanced settings.

## Quick Start

If the user wants a fresh workspace, run:

```bash
scripts/install_workspace.sh /path/to/target-workspace
```

This copies the bundled workspace template from `assets/workspace-template/`.

The install script is intentionally fast and dependency-light: it only copies the template, skips runtime caches when possible, and leaves actual user configuration to chat onboarding.

## Common Tasks

- **Install a clean workspace**: use `scripts/install_workspace.sh`
- **Validate package structure**: use `scripts/validate_workspace.sh`
- **Run paid activation**: follow `assets/workspace-template/ACTIVATION_AND_BILLING.md` and verify `GET /v1/entitlements/me`
- **Use multi-platform content fetch**: follow `references/content-fetch-api.md` (`GET /v1/content/fetch`, supports 小红书/抖音/微博/B站/公众号/视频号/快手/知乎)
- **Run conversational onboarding**: follow `references/chat-onboarding.md` and `assets/workspace-template/ONBOARDING_FLOW.md`
- **Understand packaged files**: read `references/workspace-layout.md`
- **Manually test onboarding**: read `references/testing.md`
- **Optional visual onboarding/config editor**: run `node config-server.mjs` inside the installed workspace only when the user wants the page

## Operating Rules

- Treat `assets/workspace-template/` as the distributable source of truth.
- Do not write real secrets into template files or generated configs.
- Prefer `config.yaml` over `config.example.yaml` at runtime.
- If there is no real `config.yaml`, first perform activation/entitlement check, then start context-aware conversational onboarding instead of running user-dependent skills directly.
- If a real `config.yaml` exists but critical fields are missing, ask only for the missing fields and then resave artifacts.
- Before writing onboarding results, summarize the proposed config and ask the user to confirm.
- After onboarding completes, offer a small next-step menu such as hot-topic tracking, draft writing, video teardown, style rewrite, or weekly content planning.

## Validation

After installing to a target directory:

1. Run `scripts/validate_workspace.sh /path/to/target-workspace`
2. If structure is valid, follow `references/testing.md` to complete conversational onboarding
3. Confirm that saving config also updates `USER.md` and `memory/YYYY-MM-DD.md`
4. Confirm `python3 skills/content-hot-tracker/rebang_fetcher.py weibo` runs after onboarding
