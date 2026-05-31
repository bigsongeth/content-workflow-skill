#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rebang_fetcher as r
import importlib
importlib.reload(r)

print("Testing generate_content_suggestions...")
if "--live" in sys.argv:
    results = r.fetch_all(limit_per=5, delay_between=0.5)
else:
    results = {
        "微博": {
            "list": [
                {"title": "年轻人开始关注情绪管理", "heat_num": "123456", "label_name": "热"},
                {"title": "周末轻度假搜索上涨", "heat_num": "88888", "label_name": "新"},
            ]
        },
        "小红书": {
            "list": [
                {"title": "健康饮食打卡走红", "view_num": "76543", "tag": "热搜"},
                {"title": "普通人如何缓解职场压力", "view_num": "65432", "tag": "讨论"},
            ]
        },
    }

# Check raw data
hits = []
for platform, data in results.items():
    if "error" in data:
        print(f"SKIP {platform}: error={data.get('error')}")
        continue
    raw = data.get("list") if isinstance(data, dict) else data
    if not isinstance(raw, list):
        print(f"SKIP {platform}: raw type={type(raw)}")
        continue
    print(f"OK {platform}: {len(raw)} items")
    for item in raw[:20]:
        if not isinstance(item, dict):
            continue
        title = item.get("title") or item.get("word", "")
        desc = item.get("describe") or item.get("desc", "")
        text = title + " " + desc
        for kw in ["胖", "休息", "维生素", "职场", "家庭", "旅行", "心理"]:
            if kw in text:
                hits.append((platform, kw, title[:50]))

print(f"\nTotal hits: {len(hits)}")
for h in hits[:15]:
    print(f"  {h}")

print(f"\n--- Suggestions section ---")
out = r.generate_content_suggestions(results)
print(out[:800])
