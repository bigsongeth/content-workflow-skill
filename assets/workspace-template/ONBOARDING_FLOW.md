# Content Agent Onboarding Flow

这份文档定义 onboarding 问题流。目标是帮助没有技术背景的用户，通过“选项 + 自定义输入”的方式，生成可被程序读取的 `config.yaml`。

核心原则：

1. 一次只问一组问题，先让用户能开工，再慢慢补全。
2. 每个关键问题都提供内置选项，同时保留“其他/自定义”。
3. 每个问题都必须能落到 `config.schema.json` 的具体字段。
4. 用户不知道怎么答时，允许跳过，并写入 `onboarding.missing_fields`。
5. 不收集上游 token、密码、密钥明文；客户购买后的 `CONTENT_GATEWAY_API_KEY` 属于产品激活码，只写入本地配置或环境变量，不写入公开文档。
6. 每一阶段结束后都给用户一段“我理解的是……”确认摘要。
7. 如果 Agent 运行环境已有记忆库、用户上下文、历史文档或当前对话信息，先提炼“低风险用户画像假设”，再让用户确认，不要像第一次见面一样机械查户口。

## 交互控件规范

程序运行时，每个关键问题都按这个结构渲染：

```yaml
question: 给用户看的问题
type: single_select | multi_select | text | grouped_form
options:
  - label: 选项名
    value: 写入配置的值
    helper: 给小白看的解释
allow_custom: true
custom_label: 其他，我自己写
allow_skip: true
skip_values:
  - unknown
target_fields:
  - config.path
```

控件使用规则：

- `single_select`：角色、默认存储平台、是否启用功能。
- `multi_select`：平台、风格、关键词、权限、输出格式。
- `text`：称呼、链接、路径、补充说明。
- `grouped_form`：账号矩阵、存储路由、提醒时间这类重复结构。
- 每个选择题都必须保留“其他/自定义”。
- “暂时不知道”不阻塞流程，字段进入 `onboarding.missing_fields`。

## Onboarding 分层

### L1：启动必填

完成后，Agent 应该已经能开始工作：

- 知道怎么称呼用户。
- 知道自己扮演什么角色。
- 知道用户有几个账号、每个账号大致做什么。
- 知道内容默认存在哪里。
- 知道写作时的基本语气和边界。

写入字段：

- `user`
- `assistant`
- `accounts`
- `storage.default_provider`
- `storage.workspaces`
- `storage.routes`
- `content_workflow`
- `permissions`

### L2：能力增强

完成后，Agent 可以更好地自动化内容工作流。

写入字段：

- `hot_tracker`
- `video_processing`
- `automation`
- `integrations`
- `onboarding`


## -1. 激活码与付费状态检查

目的：把“买卖关系”自然接入技能，让用户知道自己买到的是可持续服务，而不是一堆静态文件。

### 触发时机

在首次 onboarding、调用热榜、调用音视频转写前，都应检查：

1. `config.yaml` 是否已有 `integrations.content_gateway.credential_env`。
2. 环境变量 `CONTENT_GATEWAY_API_KEY` 是否存在，或配置中是否保存了本地激活码引用。
3. 调用 `GET /v1/entitlements/me` 检查 Token 状态。

### 推荐话术

```text
推荐先激活内容工作流。
如果你购买了我们的服务，请粘贴收到的 Token/激活码。这个码只用于验证套餐，不是上游平台密钥。

如果你已经有自建网关，也可以填自己的服务地址和 Token；不过自建配置比较麻烦，我们默认先不展开。

激活后我会自动检查：套餐类型、是否到期、能否使用热榜和音视频转写。
如果你想先跳过，也可以先完成基础配置，之后再激活付费能力。
```

### Token 状态处理

