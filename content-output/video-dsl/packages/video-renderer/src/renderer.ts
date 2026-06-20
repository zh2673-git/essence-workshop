import { build } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs';
import http from 'http';
import path from 'path';
import { spawnSync } from 'child_process';
import { chromium } from 'playwright';
import type { RenderOptions, RenderProgress, RenderResult } from './types.js';
import { checkDependencies, getVideoCoreRoot } from './env.js';

const MAIN_TSX = `import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom/client';
import { VideoProgram } from './VideoProgram';

const win = window as any;
win.__essence_currentFrame = 0;
win.__essence_listeners = new Set();
win.__essence_setFrame = (f: number) => {
  win.__essence_currentFrame = f;
  win.__essence_listeners.forEach((l: (n: number) => void) => l(f));
};
win.__essence_subscribe = (listener: (n: number) => void) => {
  win.__essence_listeners.add(listener);
  return () => win.__essence_listeners.delete(listener);
};

function App() {
  // Force re-render once globals are ready and after first mount.
  const [, setTick] = useState(0);
  useEffect(() => {
    setTick((n) => n + 1);
  }, []);
  return <VideoProgram />;
}

const root = document.getElementById('root');
if (root) {
  ReactDOM.createRoot(root).render(<App />);
}
`;

const INDEX_HTML = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Essence Video</title>
  <style>body { margin: 0; overflow: hidden; background: #000; }</style>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.tsx"></script>
</body>
</html>
`;

function getDurationInFrames(entryFile: string, defaultFrames = 90): number {
  const content = fs.readFileSync(entryFile, 'utf-8');
  const matches = Array.from(content.matchAll(/durationInFrames\s*[=:]\s*\{?(\d+)\}?/g));
  if (matches.length === 0) return defaultFrames;
  // Composition-level duration is typically the last/largest value.
  return Math.max(...matches.map((m) => parseInt(m[1], 10)));
}

function getDimensions(entryFile: string): { width: number; height: number } {
  const content = fs.readFileSync(entryFile, 'utf-8');
  const widthMatches = Array.from(content.matchAll(/width\s*[=:]\s*\{?(\d+)\}?/g));
  const heightMatches = Array.from(content.matchAll(/height\s*[=:]\s*\{?(\d+)\}?/g));
  return {
    width: widthMatches.length ? Math.max(...widthMatches.map((m) => parseInt(m[1], 10))) : 1080,
    height: heightMatches.length ? Math.max(...heightMatches.map((m) => parseInt(m[1], 10))) : 1920,
  };
}

function serveStatic(rootDir: string, port: number): Promise<http.Server> {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      let filePath = path.join(rootDir, req.url === '/' ? 'index.html' : req.url!);
      if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
        filePath = path.join(rootDir, 'index.html');
      }
      const ext = path.extname(filePath);
      const contentType: Record<string, string> = {
        '.html': 'text/html',
        '.js': 'application/javascript',
        '.mjs': 'application/javascript',
        '.ts': 'application/javascript',
        '.tsx': 'application/javascript',
        '.css': 'text/css',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.svg': 'image/svg+xml',
      };
      res.writeHead(200, { 'Content-Type': contentType[ext] ?? 'application/octet-stream' });
      fs.createReadStream(filePath).pipe(res);
    });
    server.listen(port, () => resolve(server));
  });
}

export async function renderVideo(options: RenderOptions): Promise<RenderResult> {
  const { entryFile, outputDir = 'output/video', publicDir, fps = 30, deviceScaleFactor = 2 } = options;
  const deps = checkDependencies();
  if (!deps.ok) {
    throw new Error(`Missing dependencies: ${deps.missing.join(', ')}`);
  }

  const dims = getDimensions(entryFile);
  const width = options.width ?? dims.width;
  const height = options.height ?? dims.height;
  const durationInFrames = options.durationInFrames ?? getDurationInFrames(entryFile);
  const durationInSeconds = durationInFrames / fps;

  const absOutputDir = path.resolve(outputDir);
  const bundleDir = path.join(absOutputDir, '_bundle');
  const distDir = path.join(bundleDir, 'dist');
  const framesDir = path.join(absOutputDir, '_frames');
  fs.mkdirSync(framesDir, { recursive: true });
  fs.mkdirSync(path.join(bundleDir, 'src'), { recursive: true });

  const videoCoreRoot = getVideoCoreRoot();
  const nodeModulesRoot = path.join(videoCoreRoot, 'node_modules');
  const reactAlias = path.join(nodeModulesRoot, 'react');
  const reactDomAlias = path.join(nodeModulesRoot, 'react-dom');

  fs.copyFileSync(path.resolve(entryFile), path.join(bundleDir, 'src', 'VideoProgram.tsx'));
  if (publicDir) {
    const targetPublic = path.join(bundleDir, 'public');
    fs.cpSync(path.resolve(publicDir), targetPublic, { recursive: true, force: true });
  }

  fs.writeFileSync(path.join(bundleDir, 'index.html'), INDEX_HTML);
  fs.writeFileSync(path.join(bundleDir, 'src', 'main.tsx'), MAIN_TSX);

  options.onProgress?.({ currentFrame: 0, totalFrames: durationInFrames, phase: 'bundle' });

  await build({
    root: bundleDir,
    build: {
      outDir: distDir,
      emptyOutDir: true,
    },
    plugins: [react()],
    resolve: {
      alias: {
        '@essence/video-core': videoCoreRoot,
        react: reactAlias,
        'react-dom': reactDomAlias,
        'react/jsx-runtime': path.join(reactAlias, 'jsx-runtime.js'),
        'react/jsx-dev-runtime': path.join(reactAlias, 'jsx-dev-runtime.js'),
      },
    },
  });

  const port = 12451;
  const server = await serveStatic(distDir, port);

  const browser = await chromium.launch({ channel: 'chrome' }).catch(async () => chromium.launch());
  const context = await browser.newContext({
    viewport: { width, height },
    deviceScaleFactor,
  });
  const page = await context.newPage();
  await page.goto(`http://localhost:${port}/`, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => !!(window as any).__essence_setFrame);

  options.onProgress?.({ currentFrame: 0, totalFrames: durationInFrames, phase: 'screenshot' });

  for (let frame = 0; frame < durationInFrames; frame++) {
    await page.evaluate((f) => (window as any).__essence_setFrame(f), frame);
    await page.waitForTimeout(50);
    await page.waitForLoadState('networkidle');
    const padded = String(frame).padStart(5, '0');
    await page.screenshot({
      path: path.join(framesDir, `frame_${padded}.png`),
      type: 'png',
    });
    options.onProgress?.({ currentFrame: frame + 1, totalFrames: durationInFrames, phase: 'screenshot' });
  }

  await browser.close();
  await new Promise<void>((resolve, reject) => server.close((err) => (err ? reject(err) : resolve())));

  options.onProgress?.({ currentFrame: durationInFrames, totalFrames: durationInFrames, phase: 'encode' });

  const framePattern = path.join(framesDir, 'frame_%05d.png');
  const format = options.format ?? 'mp4';
  const quality = options.quality ?? 'medium';
  const crf = quality === 'draft' ? '28' : quality === 'high' ? '17' : '20';
  const scale = deviceScaleFactor === 1 ? `${width}:${height}` : `${width * deviceScaleFactor}:${height * deviceScaleFactor}`;

  if (format === 'gif') {
    const gifPath = path.join(absOutputDir, 'final.gif');
    const args = [
      '-y',
      '-framerate', String(fps),
      '-i', framePattern,
      '-vf', `fps=${fps},scale=${width}:${height}:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer`,
      '-loop', '0',
      gifPath,
    ];
    const result = spawnSync(deps.ffmpeg, args, { stdio: 'pipe' });
    if (result.status !== 0) {
      throw new Error(`FFmpeg GIF failed: ${result.stderr?.toString() ?? 'unknown error'}`);
    }
    options.onProgress?.({ currentFrame: durationInFrames, totalFrames: durationInFrames, phase: 'done' });
    return { videoPath: gifPath, framesDir, durationInSeconds };
  }

  const videoPath = path.join(absOutputDir, 'final.mp4');
  const hasAudio = options.audioPath && fs.existsSync(options.audioPath);
  const hasBgm = options.bgmPath && fs.existsSync(options.bgmPath);

  const args = [
    '-y',
    '-framerate', String(fps),
    '-i', framePattern,
  ];

  let filterComplex = '';
  let outputMapping = ['-map', '0:v'];

  if (hasAudio && hasBgm) {
    args.push('-i', options.audioPath!, '-i', options.bgmPath!);
    filterComplex = '[1:a][2:a]amix=inputs=2:duration=first:dropout_transition=2[aout]';
    outputMapping = ['-map', '0:v', '-map', '[aout]'];
  } else if (hasAudio) {
    args.push('-i', options.audioPath!);
    outputMapping = ['-map', '0:v', '-map', '1:a'];
  }

  args.push(
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', quality === 'draft' ? 'superfast' : quality === 'high' ? 'slow' : 'medium',
    '-crf', crf,
    '-movflags', '+faststart'
  );

  if (hasAudio || hasBgm) {
    args.push('-c:a', 'aac', '-b:a', '128k', '-shortest');
    if (filterComplex) args.push('-filter_complex', filterComplex);
  }

  args.push(...outputMapping, videoPath);

  const result = spawnSync(deps.ffmpeg, args, { stdio: 'pipe' });
  if (result.status !== 0) {
    throw new Error(`FFmpeg failed: ${result.stderr?.toString() ?? 'unknown error'}`);
  }

  options.onProgress?.({ currentFrame: durationInFrames, totalFrames: durationInFrames, phase: 'done' });

  return { videoPath, framesDir, durationInSeconds };
}
