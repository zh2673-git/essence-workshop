---
name: 本质工坊
description: |
  认知→格式→平台 三层可组合富媒体交付系统（v3.0）。
  三层架构：认知引擎层（用什么视角理解）× 格式管线层（用什么格式表达）× 平台适配层（交付到哪里）。
  场景编排层：场景 = 认知视角 × 格式 × 平台 的组合，支持11大场景。
  元场景：蒸馏（生产新认知子skill）+ Skill优化（优化任意层skill）。
  认知引擎基于方法论：三阶合一（阶段1是什么·点出本质 → 阶段2为什么·建立因果 → 阶段3怎么做·展开方法·视角升级）+ 本质定义双引擎（分析式+原型式）+ 顿悟触发机制。
  通用逻辑为框架基座，易经/法条/寓言为视角实现（框架+实现关系，无冲突）。
  触发词：「探索XX」「拆解XX」「蒸馏XX」「开发XX」「分析XX」「写公众号」「做视频」「做PPT」「HTML交互」「做notebook」「白板录制」「录白板」「白板讲解」「写连载小说」「小说连载」「用寓言讲XX」「XX寓言化」「优化skill」「达尔文」「darwin」「用易经看XX」「XX是什么象」「取象分析XX」「易解XX」「卦象视角」。
version: 3.0
---

# 本质工坊 · 三层可组合架构路由

> **v3.0 核心原则**：三层可组合 —— 认知引擎（理解）× 格式管线（表达）× 平台适配（交付）
>
> **认知方法论**：三阶合一 —— 阶段1（是什么·点出本质）→ 阶段2（为什么·建立因果）→ 阶段3（怎么做·展开方法·视角升级）
>
> **本质定义双引擎**：引擎A（分析式，通用逻辑）+ 引擎B（原型式，易经取象）。框架+实现关系。
>
> **顿悟触发**：阶段1一句话点破 + 阶段2反常识根因 + 阶段3视角升级
>
> **场景编排**：场景 = 认知视角 × 格式 × 平台 的组合

---

## ⚠️ Agent 执行纪律

1. **先读规范再操作**：执行前必须检查对应子Skill中 `references/` 的硬性约束
2. **约束语言含义**：`必须` = 无条件遵守；`禁止` = 绝对不能做
3. **生成后自检**：每次生成文件后，必须执行质量自检
4. **Windows 环境**：PowerShell 用 `;` 替代 `&&`
5. **三层依次调用**：认知引擎产出认知产物 → 格式管线转为格式产物 → 平台适配为平台成品

---

## v3.0 三层架构

```
┌─────────────────────────────────────────────────────────────┐
│  认知引擎层（cognitive-engine）—— 用什么视角理解              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │通用逻辑  │ │易经视角  │ │法条适用  │ │概念寓言化│        │
│  │(框架基座)│ │(原型式)  │ │(法律场景)│ │(叙事式)  │        │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘        │
│       └────────────┴────────────┴────────────┘              │
│                    ↓ 输出：认知产物（结构化数据）             │
├─────────────────────────────────────────────────────────────┤
│  格式管线层（format-pipeline）—— 用什么格式表达              │
│  ┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐  │
│  │Markdown││ HTML ││Notebook││ PPT ││视频 ││音频 ││白板 │  │
│  └──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘  │
│     └────────┴────────┴────────┴────────┴────────┴───────┘  │
│                    ↓ 输出：格式产物（通用格式文件）           │
├─────────────────────────────────────────────────────────────┤
│  平台适配层（platform-adapter）—— 交付到哪里                 │
│  ┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐  │
│  │公众号││视频号││Reveal││浏览器││PPT/WPS││Jupyter││白板录制│  │
│  └──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘└──┬───┘  │
│     └────────┴────────┴────────┴────────┴────────┴───────┘  │
│                    ↓ 输出：平台成品（可交付物）               │
└─────────────────────────────────────────────────────────────┘

场景编排层（scenarios）—— 组合"认知视角 × 格式 × 平台"
元场景：蒸馏（生产新认知子skill）+ Skill优化（优化任意层skill）
```

### 三层映射到 类-属性-方法-路由

