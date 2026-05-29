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
VALID_VISUAL_STYLES = ["tech", "edu", "compare", "philosophy"]


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

    async def _generate_one(text, output_path, tts_rate="+0%", max_retries=3):
        for attempt in range(max_retries):
            try:
                communicate = edge_tts.Communicate(text, voice, rate=tts_rate)
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

            success = await _generate_one(text, output_path, tts_rate=rate)
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

    tmp_dir = os.path.join(os.path.dirname(output_path), "_concat_tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    try:
        file_list_path = os.path.join(tmp_dir, "filelist.txt")
        with open(file_list_path, "w", encoding="utf-8") as f:
            for af in audio_files:
                af_abs = os.path.abspath(af).replace("\\", "/")
                f.write(f"file '{af_abs}'\n")
        cmd = [
            FFMPEG, "-y",
            "-f", "concat", "-safe", "0",
            "-i", file_list_path,
            "-c:a", "libmp3lame", "-b:a", "128k",
            "-ar", "24000", "-ac", "1",
            output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except Exception as e:
        print(f"  [WARN] FFmpeg concat failed: {e}, trying WAV concat...")
        try:
            import wave
            wav_files = []
            for i, af in enumerate(audio_files):
                wav_path = os.path.join(tmp_dir, f"_{i:03d}.wav")
                cmd = [FFMPEG, "-y", "-i", af, "-ar", "24000", "-ac", "1", "-acodec", "pcm_s16le", wav_path]
                subprocess.run(cmd, check=True, capture_output=True)
                wav_files.append(wav_path)

            merged_wav = os.path.join(tmp_dir, "merged.wav")
            with wave.open(wav_files[0], 'rb') as first:
                params = first.getparams()
                all_frames = [first.readframes(first.getnframes())]

            for wf in wav_files[1:]:
                with wave.open(wf, 'rb') as f:
                    all_frames.append(f.readframes(f.getnframes()))

            with wave.open(merged_wav, 'wb') as out:
                out.setparams(params)
                for frames in all_frames:
                    out.writeframes(frames)

            cmd = [FFMPEG, "-y", "-i", merged_wav, "-c:a", "libmp3lame", "-b:a", "128k", output_path]
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
        except Exception as e2:
            print(f"  [WARN] All concat methods failed: {e2}")
            raise RuntimeError(f"Audio concatenation failed: {e2}")
    finally:
        import shutil
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)


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
    cmd = [
        FFMPEG, "-i", video_path,
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    for line in result.stderr.split("\n"):
        if "Duration" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
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


def adjust_slide_durations_per_audio(slides, audio_files):
    adjusted_count = 0
    audio_idx = 0
    for i, slide in enumerate(slides):
        narration = slide.get("narration", "")
        if narration and narration.strip() and audio_idx < len(audio_files):
            try:
                dur = get_audio_duration(audio_files[audio_idx])
                slide["duration"] = max(3, round(dur, 2))
                adjusted_count += 1
            except Exception:
                pass
            audio_idx += 1

    total = sum(s.get("duration", 10) for s in slides)
    print(f"  [DURATION] Per-slide sync: {adjusted_count}/{len(slides)} slides matched, total {total:.1f}s")
    return slides


def record_video(slides, template_html, output_path, width=1080, height=1920, style="dark", visual_style="tech", brand_spec=None):
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

        record_start = time.time()

        template_url = f"file:///{os.path.abspath(template_html).replace(os.sep, '/')}"
        page.goto(template_url)
        page.wait_for_timeout(500)

        page.evaluate(f"window.slidesData = {json.dumps({'slides': slides}, ensure_ascii=False)}")
        page.evaluate(f"window.themeName = '{style}'")
        page.evaluate(f"window.visualStyle = '{visual_style}'")

        if brand_spec:
            page.evaluate(f"window.brandSpec = {json.dumps(brand_spec, ensure_ascii=False)}")
        else:
            page.evaluate("window.brandSpec = null")

        anim_start = time.time()
        offset_seconds = anim_start - record_start

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

    print(f"  [VIDEO] Recorded: {output_path} (blank prefix: {offset_seconds:.2f}s)")
    return output_path, offset_seconds


def prepare_video(raw_path, output_path, trim_start=0.0, target_duration=None):
    video_dur = get_video_duration(raw_path)
    if video_dur is None:
        print("  [WARN] Could not get video duration, copying as-is")
        import shutil
        shutil.copy2(raw_path, output_path)
        return output_path

    effective_dur = max(0, video_dur - trim_start)

    cmd = [FFMPEG, "-y"]

    if trim_start > 0.3:
        cmd.extend(["-ss", f"{trim_start:.3f}"])

    cmd.extend(["-i", raw_path])

    pts_factor = 1.0
    if target_duration and effective_dur > 0 and abs(effective_dur - target_duration) > 0.5:
        pts_factor = target_duration / effective_dur
        cmd.extend(["-filter:v", f"setpts=PTS*{pts_factor:.6f}"])
        print(f"  [PREPARE] Speed: {1/pts_factor:.4f}x ({effective_dur:.1f}s -> {target_duration:.1f}s)")

    cmd.extend([
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-an",
        "-movflags", "+faststart",
        output_path,
    ])
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  [PREPARE] Output: {output_path}")
    return output_path


def merge_video_audio(video_path, audio_path, output_path, target_duration=None):
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


SFX_CUE_PRESETS = {
    "tech": [
        {"time": 0.10, "name": "whoosh", "volume": 0.55},
        {"time": 3.0, "name": "enter", "volume": 0.55},
        {"time": 4.0, "name": "slide-in", "volume": 0.55},
        {"time": 5.5, "name": "sparkle", "volume": 0.70},
        {"time": 7.0, "name": "sparkle", "volume": 0.70},
        {"time": 8.5, "name": "sparkle", "volume": 0.70},
        {"time": 10.0, "name": "sparkle", "volume": 0.70},
        {"time": 11.5, "name": "sparkle", "volume": 0.70},
        {"time": 14.0, "name": "click", "volume": 0.55},
        {"time": 17.8, "name": "logo-reveal", "volume": 0.85},
    ],
    "edu": [
        {"time": 0.10, "name": "whoosh", "volume": 0.50},
        {"time": 3.0, "name": "enter", "volume": 0.50},
        {"time": 5.0, "name": "sparkle", "volume": 0.65},
        {"time": 8.0, "name": "sparkle", "volume": 0.65},
        {"time": 11.0, "name": "sparkle", "volume": 0.65},
        {"time": 14.0, "name": "click", "volume": 0.50},
        {"time": 17.8, "name": "logo-reveal", "volume": 0.80},
    ],
    "compare": [
        {"time": 0.10, "name": "whoosh", "volume": 0.55},
        {"time": 3.0, "name": "enter", "volume": 0.55},
        {"time": 5.0, "name": "click", "volume": 0.60},
        {"time": 8.0, "name": "click", "volume": 0.60},
        {"time": 11.0, "name": "sparkle", "volume": 0.70},
        {"time": 14.0, "name": "click", "volume": 0.55},
        {"time": 17.8, "name": "logo-reveal", "volume": 0.85},
    ],
    "philosophy": [
        {"time": 0.10, "name": "whoosh", "volume": 0.40},
        {"time": 5.0, "name": "sparkle", "volume": 0.50},
        {"time": 10.0, "name": "sparkle", "volume": 0.50},
        {"time": 17.8, "name": "logo-reveal", "volume": 0.75},
    ],
}


def _generate_sfx_track(sfx_cues, sfx_dir, duration, output_path):
    if not sfx_cues or not sfx_dir or not os.path.isdir(sfx_dir):
        return None

    available = {}
    for f in os.listdir(sfx_dir):
        name = os.path.splitext(f)[0]
        available[name] = os.path.join(sfx_dir, f)

    valid_cues = []
    for cue in sfx_cues:
        if cue["time"] < duration and cue["name"] in available:
            valid_cues.append(cue)

    if not valid_cues:
        return None

    inputs = []
    filter_parts = []
    for i, cue in enumerate(valid_cues):
        path = available[cue["name"]]
        inputs.extend(["-i", path])
        delay_ms = int(cue["time"] * 1000)
        vol = cue.get("volume", 0.55)
        filter_parts.append(
            f"[{i + 1}:a]adelay={delay_ms}|{delay_ms},volume={vol}[sfx{i}]"
        )

    mix_inputs = "".join(f"[sfx{i}]" for i in range(len(valid_cues)))
    filter_parts.append(f"{mix_inputs}amix=inputs={len(valid_cues)}:duration=longest[sfxout]")

    filter_complex = ";".join(filter_parts)

    cmd = [
        FFMPEG, "-y",
        "-f", "lavfi",
        "-i", f"anullsrc=r=44100:cl=stereo",
    ]
    cmd.extend(inputs)
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[sfxout]",
        "-t", f"{duration:.2f}",
        "-c:a", "aac",
        "-b:a", "128k",
        output_path,
    ])

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"  [SFX] Generated SFX track: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"  [WARN] SFX generation failed: {e}")
        return None


