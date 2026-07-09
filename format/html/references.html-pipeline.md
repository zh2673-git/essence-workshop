# HTML交互管线规范（HTML Interactive Pipeline）

> 从元素层读取 → 直接嵌入（无降级）→ 完整交互HTML

---

## 管线概览

```
元素层读取 → 课程骨架模板 → 元素直接嵌入 → 交互模块接入 → 样式响应式 → 完整HTML
```

## 管线定位

HTML交互管线是**能力最完整的管线**：
- SVG 直接嵌入，保留交互能力
- 动画直接嵌入，保留完整效果
- 交互模块直接接入，保留全部交互
- 音频可嵌入，保留播放控制

其他管线都是 HTML交互管线的**降级版本**：
- 公众号管线 = HTML交互管线 - JS交互 - SVG直接嵌入
- 视频管线 = HTML交互管线 - 交互 + 录制交付
- 演示管线 = HTML交互管线 - 交互 + 幻灯片结构
- PPT管线 = HTML交互管线 - 交互 - SVG - 动画

## 元素消费与转换

| 元素类型 | 转换规则 | 说明 |
|---------|---------|------|
| 文本元素 | Markdown → HTML | 保留完整结构 |
| SVG图形 | `<svg>` 直接嵌入 | 保留交互 |
| SVG动画 | SMIL/CSS动画直接嵌入 | 自动播放 |
| Canvas动画 | `<canvas>` + JS 直接嵌入 | 完整动画 |
| 音频元素 | `<audio>` 标签嵌入 | 播放控制 |
| 交互模块 | 大模型按需生成HTML/CSS/JS | 完整交互 |
| 数据元素 | JSON 驱动交互状态 | — |

## 课程骨架模板

模板路径：`templates/reveal-template.html`

### 骨架结构

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>课程标题</title>
  <style>
    /* CSS变量：取值由上层 --brand-spec 注入，形式层不规定具体配色 */
    :root {
      --primary: ...;     /* 强调色，上层指定 */
      --accent: ...;
      --bg: ...;          /* 背景色，上层指定 */
      --text: ...;        /* 文字色，上层指定 */
      --text-muted: ...;
      --border: ...;
      --card-bg: ...;
    }
    /* 响应式布局（断点由上层指定） */
    /* 打印样式 */
  </style>
</head>
<body>
  <nav><!-- 导航栏 + 侧边目录 --></nav>
  <main>
    <!-- 坡度导航器 -->
    <!-- 三阶进度条 -->
    <!-- 内容区域 -->
  </main>
  <script>
    // 交互逻辑
  </script>
</body>
</html>
```

## 交互组件

交互组件由大模型按需生成，不再使用预制modules。大模型根据内容需求直接生成HTML/CSS/JS代码嵌入到页面中。

**设计原则**：
- 交互必须服务于认知目标（如：翻转卡片帮助理解正反，知识图谱帮助理解关系）
- 不为交互而交互——纯展示内容不需要交互
- 每个交互组件必须可键盘操作，有 `alt`/`aria` 标签

## HTML六维信息容器

HTML作为六维信息容器，每个维度对应元素层的能力：

| 维度 | 对应元素 | HTML实现 |
|------|---------|---------|
| 内容 | 文本元素 | `<p>`, `<h1>`-`<h6>`, `<ul>`, `<table>` |
| 结构 | 数据元素 | `<section>`, `<article>`, `<nav>` |
| 布局 | 数据元素 | CSS Grid, Flexbox |
| 样式 | 图形元素 | CSS变量, `<svg>` |
| 交互 | 交互元素 | JS事件, DOM操作 |
| 保真 | 动画元素 | `<svg>` SMIL, CSS animation, `<canvas>` |

## 执行步骤

1. 从 `output/elements/` 读取元素
2. 加载课程骨架模板
3. 文本元素 → HTML结构
4. SVG/Canvas/交互模块 → 直接嵌入
5. 音频元素 → `<audio>` 嵌入
6. CSS变量 → 品牌色覆写
7. 响应式检查
8. 输出单文件HTML

## 输出

- 路径：`output/html/index.html`
- 格式：单文件，所有资源内联（CSS/JS/SVG）
- ⚠️ 单个HTML文件大小 ≤5MB

## 质量自检

| 检查项 | 标准 | 异常处理 |
|--------|------|---------|
| SVG渲染 | 所有SVG正确显示 | 检查viewBox和xmlns |
| 交互功能 | 所有模块可交互 | 测试点击/拖拽/翻转 |
| 响应式 | 移动端正常显示 | 检查断点布局 |
| 文件大小 | ≤5MB | 过大则拆分或压缩SVG |
| 打印 | 打印样式正常 | 检查@media print |