```
本质定义（认知引擎产出）
    ↓ 锚定
类归属 + 属性 = 认知引擎层（cognitive-engine）
    ↓ 体现
方法 = 格式管线层（format-pipeline）—— "怎么表达"
    ↓ 适配
路由 = 平台适配层（platform-adapter）—— "交付到哪里"

回溯检验：每一层必须能回溯到本质定义。
```

---

## 场景路由表

| 场景 | 触发词 | 认知视角 | 格式 | 平台 | 子Skill |
|-----|--------|---------|------|------|---------|
| **A: 知识探索** | 「探索XX」「理解XX」「XX是什么」 | 通用逻辑（默认） | Markdown | Obsidian | [scenarios/knowledge-exploration/](scenarios/knowledge-exploration/SKILL.md) |
| **A2: K12拆解** | 「拆解XX」「讲解XX」「知本」 | 通用逻辑 | HTML交互 | 浏览器 | [scenarios/k12-decomposition/](scenarios/k12-decomposition/SKILL.md) |
| **C: 项目开发** | 「开发XX」「设计XX系统」 | 通用逻辑 | Markdown+代码 | 项目交付 | [scenarios/project-dev/](scenarios/project-dev/SKILL.md) |
| **C2: 迭代开发** | 「迭代开发XX」「从0到1构建XX并迭代」 | 通用逻辑 | Markdown+代码 | 项目交付 | [scenarios/project-dev/iterative-loop.md](scenarios/project-dev/iterative-loop.md) |
| **D: 项目解析** | 「分析XX项目」「拆解XX代码」 | 通用逻辑（逆向） | Markdown | Obsidian | [scenarios/project-analysis/](scenarios/project-analysis/SKILL.md) |
| **E2: 连载小说** | 「写连载小说」「小说连载」「连载XX」 | 通用逻辑+寓言 | Markdown | 公众号 | [scenarios/serial-fiction/](scenarios/serial-fiction/SKILL.md) |
| **H: 易经视角** | 「用易经看XX」「XX是什么象」「取象分析XX」「易解XX」 | 易经视角 | Markdown | Obsidian | [cognitive-engine/yijing-perspective/](cognitive-engine/yijing-perspective/SKILL.md) |
| **G: 概念寓言化** | 「用寓言讲XX」「XX寓言化」「给XX编个故事」 | 概念寓言化 | Markdown | 元素层 | [cognitive-engine/fable-concept/](cognitive-engine/fable-concept/SKILL.md) |
| **L: 法律分析** | 「法条适用」「法律关系」「涵摄」「怎么证明」 | 法条适用 | Markdown | - | [scenarios/law-analysis/](scenarios/law-analysis/SKILL.md) |

### 元场景（生产/优化 Skill 本身）

| 元场景 | 触发词 | 功能 | 子Skill |
|--------|--------|------|---------|
| **B+B2: 蒸馏** | 「蒸馏XX」「提炼XX思维」「造skill」 | 生产新认知子skill，产出放入 cognitive-engine/ 或 distillation/output/ | [distillation/](distillation/SKILL.md) |
| **F: Skill优化** | 「优化skill」「达尔文」「darwin」 | 评估→改进→验证循环，优化任意层skill | [skill-optimization/](skill-optimization/SKILL.md) |

### 格式+平台直接调用（不经过场景编排）

| 触发词 | 格式管线 | 平台适配 |
|--------|---------|---------|
| 「写公众号」 | Markdown/HTML | 微信公众号 |
| 「做视频」 | 视频 | 视频号 |
| 「做PPT」 | PPT | PPT/WPS |
| 「HTML交互」 | HTML | 浏览器 |
| 「做notebook」 | Notebook | Jupyter |
| 「白板录制」「录白板」 | 白板 | 白板录制器 |

直接调用时：[format-pipeline/SKILL.md](format-pipeline/SKILL.md) + [platform-adapter/SKILL.md](platform-adapter/SKILL.md)

---

## 场景间流转

