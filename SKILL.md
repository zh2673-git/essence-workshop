---
name: 本质工坊
description: |
  认知→元素→管线→平台 富媒体交付系统。
  联邦式架构：7个独立子Skill + 1个路由Skill，每个子Skill自包含（references+templates+scripts），可独立使用也可统一调度。
  基于三阶方法论（是什么-为什么-怎么做）和类-属性-方法-路由模型，融合坡度理解渐进式认知方法。
  支持7大场景：知识探索、K12知识拆解、人物蒸馏、项目开发、项目解析、内容输出、Skill优化。
  三层交付架构：元素层（原子资产）→ 管线层（按平台约束组装）→ 平台层（交付成品）。
  6条管线：公众号管线、视频号管线、HTML交互管线、演示管线、PPT管线、Notebook管线。
  触发词：「探索XX」「拆解XX」「蒸馏XX」「开发XX」「分析XX」「写公众号」「做视频」「做PPT」「HTML交互」「做notebook」「优化skill」「达尔文」「darwin」。
---

# 本质工坊 · 场景路由

> **核心原则**：坡度理解 —— 先点出概念 → 建立联系 → 再详细解释
>
> **蒸馏公式**：三阶方法论（是什么→为什么→怎么做）× 坡度理解 × 类-属性-方法-路由
>
> **交付架构**：元素层（原子资产）→ 管线层（按平台约束组装）→ 平台层（交付成品）

---

## ⚠️ Agent 执行纪律

1. **先读规范再操作**：执行前必须检查对应子Skill中 `references/` 的硬性约束
2. **约束语言含义**：`必须` = 无条件遵守；`禁止` = 绝对不能做
3. **生成后自检**：每次生成文件后，必须执行质量自检
4. **Windows 环境**：PowerShell 用 `;` 替代 `&&`

---

## 场景路由表

| 路由 | 触发词 | 子Skill | 说明 |
|-----|--------|---------|------|
| **A: 知识探索** | 「探索XX」「理解XX」「XX是什么」 | [exploration/](exploration/SKILL.md) | 三阶正向推导，构建知识体系 |
| **A2: K12知识拆解** | 「拆解XX」「讲解XX」「知本」 | [knowledge/](knowledge/SKILL.md) | 七维框架拆解知识点，交互式HTML+知识图谱 |
| **B+B2: 蒸馏** | 「蒸馏XX」「提炼XX思维」「造skill」 | [distillation/](distillation/SKILL.md) | 人物/话题蒸馏，生成认知操作系统Skill |
| **C: 项目开发** | 「开发XX」「设计XX系统」 | [project-dev/](project-dev/SKILL.md) | 从零构建系统，设计文档+可运行代码 |
| **C2: 迭代开发** | 「迭代开发XX」「从0到1构建XX并迭代」「构建agent」 | [project-dev/iterative-loop.md](project-dev/iterative-loop.md) | Ratchet Loop闭环迭代，方案→执行→测试→评估→保留/回退 |
| **D: 项目解析** | 「分析XX项目」「拆解XX代码」 | [project-analysis/](project-analysis/SKILL.md) | 逆向分析现有项目 |
| **E: 内容输出** | 「写公众号」「做视频」「做PPT」「HTML交互」「做notebook」 | [content-output/](content-output/SKILL.md) | 多管线发布（6条管线+3种风格） |
| **F: Skill优化** | 「优化skill」「达尔文」「darwin」 | [skill-optimization/](skill-optimization/SKILL.md) | 评估→改进→验证循环 |

### 场景间流转

```
A(探索) → 理解概念后想开发 → C(项目开发)
A(探索) → 输出教学notebook → E(Notebook管线)
A2(拆解) → 拆解后想做视频 → E(内容输出) → 视频号管线
A2(拆解) → 拆解后想继续拆解 → A2(递归)
B(蒸馏) → 蒸馏后想用其风格输出 → E(内容输出) + 蒸馏Skill风格
B(蒸馏) → 质量不达标 → F(Skill优化)
C(开发) → 开发完想输出文章 → E(内容输出)
C(开发) → 开发完想生成教学notebook → E(Notebook管线)
C(开发) → 需要迭代改进 → C2(迭代开发)
C2(迭代) → 收敛后沉淀经验 → B2(话题蒸馏)
C2(迭代) → 收敛后生成教学notebook → E(Notebook管线)
D(解析) → 解析完想输出文章 → E(内容输出)
D(解析) → 解析完想生成教学notebook → E(Notebook管线)
E(输出) → 同一内容可走不同管线 → 管线切换（元素层复用）
```

