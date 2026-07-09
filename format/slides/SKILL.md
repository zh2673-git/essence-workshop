---
name: Slides管线
description: |
  Reveal.js幻灯片格式管线：将认知产物转为Reveal.js单文件演示HTML。
  产出依赖CDN加载Reveal.js的演示页，支持SVG嵌入、CSS动画、演讲者备注、PDF导出。
  输入：认知产物（文本+图形元素）。输出：Reveal.js演示HTML。
  触发词：「做演示」「做slides」「Reveal演示」。
version: 1.0
layer: format
pipeline: slides
---

# Slides管线

> 将认知产物转为 Reveal.js 单文件演示 HTML。本管线只负责"结构正确的 Reveal.js 演示页"，视觉风格、页数、图文比例等由上层工作流指定。

## 输入输出

- **输入**：元素层中的文本元素与图形元素（SVG 直接嵌入保留矢量）
- **输出**：单文件 `index.html`（依赖 CDN 加载 Reveal.js@5），可通过 `?print-pdf` 导出 PDF

## 幻灯片结构映射

| Markdown | Reveal.js | 说明 |
|----------|-----------|------|
| H1 | `<section>` 封面 | 标题+副标题 |
| H2 | `<section>` 分隔 | 章节标题 |
| H3 | `<section>` 内容 | 正文内容 |
| 段落 | `<p>` | 幻灯片正文 |
| 列表 | `<ul>/<ol>` | 要点列表 |
| 代码块 | `<pre><code>` | 代码高亮 |
| 图片 | `<img>` 或 `<svg>` | 配图 |

## 技术约束

- **框架**：Reveal.js@5（CDN 加载）
- **SVG**：直接嵌入，必须含 `viewBox` 和 `xmlns`
- **演讲者备注**：`<aside class="notes">`
- **字体**：系统字体，不依赖外部字体

> 幻灯片页数、图文比例、主题配色等由上层工作流/平台适配指定，形式层只保证 Reveal.js 结构正确可演示。

## 与其他管线的关系

- **HTML管线**：slides 是 HTML 的演示结构变体（section 化、非滚动）
- **PPT管线**：同为演示形式，但 slides 产出 HTML（Git/AI 友好），PPT 产出 .pptx（企业模板友好）

## 脚本与references

- 脚本：[scripts/generator.py](scripts/generator.py)
- references：[references.slides-pipeline.md](references.slides-pipeline.md)

---

*Slides管线 · 文本+SVG元素 → Reveal.js演示HTML · 结构正确·风格交由工作流*
