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

### 断点

```css
@media (max-width: 768px) { /* 移动端 */ }
@media (min-width: 769px) and (max-width: 1024px) { /* 平板 */ }
@media (min-width: 1025px) { /* 桌面端 */ }
```

### 打印样式

```css
@media print {
  nav, .interactive-module { display: none; }
  section { page-break-inside: avoid; }
}
```

## CSS变量规范

```css
:root {
  --primary: #2563eb;
  --primary-light: #60a5fa;
  --secondary: #7c3aed;
  --bg: #ffffff;
  --bg-alt: #f3f4f6;
  --text: #1f2937;
  --text-light: #6b7280;
  --border: #e5e7eb;
  --radius: 8px;
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: "SF Mono", "Fira Code", monospace;
}
```

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
