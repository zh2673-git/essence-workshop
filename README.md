# 本质工坊 · Essence Workshop

**[中文](README.md)** ｜ **[English](README_EN.md)**

> **认知 → 元素 → 管线 → 平台** 富媒体交付系统

融合三阶方法论（是什么-为什么-怎么做）和类-属性-方法-路由模型，支持7大场景独立运行。

---

## 架构：7个独立子Skill + 1个路由

每个子Skill自包含（references + templates + scripts），可独立使用，也可通过路由Skill统一调度。

```
essence-workshop/                    # 路由Skill
├── SKILL.md                         # 场景路由表
│
├── exploration/                     # A: 知识探索
├── knowledge/                       # A2: K12知识拆解（知本）
├── distillation/                    # B+B2: 人物/话题蒸馏
├── project-dev/                     # C: 项目开发
├── project-analysis/                # D: 项目解析
├── content-output/                  # E: 内容输出（5条管线）
└── skill-optimization/              # F: Skill优化
```

## 7大场景

| 场景 | 触发词 | 子Skill | 输出 |
|------|--------|---------|------|
| **A: 知识探索** | 「探索XX」「理解XX」 | exploration/ | 结构化知识笔记 |
| **A2: K12知识拆解** | 「拆解XX」「讲解XX」「知本」 | knowledge/ | 交互式HTML+知识图谱 |
| **B+B2: 蒸馏** | 「蒸馏XX」「提炼XX思维」 | distillation/ | 认知操作系统Skill |
| **C: 项目开发** | 「开发XX」「设计XX系统」 | project-dev/ | 设计文档+可运行代码 |
| **D: 项目解析** | 「分析XX项目」 | project-analysis/ | 项目理解文档 |
| **E: 内容输出** | 「写公众号」「做视频」「做PPT」 | content-output/ | 公众号/视频/HTML/演示/PPT |
| **F: Skill优化** | 「优化skill」「达尔文」 | skill-optimization/ | 评分卡+优化报告 |

## 5条管线（场景E）

| 管线 | 状态 | 输出 |
|------|------|------|
| 公众号 | ✅ 生产可用 | 微信受限HTML |
| 视频号 | ✅ 生产可用 | MP4视频 |
| HTML交互 | 🟡 骨架可用 | 完整交互HTML |
| 演示 | 🟡 骨架可用 | Reveal.js HTML |
| PPT | 🟡 骨架可用 | .pptx文件 |

## 已蒸馏实例（11个）

查理·芒格 · 达尔文 · 爱因斯坦 · 孔子 · 老子 · 鲁迅 · 倪海厦 · 苏格拉底 · 王阳明 · 荀子 · 诸葛亮

---

*本质工坊 · 认知→元素→管线→平台 · 三阶方法论 × 坡度理解 × 类-属性-方法-路由*
