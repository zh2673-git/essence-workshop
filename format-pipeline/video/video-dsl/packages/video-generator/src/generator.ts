import fs from 'fs';
import path from 'path';
import type { GenerateOptions, GenerationResult, VideoGenerationSpec } from './types.js';
import { buildPrompt } from './prompt.js';
import { validateVideoProgram } from './validator.js';

export async function generateVideoProgram(options: GenerateOptions): Promise<GenerationResult> {
  const { spec, outputDir, agentClient, promptTemplate, maxRetries = 3 } = options;
  fs.mkdirSync(outputDir, { recursive: true });

  const specPath = path.join(outputDir, 'spec.json');
  fs.writeFileSync(specPath, JSON.stringify(spec, null, 2), 'utf-8');

  let prompt = buildPrompt(spec, promptTemplate);
  let code = '';
  let lastReport = validateVideoProgram('', spec);

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    code = await agentClient.generateCode(prompt);
    lastReport = validateVideoProgram(code, spec);
    if (lastReport.valid) break;
    if (attempt === maxRetries) {
      throw new Error(`生成失败，超过最大重试次数：\n${lastReport.errors.join('\n')}`);
    }
    prompt = `${prompt}\n\n# 上次生成的问题（请修复）\n${lastReport.errors.map((e) => `- ${e}`).join('\n')}`;
  }

  const videoProgramPath = path.join(outputDir, 'VideoProgram.tsx');
  fs.writeFileSync(videoProgramPath, code, 'utf-8');

  const manifest = {
    id: spec.title,
    width: aspectRatioToDimensions(spec.aspectRatio).width,
    height: aspectRatioToDimensions(spec.aspectRatio).height,
    fps: spec.fps,
    durationInFrames: spec.durationSeconds * spec.fps,
    assets: spec.assets ?? {},
    validation: lastReport,
  };
  const manifestPath = path.join(outputDir, 'manifest.json');
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), 'utf-8');

  return {
    videoProgramPath,
    manifestPath,
    specPath,
    assets: [...(spec.assets?.images ?? []), ...(spec.assets?.videos ?? []), ...(spec.assets?.bgm ? [spec.assets.bgm] : [])],
  };
}

function aspectRatioToDimensions(aspectRatio: string): { width: number; height: number } {
  switch (aspectRatio) {
    case '16:9':
      return { width: 1920, height: 1080 };
    case '1:1':
      return { width: 1080, height: 1080 };
    case '9:16':
    default:
      return { width: 1080, height: 1920 };
  }
}