| 网关错误码 | 用户可见说明 | Agent 应做什么 |
|---|---|---|
| `missing_or_invalid_api_key` | 没检测到有效激活码 | 让用户粘贴 Token；同时给购买/价格页 |
| `subscription_expired` | 订阅已到期 | 停止调用付费功能；保留本地配置；给续费入口 |
| `subscription_inactive` | 授权未激活 | 提示可能未付款/退款/暂停；给客服入口 |
| `feature_not_in_plan` | 当前套餐不含该功能 | 提示升级，不要继续重试 |
| `quota_exceeded` | 本期额度已用完 | 提示等下周期或升级/加购 |

### 到期时推荐话术

```text
你的内容工作流订阅已经到期，所以我暂时不能继续获取热榜或处理音视频转写。

不用担心，之前的账号配置、知识库路径、历史文档都还在。
续费后我可以直接接着用，不需要重新 onboarding。

你可以选择：
1. 月付续费：25 元/月
2. 年付续费：199 元/年
3. 买断：599 元永久使用
```

### 配置写入

激活成功后写入：

```yaml
integrations:
  content_gateway:
    enabled: true
    base_url: http://fm.rainplay.cn:26056
    credential_env: CONTENT_GATEWAY_API_KEY
    activation_status: active
    plan: monthly | annual | lifetime
    expires_at: YYYY-MM-DD | null
```

不要把上游 BibiGPT Token、Rebang 源地址等写入客户配置。

## -0. 上下文感知开场

目的：让不同 Agent（例如龙虾、爱马仕或其他支持读取工作区文档的 Agent）都能先读当前上下文，再开始 onboarding。

### 启动前读取顺序

1. 当前对话里用户已经说过的信息。
2. Agent 自身可用的长期记忆或用户画像。
3. 工作区文档：`USER.md`、`MEMORY.md`、`SOUL.md`、`IDENTITY.md`。
4. 已存在的 `config.yaml`。

### 低风险画像假设

允许主动说出“我先猜/我看到你可能是……”，但必须符合以下规则：

- 只说与内容工作流相关的信息：账号方向、平台、写作偏好、存储方式、目标。
- 不主动暴露敏感隐私、私人关系、支付信息、身份证明、联系方式。
- 不把猜测当事实，要用“我先按这个理解，如果不对你直接改”这种表达。
- 群聊或共享环境中，少说具体个人细节，优先让用户确认。

### 推荐开场模板

```text
我先根据当前上下文帮你起个草稿，不从零查户口。

我目前理解你大概是：
- 做内容/自媒体，希望更稳定地产生选题和素材
- 需要热榜追踪、音视频转写、选题建议和文档归档
- 偏好先能开工，细节后面慢慢补

如果这个方向对，我们只需要补 3 件事：
1. 你的主要账号/平台
2. 内容资料放哪里
3. 你的激活码 Token（可跳过；有自建网关也可以之后再填）
```

### 抛砖引玉式问题

不要问“你是谁？你做什么？你想怎样？”这种空问题。

改成：

```text
我先给你一个默认方案：
- 角色：内容创作搭档 + 选题军师
- 默认流程：每天看热点 → 匹配你的账号方向 → 生成 5 个选题 → 需要时转写视频素材
- 默认存储：先存在本地 `知识结构/`，以后可以接飞书/Notion

你只要告诉我：这个方案哪里不对？
```

如果用户直接确认，就用默认配置开工；不要继续追问所有字段。

## 0. 开场和预期管理

目的：降低用户压力，让用户知道“不需要一次答完”。

推荐话术：

```text
我会用几个简单问题帮你搭好内容工作流配置。
你不用懂技术，也不用一次说完整。每个问题我都会给你几个选项，不合适也可以自己写。

我们先把最关键的部分完成：你是谁、做什么账号、内容存哪里、希望我怎么帮你。
如果你更喜欢图形化页面，也可以让我打开本地 onboarding 编辑器；默认先在对话里完成，不强制打开网页。
```

如果用户跳过：

- 使用默认配置骨架。
- 默认先创建并使用 `知识结构/`，因为新用户可能还没有自己的知识库结构。
- 将缺失字段写入 `onboarding.missing_fields`。

## 1. 用户和协作方式

目的：建立用户身份、Agent 角色和互动风格。

