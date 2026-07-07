---
name: 白板录制
description: 无限画布白板讲解录制系统，AI自动根据内容生成Excalidraw手绘白板图解和提词器脚本，支持镜头自动跟随、人像叠加、一键录制
version: 1.0
scene: E3
---

# 白板录制 · Skill

## 核心方法

内容输入（Markdown/URL/纯文本）→ AI深度理解→ 无限画布Excalidraw图解自动生成 → 提词器脚本自动生成 → 镜头自动跟随 → 带人像叠加录制。

## 触发条件

- 「白板录制」「录白板」「白板讲解」「做白板视频」
- 「白板演示」「录制讲解视频」「录课白板」
- 「自动生成白板」「AI画白板」

## 执行流程

1. **内容获取**：读取本地Markdown文件 / 抓取公众号文章URL / 接收纯文本输入 / 读取 content-output 生成的 `broadcast-script.md`
2. **AI生成**：调用LLM深度理解内容，在无限画布上自由排布手绘图解，自动分页，生成讲解节奏（口播稿输入时按已有镜头拆分，旁白直接作为提词器）
3. **镜头规划**：AI给出每个讲解点对应的视口中心坐标，实现镜头平滑跟随
4. **提词生成**：同步生成口语化提词器脚本，与镜头移动同步
5. **前端加载**：导入到WhiteboardCaster录制工具，即可直接开始录制
6. **录制导出**：支持摄像头人像叠加、光标特效、一键导出MP4

## 无限画布模式

- 所有内容在同一个无限大Excalidraw画布上，按讲解顺序排列
- 讲解时镜头自动平滑移动到当前内容区域
- 可以手动拖动白板自由浏览，随时回看
- 支持跨区域画关联箭头，展示内容逻辑联系

## 参考文档

- [references/excalidraw-element-spec.md](references/excalidraw-element-spec.md) — Excalidraw元素规格说明
- [references/ai-prompt-guide.md](references/ai-prompt-guide.md) — AI生成Prompt设计指南

## 脚本

- `scripts/whiteboard_generator.py` — AI白板内容生成器，输入文本/URL，输出无限画布JSON+提词脚本
- `scripts/broadcast_to_whiteboard.py` — 口播稿→白板桥接器，输入 content-output 生成的 `broadcast-script.md`，按镜头生成白板画面+提词器
- `scripts/` 复用 `../content-output/scripts/shared/article_fetcher.py` 做内容抓取

## 前端工具

WhiteboardCaster录制界面位于本项目webapp目录，支持：
- Excalidraw无限画布手绘
- 场景导航+镜头自动跟随
- 提词器面板
- 摄像头人像叠加/拖拽/大小调整
- 光标特效
- 录制预览/导出
