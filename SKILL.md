---
name: 本质工坊
description: |
  认知→框架→形式→工作流 四层可组合富媒体交付系统（v4.0）。
  四层架构：认知层（理解事物）× 内容框架层（组织内容）× 形式层（转换格式）× 工作流层（编排交付）。
  认知层帮我们理解事物，经过理解后形成实际的内容框架进行沉淀，然后根据框架转化为不同形式的内容，如果有固定工作场景则进一步沉淀为工作流。
  工作流 = 认知×框架×格式×平台的组合。平台只是工作流的一部分，不以平台去划分。
  元场景：蒸馏（生产新认知子skill）+ Skill优化（优化任意层skill）。
  认知层基于方法论：三阶合一（阶段1是什么·点出本质 → 阶段2为什么·建立因果 → 阶段3怎么做·展开方法·视角升级）+ 本质定义双引擎（分析式+原型式）+ 顿悟触发机制。
  认知层只有两类：通用逻辑（理性逻辑）+ 易经视角（感性逻辑）。法条适用、寓言故事等已沉淀为内容框架层的内容框架。
  触发词：「探索XX」「拆解XX」「蒸馏XX」「开发XX」「分析XX」「写公众号」「做视频」「做PPT」「HTML交互」「做notebook」「白板录制」「录白板」「白板讲解」「写连载小说」「小说连载」「用寓言讲XX」「XX寓言化」「优化skill」「达尔文」「darwin」「用易经看XX」「XX是什么象」「取象分析XX」「易解XX」「卦象视角」。
version: 4.0
---

# 本质工坊 · 四层可组合架构路由

> **v4.0 核心原则**：四层可组合 —— 认知（理解）× 框架（组织）× 形式（转换）× 工作流（交付）
>
> **认知方法论**：三阶合一 —— 阶段1（是什么·点出本质）→ 阶段2（为什么·建立因果）→ 阶段3（怎么做·展开方法·视角升级）
>
> **本质定义双引擎**：引擎A（分析式，通用逻辑）+ 引擎B（原型式，易经取象）。框架+实现关系。
>
> **顿悟触发**：阶段1一句话点破 + 阶段2反常识根因 + 阶段3视角升级
>
> **工作流编排**：工作流 = 认知 × 框架 × 格式 × 平台 的组合

---

## ⚠️ Agent 执行纪律

1. **先读规范再操作**：执行前必须检查对应子Skill中 `references/` 的硬性约束
2. **约束语言含义**：`必须` = 无条件遵守；`禁止` = 绝对不能做
3. **生成后自检**：每次生成文件后，必须执行质量自检
4. **Windows 环境**：PowerShell 用 `;` 替代 `&&`
5. **四层依次调用**：认知层产出认知产物 → 内容框架层组织内容 → 形式层转换格式 → 工作流层编排交付

---

## v4.0 四层架构

```
┌─────────────────────────────────────────────────────────────┐
│  认知层（cognitive）—— 用什么视角理解事物                     │
│  ┌──────────┐ ┌──────────┐                                    │
│  │通用逻辑  │ │易经视角  │  认知层只有两类：理性逻辑+感性逻辑 │
│  │(理性基座)│ │(感性原型)│                                    │
│  └────┬─────┘ └────┬─────┘                                    │
│       └────────────┘                                          │
│                    ↓ 输出：认知产物（结构化数据）             │
├─────────────────────────────────────────────────────────────┤
│  内容框架层（content-framework）—— 用什么框架组织内容        │
│  ┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐  │
│  │作文  ││寓言  ││法律  ││K12   ││连载  ││项目  ││蒸馏  │..│
│  │框架  ││故事  ││适用  ││课件  ││小说  ││开发  ││框架  │  │
│  └──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘  │
│     └───────┴───────┴───────┴───────┴───────┴───────┘      │
│                    ↓ 输出：结构化内容（可转为任意格式）       │
├─────────────────────────────────────────────────────────────┤
│  形式层（format）—— 用什么格式表达                           │
│  ┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐  │
│  │Markdown││ HTML ││Notebook││ PPT ││视频 ││音频 ││白板 │  │
│  └──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘  │
│     └────────┴────────┴────────┴────────┴───────┘          │
│                    ↓ 输出：格式产物（通用格式文件）           │
├─────────────────────────────────────────────────────────────┤
│  工作流层（workflow）—— 编排交付（含平台+场景流程）          │
│  ┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐  │
│  │公众号││白板  ││视频号││K12   ││连载  ││项目  ││蒸馏  │..│
│  │发布  ││录制  ││      ││课件  ││小说  ││开发  ││工作流│  │
│  └──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘  │
│     └────────┴────────┴────────┴───────┴───────┴───────┘   │
│                    ↓ 输出：交付成品（含 output/ 产物）       │
└─────────────────────────────────────────────────────────────┘

元场景：蒸馏（生产新认知子skill）+ Skill优化（优化任意层skill）
```