### 问题 1.1：用户称呼

```yaml
question: 我怎么称呼你？
type: text
allow_custom: true
target_fields:
  - user.display_name
```

### 问题 1.2：所在地或内容 base

```yaml
question: 你有没有希望我记住的所在地、常驻地或内容 base？比如上海、成都、线上办公。
type: text
allow_skip: true
target_fields:
  - user.location
```

### 问题 1.3：Agent 角色

```yaml
question: 你希望我主要像什么角色？
type: single_select
options:
  - label: 内容创作搭档
    value: content_partner
    helper: 陪你选题、写稿、改稿、复盘。
  - label: 运营助理
    value: operations_assistant
    helper: 整理素材、存文档、提醒发布。
  - label: 写作教练
    value: writing_coach
    helper: 关注表达、结构、风格和改稿。
  - label: 资料管理员
    value: knowledge_manager
    helper: 关注素材、知识库、转写和归档。
  - label: 内容军师
    value: strategist
    helper: 关注选题判断、账号定位和策略。
  - label: 暂时不确定
    value: unknown
    helper: 先用默认搭档模式，后面再改。
allow_custom: true
custom_label: 其他，我自己写
target_fields:
  - assistant.role
```

### 问题 1.4：协作风格

```yaml
question: 你希望我平时怎么和你说话？可以多选。
type: multi_select
options:
  - label: 简洁直接
    value: concise
  - label: 温和陪伴
    value: warm
  - label: 专业严谨
    value: professional
  - label: 犀利有观点
    value: sharp
  - label: 主动推进
    value: proactive
  - label: 少问问题，直接给建议
    value: low_questions
  - label: 多给我选择
    value: offer_options
allow_custom: true
custom_label: 其他风格
target_fields:
  - assistant.interaction_style
```

### 问题 1.5：协作禁忌

```yaml
question: 有没有你不喜欢的协作方式？可以多选。
type: multi_select
options:
  - label: 不要催我
    value: do_not_push
  - label: 不要替我做最终决定
    value: do_not_decide_for_me
  - label: 不要太营销腔
    value: avoid_marketing_tone
  - label: 不要长篇大论
    value: avoid_long_explanations
  - label: 不要频繁追问
    value: avoid_too_many_questions
  - label: 暂时没有
    value: none
allow_custom: true
custom_label: 其他禁忌
target_fields:
  - assistant.communication_rules
```

确认摘要：

```text
我先这样记录：我称呼你为「{display_name}」，我主要是你的「{role}」，协作风格是「{style_list}」。如果没问题，我们继续看你的账号。
```

## 2. 账号矩阵

目的：梳理每个账号的定位、受众、人设和内容边界。

### 问题 2.1：账号数量

```yaml
question: 你现在有几个自媒体账号？
type: single_select
options:
  - label: 1 个
    value: 1
  - label: 2 个
    value: 2
  - label: 3 个
    value: 3
  - label: 还不确定
    value: unknown
allow_custom: true
custom_label: 其他数量
target_fields:
  - accounts
```

### 问题 2.2：每个账号的基础信息

```yaml
question: 请补充每个账号的名称、平台和定位。
type: grouped_form
repeat_by: accounts_count
fields:
  - label: 账号名称
    input: text
    target_field: accounts[].name
  - label: 主要平台
    input: multi_select
    options: [小红书, 抖音, 视频号, 公众号, B站, 快手, 微博, 知乎, 其他]
    allow_custom: true
    target_field: accounts[].platforms
  - label: 账号定位
    input: text
    placeholder: 例如：营养健康、职场心理、亲子教育、城市文旅
    target_field: accounts[].positioning
target_fields:
  - accounts[].id
  - accounts[].name
  - accounts[].platforms
  - accounts[].positioning
```

### 问题 2.3：人设关键词

