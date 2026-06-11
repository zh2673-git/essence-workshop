"""
本质工坊 · 统一CLI入口

用法:
  python -m scripts.cli publish article.md [--auto-cover] [--theme essence]
  python -m scripts.cli video slides.json [--output output/video/] [--style tech]
  python -m scripts.cli html --elements output/elements/ --output output/html/
  python -m scripts.cli slides --elements output/elements/ --output output/slides/
  python -m scripts.cli pptx --elements output/elements/ --output output/pptx/
  python -m scripts.cli gif animation.html [output.gif]
  python -m scripts.cli brand --article output/article.md
  python -m scripts.cli fetch --url https://mp.weixin.qq.com/s/xxx
"""

import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..")


def cmd_publish(args):
    sys.path.insert(0, os.path.join(SCRIPT_DIR, "pipelines", "wechat"))
    from publish import main as wechat_main
    sys.argv = ["publish"] + args.rest
    wechat_main()


def cmd_video(args):
    sys.path.insert(0, os.path.join(SCRIPT_DIR, "pipelines", "video"))
    from pipeline import main as video_main
    sys.argv = ["video"] + args.rest
    video_main()


def cmd_html(args):
    from scripts.pipelines.html.generator import main as html_main
    sys.argv = ["html"] + args.rest
    html_main()


def cmd_slides(args):
    from scripts.pipelines.slides.generator import main as slides_main
    sys.argv = ["slides"] + args.rest
    slides_main()


def cmd_pptx(args):
    from scripts.pipelines.pptx.generator import main as pptx_main
    sys.argv = ["pptx"] + args.rest
    pptx_main()


def cmd_gif(args):
    sys.path.insert(0, os.path.join(SCRIPT_DIR, "elements"))
    from record_gif import main as gif_main
    sys.argv = ["gif"] + args.rest
    gif_main()


def cmd_brand(args):
    sys.path.insert(0, os.path.join(SCRIPT_DIR, "elements"))
    from brand_extractor import main as brand_main
    sys.argv = ["brand"] + args.rest
    brand_main()


def cmd_fetch(args):
    sys.path.insert(0, os.path.join(SCRIPT_DIR, "shared"))
    from article_fetcher import main as fetch_main
    sys.argv = ["fetch"] + args.rest
    fetch_main()


PIPELINE_COMMANDS = {
    "publish": ("公众号管线：Markdown → 微信HTML → 推送草稿箱", cmd_publish),
    "video": ("视频号管线：slides.json → Canvas录制 → MP4", cmd_video),
    "html": ("HTML交互管线：元素层 → 完整交互HTML", cmd_html),
    "slides": ("演示管线：元素层 → Reveal.js HTML", cmd_slides),
    "pptx": ("PPT管线：元素层 → .pptx文件", cmd_pptx),
    "gif": ("GIF录制：SVG动画 → GIF", cmd_gif),
    "brand": ("品牌提取：文章 → brand-spec.json", cmd_brand),
    "fetch": ("文章拉取：公众号URL → Markdown", cmd_fetch),
}


def main():
    parser = argparse.ArgumentParser(
        prog="essence-workshop",
        description="本质工坊 · 统一CLI入口",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用管线命令")

    for name, (desc, _) in PIPELINE_COMMANDS.items():
        subparsers.add_parser(name, help=desc)

    args, rest = parser.parse_known_args()

    if not args.command:
        parser.print_help()
        print("\n管线命令:")
        for name, (desc, _) in PIPELINE_COMMANDS.items():
            print(f"  {name:12s} {desc}")
        sys.exit(0)

    args.rest = rest
    _, handler = PIPELINE_COMMANDS[args.command]
    handler(args)


if __name__ == "__main__":
    main()
