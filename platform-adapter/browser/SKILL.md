---
name: 浏览器平台
description: |
  浏览器平台适配器：将通用HTML格式产物适配为浏览器优化的交互式HTML成品。
  关注响应式布局、SEO、可访问性、性能优化。不限制CSS/JS（区别于公众号受限HTML）。
  输入：通用HTML格式产物。输出：浏览器优化的.html成品。
  触发词：「HTML交互」「做网页」「浏览器版」。
version: 1.0
layer: platform
adapter: browser
---

# 浏览器平台适配器

> 将通用HTML适配为浏览器优化的交互式页面。无CSS/JS限制，支持完整交互。

## 平台约束

| 约束项 | 说明 |
|--------|------|
| CSS/JS | ✅ 无限制（内联或外部引用均可） |
| 响应式 | 必须支持桌面+移动端（viewport meta + media query） |
| SEO | 必须含title、meta description、语义化HTML标签 |
| 可访问性 | 必须含alt文本、ARIA标签、键盘导航支持 |
| 性能 | 单文件<2MB，首屏<3秒（LCP） |
| 浏览器兼容 | Chrome 90+、Firefox 88+、Safari 14+、Edge 90+ |

## 适配流程

```
1. 通用HTML产物 → 检查结构完整性
2. 注入响应式meta和media query
3. 注入SEO标签（title/description/og:）
4. 检查可访问性（alt/aria/keyboard）
5. （可选）压缩CSS/JS
6. 导出 .html 成品
```

## 与其他适配器的关系

| 适配器 | 区别 |
|--------|------|
| **浏览器（本适配器）** | 无CSS/JS限制，完整交互 |
| 微信公众号 | CSS必须内联，禁止外部JS，图片需上传素材库 |
| Reveal演示 | Reveal.js框架，slides结构，非滚动页面 |

## 脚本

```
browser/
└── scripts/                    # 适配脚本（规划中）
    └── adapter.py              # HTML→浏览器优化HTML
```

共享平台脚本：[../scripts/platforms/browser.py](../scripts/platforms/browser.py)

## 使用场景

- K12知识拆解的交互式HTML输出
- 知识探索的富交互页面
- 任何需要完整CSS/JS交互的HTML成品

---

*浏览器平台 · 通用HTML→浏览器优化HTML · 无CSS/JS限制*
