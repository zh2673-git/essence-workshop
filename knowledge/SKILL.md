---
name: K12知识拆解
description: 七维框架拆解知识点，基于v2方法论（本质定义先行+顿悟触发），支持知识点/项目式/讲课三种模式
version: 2.0
scene: A2
---

# K12知识拆解（知本）· Skill

## 核心方法（v2）

**本质定义先行 → 七维框架展开（含顿悟触发）**：
1. Step 0（v2新增）：本质定义先行——为知识点找到本质定义并通过本质检验
2. 七维框架：定义锚点（升级为本质锚点） → 溯源 → 矛盾（含反常识根因） → 应用 → 延伸（含视角升级） → 网络 → 验证
3. 类-属性-方法-路由由本质定义锚定，每个维度必须能回溯到本质
4. 配合范式族插件和学段适配

## 触发条件

- 「拆解XX」「讲解XX」「XX怎么理解」「知本」
- K12学科知识点拆解

## 执行流程

详见 [A2-knowledge-decomposition.md](A2-knowledge-decomposition.md)

## 参考文档

- [../exploration/references/methodology.md](../exploration/references/methodology.md) — v2方法论基础
- [references/formal-science.md](references/formal-science.md) — 形式科学族插件
- [references/humanities.md](references/humanities.md) — 人文学科族插件
- [references/life-science.md](references/life-science.md) — 生命科学族插件
- [references/grade-adapter.md](references/grade-adapter.md) — 学段适配规则

## 模板

- [templates/decomposition.html](templates/decomposition.html) — 知识点七维拆解
- [templates/project.html](templates/project.html) — 项目式学习路径
- [templates/lecture.html](templates/lecture.html) — 讲课模式（跨知识点导航）

## 三种模式

| 模式 | 触发 | 产出 |
|------|------|------|
| 知识点模式 | 「拆解XX」 | 单个知识点HTML |
| 项目式模式 | 「项目式学习XX」 | 项目HTML + 多个知识点HTML |
| 讲课模式 | 「讲课模式」「录制视频」 | 单页讲课导航HTML，支持自动演示 |

## 产出

生成的HTML和知识图谱存放在 `output/` 目录下。