```yaml
question: 这个账号希望别人记住你的哪几个关键词？可以多选。
type: multi_select
options:
  - label: 专业可信
    value: professional
  - label: 真实接地气
    value: grounded
  - label: 温暖陪伴
    value: warm
  - label: 犀利有观点
    value: sharp
  - label: 疗愈放松
    value: healing
  - label: 干货实用
    value: practical
  - label: 有趣会讲故事
    value: storytelling
allow_custom: true
custom_label: 其他人设
target_fields:
  - accounts[].persona
```

### 问题 2.4：受众和痛点

```yaml
question: 这个账号主要写给谁看？他们最想解决什么问题？可以多选。
type: multi_select
options:
  - label: 想学习专业知识的人
    value: knowledge_seekers
  - label: 有焦虑和压力的人
    value: stressed_people
  - label: 想变健康/变美/变好的普通人
    value: self_improvement
  - label: 想做内容或搞副业的人
    value: creators
  - label: 想旅行、放松、疗愈的人
    value: travel_healing
  - label: 亲子/家庭关系困扰的人
    value: family_parenting
allow_custom: true
custom_label: 其他受众和痛点
target_fields:
  - accounts[].audience.description
  - accounts[].audience.pain_points
  - accounts[].audience.desired_outcomes
```

### 问题 2.5：内容边界

```yaml
question: 这个账号有哪些内容边界？可以多选。
type: multi_select
options:
  - label: 不做医疗诊断或疗效承诺
    value: no_medical_claims
  - label: 不碰政治和公共敏感议题
    value: avoid_political_sensitive
  - label: 不讲明星八卦
    value: avoid_celebrity_gossip
  - label: 不做焦虑营销
    value: avoid_anxiety_marketing
  - label: 不夸大收益或效果
    value: avoid_exaggerated_claims
  - label: 暂时没有
    value: none
allow_custom: true
custom_label: 其他边界
target_fields:
  - accounts[].content_boundaries.allowed_topics
  - accounts[].content_boundaries.avoid_topics
  - accounts[].content_boundaries.claims_policy
```

确认摘要：

```text
我理解你现在有 {account_count} 个账号：
1. {account_name}：{positioning}，人设关键词是 {persona}
2. ...

接下来我会问写作风格，这会决定我以后帮你写稿时像不像你。
```

## 3. 写作风格和成稿规格

目的：让 Agent 产出的内容更接近用户风格。

### 问题 3.1：常用内容格式

```yaml
question: 你平时最常需要我帮你产出什么？可以多选。
type: multi_select
options:
  - label: 短视频口播稿
    value: short_video_script
  - label: 小红书笔记
    value: xiaohongshu_note
  - label: 公众号文章
    value: wechat_article
  - label: 直播稿
    value: livestream_script
  - label: 选题大纲
    value: outline
  - label: 长视频脚本
    value: long_video_script
  - label: 图文标题/封面文案
    value: other
allow_custom: true
custom_label: 其他格式
target_fields:
  - accounts[].writing_profile.formats
```

### 问题 3.2：内容语气

```yaml
question: 你希望内容是什么语气？可以多选。
type: multi_select
options:
  - label: 说人话
    value: plainspoken
  - label: 专业但不端着
    value: professional_accessible
  - label: 情绪强一点
    value: emotional
  - label: 温柔疗愈
    value: gentle_healing
  - label: 有画面感
    value: visual
  - label: 干货密度高
    value: dense_practical
  - label: 犀利观点型
    value: sharp_opinion
allow_custom: true
custom_label: 其他语气
target_fields:
  - accounts[].writing_profile.tone
```

### 问题 3.3：内容结构

```yaml
question: 你喜欢哪种内容结构？可以多选。
type: multi_select
options:
  - label: 开头钩子
    value: hook
  - label: 生活案例
    value: daily_example
  - label: 专业解释
    value: expert_explanation
  - label: 具体步骤
    value: action_steps
  - label: 故事反转
    value: story_turn
  - label: 结尾金句
    value: closing_line
  - label: 行动号召
    value: call_to_action
allow_custom: true
custom_label: 其他结构
target_fields:
  - accounts[].writing_profile.structure
```

