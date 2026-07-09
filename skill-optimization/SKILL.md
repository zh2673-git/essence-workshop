---
name: Skill优化
description: |
  自主优化循环：评估→改进→验证→确认→保留或回滚，生成评分卡。
  基于Darwin Skill 2.0的hill-climbing优化循环 + Karpathy autoresearch的自主实验思想。
  可优化本质工坊任意层的skill（cognitive/format/workflow/scenarios）以及蒸馏产出的人物skill。
  9+1维度评分体系（结构65分+效果35分+一致性10分），LLM-as-judge准确率46.4%，重要决策必须人审。
  触发词：「优化skill」「skill评分」「达尔文」「darwin」「帮我改改skill」「skill怎么样」。
version: 2.0
scene: F
---

# Skill优化 · 自主优化循环

> Hill-climbing优化循环：评估 → 改进 → 实测验证 → 人类确认 → 保留或回滚

## 触发条件

- 「优化skill」「skill评分」「达尔文」「darwin」「自动优化」
- 「帮我改改skill」「skill怎么样」「提升skill质量」
- 蒸馏完成后质量门控评分低于A级

## 优化范围

可优化本质工坊**任意层**的skill：

| 层级 | 示例 | 路径 |
|------|------|------|
| 认知引擎 | 通用逻辑/易经/法条/寓言 | cognitive/*/SKILL.md |
| 格式管线 | markdown/html/notebook/ppt/video | format/*/SKILL.md |
| 平台适配 | wechat/reveal/whiteboard-recorder | workflow/*/SKILL.md |
| 场景编排 | 知识探索/K12/项目开发 | content-framework/*/框架.md |
| 蒸馏产物 | 老子/达尔文/孔子... | distillation/output/*/SKILL.md |
| 本身 | 本质工坊主路由 | SKILL.md |

## 优化循环（6阶段）

```
Phase 0: 初始化 → 确认优化范围 + 创建备份 + 读取历史记录
Phase 0.5: 测试Prompt设计 → 为每个skill设计2-3个测试prompt
Phase 1: 评估 → 用9+1维度Rubric打分，生成评分卡
Phase 2: 改进 → 针对低分维度改进，每次只改1-2个维度
Phase 3: 实测验证 → 用测试prompt跑改进后的skill，对比改进前
Phase 4: 人类确认 → 展示改进前后对比，由用户决定保留或回滚
Phase 5: 收敛 → 改进后总分必须严格高于改进前才保留，否则回滚
```

## 9+1维度评分体系（总分110）

**结构维度（65分）— 静态分析**：
1. Frontmatter质量（7分）
2. 工作流清晰度（12分）
3. 失败模式编码（12分）— 必须显式编码"如果X失败→Y"
4. 检查点设计（6分）— 🔴CHECKPOINT / 🔵AUTO-CHECK
5. 可执行具体性（17分）— 禁止"建议/可以考虑/根据情况"等软化措辞
6. 资源整合度（4分）
7. 整体架构（7分）— 与v3.0四层架构一致

**效果维度（35分）— 需实测**：
8. 实测表现（23分）— 用测试prompt跑一遍
9. 反例与黑名单（6分）— 必须有"不要做什么"清单
10. 本质工坊一致性（6分）— 三阶合一/顿悟触发/类-属性-方法-路由

**分数等级**：A(90+) / B(80+) / C(70+) / D(60+) / F(<60)

## 执行流程

详见 [F-skill-optimization.md](F-skill-optimization.md)

## 参考文档

- [references/skill-rubric.md](references/skill-rubric.md) — 9+1维度评分标准（详细打分规则）
- [references/skill-antipatterns.md](references/skill-antipatterns.md) — Skill反模式（禁止清单）
- [references/skill-template.md](references/skill-template.md) — Skill模板规范

## 与其他层的关系

- **上游**：蒸馏（distillation）完成后触发质量门控评分
- **作用对象**：任意层skill（含认知引擎/格式管线/平台适配/场景编排/蒸馏产物）
- **方法论基础**：[cognitive/general-logic/SKILL.md](../cognitive/general-logic/SKILL.md) — 三阶合一框架

## 输出

优化后的Skill + 评分卡 + 优化记录 + 测试prompt集

---

*Skill优化 · 评估→改进→验证→确认→保留/回滚 · 9+1维度评分 · 任意层skill可优化*