---

## 三层交付架构

```
元素层（Element）—— 原子资产，跨管线共享
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│文本元素│ │图形元素│ │动画元素│ │音频元素│ │交互元素│
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
         ↓
管线层（Pipeline）—— 按平台约束组装
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│公众号  │ │视频号  │ │HTML交互│ │ 演示   │ │  PPT   │ │Notebook│
└───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
    ↓          ↓          ↓          ↓          ↓          ↓
平台层（Platform）—— 交付成品
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│微信公众号│ │视频号  │ │浏览器  │ │Reveal  │ │PPT/WPS │ │Jupyter │
│受限HTML │ │MP4     │ │HTML交互│ │.js演示 │ │.pptx   │ │.ipynb  │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

### 输出风格

| 风格 | 说明 |
|------|------|
| 论文风格 | 专业严谨，五段式结构 |
| 对话风格 | Q&A结构，播客文字版 |
| 蒸馏Skill风格 | 激活distillation/output/中对应人物Skill，以其视角输出 |

---

## 核心公式

```
坡度理解：阶段1（点出概念）→ 阶段2（建立联系）→ 阶段3（详细解释）

三阶推导：
  场景A/B/C：是什么 → 为什么 → 怎么做
  场景D：怎么做 ← 为什么 ← 是什么

蒸馏公式：
  认知系统 = Class，心智模型 = 属性，决策启发式 = 方法，场景适配 = 路由，表达DNA = 接口

三层架构映射：
  元素层 = 属性（原子资产）
  管线层 = 方法（按平台约束组装）
  平台层 = 路由（交付分发）
```

---

## 文件结构

```
essence-workshop/                    # 路由Skill（本文件）
├── SKILL.md                         # 场景路由表
│
├── exploration/                     # A: 知识探索
│   ├── SKILL.md
│   ├── A-knowledge-exploration.md   # 工作流
│   └── references/                  # 方法论+笔记模板
│
├── knowledge/                       # A2: K12知识拆解（知本）
│   ├── SKILL.md
│   ├── references/                  # 范式族插件+学段适配
│   ├── templates/                   # HTML模板（decomposition/project/lecture）
│   ├── output/                      # 生成的HTML+知识图谱
│   └── docs/                        # 设计文档
│
├── distillation/                    # B+B2: 人物/话题蒸馏
│   ├── SKILL.md
│   ├── B-person-distillation.md     # 人物蒸馏工作流
│   ├── B2-topic-distillation.md     # 话题蒸馏工作流
│   ├── references/                  # 蒸馏方法论+材料验证
│   ├── templates/                   # 蒸馏Skill模板
│   └── output/                      # 蒸馏实例（11个已蒸馏Skill）
│
├── project-dev/                     # C: 项目开发
│   ├── SKILL.md
│   ├── C-project-development.md     # 工作流（含迭代模式）
│   ├── iterative-loop.md            # C2: 迭代开发（通用Ratchet Loop）
│   ├── references/                  # 设计原则 + ratchet-loop
│   └── templates/                   # 项目模板 + program.md
│
├── project-analysis/                # D: 项目解析
│   ├── SKILL.md
│   ├── D-project-analysis.md        # 工作流
│   ├── references/                  # 代码阅读+设计原则
│   └── templates/                   # 解析模板
│
├── content-output/                  # E: 内容输出
│   ├── SKILL.md
│   ├── E-content-output.md          # 工作流
│   ├── references/                  # 5条管线规范+通用规范
│   ├── templates/                   # Reveal模板+品牌规格
│   └── scripts/                     # 管线脚本（html/pptx/slides/video/wechat）
│
└── skill-optimization/              # F: Skill优化
    ├── SKILL.md
    ├── F-skill-optimization.md      # 工作流
    └── references/                  # Skill模板+评分+反模式
```

---

*本质工坊 · 认知→元素→管线→平台 · 三阶方法论 × 坡度理解 × 类-属性-方法-路由*