### 架构逻辑

```
认知层 → 理解事物 → 产出认知产物
    ↓
内容框架层 → 组织内容 → 产出结构化内容（框架不绑定场景，可被任意工作流调用）
    ↓
形式层 → 转换格式 → 产出格式产物（md/html/audio/video等）
    ↓
工作流层 → 编排交付 → 产出交付成品（工作流 = 认知×框架×格式×平台）
```

**关键设计**：框架与场景解耦。比如高考作文框架是独立的内容框架，可被口播、文章、视频等任何工作流灵活调用。

---

## 场景路由表

| 场景 | 触发词 | 认知视角 | 内容框架 | 形式 | 工作流 | 子Skill |
|-----|--------|---------|---------|------|--------|---------|
| **A: 知识探索** | 「探索XX」「理解XX」「XX是什么」 | 通用逻辑（默认） | -（直接用认知层） | Markdown | Obsidian | [cognitive/general-logic/](cognitive/general-logic/SKILL.md) + [workflow/knowledge-exploration/](workflow/knowledge-exploration/A-knowledge-exploration.md) |
| **A2: K12拆解** | 「拆解XX」「讲解XX」「知本」 | 通用逻辑 | K12拆解框架 | HTML交互 | 浏览器交互 | [content-framework/k12-decomposition/](content-framework/k12-decomposition/k12-decomposition.md) + [workflow/k12-decomposition/](workflow/k12-decomposition/A2-knowledge-decomposition.md) |
| **C: 项目开发** | 「开发XX」「设计XX系统」 | 通用逻辑 | 项目开发框架 | Markdown+代码 | 项目交付 | [content-framework/project-dev/](content-framework/project-dev/project-dev.md) + [workflow/project-dev/](workflow/project-dev/C-project-development.md) |
| **C2: 迭代开发** | 「迭代开发XX」「从0到1构建XX并迭代」 | 通用逻辑 | 项目开发框架 | Markdown+代码 | 项目交付 | [workflow/project-dev/iterative-loop.md](workflow/project-dev/iterative-loop.md) |
| **D: 项目解析** | 「分析XX项目」「拆解XX代码」 | 通用逻辑（逆向） | 项目分析框架 | Markdown | Obsidian | [content-framework/project-analysis/](content-framework/project-analysis/project-analysis.md) + [workflow/project-analysis/](workflow/project-analysis/D-project-analysis.md) |
| **E2: 连载小说** | 「写连载小说」「小说连载」「连载XX」 | 通用逻辑 | 连载小说框架 | Markdown | 公众号发布 | [content-framework/serial-fiction/](content-framework/serial-fiction/serial-fiction.md) + [workflow/serial-fiction/](workflow/serial-fiction/SF-serial-fiction.md) |
| **H: 易经视角** | 「用易经看XX」「XX是什么象」「取象分析XX」「易解XX」 | 易经视角 | - | Markdown | Obsidian | [cognitive/yijing-perspective/](cognitive/yijing-perspective/SKILL.md) |
| **G: 概念寓言化** | 「用寓言讲XX」「XX寓言化」「给XX编个故事」 | 通用逻辑 | 寓言故事框架 | Markdown | - | [content-framework/fable-concept/](content-framework/fable-concept/fable-concept.md) |
| **L: 法律分析** | 「法条适用」「法律关系」「涵摄」「怎么证明」 | 通用逻辑 | 法律适用框架 | Markdown | - | [content-framework/law-application/](content-framework/law-application/law-application.md) + [workflow/law-analysis/](workflow/law-analysis/SKILL.md) |

