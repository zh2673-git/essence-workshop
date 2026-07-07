---
name: 内容输出
description: 多管线发布系统，将内容按风格改写后输出到目标平台，支持7种输出风格与连载小说子系统。基于 v2 方法论：三阶合一（阶段1是什么·点出本质·本质定义先行 → 阶段2为什么·建立因果·含反常识根因 → 阶段3怎么做·展开方法·视角升级）+ 顿悟触发机制（一句话点破+反常识根因+视角升级）+ 类-属性-方法-路由（由本质定义锚定）。
version: 2.2
scene: E
---

# 内容输出 · Skill

## 核心方法

**本质定义先行** → 风格改写（按三阶段主线展开+植入顿悟触发器）→ 元素层资产生成 → 管线输出，支持7条管线（公众号/视频号/口播稿/HTML交互/演示/PPT/Notebook）。

### v2 方法论约束（硬性）

- **本质定义先行**：所有风格改写、配图规划、镜头拆分必须先确定内容的本质定义，并通过本质检验（能解释所有其他属性）
- **三阶合一**：阶段1（是什么·点出本质）→ 阶段2（为什么·建立因果）→ 阶段3（怎么做·展开方法·视角升级），三阶与坡度三阶段一一对应，不再正交为9宫格
- **顿悟触发器三件套**（缺一不可）：阶段1一句话点破 + 阶段2反常识根因 + 阶段3视角升级
- **类-属性-方法-路由由本质定义锚定**：本质定义 → 内容类归属 → 属性展开 → 风格+结构方法 → 管线路由适配，每一层必须能回溯到本质定义

## 触发条件

- 「写公众号」「做视频」「HTML交互」「做演示」「做PPT」
- 「做notebook」「生成教学notebook」「教学课件」
- 「写口播稿」「写录制稿」「口播脚本」「录制脚本」「真人出镜稿」→ 口播稿管线
- 「写连载小说」「小说连载」「连载XX」→ 连载小说子系统
- 其他场景产出后选择输出

## 执行流程

详见 [E-content-output.md](E-content-output.md)

## 参考文档

### 管线规范
- [references/pipeline-wechat.md](references/pipeline-wechat.md) — 公众号管线
- [references/pipeline-video.md](references/pipeline-video.md) — 视频号管线
- [references/pipeline-broadcast.md](references/pipeline-broadcast.md) — 口播稿管线
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

### 连载小说子系统
- [serial-fiction/SKILL.md](serial-fiction/SKILL.md) — 连载小说子系统说明
- [serial-fiction/SF-serial-fiction.md](serial-fiction/SF-serial-fiction.md) — 连载小说工作流
- [serial-fiction/references/fiction-style-guide.md](serial-fiction/references/fiction-style-guide.md) — 小说风格规范
- [serial-fiction/references/world-building-guide.md](serial-fiction/references/world-building-guide.md) — 世界观构建方法
- [serial-fiction/references/character-card-template.md](serial-fiction/references/character-card-template.md) — 人物卡模板
- [serial-fiction/references/chapter-outline-template.md](serial-fiction/references/chapter-outline-template.md) — 分章大纲模板
- [serial-fiction/references/series-state-spec.md](serial-fiction/references/series-state-spec.md) — 连载状态规范

## 模板

- [templates/reveal-template.html](templates/reveal-template.html) — 演示管线模板
- [templates/brand-spec.json](templates/brand-spec.json) — 品牌规格
- [templates/notebook-template.ipynb](templates/notebook-template.ipynb) — Notebook管线模板
- [templates/broadcast-script-template.md](templates/broadcast-script-template.md) — 口播稿模板

## 脚本

- `scripts/pipelines/` — 各形式生成器（html/pptx/slides/video/notebook/markdown）
- `scripts/pipelines/platforms/` — 统一平台适配器（browser/wechat/office/jupyter/reveal/obsidian/video-channel/bilibili/douyin）
- `scripts/pipelines/dispatcher.py` — 形式-平台统一调度器
- `scripts/elements/` — 元素层脚本（brand_extractor/record_gif/svg_to_png）
- `scripts/shared/` — 跨管线共享（article_fetcher/article_to_video）
- `scripts/cli.py` — 命令行入口

## 输出风格

| 风格 | 说明 | 默认篇幅 |
|------|------|---------|
| 论文风格 | 学术论文式严谨输出 | 7000-8000字 |
| 专栏风格 | 论文的轻量版，观点+案例 | 3000-5000字 |
| 故事风格 | 用叙事包装知识/案例 | 2500-4500字 |
| 教程/清单风格 | 步骤清晰，直接可用 | 1500-3000字 |
| 观点/时评风格 | 立场鲜明，短小犀利 | 1200-2500字 |
| 对话风格 | 通俗易懂的对话体 | 不定 |
| 蒸馏Skill风格 | 激活distillation/output/中对应人物Skill，以其视角输出 | 不定 |

> 连载小说作为独立子系统，单章篇幅 2000-4000字，详见 [serial-fiction/SKILL.md](serial-fiction/SKILL.md)。

## 实战案例

- [cases/wechat-zh2673.md](../cases/wechat-zh2673.md) — 公众号zh2673自动化运营（场景E+B2，一个月内出现爆款，集中带来用户增长）
- [cases/video-dsl-ratchet.md](../cases/video-dsl-ratchet.md) — Video DSL 从零到完整视频管线（场景C2+E，6轮 Ratchet Loop，含形式vs平台重构实现）
- [cases/video-dsl/](../cases/video-dsl/) — Video DSL 迭代计划、测试报告、验收文档归档

## 架构演进

- [docs/form-vs-platform.md](docs/form-vs-platform.md) — 内容输出层重构：将管线拆分为“形式层”与“平台适配层”。视频管线与非视频形式已统一调度（`--form video/html/slides/pptx/notebook --platform ...`），平台适配器全部合并到 `scripts/pipelines/platforms/`。
