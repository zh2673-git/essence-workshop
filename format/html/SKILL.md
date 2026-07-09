---
name: HTML交互管线
description: |
  HTML交互格式管线：将认知产物转为单文件HTML交互文档。
  HTML是六维信息容器（内容/结构/布局/样式/交互/保真），支持scroll连续滚动和paged分页课件两种模式。
  能力最完整的管线，其他管线均为其降级版本。
  输入：认知产物（文本+图形+动画元素）。输出：单文件.html。
  触发词：「做HTML」「HTML交互」「交互课件」。
version: 1.0
layer: format
pipeline: html
---

# HTML交互管线

> 将认知产物转为单文件 HTML 交互文档。HTML 是唯一能同时承载六个信息维度的格式，因此本管线为能力最完整的管线，其他管线均为其降级版本。

## 输入输出

- **输入**：元素层中的文本/图形/动画/音频/交互元素
- **输出**：单文件 `index.html`（所有资源内联：CSS / JS / SVG / Data URI）

## 两种模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `scroll` | 连续滚动（v1） | 长文阅读、知识探索 |
| `paged` | 分页课件（v2，TeachAny风格） | 课件演示、教学场景 |

## 六维信息容器

| 维度 | 对应元素 | HTML实现 |
|------|---------|---------|
| 内容 | 文本元素 | `<p>`, `<h1>`-`<h6>`, `<ul>`, `<table>` |
| 结构 | 数据元素 | `<section>`, `<article>`, `<nav>` |
| 布局 | 数据元素 | CSS Grid, Flexbox |
| 样式 | 图形元素 | CSS变量, `<svg>` |
| 交互 | 交互元素 | JS事件, DOM操作 |
| 保真 | 动画元素 | `<svg>` SMIL, CSS animation, `<canvas>` |

## 单文件原则

所有资源内联：CSS → `<style>`、JS → `<script>`、SVG → `<svg>`、图片 → Data URI、字体 → 系统字体（不内联外部字体）。

## 配色与样式

配色、字体、布局等视觉样式**由上层（工作流/平台适配）通过 `--brand-spec` 指定**，形式层不规定具体配色方案、断点尺寸或视觉风格。未指定时生成器使用可运行的占位默认值（可被任意覆盖）。具体样式规范见各工作流层。

## 生成流程

```
1. 从 output/elements/ 读取元素
2. 加载模板（scroll / paged）
3. 文本元素 → HTML 结构（语义化标签）
4. SVG / Canvas / 交互模块 → 直接嵌入（无降级）
5. 音频元素 → <audio> 嵌入
6. CSS 变量 → 品牌色覆写（--primary 等）
7. 响应式检查（含打印样式）
8. 输出单文件 HTML
```

## 技术约束

- **文件大小**：单文件 ≤ 5MB
- **字体**：系统字体，不依赖外部字体
- **可访问性**：所有图片有 `alt`、交互可键盘操作、语义化标签
- **响应式**：需支持响应式布局与打印样式（`@media print`），具体断点由上层指定
- **交互原则**：交互必须服务于认知目标，不为交互而交互

## 失败模式

| 现象 | 处理 |
|------|------|
| SVG 渲染失败 | 检查 `viewBox` 和 `xmlns` |
| 文件 > 5MB | 拆分页面或压缩 SVG |
| 交互不响应 | 测试点击 / 拖拽 / 翻转事件绑定 |
| 移动端错位 | 检查断点布局 |
| 打印样式异常 | 检查 `@media print` |

## 与其他管线的关系

- **定位**：能力最完整管线，其他管线是它的降级版本
- **公众号适配器** = HTML − JS交互 − SVG直嵌（平台层做受限适配）
- **视频适配器** = HTML − 交互 + 录制交付（平台层做录制适配）
- **PPT管线** = HTML − 交互 − SVG − 动画
- **演示适配器** = HTML − 交互 + 幻灯片结构

## 脚本与模板

- 脚本：[scripts/generator.py](scripts/generator.py)（支持 `--mode scroll/paged`、`--brand-spec`）
- 模板：[templates/reveal-template.html](templates/reveal-template.html)、[templates/brand-spec.json](templates/brand-spec.json)
- references：
  - [references.html-output-guide.md](references.html-output-guide.md)（输出规范）
  - [references.html-pipeline.md](references.html-pipeline.md)（管线规范）

## 质量自检

| 检查项 | 标准 |
|--------|------|
| SVG渲染 | 所有SVG正确显示 |
| 交互功能 | 所有模块可交互 |
| 响应式 | 移动端正常显示 |
| 文件大小 | ≤5MB |
| 打印 | 打印样式正常 |

---

*HTML交互管线 · 认知产物 → 单文件.html · 六维信息容器·能力最完整*
