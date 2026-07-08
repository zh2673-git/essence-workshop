import type { ValidationReport, VideoGenerationSpec } from './types.js';

export function validateVideoProgram(code: string, spec: VideoGenerationSpec): ValidationReport {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (!code.includes('<Composition')) {
    errors.push('缺少 <Composition> 组件');
  }

  if (/animation\s*:/.test(code) || /transition\s*:/.test(code)) {
    errors.push('禁止使用 CSS animation / transition');
  }

  if (/requestAnimationFrame\s*\(/.test(code) || /setInterval\s*\(/.test(code)) {
    errors.push('禁止使用 requestAnimationFrame / setInterval');
  }

  if (!code.includes('useCurrentFrame')) {
    warnings.push('未检测到 useCurrentFrame，可能缺少动画');
  }

  const srcMatches = code.match(/src\s*=\s*["']([^"']+)["']/g) || [];
  for (const src of srcMatches) {
    if (!src.includes('staticFile(')) {
      warnings.push(`媒体资源建议通过 staticFile 引用：${src}`);
    }
  }

  if (!code.includes('export const VideoProgram') && !code.includes('export function VideoProgram')) {
    errors.push('必须导出 VideoProgram 组件');
  }

  const totalFrames = spec.durationSeconds * spec.fps;
  const sectionFrames = spec.sections.reduce((sum, s) => sum + (s.durationFrames ?? 0), 0);
  if (sectionFrames > 0 && sectionFrames !== totalFrames) {
    warnings.push(`sections durationFrames 总和 (${sectionFrames}) 与总帧数 (${totalFrames}) 不一致`);
  }

  return { valid: errors.length === 0, errors, warnings };
}
