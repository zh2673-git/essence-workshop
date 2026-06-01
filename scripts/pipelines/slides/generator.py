"""
本质工坊 · 演示管线（Reveal.js）
从元素层读取 → 幻灯片结构生成 → 图形嵌入 → Reveal.js模板 → 演示HTML

参考: huashu-design 的 HTML Slides 能力
      Reveal.js 官方文档

用法:
  python -m scripts.pipelines.slides.generator --elements output/elements/ --output output/slides/
  python -m scripts.pipelines.slides.generator --elements output/elements/ --output output/slides/ --title "演示标题"
  python -m scripts.pipelines.slides.generator --elements output/elements/ --output output/slides/ --theme black
"""

import argparse
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

REVEAL_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/theme/{theme}.css">
  <style>
    .reveal h1, .reveal h2, .reveal h3 {{ font-weight: 700; }}
    .reveal section {{ text-align: left; }}
    .reveal svg {{ max-width: 90%; height: auto; }}
    .reveal pre {{ width: 100%; font-size: 0.55em; }}
    .reveal figure {{ margin: 16px 0; }}
    .reveal figcaption {{ font-size: 0.6em; color: #6b7280; }}
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
{slides}
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5/plugin/highlight/highlight.js"></script>
  <script>
    Reveal.initialize({{
      hash: true,
      slideNumber: true,
      transition: 'slide',
      plugins: [ RevealHighlight ]
    }});
  </script>
</body>
</html>"""

VALID_THEMES = ["black", "white", "league", "beige", "sky", "night", "serif", "simple", "solarized"]


def markdown_to_slides(markdown_text):
    slides = []
    current_slide_lines = []
    current_level = 0

    for line in markdown_text.split("\n"):
        h_match = re.match(r'^(#{1,3})\s+(.+)$', line)
        if h_match:
            level = len(h_match.group(1))
            heading = h_match.group(2)

            if current_slide_lines:
                slides.append({
                    "level": current_level,
                    "content": "\n".join(current_slide_lines),
                })
                current_slide_lines = []

            current_level = level
            current_slide_lines.append(line)
        else:
            current_slide_lines.append(line)

    if current_slide_lines:
        slides.append({
            "level": current_level,
            "content": "\n".join(current_slide_lines),
        })

    return slides


def slide_to_html(slide):
    content = slide["content"]
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', content, flags=re.MULTILINE)
    content = re.sub(r'^- (.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
    content = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', content, flags=re.MULTILINE)
    content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)

    if slide["level"] == 1:
        return f'<section>\n{content}\n</section>'
    else:
        return f'<section>\n{content}\n</section>'


def load_text_elements(elements_dir):
    text_dir = os.path.join(elements_dir, "text")
    texts = []
    if os.path.isdir(text_dir):
        for f in sorted(os.listdir(text_dir)):
            if f.endswith(".md"):
                with open(os.path.join(text_dir, f), "r", encoding="utf-8") as fh:
                    texts.append(fh.read())
    return texts


def load_svg_elements(elements_dir):
    graphics_dir = os.path.join(elements_dir, "graphics")
    svgs = {}
    if os.path.isdir(graphics_dir):
        for f in sorted(os.listdir(graphics_dir)):
            if f.endswith(".svg"):
                name = os.path.splitext(f)[0]
                with open(os.path.join(graphics_dir, f), "r", encoding="utf-8") as fh:
                    svgs[name] = fh.read()
    return svgs


def generate_slides(elements_dir, output_dir, title="演示", theme="white"):
    print("[Slides Pipeline] Starting...")

    texts = load_text_elements(elements_dir)
    svgs = load_svg_elements(elements_dir)
    print(f"  Elements loaded: {len(texts)} text, {len(svgs)} SVG")

    all_slides_html = []

    for text in texts:
        slides = markdown_to_slides(text)
        for slide in slides:
            html = slide_to_html(slide)
            all_slides_html.append(html)

    for name, svg in svgs.items():
        svg_slide = f'<section>\n<figure>\n{svg}\n<figcaption>{name}</figcaption>\n</figure>\n</section>'
        all_slides_html.append(svg_slide)

    if not all_slides_html:
        all_slides_html.append('<section>\n<h1>空演示</h1>\n<p>没有找到元素层内容</p>\n</section>')

    slides_html = "\n".join(all_slides_html)
    html = REVEAL_TEMPLATE.format(title=title, theme=theme, slides=slides_html)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    num_slides = len(all_slides_html)
    print(f"  Slides: {num_slides}")
    if num_slides < 10:
        print("  WARNING: Less than 10 slides. Consider adding more content.")
    if num_slides > 30:
        print("  WARNING: More than 30 slides. Consider splitting.")
    print(f"  Output: {output_path}")
    print("[Slides Pipeline] Done.")


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · 演示管线（Reveal.js）")
    parser.add_argument("--elements", required=True, help="元素层目录路径")
    parser.add_argument("--output", required=True, help="输出目录路径")
    parser.add_argument("--title", default="演示", help="演示标题")
    parser.add_argument("--theme", default="white", choices=VALID_THEMES, help="Reveal.js 主题")
    args = parser.parse_args()

    generate_slides(args.elements, args.output, args.title, args.theme)


if __name__ == "__main__":
    main()
