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

## 两种产品开发路径

本 Skill 支持开发两类产品，由用户在需求沟通阶段明确或根据需求特征自动判断：

| 路径 | 产物形态 | 核心设计增量 | 适用场景 |
|------|---------|-------------|---------|
| **纯工具产品** | 无 LLM 运行时的规则/代码/数据系统 | 数据结构、状态机、接口契约、P/Q/I 验证 | 需求明确、结构化、重复性高 |
| **协同产品** | 含 LLM 运行时 + 符号系统约束的系统 | 额外设计 LLM 接入层、符号校验层、Prompt 管理、失败降级 | 需求模糊、需自然语言理解、动态生成、创新性任务 |

**说明**：
- 两种路径都与标准/迭代模式自由组合，形成 4 种子模式（标准纯工具、标准协同、迭代纯工具、迭代协同）。
- 执行开发流程的 Agent 本身含有 LLM，两种路径的区别**不在于 Skill 是否调用 LLM**，而在于**被开发产品本身是否包含 LLM 运行时和符号系统约束**。
- 协同产品路径的详细工作流和模板见 [C-project-development.md](C-project-development.md) 和 [templates/synergy-product-design.md](templates/synergy-product-design.md)。

## 触发条件

- 「开发XX」「设计XX系统」「帮我做一个XX」→ 标准模式
- 「迭代开发XX」「从0到1构建XX并迭代」「测试驱动开发XX」→ 迭代模式
- 「开发一个 LLM 协同的 XX」「做一个带大模型的 XX」→ 协同产品路径
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

## 实战案例

- [cases/pi-agent-iteration.md](../cases/pi-agent-iteration.md) — PI-Agent 6轮Ratchet Loop迭代实录（本地小模型编码Agent，6轮0回退，3.5x性能提升）

## 输出

- 标准模式：可运行的代码实现 + 设计文档
- 迭代模式：可运行的代码实现 + 设计文档 + 测试报告 + 版本化方案
