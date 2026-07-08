---
name: 连载小说
description: 多章节连载小说创作与管理系统，支持世界观构建、人物设定、分章大纲、单章写作与连载状态跟踪。基于方法论：三阶合一（阶段1是什么·点出本质·本质定义先行 → 阶段2为什么·建立因果·含反常识根因 → 阶段3怎么做·展开方法·视角升级）+ 每章一个本质（核心概念内核）+ 顿悟触发机制（一句话点破+反常识根因+视角升级）+ 类-属性-方法-路由（由本质定义锚定）。
version: 2.0
scene: E2
---

# 连载小说 · Skill

## 核心方法

三阶合一框架（本质定义先行 + 顿悟触发 + 类-属性-方法-路由由本质锚定）详见 [../../cognitive-engine/general-logic/SKILL.md](../../cognitive-engine/general-logic/SKILL.md)。

**连载小说特有约束（硬性）**：
- **每章一个本质**：每章动笔前必须先确定本章的本质定义（核心概念内核），并通过本质检验
- **顿悟触发器三件套**（每章必备，缺一不可）：阶段1一句话点破 + 阶段2反常识根因 + 阶段3视角升级
- **三阶与坡度三阶段一一对应**，不再正交为9宫格
- **类-属性-方法-路由在小说中的映射**：本质定义 → 故事类归属 → 属性展开（世界观/人物/冲突）→ 方法体现（叙事策略）→ 路由适配（章节载体）

**工作流**：每章本质定义先行 → 世界观构建 → 人物设定 → 故事主线 → 分季/分章大纲 → 单章写作（植入顿悟触发器）→ 配图生成（走 format-pipeline）→ 连载推送（走 platform-adapter/wechat）→ 状态更新。

## 触发条件

- 「写连载小说」「小说连载」「连载XX」
- 用户希望将知识/案例/话题以小说形式长期输出
- 用户要求创建多章节故事序列

## 执行流程

详见 [SF-serial-fiction.md](SF-serial-fiction.md)

## 参考文档

- [references/fiction-style-guide.md](references/fiction-style-guide.md) — 小说风格规范
- [references/world-building-guide.md](references/world-building-guide.md) — 世界观构建方法
- [references/chapter-outline-template.md](references/chapter-outline-template.md) — 分章大纲模板
- [references/series-state-spec.md](references/series-state-spec.md) — 连载状态规范

## 模板

- [templates/world-building-template.md](templates/world-building-template.md) — 世界观文档模板
- [templates/character-card-template.md](templates/character-card-template.md) — 人物卡模板
- [templates/chapter-template.md](templates/chapter-template.md) — 章节正文模板

## 输出资产

```
serial-fiction/output/{series-name}/
├── world-building.md
├── characters/
├── seasons/
│   └── season-XX/
│       ├── outline.md
│       └── chapters/
│           ├── chapter-XX-outline.md
│           └── chapter-XX.md
├── assets/
│   ├── characters-relation.svg
│   └── covers/
└── series-state.json
```

## 与格式管线层的关系

连载小说子系统是场景编排层的独立分支。它不通过格式管线层的通用风格选择步骤，而是有独立工作流。单章完成后，走公众号管线（format-pipeline/markdown + platform-adapter/wechat）推送时按"连载小说"风格的字数与配图标准执行。
