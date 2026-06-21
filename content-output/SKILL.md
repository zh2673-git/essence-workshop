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

- `scripts/pipelines/` — 各形式生成器（html/pptx/slides/video/notebook/markdown）
- `scripts/pipelines/platforms/` — 统一平台适配器（browser/wechat/office/jupyter/reveal/obsidian/video-channel/bilibili/douyin）
- `scripts/pipelines/dispatcher.py` — 形式-平台统一调度器
- `scripts/elements/` — 元素层脚本（brand_extractor/record_gif/svg_to_png）
- `scripts/shared/` — 跨管线共享（article_fetcher/article_to_video）
- `scripts/cli.py` — 命令行入口

## 输出风格

| 风格 | 说明 |
|------|------|
| 论文风格 | 学术论文式严谨输出 |
| 对话风格 | 通俗易懂的对话体 |
| 蒸馏Skill风格 | 激活distillation/output/中对应人物Skill，以其视角输出 |

## 实战案例

- [cases/wechat-zh2673.md](../cases/wechat-zh2673.md) — 公众号zh2673自动化运营（场景E+B2，一个月内出现爆款，集中带来用户增长）
- [cases/video-dsl-ratchet.md](../cases/video-dsl-ratchet.md) — Video DSL 从零到完整视频管线（场景C2+E，6轮 Ratchet Loop，含形式vs平台重构实现）
- [cases/video-dsl/](../cases/video-dsl/) — Video DSL 迭代计划、测试报告、验收文档归档

## 架构演进

- [docs/form-vs-platform.md](docs/form-vs-platform.md) — 内容输出层重构：将管线拆分为“形式层”与“平台适配层”。视频管线与非视频形式已统一调度（`--form video/html/slides/pptx/notebook --platform ...`），平台适配器全部合并到 `scripts/pipelines/platforms/`。
