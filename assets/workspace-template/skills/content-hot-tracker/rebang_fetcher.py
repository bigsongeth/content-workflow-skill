#!/usr/bin/env python3
"""
rebang_fetcher.py - 今日热榜 Rebang.today 多平台热点数据获取脚本
支持平台：全站、微博、知乎、抖音、小红书、百度、头条、B站、GitHub、V2EX、IT之家、36氪、虎扑、少数派等
功能：优先走自有网关；未配置网关时可直连 Rebang.today，并带重试机制（指数退避）应对 429 限流
"""

import json
import os
import time
import random
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config_loader import ConfigError, get_path, hot_tracker_config, load_config, resolve_route

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ========== 配置 ==========
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

# 平台 API 端点（来自 rebang.today /v1/menu_tabs 与前端懒加载 chunk 实测）
ENDPOINTS = {
    "全站":    "https://api.rebang.today/v1/items?tab=top&sub_tab=today&date_type=now&page={page}&version=1",
    "全站24小时": "https://api.rebang.today/v1/items?tab=top&sub_tab=lasthour&page={page}&version=1",
    "微博":    "https://api.rebang.today/v1/items?tab=weibo&sub_tab=search&version=2",
    "知乎":    "https://api.rebang.today/v1/items?tab=zhihu&date_type=now&page={page}&version=1",
    "小红书":  "https://api.rebang.today/v1/items?tab=xiaohongshu&sub_tab=hot-search&date_type=now&page={page}&version=1",
    "头条":    "https://api.rebang.today/v1/items?tab=toutiao&date_type=now&page={page}&version=1",
    "百度":    "https://api.rebang.today/v1/items?tab=baidu&sub_tab=realtime&date_type=now&page={page}&version=1",
    "抖音":    "https://api.rebang.today/v1/items?tab=douyin&date_type=now&page={page}&version=1",
    "B站":     "https://api.rebang.today/v1/items?tab=bilibili&sub_tab=popular&date_type=now&page={page}&version=1",
    "GitHub":  "https://api.rebang.today/v1/items?tab=github&sub_tab=all&date_type=daily&chinese=false&page={page}&version=1",
    "V2EX":    "https://api.rebang.today/v1/items?tab=v2ex&sub_tab=tech&date_type=now&page={page}&version=1",
    "IT之家":  "https://api.rebang.today/v1/items?tab=ithome&sub_tab=today&date_type=now&page={page}&version=1",
    "36氪":    "https://api.rebang.today/v1/items?tab=36kr&sub_tab=hotlist&date_type=now&page={page}&version=1",
    "虎扑":    "https://api.rebang.today/v1/items?tab=hupu&sub_tab=all-gambia&date_type=now&page={page}&version=1",
    "少数派":  "https://api.rebang.today/v1/items?tab=sspai&sub_tab=recommend&date_type=now&page={page}&version=1",
    "虎嗅":    "https://api.rebang.today/v1/items?tab=huxiu&sub_tab=hot&date_type=now&page={page}&version=1",
    "澎湃新闻": "https://api.rebang.today/v1/items?tab=thepaper&sub_tab=hot&date_type=now&page={page}&version=1",
    "豆瓣社区": "https://api.rebang.today/v1/items?tab=douban-community&sub_tab=discussion&date_type=now&page={page}&version=1",
    "豆瓣书影音": "https://api.rebang.today/v1/items?tab=douban-media&sub_tab=movie&date_type=now&page={page}&version=1",
    "微信读书": "https://api.rebang.today/v1/items?tab=weread&sub_tab=rising&date_type=now&page={page}&version=1",
    "百度贴吧": "https://api.rebang.today/v1/items?tab=baidu-tieba&sub_tab=topic&date_type=now&page={page}&version=1",
    "吾爱破解": "https://api.rebang.today/v1/items?tab=52pojie&sub_tab=today&date_type=now&page={page}&version=1",
    "掘金":    "https://api.rebang.today/v1/items?tab=juejin&sub_tab=all&date_type=now&page={page}&version=1",
    "InfoQ":   "https://api.rebang.today/v1/items?tab=infoq&sub_tab=day&date_type=now&page={page}&version=1",
    "NGA":     "https://api.rebang.today/v1/items?tab=nga&date_type=now&page={page}&version=1",
}

