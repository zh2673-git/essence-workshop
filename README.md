# 本质工坊 · Essence Workshop

> **认知 → 设计 → 开发 → 输出** 全链路系统

[English](README_EN.md)

融合「本质探索」「本质蒸馏」「公众号发布」三合一的认知工坊。基于**三阶方法论**（是什么-为什么-怎么做）和**类-属性-方法-路由**模型，融合**坡度理解**渐进式认知方法。

---

## 核心能力

```
输入 → 路由分发 → 场景执行 → 输出风格选择 → 最终产出
```

### 5大场景

| 场景 | 触发词 | 核心目标 | 输出 |
|------|--------|---------|------|
| **A: 知识探索** | 「探索XX」「理解XX」「XX是什么」 | 从零构建知识体系 | 结构化知识笔记 |
| **B: 人物蒸馏** | 「蒸馏XX」「提炼XX思维」「造skill」 | 蒸馏认知操作系统 | 认知操作系统Skill |
| **C: 项目开发** | 「开发XX」「设计XX系统」「构建XX」 | 从零构建系统 | 设计文档+可运行代码 |
| **D: 项目解析** | 「分析XX项目」「拆解XX代码」 | 理解已有系统 | 项目理解文档 |
| **E: 内容输出** | 「写公众号」「发布文章」「输出文章」 | 多渠道内容发布 | 公众号文章/其他渠道 |

### 输出风格系统

场景执行完成后，可选择输出风格：

| 风格 | 适用场景 | 说明 |
|------|---------|------|
| **论文风格**（默认） | 知识科普、技术文章 | 专业严谨，五段式结构 |
| **对话风格** | AI聊天记录整理 | Q&A结构，播客文字版 |
| **蒸馏Skill风格** | 用某人物的思维方式写文章 | 激活examples/中对应人物Skill，以其视角输出 |

### 已蒸馏实例

8个人物/主题的认知操作系统已就绪：

- 🏥 `nihaixia.skill` — 倪海厦（中医经方）
- ❓ `socrates.skill` — 苏格拉底（诘问辩证）
- ☯️ `laozi.skill` — 老子（道法自然）
- ✒️ `luxun.skill` — 鲁迅（国民性解剖）
- 📜 `kongzi.skill` — 孔子（仁礼中庸）
- ⚛️ `einstein.skill` — 爱因斯坦（相对论直觉）
- 💡 `wangyangming.skill` — 王阳明（心学致良知）
- 🔭 `zhugeliang.skill` — 诸葛亮（审时度势）

---

## 文件结构

```
essence-workshop/
├── SKILL.md                              # 主入口（~211行：路由+核心概念+触发词）
├── references/                           # 共用基础文档
│   ├── methodology.md                    # 三阶方法论+坡度理解+类-属性-方法-路由
│   ├── design-principles.md              # 设计原则
│   ├── distillation-framework.md         # 蒸馏方法论详解
│   ├── skill-template.md                 # 认知操作系统Skill模板
│   ├── writing-style-guide.md            # 写作风格规范
│   ├── wechat-formatting.md              # 微信排版规范
│   ├── image-generation.md               # 配图方案
│   ├── fact-checking.md                  # 材料验证与引用溯源
│   └── code-reading-guide.md             # 代码阅读辅助指南
├── workflows/                            # 5个场景工作流
│   ├── A-knowledge-exploration.md        # 知识探索
│   ├── B-person-distillation.md          # 人物蒸馏
│   ├── C-project-development.md          # 新项目开发
│   ├── D-project-analysis.md             # 现有项目解析
│   └── E-content-output.md               # 内容输出（含风格选择系统+多渠道）
├── scripts/                              # 可执行脚本
│   ├── wechat_client.py                  # 微信API客户端（token+上传+草稿+文章拉取）
│   ├── wechat_converter.py               # Markdown→微信HTML转换器（3主题+内联样式）
│   ├── wechat_publish.py                 # 公众号发布管线（转换+封面+推送草稿）
│   ├── article_fetcher.py                # 公众号文章拉取（API+URL）
│   ├── video-template.html               # Canvas卡片翻页HTML模板
│   ├── video_pipeline.py                 # 视频生成管线（录制+TTS+FFmpeg）
│   ├── article_to_video.py               # 文章转视频（拉取→拆镜头→视频）
│   └── example-slides.json               # 示例镜头JSON
├── templates/                            # 文档模板
├── examples/                             # 8个蒸馏实例（自包含）
└── output/                               # 运行时输出目录
```

---

## 核心方法论

### 三阶方法论

```
场景A/B/C：是什么 → 为什么 → 怎么做    （正向推导）
场景D：     怎么做 ← 为什么 ← 是什么    （逆向分析）
```

### 坡度理解

```
阶段1（点出概念）→ 阶段2（建立联系）→ 阶段3（详细解释）
```

### 类-属性-方法-路由模型

```
项目 = 类，模块 = 属性，接口 = 契约，路由 = 方法分发
```

---

## 与其他仓库的关系

本仓库整合了以下三个仓库的核心能力，现已完全自包含，不依赖外部项目：

| 源仓库 | 角色 | 贡献内容 |
|--------|------|---------|
| [essence-programming](https://github.com/zh2673-git/essence-programming) | 认知与设计引擎 | 三阶方法论、设计原则、知识探索、项目开发、项目解析 |
| [essence-distillation-skill](https://github.com/zh2673-git/essence-distillation-skill) | 认知蒸馏引擎 | 7Agent调研、根因追溯、人物蒸馏、8个实例 |
| [md2wechat-py](https://github.com/zh2673-git/md2wechat-py) | 内容输出引擎 | 写作风格、微信排版、配图方案、公众号推送（已内化为自包含模块） |

公众号相关功能已内化为 `scripts/` 下的三个自包含模块（`wechat_client.py` / `wechat_converter.py` / `wechat_publish.py`），无需安装 `wechat-pub` 或 `md2wechat-py`。

---

## 使用方式

将整个 `essence-workshop/` 目录复制到支持 Skill 的平台即可使用。

SKILL.md 作为主入口，包含完整的路由表和触发词，Agent 会根据用户输入自动分发到对应场景。

---

*本质工坊 · 认知→设计→开发→输出 全链路系统*
