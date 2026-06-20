# 方案 v4

## 目标

完善 Pipeline Router 与 content-output CLI 的集成：统一入口支持 `--pipeline dsl`，保留 HTML 录制与公众号文章管线；CLI 文档体现 DSL 用法。

## 关键改动

1. 创建 `content-output/scripts/pipelines/video/pipeline.py` 作为统一视频入口。
2. 更新 `content-output/scripts/cli.py` 的 docstring 与 video 管线描述。
3. `dsl_video_pipeline.py` 与 `pipeline.py` 透传 `--format`、`--quality`、`--bgm`。

## 验证契约

- `python -m scripts.cli video VideoProgram.tsx --pipeline dsl --output ...` 成功生成含音频的 MP4。
- Router 分支测试仍然通过。
