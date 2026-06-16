---
name: 内容输出
description: 多管线发布系统，将内容按风格改写后输出到目标平台
version: 2.0
scene: E
---

# 内容输出 · Skill

## 核心方法

风格改写 → 元素层资产生成 → 管线输出，支持6条管线（公众号/视频号/HTML交互/演示/PPT/Notebook）。

## 触发条件

- 「写公众号」「做视频」「HTML交互」「做演示」「做PPT」
- 「做notebook」「生成教学notebook」「教学课件」
- 其他场景产出后选择输出

## 执行流程

详见 [E-content-output.md](E-content-output.md)

## 参考文档

### 管线规范
- [references/pipeline-wechat.md](references/pipeline-wechat.md) — 公众号管线
- [references/pipeline-video.md](references/pipeline-video.md) — 视频号管线
- [references/pipeline-html.md](references/pipeline-html.md) — HTML交互管线
- [references/pipeline-slides.md](references/pipeline-slides.md) — 演示管线
- [references/pipeline-pptx.md](references/pipeline-pptx.md) — PPT管线
- [references/pipeline-notebook.md](references/pipeline-notebook.md) — Notebook管线

### 通用规范
- [references/html-output-guide.md](references/html-output-guide.md) — HTML输出规范
- [references/wechat-formatting.md](references/wechat-formatting.md) — 公众号排版
- [references/writing-style-guide.md](references/writing-style-guide.md) — 写作风格
- [references/topic-selection.md](references/topic-selection.md) — 选题诊断
- [references/element-spec.md](references/element-spec.md) — 元素层规格

## 模板

- [templates/reveal-template.html](templates/reveal-template.html) — 演示管线模板
- [templates/brand-spec.json](templates/brand-spec.json) — 品牌规格
- [templates/notebook-template.ipynb](templates/notebook-template.ipynb) — Notebook管线模板

## 脚本

- `scripts/pipelines/` — 各管线脚本（html/pptx/slides/video/wechat/notebook）
- `scripts/elements/` — 元素层脚本（brand_extractor/record_gif/svg_to_png）
- `scripts/shared/` — 跨管线共享（article_fetcher/article_to_video）
- `scripts/cli.py` — 命令行入口

## 输出风格

| 风格 | 说明 |
|------|------|
| 论文风格 | 学术论文式严谨输出 |
| 对话风格 | 通俗易懂的对话体 |
| 蒸馏Skill风格 | 激活distillation/output/中对应人物Skill，以其视角输出 |
