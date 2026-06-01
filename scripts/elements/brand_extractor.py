"""
本质工坊 · 品牌素材自动提取
从公众号文章或Markdown文件中自动提取品牌素材信息，生成brand-spec.json

三步协议：
  1. 问 - 扫描文章/Markdown中的品牌信号（标题、配色、关键词）
  2. 提取 - 从信号中提炼品牌要素（颜色、字体、图标偏好）
  3. 固化 - 生成brand-spec.json，供视频模板和图片生成使用

用法:
  python brand_extractor.py --url https://mp.weixin.qq.com/s/xxx
  python brand_extractor.py --article output/article.md
  python brand_extractor.py --article output/article.md --output templates/brand-spec.json
"""

import argparse
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_BRAND_SPEC = os.path.join(SCRIPT_DIR, "..", "..", "templates", "brand-spec.json")

COLOR_PATTERNS = {
    "暖色系": ["#D4763A", "#C96442", "#8B5E3C", "#F0C27F", "#FAF7F2"],
    "冷色系": ["#00D2FF", "#4ECDC4", "#16213E", "#0F0F23", "#7A7A9E"],
    "深色系": ["#0F0F23", "#1A1A2E", "#16213E", "#3C2415", "#111111"],
    "浅色系": ["#FAF7F2", "#FDF6EC", "#FFFFFF", "#FAFAFA", "#F5F5F5"],
    "自然系": ["#0D1F0D", "#142814", "#C9A84C", "#8FAA6B", "#6BA3A0"],
}

KEYWORD_THEME_MAP = {
    "技术": "dark",
    "编程": "dark",
    "代码": "dark",
    "AI": "dark",
    "工程": "dark",
    "算法": "dark",
    "数据": "dark",
    "温暖": "warm",
    "生活": "warm",
    "教育": "warm",
    "成长": "warm",
    "阅读": "warm",
    "写作": "warm",
    "极简": "minimal",
    "设计": "minimal",
    "美学": "minimal",
    "哲学": "minimal",
    "自然": "nature",
    "生态": "nature",
    "环保": "nature",
    "中医": "nature",
    "养生": "nature",
}


def detect_theme_from_content(text):
    scores = {"dark": 0, "warm": 0, "minimal": 0, "nature": 0}
    for keyword, theme in KEYWORD_THEME_MAP.items():
        count = text.count(keyword)
        scores[theme] += count
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "dark"
    return best


def extract_brand_from_markdown(markdown, title=""):
    theme = detect_theme_from_content(markdown)

    heading_count = len(re.findall(r'^#{1,4}\s+', markdown, re.MULTILINE))
    bullet_count = len(re.findall(r'^[-*]\s+', markdown, re.MULTILINE))
    quote_count = len(re.findall(r'^>\s+', markdown, re.MULTILINE))
    code_count = len(re.findall(r'```', markdown))

    icon_prefs = []
    if code_count > 2 or "代码" in markdown or "编程" in markdown:
        icon_prefs.extend(["layers", "zap", "hexagon"])
    if quote_count > 2:
        icon_prefs.extend(["lightbulb", "diamond"])
    if bullet_count > 5:
        icon_prefs.extend(["target", "check", "arrow"])
    if "对比" in markdown or "vs" in markdown.lower():
        icon_prefs.append("scale")
    if not icon_prefs:
        icon_prefs = ["brain", "lightbulb", "target", "layers", "zap"]

    brand_name = title.split("：")[0].split(":")[0].split("—")[0].strip() if title else ""
    if len(brand_name) > 20:
        brand_name = brand_name[:20]

    tagline = ""
    tagline_match = re.search(r'^>\s*(.{10,50})', markdown, re.MULTILINE)
    if tagline_match:
        tagline = tagline_match.group(1).strip()

    brand_spec = {
        "brand": {
            "name": brand_name,
            "tagline": tagline,
            "description": f"Auto-extracted from article: {title}"
        },
        "colors": {
            "primary": COLOR_PATTERNS.get(theme + "系", COLOR_PATTERNS["冷色系"])[0],
            "secondary": COLOR_PATTERNS.get(theme + "系", COLOR_PATTERNS["暖色系"])[1],
            "accent": COLOR_PATTERNS.get(theme + "系", COLOR_PATTERNS["冷色系"])[2],
            "background_dark": COLOR_PATTERNS["深色系"][0],
            "background_light": COLOR_PATTERNS["浅色系"][0],
            "text_primary": "#F0F0F0" if theme in ("dark", "nature") else "#3C2415",
            "text_secondary": "#7A7A9E" if theme in ("dark", "nature") else "#8B7355",
            "success": "#4ECDC4" if theme == "dark" else "#5B8C5A",
            "warning": "#FFE66D" if theme == "dark" else "#D4763A",
        },
        "fonts": {
            "heading": "'PingFang SC', 'Microsoft YaHei', sans-serif",
            "body": "'PingFang SC', 'Microsoft YaHei', sans-serif",
            "mono": "'JetBrains Mono', 'Fira Code', monospace"
        },
        "icons": {
            "style": "stroke",
            "weight": 2,
            "preferred": list(dict.fromkeys(icon_prefs))[:6]
        },
        "spacing": {
            "card_radius": 32,
            "card_padding": 40,
            "element_gap": 24
        },
        "animation": {
            "default_easing": "expoOut",
            "enter_duration": 0.5,
            "exit_duration": 0.4,
            "stagger_delay": 0.25
        },
        "rules": {
            "no_gradient_text": True,
            "no_emoji_icons": True,
            "no_purple_primary": True,
            "max_colors_per_slide": 3,
            "min_contrast_ratio": 4.5,
            "card_must_have_border": True,
            "background_must_have_texture": True
        },
        "detected_theme": theme
    }

    return brand_spec


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · 品牌素材自动提取")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", type=str, help="公众号文章URL")
    group.add_argument("--article", type=str, help="本地Markdown文章路径")

    parser.add_argument("--output", "-o", default=None, help="输出brand-spec.json路径")
    parser.add_argument("--print-only", action="store_true", help="仅打印结果，不保存文件")

    args = parser.parse_args()

    print("[1/3] Loading article...")
    if args.url:
        sys.path.insert(0, os.path.join(SCRIPT_DIR, "..", "shared"))
        from article_fetcher import fetch_article_by_url
        article = fetch_article_by_url(args.url)
        if not article:
            print("ERROR: Could not fetch article.")
            sys.exit(1)
        markdown = article.get("content_markdown", "")
        title = article.get("title", "")
    else:
        with open(args.article, "r", encoding="utf-8") as f:
            markdown = f.read()
        title_match = re.match(r'^#\s+(.+)', markdown)
        title = title_match.group(1).strip() if title_match else os.path.basename(args.article)

    print(f"  Title: {title}")
    print(f"  Content length: {len(markdown)} chars")

    print("\n[2/3] Extracting brand signals...")
    brand_spec = extract_brand_from_markdown(markdown, title)
    print(f"  Detected theme: {brand_spec['detected_theme']}")
    print(f"  Primary color: {brand_spec['colors']['primary']}")
    print(f"  Icon preferences: {brand_spec['icons']['preferred']}")

    print("\n[3/3] Saving brand spec...")
    if args.print_only:
        print(json.dumps(brand_spec, ensure_ascii=False, indent=2))
    else:
        output_path = args.output or DEFAULT_BRAND_SPEC
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(brand_spec, f, ensure_ascii=False, indent=2)
        print(f"  Saved: {output_path}")

    print("\n[DONE] Brand spec extracted successfully!")


if __name__ == "__main__":
    main()