### 问题 3.4：篇幅、参考和禁用表达

```yaml
question: 有没有默认篇幅、参考账号/文章，或者绝对不要出现的词？没有可以跳过。
type: text
allow_skip: true
allow_custom: true
target_fields:
  - accounts[].writing_profile.length_defaults
  - accounts[].writing_profile.style_references
  - accounts[].writing_profile.banned_words
  - accounts[].writing_profile.must_include
```

确认摘要：

```text
以后我给「{account_name}」写内容时，会优先用「{formats}」，语气偏「{tone}」，结构大致是「{structure}」。
```

## 4. 内容存储方式

目的：建立内容资产的存储抽象，让 Skill 后续只读 route key。

默认假设新用户还没有自己的知识结构。除非用户明确给出飞书、Notion、Obsidian 或其他现有库，先使用当前工作区内的 `知识结构/`，并预置四个分区：

- `知识体系/`：书籍、文章、课程、研究和个人观点等长期输入。
- `竞品素材/`：对标账号、竞品内容、拆解记录和参考表达。
- `热点素材/`：每日抓取热点、趋势和选题机会。
- `历史文章/`：过往发布内容，以及和 Agent 一起写过的草稿与定稿。

### 问题 4.1：默认存储平台

```yaml
question: 你的内容资料一般存在哪里？
type: single_select
options:
  - label: 飞书知识库/云文档
    value: feishu
  - label: Notion
    value: notion
  - label: 本地文件夹
    value: local
  - label: Obsidian
    value: obsidian
  - label: Google Drive
    value: google_drive
  - label: 多个地方混用
    value: other
  - label: 暂时不知道
    value: unknown
allow_custom: true
custom_label: 其他存储方式
target_fields:
  - storage.default_provider
```

### 问题 4.2：内容分类路由

```yaml
question: 你希望这些内容分别放到哪里？不知道的可以先跳过。
type: grouped_form
fields:
  - label: 知识体系
    target_field: storage.routes.knowledge_system
  - label: 热点搜集
    target_field: storage.routes.hot_topics
  - label: 视频/音频转写
    target_field: storage.routes.transcripts
  - label: 竞品对标
    target_field: storage.routes.competitors
  - label: 选题池
    target_field: storage.routes.topic_pool
  - label: 成品/半成品文稿
    target_field: storage.routes.drafts
  - label: 已发布归档
    target_field: storage.routes.published
  - label: 历史文章总归档
    target_field: storage.routes.historical_articles
  - label: 复盘记录
    target_field: storage.routes.reviews
allow_custom: true
allow_skip: true
target_fields:
  - storage.workspaces
  - storage.routes
  - accounts[].default_storage
```

### 问题 4.3：具体链接或路径

```yaml
question: 如果你用飞书/Notion，可以把知识库、页面或数据库链接发给我；如果是本地或 Obsidian，可以填文件夹路径。现在没有也可以跳过。
type: text
allow_skip: true
allow_custom: true
target_fields:
  - storage.workspaces[].external_id
  - storage.workspaces[].base_path
  - storage.routes.*.provider_target_id
  - storage.routes.*.path
```

### 问题 4.4：链接返回规则

```yaml
question: 创建新文档后，要不要把链接发给你？
type: single_select
options:
  - label: 每次都发链接
    value: always_return_link
  - label: 有链接就发
    value: return_link_when_available
  - label: 不用发链接
    value: never_return_link
allow_custom: false
target_fields:
  - storage.link_policy
```

确认摘要：

```text
我会把内容这样存：
- 知识体系：{knowledge_system_route}
- 热点：{hot_topics_route}
- 视频转写：{transcripts_route}
- 竞品：{competitors_route}
- 文稿：{draft_routes}
- 历史文章：{historical_articles_route}

缺少具体链接或路径的地方，我先标记为待补。
```

## 5. 内容生产工作流

目的：定义从选题到发布的默认流程。

### 问题 5.1：默认工作流

