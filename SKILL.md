---
name: 本质工坊
description: |
  认知→元素→管线→平台 富媒体交付系统。
  基于三阶方法论（是什么-为什么-怎么做）和类-属性-方法-路由模型，融合坡度理解渐进式认知方法。
  支持5大场景：知识探索、人物蒸馏、项目开发、项目解析、内容输出。
  三层交付架构：元素层（原子资产）→ 管线层（按平台约束组装）→ 平台层（交付成品）。
  5条管线：公众号管线、视频号管线、HTML交互管线、演示管线、PPT管线。
  输出风格支持：论文风格、蒸馏Skill风格、对话风格，以及预留扩展。
  触发词：「探索XX」「蒸馏XX」「开发XX」「分析XX」「写公众号」「发布文章」「做视频」「视频号」「做PPT」「HTML交互」。
  模糊需求也触发：「我想提升决策质量」「帮我理解XX」「设计一个XX系统」。
---

# 本质工坊 · 认知→元素→管线→平台 富媒体交付系统

> **核心原则**：坡度理解 —— 先点出概念 → 建立联系 → 再详细解释
>
> **设计思想**：项目 = 类，模块 = 属性，接口 = 契约，路由 = 方法分发
>
> **蒸馏公式**：三阶方法论（是什么→为什么→怎么做）× 坡度理解 × 类-属性-方法-路由
>
> **交付架构**：元素层（原子资产）→ 管线层（按平台约束组装）→ 平台层（交付成品）

---

## ⚠️ Agent 执行纪律（必须遵守）

在执行任何操作前，Agent 必须遵守以下硬性约束：

1. **先读规范再操作**：执行任何生成/转换/推送操作前，必须先检查 `references/` 中对应规范文件的硬性约束（标记为 ⚠️ 的规则），违反约束的操作不要执行
2. **约束语言含义**：`必须` = 无条件遵守；`禁止` = 绝对不能做；`优先` = 默认选择但允许降级；`建议` = 可选
3. **生成后自检**：每次生成文件（PNG/GIF/MP4/HTML）后，必须执行对应的质量自检步骤（见各 references/ 文件中的"质量自检"章节），不通过则修复后重新生成
4. **Windows 环境**：PowerShell 不支持 `&&` 连接命令，用 `;` 替代，或拆分为单独的命令调用

---

## 系统架构

```
┌──────────────────────────────────────────────────────────────────────┐
│                           本质工坊 v2                                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   输入 → 路由分发 → 场景执行 → 风格选择 → 管线选择 → 平台交付      │
│                                                                       │
│   ┌──────────┐                                                       │
│   │  路由表  │                                                       │
│   ├──────────┤                                                       │
│   │ A:探索   │ → 知识探索 → 结构化知识笔记                          │
│   │ B:蒸馏   │ → 人物蒸馏 → 认知操作系统Skill                       │
│   │ C:开发   │ → 项目开发 → 设计文档+可运行代码                     │
│   │ D:解析   │ → 项目解析 → 项目理解文档                             │
│   │ E:输出   │ → 内容输出 → 元素层 → 管线选择 → 平台交付            │
│   └──────────┘                                                       │
│                                                                       │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │              三层交付架构                                     │    │
│   ├─────────────────────────────────────────────────────────────┤    │
│   │                                                              │    │
│   │  元素层（Element）—— 原子资产，跨管线共享                     │    │
│   │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │    │
│   │  │文本元素│ │图形元素│ │动画元素│ │音频元素│ │交互元素│   │    │
│   │  │Markdown│ │SVG图谱 │ │SVG动画 │ │TTS旁白 │ │拖拽组件│   │    │
│   │  │标题段落│ │SVG流程 │ │Canvas帧│ │BGM音效 │ │折叠面板│   │    │
│   │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘   │    │
│   │                                                              │    │
│   │  管线层（Pipeline）—— 从元素层读取，按平台约束组装             │    │
│   │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │    │
│   │  │公众号  │ │视频号  │ │HTML交互│ │ 演示   │ │  PPT   │   │    │
│   │  │管线    │ │管线    │ │管线    │ │管线    │ │管线    │   │    │
│   │  └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘   │    │
│   │      ↓          ↓          ↓          ↓          ↓         │    │
│   │  平台层（Platform）—— 交付成品                                │    │
│   │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │    │
│   │  │微信公众号│ │视频号  │ │浏览器  │ │Reveal  │ │PPT/WPS │   │    │
│   │  │受限HTML │ │MP4     │ │HTML交互│ │.js演示 │ │.pptx   │   │    │
│   │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘   │    │
│   │                                                              │    │
│   └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│   ┌──────────────────────────────────────────┐                       │
│   │           输出风格系统                    │                       │
│   ├──────────────────────────────────────────┤                       │
│   │ 论文风格  │ 蒸馏Skill风格 │ 对话风格 │ ... │                       │
│   └──────────────────────────────────────────┘                       │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 三层交付架构

### 核心原则

- **元素是原子资产**：自包含、可寻址、可复用、跨管线共享
- **管线是转换器**：从元素层读取 → 按平台约束组装 → 输出成品
- **平台是约束集**：每个平台有各自的格式要求和能力限制
- **新平台 = 新管线**：元素层不变，只需编写新管线

### 管线与元素消费关系

| 管线 | 读取元素 | 输出 | 核心转换 |
|------|---------|------|---------|
| **公众号管线** | 文本+图形+动画 | 微信受限HTML | SVG→PNG内联，动画→GIF，文本→微信排版 |
| **视频号管线** | 文本+图形+动画+音频 | MP4视频 | SVG→Canvas帧，文本→卡片，音频→TTS+BGM |
| **HTML交互管线** | 文本+图形+动画+交互+数据 | 完整HTML | SVG直接嵌入，交互模块接入，保留全部能力 |
| **演示管线** | 文本+图形+动画 | Reveal.js HTML | 文本→幻灯片section，图形嵌入幻灯片 |
| **PPT管线** | 文本+图形+动画 | .pptx文件 | SVG→PNG，文本→幻灯片，动画→关键帧截图 |

### 管线选择流程

```
场景执行完成 → 产出原始内容 → 生成元素层资产
    ↓
