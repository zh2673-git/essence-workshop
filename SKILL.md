---
name: 本质工坊
description: |
  融合「本质探索」「本质蒸馏」「公众号发布」「视频号生成」四合一的认知→设计→开发→输出系统。
  基于三阶方法论（是什么-为什么-怎么做）和类-属性-方法-路由模型，融合坡度理解渐进式认知方法。
  支持5大场景：知识探索、人物蒸馏、项目开发、项目解析、内容输出。
  输出阶段支持多渠道：微信公众号（图文）、微信视频号（短视频）。
  输出风格支持：论文风格、蒸馏Skill风格、对话风格，以及预留扩展。
  触发词：「探索XX」「蒸馏XX」「开发XX」「分析XX」「写公众号」「发布文章」「做视频」「视频号」。
  模糊需求也触发：「我想提升决策质量」「帮我理解XX」「设计一个XX系统」。
---

# 本质工坊 · 认知→设计→开发→输出 全链路系统

> **核心原则**：坡度理解 —— 先点出概念 → 建立联系 → 再详细解释
>
> **设计思想**：项目 = 类，模块 = 属性，接口 = 契约，路由 = 方法分发
>
> **蒸馏公式**：三阶方法论（是什么→为什么→怎么做）× 坡度理解 × 类-属性-方法-路由
>
> **输出渠道**：微信公众号（图文） / 微信视频号（Canvas卡片翻页+TTS短视频）

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        本质工坊                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   输入 → 路由分发 → 场景执行 → 输出风格选择 → 最终产出          │
│                                                                  │
│   ┌──────────┐                                                   │
│   │  路由表  │                                                   │
│   ├──────────┤                                                   │
│   │ A:探索   │ → 知识探索 → 结构化知识笔记                      │
│   │ B:蒸馏   │ → 人物蒸馏 → 认知操作系统Skill                   │
│   │ C:开发   │ → 项目开发 → 设计文档+可运行代码                 │
│   │ D:解析   │ → 项目解析 → 项目理解文档                        │
│   │ E:输出   │ → 内容输出 → 多渠道发布（公众号/视频号）            │
│   └──────────┘                                                   │
│                                                                  │
│   ┌──────────────────────────────────────────┐                  │
│   │           输出风格系统                    │                  │
│   ├──────────────────────────────────────────┤                  │
│   │ 论文风格  │ 蒸馏Skill风格 │ 对话风格 │ ... │                  │
│   └──────────────────────────────────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5大场景路由

| 路由 | 触发词 | 核心目标 | 输出 | 详见 |
|-----|--------|---------|------|------|
| **A: 知识探索** | 「探索XX」「理解XX」「XX是什么」 | 从零构建知识体系 | 结构化知识笔记 | [workflows/A-knowledge-exploration.md](workflows/A-knowledge-exploration.md) |
| **B: 人物蒸馏** | 「蒸馏XX」「提炼XX思维」「造skill」 | 蒸馏认知操作系统 | 认知操作系统Skill | [workflows/B-person-distillation.md](workflows/B-person-distillation.md) |
| **C: 项目开发** | 「开发XX」「设计XX系统」「构建XX」 | 从零构建系统 | 设计文档+可运行代码 | [workflows/C-project-development.md](workflows/C-project-development.md) |
| **D: 项目解析** | 「分析XX项目」「拆解XX代码」 | 理解已有系统 | 项目理解文档 | [workflows/D-project-analysis.md](workflows/D-project-analysis.md) |
| **E: 内容输出** | 「写公众号」「发布文章」「做视频」「视频号」 | 多渠道内容发布 | 公众号文章/视频号视频 | [workflows/E-content-output.md](workflows/E-content-output.md) |

### 场景间流转

场景之间不是孤立的，可以自然流转：

```
A(知识探索) → 理解了概念后，想开发 → C(项目开发)
B(人物蒸馏) → 蒸馏了Skill后，想用其风格输出 → E(内容输出) + 蒸馏Skill风格
C(项目开发) → 开发完成后，想输出文章 → E(内容输出)
D(项目解析) → 解析完项目后，想输出文章 → E(内容输出)
E(内容输出) → 输出时发现需要深入理解 → A(知识探索)
```

