# TOOLS.md - 本地工具配置笔记

技能定义了工具怎么用。这个文件记的是你自己的具体配置，属于你的环境、你的设置。

## 记什么

技能在运行时需要的具体参数、偏好。比如：

- 图片生成的偏好风格
- 语音生成的默认音色
- 任何跟你的环境相关的特有配置

## 为什么单独放

技能是共享的，配置是你自己的。分开放，更新技能不会丢你的笔记，分享技能不会泄露你的环境。

---

## BibiGPT Skill（视频/音频总结）

**技能位置**：`~/.npm-global/lib/node_modules/openclaw/skills/bibi/`

**API Token**：存放在环境变量 `BIBI_API_TOKEN` 中，不在文档中展示明文。

**输出规范**：
> 通用 Skill 注意：本节包含当前工作区的历史默认值。迁移后的 Bibi/视频转写流程必须读取 `config.yaml` 中的 `video_processing.routes` 和 `storage.routes`，不要把这里的飞书节点写死到 Skill 中。

- 总结结果写入 `config.yaml` 指定的存储位置
- 普通转写读取 `video_processing.routes.transcripts`
- 竞品对标文章读取 `video_processing.routes.competitors`
- 具体位置通过 `storage.routes` 解析，可以是飞书、Notion、本地文件、Obsidian 或其他系统
- 每次新建文档或笔记，命名格式：`[转写] {原标题}`

**支持平台**：B站、YouTube、小红书、抖音、TikTok、Twitter/X、播客、本地音视频文件

**触发关键词**：总结视频、视频转文字、帮我看看这个视频讲了什么、小红书总结、podcast 转文字 等

**SKILL.md 更新要点**：
- description 中加入触发词和 Output 说明
- workflows/quick-summary.md 重写为云文档输出流程

---

记下任何帮你干活的东西。这是你的备忘录。
