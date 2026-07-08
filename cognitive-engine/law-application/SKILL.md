---
name: law-application
description: |
  中国大陆成文法体系下的通用法条适用认知框架。
  当用户需要完成以下任务时触发本技能：
  - 分析具体事件的法律关系与法律后果；
  - 检索并适用法律规范；
  - 进行涵摄、冲突裁决、法律解释、抗辩检视；
  - 把法律要件转化为可取得的证据材料并评估证明力。
  触发词包括：「法条适用」「法律关系」「涵摄」「怎么证明」「需要什么证据」「去哪里查」「找哪个部门」「材料怎么取」。
  本技能由 8 个核心原子 skill 和 4 个辅助原子 skill 组成，端到端编排由 scenarios/law-analysis 负责。
  边界：不构成法律意见，不替代执业律师；重大、复杂或涉及人身自由的案件必须建议咨询执业法律专业人员。
---

# law-application · 法条适用认知框架

## 法律声明

> 本技能输出的所有内容均为结构化法律分析草稿，**不构成法律意见，不替代执业律师**。其中的法条引用、案例引用、解释结论、量化计算结果均需通过官方法律数据库复核确认。重大决策前请咨询执业法律专业人员。

---

## 一、定位

本技能作为认知引擎的"法条适用"视角，用规则识别与适用实现三阶合一框架。三阶合一框架定义详见 [../general-logic/SKILL.md](../general-logic/SKILL.md)。

端到端的法律分析编排（调用顺序、QC检查点、条件分支）由 [../../scenarios/law-analysis/SKILL.md](../../scenarios/law-analysis/SKILL.md) 负责。

---

## 二、内部结构

```
law-application/
├── SKILL.md              # 本文件：认知视角总入口
├── README.md             # 总览与使用说明
├── references/           # 统一支撑材料（essence + research）
└── skills/               # 原子 skill 目录（认知方法）
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

## 三、原子 skill 清单

根据需求调用具体原子 skill（端到端编排走 scenarios/law-analysis）：

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
| 推导取证方案 | `skills/evidence-discovery` |
| 评估证据 | `skills/evidence-evaluation` |
| 计算赔偿/刑期/处罚 | `skills/legal-consequence-calculation` |

---

## 四、检索策略（认知原则）

法条与案例检索的分层降级原则（具体执行由 platform-adapter 负责）：

| 层级 | 方式 | 说明 |
|------|------|------|
| 第一层 | 已配置 MCP 工具 | 北大法宝 MCP、秘塔搜索 MCP 等 |
| 第二层 | 模型/Agent 联网搜索 | 国家法律法规数据库、裁判文书网、人民法院案例库等 |
| 第三层 | 模型内部知识 | 仅作框架性提示，必须标注 `[待校验]` |

---

## 五、支撑材料

本技能的支撑材料统一存放在 `references/` 目录：

- `references/essence/`：本质、根因、系统运作说明
- `references/research/`：定义、起源、观点、案例、趋势、争议、本质提炼

这些材料用于理解本技能的设计依据与认知基础，不直接参与运行时的法律分析。

---

*law-application 认知框架 · 法条适用视角 · 原子skill定义 · 编排走scenarios/law-analysis*
