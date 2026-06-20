"""
本质工坊 · 统一CLI入口

新模型（推荐）：
  python -m scripts.cli output --form video --platform video-channel --input VideoProgram.tsx --output output/video/
  python -m scripts.cli output --form html --platform browser --elements output/elements/ --output output/html/
  python -m scripts.cli output --form html --platform wechat --elements output/elements/ --output output/wechat/
  python -m scripts.cli output --form slides --platform browser --elements output/elements/ --output output/slides/
  python -m scripts.cli output --form pptx --platform office --elements output/elements/ --output output/pptx/
  python -m scripts.cli output --form notebook --platform jupyter --elements output/elements/ --output output/notebook/

兼容命令：
  python -m scripts.cli publish article.md [--auto-cover] [--theme essence]
  python -m scripts.cli video slides.json [--output output/video/] [--style tech]
  python -m scripts.cli video VideoProgram.tsx --pipeline dsl --output output/video/
  python -m scripts.cli html --elements output/elements/ --output output/html/
  python -m scripts.cli slides --elements output/elements/ --output output/slides/
  python -m scripts.cli pptx --elements output/elements/ --output output/pptx/
  python -m scripts.cli notebook --elements output/elements/ --output output/notebook/
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
    """兼容入口：透传所有参数到 video/pipeline.py"""
    sys.path.insert(0, os.path.join(SCRIPT_DIR, "pipelines", "video"))
    from pipeline import main as video_main
    sys.argv = ["video"] + args.rest
    video_main()


def cmd_output(args):
    """新模型入口：先选 form，再选 platform。"""
    form = args.form
    platform = args.platform
    rest = args.rest

    if form == 'video':
        sys.path.insert(0, os.path.join(SCRIPT_DIR, "pipelines", "video"))
        from pipeline import main as video_main
        argv = []
        if args.input:
            argv.append(args.input)
        argv.extend([
            '--form', form,
            '--platform', platform,
            '--output', args.output,
        ])
        if args.elements:
            argv.extend(['--elements', args.elements])
        argv.extend(rest)
        sys.argv = ["video"] + argv
        video_main(argv)
    elif form in ('html', 'slides', 'pptx', 'notebook'):
        from .pipelines.dispatcher import main as dispatcher_main
        argv = [
            '--form', form,
            '--platform', platform,
            '--elements', args.elements,
            '--output', args.output,
        ]
        if args.title:
            argv.extend(['--title', args.title])
        argv.extend(rest)
        dispatcher_main(argv)
    else:
        print(f"[Error] 不支持的 form: {form}")
        sys.exit(1)


def cmd_html(args):
    from scripts.pipelines.html.generator import main as html_main
    sys.argv = ["html"] + args.rest
    html_main(args.rest)


def cmd_slides(args):
    from scripts.pipelines.slides.generator import main as slides_main
    sys.argv = ["slides"] + args.rest
    slides_main(args.rest)


def cmd_pptx(args):
    from scripts.pipelines.pptx.generator import main as pptx_main
    sys.argv = ["pptx"] + args.rest
    pptx_main(args.rest)


def cmd_notebook(args):
    from scripts.pipelines.notebook.generator import main as notebook_main
    sys.argv = ["notebook"] + args.rest
    notebook_main(args.rest)


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
    "video": ("视频管线：slides.json/VideoProgram.tsx → Canvas录制/DSL渲染 → MP4", cmd_video),
    "output": ("统一输出：--form <form> --platform <platform> → 平台成品", cmd_output),
    "html": ("HTML交互管线：元素层 → 完整交互HTML", cmd_html),
    "slides": ("演示管线：元素层 → Reveal.js HTML", cmd_slides),
    "pptx": ("PPT管线：元素层 → .pptx文件", cmd_pptx),
    "notebook": ("Notebook管线：元素层 → .ipynb文件", cmd_notebook),
    "gif": ("GIF录制：SVG动画 → GIF", cmd_gif),
    "brand": ("品牌提取：文章 → brand-spec.json", cmd_brand),
    "fetch": ("文章拉取：公众号URL → Markdown", cmd_fetch),
}


# 各 form 支持的默认 platform
DEFAULT_PLATFORM = {
    "video": "video-channel",
    "html": "browser",
    "slides": "browser",
    "pptx": "office",
    "notebook": "jupyter",
}

# 各 form 支持的平台
FORM_PLATFORMS = {
    "video": ["video-channel", "bilibili", "douyin"],
    "html": ["browser", "wechat"],
    "slides": ["browser", "reveal"],
    "pptx": ["office"],
    "notebook": ["jupyter"],
}


def main():
    parser = argparse.ArgumentParser(
        prog="essence-workshop",
        description="本质工坊 · 统一CLI入口",
    )
    subparsers = parser.add_subparsers(dest="command", help="可用管线命令")

    for name, (desc, _) in PIPELINE_COMMANDS.items():
        sub = subparsers.add_parser(name, help=desc)
        if name == "output":
            sub.add_argument("--form", required=True,
                             choices=["video", "html", "slides", "pptx", "notebook"],
                             help="内容形式")
            sub.add_argument("--platform", default=None,
                             choices=["video-channel", "bilibili", "douyin", "browser", "wechat", "reveal", "office", "jupyter"],
                             help="目标平台（默认由 form 决定）")
            sub.add_argument("--input", help="输入文件（video 形式）")
            sub.add_argument("--elements", help="元素层目录（非 video 形式）")
            sub.add_argument("--output", default="output", help="输出目录")
            sub.add_argument("--title", default="", help="标题")

    args, rest = parser.parse_known_args()

    if not args.command:
        parser.print_help()
        print("\n管线命令:")
        for name, (desc, _) in PIPELINE_COMMANDS.items():
            print(f"  {name:12s} {desc}")
        sys.exit(0)

    # output 命令默认 platform
    if args.command == "output" and args.platform is None:
        args.platform = DEFAULT_PLATFORM[args.form]

    args.rest = rest
    _, handler = PIPELINE_COMMANDS[args.command]
    handler(args)


if __name__ == "__main__":
    main()
