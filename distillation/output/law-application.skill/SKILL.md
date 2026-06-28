---
name: law-application
description: |
  中国大陆成文法体系下的通用法条适用认知框架（v2）。
  当用户需要完成以下任务时触发本技能：
  - 分析具体事件的法律关系与法律后果；
  - 检索并适用法律规范；
  - 进行涵摄、冲突裁决、法律解释、抗辩检视；
  - 生成端到端的法条适用分析报告。
  本技能内部由 1 个复合编排器、8 个核心原子 skill 和 3 个辅助原子 skill 组成。
  默认入口为 `skills/orchestrator/SKILL.md`，负责按标准流程调度原子 skill。
  边界：不构成法律意见，不替代执业律师；重大、复杂或涉及人身自由的案件必须建议咨询执业法律专业人员。
---

# law-application.skill · 法条适用认知框架（v2）

## 法律声明

> 本技能输出的所有内容均为结构化法律分析草稿，**不构成法律意见，不替代执业律师**。其中的法条引用、案例引用、解释结论、量化计算结果均需通过官方法律数据库复核确认。重大决策前请咨询执业法律专业人员。

---

## 一、定位

`law-application.skill` 是原 v1 版本的原子化升级版（v2）。它将 v1 中内嵌的 8 个认知框架拆分为可独立调用的原子 skill，并新增复合编排器与辅助 skill，形成完整的法条适用技能族。

v1 版本已迁移归档，当前目录即为 v2 正式版本。

---

## 二、内部结构

```
law-application.skill/
├── SKILL.md              # 本文件：总入口
├── README.md             # 总览与使用说明
├── references/           # 统一支撑材料（essence + research）
└── skills/               # 原子 skill 目录
    ├── orchestrator/     # 复合编排器：端到端分析入口
    ├── fact-trimming/                 # 事实裁剪
    ├── legal-relationship-typing/     # 法律关系定性
    ├── norm-retrieval/                # 规范检索
    ├── subsumption/                   # 涵摄
    ├── conflict-resolution/           # 冲突裁决
    ├── legal-interpretation/          # 法律解释
    ├── defense-and-validity-review/   # 抗辩与效力检视
    ├── fallback-application/          # 兜底适用
    ├── case-retrieval/                # 案例检索（辅助）
    ├── evidence-evaluation/           # 证据评估（辅助）
    └── legal-consequence-calculation/ # 法律后果量化计算（辅助）
```

---

## 三、使用方式

### 方式一：端到端分析（推荐）

直接调用 `skills/orchestrator/SKILL.md`，输入具体事件描述，获得完整法条适用分析报告。

### 方式二：单独调用原子 skill

根据需求调用具体原子 skill：

| 需求 | 调用 skill |
|------|-----------|
| 整理事实 | `skills/fact-trimming` |
| 判断法律关系领域 | `skills/legal-relationship-typing` |
| 检索法条 | `skills/norm-retrieval` |
| 判断要件是否满足 | `skills/subsumption` |
| 解决规范/证据/争点冲突 | `skills/conflict-resolution` |
| 解释模糊规范 | `skills/legal-interpretation` |
| 审查抗辩与效力 | `skills/defense-and-validity-review` |
| 穷尽具体规则后兜底 | `skills/fallback-application` |
| 检索类案 | `skills/case-retrieval` |
| 评估证据 | `skills/evidence-evaluation` |
| 计算赔偿/刑期/处罚 | `skills/legal-consequence-calculation` |

---

## 四、标准调用链

复合编排器 `skills/orchestrator` 默认按以下流程调度：

```
fact-trimming
  → legal-relationship-typing
  → norm-retrieval
  → [case-retrieval]
  → subsumption
  → [legal-interpretation]
  → [conflict-resolution]
  → defense-and-validity-review
  → [legal-consequence-calculation]
  → [fallback-application]
```

每个阶段均设有质量检查点（QC），未通过则回溯至前序阶段。

---

## 五、检索策略

法条与案例检索采用**分层降级策略**：

| 层级 | 方式 | 说明 |
|------|------|------|
| 第一层 | 已配置 MCP 工具 | 北大法宝 MCP、秘塔搜索 MCP 等 |
| 第二层 | 模型/Agent 联网搜索 | 国家法律法规数据库、裁判文书网、人民法院案例库等 |
| 第三层 | 模型内部知识 | 仅作框架性提示，必须标注 `[待校验]` |

---

## 六、支撑材料

本技能的支撑材料统一存放在 `references/` 目录：

- `references/essence/`：本质、根因、系统运作说明
- `references/research/`：定义、起源、观点、案例、趋势、争议、本质提炼

这些材料用于理解本技能的设计依据与认知基础，不直接参与运行时的法律分析。

---

## 七、与 v1 的关系

| 维度 | v1 | v2（当前版本） |
|------|-----|-------------|
| 结构 | 单一 mega-skill | 总 skill + 原子 skill 族 |
| 核心能力 | 8 个认知框架 | 8 个核心原子 skill + 3 个辅助 skill |
| 编排 | 无 | 有复合编排器 |
| 检索策略 | 倾向绑定北大法宝 MCP | MCP 优先 + 联网搜索兜底 |
| 可组合性 | 低 | 高 |
| 支撑材料 | 内置 references | 统一 references |

---

*law-application.skill v2 由本质工坊 · 项目开发方法生成，基于 v1 升级而来。*
