---
name: 视频号适配器
description: |
  视频号平台适配：将口播稿格式产物适配到视频号平台规格。
  接收content-framework/essay产出的口播稿，桥接到白板录制生成视频MP4。
  平台职责：视频规格适配、TTS录制、白板桥接。不负责口播稿内容生成（那是格式层职责）。
  输入：口播稿Markdown（来自content-framework/essay）。输出：视频号规格MP4。
  触发词：「发视频号」「录制视频号」「视频号发布」。
version: 2.0
layer: workflow
adapter: video-channel
---

# 视频号适配器

> 将口播稿格式产物适配到视频号平台规格。口播稿内容由 content-framework/essay 生成（5镜头结构+口语化），本适配器只负责平台适配：视频规格、TTS录制、白板桥接。

## 输入与输出

| 项 | 说明 |
|----|------|
| 输入 | 口播稿 Markdown（来自 [../../content-framework/essay/essay.md](../../content-framework/essay/essay.md)） |
| 输出 | 视频号规格 MP4 + 白板录制源文件 |

## 平台约束

| 约束 | 说明 |
|------|------|
| 画幅 | 1080×1920 竖屏（视频号默认） |
| 时长 | 1-5 分钟（由口播稿字数决定，约150字/分钟） |
| 编码 | H.264 MP4 |
| 字幕 | 口播稿的5镜头结构可作为字幕分段 |
| 敏感内容 | 口播稿的认知/风格/寓言化由上层处理，平台层不再处理 |

## 适配流程

```
1. 读取口播稿 broadcast-script.md（来自 content-framework/essay）
2. 读取白板JSON（来自 format/whiteboard，含场景和元素）
3. 桥接到白板录制器：
   - 白板JSON → broadcast_to_whiteboard.py → .whiteboard.json + .excalidraw + 提词器.md
4. TTS生成旁白音频（每镜头一段）
5. 白板录制器渲染白板动画视频
6. 合并视频 + 音频（可选BGM ducking）
7. 输出视频号规格 MP4
```

## 白板桥接

```
白板JSON(来自 format/whiteboard)
  → broadcast_to_whiteboard.py（应用场景坐标布局）
  → .whiteboard.json + .excalidraw + 提词器.md
  → whiteboard-recorder 录制
  → MP4
```

脚本位置：`../whiteboard-recorder/scripts/broadcast_to_whiteboard.py`

## 失败模式

| 现象 | 处理 |
|------|------|
| 口播稿缺失 | 先走 content-framework/essay 生成口播稿 |
| 白板JSON缺失 | 先走 format/whiteboard 生成白板JSON |
| 白板桥接失败 | 检查白板JSON格式（场景和元素是否完整） |
| TTS失败 | 检查 edge-tts 安装与网络 |
| 视频>50MB | 压缩或分段 |
| 白板动画与旁白不同步 | 检查白板录制的时间映射 |

## 质量自检

| 检查项 | 标准 |
|--------|------|
| 画幅 | 1080×1920 竖屏 |
| 时长 | 1-5 分钟 |
| 旁白完整 | 5镜头每段有旁白 |
| 白板动画 | 与旁白同步 |
| 文件大小 | ≤50MB |
| 字幕 | 可选，5镜头分段 |

## 与其他适配器的关系

| 适配器 | 输入格式 | 输出 | 与视频号的区别 |
|--------|---------|------|--------------|
| **视频号（本适配器）** | 口播稿.md | 竖屏MP4 | 竖屏 + 白板录制 |
| 白板录制器 | .whiteboard.json | 白板MP4 | 录制执行层（被本适配器桥接） |
| 公众号 | .md/.html | 受限HTML | 纯图文，无视频 |

## 与格式层的关系

- **上游**：[../../content-framework/essay/essay.md](../../content-framework/essay/essay.md) — 口播稿框架（负责5步法结构+口语化格式化）
- **口播稿的认知/风格/寓言化**由上层（认知引擎/场景层）处理，格式层只做格式组装，本适配器只做平台适配

---

*视频号适配器 · 口播稿.md → 竖屏MP4 · 白板桥接 + TTS录制 · 工作流层*
