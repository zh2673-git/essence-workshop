---
name: Reveal演示适配器
description: |
  Reveal.js演示平台适配：将Markdown/HTML转为Reveal.js幻灯片演示页。
  支持SVG直接嵌入、CSS动画、演讲者备注、PDF导出。
  相比PPT管线更轻量、Git友好、AI生成友好。
  输入：Markdown/HTML格式产物。输出：Reveal.js演示HTML。
  触发词：「做演示」「做slides」「Reveal演示」。
version: 1.0
layer: workflow
adapter: reveal
---

# Reveal演示适配器

> 将Markdown/HTML适配为Reveal.js幻灯片演示页，支持SVG嵌入、CSS动画与PDF导出。

## 输入与输出

| 项 | 说明 |
|----|------|
| 输入 | Markdown/HTML 格式产物（来自 format） |
| 输出 | Reveal.js 演示HTML（依赖CDN加载Reveal.js） |

## 平台约束

| 约束项 | 说明 |
|--------|------|
| 框架 | Reveal.js（slides结构，非滚动页面） |
| 依赖 | CDN加载 reveal.js@5 |
| 导出 | 支持PDF导出（URL加 `?print-pdf`） |
| 浏览器 | 需现代浏览器（Chrome/Firefox/Safari/Edge） |

## 元素转换

| 源元素 | 目标 |
|--------|------|
| 文本 H1 | section 封面 |
| 文本 H2 | section 分隔 |
| 文本 H3 | section 内容 |
| SVG | 直接嵌入（保留矢量） |
| SVG动画 | SMIL/CSS 嵌入 |
| Canvas | JS 嵌入 |
| 音频/交互 | 不消费（跳过） |

## 模板特性

- 演讲者备注（`aside.notes`）
- PDF导出（`?print-pdf`）
- 代码高亮（highlight.js）
- 响应式 + 键盘/触摸导航
- 幻灯片编号

## 适配流程

```
1. 读取元素（文本/SVG/SVG动画/Canvas）
2. 文本按 H1/H2/H3 拆分 section
3. SVG 嵌入对应 section（保留 viewBox/xmlns）
4. 加载 Reveal.js 模板
5. 注入内容
6. 输出 HTML
```

## 失败模式

| 失败 | 处理 |
|------|------|
| 幻灯片 <10页 | 合并相邻内容 |
| 幻灯片 >30页 | 拆分为多个演示 |
| 纯文字 >50% | 拆分或加图 |
| 动画不流畅 | 检查CSS兼容性 |
| SVG不显示 | 检查 viewBox/xmlns |

## 质量自检

- [ ] 幻灯片页数 10-30
- [ ] 文本按 H1/H2/H3 正确拆分 section
- [ ] SVG含 viewBox/xmlns，矢量保留
- [ ] 纯文字占比 <50%
- [ ] 演讲者备注（aside.notes）齐全
- [ ] PDF导出（?print-pdf）可用
- [ ] Reveal.js@5 CDN 正常加载
- [ ] 代码高亮（highlight.js）生效

## 使用场景

- 知识探索的轻量演示输出
- Git友好的演示版本管理
- AI生成友好的幻灯片快速产出

## 与PPT管线对比

| 维度 | Reveal（本适配器） | PPT管线 |
|------|---------------------|---------|
| 交互 | ✅ CSS/SVG动画 | ❌ 无交互 |
| 格式 | HTML（Git友好） | .pptx（Git不友好） |
| AI生成 | ✅ 友好 | 需库辅助 |
| 浏览器 | 需浏览器 | 离线可用 |
| 企业模板 | ❌ | ✅ 支持 |

平台选择由上层场景层决定，本适配器不做平台推荐。

## 脚本

```
reveal/
└── scripts/
    └── generator.py          # Markdown/HTML → Reveal.js HTML
```

模板：`../../format/html/templates/reveal-template.html`（reveal 共用 html 管线模板）

## 与其他适配器的关系

| 适配器 | 区别 |
|--------|------|
| **Reveal演示（本适配器）** | Reveal.js框架，slides结构，CSS/SVG动画 |
| 浏览器 | 滚动页面，无框架约束 |
| PPT/WPS | .pptx格式，PowerPoint/WPS兼容 |

## references

- [references.slides-pipeline.md](references.slides-pipeline.md) — 幻灯片管线规范

---

*Reveal演示适配器 · Markdown/HTML→Reveal.js演示HTML · SVG嵌入+CSS动画+PDF导出*
