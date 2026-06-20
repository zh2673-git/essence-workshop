import type { VideoGenerationSpec } from './types.js';

const DEFAULT_TEMPLATE = `# Role
你是一名 Essence Video DSL 程序员。请根据输入的 VideoGenerationSpec，生成一个 TypeScript React 组件文件 VideoProgram.tsx。

# 必须遵守的规则
1. 所有动画必须基于 \`useCurrentFrame()\` 返回的 frame 计算。
2. 使用 \`interpolate(frame, [start, end], [from, to])\` 计算数值属性。
3. 使用 \`<Sequence from={...} durationInFrames={...}>\` 控制元素出现时间。
4. 使用 \`<AbsoluteFill>\` 作为根布局容器。
5. 媒体文件必须使用 \`staticFile('relative/path')\` 引用。
6. 禁止使用 CSS animation、transition、requestAnimationFrame。
7. 所有视觉变化必须能从 frame 推导，保证渲染确定性。
8. 组件必须导出为 \`export const VideoProgram\`。

# 输出格式
只输出完整的 TypeScript 代码，不要解释，不要 markdown 代码块标记。

# VideoGenerationSpec
{{spec_json}}

# 尺寸信息
- 宽度：{{width}} 像素
- 高度：{{height}} 像素
- 帧率：{{fps}} fps
- 总帧数：{{durationInFrames}}
`;

export function buildPrompt(spec: VideoGenerationSpec, template?: string): string {
  const tpl = template ?? DEFAULT_TEMPLATE;
  const dims = aspectRatioToDimensions(spec.aspectRatio);
  const durationInFrames = spec.durationSeconds * spec.fps;
  return tpl
    .replace('{{spec_json}}', JSON.stringify(spec, null, 2))
    .replace('{{width}}', String(dims.width))
    .replace('{{height}}', String(dims.height))
    .replace('{{fps}}', String(spec.fps))
    .replace('{{durationInFrames}}', String(durationInFrames));
}

export function aspectRatioToDimensions(aspectRatio: string): { width: number; height: number } {
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
