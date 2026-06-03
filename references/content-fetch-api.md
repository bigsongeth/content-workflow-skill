# 内容抓取 API (Content Fetch API)

通过你的激活码访问多平台内容数据。统一入口、统一鉴权,无需关心各平台底层差异。

## 鉴权

所有请求带上你购买后收到的激活码:

```http
X-API-Key: <你的激活码>
```

> 这是你购买的产品激活码,不是任何第三方平台密钥。

## 统一入口

```http
GET {CONTENT_GATEWAY_BASE_URL}/v1/content/fetch?platform=<平台>&action=<动作>&<参数...>
```

- `platform`: 目标平台(见下表)
- `action`: 要执行的动作(见下表)
- 其余为该动作所需参数

成功返回:

```json
{ "success": true, "platform": "...", "action": "...", "data": { ... } }
```

计费/限流类错误返回 `error_type: billing`,不要重试,按提示续费或等待配额重置。

## 支持的平台

小红书 · 抖音 · 微博 · B站 · 微信公众号 · 微信视频号 · 快手 · 知乎

> 其他平台陆续开放中,有需要可提需求。

## 动作清单

### 小红书 `platform=xiaohongshu`

| action | 说明 | 必填参数 | 可选参数 |
|--------|------|----------|----------|
| `note_detail` | 笔记详情 | `note_id` | `share_text` |
| `note_comments` | 笔记评论 | `note_id` | `cursor`, `sort` |
| `user_info` | 用户资料 | `user_id` | `share_text` |
| `user_notes` | 用户笔记列表 | `user_id` | `cursor` |
| `search` | 搜索 | `keyword`, `page` | `sort` |

### 抖音 `platform=douyin`

| action | 说明 | 必填参数 | 可选参数 |
|--------|------|----------|----------|
| `video_detail` | 视频详情 | `video_id` | — |
| `video_by_url` | 按分享链接取视频 | `share_url` | — |
| `user_videos` | 用户视频列表 | `user_id` | `cursor`, `count` |
| `search` | 搜索 | `keyword` | `offset`, `count` |
| `hot_search` | 热搜榜 | — | — |

### 微博 `platform=weibo`

| action | 说明 | 必填参数 | 可选参数 |
|--------|------|----------|----------|
| `post_detail` | 帖子详情 | `post_id` | — |
| `post_comments` | 帖子评论 | `post_id` | `cursor`, `sort` |
| `user_info` | 用户资料 | `user_id` | — |
| `user_timeline` | 用户动态 | `user_id` | `page` |
| `search` | 搜索 | `keyword` | `page` |
| `hot_search` | 热搜榜 | — | `page`, `count` |

### B站 `platform=bilibili`

| action | 说明 | 必填参数 | 可选参数 |
|--------|------|----------|----------|
| `video_detail` | 视频详情 | — | `bv_id`, `av_id` |
| `video_comments` | 视频评论 | — | `bv_id`, `av_id`, `cursor` |
| `user_info` | 用户资料 | `user_id` | — |
| `user_videos` | 用户视频列表 | `user_id` | `page` |
| `search` | 搜索 | `keyword` | `page` |
| `hot_search` | 热搜榜 | `limit` | — |

### 微信公众号 `platform=wechat_mp`

| action | 说明 | 必填参数 | 可选参数 |
|--------|------|----------|----------|
| `article_detail` | 文章详情 | `url` | — |
| `article_list` | 文章列表 | `ghid` | `offset` |
| `read_count` | 阅读量 | `url`, `comment_id` | — |
| `comments` | 评论 | `url` | `comment_id` |

### 微信视频号 `platform=wechat_channels`

| action | 说明 | 必填参数 | 可选参数 |
|--------|------|----------|----------|
| `video_detail` | 视频详情 | — | `id`, `export_id` |
| `video_by_url` | 按分享链接取视频 | `share_url` | — |
| `search` | 搜索 | `keyword` | — |
| `user_search` | 用户搜索 | `keyword` | `page` |
| `hot_words` | 热门话题 | — | — |

### 快手 `platform=kuaishou`

| action | 说明 | 必填参数 | 可选参数 |
|--------|------|----------|----------|
| `video_detail` | 视频详情 | `video_id` | — |
| `video_by_url` | 按分享链接取视频 | `share_url` | — |
| `video_comments` | 视频评论 | `video_id` | `cursor` |
| `user_info` | 用户资料 | `user_id` | — |
| `user_videos` | 用户视频列表 | `user_id` | `cursor` |
| `search` | 搜索 | `keyword` | `page` |
| `hot_search` | 热搜榜 | — | `board_type` |

### 知乎 `platform=zhihu`

| action | 说明 | 必填参数 | 可选参数 |
|--------|------|----------|----------|
| `question_answers` | 问题回答列表 | `question_id` | `cursor`, `limit` |
| `article_detail` | 文章详情 | `article_id` | — |
| `answer_comments` | 回答评论 | `answer_id` | `limit`, `offset` |
| `user_info` | 用户资料 | `user_token` | — |
| `user_articles` | 用户文章 | `user_token` | `offset`, `limit` |
| `search` | 搜索 | `keyword` | `limit`, `offset` |
| `hot_search` | 热搜榜 | — | `limit` |

## 示例

抓一条小红书笔记详情:
```bash
curl -H "X-API-Key: $KEY" \
  "$CONTENT_GATEWAY_BASE_URL/v1/content/fetch?platform=xiaohongshu&action=note_detail&note_id=NOTE_ID"
```

搜索抖音视频:
```bash
curl -H "X-API-Key: $KEY" \
  "$CONTENT_GATEWAY_BASE_URL/v1/content/fetch?platform=douyin&action=search&keyword=露营"
```

取B站视频详情:
```bash
curl -H "X-API-Key: $KEY" \
  "$CONTENT_GATEWAY_BASE_URL/v1/content/fetch?platform=bilibili&action=video_detail&bv_id=BV1xx411c7mD"
```

## 错误码

| HTTP | error | 含义 | 处理 |
|------|-------|------|------|
| 400 | `platform_not_supported` | 平台未开放 | 换支持的平台或提需求 |
| 400 | `action_not_supported` | 动作不存在 | 查动作清单 |
| 400 | `missing_required_param` | 缺必填参数 | 补齐参数 |
| 401 | `missing_or_invalid_api_key` | 激活码无效 | 检查/重新粘贴激活码 |
| 402 | `subscription_expired` | 订阅到期 | 续费 |
| 429 | `rate_limited` | 触发限流 | 稍后重试 |
| 429 | `quota_exceeded` | 配额用尽 | 等待重置或升级 |
| 502 | `upstream_error` | 数据源临时异常 | 稍后重试 |