CONFIG_SOURCE = None
HOT_CONFIG = {}
CONFIG_LOAD_ERROR = None

try:
    CONFIG_SOURCE = load_config()
    HOT_CONFIG = hot_tracker_config(CONFIG_SOURCE)
except ConfigError as exc:
    CONFIG_LOAD_ERROR = exc

PLATFORM_ALIASES = {
    "all": "全站", "top": "全站", "全站": "全站",
    "top-daylong": "全站24小时", "24h": "全站24小时", "全站24小时": "全站24小时",
    "weibo": "微博", "微博": "微博",
    "zhihu": "知乎", "知乎": "知乎",
    "douyin": "抖音", "抖音": "抖音",
    "xiaohongshu": "小红书", "xhs": "小红书", "小红书": "小红书",
    "toutiao": "头条", "头条": "头条", "今日头条": "头条",
    "baidu": "百度", "百度": "百度",
    "bilibili": "B站", "B站": "B站", "b站": "B站",
    "github": "GitHub", "GitHub": "GitHub",
    "v2ex": "V2EX", "V2EX": "V2EX",
    "ithome": "IT之家", "IT之家": "IT之家", "it之家": "IT之家",
    "36kr": "36氪", "36氪": "36氪",
    "hupu": "虎扑", "虎扑": "虎扑",
    "sspai": "少数派", "少数派": "少数派",
    "huxiu": "虎嗅", "虎嗅": "虎嗅",
    "thepaper": "澎湃新闻", "澎湃": "澎湃新闻", "澎湃新闻": "澎湃新闻",
    "douban-community": "豆瓣社区", "豆瓣社区": "豆瓣社区",
    "douban-media": "豆瓣书影音", "豆瓣书影音": "豆瓣书影音",
    "weread": "微信读书", "微信读书": "微信读书",
    "baidu-tieba": "百度贴吧", "贴吧": "百度贴吧", "百度贴吧": "百度贴吧",
    "52pojie": "吾爱破解", "吾爱破解": "吾爱破解",
    "juejin": "掘金", "掘金": "掘金",
    "infoq": "InfoQ", "InfoQ": "InfoQ",
    "nga": "NGA", "NGA": "NGA", "NGA社区": "NGA",
}

# 各平台返回字段映射（统一格式）
FIELD_MAP = {
    "微博":    ["title", "heat_num", "label_name"],
    "知乎":    ["title", "heat_str", "label_str"],
    "抖音":    ["title", "heat_str", "describe"],
    "小红书":  ["title", "view_num", "tag"],
    "百度":    ["word", "hot_score", "hot_tag", "desc"],
    "头条":    ["title", "hot_value", "label"],
    "B站":     ["title", "hot_value", "label"],
    "全站":    ["title", "heat", "tag"],
}

# 429 指数退避配置
MAX_RETRIES = 5
BASE_DELAY = 2  # 秒
MAX_DELAY = 120  # 秒


def configured_platforms():
    """Return platform names from config.hot_tracker.sources."""
    if not HOT_CONFIG:
        return list(ENDPOINTS.keys())
    sources = HOT_CONFIG.get("sources") or []
    if not sources:
        return list(ENDPOINTS.keys())
    platforms = []
    for source in sources:
        platform = PLATFORM_ALIASES.get(str(source))
        if platform == "全站" and str(source).lower() == "all":
            return list(ENDPOINTS.keys())
        if platform and platform not in platforms:
            platforms.append(platform)
    return platforms or list(ENDPOINTS.keys())


def configured_topic_fields():
    if not HOT_CONFIG:
        return []
    fields = HOT_CONFIG.get("topic_fields") or []
    normalized = []
    for field in fields:
        if not isinstance(field, dict):
            continue
        keywords = [str(x) for x in field.get("keywords", []) if str(x).strip()]
        if keywords:
            normalized.append({
                "name": field.get("name") or "内容领域",
                "keywords": keywords,
                "angle_guidance": field.get("angle_guidance") or "",
            })
    return normalized


def configured_max_recommendations(default=6):
    if CONFIG_SOURCE is None:
        return default
    value = get_path(CONFIG_SOURCE, "hot_tracker.selection_preferences.max_recommendations", default)
    try:
        return max(1, int(value))
    except Exception:
        return default


