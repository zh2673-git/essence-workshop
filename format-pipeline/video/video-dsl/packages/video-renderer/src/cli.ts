#!/usr/bin/env node
import { renderVideo } from './renderer.js';

const args = process.argv.slice(2);
const entryFile = args[0];
if (!entryFile) {
  console.error('Usage: essence-render <entry.tsx> [--output dir] [--fps n] [--width n] [--height n] [--audio path] [--bgm path] [--format mp4|gif] [--quality draft|medium|high]');
  process.exit(1);
}

const options: Record<string, string> = {};
for (let i = 1; i < args.length; i += 2) {
  const key = args[i].replace(/^--/, '');
  options[key] = args[i + 1];
}

renderVideo({
  entryFile,
  outputDir: options.output ?? 'output/video',
  fps: options.fps ? parseInt(options.fps, 10) : 30,
  width: options.width ? parseInt(options.width, 10) : undefined,
  height: options.height ? parseInt(options.height, 10) : undefined,
  audioPath: options.audio,
  bgmPath: options.bgm,
  format: options.format as 'mp4' | 'gif' | undefined,
  quality: options.quality as 'draft' | 'medium' | 'high' | undefined,
  onProgress: (p) => {
    if (p.phase === 'screenshot') {
      process.stdout.write(`\r  [Render] Frame ${p.currentFrame}/${p.totalFrames}`);
    }
  },
})
  .then((result) => {
    console.log(`\n  [Done] Video: ${result.videoPath}`);
  })
  .catch((err) => {
    console.error('\n  [Error]', err.message);
    process.exit(1);
  });
