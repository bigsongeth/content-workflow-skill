# Skill Runtime Flow

这份文档定义 Content Agent Skill 的运行总控逻辑。

它不替代 `BOOTSTRAP.md`。`BOOTSTRAP.md` 是 Agent 第一次启动时认识用户的通用流程；本文件只描述这个内容创作 Skill 在安装后、触发时、运行时如何读取配置和决定是否进入 onboarding。

## 核心原则

1. Skill 通用能力不写死用户信息。
2. 运行时优先读取 `config.yaml`。
3. 没有 `config.yaml` 时，才进入完整 onboarding。
4. 有 `config.yaml` 时，不重复完整 onboarding。
5. 配置缺关键字段时，只补问缺失字段。
6. 用户可以随时通过配置页面细调，而不是重新 onboarding。

## 启动判断

每次 Skill 被触发时，先执行配置检查。

```text
检查 config.yaml
  ↓
不存在
  → 进入 onboarding
  → 生成最小可用 config.yaml
  → 再执行用户任务

存在
  → 读取 config.yaml
  → 检查 onboarding 状态和关键字段
  → 直接执行用户任务，除非缺关键字段
```

## 详细流程

### 1. 检查配置文件

按优先级查找：

1. `config.yaml`
2. `config.json`
3. `config.example.yaml`

处理规则：

- 找到 `config.yaml`：视为用户实际配置。
- 找到 `config.json`：可作为用户实际配置，但推荐最终写回 `config.yaml`。
- 只找到 `config.example.yaml`：只能作为模板，不能视为用户已完成配置。
- 三者都没有：提示缺少配置模板，无法自动 onboarding。

### 2. 没有实际配置时

如果不存在 `config.yaml` 和 `config.json`：

1. 启动 `ONBOARDING_FLOW.md` 中的 L1 引导。
2. 只收集最小可用配置，不追求完整。
3. 生成 `config.yaml`。
4. 根据 L1 关键字段完成情况设置 onboarding 状态：

```yaml
onboarding:
  completed: true
  missing_fields: []
```

5. 如果 L1 关键字段齐全，可以继续执行用户任务；非关键细节字段留到配置页面后续补全，不阻塞运行。

6. 生成或更新配套上下文文件：

- 更新 `USER.md`：写入匿名化、可读的用户画像摘要
- 更新 `memory/YYYY-MM-DD.md`：记录今天完成 onboarding、还有哪些待补项
- 如有必要，在 `MEMORY.md` 中补充索引或一句摘要，但不要把敏感细节堆进去

L1 关键字段：

- `user.display_name`
- `assistant.role`
- `accounts[].id`
- `accounts[].name`
- `accounts[].positioning`
- `storage.default_provider`
- 至少 1 个可用 `storage.workspaces`
- 至少 1 个可用 `storage.routes`
- `storage.workspaces`
- `storage.routes`
- `content_workflow.default_account_id`
- `permissions.require_confirmation_for`

### 3. 有实际配置时

如果存在 `config.yaml` 或 `config.json`：

1. 读取配置。
2. 校验配置结构。
3. 不执行完整 onboarding。
4. 根据用户任务读取对应配置块。

示例：

| 用户任务 | 读取配置 |
|---|---|
| 写稿 | `accounts`、`content_workflow`、`storage.routes` |
| 热点追踪 | `hot_tracker`、`storage.routes.hot_topics` |
| 视频转写 | `video_processing`、`storage.routes.transcripts` |
| 竞品拆解 | `video_processing.competitor_detection`、`storage.routes.competitors` |
| 保存文稿 | `accounts[].default_storage`、`storage.routes` |
| 提醒发布 | `automation.publish_reminder`、`permissions` |

### 4. 缺关键字段时

如果配置存在，但有关键字段缺失：

1. 不重跑完整 onboarding。
2. 只针对缺失字段补问。
3. 补问时继续使用“选项 + 自定义输入”。
4. 写回 `config.yaml`。
5. 更新 `onboarding.missing_fields`。