```yaml
question: 你希望我帮你写内容时，默认走哪种流程？
type: single_select
options:
  - label: 选题 → 大纲 → 初稿 → 修改 → 定稿 → 发布提醒
    value: full_creation_loop
  - label: 直接写初稿 → 修改 → 定稿
    value: draft_first
  - label: 只帮我出选题和大纲
    value: topic_outline_only
  - label: 我给方向，你直接写成稿
    value: direction_to_final
  - label: 暂时不固定
    value: flexible
allow_custom: true
custom_label: 自定义流程
target_fields:
  - content_workflow.draft_lifecycle
```

### 问题 5.2：确认规则

```yaml
question: 哪些环节需要我先问你？可以多选。
type: multi_select
options:
  - label: 账号不清楚时先问我
    value: ask_before_writing_when_account_unclear
  - label: 每次改完问我继续改还是定稿
    value: ask_after_each_revision
  - label: 保存文稿前先确认
    value: ask_before_saving
  - label: 对外分享前必须确认
    value: ask_before_external_share
allow_custom: true
custom_label: 其他确认规则
target_fields:
  - content_workflow.ask_before_writing_when_account_unclear
  - content_workflow.confirmation_policy
```

确认摘要：

```text
默认工作流我记录为：{draft_lifecycle}。账号不清楚时会先问你，改稿后会按你的确认规则推进。
```

## 6. 热点追踪

目的：让热点技能知道追什么、避开什么、怎么筛选。

### 问题 6.1：是否启用热点追踪

```yaml
question: 你需要每日热点/选题推送吗？
type: single_select
options:
  - label: 需要，每天推送
    value: true
  - label: 暂时不需要
    value: false
  - label: 以后再说
    value: unknown
allow_custom: false
target_fields:
  - hot_tracker.enabled
```

### 问题 6.2：热点来源

```yaml
question: 想看哪些平台的热点？可以多选。
type: multi_select
options:
  - label: 微博
    value: weibo
  - label: 抖音
    value: douyin
  - label: 小红书
    value: xiaohongshu
  - label: 知乎
    value: zhihu
  - label: B站
    value: bilibili
  - label: 头条
    value: toutiao
  - label: 百度
    value: baidu
  - label: 全部
    value: all
allow_custom: true
custom_label: 其他平台
target_fields:
  - hot_tracker.sources
```

### 问题 6.3：内容关键词

```yaml
question: 你的内容领域有哪些关键词？可以多选，也可以自己写。
type: multi_select
options:
  - label: 营养健康
    value: nutrition_health
  - label: 心理情绪
    value: psychology_emotion
  - label: 亲子家庭
    value: parenting_family
  - label: 职场成长
    value: career_growth
  - label: 文旅旅行
    value: travel
  - label: 疗愈放松
    value: healing
  - label: 本地城市/地域
    value: local_city
allow_custom: true
custom_label: 自定义关键词
target_fields:
  - hot_tracker.topic_fields
```

### 问题 6.4：选题偏好和避雷

```yaml
question: 你更喜欢哪类切入角度？哪些热点不要碰？
type: multi_select
options:
  - label: 干货教程
    value: practical
  - label: 故事案例
    value: story
  - label: 情绪共鸣
    value: emotional_resonance
  - label: 观点评论
    value: opinion
  - label: 种草推荐
    value: recommendation
  - label: 避坑提醒
    value: warning
allow_custom: true
custom_label: 自定义偏好或避雷
target_fields:
  - hot_tracker.selection_preferences.preferred_angles
  - hot_tracker.selection_preferences.avoid_topics
```

确认摘要：

```text
热点追踪会关注 {sources}，用 {topic_fields} 这些关键词筛选，优先给你 {preferred_angles} 方向。
```

## 7. 视频转写和竞品参考

目的：定义用户发链接时的默认处理方式。

### 问题 7.1：链接默认处理方式

