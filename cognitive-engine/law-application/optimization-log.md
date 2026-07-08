# law-application.skill 优化记录

## 优化目标
增加实务可操作视角：在法律涵摄之后，反向推导每个待证要件对应的证据材料、获取主体/渠道、证明力等级，实现从「法律判断」到「实务取证」的闭环。

## 基线评估

| 维度 | 权重 | 得分 | 简评 |
|------|------|------|------|
| 1. Frontmatter质量 | 7 | 8 | description 完整，触发词清晰，无空话尾巴 |
| 2. 工作流清晰度 | 12 | 8 | orchestrator 步骤明确，原子 skill 输入输出模板化 |
| 3. 失败模式编码 | 12 | 7 | 有失败模式表，但非每个关键步骤都有显式 if-then 分支 |
| 4. 检查点设计 | 6 | 6 | 有 QC 表，但缺少 🔵/🔴 显性视觉标记 |
| 5. 可执行具体性 | 17 | 7 | 模板具体，但部分步骤仍偏抽象 |
| 6. 资源整合度 | 4 | 9 | references 路径正确，支撑材料统一 |
| 7. 整体架构 | 7 | 9 | 总 skill + 原子 skill 族 + 编排器结构清晰 |
| 8. 实测表现 | 23 | 5 | dry_run：对「实务取证」类 prompt 缺少 evidence-discovery，无法输出获取渠道与证明力排序 |
| 9. 反例与黑名单 | 6 | 4 | 有法律声明，但缺少「不要做什么」反例清单 |
| 10. 本质工坊一致性 | 6 | 6 | 结构清晰，但坡度理解与三阶方法论应用不够显性 |

**基线总分：约 67 / 110（B 级）**

## 优化动作

1. 新增 `skills/evidence-discovery/SKILL.md`：构成要件 → 取证材料 → 获取主体/渠道 → 证明力等级。
2. 修改 `skills/orchestrator/SKILL.md`：在 subsumption 之后插入 evidence-discovery，新增 QC4b/QC6a。
3. 修改 `skills/fact-trimming/SKILL.md`：事实单元增加「可能证据来源」列。
4. 修改 `skills/subsumption/SKILL.md`：要件对照表增加「证明该要件通常需要的证据类型」列。
5. 修改 `skills/evidence-evaluation/SKILL.md`：输入增加 evidence-discovery 输出，评估时对照取证方案。
6. 修改 `SKILL.md`：description 补充实务取证触发词；标准调用链中 evidence-discovery 改为默认执行。
7. 修改 `README.md`：更新目录结构与版本差异说明。
8. 二次调整（2026-07-01）：evidence-discovery 从「按需」改为「默认执行」。
9. 三次调整（2026-07-01）：orchestrator 端到端流程全部阶段改为默认执行（case-retrieval、legal-interpretation、conflict-resolution、legal-consequence-calculation、fallback-application 均默认执行，不适用时标注"本阶段无需…"）；删除 backups 目录。

## 优化后评估

| 维度 | 权重 | 得分 | 简评 |
|------|------|------|------|
| 1. Frontmatter质量 | 7 | 9 | 总入口与 evidence-discovery 均补充了实务取证触发词 |
| 2. 工作流清晰度 | 12 | 9 | evidence-discovery 有 7 个明确步骤和 C-E 映射方法 |
| 3. 失败模式编码 | 12 | 8 | evidence-discovery 编码 7 种失败场景与降级路径 |
| 4. 检查点设计 | 6 | 7 | 新增 QC4b/QC6a，但 🔵/🔴 视觉标记仍可加强 |
| 5. 可执行具体性 | 17 | 8 | 输出模板具体到「获取主体/渠道/证明力/优先级/替代方案」 |
| 6. 资源整合度 | 4 | 9 | 新增 skill 路径正确，与现有 skill 输入输出衔接 |
| 7. 整体架构 | 7 | 9 | 新增原子 skill 后结构仍清晰，未超过原体积 150% |
| 8. 实测表现 | 23 | 8 | dry_run：对「实务取证」类 prompt 可输出获取渠道与证明力排序 |
| 9. 反例与黑名单 | 6 | 7 | evidence-discovery 增加 6 条反例黑名单 |
| 10. 本质工坊一致性 | 6 | 7 | evidence-discovery 应用坡度理解与三阶方法论 |

**优化后总分：约 81 / 110（A 级）**
**提升：+14 分（67 → 81）**

## 改动文件清单

- 新增：`skills/evidence-discovery/SKILL.md`
- 修改：`skills/orchestrator/SKILL.md`
- 修改：`skills/fact-trimming/SKILL.md`
- 修改：`skills/subsumption/SKILL.md`
- 修改：`skills/evidence-evaluation/SKILL.md`
- 修改：`SKILL.md`
- 修改：`README.md`
- 新增：`test-prompts.json`
- 新增：`optimization-log.md`
- 备份目录：`backups/20260701-1515/`
