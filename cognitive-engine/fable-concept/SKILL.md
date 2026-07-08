---
name: 概念寓言化
description: |
  将抽象概念转化为一则寓言故事，让读者在叙事中自行悟出概念本质。
  作为本质定义的叙事式表达，寓言横跨三阶（思考层）：开头呼应本质（阶段1）→中段建立反差（阶段2反常识根因）→结尾视角升级（阶段3）。
  用途：当用户想用故事/寓言方式理解一个概念、给概念打比方、把抽象知识讲给外行/儿童听时使用。
  触发词：「用寓言讲XX」「XX寓言化」「给XX编个故事」「坡度寓言XX」「用故事解释XX」「fable XX」。
version: 3.0
scene: G
layer: cognitive
role: perspective-implementation
---

# 概念寓言化 · Skill

## 核心方法

> 三阶合一框架定义、思考层 vs 输出层分离原则详见 [../general-logic/SKILL.md](../general-logic/SKILL.md) 与 [../general-logic/references/methodology.md](../general-logic/references/methodology.md)。本节描述寓言视角如何实现三阶段。

寓言是本质定义的叙事式表达。三阶合一 × 寓言叙事：先用本质定义点出本质（阶段1），再用寓言建立因果并触发反常识根因（阶段2），最后展开迁移并视角升级（阶段3）。寓言的内核由本质定义锚定，反差/反转对应反常识根因，寓意收尾对应视角升级。

## 触发条件

- 「用寓言讲XX」「XX寓言化」「给XX编个故事」
- 「用故事解释XX」「坡度寓言XX」「fable XX」
- 其他场景需要"建立因果"叙事载体时，调用本视角生成寓言元素

## 认知方法

详见 [F-fable-concept.md](F-fable-concept.md)

## 参考文档

- [references/fable-method.md](references/fable-method.md) — 寓言化认知方法与映射回溯规范
- [references/slope-integration.md](references/slope-integration.md) — 寓言与三阶合一的关系

## 模板

- [templates/fable-prompt.md](templates/fable-prompt.md) — 寓言化认知原则与自检清单

## 输出（认知产物）

本质定义 + 一则寓言故事 + 概念点破句 + 寓言→概念映射表（回溯到本质）+ 2个迁移问题 + 视角升级句。具体输出格式（字数、模板、分节）由 format-pipeline 决定，调用编排与跨场景流转由 scenarios 决定。
