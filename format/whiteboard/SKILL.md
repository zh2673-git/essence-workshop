---
name: 白板管线
description: |
  白板格式管线：将认知产物转换为白板场景JSON（.whiteboard.json）。
  负责生成Excalidraw兼容的白板元素结构，不含录制功能（录制由workflow/whiteboard-recorder负责）。
  输入：认知产物（场景化的知识点结构）。输出：.whiteboard.json文件。
  触发词：「做白板」「白板内容」「白板JSON」。
version: 1.0
layer: format
pipeline: whiteboard
---

# 白板管线

> 生成白板场景JSON。本管线只负责"画什么"，"怎么录"由工作流层处理。

## 与工作流层的分工

| 职责 | 归属 |
|------|------|
| 生成白板元素JSON（场景结构、文字、图形、箭头） | **本管线**（format/whiteboard） |
| 白板渲染、镜头跟随、提词器、录制MP4 | workflow/whiteboard-recorder |

## 输入输出

- **输入**：认知产物（本质定义、因果链、方法步骤等结构化数据）
- **输出**：.whiteboard.json 文件（Excalidraw兼容格式）

## 场景结构

认知产物的三阶段映射到白板场景：

```
场景1（是什么）← 本质定义 + 一句话点破
场景2（为什么）← 因果链 + 反常识根因
场景3（怎么做）← 方法步骤 + 视角升级
（可选）场景0（钩子）+ 场景4（收尾）
```

## 元素规范

白板JSON必须遵循Excalidraw元素规范，详见：
- [workflow/whiteboard-recorder/SKILL.md](../../workflow/whiteboard-recorder/SKILL.md) 的元素约束
- 硬性约束：每个元素必须包含 version、versionNonce、isDeleted、seed 字段
- 字体：中文使用 `fontFamily: 2`（标准字体），禁止使用 `fontFamily: 1`（Virgil，中文渲染不稳定）
- 坐标偏移：由 `validate_elements()` 统一处理，生成脚本中不手动计算偏移

## 生成流程

```
1. 认知产物 → 场景拆分（按三阶段）
2. 每个场景 → 元素布局（标题+正文+图形+箭头）
3. 元素 → normalizeElement() 补全字段
4. validate_elements() 统一坐标偏移
5. 导出 .whiteboard.json
```

## 失败模式

| 现象 | 处理 |
|------|------|
| JSON解析失败（特定位置截断） | 检查JSON完整性，排查截断位置；通常是元素数据被截断 |
| viewport字段缺失导致访问报错 | 补全 viewport.x/y/zoom 字段（或设为optional） |
| 中文渲染不稳定 | 检查fontFamily，必须用2（标准字体），禁止1（Virgil） |
| 元素被推出视口 | 坐标偏移只能在generator或validate_elements中处理一次，不可重复 |
| 白屏问题 | 使用Excalidraw内置scrollToContent()而非手动计算scrollX/Y |
| 元素重叠 | 调整布局算法，增加元素间距检测 |

## 质量自检

| 检查项 | 标准 |
|--------|------|
| JSON完整性 | 所有元素含version/versionNonce/isDeleted/seed字段 |
| 字体 | 中文使用fontFamily:2，无fontFamily:1 |
| 坐标 | 偏移只处理一次，元素在视口范围内 |
| 场景结构 | 三阶段映射完整（是什么/为什么/怎么做） |
| viewport | x/y/zoom字段完整或声明optional |
| Excalidraw兼容 | 可在Excalidraw中正常打开和编辑 |

## 脚本

```
whiteboard/
└── scripts/                    # 生成脚本（规划中）
    └── generator.py            # 认知产物→白板JSON
```

白板JSON生成逻辑归属本管线。`workflow/whiteboard-recorder/scripts/whiteboard_generator.py` 的内容生成部分归属本管线，平台适配器仅复用其元素处理逻辑做渲染验证。

---

*白板管线 · 认知产物→白板场景JSON · Excalidraw兼容 · 与whiteboard-recorder分工协作*
