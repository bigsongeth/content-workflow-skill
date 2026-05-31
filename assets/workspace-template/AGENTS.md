# AGENTS.md - 工作区入口

这是一个可分发、可测试的内容工作流 Skill 工作区。

它的目标不是绑定某一个具体用户，而是提供一套：

- onboarding 机制
- 配置驱动运行方式
- 可扩展的内容工作流技能
- 可持续更新的用户画像与记忆文件

## 首次进入时要做什么

如果工作区里**没有真实 `config.yaml`**：

1. 不要直接执行依赖用户配置和付费授权的技能
2. 先读取当前 Agent 可用的用户记忆、当前对话、`USER.md`、`MEMORY.md`、`SOUL.md`、`IDENTITY.md`，形成低风险用户画像假设
3. 先进行激活码检查：引导用户提供 `CONTENT_GATEWAY_API_KEY`，并调用网关验证套餐/到期状态
4. 再进入 onboarding，默认通过问答流程生成真实 `config.yaml`
5. 如果用户偏好图形化页面，再启动本地配置服务
6. 同步更新：
   - `USER.md`
   - `memory/YYYY-MM-DD.md`

如果工作区里**已经有真实 `config.yaml`**：

1. 优先读取 `config.yaml`
2. 只在缺字段时补问
3. 不要把 `config.example.yaml` 当成真实用户状态

## 运行优先级

运行时请按以下优先级理解工作区：

1. `config.yaml`
2. `config.json`
3. `config.example.yaml` 仅作模板参考

以下文件是辅助上下文，不是运行时事实来源：

- `USER.md`
- `MEMORY.md`
- `SOUL.md`
- `IDENTITY.md`

## 核心规则

- 通用 Skill 不写死某个用户的身份、账号、知识库 ID 或平台路径
- 所有用户个性化信息应来自 `config.yaml`
- `USER.md` 只保存隐私收敛后的人类可读摘要
- `memory/YYYY-MM-DD.md` 记录 onboarding 和关键协作事件
- 不在配置或摘要文件中保存 token、密码、密钥明文

## 推荐测试方式

如果你是第一次测试这个工作区：

1. 复制一个干净副本
2. 删除真实 `config.yaml`
3. 通过对话完成一次 onboarding
4. 如用户偏好图形化页面，再启动 `config-server.mjs`
5. 验证是否生成：
   - `config.yaml`
   - `USER.md`
   - `memory/YYYY-MM-DD.md`
6. 再运行 skill 命令做反向验证

测试步骤见：

- `TEST_ONBOARDING.md`

## 用户画像与记忆

- `USER.md`：当前用户的匿名化摘要
- `memory/YYYY-MM-DD.md`：当天日志
- `MEMORY.md`：长期规则和总结

如果 onboarding 改变了用户定位、协作方式、知识库存放位置，应该同步更新这些文件。

## 内容工作流

当前工作区重点围绕：

- 热点追踪
- 视频/音频转写
- 竞品拆解
- 文稿起草与归档

具体行为应由各 skill 读取 `config.yaml` 后决定，而不是从本文件硬编码推断。

## 安全边界

- 删除、覆盖、对外分享、公开发布等敏感动作要先确认
- 涉及外部 API 时，只记录环境变量名，不记录密钥内容
- 群聊或共享环境中，不泄露用户私密上下文

## 工具与文档

- `SKILL_RUNTIME_FLOW.md`：运行总控逻辑
- `ONBOARDING_FLOW.md`：首次配置与补问问题流
- `CONFIG_SCHEMA.md`：配置结构说明
- `CONFIG_EDITOR.md`：本地配置页面说明
- `TEST_ONBOARDING.md`：手动测试手册
- `ACTIVATION_AND_BILLING.md`：激活码、套餐、到期、续费与计费错误处理

## 分发说明

如果要把这份工作区交给其他 Agent 安装测试，优先使用 skill 根目录的安装脚本生成干净副本：

```bash
scripts/install_workspace.sh /path/to/export-dir
```

导出副本应保留模板和运行逻辑，但不应携带：

- 真实 `config.yaml`
- dated memory 日志
- 本地缓存
- 私人历史上下文
