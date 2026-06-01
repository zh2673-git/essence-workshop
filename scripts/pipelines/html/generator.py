"""
本质工坊 · HTML交互管线
从元素层读取 → 课程骨架模板 → 元素直接嵌入 → 交互模块接入 → 完整HTML

HTML交互管线是能力最完整的管线：
- SVG 直接嵌入，保留交互能力
- 动画直接嵌入，保留完整效果
- 交互模块直接接入，保留全部交互
- 音频可嵌入，保留播放控制

模式:
  scroll  - 连续滚动（默认，v1行为）
  paged   - 分页课件（v2，TeachAny风格）

用法:
  python -m scripts.pipelines.html.generator --elements output/elements/ --output output/html/
  python -m scripts.pipelines.html.generator --elements output/elements/ --output output/html/ --mode paged
  python -m scripts.pipelines.html.generator --elements output/elements/ --output output/html/ --brand-spec brand-spec.json
  python -m scripts.pipelines.html.generator --elements output/elements/ --output output/html/ --modules slope-navigator,three-stage-progress
"""

import argparse
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..", "..", "..")
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "templates", "course-skeleton.html")
TEMPLATE_V2_PATH = os.path.join(PROJECT_ROOT, "templates", "course-skeleton-v2.html")

AVAILABLE_MODULES = [
    "slope-navigator",
    "three-stage-progress",
    "knowledge-graph",
    "card-flip",
    "comparison-table",
    "ai-companion",
    "tts-narrator",
    "section-hints",
    "mentor-card",
    "quiz-widget",
]

