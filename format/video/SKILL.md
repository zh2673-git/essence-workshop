---
name: 视频管线
description: |
  视频格式管线：通过HTML直接录制+Edge TTS旁白+FFmpeg合并生成MP4。
  核心思路：HTML本身就是最好的视觉呈现，直接录制滚动过程配合TTS旁白。
  包含video-dsl子系统（声明式视频生成）。
  输入：HTML文件或认知产物。输出：.mp4文件。
  触发词：「做视频」「HTML转视频」。
version: 1.0
layer: format
pipeline: video
---

# 视频管线

> 通过 HTML 直接录制 + Edge TTS 旁白 + FFmpeg 合成生成 MP4。核心思路：HTML 本身就是最好的视觉呈现，无需转换到 Canvas 卡片模板——直接录制 HTML 页面的滚动过程，配合 TTS 旁白生成视频。包含 video-dsl 子系统支持声明式视频生成。

## 输入输出

- **输入**：HTML 文件（已有高质量视觉呈现）或认知产物（先走 HTML 管线再录制）
- **输出**：`.mp4` 文件（H.264 编码）

## 录制策略

1. **自动检测 section**：扫描 HTML 中的语义结构元素（section/分组/卡片等），确定滚动停止点
2. **按 section 停留**：每个 section 停留时间由对应 TTS 旁白时长决定，无旁白则使用默认停留
3. **平滑滚动**：使用 `scrollTo({behavior: 'smooth'})` 实现自然滚动
4. **首尾处理**：开头与结尾适当停留

> 具体的 section 选择器、停留时长、首尾停留秒数等由上层工作流/平台适配指定。

## 视频约束

| 参数 | 标准 | 说明 |
|------|------|------|
| 画幅 | 由上层 --aspect 指定 | 支持 9:16竖屏 / 16:9横屏 / 1:1方屏 |
| 帧率 | 30fps | Playwright默认 |
| 编码 | H.264 | 兼容性最好 |
| 设备像素比 | 2 | 保证清晰度 |
| 时长 | 由内容与旁白长度决定 | 时长范围由上层工作流指定 |

## 旁白生成

支持三种方式：

| 方式 | 参数 | 说明 |
|------|------|------|
| 单段旁白 | `--narration "完整旁白文本"` | 整段对应整个视频 |
| 多段旁白 | `--narration-file narration.txt` | 每行一段，对应一个 section |
| 代码传入 | `narration_sections=[...]` | 编程接口调用 |

### TTS语音参数

语音由上层通过 `--voice` 参数指定，格式层不自行判断场景。常用语音ID：

| 语音ID | 特点 |
|--------|------|
| zh-CN-YunxiNeural | 年轻男性，沉稳 |
| zh-CN-XiaoxiaoNeural | 年轻女性，活泼 |
| zh-CN-YunjianNeural | 成熟男性，有力 |

## video-dsl子系统

声明式视频生成子系统，路径 `video-dsl/`，流程为 `VideoProgram.tsx → 渲染 → MP4`。包含三个包：`video-core`（核心组件 + composition/sequence/interpolate 基础能力）、`video-generator`（generator/prompt/validator）、`video-renderer`（cli/renderer/env）。

## 生成流程

```
1. HTML 文件加载（或先走 HTML 管线生成）
2. Playwright 滚动录制（按 section 停留）
3. Edge TTS 生成旁白 MP3
4. FFmpeg 合并视频 + 音频
5. （可选）混音 BGM（带 ducking）
6. 输出 MP4
```

## 失败模式

| 现象 | 处理 |
|------|------|
| Playwright 启动失败 | 检查浏览器安装 |
| TTS 失败 | 检查 `edge-tts` 安装与网络 |
| FFmpeg 失败 | 检查 `ffmpeg` 安装 |
| 视频 > 50MB | 压缩或分段 |
| 滚动卡顿 | 调整 `scroll_speed` |
| section 遗漏 | 检查 section 检测逻辑 |

## 与其他管线的关系

- **HTML管线**：提供视觉源（HTML 即视频画面）
- **音频管线**：共享 TTS 能力（`video-dsl/scripts/generate_audio.py`）
- **脚本来源**：旁白文本由上层工作流提供

## 脚本与命令

- 脚本：[scripts/pipeline.py](scripts/pipeline.py)（统一入口）、[scripts/dsl_video_pipeline.py](scripts/dsl_video_pipeline.py)、[scripts/html_to_video.py](scripts/html_to_video.py)、[scripts/router.py](scripts/router.py)
- 命令：

```bash
python -m scripts.cli video input.html --output output/video/ --narration "旁白文本"
python -m scripts.cli video input.html --output output/video/ --narration-file narration.txt
python -m scripts.cli video input.html --output output/video/ --bgm bgm.mp3
```

- references：[references.video-pipeline.md](references.video-pipeline.md)

## 质量自检

| 检查项 | 标准 |
|--------|------|
| 文件大小 | ≤ 50MB |
| 画面清晰 | 1080p（device_scale_factor=2） |
| 旁白完整 | 每个 section 有旁白 |
| 滚动流畅 | 无卡顿 |
| 内容完整 | HTML 所有 section 都被录制 |

---

*视频管线 · HTML → MP4 · HTML直接录制+TTS旁白+FFmpeg合并*
