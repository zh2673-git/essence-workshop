---
name: Skill文档管线
description: |
  Skill文档格式管线：将蒸馏产出的结构化数据按Skill模板规范组装为标准SKILL.md文档。管线层只管格式转换，认知分析/风格选择由上层指定。
  蒸馏分析（提炼心智模型、根因追溯、提取决策启发式、识别场景路由、提取表达DNA）是distillation元场景的工作，本管线只负责按模板组装各章节。
  输入：蒸馏产出的结构化数据。输出：标准SKILL.md文件。
  主要被distillation元场景调用。
version: 1.0
layer: format
pipeline: skill
---

# Skill文档管线

> 将蒸馏数据按Skill模板规范组装为标准SKILL.md文档。管线只管格式转换——蒸馏分析（提炼心智模型、根因追溯、提取决策启发式、识别场景路由、提取表达DNA）由distillation元场景完成后传入结构化数据，本管线只负责按模板填充各章节。

## 输入输出

- **输入**：蒸馏产出的结构化数据（已由distillation元场景完成分析：核心心智模型 + 决策启发式 + 场景路由 + 表达DNA + 根因追溯等）
- **输出**：标准SKILL.md文件（可被cognitive-engine作为蒸馏视角激活）

## Skill文档结构模板

```markdown
---
name: {人物/话题}-essence
description: |
  {人物}的认知操作系统。基于N维度深度调研，通过三阶蒸馏提炼N个核心心智模型、
  N条决策启发式、N条场景路由和完整的表达DNA。含根因追溯。
  用途：作为思维顾问，用{人物}的视角分析问题、审视决策、提供反馈。
  触发词：「用{人物}的视角」「{人物}会怎么看」
---

# {人物} · 认知操作系统

## 30秒抓住{人物}          ← 本质定义（揭底式）
## 2分钟理解心智模型关系     ← 模型关系图
## N个核心心智模型（按需深入）← 每个含：定义+根因追溯+运行方式+局限
## N条决策启发式             ← 一句话规则
## N条场景路由               ← 面对XX→用哪个模型组合
## 表达DNA                   ← 语气+节奏+用词特征+反模式
## 递归深入（可选）           ← 核心模型的子结构
## Few-shot 示例             ← 2-3个问答示例
## 核心张力（内在矛盾）       ← 模型间的悖论
## 诚实边界                  ← 这个Skill做不到什么
## 根因追溯表                ← 心智模型×形成经历×关键转折×认知固化点
```

## 生成流程

```
1. 接收蒸馏产出的结构化数据（已完成分析，不做提炼/追溯/DNA提取）
2. 按frontmatter规范填充 name / description / 触发词
3. 按章节模板依次填充：本质定义 → 模型关系图 → 核心心智模型 → 决策启发式
   → 场景路由 → 表达DNA → 递归深入（可选） → Few-shot → 核心张力 → 诚实边界 → 根因追溯表
4. 校验格式完整性（章节齐全、字段完整、frontmatter规范）
5. 输出标准SKILL.md
```

> 注：心智模型提炼、根因追溯、决策启发式浓缩、场景路由识别、表达DNA提取等分析工作不在本管线执行；若输入缺少这些字段，应退回distillation元场景。

## 格式质量标准

- **章节齐全**：上述11个章节全部存在（"递归深入"可选，其余必备）
- **frontmatter规范**：name/description/触发词三字段完整，description含用途说明
- **字段完整**：每个心智模型含"定义+根因追溯+运行方式+局限"四要素；每条启发式为一句话规则；表达DNA含"语气+节奏+用词+反模式"四要素
- **Few-shot**：至少2个问答示例
- **诚实边界**：必须说明Skill做不到什么

## 模板参考

- [skill-optimization/references/skill-template.md](../../skill-optimization/references/skill-template.md) — Skill模板规范
- [skill-optimization/references/skill-rubric.md](../../skill-optimization/references/skill-rubric.md) — Skill评分标准
- [skill-optimization/references/skill-antipatterns.md](../../skill-optimization/references/skill-antipatterns.md) — Skill反模式

## 脚本

```
skill/
└── scripts/          # 生成脚本（规划中）
    └── generator.py  # 蒸馏数据 → SKILL.md（仅组装，不分析）
```

---

*Skill文档管线 · 蒸馏数据 → 标准SKILL.md · 只管格式组装 · 被distillation元场景调用*
