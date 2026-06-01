"""
本质工坊 · HTML交互管线
从元素层读取 → 课程骨架模板 → 元素直接嵌入 → 交互模块接入 → 完整HTML

HTML交互管线是能力最完整的管线：
- SVG 直接嵌入，保留交互能力
- 动画直接嵌入，保留完整效果
- 交互模块直接接入，保留全部交互
- 音频可嵌入，保留播放控制

参考: huashu-design 的 Interactive Prototype 能力
      TeachAny 的互动课件系统

用法:
  python -m scripts.pipelines.html.generator --elements output/elements/ --output output/html/
  python -m scripts.pipelines.html.generator --elements output/elements/ --output output/html/ --brand-spec brand-spec.json
  python -m scripts.pipelines.html.generator --elements output/elements/ --output output/html/ --modules slope-navigator,three-stage-progress
"""

import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..", "..", "..")
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "templates", "course-skeleton.html")

AVAILABLE_MODULES = [
    "slope-navigator",
    "three-stage-progress",
    "knowledge-graph",
    "card-flip",
    "comparison-table",
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
      --secondary: {secondary_color};
      --bg: {bg_color};
      --text: {text_color};
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Noto Sans SC", sans-serif;
      --font-mono: "SF Mono", "Fira Code", "Cascadia Code", monospace;
      --radius: 8px;
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: var(--font-sans);
      background: var(--bg);
      color: var(--text);
      line-height: 1.8;
    }}
    nav {{
      position: sticky; top: 0; z-index: 100;
      background: var(--bg); border-bottom: 1px solid #e5e7eb;
      padding: 12px 24px;
    }}
    main {{
      max-width: 800px; margin: 0 auto; padding: 24px 16px;
    }}
    section {{ margin-bottom: 48px; }}
    h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 16px; }}
    h2 {{ font-size: 22px; font-weight: 600; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #e5e7eb; }}
    h3 {{ font-size: 18px; font-weight: 600; margin-bottom: 8px; }}
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


def generate_html(elements_dir, output_dir, brand_spec_path=None, modules=None, title="课程"):
    print("[HTML Pipeline] Starting...")

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

    primary_color = brand.get("colors", {}).get("primary", "#2563eb")
    secondary_color = brand.get("colors", {}).get("secondary", "#7c3aed")
    bg_color = brand.get("colors", {}).get("bg", "#ffffff")
    text_color = brand.get("colors", {}).get("text", "#1f2937")

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
        secondary_color=secondary_color,
        bg_color=bg_color,
        text_color=text_color,
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
    print("[HTML Pipeline] Done.")


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · HTML交互管线")
    parser.add_argument("--elements", required=True, help="元素层目录路径")
    parser.add_argument("--output", required=True, help="输出目录路径")
    parser.add_argument("--brand-spec", default=None, help="品牌规格文件路径")
    parser.add_argument("--modules", default=None, help="交互模块列表（逗号分隔）")
    parser.add_argument("--title", default="课程", help="课程标题")
    args = parser.parse_args()

    modules = None
    if args.modules:
        modules = [m.strip() for m in args.modules.split(",")]
        invalid = [m for m in modules if m not in AVAILABLE_MODULES]
        if invalid:
            print(f"WARNING: Unknown modules: {invalid}")
            print(f"  Available: {AVAILABLE_MODULES}")

    generate_html(args.elements, args.output, args.brand_spec, modules, args.title)


if __name__ == "__main__":
    main()
