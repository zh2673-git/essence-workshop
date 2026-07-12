---
name: 周易占卜工作流
description: |
  周易占卜的浏览器交互式交付工作流。
  编排：认知(易经视角) × 框架(周易占卜框架) × 形式(HTML) × 平台(浏览器)。
  源自「有疑再问」微信小程序的转换，绕过微信平台限制，保留完整占卜体验。
  产物存放在 output/ 目录。
version: 1.0
layer: workflow
source: 源自 002-有疑再问小程序 转换
---

# 周易占卜工作流 · 浏览器交互式交付

> **本工作流将「有疑再问」微信小程序转换为浏览器HTML版**。
> 微信官方对占卜类小程序有限制，通过转换为浏览器版绕过限制，保留完整占卜体验。

---

## 工作流编排

```
工作流 = 认知(易经视角) × 框架(周易占卜框架) × 形式(HTML) × 平台(浏览器)
```

| 因子 | 选择 | 来源 |
|------|------|------|
| 认知 | 易经视角（不疑不问心法、取象定象） | [cognitive/yijing-perspective/](../../cognitive/yijing-perspective/SKILL.md) |
| 框架 | 周易占卜框架（问题→摇卦→卦象→解释） | [content-framework/iching-divination/](../../content-framework/iching-divination/iching-divination.md) |
| 形式 | HTML（单页应用SPA） | [format/html/](../../format/html/SKILL.md) |
| 平台 | 浏览器（无平台限制） | [workflow/browser-interactive/](../browser-interactive/SKILL.md) |

---

## 转换映射表

### 微信小程序 → 浏览器HTML

| 小程序 | 浏览器HTML | 说明 |
|--------|-----------|------|
| `app.js` (globalData) | JS 全局对象 + localStorage | 状态管理与持久化 |
| `wx.navigateTo` | 视图切换函数 `showView(name)` | 单页应用路由 |
| `wx.setStorageSync` | `localStorage.setItem` | 本地存储 |
| `wx.showModal` | 自定义模态框 `showModal()` | 替代微信API |
| `wx.showToast` | 自定义提示 `showToast()` | 替代微信API |
| `Component({})` (coin) | HTML + CSS3 3D Transform | 硬币翻转动画 |
| `wx.createAnimation` | CSS @keyframes + JS class 切换 | 动画系统 |
| WXML 模板 | HTML + 模板字符串 | 视图结构 |
| WXSS 样式 (rpx) | CSS (px, 按比例转换) | 样式系统 |
| `bindtap` | `addEventListener('click')` | 事件绑定 |
| `image` 组件 | `<img>` 标签 | 图片资源 |
| `progress` 组件 | `<div>` + CSS width | 进度条 |

### 页面 → 视图

| 小程序页面 | HTML视图 | 功能 |
|-----------|---------|------|
| `pages/index/index` | `#view-home` | 首页（介绍+统计+最近记录） |
| `pages/divinationPkg/divination/divination` | `#view-divination` | 占卜页（问题→摇卦→结果） |
| `pages/divinationPkg/detail/detail` | `#view-detail` | 详情页（卦象+卦辞+解释） |
| `pages/divinationPkg/history/history` | `#view-history` | 历史页（记录列表） |

---

## 产物结构

```
workflow/iching-divination/
├── SKILL.md                          # 本工作流编排文档
└── output/
    ├── index.html                    # 浏览器HTML成品（单文件SPA）
    └── assets/
        └── images/
            ├── hexagrams/            # 64卦图片（0.jpg ~ 63.jpg）
            ├── coin_front.png        # 硬币正面
            ├── coin_back.png         # 硬币背面
            ├── coin_yang.png         # 阳爻硬币
            ├── coin_yin.png          # 阴爻硬币
            ├── logo.png              # Logo
            └── empty.png             # 空状态图
```

---

## 交付流程

```
1. 调用认知层（易经视角）→ 提供心法约束与取象视角
2. 调用框架层（周易占卜框架）→ 提供内容组织结构与数据规范
3. 调用形式层（HTML）→ 将结构化内容转为HTML格式
4. 浏览器平台适配 → 响应式布局 + SEO + 完整交互
5. 输出到 output/ 目录 → index.html + assets/
```

---

## 关键实现要点

### 1. 状态管理
- 全局状态对象 `app` 替代小程序 `getApp().globalData`
- `localStorage` 持久化历史记录与每日统计
- 日期变更时重置今日预测次数

### 2. 硬币翻转动画
- CSS3 `transform-style: preserve-3d` + `backface-visibility: hidden`
- `@keyframes` 实现翻转，JS 控制时长与结果
- 正反面用 `coin_yang.png` / `coin_yin.png`

### 3. 卦象计算逻辑
- 三硬币法：阳面计3，阴面计2，和值6/7/8/9
- 本卦/变卦计算：变爻反转
- 上下卦映射：八卦二进制查表
- 64卦查询：HEXAGRAM_LOOKUP 表

### 4. 视图切换（SPA）
- 单 HTML 文件包含所有视图
- JS 函数 `showView(viewName)` 控制显示
- 浏览器前进后退通过 `location.hash` 支持（可选）

### 5. 响应式适配
- 移动端优先设计（保持小程序的竖屏体验）
- viewport meta + media query
- 触摸事件优化

---

## 与原小程序的差异

| 项目 | 小程序 | 浏览器版 |
|------|--------|---------|
| 平台限制 | 微信审核（占卜类受限） | 无限制 |
| 分发 | 微信扫码/搜索 | URL直链/部署 |
| 存储 | wx.setStorageSync | localStorage |
| 性能 | 微信运行时 | 浏览器原生 |
| 跨平台 | 仅微信 | 任意浏览器 |

---

## 扩展能力

由于采用了四层架构，本工作流可灵活扩展：

- **换形式**：调用 Markdown 形式 → 输出周易解读文章
- **换平台**：调用公众号发布工作流 → 推送卦象解读
- **换场景**：调用 K12 课件工作流 → 国学教育课件
- **换视角**：调用白板录制工作流 → 卦象讲解视频

---

*周易占卜工作流 · v1.0 · 认知×框架×形式×平台 · 浏览器交互式交付*