用户选择管线（默认：根据触发词自动选择）
    ↓
公众号触发词 → 公众号管线
视频号触发词 → 视频号管线
HTML交互触发词 → HTML交互管线
演示触发词 → 演示管线
PPT触发词 → PPT管线
    ↓
管线从元素层读取 → 按平台约束组装 → 输出成品
```

---

## 5大场景路由

| 路由 | 触发词 | 核心目标 | 输出 | 详见 |
|-----|--------|---------|------|------|
| **A: 知识探索** | 「探索XX」「理解XX」「XX是什么」 | 从零构建知识体系 | 结构化知识笔记 | [workflows/A-knowledge-exploration.md](workflows/A-knowledge-exploration.md) |
| **B: 人物蒸馏** | 「蒸馏XX」「提炼XX思维」「造skill」 | 蒸馏认知操作系统 | 认知操作系统Skill | [workflows/B-person-distillation.md](workflows/B-person-distillation.md) |
| **C: 项目开发** | 「开发XX」「设计XX系统」「构建XX」 | 从零构建系统 | 设计文档+可运行代码 | [workflows/C-project-development.md](workflows/C-project-development.md) |
| **D: 项目解析** | 「分析XX项目」「拆解XX代码」 | 理解已有系统 | 项目理解文档 | [workflows/D-project-analysis.md](workflows/D-project-analysis.md) |
| **E: 内容输出** | 「写公众号」「做视频」「HTML交互」「做PPT」 | 多管线内容发布 | 公众号/视频号/HTML/演示/PPT | [workflows/E-content-output.md](workflows/E-content-output.md) |

### 场景间流转

场景之间不是孤立的，可以自然流转：

```
A(知识探索) → 理解了概念后，想开发 → C(项目开发)
B(人物蒸馏) → 蒸馏了Skill后，想用其风格输出 → E(内容输出) + 蒸馏Skill风格
C(项目开发) → 开发完成后，想输出文章 → E(内容输出)
D(项目解析) → 解析完项目后，想输出文章 → E(内容输出)
E(内容输出) → 输出时发现需要深入理解 → A(知识探索)
E(内容输出) → 同一内容可走不同管线 → 管线切换（元素层复用）
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
生成元素层资产 → 进入管线选择 → 平台交付
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
| **元素层规范** | 原子资产定义：文本/图形/动画/音频/交互/数据 | [references/element-spec.md](references/element-spec.md) |
| **公众号管线** | SVG→PNG，动画→GIF，文本→微信排版 | [references/pipeline-wechat.md](references/pipeline-wechat.md) |
| **视频号管线** | SVG→Canvas帧，文本→卡片，TTS+BGM→MP4 | [references/pipeline-video.md](references/pipeline-video.md) |
| **HTML交互管线** | SVG直接嵌入，交互模块接入，保留全部能力 | [references/pipeline-html.md](references/pipeline-html.md) |
| **演示管线** | 文本→幻灯片section，Reveal.js输出 | [references/pipeline-slides.md](references/pipeline-slides.md) |
| **PPT管线** | SVG→PNG，文本→幻灯片，.pptx输出 | [references/pipeline-pptx.md](references/pipeline-pptx.md) |
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

三层架构映射：
  元素层 = 属性（原子资产）
  管线层 = 方法（按平台约束组装）
  平台层 = 路由（交付分发）

开发模式：项目开发 = 属性化静态开发 + 方法化动态开发
方法扩展：多场景 = 同核心方法的路由分支
接口本质：接口 = 跨模块协作契约
状态治理：单一状态源 = 项目级全局状态 + 模块级内部状态
基础设施：四层框架 = 数据规矩 → 数据存储 → 数据流转 → 接口层
编码纪律：先思后写 + 简洁优先 + 精准修改 + 目标驱动