COURSE_SKELETON_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    :root {{
      --primary: {primary_color};
      --accent: {accent_color};
      --bg: {bg_color};
      --fg: {fg_color};
      --muted: {muted_color};
      --border: {border_color};
      --primary-dim: {primary_dim};
      --accent-dim: {accent_dim};
      --font-display: {font_display};
      --font-body: {font_body};
      --font-mono: {font_mono};
      --radius: 8px;
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: var(--font-body);
      background: var(--bg);
      color: var(--fg);
      line-height: 1.8;
    }}
    nav {{
      position: sticky; top: 0; z-index: 100;
      background: var(--bg); border-bottom: 1px solid var(--border);
      padding: 12px 24px;
    }}
    main {{
      max-width: 800px; margin: 0 auto; padding: 24px 16px;
    }}
    section {{ margin-bottom: 48px; }}
    h1 {{ font-family: var(--font-display); font-size: 28px; font-weight: 700; margin-bottom: 16px; }}
    h2 {{ font-size: 22px; font-weight: 600; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid var(--primary); }}
    h3 {{ font-size: 18px; font-weight: 600; margin-bottom: 8px; color: var(--primary); }}
    p {{ margin-bottom: 12px; }}
    ul, ol {{ margin-bottom: 12px; padding-left: 24px; }}
    code {{
      font-family: var(--font-mono); background: #f3f4f6; padding: 2px 6px;
      border-radius: 4px; font-size: 0.9em;
    }}
    pre {{
      background: #1f2937; color: #e5e7eb; padding: 16px; border-radius: var(--radius);
      overflow-x: auto; margin-bottom: 16px;
    }}
    pre code {{ background: none; padding: 0; }}
    blockquote {{
      border-left: 4px solid var(--primary); padding: 12px 20px;
      margin: 16px 0; background: var(--primary-dim);
      border-radius: 0 var(--radius) var(--radius) 0;
    }}
    svg {{ max-width: 100%; height: auto; }}
    @media (max-width: 768px) {{
      main {{ padding: 16px 12px; }}
      h1 {{ font-size: 22px; }}
      h2 {{ font-size: 18px; }}
    }}
    @media print {{
      nav {{ display: none; }}
      section {{ page-break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <nav>
    <strong>{title}</strong>
  </nav>
  <main>
    {content}
  </main>
  {scripts}
</body>
</html>"""


def load_elements(elements_dir):
    elements = {"text": [], "graphics": [], "animations": [], "audio": [], "interactions": [], "data": []}
    if not os.path.isdir(elements_dir):
        print(f"WARNING: Elements directory not found: {elements_dir}")
        return elements

    for category in elements:
        cat_dir = os.path.join(elements_dir, category)
        if os.path.isdir(cat_dir):
            for f in sorted(os.listdir(cat_dir)):
                if f.startswith(".") or f == "__init__.py":
                    continue
                fpath = os.path.join(cat_dir, f)
                if os.path.isfile(fpath):
                    elements[category].append(fpath)

    return elements


def render_text_elements(text_files):
    html_parts = []
    for fpath in text_files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        html_parts.append(f'<section>\n{content}\n</section>')
    return "\n\n".join(html_parts)


def render_svg_elements(graphic_files):
    html_parts = []
    for fpath in graphic_files:
        if fpath.endswith(".svg"):
            with open(fpath, "r", encoding="utf-8") as f:
                svg_content = f.read()
            html_parts.append(f'<figure>\n{svg_content}\n</figure>')
    return "\n\n".join(html_parts)


def render_modules(modules, modules_dir):
    html_parts = []
    for mod_name in modules:
        mod_dir = os.path.join(modules_dir, mod_name)
        if not os.path.isdir(mod_dir):
            print(f"  WARNING: Module not found: {mod_name}")
            continue
        mod_html = os.path.join(mod_dir, "index.html")
        mod_js = os.path.join(mod_dir, "script.js")
        mod_css = os.path.join(mod_dir, "style.css")
        if os.path.isfile(mod_css):
            with open(mod_css, "r", encoding="utf-8") as f:
                html_parts.append(f'<style>\n{f.read()}\n</style>')
        if os.path.isfile(mod_html):
            with open(mod_html, "r", encoding="utf-8") as f:
                html_parts.append(f.read())
        if os.path.isfile(mod_js):
            with open(mod_js, "r", encoding="utf-8") as f:
                html_parts.append(f'<script>\n{f.read()}\n</script>')
    return "\n\n".join(html_parts)


def load_template():
    if os.path.isfile(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return COURSE_SKELETON_TEMPLATE


def load_template_v2():
    if os.path.isfile(TEMPLATE_V2_PATH):
        with open(TEMPLATE_V2_PATH, "r", encoding="utf-8") as f:
            return f.read()
    print("WARNING: course-skeleton-v2.html not found, falling back to v1 template")
    return load_template()


def infer_page_type(section_index, total_sections, heading=""):
    if section_index == 0:
        return "cover"
    if section_index == total_sections - 1:
        return "summary"
    heading_lower = heading.lower()
    if any(kw in heading_lower for kw in ["测试", "练习", "quiz", "测验"]):
        return "quiz"
    if any(kw in heading_lower for kw in ["互动", "探究", "实验", "interactive"]):
        return "interactive"
    if any(kw in heading_lower for kw in ["目标", "目的", "objective"]):
        return "objectives"
    return "concept"


def parse_markdown_to_sections(md_content):
    sections = []
    current_heading = ""
    current_body_lines = []

    for line in md_content.split("\n"):
        if re.match(r"^#{1,3}\s", line):
            if current_heading or current_body_lines:
                sections.append({
                    "heading": current_heading,
                    "body": "\n".join(current_body_lines).strip(),
                })
            current_heading = re.sub(r"^#{1,3}\s+", "", line).strip()
            current_body_lines = []
        else:
            current_body_lines.append(line)

    if current_heading or current_body_lines:
        sections.append({
            "heading": current_heading,
            "body": "\n".join(current_body_lines).strip(),
        })

    return sections


def md_to_html(text):
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    lines = text.split("\n")
    html_lines = []
    in_list = False
    list_type = "ul"
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
                list_type = "ul"
            html_lines.append(f"<li>{stripped[2:]}</li>")
        elif re.match(r"^\d+\.\s", stripped):
            if not in_list:
                html_lines.append("<ol>")
                in_list = True
                list_type = "ol"
            list_text = re.sub(r'^\d+\.\s', '', stripped)
            html_lines.append(f"<li>{list_text}</li>")
        else:
            if in_list:
                html_lines.append(f"</{list_type}>")
                in_list = False
            if stripped:
                html_lines.append(f"<p>{stripped}</p>")
    if in_list:
        html_lines.append(f"</{list_type}>")
    return "\n".join(html_lines)


def build_paged_slides(sections, elements, brand, modules, modules_dir):
    total = len(sections)
    if total == 0:
        return ""

    slide_parts = []
    for i, section in enumerate(sections):
        page_type = infer_page_type(i, total, section["heading"])
        heading = section["heading"] or f"第{i+1}页"
        body_html = md_to_html(section["body"]) if section["body"] else ""

        if page_type == "cover":
            slide_html = f'''<section class="slide-page" data-page-index="{i}" data-page-type="cover">
  <div class="cover-decoration"></div>
  <div class="cover-decoration-2"></div>
  <div class="slide-content">
    <h1>{heading}</h1>
    <p class="subtitle">{body_html.replace("<p>", "").replace("</p>", "") if body_html else ""}</p>
  </div>
</section>'''

        elif page_type == "objectives":
            items = ""
            for line in section["body"].split("\n"):
                line = line.strip()
                if line.startswith("- ") or line.startswith("* "):
                    items += f"<li>{line[2:]}</li>\n"
                elif line:
                    items += f"<li>{line}</li>\n"
            if not items:
                items = "<li>（待补充）</li>"
            slide_html = f'''<section class="slide-page" data-page-index="{i}" data-page-type="objectives">
  <div class="slide-content">
    <h2>{heading}</h2>
    <ul class="objective-list">
      {items}
    </ul>
  </div>
</section>'''

        elif page_type == "quiz":
            options = ""
            for line in section["body"].split("\n"):
                line = line.strip()
                if line.startswith("- ") or line.startswith("* "):
                    options += f'<div class="quiz-option">{line[2:]}</div>\n'
                elif line:
                    options += f'<div class="quiz-option">{line}</div>\n'
            slide_html = f'''<section class="slide-page" data-page-index="{i}" data-page-type="quiz">
  <div class="slide-content">
    <h2>{heading}</h2>
    {options}
  </div>
</section>'''

        elif page_type == "summary":
            slide_html = f'''<section class="slide-page" data-page-index="{i}" data-page-type="summary">
  <div class="slide-content">
    <h2>{heading}</h2>
    {body_html}
  </div>
</section>'''

        else:
            slide_html = f'''<section class="slide-page" data-page-index="{i}" data-page-type="{page_type}">
  <div class="slide-content">
    <h2>{heading}</h2>
    {body_html}
  </div>
</section>'''

        slide_parts.append(slide_html)

    if elements["graphics"]:
        for fpath in elements["graphics"]:
            if fpath.endswith(".svg"):
                with open(fpath, "r", encoding="utf-8") as f:
                    svg_content = f.read()
                idx = len(slide_parts)
                slide_parts.append(f'''<section class="slide-page" data-page-index="{idx}" data-page-type="concept">
  <div class="slide-content">
    <figure>
      {svg_content}
    </figure>
  </div>
</section>''')

    if modules:
        mod_html = render_modules(modules, modules_dir)
        if mod_html:
            idx = len(slide_parts)
            slide_parts.append(f'''<section class="slide-page" data-page-index="{idx}" data-page-type="interactive">
  <div class="slide-content">
    {mod_html}
  </div>
</section>''')

    return "\n\n".join(slide_parts)


def generate_html(elements_dir, output_dir, brand_spec_path=None, modules=None, title="课程", mode="scroll"):
    print(f"[HTML Pipeline] Starting... (mode={mode})")

    if mode == "paged":
        template = load_template_v2()
        print(f"  Template v2 loaded: {TEMPLATE_V2_PATH}")
    else:
        template = load_template()
        if template != COURSE_SKELETON_TEMPLATE:
            print(f"  Template loaded: {TEMPLATE_PATH}")

    elements = load_elements(elements_dir)
    print(f"  Elements loaded: {sum(len(v) for v in elements.values())} files")

    brand = {}
    if brand_spec_path and os.path.isfile(brand_spec_path):
        with open(brand_spec_path, "r", encoding="utf-8") as f:
            brand = json.load(f)
        print(f"  Brand spec loaded: {brand_spec_path}")

    colors = brand.get("colors", {})
    derived = brand.get("derived", {})
    fonts = brand.get("fonts", {})

    primary_color = colors.get("primary", "#0F766E")
    accent_color = colors.get("accent", "#E94560")
    bg_color = colors.get("bg", "#FAFAFA")
    fg_color = colors.get("fg", "#1A1A1A")
    muted_color = colors.get("muted", "#7A7A9E")
    border_color = colors.get("border", "#E5E7EB")

    primary_dim = derived.get("primary-dim", "rgba(15,118,110,0.08)")
    accent_dim = derived.get("accent-dim", "rgba(233,69,96,0.08)")
    card_bg = derived.get("card-bg", "rgba(255,255,255,0.7)")
    card_border = derived.get("card-border", "rgba(0,0,0,0.06)")
    primary_rgb = derived.get("primary-rgb", "15,118,110")
    accent_rgb = derived.get("accent-rgb", "233,69,96")

    font_display = fonts.get("display", "'Noto Serif SC', Georgia, serif")
    font_body = fonts.get("body", "-apple-system, BlinkMacSystemFont, 'PingFang SC', 'Noto Sans SC', sans-serif")
    font_mono = fonts.get("mono", "'JetBrains Mono', 'Fira Code', monospace")

    if mode == "paged":
        md_content = ""
        if elements["text"]:
            for fpath in elements["text"]:
                with open(fpath, "r", encoding="utf-8") as f:
                    md_content += f.read() + "\n\n"

        if not md_content.strip():
            md_content = f"# {title}\n\n## 概述\n\n这是一个由本质工坊生成的分页课件示例。\n\n## 核心概念\n\n本课件展示了分页交互课件的完整效果。\n\n## 总结\n\n感谢阅读。"

        sections = parse_markdown_to_sections(md_content)
        modules_dir = os.path.join(PROJECT_ROOT, "modules")
        content = build_paged_slides(sections, elements, brand, modules, modules_dir)
        scripts = ""
    else:
        content_parts = []
        if elements["text"]:
            content_parts.append(render_text_elements(elements["text"]))
        if elements["graphics"]:
            content_parts.append(render_svg_elements(elements["graphics"]))
        if elements["animations"]:
            for fpath in elements["animations"]:
                if fpath.endswith(".svg"):
                    with open(fpath, "r", encoding="utf-8") as f:
                        content_parts.append(f.read())
                elif fpath.endswith(".css"):
                    with open(fpath, "r", encoding="utf-8") as f:
                        content_parts.append(f'<style>\n{f.read()}\n</style>')

        scripts_parts = []
        if modules:
            modules_dir = os.path.join(PROJECT_ROOT, "modules")
            mod_html = render_modules(modules, modules_dir)
            if mod_html:
                content_parts.append(mod_html)

        content = "\n\n".join(content_parts)
        scripts = "\n".join(scripts_parts)

    html = template.format(
        title=title,
        content=content,
        scripts=scripts,
        primary_color=primary_color,
        accent_color=accent_color,
        bg_color=bg_color,
        fg_color=fg_color,
        muted_color=muted_color,
        border_color=border_color,
        primary_dim=primary_dim,
        accent_dim=accent_dim,
        card_bg=card_bg,
        card_border=card_border,
        primary_rgb=primary_rgb,
        accent_rgb=accent_rgb,
        font_display=font_display,
        font_body=font_body,
        font_mono=font_mono,
    )

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    file_size_kb = os.path.getsize(output_path) / 1024
    print(f"  Output: {output_path}")
    print(f"  File size: {file_size_kb:.1f} KB")
    if file_size_kb > 5120:
        print("  WARNING: File size exceeds 5MB limit. Consider splitting or compressing SVGs.")

    if mode == "paged":
        page_count = html.count('class="slide-page"')
        print(f"  Pages: {page_count}")
        if page_count < 12:
            print(f"  WARNING: Less than 12 pages ({page_count}). Consider adding more content.")

    print("[HTML Pipeline] Done.")


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · HTML交互管线")
    parser.add_argument("--elements", required=True, help="元素层目录路径")
    parser.add_argument("--output", required=True, help="输出目录路径")
    parser.add_argument("--brand-spec", default=None, help="品牌规格文件路径")
    parser.add_argument("--modules", default=None, help="交互模块列表（逗号分隔）")
    parser.add_argument("--title", default="课程", help="课程标题")
    parser.add_argument("--mode", default="scroll", choices=["scroll", "paged"], help="输出模式：scroll=连续滚动, paged=分页课件")
    args = parser.parse_args()

    modules = None
    if args.modules:
        modules = [m.strip() for m in args.modules.split(",")]
        invalid = [m for m in modules if m not in AVAILABLE_MODULES]
        if invalid:
            print(f"WARNING: Unknown modules: {invalid}")
            print(f"  Available: {AVAILABLE_MODULES}")

    generate_html(args.elements, args.output, args.brand_spec, modules, args.title, args.mode)


if __name__ == "__main__":
    main()
