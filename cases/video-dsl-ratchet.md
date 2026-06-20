# 实战案例：Video DSL 从零到完整视频管线

> 本案例展示了如何用本质工坊的场景C2（迭代开发/Ratchet Loop）+ 场景E（内容输出），从零设计并实现一套 Video DSL 视频生成管线。
> 6轮迭代，0次回退，完成 Phase 1-3，最终产出带 TTS 旁白的 9 秒 MP4 与 GIF 预览。

## 相关文档

原始设计方案、迭代计划、测试报告、API 参考与最终验收已归档到本案例目录：

- 原始方案：[`video-dsl/00-essence-video-generation-plan.md`](video-dsl/00-essence-video-generation-plan.md)、[`video-dsl/04-video-core-四层设计.md`](video-dsl/04-video-core-四层设计.md) 等
- 迭代计划：[`video-dsl/plan-v1.md`](video-dsl/plan-v1.md) ~ [`plan-v6.md`](video-dsl/plan-v6.md)
- 测试报告：[`video-dsl/test-report-v1.md`](video-dsl/test-report-v1.md) ~ [`test-report-v6.md`](video-dsl/test-report-v6.md)
- API 参考：[`video-dsl/api-reference.md`](video-dsl/api-reference.md)
- 最终验收：[`video-dsl/final-acceptance.md`](video-dsl/final-acceptance.md)
- 迭代记录：[`video-dsl/results.tsv`](video-dsl/results.tsv)

代码实现位于 [`content-output/video-dsl/`](../content-output/video-dsl/)。

## 项目背景

### 是什么

本质工坊的内容输出层已有公众号、PPT、Notebook 等管线，但缺少**视频**这一高传播力形式。现有视频脚本依赖 Canvas 录制 HTML，对帧级动画、音画同步控制力弱。

### 核心矛盾

- HTML 录制适合“静态页面翻页”，不适合“精确到帧的动画”。
- Agent 生成视频代码时，容易写出 CSS animation / requestAnimationFrame 等不可渲染的代码。
- 视频需要音频（TTS 旁白、BGM），但旧管线没有统一音频合成路径。

### 策略

**Video DSL**：用一套狭窄、确定的 TypeScript/React API，让 Agent 生成可静态渲染为逐帧 PNG 的视频程序，再由 FFmpeg 合成 MP4/GIF。

## 验证合同

| 维度 | 内容 |
|------|------|
| **P（前置）** | Node.js 18+、TypeScript、Playwright、FFmpeg、edge-tts |
| **Q（后置）** | video-core 类型通过、renderer 输出有效 MP4、generator 拦截非法代码、pipeline 自动路由、TTS 时长匹配、GIF 输出成功 |
| **I（不变量）** | 现有 HTML 录制/公众号管线不被破坏、不修改用户源码、Prompt 契约向后兼容 |

## 架构设计

```
content-output/video-dsl/
├── packages/
│   ├── video-core/        # 元素层：Hooks + 基础组件 + 动画组件库
│   ├── video-renderer/    # 管线层：Vite 打包 + Playwright 截图 + FFmpeg 合成
│   └── video-generator/   # 管线层：Prompt 模板 + 代码静态校验
├── examples/negative-numbers/  # Demo：负数是什么
├── scripts/
│   └── generate_audio.py  # TTS/BGM 生成
└── tests/                 # 三维验证测试
```

## 迭代记录

详见 [`video-dsl/results.tsv`](video-dsl/results.tsv) 与 [`video-dsl/plan-v1.md`](video-dsl/plan-v1.md) ~ [`plan-v6.md`](video-dsl/plan-v6.md) / [`test-report-v1.md`](video-dsl/test-report-v1.md) ~ [`test-report-v6.md`](video-dsl/test-report-v6.md)。

## 迭代进度总览

| 版本 | 目标 | 关键改动 | 验证结果 |
|------|------|---------|---------|
| v1 | Phase 1 MVP | video-core / renderer / generator / router / Demo | 跑通，但画面为空 |
| v2 | 修复空白画面 | 模块级 `__essence_setFrame`、新增 `useSequenceTime` | 标题与电梯场景可见 |
| v3 | Phase 2 音频 | edge-tts、BGM 混合、FFmpeg 音画合成 | MP4 含 AAC 音轨 |
| v4 | CLI 集成 | `pipeline.py` + `cli.py` DSL 入口 | 统一 CLI 可用 |
| v5 | Phase 3 组件库 | FadeIn/FlyIn/Counter/Timeline/Compare | Demo 使用组件库 |
| v6 | GIF/质量 | `--format gif`、`--quality draft/medium/high` | GIF 输出成功 |

## 6轮迭代实录

### v1: Phase 1 MVP — 管线跑通

**改动**：
- 实现 `video-core`：Composition、Sequence、AbsoluteFill、interpolate、media 组件。
- 实现 `video-renderer`：Vite 打包 + Playwright 截图 + FFmpeg 合成。
- 实现 `video-generator`：Prompt 模板 + 静态校验。
- 实现 Python `router.py`、`dsl_video_pipeline.py`。
- 创建 `negative-numbers` Demo。

**关键发现**：
- npm workspaces 未提升 `react`，需 alias 到 `video-core/node_modules`。
- 环境无 Playwright Chromium，通过 `chromium.launch({ channel: 'chrome' })` fallback 到系统 Chrome。
- 用 `imageio_ffmpeg` 定位 ffmpeg 二进制。

**Ratchet决策**：P✅ Q✅（类型/渲染/校验通过） I✅ → **保留，但画面为空需修复**