### 元场景（生产/优化 Skill 本身）

| 元场景 | 触发词 | 功能 | 子Skill |
|--------|--------|------|---------|
| **B+B2: 蒸馏** | 「蒸馏XX」「提炼XX思维」「造skill」 | 生产新认知子skill。蒸馏框架在内容框架层，蒸馏工作流在工作流层 | 框架：[content-framework/distillation/](content-framework/distillation/distillation.md) + 工作流：[workflow/distillation/](workflow/distillation/B-person-distillation.md) |
| **F: Skill优化** | 「优化skill」「达尔文」「darwin」 | 评估→改进→验证循环，优化任意层skill | [skill-optimization/](skill-optimization/SKILL.md) |

### 形式+工作流直接调用（不经过场景编排）

| 触发词 | 形式层 | 工作流层 |
|--------|--------|---------|
| 「写公众号」 | Markdown/HTML | 公众号发布 |
| 「做视频」 | 视频 | 视频号 |
| 「做PPT」 | PPT | PPT/WPS |
| 「HTML交互」 | HTML | 浏览器交互 |
| 「做notebook」 | Notebook | Jupyter |
| 「白板录制」「录白板」 | 白板 | 白板录制 |

直接调用时：[format/SKILL.md](format/SKILL.md) + [workflow/SKILL.md](workflow/SKILL.md)

---

## 场景间流转

```
A(探索) → 理解概念后想开发 → C(项目开发)
A(探索) → 输出教学notebook → 形式层(Notebook) + 工作流层(Jupyter)
A2(拆解) → 拆解后想做视频 → 形式层(视频) + 工作流层(视频号)
A2(拆解) → 拆解后想继续拆解 → A2(递归)
B(蒸馏) → 蒸馏后想用其风格输出 → 形式层 + 工作流层 + 蒸馏Skill风格
B(蒸馏) → 质量不达标 → F(Skill优化)
C(开发) → 开发完想输出文章 → 形式层(Markdown) + 工作流层(公众号)
C(开发) → 开发完想生成教学notebook → 形式层(Notebook)
C(开发) → 需要迭代改进 → C2(迭代开发)
C2(迭代) → 收敛后沉淀经验 → B2(话题蒸馏)
C2(迭代) → 收敛后生成教学notebook → 形式层(Notebook)
D(解析) → 解析完想输出文章 → 形式层(Markdown) + 工作流层(公众号)
D(解析) → 解析完想生成教学notebook → 形式层(Notebook)
E2(连载小说) → 世界观构建后想输出单章 → 形式层(Markdown) + 工作流层(公众号)
E2(连载小说) → 素材来自场景A/B/C/D → 先蒸馏/探索再小说化
G(寓言化) → 寓言想输出成文章/视频 → 形式层 + 工作流层
G(寓言化) → 寓言想做成教学HTML → A2(K12拆解) 插入寓言引入模块
A(探索) → 概念太抽象想用故事讲 → G(概念寓言化)
A2(拆解) → 知识点需要故事引入 → G(概念寓言化)
B(蒸馏) → 想用寓言浓缩人物思维 → G(概念寓言化)
E2(连载小说) → 每章需要一个概念内核 → G(概念寓言化)
A(探索) → 概念需要原型定位 → H(易经视角) → 取象作为本质定义
A2(拆解) → 知识点需要原型节点 → H(易经视角) → 卦象作为知识图谱原型
B(蒸馏) → 人物思维需要分类坐标系 → H(易经视角) → 64卦分类心智模型
C(开发) → 项目类型不清晰 → H(易经视角) → 项目定象判断阶段
D(解析) → 项目本质不明 → H(易经视角) → 反推卦象识别模式
H(易经) → 取象后想深入分析 → A(知识探索) → 用定象结果作为本质定义起点
H(易经) → 易解后想输出文章 → 形式层 + 工作流层 → 象辞式风格+卦象叙事
H(易经) → 卦象本身就是寓言 → G(概念寓言化) → 用卦象故事讲概念
```

