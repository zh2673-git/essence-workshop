---
name: 白板录制
description: 无限画布白板讲解录制系统，AI自动根据内容生成Excalidraw手绘白板图解和提词器脚本，支持镜头自动跟随、人像叠加、一键录制；v2方法论驱动"先点破本质再展开图解"
version: 2.0
scene: E3
---

# 白板录制 · Skill（v2）

## v2 方法论锚点

本Skill遵循本质工坊 v2 方法论，**白板内容必须按"三阶合一"组织**，而不是平铺罗列：

```
阶段1（是什么·点出本质）   → 必须有"一句话点破本质"作为视觉焦点
阶段2（为什么·建立因果）   → 必须暴露"反常识根因"制造认知冲突
阶段3（怎么做·展开方法）   → 必须"视角升级收尾"，重新定义问题
```

**顿悟触发机制**（v2核心，强制）：
- 每页必须有一个顿悟触发点：**红色标记 + 问号 + 反差**
- 阶段1一句话点破本质（不是描述外延，是揭底）
- 阶段2至少1个反常识根因（反直觉点制造"原来如此"）
- 阶段3视角升级收尾（不是总结，是重新定义问题）

**本质定义先行**：每页的图解先有本质点破，再有展开。**禁止描述性定义平铺**（如"区块链是按时间顺序链接的区块组成的分布式账本"这种属加种差定义禁用），必须用本质定义（如"区块链是用算力代价换取无需信任第三方的机制"）。

**结构性比喻**（取代"视觉隐喻"）：比喻的内部结构必须与本质同构，不是装饰性比喻。比如"区块链=把区块串成链"是描述性比喻，"区块链=用算力换信任的拍卖场"是结构性比喻。

## 核心方法

内容输入（Markdown/URL/纯文本）→ AI深度理解 → 按"阶段1/阶段2/阶段3"拆分场景 → 无限画布Excalidraw图解自动生成（每页先点破本质，再展开图解） → 提词器脚本自动生成（含反常识根因+视角升级收尾） → 镜头自动跟随 → 带人像叠加录制。

## 触发条件

- 「白板录制」「录白板」「白板讲解」「做白板视频」
- 「白板演示」「录制讲解视频」「录课白板」
- 「自动生成白板」「AI画白板」

## 执行流程

1. **内容获取**：读取本地Markdown文件 / 抓取公众号文章URL / 接收纯文本输入 / 读取 content-output 生成的 `broadcast-script.md`
2. **AI生成（v2）**：调用LLM深度理解内容，**按"阶段1/阶段2/阶段3"拆分场景**，每页先有"一句话点破本质"作为视觉焦点，再展开图解；提词器脚本必须包含"反常识根因"和"视角升级收尾"
3. **镜头规划**：AI给出每个讲解点对应的视口中心坐标，实现镜头平滑跟随
4. **提词生成**：同步生成口语化提词器脚本，与镜头移动同步
5. **前端加载**：导入到WhiteboardCaster录制工具，即可直接开始录制
6. **录制导出**：支持摄像头人像叠加、光标特效、一键导出MP4

## 无限画布模式

- 所有内容在同一个无限大Excalidraw画布上，按讲解顺序排列
- 讲解时镜头自动平滑移动到当前内容区域
- 可以手动拖动白板自由浏览，随时回看
- 支持跨区域画关联箭头，展示内容逻辑联系

## SVG→PNG→image 混合渲染方案（v2新增）

针对其他场景（K12拆解、知识图谱、HTML管线、演示管线等）已生成的SVG图解，提供桥接能力把它们嵌入白板：

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

**与原生Excalidraw元素的关系**：image元素是补充手段，不是替代。AI生成的手绘图解（rectangle/arrow/text）仍然是主线，image元素用于嵌入"难以用Excalidraw原生元素表达"的复杂图解。

## 参考文档

- [references/excalidraw-element-spec.md](references/excalidraw-element-spec.md) — Excalidraw元素规格说明（含image元素）
- [references/ai-prompt-guide.md](references/ai-prompt-guide.md) — AI生成Prompt设计指南（v2方法论）

## 脚本

- `scripts/whiteboard_generator.py` — AI白板内容生成器（v2 Prompt：阶段拆分 + 顿悟触发点 + 本质定义先行），输入文本/URL，输出无限画布JSON+提词脚本
- `scripts/broadcast_to_whiteboard.py` — 口播稿→白板桥接器，输入 content-output 生成的 `broadcast-script.md`，按镜头生成白板画面+提词器
- `scripts/svg_to_whiteboard.py` — SVG→PNG→image桥接器，把其他场景的SVG图解转换为Excalidraw可嵌入的image元素
- `scripts/` 复用 `../content-output/scripts/shared/article_fetcher.py` 做内容抓取
- `scripts/` 复用 `../content-output/scripts/elements/svg_to_png.py` 做SVG→PNG转换

## 前端工具

WhiteboardCaster录制界面位于本项目webapp目录，支持：
- Excalidraw无限画布手绘
- 场景导航+镜头自动跟随
- 提词器面板
- 摄像头人像叠加/拖拽/大小调整
- 光标特效
- 录制预览/导出

## v2 编码纪律

- **不要破坏 validate_elements()**：坐标偏移只在 validate_elements 里应用一次，generator脚本里不重复加偏移
- **fontFamily 强制 2**：fontFamily=1（Virgil）导致中文渲染不稳定，AI生成时必须用 fontFamily=2（印刷体）
- **Whiteboard JSON 必须含全部必填字段**：参考 excalidraw-element-spec.md 的字段清单
- **TypeScript 类型定义**：viewport、duration_estimate、index 字段设为 optional
