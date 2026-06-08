"""
本质工坊 · SVG→PNG 元素渲染器
使用 Playwright 将 SVG 文件渲染为高分辨率 PNG

支持:
  - 单文件转换: svg_to_png input.svg -o output.png
  - 批量转换: svg_to_png graphics/ -o output/graphics/ --dpi 2
  - 指定尺寸: svg_to_png input.svg -o output.png --width 1200

依赖: playwright (pip install playwright && playwright install chromium)

注意:
  - 必须使用本脚本进行 SVG→PNG 转换，不要使用 cairosvg
  - cairosvg 不支持系统字体，会导致中文字体回退为衬线体
  - 本脚本通过 Playwright 浏览器渲染，确保字体和样式正确
  - bg_color 默认自动从 SVG 中提取背景色（bg1），无需手动指定
  - 深色主题 SVG 会自动使用深色背景色，不会出现白色底色问题
"""

import argparse
import os
import re
import sys
import time


def check_playwright_available():
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False


def _extract_bg_color(svg_content):
    """从SVG内容中自动提取背景色（bg1），用于Playwright页面背景色。

    优先级:
      1. <solidColor id="bg-grad" color="..."/> （本质工坊SVG的标准背景定义）
      2. linearGradient 中第一个 stop 的 stop-color
      3. <rect> 全屏填充色（与 viewBox 同尺寸）
      4. 第一个 <rect> 的 fill（常见于手写封面SVG）
      5. 回退到 #ffffff
    """
    # 方式0: 提取 <solidColor id="bg-grad" color="..."/>
    # 本质工坊SVG使用 solidColor 定义背景，这是最准确的背景色来源
    solid_color = re.search(r'<solidColor[^>]+id="bg-grad"[^>]*color="([^"]+)"', svg_content)
    if not solid_color:
        solid_color = re.search(r'<solidColor[^>]*color="([^"]+)"[^>]*id="bg-grad"', svg_content)
    if solid_color:
        return solid_color.group(1)

    # 方式1: 提取 linearGradient 第一个 stop-color
    stops = re.findall(r'stop-color="([^"]+)"', svg_content)
    if stops:
        return stops[0]

    # 方式2: 提取全屏rect的fill
    # 2a: 匹配 width="100%" 的 rect
    rect_fill = re.search(r'<rect[^>]+width="100%[^>]*fill="([^"]+)"', svg_content)
    if not rect_fill:
        rect_fill = re.search(r'<rect[^>]+fill="([^"]+)"[^>]+width="100%', svg_content)
    if rect_fill:
        return rect_fill.group(1)

    # 2b: 匹配 viewBox 同尺寸的 rect（属性顺序不固定）
    vb_match2 = re.search(r'viewBox="[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)"', svg_content)
    if vb_match2:
        vb_w, vb_h = vb_match2.group(1), vb_match2.group(2)
        # 查找所有 rect，逐一检查是否有匹配 viewBox 的 width+height
        for rect_match in re.finditer(r'<rect\s+([^>]+)/?>', svg_content):
            attrs = rect_match.group(1)
            rw = re.search(r'width="([^"]+)"', attrs)
            rh = re.search(r'height="([^"]+)"', attrs)
            rf = re.search(r'fill="([^"]+)"', attrs)
            if rw and rh and rf and rw.group(1) == vb_w and rh.group(1) == vb_h:
                return rf.group(1)

    # 方式3: 提取第一个 <rect> 的 fill（手写封面SVG通常第一个rect就是背景）
    first_rect = re.search(r'<rect[^>]+fill="([^"]+)"', svg_content)
    if first_rect:
        return first_rect.group(1)

    # 方式4: 回退白底（深色SVG如果提取失败，白底比黑底更容易发现问题）
    return "#FFFFFF"


def svg_to_png(svg_path, output_path, width=None, height=None, dpi=2, bg_color=None, max_retries=3):
    from playwright.sync_api import sync_playwright

    with open(svg_path, "r", encoding="utf-8") as f:
        svg_content = f.read()

    # 自动提取背景色（如果未显式指定）
    if bg_color is None:
        bg_color = _extract_bg_color(svg_content)

    if not width or not height:
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

    # Force SVG element to fill container by overriding its width/height to 100%
    # 只替换 <svg ...> 标签自身的 width/height，避免误命中 <rect> 等子元素
    svg_content = re.sub(r'(<svg[^>]*?)\bwidth="[^"]*"', r'\1width="100%"', svg_content, count=1)
    svg_content = re.sub(r'(<svg[^>]*?)\bheight="[^"]*"', r'\1height="100%"', svg_content, count=1)
    # 如果 <svg> 没有 width/height 属性，补上
    if not re.search(r'<svg[^>]*\bwidth=', svg_content):
        svg_content = svg_content.replace('<svg', '<svg width="100%"', 1)
    if not re.search(r'<svg[^>]*\bheight=', svg_content):
        svg_content = svg_content.replace('<svg', '<svg height="100%"', 1)

    html = f"""<!DOCTYPE html>
<html><head><style>
* {{ margin:0; padding:0; box-sizing:border-box; font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans SC", sans-serif !important; }}
svg, svg text {{ font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans SC", sans-serif !important; }}
body {{ background:{bg_color}; margin:0; padding:0; }}
#svg-container {{ width:{width}px; height:{height}px; overflow:hidden; }}
#svg-container svg {{ display:block; }}
</style></head>
<body>
<div id="svg-container">
{svg_content}
</div>
</body></html>"""

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=dpi)
                page.set_content(html)
                container = page.query_selector("#svg-container")
                container.screenshot(path=output_path)
                browser.close()
            return  # 成功，直接返回
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                wait_s = attempt * 2
                print(f"  RETRY {attempt}/{max_retries}: SVG→PNG failed ({e}), retrying in {wait_s}s...")
                time.sleep(wait_s)

    # 所有重试都失败
    raise RuntimeError(f"SVG→PNG failed after {max_retries} retries: {last_error}")


def batch_convert(input_dir, output_dir, dpi=2, bg_color=None):
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
    parser.add_argument("--bg", default=None, help="背景色（默认自动从SVG提取）")
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
