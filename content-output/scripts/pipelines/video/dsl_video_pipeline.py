"""
本质工坊 · DSL 视频管线入口

新模型：
- form = 'video'
- method = 'dsl'
- platform = video-channel / bilibili / douyin（由 --platform 指定）

平台约束通过 platform adapters 应用。
"""
import argparse
import json
import os
import subprocess
import sys
from typing import Any

from router import select_method, explain_decision
from scripts.pipelines.platforms import get_adapter, list_platforms


def find_ffmpeg():
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return 'ffmpeg'
    except Exception:
        pass
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    return None


def content_spec_from_args(args) -> dict:
    spec: dict[str, Any] = {
        'source': args.source or 'user_input',
        'visualComplexity': args.visual_complexity or 'medium',
        'hasAnimationRequirements': args.has_animation,
        'hasMediaSync': args.has_media_sync,
        'durationSeconds': args.duration or 60,
        'platform': args.platform,
    }
    if args.html:
        spec['hasStructuredHTML'] = True
        spec['htmlPath'] = args.html
    if args.url:
        spec['source'] = 'wechat_article'
        spec['articleUrl'] = args.url
    return spec


def apply_platform_constraints(platform: str, options: dict) -> dict:
    adapter = get_adapter(platform)
    errors = adapter.validate(options)
    if errors:
        raise ValueError(f"平台 {platform} 校验失败：" + '; '.join(errors))
    return adapter.apply(options)


def run_dsl_pipeline(entry_file: str, output_dir: str, fps: int = 30, width: int = 1080, height: int = 1920,
                     audio_path: str = '', bgm_path: str = '', output_format: str = 'mp4', quality: str = 'medium'):
    """调用 Node.js CLI 渲染 DSL 视频。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    video_dsl = os.path.abspath(os.path.join(script_dir, '..', '..', '..', 'video-dsl'))
    cli = os.path.join(video_dsl, 'packages', 'video-renderer', 'dist', 'cli.js')
    if not os.path.exists(cli):
        raise RuntimeError(f'DSL renderer CLI not found: {cli}')

    cmd = [
        'node', cli, entry_file,
        '--output', output_dir,
        '--fps', str(fps),
        '--width', str(width),
        '--height', str(height),
        '--format', output_format,
        '--quality', quality,
    ]
    if audio_path:
        cmd.extend(['--audio', audio_path])
    if bgm_path:
        cmd.extend(['--bgm', bgm_path])
    print(f"  [DSL] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    ext = 'gif' if output_format == 'gif' else 'mp4'
    return os.path.join(output_dir, f'final.{ext}')


def run_html_record_pipeline(html_path: str, output_dir: str):
    from html_to_video import main as html_main
    html_main([html_path, '--output', output_dir])
    return os.path.join(output_dir, 'final.mp4')


def run_article_to_video_pipeline(url: str, output_dir: str):
    shared_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
    sys.path.insert(0, shared_dir)
    from article_to_video import main as article_main
    article_main(['--url', url, '--output', output_dir])
    return os.path.join(output_dir, 'final.mp4')


def generate_video(content_spec: dict, output_dir: str, entry_file: str = '',
                   bgm_path: str = '', output_format: str = 'mp4', quality: str = 'medium',
                   width: int = 0, height: int = 0, fps: int = 30) -> dict:
    decision = select_method(content_spec)
    print(f"  [Router] {explain_decision(decision)}")

    log_path = os.path.join(output_dir, 'router-decision.json')
    os.makedirs(output_dir, exist_ok=True)
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(decision, f, ensure_ascii=False, indent=2)

    method = decision['method']
    platform = decision['platform']

    # 应用平台约束
    options = {
        'duration': content_spec.get('durationSeconds', 60),
        'fps': fps,
        'width': width,
        'height': height,
        'format': output_format,
        'quality': quality,
    }
    options = apply_platform_constraints(platform, options)

    if method == 'dsl':
        if not entry_file or not os.path.exists(entry_file):
            raise ValueError('DSL 管线需要提供有效的 VideoProgram.tsx 入口文件')
        # Auto-generate TTS audio if spec.json exists next to entry file.
        audio_path = ''
        spec_path = os.path.join(os.path.dirname(entry_file), 'spec.json')
        if os.path.exists(spec_path):
            audio_dir = os.path.join(output_dir, '_audio')
            video_dsl = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'video-dsl'))
            audio_script = os.path.join(video_dsl, 'scripts', 'generate_audio.py')
            print(f'  [Audio] Generating from {spec_path}')
            subprocess.run(['python', audio_script, spec_path, '--output', audio_dir], check=True)
            audio_path = os.path.join(audio_dir, 'audio.m4a')
        video_path = run_dsl_pipeline(
            entry_file, output_dir,
            fps=options['fps'], width=options['width'], height=options['height'],
            audio_path=audio_path, bgm_path=bgm_path,
            output_format=options['format'], quality=options['quality']
        )
    elif method == 'html_record':
        html_path = content_spec.get('htmlPath')
        if not html_path or not os.path.exists(html_path):
            raise ValueError('HTML 录制管线需要提供有效的 HTML 文件路径')
        video_path = run_html_record_pipeline(html_path, output_dir)
    elif method == 'article_to_video':
        url = content_spec.get('articleUrl')
        if not url:
            raise ValueError('公众号文章转视频管线需要提供文章 URL')
        video_path = run_article_to_video_pipeline(url, output_dir)
    else:
        raise ValueError(f"Unknown method: {method}")

    return {'method': method, 'platform': platform, 'video': video_path, 'decision': decision}


def main(argv=None):
    parser = argparse.ArgumentParser(description='本质工坊 · DSL 视频管线')
    parser.add_argument('entry', nargs='?', help='VideoProgram.tsx 入口文件')
    parser.add_argument('--output', default='output/video-dsl', help='输出目录')
    parser.add_argument('--source', default='user_input', help='内容来源')
    parser.add_argument('--visual-complexity', default='medium', help='视觉复杂度 low/medium/high')
    parser.add_argument('--has-animation', action='store_true', help='是否有动画需求')
    parser.add_argument('--has-media-sync', action='store_true', help='是否需要音画同步')
    parser.add_argument('--html', help='HTML 文件路径（HTML 录制分支）')
    parser.add_argument('--url', help='公众号文章 URL（article_to_video 分支）')
    parser.add_argument('--bgm', help='背景音乐文件路径')
    parser.add_argument('--duration', type=int, default=60, help='视频时长（秒）')
    parser.add_argument('--fps', type=int, default=30)
    parser.add_argument('--width', type=int, default=0, help='覆盖平台默认宽度')
    parser.add_argument('--height', type=int, default=0, help='覆盖平台默认高度')
    parser.add_argument('--format', choices=['mp4', 'gif'], default='mp4', help='输出格式')
    parser.add_argument('--quality', choices=['draft', 'medium', 'high'], default='medium', help='渲染质量')
    parser.add_argument('--platform', choices=list_platforms(), default='video-channel',
                        help='目标平台，决定默认分辨率与格式约束')

    args = parser.parse_args(argv)
    if not args.entry and not args.html and not args.url:
        parser.error('请提供 --entry 或 --html 或 --url')

    content_spec = content_spec_from_args(args)
    result = generate_video(
        content_spec, args.output, entry_file=args.entry or '',
        bgm_path=args.bgm or '', output_format=args.format, quality=args.quality,
        width=args.width, height=args.height, fps=args.fps
    )
    print(f"  [Done] {result['platform']}: {result['video']}")


if __name__ == '__main__':
    main()
