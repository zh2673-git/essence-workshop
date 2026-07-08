# 本质工坊 · Essence Workshop

**[中文](README.md)** ｜ **[English](README_EN.md)**

> **认知引擎 × 格式管线 × 平台适配 × 场景编排** 富媒体交付系统（v3.0）

融合三阶方法论（是什么-为什么-怎么做）和类-属性-方法-路由模型，通过四层架构实现职责纯粹性：认知引擎管认知视角、格式管线管格式表达、平台适配管平台适配、场景编排管调用顺序。

---

## v3.0 四层架构

```
essence-workshop/
├── cognitive-engine/          # 认知引擎层（认知视角与理解方法）
│   ├── general-logic/         # 通用逻辑：三阶合一、本质定义先行、顿悟触发
│   ├── yijing-perspective/    # 易经视角：取象分析、卦象映射
│   ├── law-application/       # 法条适用：事实裁剪、涵摄、法律解释
│   └── fable-concept/         # 寓言化：概念寓言化、本质隐喻
│
├── format-pipeline/           # 格式管线层（格式表达）
│   ├── markdown/              # Markdown 格式（含 Obsidian 兼容）
│   ├── html/                  # HTML 交互页面
│   ├── video/                 # 视频管线
│   ├── whiteboard/            # 白板动画 JSON
│   ├── broadcast/             # 口播稿
│   ├── notebook/              # Jupyter notebook
│   ├── ppt/                   # PPTX 演示
│   └── audio/                 # 音频管线
│
├── platform-adapter/          # 平台适配层（交付适配）
│   ├── wechat/                # 公众号平台
│   ├── video-channel/         # 视频号平台
│   ├── reveal/                # Reveal.js 演示
│   ├── whiteboard-recorder/   # 白板录制器
│   ├── obsidian/              # Obsidian 本地知识库
│   ├── jupyter/               # Jupyter 平台
│   ├── browser/               # 浏览器交付
│   ├── ppt-wps/               # PPT 平台（WPS/Office）
│   └── project/               # 项目交付
│
├── scenarios/                 # 场景编排层（调用顺序）
│   ├── knowledge-exploration/ # A: 知识探索
│   ├── k12-decomposition/     # A2: K12知识拆解（知本）
│   ├── project-dev/           # C: 项目开发
│   ├── project-analysis/      # D: 项目解析
│   ├── serial-fiction/        # E2: 连载小说
│   ├── law-analysis/          # L: 法律分析
│   └── distillation/          # B+B2: 人物/话题蒸馏
│
├── cases/                     # 实战案例与归档文档
│   ├── samples/               # 示例项目
│   ├── video-dsl/             # 视频DSL设计文档
│   ├── k12-design-docs/       # K12架构设计文档（归档）
│   └── ...
│
└── skill-optimization/        # F: Skill优化（元场景）
```

### 职责纯粹性原则

| 层 | 职责 | 不做什么 |
|---|------|---------|
| **认知引擎** | 认知视角与理解方法 | 不规定格式模板、字数篇幅、分节决策、平台约束 |
| **格式管线** | 格式转换与元素规范 | 不做认知分析、风格选择、平台适配 |
| **平台适配** | 平台约束执行、素材上传 | 不做内容生成、认知分析、风格选择 |
| **场景编排** | 调用顺序、QC检查点、条件分支 | 不直接实现认知分析、格式转换、平台适配 |

---

## 9大场景

| 场景 | 触发词 | 认知视角 | 格式 | 平台 | 子Skill |
|------|--------|---------|------|------|---------|
| **A: 知识探索** | 「探索XX」「理解XX」 | 通用逻辑 | Markdown | Obsidian | scenarios/knowledge-exploration/ |
| **A2: K12拆解** | 「拆解XX」「讲解XX」 | 通用逻辑 | HTML交互 | 浏览器 | scenarios/k12-decomposition/ |
| **B+B2: 蒸馏** | 「蒸馏XX」「提炼XX思维」 | 蒸馏框架 | Skill | 认知层 | distillation/ |
| **C: 项目开发** | 「开发XX」「设计XX系统」 | 通用逻辑 | Markdown+代码 | 项目交付 | scenarios/project-dev/ |
| **D: 项目解析** | 「分析XX项目」 | 通用逻辑（逆向） | Markdown | Obsidian | scenarios/project-analysis/ |
| **E2: 连载小说** | 「写连载小说」「连载XX」 | 通用逻辑+寓言 | Markdown | 公众号 | scenarios/serial-fiction/ |
| **F: Skill优化** | 「优化skill」「达尔文」 | Skill评估框架 | Markdown | - | skill-optimization/ |
| **H: 易经视角** | 「用易经看XX」「XX是什么象」 | 易经视角 | Markdown | Obsidian | cognitive-engine/yijing-perspective/ |
| **L: 法律分析** | 「法条适用」「怎么证明」 | 法条适用 | Markdown | - | scenarios/law-analysis/ |

---

## 8条格式管线

| 管线 | 状态 | 输出 |
|------|------|------|
| Markdown | ✅ 生产可用 | 标准.md（含 Obsidian wiki-links） |
| HTML | ✅ 生产可用 | 交互式HTML |
| Video | ✅ 生产可用 | MP4视频 |
| 白板动画 | ✅ 生产可用 | Excalidraw JSON |
| 口播稿 | ✅ 生产可用 | 5镜头口语化Markdown |
| Notebook | 🟡 骨架可用 | Jupyter .ipynb |
| PPT | 🟡 骨架可用 | .pptx文件 |
| Audio | 🟡 骨架可用 | MP3音频 |

---

## 方法论核心

**三阶合一**：阶段1「是什么」点出本质 → 阶段2「为什么」建立因果（含反常识根因）→ 阶段3「怎么做」展开方法（视角升级）

**本质定义先行**：所有分析先确定本质定义，通过本质检验（可回溯检验）

**顿悟触发机制**：一句话点破 + 反常识根因 + 视角升级

**类-属性-方法-路由**：由本质定义锚定，本质 → 类归属 → 属性展开 → 方法体现 → 路由适配

详见：cognitive-engine/general-logic/references/methodology.md

---

## 已蒸馏实例（11个）

查理·芒格 · 达尔文 · 爱因斯坦 · 孔子 · 老子 · 鲁迅 · 倪海厦 · 苏格拉底 · 王阳明 · 荀子 · 诸葛亮

---

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/your-username/essence-workshop.git

# 探索场景路由
cat SKILL.md

# 使用特定场景（例如知识探索）
cat scenarios/knowledge-exploration/SKILL.md
```

---

*本质工坊 v3.0 · 认知引擎×格式管线×平台适配×场景编排 · 三阶合一 × 本质定义先行 × 顿悟触发机制*