def merge_with_sfx(video_path, narration_path, bgm_path, sfx_cues, sfx_dir, output_path,
                   bgm_volume=0.3, duck_threshold=0.1, duck_ratio=4):
    duration = get_video_duration(video_path)
    if duration is None:
        duration = get_audio_duration(video_path)

    sfx_path = None
    if sfx_cues and sfx_dir:
        sfx_tmp = os.path.join(os.path.dirname(output_path), "sfx_track.m4a")
        sfx_path = _generate_sfx_track(sfx_cues, sfx_dir, duration, sfx_tmp)

    if not sfx_path:
        if bgm_path and os.path.exists(bgm_path):
            return merge_with_bgm_ducking(video_path, narration_path, bgm_path, output_path,
                                          bgm_volume, duck_threshold, duck_ratio)
        elif narration_path and os.path.exists(narration_path):
            return merge_video_audio(video_path, narration_path, output_path)
        else:
            return None

    audio_inputs = []
    filter_parts = []

    input_idx = 1
    if narration_path and os.path.exists(narration_path):
        audio_inputs.extend(["-i", narration_path])
        filter_parts.append(f"[{input_idx}:a]volume=1.0[narr]")
        narr_idx = input_idx
        input_idx += 1
    else:
        narr_idx = None

    if bgm_path and os.path.exists(bgm_path):
        audio_inputs.extend(["-i", bgm_path])
        filter_parts.append(
            f"[{input_idx}:a]volume={bgm_volume},atrim=0:{duration:.2f},"
            f"afade=t=in:st=0:d=0.3,afade=t=out:st={max(0, duration - 1):.2f}:d=1[bgm]"
        )
        bgm_idx = input_idx
        input_idx += 1
    else:
        bgm_idx = None

    audio_inputs.extend(["-i", sfx_path])
    filter_parts.append(f"[{input_idx}:a]volume=0.55[sfx]")
    sfx_idx = input_idx
    input_idx += 1

    if narr_idx and bgm_idx:
        filter_parts.append(
            f"[bgm][narr]sidechaincompress=threshold={duck_threshold}:ratio={duck_ratio}:"
            f"attack=5:release=50[bgm_ducked]"
        )
        filter_parts.append("[bgm_ducked][sfx]amix=inputs=2:duration=longest[mixed]")
    elif narr_idx:
        filter_parts.append(f"[narr][sfx]amix=inputs=2:duration=longest[mixed]")
    elif bgm_idx:
        filter_parts.append(f"[bgm][sfx]amix=inputs=2:duration=longest[mixed]")
    else:
        filter_parts.append(f"[sfx]acopy[mixed]")

    filter_complex = ";".join(filter_parts)

    cmd = [
        FFMPEG, "-y",
        "-i", video_path,
    ]
    cmd.extend(audio_inputs)
    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[mixed]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        output_path,
    ])

    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  [BGM+SFX] Output: {output_path}")
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
                   style=None, bgm=None, fmt="mp4", visual_style="tech", sfx_dir=None,
                   brand_spec_path=None):
    check_dependencies()

    if style is not None and style not in VALID_STYLES:
        print(f"  [WARN] Unknown style '{style}', using 'dark'")
        style = "dark"

    if visual_style not in VALID_VISUAL_STYLES:
        print(f"  [WARN] Unknown visual_style '{visual_style}', using 'tech'")
        visual_style = "tech"

    if fmt not in VALID_FORMATS:
        print(f"  [WARN] Unknown format '{fmt}', using 'mp4'")
        fmt = "mp4"

    if template_html is None:
        template_html = DEFAULT_TEMPLATE

    brand_spec = None
    if brand_spec_path and os.path.exists(brand_spec_path):
        with open(brand_spec_path, "r", encoding="utf-8") as f:
            brand_spec = json.load(f)
        print(f"  [BRAND] Loaded brand spec: {brand_spec_path}")

    if style is None:
        if brand_spec and brand_spec.get("detected_theme"):
            style = brand_spec["detected_theme"]
            print(f"  [BRAND] Auto-detected theme from brand spec: {style}")
        else:
            style = "dark"
            print(f"  [STYLE] No style specified, using default: dark")

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(output_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)

    with open(slides_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    slides = data["slides"]

    print(f"[1/6] Generating TTS narrations ({len(slides)} slides)...")
    narrations = [s.get("narration", "") for s in slides]
    audio_dir = os.path.join(output_dir, "audio")
    audio_files = generate_tts(narrations, audio_dir, voice=voice, rate=rate)

    print("[2/6] Concatenating audio...")
    concat_audio_path = os.path.join(output_dir, "narration.mp3")
    if audio_files:
        concat_audios(audio_files, concat_audio_path)
        print("[2.5/6] Syncing slide durations to audio...")
        slides = adjust_slide_durations_per_audio(slides, audio_files)
    else:
        concat_audio_path = None
        print("  [WARN] No narrations generated, producing silent video")

    print(f"[3/6] Recording Canvas animation (style={style}, visual={visual_style})...")
    raw_video_path = os.path.join(output_dir, "raw.webm")
    raw_video_path, offset_seconds = record_video(
        slides, template_html, raw_video_path, width=width, height=height,
        style=style, visual_style=visual_style, brand_spec=brand_spec)

    target_duration = sum(s.get("duration", 10) for s in slides)
    if concat_audio_path and os.path.exists(concat_audio_path):
        try:
            audio_dur = get_audio_duration(concat_audio_path)
            target_duration = audio_dur
            print(f"  [SYNC] Audio duration: {audio_dur:.2f}s, using as target")
        except Exception:
            pass

    print(f"[4/6] Preparing video (trim={offset_seconds:.2f}s, target={target_duration:.2f}s)...")
    prepared_path = os.path.join(output_dir, "prepared.mp4")
    prepare_video(raw_video_path, prepared_path,
                  trim_start=offset_seconds, target_duration=target_duration)

    print("[5/6] Merging video and audio...")
    final_path = os.path.join(output_dir, "final.mp4")

    sfx_cues = SFX_CUE_PRESETS.get(visual_style)
    has_sfx = sfx_dir and os.path.isdir(sfx_dir) and sfx_cues

    if has_sfx:
        print(f"  [SFX] Applying BGM+SFX with ducking (visual_style={visual_style})")
        merge_with_sfx(prepared_path, concat_audio_path, bgm, sfx_cues, sfx_dir, final_path)
    elif bgm and os.path.exists(bgm) and concat_audio_path and os.path.exists(concat_audio_path):
        print(f"  [BGM] Applying BGM with ducking: {bgm}")
        merge_with_bgm_ducking(prepared_path, concat_audio_path, bgm, final_path)
    elif concat_audio_path and os.path.exists(concat_audio_path):
        merge_video_audio(prepared_path, concat_audio_path, final_path)
    else:
        cmd = [
            FFMPEG, "-y",
            "-i", prepared_path,
            "-c:v", "copy",
            "-movflags", "+faststart",
            "-an",
            final_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    if compress:
        compressed_path = os.path.join(output_dir, "final_compressed.mp4")
        compress_video(final_path, compressed_path)
        final_path = compressed_path

    print("[6/6] Exporting additional formats...")
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
    print(f"  Visual: {visual_style}")
    print(f"  Format: {fmt}")
    if bgm:
        print(f"  BGM: {bgm}")
    if has_sfx:
        print(f"  SFX: {sfx_dir} ({len(sfx_cues)} cues)")

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
    parser.add_argument("--style", default=None,
                        help="Visual style: dark, warm, minimal, nature. Auto-detected from brand-spec if omitted.")
    parser.add_argument("--visual-style", default="tech", choices=VALID_VISUAL_STYLES,
                        dest="visual_style",
                        help="Cinematic visual language: tech, edu, compare, philosophy")
    parser.add_argument("--bgm", default=None,
                        help="Background music file path (MP3/WAV). Auto ducking when narration plays.")
    parser.add_argument("--sfx-dir", default=None, dest="sfx_dir",
                        help="SFX audio directory (contains whoosh.mp3, sparkle.mp3, etc.)")
    parser.add_argument("--format", default="mp4", choices=VALID_FORMATS,
                        help="Output format: mp4 (25fps), mp4_60fps, gif")
    parser.add_argument("--brand-spec", default=None, dest="brand_spec",
                        help="Path to brand-spec.json for color override on top of theme")

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
        visual_style=args.visual_style,
        sfx_dir=args.sfx_dir,
        brand_spec_path=args.brand_spec,
    )


if __name__ == "__main__":
    main()