```yaml
question: 你发视频、播客或小红书链接给我时，默认希望我做什么？
type: single_select
options:
  - label: 总结内容
    value: summarize
  - label: 提取完整转写
    value: transcribe
  - label: 提炼选题
    value: extract_topics
  - label: 改写成文章/文案
    value: rewrite_article
  - label: 每次先问我
    value: ask
allow_custom: true
custom_label: 其他处理方式
target_fields:
  - video_processing.enabled
  - video_processing.default_action
```

### 问题 7.2：竞品识别

```yaml
question: 什么情况下我应该把它当成竞品对标？可以多选。
type: multi_select
options:
  - label: 我说“竞品”
    value: 竞品
  - label: 我说“对标”
    value: 对标
  - label: 我说“参考这个”
    value: 参考这个
  - label: 我说“拆解一下”
    value: 拆解一下
  - label: 我发外部链接时都先问我
    value: ask_on_external_link
allow_custom: true
custom_label: 其他触发词
target_fields:
  - video_processing.competitor_detection.save_when_user_says
```

### 问题 7.3：竞品输出格式

```yaml
question: 竞品内容需要保存哪些东西？可以多选。
type: multi_select
options:
  - label: 摘要
    value: summary
  - label: 原始转写
    value: transcript
  - label: 章节
    value: chapters
  - label: 金句
    value: key_quotes
  - label: 可复用选题
    value: article_angles
  - label: 改写稿
    value: rewrite
allow_custom: true
custom_label: 其他输出内容
target_fields:
  - video_processing.output_format
  - video_processing.routes
```

确认摘要：

```text
以后你发链接时，我默认会 {default_action}。当你说 {competitor_keywords} 时，我会按竞品处理并存到 {competitor_route}。
```

## 8. 自动化和提醒

目的：定义推送、发布提醒、复盘提醒。

### 问题 8.1：自动化任务

```yaml
question: 你需要我定时做哪些事？可以多选。
type: multi_select
options:
  - label: 每日热点推送
    value: hot_topic_push
  - label: 定稿后提醒发布
    value: publish_reminder
  - label: 发布后提醒复盘数据
    value: review_reminder
  - label: 暂时不需要自动化
    value: none
allow_custom: true
custom_label: 其他自动化
target_fields:
  - automation.hot_topic_push.enabled
  - automation.publish_reminder.enabled
  - automation.review_reminder.enabled
```

### 问题 8.2：提醒时间和渠道

```yaml
question: 这些提醒什么时候发、发到哪里？
type: grouped_form
fields:
  - label: 时间
    input: text
    placeholder: 例如：每天 09:00、定稿后 2 小时、发布后 24 小时
  - label: 渠道
    input: single_select
    options: [私聊, 群聊, 文档, 日历, 仅本地记录, 其他]
    allow_custom: true
allow_skip: true
target_fields:
  - automation.timezone
  - automation.*.schedule
  - automation.*.destination
```

确认摘要：

```text
自动化我先这样记录：{automation_summary}。涉及发消息、建日历或群聊通知时，我会按权限规则确认。
```

## 9. 权限和工具集成

目的：防止 Agent 越权，同时记录工具状态。

### 问题 9.1：默认权限

```yaml
question: 哪些事你允许我默认做？可以多选。
type: multi_select
options:
  - label: 创建新文档
    value: allow_create_documents
  - label: 编辑已有文档
    value: allow_edit_existing_documents
  - label: 给我发消息
    value: allow_send_messages
  - label: 创建提醒
    value: allow_create_reminders
  - label: 暂时都先问我
    value: ask_first
allow_custom: true
custom_label: 其他默认权限
target_fields:
  - permissions.allow_create_documents
  - permissions.allow_edit_existing_documents
  - permissions.allow_send_messages
  - permissions.allow_create_reminders
```

### 问题 9.2：必须确认的动作

```yaml
question: 哪些事必须先问你？可以多选。
type: multi_select
options:
  - label: 删除内容
    value: delete
  - label: 覆盖旧内容
    value: overwrite
  - label: 对外分享
    value: external_share
  - label: 公开发布
    value: public_publish
  - label: 发邮件
    value: send_email
  - label: 建日历邀请
    value: calendar_invite
  - label: 批量操作
    value: bulk_operation
  - label: 涉及付费或合同
    value: paid_action
  - label: 涉及法律承诺
    value: legal_commitment
allow_custom: true
custom_label: 其他必须确认事项
target_fields:
  - permissions.require_confirmation_for
```