---

## 输出风格系统

场景E（内容输出）和场景A/B/C/D的最终输出阶段，可以选择输出风格：

| 风格 | 来源 | 适用场景 | 说明 |
|------|------|---------|------|
| **论文风格** | 公众号发布原有 | 知识科普、技术文章 | 专业严谨，五段式结构 |
| **对话风格** | 公众号发布原有 | AI聊天记录整理 | Q&A结构，播客文字版 |
| **蒸馏Skill风格** | 本质蒸馏产出 | 用某人物的思维方式写文章 | 激活examples/中对应人物Skill，以其视角输出 |
| **（预留扩展）** | — | — | 后续可添加：故事风格、教程风格等 |

### 风格选择流程

```
场景执行完成 → 产出原始内容
    ↓
用户选择输出风格（默认：论文风格）
    ↓
如果是「蒸馏Skill风格」→ 激活examples/中对应人物Skill → 以其表达DNA重写
如果是「论文/对话风格」→ 按内容输出规则改写
    ↓
进入排版+配图+推送流程（按输出渠道）
```

---

## 核心概念（速览）

| 概念 | 一句话 | 详见 |
|-----|--------|------|
| **三阶方法论** | 是什么 → 为什么 → 怎么做 | [references/methodology.md](references/methodology.md) |
| **坡度理解** | 点出概念 → 建立联系 → 详细解释 | [references/methodology.md](references/methodology.md) |
| **类-属性-方法-路由** | 项目=类, 模块=属性, 接口=契约, 路由=分发 | [references/methodology.md](references/methodology.md) |
| **单一状态源** | 每个层级有且仅有一个状态源 | [references/design-principles.md](references/design-principles.md) |
| **基础设施四层** | 数据规矩→存储→流转→接口 | [references/design-principles.md](references/design-principles.md) |
| **编码纪律** | 先思后写、简洁优先、精准修改、目标驱动 | [references/design-principles.md](references/design-principles.md) |
| **根因追溯** | 追溯「为什么这么想」而非只记录「怎么想」 | [references/distillation-framework.md](references/distillation-framework.md) |
| **写作风格规范** | 真实、自然、不端着，禁止AI味 | [references/writing-style-guide.md](references/writing-style-guide.md) |
| **微信安全排版** | 只用原生Markdown，禁用:::block | [references/wechat-formatting.md](references/wechat-formatting.md) |
| **配图方案** | SVG→PNG首选，Canvas→GIF动态，AI生图备选 | [references/image-generation.md](references/image-generation.md) |
| **视频生成** | Canvas卡片翻页+Playwright录制+Edge TTS+FFmpeg | [references/video-generation.md](references/video-generation.md) |
| **材料验证** | 引用必须真实，出处必须可查 | [references/fact-checking.md](references/fact-checking.md) |
| **代码阅读辅助** | 三层认知模型 + 分层阅读法 | [references/code-reading-guide.md](references/code-reading-guide.md) |

---

## 核心公式

```
坡度理解：阶段1（点出概念）→ 阶段2（建立联系）→ 阶段3（详细解释）

三阶推导：
  场景A/B/C：是什么 → 为什么 → 怎么做
  场景D：怎么做 ← 为什么 ← 是什么

蒸馏公式：
  认知系统 = Class，心智模型 = 属性，决策启发式 = 方法，场景适配 = 路由，表达DNA = 接口

开发模式：项目开发 = 属性化静态开发 + 方法化动态开发
方法扩展：多场景 = 同核心方法的路由分支
接口本质：接口 = 跨模块协作契约
状态治理：单一状态源 = 项目级全局状态 + 模块级内部状态
基础设施：四层框架 = 数据规矩 → 数据存储 → 数据流转 → 接口层
编码纪律：先思后写 + 简洁优先 + 精准修改 + 目标驱动
视频管线：文章 → 镜头拆分(slides.json) → Canvas渲染+Playwright录制(WebM) + Edge TTS(MP3) → FFmpeg合并(MP4)
文章拉取：公众号API(media_id) / 文章URL抓取 → 正文提取(Markdown) → 镜头拆分 → 视频管线
```

