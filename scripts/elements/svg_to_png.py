"""
本质工坊 · SVG→PNG 元素渲染器
使用 Playwright 将 SVG 文件渲染为高分辨率 PNG

支持:
  - 单文件转换: svg_to_png input.svg -o output.png
  - 批量转换: svg_to_png graphics/ -o output/graphics/ --dpi 2
  - 指定尺寸: svg_to_png input.svg -o output.png --width 1200

依赖: playwright (pip install playwright && playwright install chromium)
"""

import argparse
import os
import sys


def check_playwright_available():
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False


def svg_to_png(svg_path, output_path, width=None, height=None, dpi=2, bg_color="#ffffff"):
    from playwright.sync_api import sync_playwright

    with open(svg_path, "r", encoding="utf-8") as f:
        svg_content = f.read()

    if not width or not height:
        import re
        vb_match = re.search(r'viewBox="([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)"', svg_content)
        w_match = re.search(r'width="([\d.]+)', svg_content)
        h_match = re.search(r'height="([\d.]+)', svg_content)

        if vb_match:
            svg_w, svg_h = float(vb_match.group(3)), float(vb_match.group(4))
        elif w_match and h_match:
            svg_w, svg_h = float(w_match.group(1)), float(h_match.group(1))
        else:
            svg_w, svg_h = 800, 600

        width = width or int(svg_w * dpi)
        height = height or int(svg_h * dpi)

    html = f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:{bg_color};">
<div id="svg-container" style="width:{width}px;height:{height}px;display:flex;align-items:center;justify-content:center;">
{svg_content}
</div>
</body></html>"""

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width + 40, "height": height + 40})
        page.set_content(html)
        container = page.query_selector("#svg-container")
        container.screenshot(path=output_path)
        browser.close()


def batch_convert(input_dir, output_dir, dpi=2, bg_color="#ffffff"):
    os.makedirs(output_dir, exist_ok=True)
    converted = 0
    for f in sorted(os.listdir(input_dir)):
        if not f.endswith(".svg"):
            continue
        svg_path = os.path.join(input_dir, f)
        png_name = os.path.splitext(f)[0] + ".png"
        png_path = os.path.join(output_dir, png_name)
        try:
            svg_to_png(svg_path, png_path, dpi=dpi, bg_color=bg_color)
            print(f"  ✓ {f} → {png_name}")
            converted += 1
        except Exception as e:
            print(f"  ✗ {f}: {e}")
    return converted


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · SVG→PNG 元素渲染器")
    parser.add_argument("input", help="SVG文件或包含SVG的目录")
    parser.add_argument("-o", "--output", required=True, help="输出PNG文件或目录")
    parser.add_argument("--dpi", type=float, default=2, help="渲染倍率（默认2x）")
    parser.add_argument("--width", type=int, default=None, help="输出宽度（像素）")
    parser.add_argument("--height", type=int, default=None, help="输出高度（像素）")
    parser.add_argument("--bg", default="#ffffff", help="背景色（默认#ffffff）")
    args = parser.parse_args()

    if not check_playwright_available():
        print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium")
        sys.exit(1)

    if os.path.isfile(args.input):
        svg_to_png(args.input, args.output, args.width, args.height, args.dpi, args.bg)
        print(f"Done: {args.input} → {args.output}")
    elif os.path.isdir(args.input):
        count = batch_convert(args.input, args.output, args.dpi, args.bg)
        print(f"Done: {count} SVG files converted")
    else:
        print(f"ERROR: Input not found: {args.input}")
        sys.exit(1)


if __name__ == "__main__":
    main()