---

## 认知层（cognitive）

认知层只有两类：通用逻辑（理性逻辑，是什么/为什么/怎么做）+ 易经视角（感性直觉，取象定象）。详见 [cognitive/SKILL.md](cognitive/SKILL.md) 和 [cognitive/general-logic/SKILL.md](cognitive/general-logic/SKILL.md)。

---

## 内容框架层（content-framework）

内容框架（作文/寓言故事/法律适用/K12课件/连载小说/项目分析/项目开发/蒸馏等）。框架是沉淀下来的可复用结构，仅限于框架，不含实质内容。框架不绑定场景，可被任意工作流灵活调用。详见 [content-framework/SKILL.md](content-framework/SKILL.md)。

---

## 形式层（format）

8条形式管线（Markdown/HTML/Notebook/PPT/视频/音频/白板/Skill）。详见 [format/SKILL.md](format/SKILL.md)。

---

## 工作流层（workflow）

工作流层编排具体做事的流程。含平台交付工作流（公众号发布/白板录制/视频号/浏览器交互/Reveal幻灯片/PPT-WPS/Jupyter/Obsidian/项目交付）和场景工作流（K12课件/连载小说/项目开发/项目解析/知识探索/法律分析/蒸馏）。工作流 = 认知×框架×格式×平台的组合，产物存放在各工作流的 output/ 目录。详见 [workflow/SKILL.md](workflow/SKILL.md)。

---

## 核心方法论

三阶合一框架、本质定义双引擎、顿悟触发机制、类-属性-方法-路由框架等核心方法论详见 [cognitive/general-logic/SKILL.md](cognitive/general-logic/SKILL.md)。

---

## 文件结构（v4.0）

```
essence-workshop/                  # 路由Skill（本文件）
├── SKILL.md                       # v4.0 四层架构路由
├── cognitive/                     # 第1层：认知（通用逻辑+易经视角）
├── content-framework/             # 第2层：内容框架（作文/寓言/法律/K12/连载/项目/蒸馏等框架）
├── format/                        # 第3层：形式（md/html/notebook/ppt/视频/音频/白板/skill 形式规范）
├── workflow/                      # 第4层：工作流（编排交付+场景流程+output产物）
└── skill-optimization/            # 元场景F：Skill优化
```

---

## 扩展规则

### 新增认知视角
在 `cognitive/` 下创建新子目录，包含SKILL.md和references/，实现三阶合一的三个阶段即可。认知层只有两类：通用逻辑（理性）+ 易经视角（感性）。蒸馏工作流产出的新认知skill自动放入此层。

### 新增内容框架
在 `content-framework/` 下创建新子目录，定义"如何组织内容"的方法论即可。框架不绑定具体格式和平台。

### 新增形式管线
在 `format/` 下创建新子目录，实现"结构化内容 → 格式产物"的转换即可。

### 新增工作流
在 `workflow/` 下创建新子目录，编排"认知 × 框架 × 格式 × 平台"的组合即可。建议同时在 `workflow/scripts/platforms/` 下添加平台实现脚本（继承 base.py）。

---

*本质工坊 · v4.0 · 认知 × 内容框架 × 形式 × 工作流 · 四层可组合架构*
