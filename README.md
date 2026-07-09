# 本质工坊 · Essence Workshop

**[中文](README.md)** ｜ **[English](README_EN.md)**

> **认知 × 内容框架 × 形式 × 工作流** 四层可组合富媒体交付系统（v4.1）

融合三阶方法论（是什么-为什么-怎么做）和类-属性-方法-路由模型，通过四层架构实现职责纯粹性：认知层管理解逻辑、内容框架层管内容结构、形式层管格式规范、工作流层管做事流程。

---

## v4.1 四层架构

```
essence-workshop/
├── cognitive/                  # 第1层：认知层（用什么视角理解事物）
│   ├── general-logic/         # 通用逻辑（理性逻辑：三阶合一、本质定义先行、顿悟触发）
│   └── yijing-perspective/    # 易经视角（感性逻辑：取象分析、卦象映射）
│
├── content-framework/           # 第2层：内容框架层（用什么框架组织内容）
│   ├── essay/                  # 高考作文框架（五步法）
│   ├── fable-concept/          # 寓言故事框架
│   ├── law-application/        # 法律适用框架（8个核心原子方法）
│   ├── k12-decomposition/      # K12课件设计框架
│   ├── serial-fiction/         # 连载小说写作框架
│   ├── project-analysis/       # 项目分析框架
│   ├── project-dev/            # 项目开发框架
│   ├── distillation/           # 蒸馏框架（结构+方法论）
│   ├── broadcast-script/       # 口播稿框架
│   └── docs/                   # 框架设计文档
│
├── format/                      # 第3层：形式层（用什么格式表达）
│   ├── markdown/               # Markdown 形式规范
│   ├── html/                   # HTML 形式规范
│   ├── slides/                 # Reveal.js 幻灯片形式
│   ├── video/                  # 视频形式（含 video-dsl）
│   ├── whiteboard/            # 白板动画形式
│   ├── notebook/              # Jupyter notebook 形式
│   ├── ppt/                   # PPTX 演示形式
│   ├── audio/                 # 音频形式
│   ├── skill/                 # Skill 文档形式
│   └── references/             # 共享元素规范
│
├── workflow/                    # 第4层：工作流层（编排交付+场景流程）
│   ├── wechat-publish/         # 公众号发布工作流
│   ├── whiteboard-recorder/   # 白板录制工作流
│   ├── video-channel/         # 视频号工作流
│   ├── browser-interactive/   # 浏览器交互工作流
│   ├── reveal-slides/         # Reveal幻灯片工作流
│   ├── ppt-wps/               # PPT/WPS工作流
│   ├── jupyter-notebook/      # Jupyter工作流
│   ├── obsidian-knowledge/    # Obsidian工作流
│   ├── project-delivery/      # 项目交付工作流
│   ├── k12-decomposition/     # K12课件工作流（含output/产物）
│   ├── knowledge-exploration/ # 知识探索工作流
│   ├── serial-fiction/        # 连载小说工作流（含output/产物）
│   ├── project-dev/           # 项目开发工作流+迭代循环
│   ├── project-analysis/      # 项目解析工作流
│   ├── law-analysis/          # 法律分析工作流（编排器）
│   └── distillation/          # 蒸馏工作流（含output/产物）
│
└── skill-optimization/         # 元场景F：Skill优化
```

### 职责纯粹性原则

| 层 | 职责 | 不做什么 |
|---|------|---------|
| **认知层** | 理解逻辑（理性+感性），总结框架 | 不规定格式、不产生实质内容、不做流程编排 |
| **内容框架层** | 沉淀可复用的内容结构 | 不含实质内容（实质内容在形式层转换时产生）、不做流程编排 |
| **形式层** | 通用形式规范（md/html等基础要求） | 不做认知分析、不定义内容框架、不做流程编排 |
| **工作流层** | 具体做事流程编排，产物存output/ | 不生成认知、不定义框架、不做格式转换 |

---

## 9大场景

