"""
本质工坊 · GIF 录制脚本（帧步进模式，防闪烁）
从包含 window.stepFrame(f) 和 window.getTotalFrames() 接口的 HTML 动画文件录制 GIF

防闪烁三原则：
1. HTML中禁用CSS transition/animation（截取中间帧会闪烁）
2. HTML中禁用渐变和半透明色（GIF 256色量化抖动）
3. 录制用统一全局调色板，optimize=False（避免帧间调色板突变）

用法:
  python record_gif.py animation.html
  python record_gif.py animation.html output.gif
  python record_gif.py animation.html output.gif --delay 200
  python record_gif.py animation.html output.gif --pause 8
"""

import argparse
import os
import sys
from io import BytesIO

from PIL import Image
from playwright.sync_api import sync_playwright


def record_gif(html_path, output_path, frame_delay_ms=200, pause_frames=8):
    html_abs = os.path.abspath(html_path)
    if not os.path.exists(html_abs):
        print(f"ERROR: HTML file not found: {html_abs}")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 800, "height": 500},
            device_scale_factor=1.5,  # 1.5x = 1200x750，清晰度与体积平衡
        )
        page.goto(f"file:///{html_abs}", timeout=60000)
        page.wait_for_timeout(500)

        try:
            total_frames = page.evaluate("window.getTotalFrames()")
        except Exception as e:
            print(f"ERROR: HTML does not expose window.getTotalFrames(): {e}")
            print("  Make sure the HTML uses frame-stepped mode (see image-generation.md)")
            browser.close()
            sys.exit(1)

        if total_frames <= 0:
            print("ERROR: getTotalFrames() returned 0 or negative")
            browser.close()
            sys.exit(1)

        print(f"Recording {total_frames} frames...")
        frames_rgb = []

        for i in range(total_frames):
            page.evaluate(f"window.stepFrame({i})")
            page.wait_for_timeout(100)  # 无transition，100ms足够渲染完成
            screenshot = page.screenshot(timeout=60000)
            img = Image.open(BytesIO(screenshot)).convert("RGB")
            frames_rgb.append(img)
            if (i + 1) % 10 == 0:
                print(f"  Frame {i + 1}/{total_frames}")

        # 末尾暂停帧
        for _ in range(pause_frames):
            frames_rgb.append(frames_rgb[-1].copy())

        browser.close()

    # 生成统一全局调色板（防闪烁关键）
    sample_imgs = [f.resize((200, 125), Image.LANCZOS) for f in frames_rgb[::2]]
    combined = Image.new("RGB", (200, 125 * len(sample_imgs)))
    for i, s in enumerate(sample_imgs):
        combined.paste(s, (0, i * 125))
    global_palette = combined.quantize(colors=256, method=Image.MEDIANCUT)

    # 用统一调色板转换所有帧
    frames_p = [f.quantize(palette=global_palette, dither=Image.FLOYDSTEINBERG) for f in frames_rgb]

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # 保存GIF：optimize=False避免帧间调色板突变，disposal=2清除上一帧确保动画可见
    frames_p[0].save(
        output_path,
        format="GIF",
        save_all=True,
        append_images=frames_p[1:],
        duration=frame_delay_ms,
        loop=0,
        optimize=False,  # 关键：不用optimize，避免帧间调色板变化闪烁
        disposal=2,  # 清除上一帧，确保每帧独立渲染
    )

    file_size_kb = os.path.getsize(output_path) / 1024
    print(f"GIF saved: {output_path} ({file_size_kb:.1f} KB, {len(frames_rgb)} frames)")

    if file_size_kb < 100:
        print(f"WARNING: GIF is only {file_size_kb:.1f} KB -- animation may not be working!")
    elif file_size_kb > 2000:
        print(f"WARNING: GIF is {file_size_kb:.1f} KB (>2MB) -- consider reducing frames or resolution")

    return file_size_kb


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · GIF 录制脚本（帧步进模式，防闪烁）")
    parser.add_argument("html", help="HTML 动画文件路径（必须暴露 stepFrame/getTotalFrames）")
    parser.add_argument("output", nargs="?", default="output.gif", help="输出 GIF 路径（默认: output.gif）")
    parser.add_argument("--delay", type=int, default=200, help="帧间隔毫秒（默认: 200）")
    parser.add_argument("--pause", type=int, default=8, help="末尾暂停帧数（默认: 8）")

    args = parser.parse_args()
    record_gif(args.html, args.output, frame_delay_ms=args.delay, pause_frames=args.pause)


if __name__ == "__main__":
    main()
