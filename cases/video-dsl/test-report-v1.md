# 测试报告 v1

## 1. 迭代历程总览

| 版本 | 关键发现 | 核心改进 | P | Q | I |
|------|---------|---------|---|---|---|
| v1 | 初始实现 video-core / video-renderer / video-generator / router / dsl_video_pipeline | 完成 Phase 1 MVP 闭环 | ✅ | ✅ | ✅ |

## 2. 三维验证结果

| 维度 | 检查项 | 结果 | 说明 |
|------|-------|------|------|
| P 前置 | Node.js 18+ | ✅ | v22.16.0 |
| P 前置 | Playwright + Chrome | ✅ | 系统 Chrome fallback |
| P 前置 | FFmpeg（imageio-ffmpeg） | ✅ | D:\\anaconda3\\...\\ffmpeg-win-x86_64-v7.1.exe |
| P 前置 | TypeScript 编译器 | ✅ | tsc 5.6.3 |
| Q 后置 | video-core 类型通过 | ✅ | `npm run typecheck` |
| Q 后置 | video-renderer 渲染 Demo | ✅ | 输出 `final.mp4`，270 帧/9 秒，2160×3840（scale=2） |
| Q 后置 | video-generator 校验拦截非法代码 | ✅ | pytest 11/11 通过 |
| Q 后置 | Python router 决策正确 | ✅ | 6 个分支测试通过 |
| I 不变量 | 现有 html_to_video 可导入 | ✅ | `find_ffmpeg()` 正常 |
| I 不变量 | 现有 article_to_video 可导入 | ✅ | `detect_visual_style` 正常 |
| I 不变量 | 用户源码不被修改 | ✅ | 渲染只写 output 目录，源码目录只读 |

## 3. Ratchet 决策

| 改动 | P | Q | I | 决策 | 原因 |
|------|---|---|---|------|------|
| video-core 实现 | ✅ | ✅ | ✅ | 保留 | 类型检查通过，API 符合设计 |
| video-renderer 实现 | ✅ | ✅ | ✅ | 保留 | 可渲染出有效 MP4 |
| video-generator 实现 | ✅ | ✅ | ✅ | 保留 | 校验器能拦截非法代码 |
| Python router / dsl_video_pipeline | ✅ | ✅ | ✅ | 保留 | 与 CLI 集成成功 |

## 4. 关键突破

1. **无 Playwright 浏览器二进制时的 fallback**：环境未下载 Chromium，通过 `chromium.launch({ channel: 'chrome' })` 使用系统 Chrome 完成渲染。
2. **工作区依赖解析**：npm workspaces 未将 `react` 提升到根 `node_modules`，通过 alias 指向 `packages/video-core/node_modules` 解决 Vite 打包。
3. **durationInFrames 解析**：从文件所有 `durationInFrames` 匹配中取最大值，避免 Sequence 的短 duration 覆盖 Composition 的总时长。

## 5. 待解决问题（下轮方向）

| 问题 | 严重度 | 可能方案 |
|------|--------|---------|
| 视频输出分辨率被 deviceScaleFactor=2 放大到 2160×3840 | 低 | 明确 scale 语义，或默认 scale=1；需要时提供 `--scale` |
| 未实现 TTS/BGM 集成 | 中 | Phase 2 接入 edge-tts 与 FFmpeg 音频合并 |
| 未实现 GIF 输出 | 低 | Phase 3 增加 `--format gif` |
| Playwright Chromium 下载慢/失败 | 中 | 文档提示优先使用系统 Chrome，或增加 `--chrome-channel` |
| 缺少常用动画组件库 | 低 | Phase 3 沉淀 FadeIn、FlyIn 等组件 |

## 6. 实验记录

| experiment_id | timestamp | change_description | pre | post | inv | kept |
|---|---|---|---|---|---|---|
| 001 | 2026-06-20 | 初始化 video-core 包 | ✅ | ✅ | ✅ | true |
| 002 | 2026-06-20 | 实现 video-renderer 本地渲染 | ✅ | ✅ | ✅ | true |
| 003 | 2026-06-20 | 修复 ffmpeg 查找与 Chrome fallback | ✅ | ✅ | ✅ | true |
| 004 | 2026-06-20 | 修复 durationInFrames 解析 | ✅ | ✅ | ✅ | true |
| 005 | 2026-06-20 | 实现 video-generator 校验与 Python router | ✅ | ✅ | ✅ | true |