---

### v2: 修复空白画面

**改动**：
- `main.tsx` 中将 `__essence_setFrame` / `__essence_subscribe` 提升到模块级，避免 Composition `useEffect` 订阅时全局函数未创建。
- 新增 `useSequenceTime()` Hook，返回 Sequence 内相对帧。
- Demo 的 ElevatorScene 改用相对帧计算动画。

**关键发现**：
- v1 中 Composition 的 useEffect 先执行，App 的 useEffect 后执行，导致订阅丢失。
- 用 PIL 采样帧像素亮度 bbox 验证：v1 的文本区域面积为 0，v2 出现可见像素块。

**Ratchet决策**：P✅ Q✅（画面可见） I✅ → **保留**

---

### v3: TTS/BGM 与音画合成

**改动**：
- 新增 `scripts/generate_audio.py`：按 `spec.json` 的 `sections[].narration` 生成 edge-tts 音频，拼接并 pad 到总时长，可选 BGM 混合。
- `video-renderer` 支持 `--audio` / `--bgm`，FFmpeg 阶段合并音轨。
- `dsl_video_pipeline.py` 自动检测同目录 `spec.json` 并生成音频。

**关键发现**：
- edge-tts 输出 MP3，直接用 AAC muxer 会失败；拼接用 `.mp3`，最终混码为 `.m4a`。
- Windows `os.rename` 目标存在时报错，需先删除。

**Ratchet决策**：P✅ Q✅（audio.m4a 9.00s，final.mp4 含 AAC） I✅ → **保留**

---

### v4: 统一 CLI 与 Router 集成

**改动**：
- 创建 `content-output/scripts/pipelines/video/pipeline.py` 作为视频统一入口。
- 更新 `content-output/scripts/cli.py`，在 docstring 和描述中体现 DSL 用法。
- 透传 `--format`、`--quality`、`--bgm`。

**关键发现**：
- `cli.py` 通过 `args.rest` 透传未知参数，`pipeline.py` 已能接收 `--pipeline dsl`。

**Ratchet决策**：P✅ Q✅（CLI 生成含音频 MP4） I✅ → **保留**

---

### v5: 动画组件库

**改动**：
- `video-core/src/components/` 新增 FadeIn、FlyIn、Counter、Timeline、Compare。
- Demo 改用 FadeIn/FlyIn 实现标题动画。

**关键发现**：
- 组件库让 Agent 生成动画代码更可控，避免手写大量 `interpolate`。

**Ratchet决策**：P✅ Q✅（组件渲染成功） I✅ → **保留**

---

### v6: GIF 输出与质量预设

**改动**：
- `RenderOptions` 增加 `format?: 'mp4' | 'gif'` 和 `quality?: 'draft' | 'medium' | 'high'`。
- FFmpeg GIF 路径使用 `palettegen` + `paletteuse`。
- MP4 路径根据 quality 调整 preset/CRF。

**关键发现**：
- GIF 文件大小与帧率、分辨率强相关；Demo 用 10fps/540x960 生成 577KB GIF。

**Ratchet决策**：P✅ Q✅（GIF 非空） I✅ → **保留**

## 最终验证

```bash
cd content-output/video-dsl
npm run typecheck   # ✅
npm run build       # ✅
python -m pytest tests/ -q  # ✅ 14 passed
```

| 产物 | 路径 | 规格 |
|------|------|------|
| 最终带音频视频 | `output/cli-final/final.mp4` | 9s, 2160x3840, AAC |
| GIF 预览 | `output/negative-numbers-gif/final.gif` | 540x960, 10fps |

## 涉及场景

- **场景C2**（迭代开发）：6轮 Ratchet Loop
- **场景E**（内容输出）：视频号管线扩展为 Video DSL 管线
- **场景F**（Skill优化）：validator、router、pipeline 持续打磨

## 重构思考：内容形式 vs 平台

本次 Video DSL 案例也暴露了原有管线的命名惯性：管线以**平台**命名（公众号、视频号、PPT、Notebook），但同一平台可能对应多种**内容形式**（form）。

建议将 content-output 重新抽象为两层：

```
内容形式（Form）          平台（Platform）
├── markdown              ├── 公众号（受限 HTML）
├── html                  ├── Obsidian（markdown + 本地链接）
├── video                 ├── 视频号（9:16 MP4）
├── image                 ├── B站（16:9 MP4）
├── slides                ├── 浏览器（标准 HTML）
├── notebook              ├── Reveal.js
└── pptx                  ├── PPT/WPS
                          └── Jupyter
```

- **形式**决定“用什么容器表达知识”。
- **平台**决定“该容器在目标环境的约束与适配”。

例如：
- 公众号文章 = `html` 形式 + `wechat` 平台适配（受限标签、图片防盗链、排版风格）。
- Obsidian 笔记 = `markdown` 形式 + `obsidian` 平台适配（wiki-link、callout、本地附件）。
- 视频号视频 = `video` 形式 + `video-channel` 平台适配（9:16、时长、封面）。

当前 Video DSL 管线已按此模型重构：默认输出 `form=video` + `platform=video-channel`（9:16），也可通过 `--platform bilibili` 直接输出 16:9，或通过 `--platform douyin` 输出 720x1280。平台适配器位于 [`content-output/scripts/pipelines/video/platforms/`](../content-output/scripts/pipelines/video/platforms/)。具体重构方案见 [content-output/docs/form-vs-platform.md](../content-output/docs/form-vs-platform.md)。
