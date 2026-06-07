# Essence Workshop

**[🇨🇳 中文](README.md)** ｜ **[🇬🇧 English](README_EN.md)**

> **Cognition → Design → Development → Output** — A full-pipeline system

A unified workshop integrating **Essence Exploration**, **Essence Distillation**, and **WeChat Publishing**. Built on the **Three-Stage Methodology** (What → Why → How) and the **Class-Attribute-Method-Route** model, with **Gradient Understanding** for progressive cognition.

[中文文档](README.md)

---

## Core Capabilities

```
Input → Route Dispatch → Scenario Execution → Style Selection → Final Output
```

### 5 Scenarios

| Scenario | Trigger | Goal | Output |
|----------|---------|------|--------|
| **A: Knowledge Exploration** | "Explore X", "Understand X" | Build knowledge from scratch | Structured knowledge notes |
| **B: Person Distillation** | "Distill X", "Extract X's thinking" | Distill cognitive operating system | Cognitive OS Skill |
| **C: Project Development** | "Develop X", "Design X system" | Build system from scratch | Design docs + runnable code |
| **D: Project Analysis** | "Analyze X project", "Decompose X code" | Understand existing system | Project understanding docs |
| **E: Content Output** | "Write article", "Publish", "Make video" | Multi-channel publishing | WeChat article / Video |

### Output Style System

After scenario execution, choose an output style:

| Style | Use Case | Description |
|-------|----------|-------------|
| **Academic** (default) | Knowledge, tech articles | Professional, five-paragraph structure |
| **Dialogue** | AI chat records | Q&A structure, podcast transcript style |
| **Distilled Skill** | Write in someone's mindset | Activate person Skill from `examples/`, output in their voice |

### Distilled Instances

8 cognitive operating systems ready to use:

- 🏥 `nihaixia.skill` — Ni Haixia (TCM classical formulas)
- ❓ `socrates.skill` — Socrates (Socratic dialectic)
- ☯️ `laozi.skill` — Laozi (Dao follows nature)
- ✒️ `luxun.skill` — Lu Xun (National character anatomy)
- 📜 `kongzi.skill` — Confucius (Ren, Li, Zhongyong)
- ⚛️ `einstein.skill` — Einstein (Relativity intuition)
- 💡 `wangyangming.skill` — Wang Yangming (XinXue, Zhi Liangzhi)
- 🔭 `zhugeliang.skill` — Zhuge Liang (Strategic assessment)

---

## File Structure

```
essence-workshop/
├── SKILL.md                              # Main entry (routing + core concepts + triggers)
├── references/                           # Shared reference docs
│   ├── methodology.md                    # Three-Stage Methodology + Gradient Understanding
│   ├── design-principles.md              # Design principles
│   ├── distillation-framework.md         # Distillation methodology
│   ├── skill-template.md                 # Cognitive OS Skill template
│   ├── writing-style-guide.md            # Writing style guide
│   ├── wechat-formatting.md              # WeChat formatting rules
│   ├── pipeline-wechat.md                # WeChat pipeline spec
│   ├── pipeline-video.md                 # Video pipeline spec
│   ├── pipeline-html.md                  # HTML pipeline spec
│   ├── pipeline-slides.md                # Slides pipeline spec
│   ├── pipeline-pptx.md                  # PPT pipeline spec
│   ├── fact-checking.md                  # Fact checking & citation
│   └── code-reading-guide.md             # Code reading guide
├── scripts/                              # Executable scripts
│   ├── cli.py                            # Unified CLI entry
│   ├── elements/                         # Element layer tools
│   │   ├── brand_extractor.py            # Content analysis → accent color derivation
│   │   ├── record_gif.py                 # SVG animation → GIF recording
│   │   └── svg_to_png.py                 # SVG → PNG renderer (Playwright)
│   ├── pipelines/                        # Pipeline layer
│   │   ├── wechat/                       # ✅ WeChat pipeline (production)
│   │   │   ├── client.py                 # WeChat API client
│   │   │   ├── converter.py              # Markdown → WeChat HTML converter
│   │   │   └── publish.py                # Publishing pipeline
│   │   ├── video/                        # ✅ Video pipeline (production)
│   │   │   ├── pipeline.py               # Video generation pipeline
│   │   │   └── template.html             # Canvas card-flip template
│   │   ├── html/                         # 🟡 HTML pipeline (skeleton)
│   │   │   └── generator.py              # Element → interactive HTML
│   │   ├── slides/                       # 🟡 Slides pipeline (skeleton)
│   │   │   └── generator.py              # Element → Reveal.js HTML
│   │   └── pptx/                         # 🟡 PPT pipeline (skeleton)
│   │       └── generator.py              # Element → .pptx file
│   └── shared/                           # Cross-pipeline shared
│       ├── article_fetcher.py            # WeChat article fetcher
│       └── article_to_video.py           # Article to video
├── workflows/                            # 5 scenario workflows
│   ├── A-knowledge-exploration.md
│   ├── B-person-distillation.md
│   ├── C-project-development.md
│   ├── D-project-analysis.md
│   └── E-content-output.md
├── templates/                            # Document templates
├── examples/                             # 8 distilled instances (self-contained)
└── output/                               # Runtime output directory
```

---

## Core Methodology

### Three-Stage Methodology

```
Scenario A/B/C: What → Why → How       (Forward reasoning)
Scenario D:     How ← Why ← What       (Reverse analysis)
```

### Gradient Understanding

```
Stage 1 (Point out concept) → Stage 2 (Build connection) → Stage 3 (Explain in detail)
```

### Class-Attribute-Method-Route Model

```
Project = Class, Module = Attribute, Interface = Contract, Route = Method dispatch
```

---

## Publishing Pipeline

### WeChat Official Account (Article)

Self-contained modules — no external `wechat-pub` dependency:

```bash
# One-click publish: Markdown → HTML + Cover + Push draft
python -m scripts.cli publish article.md --auto-cover --author "Your Name"

# Fetch articles from your account
python -m scripts.cli fetch --list --count 10
python -m scripts.cli fetch --media-id XXXXX --save output/article.md
```

### WeChat Video Account (Short Video)

Canvas card-flip style + Playwright recording + Edge TTS narration + FFmpeg merging:

```bash
# Article to video
python -m scripts.shared.article_to_video --url "https://mp.weixin.qq.com/s/xxx" --output output/video/
```

---

## Relationship with Other Repos

This repo integrates core capabilities from three source repos and is now fully self-contained:

| Source Repo | Role | Contribution |
|-------------|------|-------------|
| [essence-programming](https://github.com/zh2673-git/essence-programming) | Cognition & design engine | Three-Stage Methodology, design principles, knowledge exploration, project dev/analysis |
| [essence-distillation-skill](https://github.com/zh2673-git/essence-distillation-skill) | Cognitive distillation engine | 7-Agent research, root cause tracing, person distillation, 8 instances |
| [md2wechat-py](https://github.com/zh2673-git/md2wechat-py) | Content output engine | Writing style, WeChat formatting, image generation, publishing (internalized as self-contained modules) |

WeChat-related features have been internalized as self-contained modules under `scripts/pipelines/wechat/` (`client.py` / `converter.py` / `publish.py`). No need to install `wechat-pub` or `md2wechat-py`.

---

## Usage

Copy the entire `essence-workshop/` directory to a Skill-compatible platform.

`SKILL.md` serves as the main entry point, containing the complete routing table and trigger words. The Agent automatically dispatches user input to the corresponding scenario.

---

*Essence Workshop · Cognition → Design → Development → Output*
