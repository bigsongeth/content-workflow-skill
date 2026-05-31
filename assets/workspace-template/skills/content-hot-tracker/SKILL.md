# SKILL.md - Content Hot Tracker

## Skill Metadata

```yaml
name: Content Hot Tracker
identifier: content-hot-tracker
version: 1.8.0
description: 追踪多平台热点话题，分析趋势，为内容创作者提供选题建议和爆款方向
author: xiaohong
tags: [内容创作, 热点, 社媒, 运营, 选题]
categories: [productivity, social-media]
```

---

## 数据源

**主数据源：Content Workflow Gateway `/v1/hot`**（网关内部再中转到上游热榜服务）

| 平台 | 接口 | 说明 |
|------|------|------|
| 微博 | `tab=weibo&sub_tab=search&version=2` | 实时热搜，含热度值 |
| 知乎 | `tab=zhihu&date_type=now` | 热榜，含热度描述 |
| 抖音 | `tab=douyin&date_type=now` | 热门视频，含播放量 |
| 小红书 | `tab=xiaohongshu&sub_tab=hot-search` | 热门搜索，含浏览量 |
| 百度 | `tab=baidu&sub_tab=realtime` | 实时热搜，含热度分 |
| 今日头条 | `tab=toutiao` | 热门文章，含热度值 |
| B站 | `tab=bilibili` | 热门内容 |
| 全站 | `tab=top&sub_tab=today` | 全平台聚合 |

**脚本：`rebang_fetcher.py`**（位于本技能目录）

获取方式：客户侧调用我们的 Content Workflow Gateway；网关内部中转上游热榜服务，避免暴露直接上游。

---

## How It Works

### 热点追踪

**优先调用 Content Workflow Gateway**，不再依赖 web_search，也不在客户侧暴露上游：

```bash
python rebang_fetcher.py              # 打印所有平台热点
python rebang_fetcher.py weibo       # 只看微博
python rebang_fetcher.py douyin       # 只看抖音
python rebang_fetcher.py xiaohongshu # 只看小红书
python rebang_fetcher.py zhihu        # 只看知乎
python rebang_fetcher.py baidu       # 只看百度
python rebang_fetcher.py toutiao     # 只看今日头条
```

或作为模块导入使用：

```python
from rebang_fetcher import fetch_all, print_all
print_all()                    # 获取并打印所有平台
data = fetch_all(platforms=["微博","小红书"], limit_per=10)
```

### 输出格式

```
📊 今日热点 | 2026-04-29 14:30
============================================================

📌 微博
----------------------------------------
 1. 朋友圈改版 [热] 🔥1206407
 2. 中国羽毛球协会主席张军被查 [新] 🔥932177
 3. 我国新发现13个亿吨级油田 🔥660002
 ...
```

### 趋势分析

- **上升期话题**：热度标签为"新"或"热"，优先追
- **平稳期话题**：热度下降但仍在榜，可差异化切入
- **下降期话题**：热度持续走低，避开

### 选题建议（核心产出）

**结合用户内容定位：** 从仓库根目录的 `config.yaml` 读取。

运行前先按 `SKILL_RUNTIME_FLOW.md` 判断配置状态：
- 如果 `config.yaml` 不存在，先进入 onboarding，生成基础配置。
- 如果 `config.yaml` 存在，直接读取其中的 `hot_tracker.topic_fields`、`accounts`、`assistant` 等配置，不要使用文档里的示例值覆盖用户配置。

对所有平台热点进行人工+AI筛选，识别出与用户配置里的内容方向相关的内容。每个内容方向应包含：
- `name`：领域名称
- `keywords`：用于匹配热点的关键词
- `angle_guidance`：用于生成切入角度的偏好说明

**对每个相关热点，给出：**
1. **切入角度**（从这个热点可以做什么角度的内容）
2. **标题建议**（3-5个备选标题）
3. **适合平台**（微博/抖音/小红书/知乎/头条）

### 标题建议

