---
name: 平台适配
description: |
  平台交付层：将格式管线产出的通用格式文件，适配到具体平台的约束，生成可交付的成品。
  本层是"路由"层——回答"交付到哪里"。包含多种平台适配器：微信公众号、视频号、Reveal演示、浏览器、PPT/WPS、Jupyter、Obsidian、白板录制器、项目交付物。
  每个平台有独立的约束（如公众号的受限HTML、视频号的MP4规格），适配器负责将通用格式转为平台合规的成品。
  触发词：当场景需要平台交付时自动调用；也可由用户指定平台（如「写公众号」「发视频号」）。
version: 3.0
layer: platform
---

# 平台适配 · 平台交付路由

> **v3.0 平台层**：本层是本质工坊的"交付适配器"——把格式产物适配到平台成品。
> 平台层 = "路由"层（类-属性-方法-路由中的"路由"），回答"交付到哪里"。

---

## 架构

```
平台适配（交付到哪里）
├── wechat/                # 微信公众号（受限HTML）
├── video-channel/         # 视频号（口播稿→竖屏MP4）
├── reveal/                # Reveal.js 演示
├── browser/               # 浏览器（通用HTML交互）
├── ppt-wps/               # PPT/WPS 演示
├── jupyter/               # Jupyter Notebook
├── obsidian/              # Obsidian（wiki-links+双链+标签）
├── project/               # 项目交付物（代码+文档）
├── whiteboard-recorder/   # 白板录制器（无限画布+录制）
├── scripts/platforms/     # 共享平台脚本（base + 各平台实现）
└── ...（扩展中）
```

---

## 输入输出契约

### 输入：格式产物（来自 format-pipeline）

```
Markdown 文件 / 通用 HTML 文件 / .ipynb / .pptx / .mp4 / .whiteboard.json / broadcast-script.md / SKILL.md
```

### 输出：平台成品（交付物）

```
公众号受限HTML / 视频号MP4 / Reveal.js演示 / 浏览器HTML / PPT文件 / Jupyter / Obsidian.md / 白板MP4+源文件 / 项目代码包
```

---

## 平台适配器

| 适配器 | 平台 | 输入格式 | 输出成品 | 路径 | 状态 |
|--------|------|---------|---------|------|------|
| 微信公众号 | 微信公众号 | Markdown/HTML | 受限HTML（公众号排版） | [wechat/](wechat/) | ✅ |
| 视频号 | 视频号 | 口播稿.md | 竖屏MP4+白板源文件 | [video-channel/](video-channel/) | ✅ |
| Reveal演示 | 浏览器(演示) | Markdown/HTML | Reveal.js 演示页 | [reveal/](reveal/) | ✅ |
| 白板录制器 | 白板视频 | .whiteboard.json + broadcast-script.md | 白板MP4+源文件 | [whiteboard-recorder/](whiteboard-recorder/) | ✅ |
| 浏览器 | 浏览器(交互) | 通用HTML | 交互式HTML | [browser/](browser/) | ✅ |
| PPT/WPS | PPT软件 | .pptx | 平台PPT文件 | [ppt-wps/](ppt-wps/) | ✅ |
| Jupyter | Jupyter环境 | .ipynb | Notebook文件 | [jupyter/](jupyter/) | ✅ |
| Obsidian | Obsidian | 标准.md | Obsidian.md（wiki-links+双链） | [obsidian/](obsidian/) | ✅ |
| 项目交付 | 项目仓库 | 代码+文档 | 可运行项目 | [project/](project/) | ✅ |

---

## 平台约束（关键差异）

### 微信公众号
- **约束**：不支持外部CSS/JS，样式必须内联，图片需上传素材库
- **适配**：通用HTML → 内联样式HTML → 公众号预览版
- **脚本**：[wechat/scripts/](wechat/scripts/)（client, converter, publish）

### 视频号
- **约束**：MP4规格（1080×1920竖屏），时长1-5分钟
- **适配**：口播稿.md → 白板桥接 → TTS录制 → 竖屏MP4
- **上游**：口播稿来自 format-pipeline/broadcast

### Reveal演示
- **约束**：Reveal.js 框架，slides 结构
- **适配**：Markdown → Reveal.js HTML
- **脚本**：[reveal/scripts/](reveal/scripts/)（generator）

### 白板录制器
- **约束**：Excalidraw 元素规范，无限画布，镜头跟随
- **适配**：.whiteboard.json + broadcast-script.md → 白板动画MP4
- **上游**：白板JSON来自 format-pipeline/whiteboard，口播稿来自 format-pipeline/broadcast
- **Webapp**：[whiteboard-recorder/webapp/](whiteboard-recorder/webapp/)（React+Excalidraw）
- **脚本**：[whiteboard-recorder/scripts/](whiteboard-recorder/scripts/)（svg_to_whiteboard, broadcast_to_whiteboard）

### Obsidian
- **约束**：wiki-links `![[name.svg]]`，双链 `[[]]`，标签 `#tag`
- **适配**：标准.md → Obsidian.md（图形引用转wiki-links，可选双链和标签）
- **脚本**：本适配器实现平台专属转换（上游标准 Markdown 来自 format-pipeline/markdown）

---

## 共享平台脚本

位于 [scripts/platforms/](scripts/platforms/)：

| 脚本 | 平台 | 功能 |
|------|------|------|
| base.py | 基类 | 平台适配器基类 |
| wechat.py | 微信公众号 | 公众号适配 |
| video_channel.py | 视频号 | 视频号适配 |
| bilibili.py | B站 | B站适配 |
| douyin.py | 抖音 | 抖音适配 |
| browser.py | 浏览器 | 浏览器适配 |
| reveal.py | Reveal | Reveal演示适配 |
| jupyter.py | Jupyter | Jupyter适配 |
| obsidian.py | Obsidian | Obsidian适配 |
| office.py | Office | Office文档适配 |

---

## 平台选择规则

### 由场景指定
场景层（scenarios/）会指定使用哪个平台：
- 知识探索 → Obsidian（默认）/ 浏览器
- K12拆解 → 浏览器（交互HTML）
- 项目开发 → 项目交付（代码+文档）
- 内容输出 → 用户指定平台（公众号/视频号/...）
- 连载小说 → 公众号（连载推送）

### 由用户指定
用户可直接指定：「写公众号」「发视频号」「做PPT」

### 平台切换
同一格式产物可适配不同平台（格式层复用）：格式产物 → 平台A → 平台B，无需重新生成格式。

---

## 与其他层的关系

### 上游：format-pipeline
接收格式产物（通用格式文件），按平台约束适配。

### 协同：scenarios
场景层编排"认知视角 × 格式 × 平台"的组合，平台层是其中最后一环。

### 特殊：whiteboard-recorder
白板录制器是一个相对独立的子系统，包含完整的 webapp（React+Excalidraw）和录制脚本。v3.0后它是纯平台适配器（输入.whiteboard.json+broadcast.md，输出白板MP4），内容生成（白板JSON/口播稿）由format-pipeline处理，认知分析由cognitive-engine处理。

---

## 扩展新平台

新增平台适配器只需在 `platform-adapter/` 下创建新子目录，包含：
- `SKILL.md`（平台规范+约束）
- `scripts/`（适配脚本，可选）
- `references/`（平台规范，可选）
- 实现"格式产物 → 平台成品"的适配即可。
- 建议同时在 `scripts/platforms/` 下添加平台实现脚本（继承 base.py）。

---

*平台适配 · v3.0 · 格式产物 → 平台成品 · 9平台适配器*