def require_runtime_config():
    if CONFIG_SOURCE is None:
        raise ConfigError(
            "No runtime config found. Start chat onboarding first. "
            "If you prefer the optional visual editor, run `node config-server.mjs`, "
            "open http://127.0.0.1:8765/, and save a real config.yaml."
        )


# ========== 网关与核心请求函数 ==========

def gateway_base_url():
    configured = ""
    if CONFIG_SOURCE is not None:
        configured = get_path(CONFIG_SOURCE, "integrations.hot_rankings.gateway_url", "") or get_path(CONFIG_SOURCE, "integrations.content_gateway.base_url", "")
    return os.environ.get("CONTENT_GATEWAY_BASE_URL") or configured or os.environ.get("CONTENT_GATEWAY_URL", "")


def gateway_api_key():
    return os.environ.get("CONTENT_GATEWAY_API_KEY") or os.environ.get("CONTENT_WORKFLOW_API_KEY", "")


def fetch_gateway_hot(platform, limit=20, page=1):
    if not HAS_REQUESTS:
        raise ImportError("requests 库未安装，请先运行: pip install requests")
    base = gateway_base_url().rstrip("/")
    key = gateway_api_key()
    if not base or not key:
        return None
    if base.endswith("/v1/hot"):
        url = base
    else:
        url = base + "/v1/hot"
    resp = requests.get(
        url,
        params={"platform": platform, "limit": limit, "page": page},
        headers={"X-API-Key": key, "Accept": "application/json"},
        timeout=30,
    )
    payload = None
    try:
        payload = resp.json()
    except Exception:
        payload = None
    if resp.status_code in {401, 402, 403, 429}:
        if isinstance(payload, dict) and payload.get("error_type") == "billing":
            msg = payload.get("message") or payload.get("title") or payload.get("error")
            action = payload.get("suggested_action", "")
            renewal = payload.get("renewal_url", "")
            raise RuntimeError(f"Content Gateway 付费授权失败：{msg} action={action} renewal_url={renewal}")
        raise RuntimeError(f"Content Gateway 授权失败：HTTP {resp.status_code} {resp.text[:300]}")
    resp.raise_for_status()
    if payload is None:
        payload = resp.json()
    if not payload.get("success"):
        if payload.get("error_type") == "billing":
            raise RuntimeError(f"Content Gateway 付费授权失败：{payload.get('message') or payload.get('error')}")
        raise RuntimeError(f"Content Gateway 返回失败：{payload}")
    return payload.get("data", {})


def fetch_hot(platform, url, limit=20):
    gateway_data = fetch_gateway_hot(platform, limit=limit)
    if gateway_data is not None:
        return gateway_data
    return fetch_with_retry(url)


def fetch_with_retry(url, max_retries=MAX_RETRIES, base_delay=BASE_DELAY):
    """
    带指数退避重试的 HTTP GET 请求
    碰到 429：等待 2^n 秒 + 随机抖动，直到成功或达到最大重试次数
    """
    if not HAS_REQUESTS:
        raise ImportError("requests 库未安装，请先运行: pip install requests")

    delay = base_delay

    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            status = resp.status_code

            if status == 200:
                data = resp.json()
                if data.get("code") == 200:
                    return data["data"]
                elif data.get("code") == 1001:
                    # 接口级错误（参数无效等），不重试
                    return {"error": data.get("msg", "invalid request"), "items": []}

            elif status == 429:
                # 触发 429：指数退避 + 随机抖动
                retry_after = resp.headers.get("Retry-After")
                wait_time = int(retry_after) if retry_after else delay
                jitter = random.uniform(0.5, 1.5)
                actual_wait = min(wait_time * jitter, MAX_DELAY)
                print(f"  ⚠️  429 触发（第{attempt+1}次重试），等待 {actual_wait:.1f}s...")
                time.sleep(actual_wait)
                delay = min(delay * 2, MAX_DELAY)
                continue

            elif status == 403 or status == 451:
                return {"error": "forbidden/access denied", "items": []}

            else:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay = min(delay * 2, MAX_DELAY)
                    continue

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay = min(delay * 2, MAX_DELAY)
                continue
            return {"error": str(e), "items": []}

    return {"error": "max retries exceeded", "items": []}


