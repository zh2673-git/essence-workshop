---
name: 形式层
description: |
  形式表达层：将内容框架层产出的结构化内容，转换为特定格式的表达产物。
  本层是本质工坊四层架构的第3层——"形式"层，回答"用什么格式表达"。
  每条形式管线相互独立、自包含，只保证格式正确可运行，不规定视觉样式。
  视觉样式、篇幅、版式等由工作流层指定。格式产物不绑定平台，可被工作流层适配到具体平台。
  触发词：当场景需要格式化输出时自动调用；也可由用户指定格式（如「做PPT」「HTML交互」「做notebook」）。
version: 4.1
layer: format
---

# 形式层 · 格式表达路由

> **v4.1 形式层**：本层是本质工坊四层架构的第3层——把结构化内容转为格式产物。
> 形式层 = 四层架构的"形式"层（认知×框架×形式×工作流），回答"用什么格式表达"。

---

## 设计原则

- **每条形式独立自包含**：各形式有自己的 SKILL.md / 脚本 / references，无共享层、无共享脚本。
- **只保证格式正确**：形式层的准则是"不会错"——产出格式合法、结构正确、可被下游打开/运行。
- **不规定视觉样式**：配色、字体、断点、篇幅、页数、时长等样式决策由工作流层指定（通过 `--brand-spec` 等参数注入），形式层不限制。
- **不绑定平台**：格式产物是通用格式文件，平台适配（尺寸/标签/链接/受限规则）由工作流层处理。

---

## 架构

```
形式层（用什么格式表达，每条形式独立自包含）
├── markdown/          # Markdown 文档（最通用，跨平台）
├── html/              # HTML 交互文档（富交互，六维信息容器）
├── slides/            # Reveal.js 幻灯片（演示HTML）
├── notebook/          # Jupyter Notebook（教学+可执行）
├── ppt/               # PPT 演示（.pptx）
├── video/             # 视频（MP4，含 video-dsl）
├── audio/             # 音频（MP3，TTS 朗读/播客）
├── whiteboard/        # 白板场景JSON（Excalidraw兼容）
└── skill/             # Skill 文档（蒸馏产物组装）
```

---

## 9 条形式管线

| 管线 | 格式 | 路径 | 说明 |
|------|------|------|------|
| Markdown | .md | [markdown/](markdown/) | 最通用跨平台文本来源 |
| HTML 交互 | .html | [html/](html/) | 六维信息容器，能力最完整 |
| Slides | .html (Reveal.js) | [slides/](slides/) | 演示结构，SVG嵌入+PDF导出 |
| Notebook | .ipynb | [notebook/](notebook/) | 教学式，可执行 |
| PPT | .pptx | [ppt/](ppt/) | 富媒体降级为PNG，企业模板友好 |
| 视频 | .mp4 | [video/](video/) | HTML录制+TTS旁白+FFmpeg，含video-dsl |
| 音频 | .mp3 | [audio/](audio/) | TTS语音+可选BGM |
| 白板 | .whiteboard.json | [whiteboard/](whiteboard/) | Excalidraw兼容场景JSON |
| Skill | SKILL.md | [skill/](skill/) | 蒸馏数据按模板组装 |

---

## 输入输出契约

- **输入**：结构化内容（来自 `content-framework/` 内容框架层）
- **输出**：通用格式产物（供 `workflow/` 工作流层做平台适配）

格式产物是**未适配平台的通用格式文件**：.md / .html / .ipynb / .pptx / .mp4 / .mp3 / .whiteboard.json / SKILL.md。

---

## 管线选择规则

### 由内容框架指定
内容框架层会指定使用哪条管线（如 K12拆解→HTML、项目开发→Markdown、连载小说→Markdown）。

### 由用户指定
用户可直接指定：「做PPT」「HTML交互」「做notebook」「做视频」。

### 管线切换
同一结构化内容可走不同管线，无需重新组织内容。

---

## 与其他层的关系

- **上游**：`content-framework/`（内容框架层产出结构化内容）
- **下游**：`workflow/`（工作流层将格式产物适配到具体平台，并注入视觉样式/篇幅/版式等）
- **调用方**：`workflow/`（工作流层编排 认知×框架×形式×平台）

---

## 扩展新形式

在 `format/` 下创建新子目录，包含独立的 `SKILL.md`（管线规范，只含格式正确性约束）和可选的 `scripts/`、`references/`，实现"结构化内容 → 格式产物"的转换即可。新形式不规定视觉样式，不依赖共享层。

---

*形式层 · v4.1 · 结构化内容 → 格式产物 · 9条独立形式 · 只保证格式正确·样式交由工作流*
