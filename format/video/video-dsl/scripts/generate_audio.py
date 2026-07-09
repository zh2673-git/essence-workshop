"""
根据 VideoGenerationSpec 生成 TTS 旁白与 BGM 混合音频。
"""
import argparse
import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Any

try:
    import edge_tts
except ImportError:
    raise ImportError('请安装 edge-tts: pip install edge-tts')


def find_ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    if subprocess.run(['ffmpeg', '-version'], capture_output=True, shell=True).returncode == 0:
        return 'ffmpeg'
    raise RuntimeError('找不到 ffmpeg')


async def tts_to_file(text: str, output_path: str, voice: str = 'zh-CN-XiaoxiaoNeural'):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def concatenate_audios(paths: list[str], output_path: str, target_duration: float, ffmpeg: str):
    if not paths:
        # Generate silence
        subprocess.run(
            [ffmpeg, '-y', '-f', 'lavfi', '-i', f'anullsrc=r=24000:cl=mono',
             '-t', str(target_duration), '-acodec', 'aac', '-b:a', '128k', output_path],
            check=True
        )
        return

    list_file = output_path + '.list'
    with open(list_file, 'w', encoding='utf-8') as f:
        for p in paths:
            f.write(f"file '{os.path.abspath(p).replace(chr(39), chr(39)+chr(39))}'\n")
    concat_tmp = output_path + '.concat.mp3'
    subprocess.run(
        [ffmpeg, '-y', '-f', 'concat', '-safe', '0', '-i', list_file,
         '-c', 'copy', concat_tmp],
        check=True
    )
    os.remove(list_file)
    # Pad or trim to exact target duration.
    subprocess.run(
        [ffmpeg, '-y', '-i', concat_tmp, '-af',
         f'apad=whole_dur={target_duration},atrim=0:{target_duration}',
         '-acodec', 'libmp3lame', '-q:a', '2', output_path],
        check=True
    )
    os.remove(concat_tmp)


def mix_bgm(narration_path: str, bgm_path: str, output_path: str, bgm_volume: float, ffmpeg: str):
    if not bgm_path or not os.path.exists(bgm_path):
        if os.path.exists(output_path):
            os.remove(output_path)
        os.rename(narration_path, output_path)
        return
    subprocess.run(
        [ffmpeg, '-y', '-i', narration_path, '-i', bgm_path,
         '-filter_complex', f'[1:a]volume={bgm_volume}[bgm];[0:a][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]',
         '-map', '[aout]', '-c:a', 'aac', '-b:a', '128k', output_path],
        check=True
    )


async def generate_audio(spec_path: str, output_dir: str, voice: str = 'zh-CN-XiaoxiaoNeural', bgm_path: str = '', bgm_volume: float = 0.2):
    os.makedirs(output_dir, exist_ok=True)
    with open(spec_path, 'r', encoding='utf-8') as f:
        spec: dict[str, Any] = json.load(f)

    ffmpeg = find_ffmpeg()
    fps = spec.get('fps', 30)
    total_duration = spec.get('durationSeconds', 60)

    sections = spec.get('sections', [])
    segment_files: list[str] = []

    # Generate silence for gaps? Simpler: concatenate in order and trim/pad to total duration.
    for i, section in enumerate(sections):
        text = section.get('narration', '')
        if not text:
            # Create silence matching section duration
            duration_frames = section.get('durationFrames', int(total_duration * fps / len(sections)) if sections else total_duration * fps)
            duration = duration_frames / fps
            silent = os.path.join(output_dir, f'section_{i:03d}_silence.aac')
            subprocess.run(
                [ffmpeg, '-y', '-f', 'lavfi', '-i', f'anullsrc=r=24000:cl=mono',
                 '-t', str(duration), '-acodec', 'aac', '-b:a', '128k', silent],
                check=True
            )
            segment_files.append(silent)
            continue

        out = os.path.join(output_dir, f'section_{i:03d}.mp3')
        await tts_to_file(text, out, voice=voice)
        segment_files.append(out)

    narration_concat = os.path.join(output_dir, 'narration.mp3')
    concatenate_audios(segment_files, narration_concat, total_duration, ffmpeg)

    final_audio = os.path.join(output_dir, 'audio.m4a')
    mix_bgm(narration_concat, bgm_path, final_audio, bgm_volume, ffmpeg)
    return final_audio


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('spec', help='spec.json 路径')
    parser.add_argument('--output', required=True, help='输出目录')
    parser.add_argument('--voice', default='zh-CN-XiaoxiaoNeural')
    parser.add_argument('--bgm', default='', help='背景音乐文件路径')
    parser.add_argument('--bgm-volume', type=float, default=0.2)
    args = parser.parse_args()

    audio_path = asyncio.run(generate_audio(args.spec, args.output, args.voice, args.bgm, args.bgm_volume))
    print(f'[Audio] {audio_path}')


if __name__ == '__main__':
    main()
