---
name: 连载小说
description: 多章节连载小说创作与管理系统，支持世界观构建、人物设定、分章大纲、单章写作与连载状态跟踪
version: 1.0
scene: E2
---

# 连载小说 · Skill

## 核心方法

世界观构建 → 人物设定 → 故事主线 → 分季/分章大纲 → 单章写作 → 配图生成 → 连载推送 → 状态更新。

## 触发条件

- 「写连载小说」「小说连载」「连载XX」
- 用户希望将知识/案例/话题以小说形式长期输出
- 用户要求创建多章节故事序列

## 执行流程

详见 [SF-serial-fiction.md](SF-serial-fiction.md)

## 参考文档

- [references/fiction-style-guide.md](references/fiction-style-guide.md) — 小说风格规范
- [references/world-building-guide.md](references/world-building-guide.md) — 世界观构建方法
- [references/character-card-template.md](references/character-card-template.md) — 人物卡模板
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

## 与内容输出层的关系

连载小说子系统是 `content-output` 层的独立分支。它不通过 `E-content-output.md` 中的风格选择步骤，而是有独立工作流。单章完成后，走公众号管线推送时按"连载小说"风格的字数与配图标准执行。