# ========== 数据格式化 ==========

def format_items(platform, items, limit=20):
    """将原始项目列表统一格式化为易读文本"""
    if not items or "error" in items:
        return f"（{platform}：获取失败 - {items.get('error', 'unknown') if items else 'no data'}）"

    # items 可能是 {"list": [...], ...} 的字典，也可能是直接的列表
    if isinstance(items, dict):
        raw = items.get("list")
        if raw is None:
            return f"（{platform}：无数据）"
    else:
        raw = items

    if not raw:
        return f"（{platform}：无数据）"

    # 防御：weibo 等平台 list 字段可能是 JSON 字符串，需要解析
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            return f"（{platform}：数据解析失败）"

    if not isinstance(raw, (list, tuple)):
        return f"（{platform}：数据结构异常）"

    lines = []

    for i, item in enumerate(raw[:limit], 1):
        if not isinstance(item, dict):
            lines.append(f"{i:>2}. {str(item)}")
            continue
        title = item.get("title") or item.get("word", "（无标题）")
        tag = item.get("label_name") or item.get("label_str") or item.get("label") or item.get("tag") or ""
        heat = item.get("heat_num") or item.get("heat_str") or item.get("hot_score") or item.get("hot_value") or item.get("view_num", "")

        tag_str = f" [{tag}]" if tag else ""
        heat_str = f" 🔥{heat}" if heat else ""
        lines.append(f"{i:>2}. {title}{tag_str}{heat_str}")

    return "\n".join(lines)


# ========== 主函数 ==========

def fetch_all(platforms=None, limit_per=20, delay_between=1.5):
    """
    获取所有平台热点数据

    Args:
        platforms: list，要获取的平台，默认全部
        limit_per: int，每个平台返回条数上限
        delay_between: float，两次请求之间间隔（秒），避免触发 429

    Returns:
        dict: {平台名: 原始数据字典}
    """
    if platforms is None:
        require_runtime_config()
        platforms = configured_platforms()

    results = {}
    errors = []

    for platform in platforms:
        if platform not in ENDPOINTS:
            continue

        url_template = ENDPOINTS[platform]
        # B站/全站等需要 page 参数，其他不需要
        url = url_template.format(page=1) if "{page}" in url_template else url_template

        print(f"📡 正在获取 {platform}...")
        data = fetch_hot(platform, url, limit=limit_per)
        results[platform] = data

        if "error" in data and not data.get("items"):
            errors.append(platform)
            print(f"  ❌ {platform} 获取失败：{data.get('error')}")
        else:
            count = len(data.get("list", []))
            print(f"  ✅ {platform} 获取成功，共 {count} 条")

        time.sleep(delay_between + random.uniform(0, 0.5))

    return results


def format_markdown_report(platform, items, limit=20):
    """将原始数据格式化为 Markdown 报告"""
    if not items or "error" in items:
        return f"### {platform}\n\n> 获取失败：{items.get('error', 'unknown') if items else 'no data'}\n"

    if isinstance(items, dict):
        raw = items.get("list")
        if raw is None:
            return f"### {platform}\n\n> 暂无数据\n"
    else:
        raw = items

    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            return f"### {platform}\n\n> 数据解析失败\n"

    if not isinstance(raw, (list, tuple)):
        return f"### {platform}\n\n> 数据结构异常\n"

    lines = [f"### {platform}\n"]
    lines.append(f"| # | 标题 | 标签 | 热度 |")
    lines.append(f"|---|------|------|------|")

    for i, item in enumerate(raw[:limit], 1):
        if not isinstance(item, dict):
            lines.append(f"| {i} | {str(item)} | | |")
            continue
        title = (item.get("title") or item.get("word", "（无标题）")).replace("|", "\\|")
        tag = item.get("label_name") or item.get("label_str") or item.get("label") or item.get("tag") or ""
        heat = item.get("heat_num") or item.get("heat_str") or item.get("hot_score") or item.get("hot_value") or item.get("view_num", "")
        lines.append(f"| {i} | {title} | {tag} | {heat} |")

    return "\n".join(lines)


