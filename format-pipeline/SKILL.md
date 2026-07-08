---
name: 格式管线
description: |
  格式表达层：将认知引擎产出的结构化认知数据，转换为特定格式的表达产物。
  本层是"方法"层——回答"用什么格式表达"。包含9条格式管线：Markdown、HTML、Notebook、PPT、视频、音频、白板、口播稿、Skill。
  每条管线有独立的风格规范、元素约束和生成脚本，但共享元素层（文本/图形/动画/音频/交互元素）。
  格式产物不绑定平台，可被平台适配层进一步适配到具体平台。
  触发词：当场景需要格式化输出时自动调用；也可由用户指定格式（如「做PPT」「HTML交互」「做notebook」）。
version: 3.0
layer: format
---

# 格式管线 · 格式表达路由

> **v3.0 格式层**：本层是本质工坊的"表达转换器"——把认知产物转为格式产物。
> 格式层 = "方法"层（类-属性-方法-路由中的"方法"），回答"用什么格式表达"。

---

## 架构

```
格式管线（用什么格式表达）
├── markdown/          # Markdown 文档（最通用，跨平台）
├── html/              # HTML 交互文档（富交互）
├── notebook/          # Jupyter Notebook（教学+可执行）
├── ppt/               # PPT 演示（slides 形式）
├── video/             # 视频（MP4，含 video-dsl）
├── audio/             # 音频（播客/朗读）
├── whiteboard/        # 白板动画（与 platform-adapter/whiteboard-recorder 协同）
├── broadcast/         # 口播稿（5镜头结构×白板提示×口语短句）
├── skill/             # Skill 文档（蒸馏产物）
├── references/        # 共享元素规范+写作风格指南
├── scripts/           # 共享脚本（元素处理+CLI+dispatcher）
└── docs/              # 设计文档
```

---

## 输入输出契约

### 输入：认知产物（来自 cognitive-engine）

```yaml
认知产物:
  本质定义: "..."
  一句话点破: "..."
  类归属: "..."
  属性: [...]
  因果链: [...]
  反常识根因: "..."
  方法步骤: [...]
  视角升级: "..."
  视角来源: "general-logic / yijing / ..."
```

### 输出：格式产物（交给 platform-adapter）

格式产物是**未适配平台的通用格式文件**：
- Markdown 管线 → `.md` 文件
- HTML 管线 → 通用 `.html` 文件（未做平台适配）
- Notebook 管线 → `.ipynb` 文件
- PPT 管线 → `.pptx` 文件
- 视频管线 → `.mp4` 文件 + 源文件
- 音频管线 → `.mp3` 文件
- 白板管线 → `.whiteboard.json` 文件
- 口播稿管线 → `broadcast-script.md` 文件
- Skill 管线 → `SKILL.md` 文件

---

## 9 条格式管线

| 管线 | 格式 | 默认风格 | 路径 | 状态 |
|------|------|---------|------|------|
| Markdown | .md | 论文/专栏/故事/教程/观点/对话/蒸馏Skill/连载 | [markdown/](markdown/) | ✅ |
| HTML 交互 | .html | 富交互，含动画/图表 | [html/](html/) | ✅ |
| Notebook | .ipynb | 教学式，可执行 | [notebook/](notebook/) | ✅ |
| PPT | .pptx | 演示式，slides | [ppt/](ppt/) | ✅ |
| 视频 | .mp4 | 视频叙事，含 video-dsl | [video/](video/) | ✅ |
| 音频 | .mp3 | 播客/朗读 | [audio/](audio/) | ✅ |
| 白板 | .whiteboard.json | 白板动画 | [whiteboard/](whiteboard/) | ✅ |
| 口播稿 | broadcast-script.md | 5镜头结构×白板提示 | [broadcast/](broadcast/) | ✅ |
| Skill | SKILL.md | 蒸馏Skill产物 | [skill/](skill/) | ✅ |

---

## 输出风格（跨管线共享）

| 风格 | 说明 | 默认篇幅 |
|------|------|---------|
| 论文风格 | 专业严谨，五段式结构 | 7000-8000字 |
| 专栏风格 | 论文的轻量版，观点+案例 | 3000-5000字 |
| 故事风格 | 用叙事包装知识/案例 | 2500-4500字 |
| 教程/清单风格 | 步骤清晰，直接可用 | 1500-3000字 |
| 观点/时评风格 | 立场鲜明，短小犀利 | 1200-2500字 |
| 对话风格 | Q&A结构，播客文字版 | 不定 |
| 蒸馏Skill风格 | 激活 distillation/output/ 中对应Skill，以其视角输出 | 不定 |
| 连载小说风格 | 章节化叙事，悬念驱动 | 2000-4000字/章 |

风格选择由场景层（scenarios/）决定，格式层只负责按指定风格生成。

---

## 共享元素层

所有管线共享以下元素规范（位于 [references/](references/)）：

- [references/element-spec.md](references/element-spec.md) — 元素规范（文本/图形/动画/音频/交互）
- [references/writing-style-guide.md](references/writing-style-guide.md) — 写作风格指南

> 选题规范已迁移至 [cognitive-engine/general-logic/references/topic-selection.md](../cognitive-engine/general-logic/references/topic-selection.md)（选题是认知方法，非格式转换）

元素层是原子资产，跨管线复用：
```
文本元素 ─┐
图形元素 ─┤
动画元素 ─┼─→ 管线组装 ─→ 格式产物
音频元素 ─┤
交互元素 ─┘
```

---

## 管线选择规则

### 由场景指定
场景层（scenarios/）会指定使用哪条管线：
- 知识探索 → Markdown 管线（默认）
- K12拆解 → HTML 管线（交互式）
- 项目开发 → Markdown 管线（设计文档）+ 代码
- 项目解析 → Markdown 管线（解析文档）
- 内容输出场景 → 用户指定管线
- 连载小说 → Markdown 管线（章节）+ 视频管线（可选）

### 由用户指定
用户可直接指定：「做PPT」「HTML交互」「做notebook」「做视频」

### 管线切换
同一认知产物可走不同管线（元素层复用）：认知产物 → 管线A → 管线B，无需重新认知。

---

## 共享脚本

- [scripts/cli.py](scripts/cli.py) — 命令行入口
- [scripts/dispatcher.py](scripts/dispatcher.py) — 管线分发器
- [scripts/elements/](scripts/elements/) — 元素处理脚本（brand_extractor, svg_to_png, record_gif）
- [scripts/shared/](scripts/shared/) — 共享工具包（保留 `__init__.py`；article_fetcher / article_to_video 已迁移至 `platform-adapter/wechat/scripts/`）

---

## 扩展新管线

新增格式管线只需在 `format-pipeline/` 下创建新子目录，包含：
- `SKILL.md`（管线规范）
- `scripts/`（生成脚本，可选）
- `references/`（格式规范，可选）
- 实现"认知产物 → 格式产物"的转换即可。

---

*格式管线 · v3.0 · 认知产物 → 格式产物 · 9条管线 × 8种风格*