提供 5-8 个备选标题：
- 数字开头型："3个技巧帮你……"
- 悬念型："为什么XX突然爆火？"
- 情绪型："XX的人，最后都……"

---

## 重试机制（防 429）

`rebang_fetcher.py` 内置指数退避重试：

- **触发 429（Too Many Requests）时**：等待 `2^n` 秒 + 随机抖动（0.5~1.5倍），最长等 120s
- **最大重试次数**：5 次
- **请求间隔**：平台间默认间隔 1.5s，避免触发限流
- **非 429 错误**：也进入重试，最多重试 5 次

---

## 用户偏好设置

用户可通过 `config.yaml` 或本地配置页面自定义：
- **内容领域**：`hot_tracker.topic_fields`
- **追踪平台**：`hot_tracker.sources`
- **推荐数量**：`hot_tracker.selection_preferences.max_recommendations`
- **选题风格**：`accounts[].writing_profile`、`hot_tracker.selection_preferences`
- **存放位置**：`storage.routes.hot_topics`

---

## Output Format

### 热点汇总

```
📈 今日热点 TOP 5

1. [话题名称] - 热度: 🔥🔥🔥🔥🔥
   平台: 微博/抖音/知乎
   分类: 娱乐/科技/社会/美食
```

### 选题建议

```
📝 选题推荐

【观点类】
"从XX事件看XX现象，这才是真相"

【知识类】
"5分钟带你了解XX事件的来龙去脉"
```

---

## 定时任务

**Cron Job ID：** `596b16f3-c349-4fdb-82b4-3be9006ea8ae`

| 项目 | 说明 |
|------|------|
| 任务名 | content-hot-tracker-daily |
| 触发时间 | 每天 09:00 Asia/Shanghai |
| 触发后行为 | 运行 `python rebang_fetcher.py md` → 本地 Markdown → 按 `storage.routes.hot_topics` 新建文档 → 发消息告知链接 |
| 内容偏好 | 从 `hot_tracker.topic_fields` 和 `content` 配置读取 |

---

## 飞书知识库存储

**存储位置：由 `config.yaml` 决定**
- 默认读取 `storage.routes.hot_topics`
- 如果 route 指向飞书知识库，应读取 route 里的 `workspace_id`、`provider_target_id`、`path`
- 如果 route 指向 Notion、本地文件、Obsidian 或其他系统，按对应 route 类型保存
- **规则：每天新建一个文档**，放在热点搜集对应路由下
- 文档命名格式：`热点追踪日报 YYYY-MM-DD`

不要在通用 Skill 中写死任何 `space_id`、`node_token` 或用户姓名；这些都应来自 `config.yaml`。

---

## 本地报告存储

当 `storage.routes.hot_topics` 指向本地或 Obsidian 时，生成的 Markdown 报告保存在配置指定目录。默认路径：

```
知识结构/热点素材/
└── 热点追踪_YYYY-MM-DD.md   # 每日一份
```

---

## 配置命令

```
设置内容领域为[文旅+心理健康]
设置追踪平台为[微博,抖音,小红书]
设置选题风格为[轻松疗愈]
```

---

## Changelog

### v1.8.0 (2026-05-06)
- 默认接入 `知识结构/` 本地路由，聊天 onboarding 优先，视觉编辑器可选

### v1.5.0 (2026-05-05)
- 配置驱动：读取仓库根目录 `config.yaml` 中的平台、内容领域、推荐数量和存储路由
- 通用化：不再把单一用户的人设、知识库节点或内容定位作为 Skill 默认行为

### v1.0.0 (2026-04-29)
- **历史更新**：从 web_search 改为结构化热榜 API；v1.8 后客户侧优先经 Content Workflow Gateway 中转
- 新增 rebang_fetcher.py，支持多平台热点获取
- 内置 429 防限流重试机制（指数退避）
- 支持 8 个平台：微博、知乎、抖音、小红书、百度、头条、B站、全站

---

*此技能可以帮助自媒体创作者快速找到热门选题，提高内容产出效率*