管线公式：
  公众号管线：元素层 → SVG→PNG + 动画→GIF + 文本→微信HTML → 推送草稿箱
  视频号管线：元素层 → SVG→Canvas帧 + 文本→卡片 + TTS+BGM → FFmpeg→MP4
  HTML交互管线：元素层 → SVG直接嵌入 + 交互模块接入 → 完整HTML
  演示管线：元素层 → 文本→section + 图形嵌入 → Reveal.js HTML
  PPT管线：元素层 → SVG→PNG + 文本→幻灯片 → python-pptx/PptxGenJS → .pptx
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
│   ├── element-spec.md                   # 元素层规范（原子资产定义）
│   ├── pipeline-wechat.md                # 公众号管线规范
│   ├── pipeline-video.md                 # 视频号管线规范
│   ├── pipeline-html.md                  # HTML交互管线规范
│   ├── pipeline-slides.md                # 演示管线规范
│   ├── pipeline-pptx.md                  # PPT管线规范
│   ├── html-output-guide.md              # HTML交互输出规范
│   ├── fact-checking.md                  # 材料验证与引用溯源
│   └── code-reading-guide.md             # 代码阅读辅助指南
├── modules/                              # 标准交互模块（HTML交互管线使用）
│   ├── slope-navigator/                  # 坡度导航器
│   ├── three-stage-progress/             # 三阶进度条
│   ├── knowledge-graph/                  # 知识图谱浏览器
│   ├── card-flip/                        # 卡片翻转
│   └── comparison-table/                 # 对比表格
├── scripts/                              # 可执行脚本（三层架构）
│   ├── cli.py                            # 统一CLI入口
│   ├── elements/                         # 元素层工具
│   │   ├── record_gif.py                 # SVG动画→GIF录制
│   │   └── brand_extractor.py            # 品牌素材提取→brand-spec.json
│   ├── pipelines/                        # 管线层（按管线分目录）
│   │   ├── wechat/                       # 公众号管线
│   │   │   ├── client.py                 # 微信API客户端（token+上传+草稿+文章拉取）
│   │   │   ├── converter.py              # Markdown→微信HTML转换器（3主题+内联样式）
│   │   │   └── publish.py                # 公众号发布管线（转换+封面+推送草稿）
│   │   ├── video/                        # 视频号管线
│   │   │   ├── pipeline.py               # 视频生成管线（录制+TTS+FFmpeg）
│   │   │   ├── template.html             # Canvas卡片翻页HTML模板
│   │   │   └── example-slides.json       # 示例镜头JSON
│   │   ├── html/                         # HTML交互管线
│   │   │   └── generator.py              # 元素层→完整交互HTML
│   │   ├── slides/                       # 演示管线
│   │   │   └── generator.py              # 元素层→Reveal.js HTML
│   │   └── pptx/                         # PPT管线
│   │       └── generator.py              # 元素层→.pptx文件
│   └── shared/                           # 跨管线共享
│       ├── article_fetcher.py            # 公众号文章拉取（API+URL）
│       └── article_to_video.py           # 文章转视频（拉取→拆镜头→视频）
├── workflows/                            # 5个场景工作流
│   ├── A-knowledge-exploration.md        # 知识探索
│   ├── B-person-distillation.md          # 人物蒸馏
│   ├── C-project-development.md          # 新项目开发
│   ├── D-project-analysis.md             # 现有项目解析
│   └── E-content-output.md              # 内容输出（含风格选择+管线选择+5条管线）
├── templates/                            # 文档模板
│   ├── knowledge-note.md                 # 知识探索笔记
│   ├── project-essence.md                # 项目本质分析
│   ├── project-architecture.md           # 架构决策
│   ├── project-modules.md                # 模块设计
│   ├── four-layer-design.md              # 四层设计
│   ├── project-analysis.md               # 项目解析
│   ├── distillation-skill.md             # 蒸馏Skill模板
│   ├── brand-spec.json                   # 品牌规格
│   ├── course-skeleton.html              # HTML课程骨架模板
│   └── reveal-template.html              # Reveal.js演示模板
├── examples/                             # 蒸馏实例（每个都是自包含的）
│   ├── nihaixia.skill/
│   ├── socrates.skill/
│   ├── laozi.skill/
│   ├── luxun.skill/
│   ├── kongzi.skill/
│   ├── einstein.skill/
│   ├── wangyangming.skill/
│   └── zhugeliang.skill/
├── docs/                                 # 设计文档
│   └── html-rich-media-upgrade-plan.md   # 富媒体升级方案
└── output/                               # 运行时输出目录（按管线分子目录）
    ├── elements/                         # 元素层输出（原子资产）
    ├── wechat/                           # 公众号管线输出
    ├── video/                            # 视频号管线输出
    ├── html/                             # HTML交互管线输出
    ├── slides/                           # 演示管线输出
    └── pptx/                             # PPT管线输出
```

---

*本质工坊 · 认知→元素→管线→平台 富媒体交付系统 · 三阶方法论 × 坡度理解 × 类-属性-方法-路由*
