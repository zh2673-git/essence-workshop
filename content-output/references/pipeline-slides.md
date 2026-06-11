# 演示管线规范（Slides Pipeline）

> 从元素层读取 → Reveal.js 幻灯片 → 浏览器演示

---

## 管线概览

```
元素层读取 → 幻灯片结构生成 → 图形嵌入 → Reveal.js模板 → 演示HTML
```

## 元素消费与转换

| 元素类型 | 转换规则 | 说明 |
|---------|---------|------|
| 文本元素 | Markdown → 幻灯片 section | H1→封面，H2→分隔，H3→内容 |
| SVG图形 | `<svg>` 直接嵌入幻灯片 | 保留矢量清晰度 |
| SVG动画 | SMIL/CSS动画嵌入 | 自动播放 |
| Canvas动画 | `<canvas>` + JS 嵌入 | 完整动画 |
| 音频元素 | 不消费 | — |
| 交互元素 | 不消费 | — |
| 数据元素 | JSON 驱动幻灯片顺序 | — |

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

## Reveal.js 模板

模板路径：`templates/reveal-template.html`

### 模板特性

- 演讲者备注支持（`<aside class="notes">`）
- PDF导出支持（`?print-pdf`）
- 代码高亮（highlight.js）
- 响应式布局
- 键盘/触摸导航
- 幻灯片编号

### 模板结构

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>演示标题</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/theme/white.css">
</head>
<body>
  <div class="reveal">
    <div class="slides">
      <!-- 幻灯片内容 -->
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5/dist/reveal.js"></script>
  <script>Reveal.initialize({});</script>
</body>
</html>
```

## 执行步骤

1. 从 `output/elements/` 读取元素
2. 文本元素 → 按 H1/H2/H3 拆分为 section
3. SVG图形 → 嵌入对应 section
4. SVG动画 → 嵌入对应 section
5. 加载 Reveal.js 模板
6. 注入幻灯片内容
7. 输出

## 输出

- 路径：`output/slides/index.html`
- 格式：HTML（依赖CDN加载Reveal.js）
- 可通过 `?print-pdf` 导出PDF

## 与PPT管线对比

| 维度 | 演示管线（Reveal.js） | PPT管线（.pptx） |
|------|---------------------|-----------------|
| 交互能力 | CSS/SVG动画 | 无 |
| 格式 | HTML | .pptx |
| 版本管理 | Git友好 | Git不友好 |
| AI生成 | 原生友好 | 需要库辅助 |
| 离线使用 | 需要浏览器 | 直接打开 |
| 企业模板 | 不支持 | 支持 |
| PDF导出 | ✅ | ✅ |

**推荐**：优先使用演示管线，仅在需要 .pptx 时使用 PPT管线。

## 质量自检

| 检查项 | 标准 | 异常处理 |
|--------|------|---------|
| 幻灯片数量 | 10-30页 | 过少则合并，过多则拆分 |
| 图文比例 | 每页≤50%纯文字 | 文字过多则拆分或加图 |
| 动画流畅 | 过渡效果正常 | 检查CSS动画兼容性 |
| SVG渲染 | 所有SVG正确显示 | 检查viewBox和xmlns |
| 导航 | 键盘/触摸正常 | 测试方向键 |