---

## 递归深入协议

当分析完成初始三阶后，对标记为 ✅ 的属性自动执行递归深入：

**递归终止条件**：
1. 当前层级没有"✅ 需深入"的属性
2. 属性已经是基础类型（字符串、数字、布尔值）
3. 模块职责清晰且简单

---

## 已蒸馏实例

所有已蒸馏的实例存放在 `examples/` 目录下，每个子目录包含完整的Skill（SKILL.md + references）。

**扫描方式**：执行时扫描 `examples/` 目录，读取每个子目录下 `SKILL.md` 的 frontmatter（name + description）即可获取实例信息。

**当前实例**：
- `examples/nihaixia.skill/` — 倪海厦
- `examples/socrates.skill/` — 苏格拉底
- `examples/laozi.skill/` — 老子
- `examples/luxun.skill/` — 鲁迅
- `examples/kongzi.skill/` — 孔子
- `examples/einstein.skill/` — 爱因斯坦
- `examples/wangyangming.skill/` — 王阳明
- `examples/zhugeliang.skill/` — 诸葛亮

---

## 文件结构

```
essence-workshop/
├── SKILL.md                              # 本文件（主入口）
├── references/                           # 共用基础文档
│   ├── methodology.md                    # 三阶方法论+坡度理解+类-属性-方法-路由
│   ├── design-principles.md              # 设计原则（单一状态源、四层基础设施、编码纪律）
│   ├── distillation-framework.md         # 蒸馏方法论详解（Agent模板、根因可信度、矛盾处理）
│   ├── skill-template.md                 # 认知操作系统Skill模板
│   ├── writing-style-guide.md            # 写作风格规范
│   ├── wechat-formatting.md              # 微信排版规范
│   ├── image-generation.md               # 配图方案（公众号）
│   ├── video-generation.md               # 视频生成方案（视频号）
│   ├── fact-checking.md                  # 材料验证与引用溯源
│   └── code-reading-guide.md             # 代码阅读辅助指南
├── scripts/                              # 可执行脚本
│   ├── video-template.html               # Canvas卡片翻页HTML模板
│   ├── video_pipeline.py                 # 视频生成管线（录制+TTS+FFmpeg）
│   ├── article_fetcher.py                # 公众号文章拉取（API+URL）
│   ├── article_to_video.py               # 文章转视频（拉取→拆镜头→视频）
│   └── example-slides.json               # 示例镜头JSON
├── workflows/                            # 5个场景工作流
│   ├── A-knowledge-exploration.md        # 知识探索
│   ├── B-person-distillation.md          # 人物蒸馏
│   ├── C-project-development.md          # 新项目开发
│   ├── D-project-analysis.md             # 现有项目解析
│   └── E-content-output.md              # 内容输出（含风格选择系统+多渠道：公众号/视频号）
├── templates/                            # 文档模板
│   ├── knowledge-note.md                 # 知识探索笔记
│   ├── project-essence.md                # 项目本质分析
│   ├── project-architecture.md           # 架构决策
│   ├── project-modules.md                # 模块设计
│   ├── four-layer-design.md              # 四层设计
│   ├── project-analysis.md               # 项目解析
│   └── distillation-skill.md             # 蒸馏Skill模板
├── examples/                             # 蒸馏实例（每个都是自包含的）
│   ├── nihaixia.skill/
│   ├── socrates.skill/
│   ├── laozi.skill/
│   ├── luxun.skill/
│   ├── kongzi.skill/
│   ├── einstein.skill/
│   ├── wangyangming.skill/
│   └── zhugeliang.skill/
└── output/                               # 运行时输出目录
```

---

*本质工坊 · 认知→设计→开发→输出 全链路系统 · 三阶方法论 × 坡度理解 × 类-属性-方法-路由*
