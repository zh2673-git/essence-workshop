# 本质工坊 · Essence Workshop

**[🇨🇳 中文](README.md)** ｜ **[🇬🇧 English](README_EN.md)**

> **认知 → 设计 → 开发 → 输出** 全链路系统

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

## 管线系统（三层架构）

```
元素层(Element) → 管线层(Pipeline) → 平台层(Platform)
   原子素材        平台适配组装        最终交付物
```

### 管线成熟度

| 管线 | 状态 | 说明 |
|------|------|------|
| **公众号** | ✅ 生产可用 | Markdown→微信HTML→封面→图片上传→推送草稿箱，完整闭环 |
| **视频号** | ✅ 生产可用 | Playwright录制+Edge TTS旁白+FFmpeg合并，支持BGM/SFX/多格式 |
| **HTML交互** | 🟡 骨架可用 | 元素层→课程骨架HTML，支持交互模块接入，模块CSS加载待完善 |
| **演示** | 🟡 骨架可用 | 元素层→Reveal.js HTML，Markdown解析为简易正则，复杂格式待增强 |
| **PPT** | 🟡 骨架可用 | 元素层→.pptx，基础标题+内容+图片页，SVG→PNG转换和品牌色待集成 |

### 效果预览

**原则驱动配色**：深色背景 + 高对比文字 + 内容推导强调色（默认黑底白字+金色强调）

### 统一CLI

```bash
# 公众号（生产可用）
python -m scripts.cli publish article.md --auto-cover --author "公众号名"

# 视频号（生产可用）
python -m scripts.cli video output/slides.json --output output/video/

# HTML交互（骨架可用）
python -m scripts.cli html --elements output/elements/ --output output/html/

# 演示（骨架可用）
python -m scripts.cli slides --elements output/elements/ --output output/slides/

# PPT（骨架可用）
python -m scripts.cli pptx --elements output/elements/ --output output/pptx/

# 辅助命令
python -m scripts.cli brand --article output/article.md    # 品牌提取
python -m scripts.cli fetch --url https://mp.weixin.qq.com/s/xxx  # 文章拉取
python -m scripts.cli gif animation.html output.gif        # GIF录制
```

---

## 文件结构

```
essence-workshop/
├── SKILL.md                              # 主入口（路由+核心概念+触发词）
├── references/                           # 共用基础文档
│   ├── methodology.md                    # 三阶方法论+坡度理解+类-属性-方法-路由
│   ├── design-principles.md              # 设计原则
│   ├── distillation-framework.md         # 蒸馏方法论详解
│   ├── skill-template.md                 # 认知操作系统Skill模板
│   ├── writing-style-guide.md            # 写作风格规范
│   ├── wechat-formatting.md              # 微信排版规范
│   ├── pipeline-wechat.md                # 公众号管线规范
│   ├── pipeline-video.md                 # 视频号管线规范
│   ├── pipeline-html.md                  # HTML交互管线规范
│   ├── pipeline-slides.md                # 演示管线规范
│   ├── pipeline-pptx.md                  # PPT管线规范
│   ├── fact-checking.md                  # 材料验证与引用溯源
│   └── code-reading-guide.md             # 代码阅读辅助指南
├── scripts/                              # 可执行脚本（三层架构）
│   ├── cli.py                            # 统一CLI入口
│   ├── elements/                         # 元素层工具
│   │   ├── brand_extractor.py            # 内容分析→强调色推导
│   │   ├── record_gif.py                 # SVG动画→GIF录制
│   │   └── svg_to_png.py                 # SVG→PNG渲染器（Playwright）
│   ├── pipelines/                        # 管线层
│   │   ├── wechat/                       # ✅ 公众号管线（生产可用）
│   │   │   ├── client.py                 # 微信API客户端
│   │   │   ├── converter.py              # Markdown→微信HTML转换器
│   │   │   └── publish.py                # 发布管线（转换+封面+推送）
│   │   ├── video/                        # ✅ 视频号管线（生产可用）
│   │   │   ├── pipeline.py               # 视频生成管线
│   │   │   ├── template.html             # Canvas卡片翻页模板
│   │   │   └── example-slides.json       # 示例镜头JSON
│   │   ├── html/                         # 🟡 HTML交互管线（骨架可用）
│   │   │   └── generator.py              # 元素层→完整交互HTML
│   │   ├── slides/                       # 🟡 演示管线（骨架可用）
│   │   │   └── generator.py              # 元素层→Reveal.js HTML
│   │   └── pptx/                         # 🟡 PPT管线（骨架可用）
│   │       └── generator.py              # 元素层→.pptx文件
│   └── shared/                           # 跨管线共享
│       ├── article_fetcher.py            # 公众号文章拉取
│       └── article_to_video.py           # 文章转视频
├── templates/                            # 文档与输出模板
│   ├── course-skeleton.html              # HTML交互管线课程骨架
│   ├── reveal-template.html              # 演示管线Reveal.js模板
│   ├── brand-spec.json                   # 品牌规格
│   └── ...                               # 文档模板
├── workflows/                            # 5个场景工作流
├── examples/                             # 8个蒸馏实例（自包含）
└── output/                               # 运行时输出目录
    └── elements/                         # 元素层输出（text/graphics/animations/audio/interactions/data）
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

---

## 使用方式

将整个 `essence-workshop/` 目录复制到支持 Skill 的平台即可使用。

SKILL.md 作为主入口，包含完整的路由表和触发词，Agent 会根据用户输入自动分发到对应场景。

---

*本质工坊 · 认知→设计→开发→输出 全链路系统*