| 场景 | 触发词 | 认知视角 | 内容框架 | 工作流 | 子Skill |
|------|--------|---------|---------|--------|---------|
| **A: 知识探索** | 「探索XX」「理解XX」 | 通用逻辑 | -（直接用认知层） | Obsidian | cognitive/general-logic/ + workflow/knowledge-exploration/ |
| **A2: K12拆解** | 「拆解XX」「讲解XX」 | 通用逻辑 | K12课件框架 | 浏览器 | content-framework/k12-decomposition/ + workflow/k12-decomposition/ |
| **B+B2: 蒸馏** | 「蒸馏XX」「提炼XX思维」 | 通用逻辑 | 蒸馏框架 | 蒸馏工作流 | content-framework/distillation/ + workflow/distillation/ |
| **C: 项目开发** | 「开发XX」「设计XX系统」 | 通用逻辑 | 项目开发框架 | 项目交付 | content-framework/project-dev/ + workflow/project-dev/ |
| **C2: 迭代开发** | 「迭代开发XX」 | 通用逻辑 | 项目开发框架 | 项目交付 | workflow/project-dev/iterative-loop.md |
| **D: 项目解析** | 「分析XX项目」 | 通用逻辑（逆向） | 项目分析框架 | Obsidian | content-framework/project-analysis/ + workflow/project-analysis/ |
| **E2: 连载小说** | 「写连载小说」「连载XX」 | 通用逻辑 | 连载小说框架 | 公众号 | content-framework/serial-fiction/ + workflow/serial-fiction/ |
| **F: Skill优化** | 「优化skill」「达尔文」 | - | - | - | skill-optimization/ |
| **G: 概念寓言化** | 「用寓言讲XX」「XX寓言化」 | 通用逻辑 | 寓言故事框架 | - | content-framework/fable-concept/ |
| **H: 易经视角** | 「用易经看XX」「XX是什么象」 | 易经视角 | - | Obsidian | cognitive/yijing-perspective/ |
| **L: 法律分析** | 「法条适用」「怎么证明」 | 通用逻辑 | 法律适用框架 | 法律分析工作流 | content-framework/law-application/ + workflow/law-analysis/ |

---

## 8条形式管线

| 管线 | 状态 | 输出 |
|------|------|------|
| Markdown | ✅ 生产可用 | 标准.md（含 Obsidian wiki-links） |
| HTML | ✅ 生产可用 | 交互式HTML |
| Video | ✅ 生产可用 | MP4视频 |
| 白板动画 | ✅ 生产可用 | Excalidraw JSON |
| Slides | ✅ 生产可用 | Reveal.js 演示HTML |
| Notebook | 🟡 骨架可用 | Jupyter .ipynb |
| PPT | 🟡 骨架可用 | .pptx文件 |
| Audio | 🟡 骨架可用 | MP3音频 |

---

## 方法论核心

**三阶合一**：阶段1「是什么」点出本质 → 阶段2「为什么」建立因果（含反常识根因）→ 阶段3「怎么做」展开方法（视角升级）

**本质定义先行**：所有分析先确定本质定义，通过本质检验（可回溯检验）

**顿悟触发机制**：一句话点破 + 反常识根因 + 视角升级

**类-属性-方法-路由**：由本质定义锚定，本质 → 类归属 → 属性展开 → 方法体现 → 路由适配

详见：cognitive/general-logic/references/methodology.md

---

## 已蒸馏实例（11个）

查理·芒格 · 达尔文 · 爱因斯坦 · 孔子 · 老子 · 鲁迅 · 倪海厦 · 苏格拉底 · 王阳明 · 荀子 · 诸葛亮

蒸馏产物存放在 workflow/distillation/output/

---

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/your-username/essence-workshop.git

# 探索场景路由
cat SKILL.md

# 使用特定场景（例如知识探索，直接用认知层）
cat cognitive/general-logic/SKILL.md
```

---

*本质工坊 v4.1 · 认知×内容框架×形式×工作流 · 三阶合一 × 本质定义先行 × 顿悟触发机制*
