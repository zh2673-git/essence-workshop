"""
本质工坊 · GIF 录制脚本（帧步进模式）
从包含 window.stepFrame(f) 和 window.getTotalFrames() 接口的 HTML 动画文件录制 GIF

用法:
  python record_gif.py animation.html
  python record_gif.py animation.html output.gif
  python record_gif.py animation.html output.gif --delay 100
  python record_gif.py animation.html output.gif --pause 20
"""

import argparse
import os
import sys
from io import BytesIO

from PIL import Image
from playwright.sync_api import sync_playwright


def record_gif(html_path, output_path, frame_delay_ms=120, pause_frames=15):
    html_abs = os.path.abspath(html_path)
    if not os.path.exists(html_abs):
        print(f"ERROR: HTML file not found: {html_abs}")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 800, "height": 500},
            device_scale_factor=2,
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
        frames = []

        for i in range(total_frames):
            page.evaluate(f"window.stepFrame({i})")
            page.wait_for_timeout(50)
            screenshot = page.screenshot(timeout=60000)
            img = Image.open(BytesIO(screenshot))
            frames.append(img.convert("RGB"))
            if (i + 1) % 10 == 0:
                print(f"  Frame {i + 1}/{total_frames}")

        for _ in range(pause_frames):
            frames.append(frames[-1].copy())

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=frame_delay_ms,
            loop=0,
            optimize=True,
        )

        browser.close()

    file_size_kb = os.path.getsize(output_path) / 1024
    print(f"GIF saved: {output_path} ({file_size_kb:.1f} KB, {len(frames)} frames)")

    if file_size_kb < 100:
        print(f"WARNING: GIF is only {file_size_kb:.1f} KB -- animation may not be working!")
    elif file_size_kb > 3000:
        print(f"WARNING: GIF is {file_size_kb:.1f} KB (>3MB) -- consider reducing frames or resolution")


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · GIF 录制脚本（帧步进模式）")
    parser.add_argument("html", help="HTML 动画文件路径（必须暴露 stepFrame/getTotalFrames）")
    parser.add_argument("output", nargs="?", default="output.gif", help="输出 GIF 路径（默认: output.gif）")
    parser.add_argument("--delay", type=int, default=120, help="帧间隔毫秒（默认: 120）")
    parser.add_argument("--pause", type=int, default=15, help="末尾暂停帧数（默认: 15）")

    args = parser.parse_args()
    record_gif(args.html, args.output, frame_delay_ms=args.delay, pause_frames=args.pause)


if __name__ == "__main__":
    main()
