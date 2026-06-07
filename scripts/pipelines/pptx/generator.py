"""
本质工坊 · PPT管线
从元素层读取 → 降级转换 → python-pptx / html2pptx.js → .pptx文件

模式:
  simple   - python-pptx 直接生成（默认，v1行为）
  precise  - HTML → Playwright读取DOM → pptxgenjs精确还原（v2，huashu-design风格）

用法:
  python -m scripts.pipelines.pptx.generator --elements output/elements/ --output output/pptx/
  python -m scripts.pipelines.pptx.generator --elements output/elements/ --output output/pptx/ --mode precise
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
    "primary": "#FFD700",
    "accent": "#FFD700",
    "fg": "#FFFFFF",
    "bg": "#0A0A0A",
    "muted": "#B0B0B0",
    "border": "#333333",
    "font_title": "Microsoft YaHei",
    "font_body": "Microsoft YaHei",
}


def check_pptx_available():
    try:
        from pptx import Presentation
        return True
    except ImportError:
        return False


def generate_pptx_simple(elements_dir, output_dir, template_path=None, brand_spec_path=None, title="演示"):
    print("[PPTX Pipeline · simple] Starting...")

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
        if "derived" in spec:
            for k, v in spec["derived"].items():
                brand[k] = v
        if "fonts" in spec:
            if "display" in spec["fonts"]:
                brand["font_title"] = spec["fonts"]["display"].replace("'", "").split(",")[0].strip()
            if "body" in spec["fonts"]:
                brand["font_body"] = spec["fonts"]["body"].replace("'", "").split(",")[0].strip()
        print(f"  Brand spec loaded: {brand_spec_path}")

    if template_path and os.path.isfile(template_path):
        prs = Presentation(template_path)
        print(f"  Template loaded: {template_path}")
    else:
        prs = Presentation()
        prs.slide_width = Inches(SLIDE_WIDTH_INCHES)
        prs.slide_height = Inches(SLIDE_HEIGHT_INCHES)

    slide_layout = prs.slide_layouts[0]

    primary_rgb = RGBColor.from_string(brand["primary"].lstrip('#'))
    accent_rgb = RGBColor.from_string(brand.get("accent", "#E94560").lstrip('#'))
    fg_rgb = RGBColor.from_string(brand.get("fg", "#1A1A1A").lstrip('#'))

    title_slide = prs.slides.add_slide(slide_layout)
    title_slide.shapes.title.text = title
    for run in title_slide.shapes.title.text_frame.paragraphs[0].runs:
        run.font.color.rgb = primary_rgb
        run.font.size = Pt(36)
        run.font.bold = True
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
                for run in slide.shapes.title.text_frame.paragraphs[0].runs:
                    run.font.color.rgb = primary_rgb
                    run.font.size = Pt(28)
                    run.font.bold = True

                if body and len(slide.placeholders) > 1:
                    text_frame = slide.placeholders[1].text_frame
                    text_frame.text = body[:2000]
                    for para in text_frame.paragraphs:
                        for run in para.runs:
                            run.font.color.rgb = fg_rgb
                            run.font.size = Pt(16)

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
    print("[PPTX Pipeline · simple] Done.")


def generate_pptx_precise(elements_dir, output_dir, brand_spec_path=None, title="演示", layout="LAYOUT_16x9"):
    print("[PPTX Pipeline · precise] Starting...")

    from scripts.pipelines.pptx.bridge import html_to_pptx
    from scripts.pipelines.html.generator import generate_html

    html_output_dir = os.path.join(output_dir, "_html_temp")
    generate_html(
        elements_dir=elements_dir,
        output_dir=html_output_dir,
        brand_spec_path=brand_spec_path,
        title=title,
        mode="paged",
    )

    html_path = os.path.join(html_output_dir, "index.html")
    if not os.path.isfile(html_path):
        print("ERROR: HTML generation failed, cannot proceed with precise mode")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "output.pptx")

    success = html_to_pptx(html_path, output_path, layout=layout)
    if success:
        print(f"  Output: {output_path}")
        print("[PPTX Pipeline · precise] Done.")
    else:
        print("ERROR: html2pptx.js conversion failed")
        print("  Falling back to simple mode...")
        generate_pptx_simple(elements_dir, output_dir, brand_spec_path=brand_spec_path, title=title)


def generate_pptx(elements_dir, output_dir, template_path=None, brand_spec_path=None, title="演示", mode="simple", layout="LAYOUT_16x9"):
    if mode == "precise":
        generate_pptx_precise(elements_dir, output_dir, brand_spec_path, title, layout)
    else:
        generate_pptx_simple(elements_dir, output_dir, template_path, brand_spec_path, title)


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · PPT管线")
    parser.add_argument("--elements", required=True, help="元素层目录路径")
    parser.add_argument("--output", required=True, help="输出目录路径")
    parser.add_argument("--template", default=None, help="企业模板 .potx 文件路径")
    parser.add_argument("--brand-spec", default=None, help="品牌规格文件路径")
    parser.add_argument("--title", default="演示", help="演示标题")
    parser.add_argument("--mode", default="simple", choices=["simple", "precise"], help="生成模式：simple=python-pptx, precise=html2pptx.js")
    parser.add_argument("--layout", default="LAYOUT_16x9", choices=["LAYOUT_16x9", "LAYOUT_4x3"], help="幻灯片布局（precise模式）")
    args = parser.parse_args()

    generate_pptx(args.elements, args.output, args.template, args.brand_spec, args.title, args.mode, args.layout)


if __name__ == "__main__":
    main()
