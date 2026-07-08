---
name: 白板录制
description: |
  白板录制平台适配器：将白板场景JSON（.whiteboard.json）+ 口播稿加载到WhiteboardCaster录制工具，
  支持镜头自动跟随、人像叠加、一键录制导出MP4。
  白板JSON内容由format-pipeline/whiteboard生成，口播稿由format-pipeline/broadcast生成。
  本适配器只负责平台录制与导出，不做内容理解/场景拆分/JSON生成。
  输入：.whiteboard.json + broadcast-script.md。输出：MP4视频。
  触发词：「白板录制」「录白板」「白板讲解」「做白板视频」。
version: 3.0
layer: platform
adapter: whiteboard-recorder
---

# 白板录制平台适配器

> 将白板JSON+口播稿加载到WhiteboardCaster，完成录制与MP4导出。内容生成由format-pipeline处理，本适配器只管录制平台。

## 输入与输出

| 项 | 说明 |
|----|------|
| 输入 | .whiteboard.json（来自format-pipeline/whiteboard）+ broadcast-script.md（来自format-pipeline/broadcast） |
| 输出 | MP4视频（含镜头跟随+人像叠加） |

## 与格式管线的分工

| 职责 | 归属 |
|------|------|
| 生成白板元素JSON（场景结构、文字、图形、箭头） | format-pipeline/whiteboard |
| 生成口播稿（5镜头结构、口语化） | format-pipeline/broadcast |
| 白板渲染、镜头跟随、提词器、录制MP4 | **本适配器** |

## 平台约束

| 约束项 | 说明 |
|--------|------|
| 渲染引擎 | Excalidraw（WhiteboardCaster内置） |
| 画布模式 | 无限画布，镜头自动平滑跟随 |
| 字体 | 中文使用fontFamily:2（标准字体），禁止fontFamily:1（Virgil，中文渲染不稳定） |
| 元素字段 | 每个元素必须含version/versionNonce/isDeleted/seed |
| 坐标偏移 | 由validate_elements()统一处理，不可重复计算 |
| 镜头导航 | 使用Excalidraw内置scrollToContent()，不手动计算scrollX/Y |

## 适配流程

```
1. 读取 .whiteboard.json（来自format-pipeline/whiteboard）
2. 读取 broadcast-script.md（来自format-pipeline/broadcast，用作提词器）
3. 加载到WhiteboardCaster录制工具
4. 镜头规划：按场景边界自动设定视口中心坐标
5. 开始录制（支持摄像头人像叠加、光标特效）
6. 导出MP4
```

## SVG→PNG→image 混合渲染（平台桥接）

针对其他场景已生成的SVG图解，提供桥接能力把它们嵌入白板：

```
其他场景的SVG
    ↓ svg_to_png.py (Playwright渲染)
   PNG文件
    ↓ base64编码
Excalidraw image元素 (type="image") + files字段
    ↓ 合并到
.whiteboard.json 的对应 scene.elements
```

**用法**：

```bash
python scripts/svg_to_whiteboard.py \
  --input path/to/svg_dir \
  --output scene_assets.json \
  --scene-index 0 \
  --position-x 100 --position-y 200
```

**输出片段结构**：
- `image_elements`：可直接合并到 scene.elements 的 image 元素数组
- `files`：必须合并到 .whiteboard.json 顶层 files 字段（base64 dataURL）

**混合渲染使用场景**：
- K12拆解的HTML知识图谱 → 截图SVG → 嵌入白板作为参考图
- 项目解析的架构图SVG → 嵌入白板作为背景图
- HTML管线的交互演示 → 渲染SVG → 嵌入白板作为静态参考

## 无限画布模式

- 所有内容在同一个无限大Excalidraw画布上，按讲解顺序排列
- 讲解时镜头自动平滑移动到当前内容区域
- 可以手动拖动白板自由浏览，随时回看
- 支持跨区域画关联箭头，展示内容逻辑联系

## 前端工具

WhiteboardCaster录制界面位于本项目webapp目录，支持：
- Excalidraw无限画布手绘
- 场景导航+镜头自动跟随
- 提词器面板
- 摄像头人像叠加/拖拽/大小调整
- 光标特效
- 录制预览/导出

## 编码纪律

- **不要破坏 validate_elements()**：坐标偏移只在 validate_elements 里应用一次，generator脚本里不重复加偏移
- **fontFamily 强制 2**：fontFamily=1（Virgil）导致中文渲染不稳定，生成时必须用 fontFamily=2（印刷体）
- **Whiteboard JSON 必须含全部必填字段**：参考 excalidraw-element-spec.md 的字段清单
- **TypeScript 类型定义**：viewport、duration_estimate、index 字段设为 optional

## 参考文档

- [references/excalidraw-element-spec.md](references/excalidraw-element-spec.md) — Excalidraw元素规格说明（含image元素）

## 脚本

- `scripts/svg_to_whiteboard.py` — SVG→PNG→image桥接器，把其他场景的SVG图解转换为Excalidraw可嵌入的image元素
- `scripts/broadcast_to_whiteboard.py` — 白板项目导出器，将预生成的白板JSON应用场景坐标布局并导出为平台格式（.whiteboard.json/.excalidraw/提词器.md）
- `scripts/whiteboard_generator.py` — 白板JSON生成器（**内容生成逻辑归属format-pipeline/whiteboard**，本适配器仅复用其元素处理逻辑）
- `scripts/` 复用 `../../format-pipeline/scripts/elements/svg_to_png.py` 做SVG→PNG转换

---

*白板录制平台适配器 · whiteboard.json+broadcast.md→MP4 · 镜头跟随+人像叠加 · 不做内容生成*
