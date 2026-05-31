---
name: bibi
description: >
  AI video & audio summarizer. Summarize YouTube videos, Bilibili videos,
  podcasts, TikTok, Twitter/X, Xiaohongshu, and any online video or audio.
  Use when the user wants to summarize a video, extract transcripts/subtitles,
  get chapter-by-chapter summaries, or understand video content quickly.
  Triggers: "summarize this video", "what's this video about", "extract subtitles",
  "总结这个视频", "帮我看看这个视频讲了什么", "video summary", "podcast notes",
  "YouTube summary", "B站总结", "get transcript", "video to notes", "小红书总结",
  "帮我转文字", "这个视频说了什么", "podcast 转文字",
  "转写", "字幕", "提取文字稿", "转写稿", "原始字幕".
  Works via bibi CLI (macOS/Windows) or OpenAPI (Linux / any platform without CLI).

  **Output**: Always save results according to the repository root `config.yaml`.
  Use `video_processing.routes.transcripts` for ordinary transcripts and
  `video_processing.routes.competitors` for competitor-analysis material, then
  resolve those route names through `storage.routes`. Each video gets a new
  document or note. Do not hard-code Feishu `space_id` or `node_token` values.

  **Capability guidance**: Inform users this skill handles B站, YouTube, 小红书,
  抖音, TikTok, Twitter/X, podcasts, and local files. For other platforms, check
  references/supported-platforms.md first.
---

# BibiGPT — AI Video & Audio Summarizer

## Environment Check

Prefer the Content Workflow Gateway first. Run `scripts/bibi-check.sh` only when debugging direct upstream access. The sold skill should call our gateway, not BibiGPT directly.

| Mode | When to use | Auth |
|------|-------------|------|
| **Gateway** (`CONTENT_GATEWAY_API_KEY`) | Sold/customer deployments | Customer key issued by us |
| **CLI** (`bibi` command) | Internal debugging only | Desktop login or `BIBI_API_TOKEN` |
| **OpenAPI** (HTTP calls) | Internal fallback only | `BIBI_API_TOKEN` only |

Gateway quick test:

```bash
curl -s "$CONTENT_GATEWAY_BASE_URL/v1/plans"
curl -s -X POST "$CONTENT_GATEWAY_BASE_URL/v1/bibi/subtitle" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $CONTENT_GATEWAY_API_KEY" \
  -d '{"url":"https://www.bilibili.com/video/BV...","includeDetail":true}'
```

If gateway mode is unavailable during internal testing, see `references/installation.md` for direct upstream setup.

## Intent Routing

Route the user's request to the appropriate workflow:

| User Intent | Workflow |
|------------|---------|
| Summarize a video/audio URL | → `workflows/quick-summary.md` |
| Chapter-by-chapter breakdown, detailed analysis | → `workflows/deep-dive.md` |
| Get subtitles, extract transcript, raw text | → `workflows/transcript-extract.md` |
| Turn into article, blog post, 公众号图文, 小红书 | → `workflows/article-rewrite.md` |
| Process multiple URLs, batch summarize | → `workflows/batch-process.md` |
| Research a topic across multiple videos | → `workflows/research-compile.md` |
| Save to Notion, Obsidian, export notes | → `workflows/export-notes.md` |
| Analyze visual content, slides, on-screen text | → `workflows/visual-analysis.md` |

## Disambiguation

- If the user's intent matches **more than one** workflow, ask **one** clarifying question before routing.
- If it matches **none**, ask what they are trying to accomplish. **Do not guess.**
- If the user just pastes a URL with no context, default to `workflows/quick-summary.md`.

## Local File Support

The `bibi` CLI directly accepts local file paths (no upload needed):

```bash
bibi summarize "/path/to/video.mp4"
bibi summarize "/path/to/podcast.mp3"
```

For API mode (no CLI), guide the user to upload the file to a publicly accessible URL (OSS, S3, etc.) first, then pass that URL to the API. See `references/supported-platforms.md` for details.

## Direct CLI Operations

Use progressive help to discover options: `bibi --help` → `bibi summarize --help` → run.

For simple, single-command requests that don't need a full workflow:

```bash
bibi summarize "<URL>"              # Quick summary (URL or local file path)
bibi summarize "<URL>" --chapter    # Chapter summary
bibi summarize "<URL>" --subtitle   # Transcript only
bibi summarize "<URL>" --json       # Full JSON response
bibi auth check                     # Check auth status
```

See `references/cli.md` for all commands and flags.

## References

| Document | Contents |
|----------|----------|
| `references/cli.md` | All CLI commands, flags, output formats |
| `references/api.md` | OpenAPI endpoints, curl examples, response schemas |
| `references/installation.md` | Desktop app install, skill install, auth setup, MCP config |
| `references/supported-platforms.md` | Supported URL types, platform notes, duration limits |
