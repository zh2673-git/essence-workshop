"""
本质工坊 · HTML直接录制视频管线
从HTML文件直接录制视频，替代旧的slides.json+Canvas模板方式。

核心理念：HTML本身就是最好的视觉呈现，不需要再转换到Canvas卡片。
流程：HTML文件 → Playwright滚动录制 → Edge TTS旁白 → FFmpeg合并 → MP4

用法:
  python html_to_video.py input.html --output output/video/
  python html_to_video.py input.html --output output/video/ --narration "旁白文本"
  python html_to_video.py input.html --output output/video/ --narration-file narration.txt
  python html_to_video.py input.html --output output/video/ --bgm bgm.mp3
  python html_to_video.py input.html --output output/video/ --scroll-speed 80
  python html_to_video.py input.html --output output/video/ --sections 3
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def find_ffmpeg():
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            return "ffmpeg"
    except FileNotFoundError:
        pass
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        if os.path.exists(ffmpeg_path):
            return ffmpeg_path
    except ImportError:
        pass
    return None


FFMPEG = None


def check_dependencies():
    global FFMPEG
    missing = []
    try:
        import playwright
    except ImportError:
        missing.append("playwright (pip install playwright && playwright install chromium)")
    try:
        import edge_tts
    except ImportError:
        missing.append("edge-tts (pip install edge-tts)")
    FFMPEG = find_ffmpeg()
    if FFMPEG is None:
        missing.append("ffmpeg (install via conda: conda install -c conda-forge ffmpeg, or pip install imageio-ffmpeg)")
    if missing:
        print("Missing dependencies:")
        for m in missing:
            print(f"  - {m}")
        sys.exit(1)


def generate_tts(text, output_path, voice="zh-CN-YunxiNeural", rate="+0%"):
    """生成单段TTS音频"""
    import edge_tts

    async def _generate():
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(output_path)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0

    success = asyncio.run(_generate())
    if success:
        print(f"  [TTS] Generated: {output_path}")
        return output_path
    else:
        print(f"  [TTS] Failed to generate: {output_path}")
        return None


def generate_tts_sections(narration_sections, output_dir, voice="zh-CN-YunxiNeural", rate="+0%"):
    """按段落生成TTS音频，返回音频文件列表和对应时长"""
    import edge_tts

    os.makedirs(output_dir, exist_ok=True)
    audio_files = []
    durations = []

    async def _generate_one(text, output_path):
        for attempt in range(3):
            try:
                communicate = edge_tts.Communicate(text, voice, rate=rate)
                await communicate.save(output_path)
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    return True
            except Exception as e:
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                else:
                    print(f"    [ERROR] TTS failed after 3 attempts: {e}")
                    return False
        return False

    async def _generate_all():
        for i, text in enumerate(narration_sections):
            if not text or not text.strip():
                audio_files.append(None)
                durations.append(0)
                continue
            output_path = os.path.join(output_dir, f"section_{i:03d}.mp3")
            print(f"  [TTS] Section {i + 1}/{len(narration_sections)}: {text[:50]}...")
            success = await _generate_one(text, output_path)
            if success:
                audio_files.append(output_path)
            else:
                audio_files.append(None)
                durations.append(0)

    asyncio.run(_generate_all())

    # 获取每段音频时长
    for af in audio_files:
        if af and os.path.exists(af):
            dur = get_audio_duration(af)
            durations.append(dur)
        else:
            durations.append(5.0)  # 默认5秒

    return audio_files, durations


def get_audio_duration(audio_path):
    """获取音频时长"""
    ffprobe = FFMPEG.replace("ffmpeg", "ffprobe") if FFMPEG else None
    if ffprobe and os.path.exists(ffprobe):
        cmd = [ffprobe, "-v", "quiet", "-print_format", "json", "-show_format", audio_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)
        return float(info["format"]["duration"])
    # fallback
    cmd = [FFMPEG, "-i", audio_path, "-f", "null", "-"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    for line in result.stderr.split("\n"):
        if "Duration" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
    return 5.0


def get_video_duration(video_path):
    """获取视频时长"""
    ffprobe = FFMPEG.replace("ffmpeg", "ffprobe") if FFMPEG else None
    if ffprobe and os.path.exists(ffprobe):
        cmd = [ffprobe, "-v", "quiet", "-print_format", "json", "-show_format", video_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)
        return float(info["format"]["duration"])
    return None


def concat_audios(audio_files, output_path):
    """合并多个音频文件"""
    valid_files = [f for f in audio_files if f and os.path.exists(f)]
    if not valid_files:
        return None
    if len(valid_files) == 1:
        import shutil
        shutil.copy2(valid_files[0], output_path)
        return output_path

    tmp_dir = os.path.join(os.path.dirname(output_path), "_concat_tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    try:
        file_list_path = os.path.join(tmp_dir, "filelist.txt")
        with open(file_list_path, "w", encoding="utf-8") as f:
            for af in valid_files:
                af_abs = os.path.abspath(af).replace("\\", "/")
                f.write(f"file '{af_abs}'\n")
        cmd = [
            FFMPEG, "-y", "-f", "concat", "-safe", "0",
            "-i", file_list_path,
            "-c:a", "libmp3lame", "-b:a", "128k", "-ar", "24000", "-ac", "1",
            output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    finally:
        import shutil
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)


def record_html_video(html_path, output_path, width=1920, height=1080,
                      scroll_speed=60, pause_at_sections=True,
                      section_durations=None, device_scale_factor=2):
    """
    使用Playwright录制HTML页面的滚动视频。

    策略：
    1. 加载HTML页面
    2. 按段落/section自动滚动
    3. 每个section停留指定时间（由TTS时长决定）
    4. 平滑滚动到下一个section
    5. 录制整个过程
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=device_scale_factor,
            record_video_dir=os.path.dirname(os.path.abspath(output_path)),
            record_video_size={"width": width, "height": height},
        )
        page = context.new_page()

        html_url = f"file:///{os.path.abspath(html_path).replace(os.sep, '/')}"
        page.goto(html_url)
        page.wait_for_timeout(1000)

        # 注入滚动录制脚本
        # 检测页面中的section元素（维度卡片、组等）
        scroll_script = """
        () => {
            // 查找所有可滚动的section
            const sections = document.querySelectorAll(
                '.dimension-card, .group, .question-overview, .learning-path, .kp-card, .synthesis, .extensions, .knowledge-map, h2, h3'
            );
            const sectionPositions = [];
            sections.forEach(el => {
                const rect = el.getBoundingClientRect();
                const scrollTop = window.pageYOffset + rect.top - 100;
                sectionPositions.push({
                    top: scrollTop,
                    height: rect.height,
                    element: el.tagName + (el.className ? '.' + el.className.split(' ')[0] : '')
                });
            });
            // 去重和排序
            const unique = [];
            const seen = new Set();
            sectionPositions.forEach(s => {
                const key = Math.round(s.top / 50);
                if (!seen.has(key)) {
                    seen.add(key);
                    unique.push(s.top);
                }
            });
            unique.sort((a, b) => a - b);
            return unique;
        }
        """

        section_positions = page.evaluate(scroll_script)

        # 如果没有检测到section，按固定步长滚动
        if not section_positions or len(section_positions) < 2:
            page_height = page.evaluate("document.body.scrollHeight")
            viewport_height = page.evaluate("window.innerHeight")
            step = viewport_height * 0.7
            section_positions = list(range(0, page_height, int(step)))

        # 计算每个section的停留时间
        if section_durations and len(section_durations) >= len(section_positions):
            durations = section_durations[:len(section_positions)]
        else:
            # 默认每个section停留5秒
            durations = [5.0] * len(section_positions)

        print(f"  [SCROLL] Detected {len(section_positions)} sections")

        # 开始滚动录制
        for i, pos in enumerate(section_positions):
            # 滚动到section
            page.evaluate(f"window.scrollTo({{top: {pos}, behavior: 'smooth'}})")
            # 等待滚动完成
            page.wait_for_timeout(500)
            # 停留指定时间
            stay_time = int(durations[i] * 1000) if i < len(durations) else 3000
            page.wait_for_timeout(stay_time)

        # 最后回到顶部，停留2秒
        page.evaluate("window.scrollTo({top: 0, behavior: 'smooth'})")
        page.wait_for_timeout(2000)

        video_path = page.video.path()
        page.close()
        context.close()
        browser.close()

        if os.path.abspath(video_path) != os.path.abspath(output_path):
            import shutil
            shutil.move(video_path, output_path)

    print(f"  [VIDEO] Recorded: {output_path}")
    return output_path


