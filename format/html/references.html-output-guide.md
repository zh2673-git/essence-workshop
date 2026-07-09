# HTML交互输出规范（HTML Output Guide）

> HTML作为六维信息容器：内容、结构、布局、样式、交互、保真

---

## 核心原则

HTML是唯一能同时承载六个信息维度的格式：

| 维度 | 说明 | HTML实现 |
|------|------|---------|
| 内容 | 文本、图片、视频 | 语义化标签 |
| 结构 | 章节层次、导航 | `<section>`, `<nav>` |
| 布局 | 响应式排版 | CSS Grid, Flexbox |
| 样式 | 品牌色、字体、间距 | CSS变量 |
| 交互 | 点击、拖拽、翻转 | JS事件 |
| 保真 | 动画、过渡、音视频 | SVG SMIL, CSS animation, `<video>` |

## 单文件原则

⚠️ HTML交互管线输出为**单文件HTML**，所有资源内联：
- CSS → `<style>` 内联
- JS → `<script>` 内联
- SVG → `<svg>` 内联
- 图片 → Data URI 或 内联SVG
- 字体 → 系统字体（不内联外部字体）

## 响应式设计

HTML 需支持响应式布局与打印样式。具体断点值由上层工作流/平台适配指定，形式层不强制固定断点。

### 打印样式

```css
@media print {
  nav, .interactive-module { display: none; }
  section { page-break-inside: avoid; }
}
```

## CSS变量

HTML 通过 CSS 变量承载视觉样式（`--primary`、`--bg`、`--text` 等），由上层通过 `--brand-spec` 注入。形式层不规定具体配色、字体或尺寸取值，只规定"变量可被上层覆写"这一契约。配色方案、学科配色等样式决策归属工作流层。

## 交互模块接入规范

每个标准模块遵循统一接口：

```html
<div class="module module-{name}" data-module="{name}">
  <!-- 模块内容 -->
</div>
<script>
  // 模块初始化
  if (typeof {name}Init === 'function') {
    {name}Init(document.querySelector('[data-module="{name}"]'));
  }
</script>
```

## 可访问性

- ⚠️ 所有图片必须有 `alt` 属性
- ⚠️ 交互元素必须有键盘支持
- ⚠️ 颜色对比度 ≥ 4.5:1
- ⚠️ 使用语义化标签
