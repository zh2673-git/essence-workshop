"""
本质工坊 · PPT管线
从元素层读取 → 降级转换 → python-pptx → .pptx文件

设计思路（参考 huashu-design html2pptx.js）：
  方案一（当前实现）：python-pptx 直接生成
  方案二（未来升级）：HTML → Playwright截图 → python-pptx 组装
    huashu-design 的 html2pptx.js 方案更优，保留文本可编辑性
    但需要 Node.js 环境，当前先用 python-pptx 实现

降级规则：
  SVG → PNG（Playwright渲染）→ PPT图片
  SVG动画 → 关键帧截图 → PPT图片
  交互元素 → 静态截图 → PPT图片

用法:
  python -m scripts.pipelines.pptx.generator --elements output/elements/ --output output/pptx/
  python -m scripts.pipelines.pptx.generator --elements output/elements/ --output output/pptx/ --template corporate.potx
  python -m scripts.pipelines.pptx.generator --elements output/elements/ --output output/pptx/ --brand-spec brand-spec.json
"""

import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SLIDE_WIDTH_INCHES = 13.333
SLIDE_HEIGHT_INCHES = 7.5

DEFAULT_BRAND = {
    "primary": "#2563eb",
    "secondary": "#7c3aed",
    "text": "#1f2937",
    "bg": "#ffffff",
    "font_title": "Microsoft YaHei",
    "font_body": "Microsoft YaHei",
}


def check_pptx_available():
    try:
        from pptx import Presentation
        return True
    except ImportError:
        return False


def generate_pptx(elements_dir, output_dir, template_path=None, brand_spec_path=None, title="演示"):
    print("[PPTX Pipeline] Starting...")

    if not check_pptx_available():
        print("ERROR: python-pptx not installed. Run: pip install python-pptx")
        sys.exit(1)

    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN

    brand = dict(DEFAULT_BRAND)
    if brand_spec_path and os.path.isfile(brand_spec_path):
        with open(brand_spec_path, "r", encoding="utf-8") as f:
            spec = json.load(f)
        if "colors" in spec:
            for k, v in spec["colors"].items():
                brand[k] = v
        print(f"  Brand spec loaded: {brand_spec_path}")

    if template_path and os.path.isfile(template_path):
        prs = Presentation(template_path)
        print(f"  Template loaded: {template_path}")
    else:
        prs = Presentation()
        prs.slide_width = Inches(SLIDE_WIDTH_INCHES)
        prs.slide_height = Inches(SLIDE_HEIGHT_INCHES)

    slide_layout = prs.slide_layouts[0]

    title_slide = prs.slides.add_slide(slide_layout)
    title_slide.shapes.title.text = title
    if hasattr(title_slide, 'placeholders') and len(title_slide.placeholders) > 1:
        title_slide.placeholders[1].text = "本质工坊 自动生成"

    text_dir = os.path.join(elements_dir, "text")
    if os.path.isdir(text_dir):
        import re
        for f in sorted(os.listdir(text_dir)):
            if not f.endswith(".md"):
                continue
            with open(os.path.join(text_dir, f), "r", encoding="utf-8") as fh:
                content = fh.read()

            sections = re.split(r'\n(?=#{1,3}\s)', content)
            for section in sections:
                if not section.strip():
                    continue
                lines = section.strip().split("\n")
                heading = lines[0].lstrip("#").strip()
                body = "\n".join(lines[1:]).strip()

                slide = prs.slides.add_slide(prs.slide_layouts[1])
                slide.shapes.title.text = heading

                if body and len(slide.placeholders) > 1:
                    text_frame = slide.placeholders[1].text_frame
                    text_frame.text = body[:2000]

    graphics_dir = os.path.join(elements_dir, "graphics")
    png_files = []
    if os.path.isdir(graphics_dir):
        for f in sorted(os.listdir(graphics_dir)):
            if f.endswith(".png"):
                png_files.append(os.path.join(graphics_dir, f))

    for png_path in png_files:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.shapes.add_picture(
            png_path,
            Inches(1), Inches(0.5),
            Inches(SLIDE_WIDTH_INCHES - 2), Inches(SLIDE_HEIGHT_INCHES - 1),
        )

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "output.pptx")
    prs.save(output_path)

    num_slides = len(prs.slides)
    print(f"  Slides: {num_slides}")
    print(f"  Output: {output_path}")
    print("[PPTX Pipeline] Done.")


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · PPT管线")
    parser.add_argument("--elements", required=True, help="元素层目录路径")
    parser.add_argument("--output", required=True, help="输出目录路径")
    parser.add_argument("--template", default=None, help="企业模板 .potx 文件路径")
    parser.add_argument("--brand-spec", default=None, help="品牌规格文件路径")
    parser.add_argument("--title", default="演示", help="演示标题")
    args = parser.parse_args()

    generate_pptx(args.elements, args.output, args.template, args.brand_spec, args.title)


if __name__ == "__main__":
    main()
