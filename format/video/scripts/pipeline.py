"""
本质工坊 · 视频管线统一入口

新模型：
- --form 指定内容形式（当前仅支持 video）
- --pipeline 保留为方法别名（dsl / html_record）
"""
import argparse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def main(argv=None):
    parser = argparse.ArgumentParser(description='本质工坊 · 视频管线')
    parser.add_argument('input', nargs='?', help='输入文件（HTML 或 VideoProgram.tsx）')

    # 新模型参数
    parser.add_argument('--form', default='video', choices=['video'],
                        help='内容形式（当前仅支持 video）')

    # 向后兼容：旧 --pipeline 作为方法选择器
    parser.add_argument('--pipeline', choices=['dsl', 'html_record'],
                        help='[兼容] 选择实现方法，等价于显式指定 method')

    parser.add_argument('--output', default='output/video', help='输出目录')
    parser.add_argument('--source', default='user_input', help='内容来源')
    parser.add_argument('--visual-complexity', default='medium', help='视觉复杂度')
    parser.add_argument('--has-animation', action='store_true')
    parser.add_argument('--has-media-sync', action='store_true')
    parser.add_argument('--url', help='网页文章 URL')
    parser.add_argument('--bgm', help='背景音乐文件路径')
    parser.add_argument('--duration', type=int, default=60)
    parser.add_argument('--fps', type=int, default=30)
    parser.add_argument('--width', type=int, default=0, help='视频宽度')
    parser.add_argument('--height', type=int, default=0, help='视频高度')
    parser.add_argument('--format', choices=['mp4', 'gif'], default='mp4')
    parser.add_argument('--quality', choices=['draft', 'medium', 'high'], default='medium')

    args, rest = parser.parse_known_args(argv)

    if args.form != 'video':
        parser.error('当前视频管线只支持 --form video')

    # 统一走 dsl_video_pipeline.py，它负责根据 content_spec 路由 method
    from dsl_video_pipeline import main as dsl_main

    dsl_argv = [
        args.input or '',
        '--output', args.output,
        '--source', args.source,
        '--visual-complexity', args.visual_complexity,
        '--duration', str(args.duration),
        '--fps', str(args.fps),
        '--width', str(args.width),
        '--height', str(args.height),
        '--format', args.format,
        '--quality', args.quality,
    ]

    # 旧 --pipeline 映射为 content spec 线索
    if args.pipeline == 'dsl':
        dsl_argv.append('--has-animation')
    elif args.pipeline == 'html_record' and args.input:
        dsl_argv.extend(['--html', args.input])

    if args.has_animation:
        dsl_argv.append('--has-animation')
    if args.has_media_sync:
        dsl_argv.append('--has-media-sync')
    if args.bgm:
        dsl_argv.extend(['--bgm', args.bgm])
    if args.url:
        dsl_argv.extend(['--url', args.url])

    dsl_argv.extend(rest)
    dsl_main(dsl_argv)


if __name__ == '__main__':
    main()
