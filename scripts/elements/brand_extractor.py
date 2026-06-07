"""
本质工坊 · 品牌素材自动提取
从公众号文章或Markdown文件中自动提取品牌素材信息，生成brand-spec.json

配色策略：原则驱动——从内容推导强调色，默认深色方案
  - 技术类 → 青/蓝系
  - 人文类 → 暖金/琥珀系
  - 自然类 → 绿/棕系
  - 认知类 → 靛蓝/紫罗兰系
  - 无明确线索时默认 #FFD700

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

# ─── 内容→强调色映射 ────────────────────────────────────────
# 从文章关键词推导强调色系，而非硬编码固定色值

ACCENT_PALETTES = {
    "tech": {
        "primary": "#00D2FF",
        "accent": "#4ECDC4",
        "success": "#4ECDC4",
        "warning": "#FFD700",
    },
    "humanities": {
        "primary": "#FFD700",
        "accent": "#F0C27F",
        "success": "#8FAA6B",
        "warning": "#D4763A",
    },
    "nature": {
        "primary": "#8FAA6B",
        "accent": "#C9A84C",
        "success": "#8FAA6B",
        "warning": "#C9A84C",
    },
    "cognition": {
        "primary": "#7C83FF",
        "accent": "#A78BFA",
        "success": "#4ECDC4",
        "warning": "#FFD700",
    },
    "default": {
        "primary": "#FFD700",
        "accent": "#FFD700",
        "success": "#4ECDC4",
        "warning": "#FFD700",
    },
}

KEYWORD_CATEGORY_MAP = {
    # tech
    "技术": "tech", "编程": "tech", "代码": "tech", "AI": "tech",
    "工程": "tech", "算法": "tech", "数据": "tech", "架构": "tech",
    "开发": "tech", "软件": "tech", "API": "tech", "框架": "tech",
    # humanities
    "温暖": "humanities", "生活": "humanities", "教育": "humanities",
    "成长": "humanities", "阅读": "humanities", "写作": "humanities",
    "人文": "humanities", "历史": "humanities", "文化": "humanities",
    # nature
    "自然": "nature", "生态": "nature", "环保": "nature",
    "中医": "nature", "养生": "nature", "本草": "nature",
    "植物": "nature", "动物": "nature",
    # cognition
    "认知": "cognition", "思维": "cognition", "本质": "cognition",
    "哲学": "cognition", "深度": "cognition", "智慧": "cognition",
    "决策": "cognition", "逻辑": "cognition",
}


def detect_content_category(text):
    """从内容关键词推导内容类别。"""
    scores = {"tech": 0, "humanities": 0, "nature": 0, "cognition": 0}
    for keyword, category in KEYWORD_CATEGORY_MAP.items():
        count = text.count(keyword)
        scores[category] += count
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "default"
    return best


def extract_brand_from_markdown(markdown, title=""):
    """提取品牌素材，从内容推导强调色系。"""

    # 从内容推导类别和强调色
    category = detect_content_category(markdown)
    palette = ACCENT_PALETTES.get(category, ACCENT_PALETTES["default"])

    icon_prefs = []
    code_count = len(re.findall(r'```', markdown))
    quote_count = len(re.findall(r'^>\s+', markdown, re.MULTILINE))
    bullet_count = len(re.findall(r'^[-*]\s+', markdown, re.MULTILINE))
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
            "primary": palette["primary"],
            "secondary": "#FFFFFF",
            "accent": palette["accent"],
            "background_dark": "#0A0A0A",
            "background_light": "#141414",
            "text_primary": "#FFFFFF",
            "text_secondary": "#B0B0B0",
            "success": palette["success"],
            "warning": palette["warning"],
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
        "detected_category": category,
        "detected_theme": "dark"
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
    print(f"  Detected category: {brand_spec.get('detected_category', 'default')}")
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