def generate_content_suggestions(results):
    """
    根据 config.hot_tracker.topic_fields 筛选相关热点，生成选题建议
    返回 Markdown 格式的选题建议段落
    """
    topic_fields = configured_topic_fields()
    if not topic_fields:
        topic_fields = [
            {
                "name": "内容领域",
                "keywords": ["健康", "心理", "旅行", "职场", "家庭"],
                "angle_guidance": "结合账号定位和用户偏好，给出可执行的内容切入角度。",
            }
        ]

    def text_match(text, keywords):
        text = text.lower() if isinstance(text, str) else ""
        for kw in keywords:
            if kw.lower() in text:
                return kw
        return None

    matched = []  # (platform, title, tag, heat, group, matched_keyword, angle_guidance)

    for platform, data in results.items():
        if "error" in data:
            continue
        raw = data.get("list", []) if isinstance(data, dict) else data
        # 防御：list 可能是 JSON 字符串
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:
                continue
        if not isinstance(raw, list):
            continue
        for item in raw:
            if not isinstance(item, dict):
                continue
            title = item.get("title") or item.get("word", "")
            desc = item.get("describe") or item.get("desc", "")
            tag = item.get("label_name") or item.get("label_str") or item.get("label") or item.get("tag") or ""
            heat = item.get("heat_num") or item.get("heat_str") or item.get("hot_score") or item.get("hot_value") or item.get("view_num", "")

            # 标题 + 描述一起匹配
            for field in topic_fields:
                kw = text_match(title, field["keywords"]) or text_match(desc, field["keywords"])
                if kw:
                    matched.append((platform, title, tag, heat, field["name"], kw, field.get("angle_guidance", "")))
                    break

    # 去重（按标题）
    seen = set()
    unique = []
    for m in matched:
        if m[1] not in seen:
            seen.add(m[1])
            unique.append(m)

    if not unique:
        field_names = " / ".join(field["name"] for field in topic_fields)
        return f"### 📝 选题建议\n\n> 今日热点中未发现与「{field_names}」高度相关的话题，建议持续关注。\n"

    lines = ["### 📝 选题建议\n"]
    lines.append(f"> 基于今日热点，筛选出 **{len(unique)} 条** 与你内容方向高度相关的话题\n")

    # 按 group 分组输出
    max_items = configured_max_recommendations()
    for field in topic_fields:
        group = field["name"]
        group_items = [x for x in unique if x[4] == group]
        if not group_items:
            continue
        lines.append(f"**【{group}相关】**\n")
        for i, (platform, title, tag, heat, _, kw, guidance) in enumerate(group_items[:max_items], 1):
            tag_str = f" [{tag}]" if tag else ""
            heat_str = f" 🔥{heat}" if heat else ""
            lines.append(f"{i}. **{title}**{tag_str}（{platform} · 匹配词：{kw}）{heat_str}")
            angle = _suggest_angle(title, kw, group, guidance)
            titles = _suggest_titles(title, group)
            lines.append(f"   → 切入角度：{angle}")
            lines.append(f"   → 标题备选：{titles}")
            lines.append("")

    return "\n".join(lines)


def _suggest_angle(title, matched_keyword, group, angle_guidance=""):
    """根据热点标题和内容定位，给出切入角度"""
    base = f"「{matched_keyword}」切入，"
    if angle_guidance:
        return base + angle_guidance
    return base + f"结合「{group}」内容定位，提炼一个和用户受众相关的观点或实用建议"


def _suggest_titles(title, group):
    """生成3个适合的标题备选"""
    t = title[:12]
    templates = [
        f"从「{t}」事件，我看到一个值得深思的话题",
        f"关于「{t}」，可以这样切入",
        f"「{t}」刷屏背后：你可能忽略的信号",
    ]
    random.shuffle(templates)
    return " / ".join(templates[:3])


