"""
本质工坊 · 视频生成管线 v2
Stage+Sprite时间切片 + Playwright录制 + Edge TTS旁白 + FFmpeg合并
支持: BGM+Ducking混音, 多格式导出(MP4/GIF/60fps), 多风格模板

用法:
  python video_pipeline.py slides.json --output output/video/
  python video_pipeline.py slides.json --output output/video/ --style dark
  python video_pipeline.py slides.json --output output/video/ --bgm bgm.mp3
  python video_pipeline.py slides.json --output output/video/ --format gif
  python video_pipeline.py slides.json --output output/video/ --format mp4_60fps
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(SCRIPT_DIR, "video-template.html")

VALID_STYLES = ["dark", "warm", "minimal", "nature"]
VALID_FORMATS = ["mp4", "mp4_60fps", "gif"]


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


def generate_tts(narrations, output_dir, voice="zh-CN-YunxiNeural", rate="+0%"):
    import edge_tts

    os.makedirs(output_dir, exist_ok=True)
    audio_files = []

    async def _generate_one(text, output_path, max_retries=3):
        for attempt in range(max_retries):
            try:
                communicate = edge_tts.Communicate(text, voice, rate=rate)
                await communicate.save(output_path)
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    return True
            except Exception as e:
                if attempt < max_retries - 1:
                    wait = 2 ** attempt
                    print(f"    [RETRY] Attempt {attempt + 1} failed: {e}, retrying in {wait}s...")
                    await asyncio.sleep(wait)
                else:
                    print(f"    [ERROR] Failed after {max_retries} attempts: {e}")
                    return False
        return False

    async def _generate_all():
        for i, text in enumerate(narrations):
            if not text or not text.strip():
                continue
            output_path = os.path.join(output_dir, f"narration_{i:03d}.mp3")
            print(f"  [TTS] Generating narration {i + 1}/{len(narrations)}: {text[:40]}...")

            success = await _generate_one(text, output_path)
            if success:
                audio_files.append(output_path)
            else:
                print(f"    [SKIP] Narration {i + 1} failed, will use silent gap")

    asyncio.run(_generate_all())
    return audio_files


def concat_audios(audio_files, output_path):
    if not audio_files:
        return None

    if len(audio_files) == 1:
        import shutil
        shutil.copy2(audio_files[0], output_path)
        return output_path

    try:
        file_list_path = os.path.join(os.path.dirname(output_path), "filelist.txt")
        with open(file_list_path, "w", encoding="utf-8") as f:
            for af in audio_files:
                af_escaped = os.path.abspath(af).replace("\\", "/")
                f.write(f"file '{af_escaped}'\n")

        cmd = [
            FFMPEG, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", file_list_path,
            "-c:a", "aac",
            "-b:a", "128k",
            output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except subprocess.CalledProcessError:
        print("  [WARN] ffmpeg concat failed, falling back to binary concatenation...")
        with open(output_path, "wb") as out_f:
            for af in audio_files:
                with open(af, "rb") as in_f:
                    out_f.write(in_f.read())
        return output_path


def get_ffprobe():
    if FFMPEG is None:
        return None
    ffprobe_path = FFMPEG.replace("ffmpeg", "ffprobe")
    if os.path.exists(ffprobe_path):
        return ffprobe_path
    return None


def get_audio_duration(audio_path):
    ffprobe = get_ffprobe()
    if ffprobe is not None:
        cmd = [
            ffprobe,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            audio_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)
        return float(info["format"]["duration"])
    cmd = [
        FFMPEG, "-i", audio_path,
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    for line in result.stderr.split("\n"):
        if "Duration" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
    raise RuntimeError(f"Could not determine duration of {audio_path}")


def get_video_duration(video_path):
    ffprobe = get_ffprobe()
    if ffprobe is not None:
        cmd = [
            ffprobe,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            video_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)
        return float(info["format"]["duration"])
    return None


def adjust_slide_durations(slides, audio_path):
    try:
        audio_duration = get_audio_duration(audio_path)
    except Exception:
        print("  [WARN] Could not get audio duration, using original durations")
        return slides

    total_original = sum(s.get("duration", 10) for s in slides)
    if total_original <= 0:
        return slides

    scale = audio_duration / total_original

    for slide in slides:
        original = slide.get("duration", 10)
        slide["duration"] = max(3, round(original * scale, 1))

    new_total = sum(s.get("duration", 10) for s in slides)
    print(f"  [DURATION] Audio: {audio_duration:.1f}s, Slides adjusted: {new_total:.1f}s")
    return slides


def record_video(slides, template_html, output_path, width=1080, height=1920, style="dark"):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=2,
            record_video_dir=os.path.dirname(os.path.abspath(output_path)),
            record_video_size={"width": width, "height": height},
        )
        page = context.new_page()

        template_url = f"file:///{os.path.abspath(template_html).replace(os.sep, '/')}"
        page.goto(template_url)
        page.wait_for_timeout(500)

        page.evaluate(f"window.slidesData = {json.dumps({'slides': slides}, ensure_ascii=False)}")
        page.evaluate(f"window.themeName = '{style}'")
        page.evaluate("window.startPresentation()")

        total_duration = sum(s.get("duration", 10) for s in slides)
        page.wait_for_timeout((total_duration + 3) * 1000)

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
    cmd = [
        FFMPEG, "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-movflags", "+faststart",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  [MERGE] Output: {output_path}")
    return output_path


def merge_with_bgm_ducking(video_path, narration_path, bgm_path, output_path,
                           bgm_volume=0.3, duck_threshold=0.1, duck_ratio=4):
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
            f"[bgm][2:a]sidechaincompress=threshold={duck_threshold}:ratio={duck_ratio}:attack=5:release=50[mixed]"
        ),
        "-map", "0:v",
        "-map", "[mixed]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
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
    cmd = [
        FFMPEG, "-y",
        "-i", video_path,
        "-vf", f"fps={fps},scale={width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  [GIF] Output: {output_path}")
    return output_path


def export_60fps(video_path, audio_path, output_path):
    cmd = [
        FFMPEG, "-y",
        "-i", video_path,
        "-r", "60",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
    ]
    if audio_path and os.path.exists(audio_path):
        cmd.extend(["-i", audio_path, "-c:a", "aac", "-b:a", "128k", "-shortest"])
    else:
        cmd.extend(["-an"])
    cmd.append(output_path)
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  [60FPS] Output: {output_path}")
    return output_path


def compress_video(input_path, output_path, target_size_mb=50):
    duration = get_audio_duration(input_path)

    target_bitrate = int((target_size_mb * 8192) / duration * 0.9)

    cmd = [
        FFMPEG, "-y",
        "-i", input_path,
        "-c:v", "libx264",
        "-b:v", f"{target_bitrate}k",
        "-c:a", "aac",
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  [COMPRESS] Compressed to: {output_path}")
    return output_path


def generate_video(slides_path, output_dir, template_html=None, voice="zh-CN-YunxiNeural",
                   rate="+0%", width=1080, height=1920, compress=False,
                   style="dark", bgm=None, fmt="mp4"):
    check_dependencies()

    if style not in VALID_STYLES:
        print(f"  [WARN] Unknown style '{style}', using 'dark'")
        style = "dark"

    if fmt not in VALID_FORMATS:
        print(f"  [WARN] Unknown format '{fmt}', using 'mp4'")
        fmt = "mp4"

    if template_html is None:
        template_html = DEFAULT_TEMPLATE

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(output_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)

    with open(slides_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    slides = data["slides"]

    print(f"[1/5] Generating TTS narrations ({len(slides)} slides)...")
    narrations = [s.get("narration", "") for s in slides]
    audio_dir = os.path.join(output_dir, "audio")
    audio_files = generate_tts(narrations, audio_dir, voice=voice, rate=rate)

    print("[2/5] Concatenating audio...")
    concat_audio_path = os.path.join(output_dir, "narration.mp3")
    if audio_files:
        concat_audios(audio_files, concat_audio_path)
        print("[2.5/5] Adjusting slide durations to match audio...")
        slides = adjust_slide_durations(slides, concat_audio_path)
    else:
        concat_audio_path = None
        print("  [WARN] No narrations generated, producing silent video")

    print(f"[3/5] Recording Canvas animation (style={style})...")
    raw_video_path = os.path.join(output_dir, "raw.webm")
    record_video(slides, template_html, raw_video_path, width=width, height=height, style=style)

    print("[4/5] Merging video and audio...")
    final_path = os.path.join(output_dir, "final.mp4")

    if bgm and os.path.exists(bgm) and concat_audio_path and os.path.exists(concat_audio_path):
        print(f"  [BGM] Applying BGM with ducking: {bgm}")
        merge_with_bgm_ducking(raw_video_path, concat_audio_path, bgm, final_path)
    elif concat_audio_path and os.path.exists(concat_audio_path):
        merge_video_audio(raw_video_path, concat_audio_path, final_path)
    else:
        cmd = [
            FFMPEG, "-y",
            "-i", raw_video_path,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-an",
            final_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    if compress:
        compressed_path = os.path.join(output_dir, "final_compressed.mp4")
        compress_video(final_path, compressed_path)
        final_path = compressed_path

    print("[5/5] Exporting additional formats...")
    if fmt == "gif":
        gif_path = os.path.join(output_dir, "final.gif")
        export_gif(final_path, gif_path)
    elif fmt == "mp4_60fps":
        fps60_path = os.path.join(output_dir, "final_60fps.mp4")
        export_60fps(raw_video_path, concat_audio_path, fps60_path)
        final_path = fps60_path

    file_size_mb = os.path.getsize(final_path) / (1024 * 1024)
    print(f"\n[DONE] Video generated successfully!")
    print(f"  Output: {final_path}")
    print(f"  Size: {file_size_mb:.1f} MB")
    print(f"  Style: {style}")
    print(f"  Format: {fmt}")
    if bgm:
        print(f"  BGM: {bgm}")

    return final_path


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · 视频生成管线 v2")
    parser.add_argument("slides", help="Path to slides JSON file")
    parser.add_argument("--output", "-o", default="output/video/", help="Output directory")
    parser.add_argument("--template", "-t", default=None, help="HTML template path")
    parser.add_argument("--voice", "-v", default="zh-CN-YunxiNeural",
                        choices=["zh-CN-YunxiNeural", "zh-CN-XiaoxiaoNeural", "zh-CN-YunjianNeural"],
                        help="TTS voice")
    parser.add_argument("--rate", "-r", default="+0%", help="TTS speech rate (e.g. +10%%, -5%%)")
    parser.add_argument("--width", default=1080, type=int, help="Video width")
    parser.add_argument("--height", default=1920, type=int, help="Video height")
    parser.add_argument("--compress", action="store_true", help="Compress to 50MB limit")
    parser.add_argument("--style", default="dark", choices=VALID_STYLES,
                        help="Visual style: dark, warm, minimal, nature")
    parser.add_argument("--bgm", default=None,
                        help="Background music file path (MP3/WAV). Auto ducking when narration plays.")
    parser.add_argument("--format", default="mp4", choices=VALID_FORMATS,
                        help="Output format: mp4 (25fps), mp4_60fps, gif")

    args = parser.parse_args()
    generate_video(
        slides_path=args.slides,
        output_dir=args.output,
        template_html=args.template,
        voice=args.voice,
        rate=args.rate,
        width=args.width,
        height=args.height,
        compress=args.compress,
        style=args.style,
        bgm=args.bgm,
        fmt=args.format,
    )


if __name__ == "__main__":
    main()