def merge_video_audio(video_path, audio_path, output_path):
    """合并视频和音频"""
    # 先尝试copy模式（快速）
    cmd = [
        FFMPEG, "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        print(f"  [MERGE] Output: {output_path}")
        return output_path

    # copy模式失败，尝试重编码
    print(f"  [MERGE] Copy mode failed, trying re-encode...")
    cmd = [
        FFMPEG, "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  [MERGE] Output (re-encoded): {output_path}")
    return output_path


def merge_with_bgm_ducking(video_path, narration_path, bgm_path, output_path,
                           bgm_volume=0.3, duck_threshold=0.1, duck_ratio=4):
    """合并视频+旁白+BGM（带ducking）"""
    duration = get_video_duration(video_path)
    if duration is None:
        duration = get_audio_duration(video_path)

    cmd = [
        FFMPEG, "-y",
        "-i", video_path,
        "-i", bgm_path,
        "-i", narration_path,
        "-filter_complex",
        (
            f"[1:a]volume={bgm_volume},atrim=0:{duration:.2f},"
            f"afade=t=in:st=0:d=0.3,afade=t=out:st={max(0, duration - 1):.2f}:d=1[bgm];"
            f"[bgm][2:a]sidechaincompress=threshold={duck_threshold}:ratio={duck_ratio}:"
            f"attack=5:release=50[mixed]"
        ),
        "-map", "0:v",
        "-map", "[mixed]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  [BGM+DUCK] Output: {output_path}")
    return output_path


def export_gif(video_path, output_path, fps=10, width=540):
    """导出GIF"""
    cmd = [
        FFMPEG, "-y",
        "-i", video_path,
        "-vf", f"fps={fps},scale={width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  [GIF] Output: {output_path}")
    return output_path


def generate_video_from_html(html_path, output_dir="output/video/",
                             narration=None, narration_file=None,
                             narration_sections=None,
                             voice="zh-CN-YunxiNeural", rate="+0%",
                             width=1920, height=1080,
                             scroll_speed=60, bgm=None,
                             bgm_volume=0.3, fmt="mp4",
                             device_scale_factor=2):
    """
    从HTML文件生成视频的主函数。

    参数:
        html_path: HTML文件路径
        output_dir: 输出目录
        narration: 单段旁白文本
        narration_file: 旁白文本文件路径（每行一段）
        narration_sections: 多段旁白文本列表
        voice: TTS语音
        rate: TTS语速
        width: 视频宽度
        height: 视频高度
        scroll_speed: 滚动速度（像素/秒）
        bgm: 背景音乐路径
        bgm_volume: BGM音量
        fmt: 输出格式 (mp4/gif)
        device_scale_factor: 设备像素比
    """
    check_dependencies()

    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(html_path):
        print(f"[ERROR] HTML file not found: {html_path}")
        sys.exit(1)

    # Step 1: 准备旁白
    print("[1/4] Preparing narration...")
    audio_dir = os.path.join(output_dir, "_audio")
    os.makedirs(audio_dir, exist_ok=True)

    section_durations = None

    if narration_sections:
        # 多段旁白
        audio_files, durations = generate_tts_sections(narration_sections, audio_dir, voice, rate)
        concat_path = os.path.join(audio_dir, "narration_full.mp3")
        concat_audio_path = concat_audios(audio_files, concat_path)
        section_durations = durations
    elif narration_file and os.path.exists(narration_file):
        # 从文件读取旁白
        with open(narration_file, "r", encoding="utf-8") as f:
            sections = [line.strip() for line in f.readlines() if line.strip()]
        audio_files, durations = generate_tts_sections(sections, audio_dir, voice, rate)
        concat_path = os.path.join(audio_dir, "narration_full.mp3")
        concat_audio_path = concat_audios(audio_files, concat_path)
        section_durations = durations
    elif narration:
        # 单段旁白
        narration_path = os.path.join(audio_dir, "narration.mp3")
        result = generate_tts(narration, narration_path, voice, rate)
        concat_audio_path = result
        if result:
            dur = get_audio_duration(result)
            section_durations = [dur]
    else:
        concat_audio_path = None
        print("  [INFO] No narration provided, generating video without audio")

    # Step 2: 录制HTML视频
    print("[2/4] Recording HTML video...")
    raw_video_path = os.path.join(output_dir, "raw_video.mp4")
    record_html_video(
        html_path=html_path,
        output_path=raw_video_path,
        width=width,
        height=height,
        scroll_speed=scroll_speed,
        section_durations=section_durations,
        device_scale_factor=device_scale_factor,
    )

    # Step 3: 合并音频
    print("[3/4] Merging audio...")
    final_path = os.path.join(output_dir, "final.mp4")

    if bgm and os.path.exists(bgm) and concat_audio_path and os.path.exists(concat_audio_path):
        merge_with_bgm_ducking(raw_video_path, concat_audio_path, bgm, final_path, bgm_volume)
    elif concat_audio_path and os.path.exists(concat_audio_path):
        merge_video_audio(raw_video_path, concat_audio_path, final_path)
    else:
        # 无音频，直接重编码
        cmd = [
            FFMPEG, "-y",
            "-i", raw_video_path,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            final_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    # Step 4: 导出格式
    print("[4/4] Exporting...")
    if fmt == "gif":
        gif_path = os.path.join(output_dir, "final.gif")
        export_gif(final_path, gif_path)
        final_path = gif_path

    file_size_mb = os.path.getsize(final_path) / (1024 * 1024)
    print(f"\n[DONE] Video generated successfully!")
    print(f"  Source HTML: {html_path}")
    print(f"  Output: {final_path}")
    print(f"  Size: {file_size_mb:.1f} MB")
    print(f"  Format: {fmt}")
    if bgm:
        print(f"  BGM: {bgm}")

    return final_path


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · HTML直接录制视频管线")
    parser.add_argument("html", help="Path to HTML file")
    parser.add_argument("--output", "-o", default="output/video/", help="Output directory")
    parser.add_argument("--narration", "-n", default=None, help="Narration text (single segment)")
    parser.add_argument("--narration-file", "-f", default=None, help="Narration text file (one section per line)")
    parser.add_argument("--voice", "-v", default="zh-CN-YunxiNeural",
                        choices=["zh-CN-YunxiNeural", "zh-CN-XiaoxiaoNeural", "zh-CN-YunjianNeural"],
                        help="TTS voice")
    parser.add_argument("--rate", "-r", default="+0%", help="TTS speech rate")
    parser.add_argument("--width", default=1920, type=int, help="Video width（形式层默认16:9通用，实际由工作流层平台适配器指定）")
    parser.add_argument("--height", default=1080, type=int, help="Video height")
    parser.add_argument("--scroll-speed", default=60, type=int, help="Scroll speed (px/s)")
    parser.add_argument("--bgm", default=None, help="Background music file path")
    parser.add_argument("--bgm-volume", default=0.3, type=float, help="BGM volume (0-1)")
    parser.add_argument("--format", default="mp4", choices=["mp4", "gif"], help="Output format")
    parser.add_argument("--scale", default=2, type=int, help="Device scale factor for recording")

    args = parser.parse_args()
    generate_video_from_html(
        html_path=args.html,
        output_dir=args.output,
        narration=args.narration,
        narration_file=args.narration_file,
        voice=args.voice,
        rate=args.rate,
        width=args.width,
        height=args.height,
        scroll_speed=args.scroll_speed,
        bgm=args.bgm,
        bgm_volume=args.bgm_volume,
        fmt=args.format,
        device_scale_factor=args.scale,
    )


if __name__ == "__main__":
    main()
