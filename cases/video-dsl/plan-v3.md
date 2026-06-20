# 方案 v3

## 目标

实现 Phase 2：TTS 旁白自动生成、BGM 混合、MP4 音画合成；`video-renderer` CLI 支持 `--audio` / `--bgm`；Python DSL 管线自动根据 `spec.json` 生成音频。

## 关键改动

1. 新增 `scripts/generate_audio.py`：使用 edge-tts 按 section.narration 生成 TTS，拼接并 pad 到总时长，可选 BGM 混合。
2. `video-renderer` 的 `RenderOptions` / CLI 增加 `audioPath`、`bgmPath`。
3. FFmpeg 编码阶段根据音频存在与否选择是否合并音轨。
4. `dsl_video_pipeline.py` 自动检测同目录 `spec.json` 并调用 `generate_audio.py`。

## 验证契约

- 生成的 `audio.m4a` 时长 ≈ `spec.durationSeconds`。
- `final.mp4` 包含音频流（Stream #0:1 Audio: aac）。
- 通过 CLI 直接指定 `--audio` 也能合成。

## 不可验证项

- 音画同步精度（无人耳校验），以时长一致和流存在替代验证。
