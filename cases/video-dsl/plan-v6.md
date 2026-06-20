# 方案 v6

## 目标

实现 GIF 输出与渲染质量预设（draft/medium/high），满足短视频多平台分发需求。

## 关键改动

1. `RenderOptions` 增加 `format?: 'mp4' | 'gif'` 和 `quality?: 'draft' | 'medium' | 'high'`。
2. `video-renderer` 根据 format 选择 FFmpeg 编码路径：MP4 用 x264 + quality preset/CRF；GIF 用 palettegen + paletteuse。
3. CLI 与 Python 管线透传 `--format` / `--quality`。

## 验证契约

- `--format gif` 输出非空 `final.gif`。
- `--quality draft` 比 `--quality high` 渲染更快、文件更小（趋势验证）。
