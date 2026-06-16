---
name: 项目开发
description: 基于三阶方法论正向设计新项目，从本质推导到可运行代码。支持标准模式和迭代模式（Ratchet Loop）。
version: 2.0
scene: C
---

# 项目开发 · Skill

## 核心方法

三阶正向设计：是什么（本质推导）→ 为什么（架构决策）→ 怎么做（四层设计+代码实现）。

## 两种执行模式

| 模式 | 触发条件 | 流程 | 适用场景 |
|------|---------|------|---------|
| **标准模式** | 「开发XX」「设计XX系统」 | 设计→实现→交付 | 需求明确，一次交付 |
| **迭代模式** | 「迭代开发XX」「从0到1构建XX并迭代」 | 设计→实现→测试→评估→保留/回退→下一轮 | 需求渐进，测试驱动 |

迭代模式借鉴 Karpathy autoresearch 的 Ratchet Loop（棘轮循环），详见下方。

## 触发条件

- 「开发XX」「设计XX系统」「帮我做一个XX」→ 标准模式
- 「迭代开发XX」「从0到1构建XX并迭代」「测试驱动开发XX」→ 迭代模式
- 用户要从零开始构建新项目

## 执行流程

- 标准模式：详见 [C-project-development.md](C-project-development.md)
- 迭代模式：详见 [iterative-loop.md](iterative-loop.md)

## 参考文档

- [references/design-principles.md](references/design-principles.md) — 设计原则
- [references/ratchet-loop.md](references/ratchet-loop.md) — 棘轮循环（迭代模式核心机制）

## 模板

- [templates/project-essence.md](templates/project-essence.md) — 项目本质分析
- [templates/project-architecture.md](templates/project-architecture.md) — 架构决策
- [templates/project-modules.md](templates/project-modules.md) — 模块设计
- [templates/four-layer-design.md](templates/four-layer-design.md) — 四层设计
- [templates/program.md](templates/program.md) — 迭代策略文件（迭代模式专用）

## 输出

- 标准模式：可运行的代码实现 + 设计文档
- 迭代模式：可运行的代码实现 + 设计文档 + 测试报告 + 版本化方案
