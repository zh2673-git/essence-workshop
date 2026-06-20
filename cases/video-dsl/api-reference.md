# Essence Video DSL API 参考

> 版本：v0.1.0  
> 定位：为 Agent 提供轻量、狭窄、确定性的 Video DSL API。

## 核心原则

- 所有动画必须基于 `useCurrentFrame()` / `useSequenceTime()` 返回的 frame 计算。
- 使用 `interpolate(frame, [start, end], [from, to])` 计算数值属性。
- 使用 `<Sequence>` 控制元素出现时间。
- 使用 `<AbsoluteFill>` 作为根布局容器。
- 媒体文件必须使用 `staticFile('relative/path')` 引用。
- 禁止使用 CSS animation、transition、requestAnimationFrame、setInterval。

## Hooks

### useCurrentFrame

```tsx
const frame = useCurrentFrame();
```

返回当前全局帧号，范围 `[0, durationInFrames)`。

### useSequenceTime

```tsx
const frame = useSequenceTime();
```

返回当前 Sequence 内的相对帧号（全局帧减去 Sequence 的 `from`）。

### useVideoConfig

```tsx
const { width, height, fps, durationInFrames } = useVideoConfig();
```

返回当前 Composition 的配置。

## 数学工具

### interpolate

```tsx
const value = interpolate(frame, [0, 60], [0, 100]);
const opacity = interpolate(frame, [0, 30], [0, 1], { easing: t => t * t });
```

将 `frame` 从 `inputRange` 线性映射到 `outputRange`。

**选项**：
- `easing`: `(t: number) => number`
- `extrapolateLeft`: `'extend' | 'clamp' | 'identity'` 默认 `'clamp'`
- `extrapolateRight`: `'extend' | 'clamp' | 'identity'` 默认 `'clamp'`

## 组件

### Composition

```tsx
<Composition
  id="MyVideo"
  component={MyScene}
  width={1080}
  height={1920}
  fps={30}
  durationInFrames={270}
/>
```

### Sequence

```tsx
<Sequence from={90} durationInFrames={180}>
  <MyScene />
</Sequence>
```

只在 `[from, from + durationInFrames)` 区间内渲染子元素。

### AbsoluteFill

```tsx
<AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
  <h1>标题</h1>
</AbsoluteFill>
```

绝对定位填充父容器。

### Img / Video / Audio

```tsx
<Img src={staticFile('image.png')} />
<Video src={staticFile('clip.mp4')} />
<Audio src={staticFile('bgm.mp3')} />
```

媒体组件，自动注册到资源清单。注意：DSL 管线中音频实际通过 `--audio` / `--bgm` 在 FFmpeg 阶段混合，`<Audio>` 主要用于资源声明。

## 动画组件库

### FadeIn

```tsx
<FadeIn startFrame={0} endFrame={30}>
  <div>渐入内容</div>
</FadeIn>
```

### FlyIn

```tsx
<FlyIn direction="bottom" distance={120} startFrame={0} endFrame={40}>
  <div>飞入内容</div>
</FlyIn>
```

### Counter

```tsx
<Counter value={100} startFrame={0} endFrame={60} suffix="%" />
```

### Timeline

```tsx
<Timeline
  items={[
    { time: '2024', title: '事件一' },
    { time: '2025', title: '事件二', description: '详细说明' },
  ]}
  startFrame={0}
  revealFrames={30}
/>
```

### Compare

```tsx
<Compare
  left={{ label: '正数', value: '+5', color: '#38bdf8' }}
  right={{ label: '负数', value: '-5', color: '#f43f5e' }}
  startFrame={0}
  endFrame={60}
/>
```

## 工具

### staticFile

```tsx
const path = staticFile('public/image.png');
```

返回相对路径，并在渲染前将资源注册到 `AssetRegistry`。

## CLI

```bash
node packages/video-renderer/dist/cli.js <entry.tsx> \
  --output <dir> \
  --fps 30 \
  --width 1080 \
  --height 1920 \
  --audio <audio.m4a> \
  --bgm <bgm.mp3> \
  --format mp4 \
  --quality medium
```

- `--format`: `mp4` | `gif`
- `--quality`: `draft` | `medium` | `high`

## Python 入口

```bash
python -m scripts.cli video <VideoProgram.tsx> --pipeline dsl --output output/video/
```

*更多示例见 `examples/negative-numbers/VideoProgram.tsx`。*
