import { spawnSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

function findImageioFfmpeg(): string | null {
  try {
    const result = spawnSync(
      'python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"',
      { encoding: 'utf-8', shell: true }
    );
    if (result.status === 0) {
      const candidate = result.stdout.trim();
      if (fs.existsSync(candidate)) return candidate;
    }
  } catch {
    // ignore
  }
  return null;
}

export function findFfmpeg(): string | null {
  const imageio = findImageioFfmpeg();
  const candidates = ['ffmpeg', imageio].filter(Boolean) as string[];
  for (const cmd of candidates) {
    const result = spawnSync(cmd, ['-version'], { encoding: 'utf-8', shell: true });
    if (result.status === 0) return cmd;
  }
  return null;
}

export function findFfprobe(ffmpegPath: string): string | null {
  if (!ffmpegPath) return null;
  const ffprobe = ffmpegPath.replace('ffmpeg', 'ffprobe');
  if (fs.existsSync(ffprobe)) return ffprobe;
  try {
    const result = spawnSync(
      'python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe().replace(\\\'ffmpeg\\\',\\\'ffprobe\\\'))"',
      { encoding: 'utf-8', shell: true }
    );
    if (result.status === 0) {
      const candidate = result.stdout.trim();
      if (fs.existsSync(candidate)) return candidate;
    }
  } catch {
    // ignore
  }
  const result = spawnSync('ffprobe', ['-version'], { encoding: 'utf-8', shell: true });
  if (result.status === 0) return 'ffprobe';
  return null;
}

export function findChrome(): string | null {
  try {
    const resolved = import.meta.resolve('playwright');
    return resolved ? 'playwright' : null;
  } catch {
    return null;
  }
}

export function getVideoCoreRoot(): string {
  const currentDir = path.dirname(fileURLToPath(import.meta.url));
  return path.resolve(currentDir, '..', '..', 'video-core');
}

export function checkDependencies(): { ffmpeg: string; ok: boolean; missing: string[] } {
  const missing: string[] = [];
  const ffmpeg = findFfmpeg();
  if (!ffmpeg) missing.push('ffmpeg (install via conda or pip install imageio-ffmpeg)');
  const chrome = findChrome();
  if (!chrome) missing.push('playwright (npm install playwright)');
  return { ffmpeg: ffmpeg ?? '', ok: missing.length === 0, missing };
}
