---
name: K12知识拆解
description: 七维框架拆解知识点，基于方法论（本质定义先行+顿悟触发），支持知识点/项目式/讲课三种模式
version: 2.0
scene: A2
---

# K12知识拆解（知本）· Skill

## 核心方法

三阶合一框架（本质定义先行 + 顿悟触发 + 类-属性-方法-路由由本质锚定）详见 [../../cognitive-engine/general-logic/SKILL.md](../../cognitive-engine/general-logic/SKILL.md)。

**K12七维框架**（本质定义先行 → 七维展开，每个维度必须能回溯到本质）：定义锚点（升级为本质锚点） → 溯源 → 矛盾 → 应用 → 延伸 → 网络 → 验证。配合范式族插件和学段适配。

## 触发条件

- 「拆解XX」「讲解XX」「XX怎么理解」「知本」
- K12学科知识点拆解

## 执行流程

详见 [A2-knowledge-decomposition.md](A2-knowledge-decomposition.md)

## 参考文档

- [../../cognitive-engine/general-logic/references/methodology.md](../../cognitive-engine/general-logic/references/methodology.md) — 方法论基础
- [references/formal-science.md](references/formal-science.md) — 形式科学族插件
- [references/humanities.md](references/humanities.md) — 人文学科族插件
- [references/life-science.md](references/life-science.md) — 生命科学族插件
- [references/grade-adapter.md](references/grade-adapter.md) — 学段适配规则

## 模板

K12 专用内容模板（定义七维拆解/项目式/讲课的内容结构），HTML 渲染通过 [../../format-pipeline/html/SKILL.md](../../format-pipeline/html/SKILL.md) 管线完成：

HTML格式模板已迁移至 format-pipeline/html/templates/：
- [../../format-pipeline/html/templates/decomposition.html](../../format-pipeline/html/templates/decomposition.html) — 知识点七维拆解内容模板
- [../../format-pipeline/html/templates/project.html](../../format-pipeline/html/templates/project.html) — 项目式学习路径内容模板
- [../../format-pipeline/html/templates/lecture.html](../../format-pipeline/html/templates/lecture.html) — 讲课模式内容模板（跨知识点导航）

## 三种模式

| 模式 | 触发 | 产出 |
|------|------|------|
| 知识点模式 | 「拆解XX」 | 单个知识点HTML（走 format-pipeline/html） |
| 项目式模式 | 「项目式学习XX」 | 项目HTML + 多个知识点HTML（走 format-pipeline/html） |
| 讲课模式 | 「讲课模式」 | 单页讲课导航HTML，支持自动演示（走 format-pipeline/html） |

## 产出

生成的HTML和知识图谱存放在 `output/` 目录下。视频录制需走 platform-adapter/video-channel。
