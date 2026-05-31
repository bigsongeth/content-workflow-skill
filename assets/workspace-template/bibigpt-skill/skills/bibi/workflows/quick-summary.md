# Quick Summary

Summarize a single video or audio URL and save the result to the storage route configured for the current workspace.

## Triggers

"summarize this video", "what's this about", "TL;DR", "总结这个视频", "帮我看看这个视频讲了什么", "video summary", "podcast notes", "帮我转文字", "这个视频说了什么", "小红书总结"

## Steps

### 1. Self-Routing (When to Use This Skill)

**主动触发条件**（满足任一）：
- 用户发了一个视频/音频链接（ B站、YouTube、小红书、抖音、TikTok、Twitter/X、播客等）
- 用户说"总结一下"、"转文字"、"帮我看看这个视频讲了什么"
- 用户说"这个 podcast 转文字"

**能力边界**：
- ✅ 支持：B站、YouTube、小红书、抖音、TikTok、Twitter/X、播客、本地音视频文件
- ❌ 暂不支持：微信视频号（直接链接）、快手（部分）
- 💡 如不确定，先查 `references/supported-platforms.md`

### 2. 环境检查

优先使用我们自己的 Content Workflow Gateway。客户侧只需要 `CONTENT_GATEWAY_API_KEY`，不需要也不应该接触上游 token。

检查：
- `CONTENT_GATEWAY_BASE_URL`，默认 `http://fm.rainplay.cn:26056`
- `CONTENT_GATEWAY_API_KEY`，购买后发放
- 如果返回 401/402/403，引导用户检查 key、套餐或续费状态

### 3. Validate Input

- 从用户消息中提取 URL
- 确认是支持的平台（参见 `references/supported-platforms.md`）
- 如果是短链接（b23.tv, xhslink.com 等），API 会自动展开
- 如果没有 URL，请用户粘贴

### 4. Execute Summary

**Gateway mode**:
```bash
curl -s -X POST "${CONTENT_GATEWAY_BASE_URL:-http://fm.rainplay.cn:26056}/v1/bibi/summarize" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $CONTENT_GATEWAY_API_KEY" \
  -d "{\"url\":\"$URL\",\"includeDetail\":true}"
```

详细参数见 `references/api.md`。

### 5. 写入配置指定位置

**存储位置：从仓库根目录 `config.yaml` 读取**
- 普通视频转写：读取 `video_processing.routes.transcripts`
- 竞品对标素材：读取 `video_processing.routes.competitors`
- 再通过 `storage.routes` 解析实际存储类型与位置
- **规则：每次新建一个文档或笔记**，放在对应 route 下
- 文档命名格式：`[转写] {原标题}` 或用户指定

**创建文档或笔记**：
1. 如果 route 指向飞书，使用对应的飞书文档或知识库工具创建文档
2. 如果 route 指向 Notion、本地文件、Obsidian 或其他存储方式，按 route 中的路径或数据库配置写入
3. 文档标题：`[转写] {原标题}` 或用户指定
4. 内容为 Markdown 格式，包含：
   - 视频标题、来源链接
   - 完整总结内容
   - 原视频链接
5. 将文档链接发给用户

### 6. 向用户说明能力边界

首次使用该技能时，告知用户：
> 我的视频总结能力支持 B站、YouTube、小红书、抖音、TikTok、Twitter/X、播客等平台，也支持本地音视频文件。总结结果已经按当前工作区配置保存好了。

### 7. 后续选项

提供后续操作选项：
- "想要章节拆解？" → `workflows/deep-dive.md`
- "需要原始字幕？" → `workflows/transcript-extract.md`
- "转成公众号图文？" → `workflows/article-rewrite.md`
