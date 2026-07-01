# law-application.skill · 法条适用认知框架（v2）

> 当前目录是 `law-application.skill` 的 v2 正式版本。
> v2 是原 v1 版本的原子化升级，将内嵌的 8 个认知框架拆分为可独立调用的原子 skill，并新增复合编排器与辅助 skill。

---

## 一、版本说明

| 版本 | 路径 | 定位 | 状态 |
|------|------|------|------|
| v1（已归档） | 历史版本 | 单一 mega-skill，8 个认知框架内嵌 | 已迁移 |
| v2（当前） | `distillation/output/law-application.skill/` | 总 skill + 原子 skill 族 + 复合编排器 | 当前正式版本 |

---

## 二、目录结构

```
law-application.skill/
├── SKILL.md                          # 总入口
├── README.md                         # 本文件
├── references/                       # 统一支撑材料
│   ├── essence/
│   │   ├── 01-what-essence.md
│   │   ├── 02-why-root-causes.md
│   │   └── 03-how-system.md
│   └── research/
│       ├── 01-definitions.md
│       ├── 02-origins.md
│       ├── 03-perspectives.md
│       ├── 04-cases.md
│       ├── 05-trends.md
│       ├── 06-controversies.md
│       └── 07-essence.md
└── skills/                           # 原子 skill 目录
    ├── orchestrator/                 # 复合编排器
    │   └── SKILL.md
    │
    ├── 核心原子技能（8 个）
    │   ├── fact-trimming/            # 事实裁剪
    │   ├── legal-relationship-typing/# 法律关系定性
    │   ├── norm-retrieval/           # 规范检索
    │   ├── subsumption/              # 涵摄
    │   ├── conflict-resolution/      # 冲突裁决
    │   ├── legal-interpretation/     # 法律解释
    │   ├── defense-and-validity-review/  # 抗辩与效力检视
    │   └── fallback-application/     # 兜底适用
    │
    └── 辅助原子技能（4 个）
        ├── case-retrieval/           # 案例检索
        ├── evidence-discovery/       # 证据发现（新增）
        ├── evidence-evaluation/      # 证据评估
        └── legal-consequence-calculation/  # 法律后果量化计算
```

---

## 三、核心设计

### 3.1 总 skill + 原子 skill 族

`law-application.skill/SKILL.md` 是总入口，负责：

- 说明技能定位与触发条件；
- 列出内部原子 skill；
- 指引默认入口（`skills/orchestrator`）。

原子 skill 存放在 `skills/` 目录下，每个只解决一个最小问题：

- 有明确的触发条件、输入/输出格式、边界与失败模式；
- 可被其他 skill 单独调用，也可被编排器组合。

### 3.2 复合编排

`skills/orchestrator` 是端到端分析的默认入口，负责：

- 接收用户输入；
- 按标准流程调度原子 skill；
- 设置质量检查点（QC）；
- 处理条件分支与回溯；
- 输出完整的法条适用分析报告。

标准调用链：

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

### 3.3 统一支撑材料

`references/` 目录存放整个技能的支撑材料，避免在每个原子 skill 中重复：

- `references/essence/`：本质、根因、系统运作说明；
- `references/research/`：定义、起源、观点、案例、趋势、争议、本质提炼。

### 3.4 检索策略：MCP 优先，联网搜索兜底

法条与案例检索采用**分层降级策略**：

| 层级 | 方式 | 说明 |
|------|------|------|
| 第一层 | 已配置 MCP 工具 | 北大法宝 MCP、秘塔搜索 MCP、其他法律法规 MCP |
| 第二层 | 模型/Agent 自身联网搜索 | 国家法律法规数据库、裁判文书网、人民法院案例库等 |
| 第三层 | 模型内部知识 | 仅作框架性提示，所有引用标注 `[待校验]` |

**校验要求**：
- 所有法条、案例引用必须标注来源、检索时间、效力状态；
- 优先通过至少两个独立来源交叉验证；
- 无法核验的引用标注 `[待校验]` 或 `[效力存疑]`。

---

## 四、使用方式

### 方式一：使用总入口（推荐）

直接激活 `law-application.skill/SKILL.md`，由它路由到默认入口 `skills/orchestrator`。

### 方式二：使用复合编排器

直接激活 `skills/orchestrator/SKILL.md`，输入具体事件描述，获得端到端分析报告。

### 方式三：单独使用原子 skill

根据需要单独调用某个原子 skill：

- 只需整理事实 → `skills/fact-trimming`
- 只需判断法律关系领域 → `skills/legal-relationship-typing`
- 只需检索法条 → `skills/norm-retrieval`
- 只需判断要件是否满足 → `skills/subsumption`

---

## 五、与 v1 的主要差异

| 维度 | v1 | v2（当前版本） |
|------|-----|-------------|
| 结构 | 单一 mega-skill | 总 skill + 原子 skill 族 + 复合编排器 |
| 支撑材料 | 内嵌于 skill 目录 | 统一 `references/` |
| 可调用性 | 8 个框架内嵌，无法单独调用 | 每个原子 skill 可独立调用 |
| 编排 | 无 | 有 `skills/orchestrator` 标准调用链与 QC |
| 检索策略 | 倾向绑定北大法宝 MCP | MCP 优先，模型/Agent 联网搜索兜底 |
| 证据法 | 缺失 | 新增 `evidence-discovery`：从要件到取证材料的反向映射 + `evidence-evaluation` |
| 请求权检视 | 一般性描述 | 九阶请求权检视 |
| 案例检索 | 薄弱 | 有 `skills/case-retrieval` |
| 量化计算 | 缺失 | 有 `skills/legal-consequence-calculation` |
| 输入/输出模板 | 较少 | 每个 skill 都有结构化模板 |
| 失败模式 | 不足 | 每个 skill 都有失败模式与降级路径 |

---

## 六、与 Legal-Skills-Chinese 的关系

本技能借鉴了 [Legal-Skills-Chinese](https://github.com/THUYRan/Legal-Skills-Chinese) 的以下方法论：

- 原子化 + 复合编排的架构设计；
- 请求权基础九阶检视；
- 证据能力 → 证明力 → 证明标准的审查路径；
- 法律后果量化计算思路；
- 质量检查点（QC）与回溯机制。

但本技能并非直接复制，而是基于本质工坊的"三阶方法论 × 坡度理解 × 类-属性-方法-路由"框架，结合用户的检索策略偏好（MCP 优先 + 联网搜索兜底）重新组织与实现。

---

## 七、免责声明

> 本技能输出内容仅供学习、研究与执业法律专业人员审阅参考，**不构成法律意见，不替代执业律师**。所有法条、案例、解释结论均需通过官方法律数据库复核确认。重大决策前请咨询执业法律专业人员。

---

## 八、迭代计划

| 阶段 | 任务 |
|------|------|
| 短期 | 试用 v2，收集反馈 |
| 中期 | 根据反馈优化原子 skill 与编排器 |
| 长期 | 与 Legal-Skills-Chinese 建立能力映射 |

---

*law-application.skill v2 由本质工坊 · 项目开发方法生成，基于 v1 升级而来。*
