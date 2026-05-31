# Deep Dive

Get a chapter-by-chapter summary with timestamps, then optionally ask follow-up questions about specific sections.

## Triggers

"chapter summary", "break down by section", "detailed summary", "分章节总结", "逐章总结", "what topics does this cover"

## Steps

### 1. Environment Check

Use Content Workflow Gateway. Customer deployments should only require `CONTENT_GATEWAY_API_KEY`; use direct upstream tools only for internal debugging.

### 2. Get Chapter Summary

**Gateway mode:**
```bash
curl -s -X POST "${CONTENT_GATEWAY_BASE_URL:-http://fm.rainplay.cn:26056}/v1/bibi/chapter" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $CONTENT_GATEWAY_API_KEY" \
  -d "{\"url\":\"$URL\",\"includeDetail\":true,\"outputLanguage\":\"zh-CN\"}"
```


### 3. Present Results

Format each chapter as:

```
## Chapter 1: [Title] (00:00 – 05:30)
[Chapter summary]

## Chapter 2: [Title] (05:30 – 12:15)
[Chapter summary]
...
```

If `chapters` array is empty, fall back to the overall `chapterSummary` text and explain that the video did not have chapter markers.

### 4. Interactive Q&A

If the user wants to go deeper into a specific chapter:

1. Use the returned subtitle data (from `includeDetail=true`) as context
2. Answer follow-up questions about specific sections
3. Reference timestamps when quoting content

For example:
- "What exactly did they say about X in chapter 3?"
- "Can you elaborate on the point at 15:30?"

### 5. Follow-up Options

- "Get the full transcript" → `workflows/transcript-extract.md`
- "Turn a specific chapter into an article" → `workflows/article-rewrite.md`
- "Compare with another video on the same topic" → `workflows/research-compile.md`
- "Save these notes" → `workflows/export-notes.md`