6. 如果补问内容改变了用户画像、协作方式或知识库位置，同步更新：

- `USER.md`
- 当日 `memory/YYYY-MM-DD.md`

触发补问的条件：

- `onboarding.completed: false`
- `onboarding.missing_fields` 非空
- 当前任务必需字段为空
- 用户明确要求“补配置”

补问示例：

```text
我已经有你的基础配置，但这次要保存竞品内容，还缺少“竞品对标”的存放位置。
你想把竞品内容存到哪里？

1. 飞书知识库
2. Notion
3. 本地文件夹
4. Obsidian
5. 其他，我自己写
```

### 5. 用户主动重新配置

用户说出类似意图时，进入配置更新模式：

- “重新配置”
- “重新 onboarding”
- “修改我的账号定位”
- “换一个知识库存放位置”
- “打开配置页面”
- “调整 Skill 参数”

处理规则：

- 小改动：直接补问对应字段并写回 `config.yaml`。
- 大改动：建议打开配置页面。
- 用户要求重来：重新执行 L1 onboarding，但覆盖前必须确认。

### 6. 配置页面入口

当用户想用图形化 onboarding 编辑器、细调配置或查看完整 YAML 时，推荐使用本地配置页面。默认不需要启动它：

```bash
node config-server.mjs
```

然后打开：

```text
http://127.0.0.1:8765/
```

页面保存后会写入：

```text
config.yaml
```

详细说明见 `CONFIG_EDITOR.md`。

### 7. 任务执行时的配置读取规则

运行具体能力前，先读取任务需要的配置块。

不要从以下文件读取用户个性化配置：

- `SOUL.md`
- `USER.md`
- `MEMORY.md`
- `AGENTS.md`
- 子 Skill 的硬编码说明

这些文件可以作为当前工作空间上下文，但通用 Skill 应该以 `config.yaml` 为准。

但在 onboarding 或补配置完成后，应该把结构化配置中的高价值摘要**写回**以下文件，帮助长期协作：

- `USER.md`
- `memory/YYYY-MM-DD.md`

### 8. 安全和权限

执行前检查 `permissions`。

必须确认的动作包括但不限于：

- 删除
- 覆盖
- 对外分享
- 公开发布
- 发送邮件
- 创建日历邀请
- 批量操作
- 付费或合同相关动作
- 法律承诺

凭证规则：

- `config.yaml` 不保存 token、密码、密钥明文。
- 只保存环境变量名，例如 `BIBI_API_TOKEN`。
- 任何时候都不把密钥输出给用户或群聊。

## 状态机

```text
[No Config]
  → onboarding L1
  → [Config Draft]
  → run task if required fields exist

[Config Draft]
  → missing field patch
  → [Config Ready]

[Config Ready]
  → run task
  → optional config editor update
  → [Config Ready]

[User Requests Reset]
  → confirm overwrite
  → onboarding L1
```

## 推荐文件分工

| 文件 | 作用 |
|---|---|
| `SKILL.md` | Skill 入口、触发条件、能力概览 |
| `SKILL_RUNTIME_FLOW.md` | 运行时总控逻辑 |
| `ONBOARDING_FLOW.md` | 首次配置和补问的问题流 |
| `CONFIG_SCHEMA.md` | 配置字段说明 |
| `CONFIG_EDITOR.md` | 可视化配置页面说明 |
| `config.schema.json` | 机器可读 schema |
| `config.example.yaml` | 示例配置 |
| `config.yaml` | 用户实际配置 |

## 实现注意事项

- `config.yaml` 是用户实际状态，不应随 Skill 模板覆盖。
- `config.example.yaml` 可以随 Skill 分发。
- `ONBOARDING_FLOW.md` 不负责执行任务，只负责收集配置。
- `SKILL_RUNTIME_FLOW.md` 不负责具体写稿、追热点或转写，只负责决定该读什么配置、是否需要 onboarding。
- 具体任务应拆到 `workflows/` 文档或子 Skill 中。