### 问题 9.3：工具集成

```yaml
question: 你会用哪些工具？如果需要 token，我只记录环境变量名，不记录密钥本身。
type: multi_select
options:
  - label: 飞书
    value: feishu
  - label: Notion
    value: notion
  - label: Obsidian
    value: obsidian
  - label: 本地文件
    value: local
  - label: Google Drive
    value: google_drive
  - label: BibiGPT
    value: bibi
  - label: 暂时不确定
    value: unknown
allow_custom: true
custom_label: 其他工具
target_fields:
  - permissions.secret_policy
  - integrations.*.enabled
  - integrations.*.credential_env
```

确认摘要：

```text
权限边界我记录为：可以 {allowed_actions}；遇到 {confirmation_actions} 必须先问你。密钥不会写进配置文件。
```

## 10. 总确认和写入

目的：在写入 `config.yaml` 前让用户确认。

推荐话术：

```text
我已经整理好你的配置。你不用看代码，我用人话总结一下：

1. 你是谁、我怎么帮你
2. 你的账号矩阵
3. 内容存放位置
4. 写作风格
5. 热点、转写、提醒和权限

如果你说“确认”，我就写入配置；如果哪里不对，你直接说要改哪一块。
```

写入字段：

- 全部已收集字段。
- `onboarding.completed`
- `onboarding.completed_at`
- `onboarding.missing_fields`

同时更新的文件：

- `USER.md`
- `memory/YYYY-MM-DD.md`
- 必要时补充 `MEMORY.md` 的索引或摘要

写入规则：

- `config.yaml`：保存结构化事实，作为运行时主配置
- `USER.md`：保存隐私收敛后的人类可读用户画像摘要
- `memory/YYYY-MM-DD.md`：记录本次 onboarding 的完成情况、用户明确提出的偏好、后续待补字段
- 不要把 token、密码、精确住址、手机号、私密链接或云端平台敏感 ID 写进 `USER.md`

`USER.md` 建议同步内容：

- 用户称呼
- 身份概述
- 主要内容方向或项目
- 偏好的协作方式
- 知识库存放方式的摘要
- 必须确认的敏感动作摘要

`memory/YYYY-MM-DD.md` 建议记录：

- 今天完成了什么 onboarding
- 用户选择了本地还是云端存储
- 是否还缺 API 权限或路径配置
- 有哪些字段暂时跳过，后续需要补

完成条件：

- 用户确认。
- 或用户要求先保存草稿配置。

## HTML 表单设计建议

HTML 表单应和问答流程共用同一套字段，但交互上分成多页。

推荐页面：

1. 基本信息
2. 账号矩阵
3. 写作风格
4. 内容存储
5. 热点追踪
6. 视频转写/竞品
7. 自动化/权限
8. 预览和确认

表单体验要求：

- 支持“暂时不知道”，并写入 `onboarding.missing_fields`。
- 支持新增多个账号。
- 支持选择存储平台后显示不同字段：
  - 飞书：知识库/节点链接或 ID
  - Notion：页面/数据库链接或 ID
  - 本地：目录路径
  - Obsidian：vault 路径
- 支持从 `config.example.yaml` 预填。
- 最后一页展示人类可读摘要和 YAML 预览。
- 每个选择题都保留“其他/自定义”输入。

## 缺失字段处理

如果用户不知道某个字段，不要阻塞整个 onboarding。

处理方式：

1. 用合理默认值继续。
2. 把字段路径写入 `onboarding.missing_fields`。
3. 在最终摘要里列出“以后需要补的内容”。

示例：

```yaml
onboarding:
  completed: false
  missing_fields:
    - storage.routes.competitors.provider_target_id
    - automation.hot_topic_push.schedule
```