def save_markdown_report(platforms=None, limit_per=20, delay_between=1.5):
    """
    生成 Markdown 报告文件，保存到 config.yaml 指定的 hot_topics 路由。
    返回 (filepath, data_dict)
    """
    require_runtime_config()
    route = resolve_route(CONFIG_SOURCE, get_path(CONFIG_SOURCE, "hot_tracker.output_route", "hot_topics"))
    provider = route.get("provider")
    if provider not in {"local", "obsidian"}:
        raise ConfigError(
            f"hot topic report saving currently supports local/obsidian routes only, got: {provider}. "
            "Use the route details to create the document with the matching provider tool."
        )
    report_dir = Path(route["resolved_local_path"])
    report_dir.mkdir(parents=True, exist_ok=True)

    results = fetch_all(platforms=platforms, limit_per=limit_per, delay_between=delay_between)

    today = datetime.now().strftime("%Y-%m-%d")
    filepath = report_dir / f"热点追踪_{today}.md"

    lines = [
        f"# 📊 热点追踪日报",
        f"",
        f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ",
        f"",
        f"---",
        "",
    ]

    for platform in results:
        lines.append(format_markdown_report(platform, results[platform], limit_per))
        lines.append("")

    # 加入选题建议
    lines.append(generate_content_suggestions(results))
    lines.append("")
    lines.append(f"\n---\n*由 Content Hot Tracker 技能自动生成 · {datetime.now().strftime('%Y-%m-%d')}*")

    content = "\n".join(lines)
    filepath.write_text(content, encoding="utf-8")
    print(f"📄 报告已保存：{filepath}")
    return str(filepath), results


def print_all(platforms=None, limit_per=20):
    """格式化输出所有平台热点"""
    require_runtime_config()
    results = fetch_all(platforms=platforms, limit_per=limit_per)

    print(f"\n{'='*60}")
    print(f"📊 今日热点 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    for platform in results:
        data = results[platform]
        print(f"\n📌 {platform}")
        print("-" * 40)
        print(format_items(platform, data, limit=limit_per))

    print(f"\n{'='*60}")
    print("（由 rebang_fetcher.py 生成）")


# ========== CLI 入口 ==========

if __name__ == "__main__":
    import sys

    try:
        if len(sys.argv) == 1:
            print_all()
        else:
            cmd = sys.argv[1]
            if cmd == "list":
                print("支持平台：", "、".join(ENDPOINTS.keys()))
            elif cmd == "md":
                # 生成 Markdown 报告
                save_markdown_report()
            elif cmd == "weibo":
                require_runtime_config()
                data = fetch_hot("微博", ENDPOINTS["微博"], limit=20)
                print(f"\n📌 微博 TOP20\n{'-'*40}\n{format_items('微博', data, 20)}")
            elif cmd == "douyin":
                require_runtime_config()
                url = ENDPOINTS["抖音"]
                data = fetch_hot("抖音", url, limit=20)
                print(f"\n📌 抖音 TOP20\n{'-'*40}\n{format_items('抖音', data, 20)}")
            elif cmd == "zhihu":
                require_runtime_config()
                url = ENDPOINTS["知乎"]
                data = fetch_hot("知乎", url, limit=20)
                print(f"\n📌 知乎 TOP20\n{'-'*40}\n{format_items('知乎', data, 20)}")
            elif cmd == "xiaohongshu":
                require_runtime_config()
                url = ENDPOINTS["小红书"]
                data = fetch_hot("小红书", url, limit=20)
                print(f"\n📌 小红书 TOP20\n{'-'*40}\n{format_items('小红书', data, 20)}")
            elif cmd == "baidu":
                require_runtime_config()
                url = ENDPOINTS["百度"]
                data = fetch_hot("百度", url, limit=20)
                print(f"\n📌 百度热搜 TOP20\n{'-'*40}\n{format_items('百度', data, 20)}")
            elif cmd == "toutiao":
                require_runtime_config()
                url = ENDPOINTS["头条"]
                data = fetch_hot("头条", url, limit=20)
                print(f"\n📌 今日头条 TOP20\n{'-'*40}\n{format_items('头条', data, 20)}")
            elif cmd == "bilibili":
                require_runtime_config()
                url = ENDPOINTS["B站"]
                data = fetch_hot("B站", url, limit=20)
                print(f"\n📌 B站 TOP20\n{'-'*40}\n{format_items('B站', data, 20)}")
            else:
                print(f"未知命令: {cmd}")
                print("用法: python rebang_fetcher.py [list|weibo|douyin|zhihu|xiaohongshu|baidu|toutiao|bilibili|md]")
    except ConfigError as exc:
        print(f"配置缺失：{exc}")
        sys.exit(1)
