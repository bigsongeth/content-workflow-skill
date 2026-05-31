# Conversational Onboarding

Use this workflow when a content-workflow workspace has no real `config.yaml`, when critical fields are missing, or when the user explicitly asks to start/restart onboarding.

The goal is to make the user feel like they are talking to a content partner, not filling out an admin form. Ask natural questions, accept messy answers, fill safe defaults, and only expose YAML after the user asks for advanced editing.

## What to Tell the User First

Start with a short explanation:

> 我先用几个问题快速了解你的内容工作流。你可以随便说，不需要按格式填写；我会帮你整理成配置。
>
> 完成后我会生成三份东西：
> - `config.yaml`：给 Skill 运行用的结构化配置
> - `USER.md`：给 Agent 看的用户画像摘要
> - `memory/YYYY-MM-DD.md`：记录这次 onboarding 的完成情况和待补项
>
> 不要提供 token、密码、密钥、手机号、身份证等敏感信息。如果需要外部平台集成，我只会记录环境变量名，不保存密钥明文。
>
> 不确定的问题可以直接说“跳过”，我会先用安全默认值，并把待补项记录下来。

Then optionally add one short sentence:

> 如果你更喜欢图形化页面，也可以让我打开本地 onboarding 编辑器；默认我们先在对话里完成，不强制打开网页。

## Critical Fields

A workspace is not ready for user-dependent workflows until these are present:

- `user.display_name`
- `assistant.role`
- at least one `accounts[]` item
- `accounts[0].id`
- `accounts[0].name`
- `accounts[0].positioning`
- `storage.default_provider`
- at least one `storage.workspaces[]` item
- at least one `storage.routes` entry

If only a few fields are missing, do not restart full onboarding. Ask only for the missing information.

## Six-Question Fast Onboarding

Ask one question at a time unless the user asks to provide everything at once.

### 1. User and Content Direction

Ask:

> 第 1 个问题：你希望我怎么称呼你？你主要做什么类型的内容？
>
> 比如：AI 工具、自媒体运营、生活方式、教育、职场、知识管理、健康、财经、个人 IP 等。

Map to:

- `user.display_name`
- `user.bio`
- `user.location` if volunteered
- initial content direction for account positioning and hot-topic keywords

### 2. Account and Platforms

Ask:

> 第 2 个问题：你现在有哪些内容账号？主要发布在哪些平台？
>
> 如果只有一个账号，可以告诉我账号名、平台、你希望它给人的感觉。如果还没开始，我可以先帮你创建一个“默认主账号”。

Map to:

- `accounts[].id`
- `accounts[].name`
- `accounts[].platforms`
- `accounts[].positioning`
- `accounts[].persona`
- `content_workflow.default_account_id`

### 3. Audience and Value

Ask:

> 第 3 个问题：这个账号主要想服务谁？他们通常有什么痛点，或者你希望他们看完你的内容获得什么？

Map to:

- `accounts[].audience.description`
- `accounts[].audience.pain_points`
- `accounts[].audience.desired_outcomes`

### 4. Style and Boundaries

Ask:

> 第 4 个问题：你希望内容是什么风格？有没有不想写的话题、禁用词、表达禁区，或者你喜欢的参考风格？

Map to:

- `accounts[].writing_profile.tone`
- `accounts[].writing_profile.structure`
- `accounts[].writing_profile.style_references`
- `accounts[].writing_profile.banned_words`
- `accounts[].writing_profile.must_include`
- `accounts[].content_boundaries.allowed_topics`
- `accounts[].content_boundaries.avoid_topics`
- `accounts[].content_boundaries.claims_policy`

### 5. Storage and Knowledge Base

Ask:

> 第 5 个问题：你希望我把热点、草稿、转写、竞品拆解这些内容保存在哪里？
>
> 可以是本地 Markdown、Obsidian、飞书、Notion，或者先只保存在当前工作区。默认我会先为你建立一个 `知识结构/` 文件夹，因为我会假设你还没有现成的知识库结构。

Default when unclear:

- `storage.default_provider: local`
- `storage.workspaces[0].id: local_workspace`
- `storage.workspaces[0].base_path: ./知识结构`
- default folders: `知识体系`, `竞品素材`, `热点素材`, `历史文章`
- default routes: `knowledge_system`, `hot_topics`, `transcripts`, `competitors`, `drafts`, `published`, `historical_articles`

If the user chooses Feishu, Notion, Google Drive, or another cloud provider, remind them that the config stores only environment variable names, never secret values.

### 6. Collaboration and Permissions

Ask:

> 第 6 个问题：你希望我作为内容搭档怎么协作？哪些动作必须先问你？
>
> 比如：公开发布、删除、覆盖已有内容、发消息、创建日程、批量操作、对外分享。

Map to:

- `assistant.role`
- `assistant.interaction_style`
- `assistant.communication_rules`
- `content_workflow.confirmation_policy`
- `permissions.require_confirmation_for`

Use conservative defaults for sensitive actions:

- `delete`
- `overwrite`
- `external_share`
- `public_publish`
- `send_email`
- `calendar_invite`
- `bulk_operation`
- `paid_action`
- `legal_commitment`

## Confirmation Before Writing

Before writing files, summarize the proposed config in human language and ask for confirmation:

> 我整理了一版你的内容工作流配置草案：
>
> - 称呼：...
> - 主账号：...
> - 平台：...
> - 定位：...
> - 目标受众：...
> - 默认内容流程：选题 → 大纲 → 初稿 → 修改 → 定稿 → 发布提醒 → 数据复盘
> - 默认存储：...
> - 敏感动作：发布、删除、覆盖、外部分享前确认
>
> 如果没问题，我会保存为 `config.yaml`，并同步更新 `USER.md` 和今天的 memory。你也可以说“修改账号定位”或“跳过存储设置”。

Only write files after the user confirms.

## Writing Onboarding Results

After confirmation:

1. Start from `config.example.yaml` or the existing `config.yaml`.
2. Merge collected answers into the config.
3. Set `onboarding.completed` to `true` if critical fields are complete.
4. Put skipped or uncertain items in `onboarding.missing_fields`.
5. Write `config.yaml`.
6. Generate `USER.md` as a concise collaboration summary.
7. Generate `memory/YYYY-MM-DD.md` as the onboarding log.

Use the same artifact semantics as `config-server.mjs`:

- `config.yaml`: machine-readable runtime config
- `USER.md`: human-readable collaboration profile
- `memory/YYYY-MM-DD.md`: what was completed, what remains missing, and any onboarding notes

## After Onboarding

End by offering a practical next-step menu:

> 现在你可以直接让我做这些事：
> 1. “今天有什么热点适合我的账号？”
> 2. “帮我写一篇小红书笔记”
> 3. “拆解这个视频做成选题”
> 4. “把这段草稿改成我的账号风格”
> 5. “生成本周内容计划”

## Optional Visual Editor Trigger

Do not start the web config server by default.

During onboarding, it is okay to say the visual editor exists for people who prefer forms, but chat remains the default path. Start `node config-server.mjs` only when the user asks for the page-based editor or advanced configuration, such as:

- “打开配置器”
- “打开 onboarding 编辑器”
- “高级编辑”
- “我想看完整 config”
- “用网页改配置”
- “debug 配置”
- “导入 / 导出 YAML”

When launching the server, tell the user the local URL and explain that the visual editor is optional; they can finish onboarding entirely in chat.