```
A(探索) → 理解概念后想开发 → C(项目开发)
A(探索) → 输出教学notebook → 格式管线(Notebook) + 平台适配(Jupyter)
A2(拆解) → 拆解后想做视频 → 格式管线(视频) + 平台适配(视频号)
A2(拆解) → 拆解后想继续拆解 → A2(递归)
B(蒸馏) → 蒸馏后想用其风格输出 → 格式管线 + 平台适配 + 蒸馏Skill风格
B(蒸馏) → 质量不达标 → F(Skill优化)
C(开发) → 开发完想输出文章 → 格式管线(Markdown) + 平台适配(公众号)
C(开发) → 开发完想生成教学notebook → 格式管线(Notebook)
C(开发) → 需要迭代改进 → C2(迭代开发)
C2(迭代) → 收敛后沉淀经验 → B2(话题蒸馏)
C2(迭代) → 收敛后生成教学notebook → 格式管线(Notebook)
D(解析) → 解析完想输出文章 → 格式管线(Markdown) + 平台适配(公众号)
D(解析) → 解析完想生成教学notebook → 格式管线(Notebook)
E2(连载小说) → 世界观构建后想输出单章 → 格式管线(Markdown) + 平台适配(公众号)
E2(连载小说) → 素材来自场景A/B/C/D → 先蒸馏/探索再小说化
G(寓言化) → 寓言想输出成文章/视频 → 格式管线 + 平台适配
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
H(易经) → 易解后想输出文章 → 格式管线 + 平台适配 → 象辞式风格+卦象叙事
H(易经) → 卦象本身就是寓言 → G(概念寓言化) → 用卦象故事讲概念
```

---

## 认知引擎层（cognitive-engine）

通用逻辑为框架基座 + 3个视角实现（易经/法条/寓言）。子Skill表、三阶合一框架定义、顿悟触发机制、认知产物 YAML 详见 [cognitive-engine/SKILL.md](cognitive-engine/SKILL.md) 和 [cognitive-engine/general-logic/SKILL.md](cognitive-engine/general-logic/SKILL.md)。

---

## 格式管线层（format-pipeline）

8条格式管线（Markdown/HTML/Notebook/PPT/视频/音频/白板/Skill）和8种输出风格（论文/专栏/故事/教程/观点/对话/蒸馏Skill/连载小说）详见 [format-pipeline/SKILL.md](format-pipeline/SKILL.md)。

---

## 平台适配层（platform-adapter）

8+平台适配器（公众号/视频号/Reveal/白板录制器/浏览器/PPT-WPS/Jupyter/项目交付）和共享平台脚本详见 [platform-adapter/SKILL.md](platform-adapter/SKILL.md)。

---

## 核心方法论

三阶合一框架、本质定义双引擎、顿悟触发机制、类-属性-方法-路由框架等核心方法论详见 [cognitive-engine/general-logic/SKILL.md](cognitive-engine/general-logic/SKILL.md)。

---

## 文件结构（v3.0）

```
essence-workshop/                  # 路由Skill（本文件）
├── SKILL.md                       # v3.0 三层架构路由
├── cognitive-engine/              # 第1层：认知引擎（用什么视角理解）
├── format-pipeline/               # 第2层：格式管线（用什么格式表达）
├── platform-adapter/              # 第3层：平台适配（交付到哪里）
├── scenarios/                     # 场景编排层（认知×格式×平台 的组合）
├── distillation/                  # 元场景B：蒸馏（生产新认知子skill）
├── skill-optimization/            # 元场景F：Skill优化
└── cases/                         # 实战案例
```

---

## 扩展规则

### 新增认知视角
在 `cognitive-engine/` 下创建新子目录，包含SKILL.md和references/，实现三阶合一的三个阶段即可。蒸馏（distillation）产出的新认知skill自动放入此层。

### 新增格式管线
在 `format-pipeline/` 下创建新子目录，实现"认知产物 → 格式产物"的转换即可。

### 新增平台适配器
在 `platform-adapter/` 下创建新子目录，实现"格式产物 → 平台成品"的适配即可。建议同时在 `scripts/platforms/` 下添加平台实现脚本（继承 base.py）。

### 新增场景
在 `scenarios/` 下创建新子目录，编排"认知视角 × 格式 × 平台"的组合即可。

---

*本质工坊 · v3.0 · 认知引擎 × 格式管线 × 平台适配 · 三阶合一 × 本质定义双引擎 × 类-属性-方法-路由*
