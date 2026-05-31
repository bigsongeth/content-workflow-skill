# Content Agent Config Schema

这份配置把“通用 Skill”和“用户千人千面的信息”分开：

- `config.schema.json`：机器可读的结构约束。
- `config.example.yaml`：给用户和开发者看的示例配置。
- `config-editor.html`：给非技术用户使用的可选可视化 onboarding / 配置页面。
- `config-server.mjs`：本地保存服务，让页面可以写入 `config.yaml`。
- `CONFIG_EDITOR.md`：配置页面和本地服务的使用说明。
- `SKILL_RUNTIME_FLOW.md`：Skill 运行时如何检查配置、触发 onboarding、执行任务。

后续 Skill、脚本、onboarding 问答、HTML 表单都应该围绕同一份 schema 工作。

Skill 运行总控逻辑见 `SKILL_RUNTIME_FLOW.md`。
Onboarding 问题流见 `ONBOARDING_FLOW.md`。

## 设计原则

1. Skill 不写死用户信息，只读取 config。
2. 配置里不保存 token、密码、密钥明文，只保存环境变量名。
3. 用户不需要直接编辑 JSON Schema；问答或表单负责生成 YAML/JSON。
4. 存储位置用“逻辑路由”抽象，例如 `knowledge_system`、`hot_topics`、`transcripts`、`competitors`、`drafts`。
5. 支持飞书、Notion、本地文件、Obsidian 等不同存储方式。
6. 默认假设用户没有现成知识库，先创建并使用本地 `知识结构/`。

## 顶层字段

| 字段 | 作用 | Onboarding 是否必问 |
|---|---|---|
| `version` | 配置版本 | 否，系统默认 |
| `user` | 用户称呼、所在地、背景 | 是 |
| `assistant` | Agent 名字、角色、协作风格 | 是 |
| `accounts` | 自媒体账号矩阵 | 是 |
| `storage` | 内容资产存储方式和路由 | 是 |
| `content_workflow` | 从选题到发布的工作流 | 是 |
| `hot_tracker` | 热点追踪平台、关键词、选题偏好 | 可选 |
| `video_processing` | 视频转写、竞品拆解规则 | 可选 |
| `automation` | 定时推送和提醒 | 可选 |
| `permissions` | 创建、编辑、发送、提醒等权限边界 | 是 |
| `integrations` | 外部工具启用状态和凭证环境变量名 | 可选 |
| `onboarding` | 完成状态和缺失字段 | 系统维护 |

## 推荐 Onboarding 阶段

### 1. 认识用户和协作方式

写入：

- `user.display_name`
- `user.location`
- `user.bio`
- `assistant.name`
- `assistant.role`
- `assistant.interaction_style`
- `assistant.communication_rules`

### 2. 建立账号矩阵

写入：

- `accounts[].id`
- `accounts[].name`
- `accounts[].platforms`
- `accounts[].positioning`
- `accounts[].persona`
- `accounts[].audience`
- `accounts[].content_boundaries`
- `accounts[].writing_profile`

### 3. 建立内容存储路由

写入：

- `storage.default_provider`
- `storage.workspaces`
- `storage.routes`
- `storage.link_policy`
- `storage.naming_rules`

建议固定的 route key：

- `knowledge_system`：知识体系输入
- `hot_topics`：热点搜集
- `transcripts`：视频/音频转写
- `competitors`：竞品对标
- `topic_pool`：选题池
- `drafts_*`：文稿存放
- `published_*`：已发布归档
- `historical_articles`：历史文章总归档
- `materials`：素材库
- `reviews`：复盘记录

### 4. 内容生产规则

写入：

- `content_workflow.default_account_id`
- `content_workflow.ask_before_writing_when_account_unclear`
- `content_workflow.content_categories`
- `content_workflow.draft_lifecycle`
- `content_workflow.confirmation_policy`

### 5. 热点追踪

写入：

- `hot_tracker.enabled`
- `hot_tracker.sources`
- `hot_tracker.topic_fields`
- `hot_tracker.selection_preferences`
- `hot_tracker.output_route`

### 6. 视频转写和竞品参考

写入：

- `video_processing.enabled`
- `video_processing.default_action`
- `video_processing.supported_platform_priority`
- `video_processing.competitor_detection`
- `video_processing.routes`
- `video_processing.output_format`

### 7. 自动化和权限边界

写入：

- `automation.*`
- `permissions.*`
- `integrations.*`

## 程序读取建议

程序应优先读取用户实际配置文件，例如：

```text
config.yaml
```

如果不存在，再读取示例或启动 onboarding：

```text
config.example.yaml
```

推荐逻辑：

1. 读取 `config.yaml`。
2. 用 `config.schema.json` 校验。
3. 如果缺字段，看 `onboarding.missing_fields`。
4. 缺关键字段时启动问答或表单补齐。
5. 技能运行时只使用 route key，不直接写死飞书 node token、Notion page id 或本地路径。
