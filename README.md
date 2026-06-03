# Content Workflow Skill

一套面向自媒体 / 内容运营的 **Agent 内容工作流工作区脚手架**。安装后，你的 AI Agent 会获得一整套可配置的内容生产能力：

- **热点追踪**：多平台（微博 / 抖音 / 小红书 / 知乎 / 百度 / B站 / GitHub 等）实时热榜 + 选题建议
- **多平台内容抓取**：小红书 / 抖音 / 微博 / B站 / 公众号 / 视频号 / 快手 / 知乎统一查询接口，见 `references/content-fetch-api.md`
- **视频 / 音频转写**：B站、抖音、小红书、YouTube 等链接 → 字幕 / 摘要 / 分章 / 改写成文章
- **配置驱动**：账号定位、内容方向、存储路径全部由 `config.yaml` 决定，不写死任何人的身份
- **对话式 onboarding**：首次使用通过聊天生成配置，无需手填表单
- **本地知识库骨架**：`知识结构/`（历史文章 / 热点素材 / 竞品素材 / 知识体系）

---

## 快速开始

### 1. 安装工作区

```bash
scripts/install_workspace.sh /path/to/your-workspace
```

把模板复制到你的工作目录。安装脚本只复制模板，真实配置交给后续 onboarding 生成。

### 2. 申请激活 Key

本技能的热点 / 转写能力通过官方托管的 **Content Workflow Gateway** 提供，需要激活 Key。

- **网关地址**：`http://fm.rainplay.cn:26056`
- **申请 / 续费 / 支持**：微信 **isjuss**

拿到 Key 后，有两种填法（任选其一）：

**A. 环境变量（推荐）**
```bash
export CONTENT_GATEWAY_API_KEY="你的激活Key"
```

**B. 让 Agent 在 onboarding 时写入配置**
直接告诉 Agent 你的 Key，它会在生成 `config.yaml` 时填入 `integrations.*.credential_env` 指向的环境变量。
> 注意：`config.yaml` 只保存「环境变量名」，**不保存 Key 明文**。

### 3. 完成 onboarding

让你的 Agent 读取工作区里的 `AGENTS.md` 和 `ONBOARDING_FLOW.md`，它会：
1. 根据上下文先做一份用户画像草稿
2. 引导你填激活 Key
3. 只问最少的必要问题，生成 `config.yaml`

### 4. 跑一次验证

```bash
python3 skills/content-hot-tracker/rebang_fetcher.py weibo
```

---

## 套餐

| 套餐 | 价格 | 能力 |
|------|------|------|
| 买断制 | ¥599 | 热点追踪 + 视频/音频转写 |
| 年订阅 | ¥199/年 | 热点追踪 + 视频/音频转写 |
| 月订阅 | ¥25/月 | 热点追踪 + 视频/音频转写 |

申请与续费请联系微信 **isjuss**。

---

## 目录结构

```
.
├── SKILL.md                    # 技能入口（脚手架本体）
├── scripts/                    # 安装 / 校验脚本
│   ├── install_workspace.sh
│   └── validate_workspace.sh
├── references/                 # onboarding / 布局 / 测试文档
└── assets/workspace-template/  # 分发的工作区模板
    ├── AGENTS.md / SOUL.md / ...   # Agent 上下文与规则
    ├── config.example.yaml         # 配置模板
    ├── config-server.mjs           # 可选：可视化配置编辑器
    ├── 知识结构/                    # 本地知识库骨架
    ├── skills/content-hot-tracker/ # 热点追踪技能
    └── bibigpt-skill/              # 视频/音频转写技能
```

---

## 安全说明

- 配置文件**只记录环境变量名**，绝不保存 token / 密钥 / 密码明文
- 删除、覆盖、对外发布等敏感动作，Agent 会先与你确认
- 真实 `config.yaml`、`.env`、本地缓存与记忆日志均已在 `.gitignore` 中排除

---

*激活、续费与技术支持：微信 **isjuss***
