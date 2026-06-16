---
name: "iterative-loop"
description: |
  通用项目迭代开发闭环。借鉴autoresearch Ratchet Loop。
  方案→执行→测试→评估→保留/回退→迭代。适用于任何项目的增量迭代开发。
  Invoke when user wants to iterate on a project, build something incrementally,
  or follow the plan-build-test-iterate loop for any development.
---

# 迭代开发闭环（Ratchet Loop）

> 核心循环：**方案 → 执行 → 测试 → 评估 → 保留/回退 → 下一轮**
> 借鉴 Karpathy autoresearch 的 Ratchet Loop：棘轮只进不退
> 适用于任何项目，不限于特定领域

---

## 0. 触发条件

- 用户说「迭代开发XX」「从0到1构建XX并迭代」
- 用户说「继续迭代」「下一轮」「v+1」
- 用户有项目需要增量改进
- 用户说「构建agent」「开发系统」且暗示需要迭代

---

## 1. 项目形态

迭代开发统一使用**项目代码模式**：

```
project-root/
├── program.md              # 迭代策略（人类编写）
├── core/                   # 基础设施（不修改）
│   └── ...
├── src/                    # 项目核心逻辑（迭代修改）
│   └── ...
├── tests/                  # 测试（pytest）
│   └── ...
├── docs/
│   ├── plan-v1.md          # 方案文档
│   ├── test-report-v1.md   # 测试报告
│   └── ...
├── pyproject.toml          # 项目依赖
└── results.tsv             # 评估结果记录
```

> **教学notebook**：开发完成后，可通过场景E的notebook管线将项目代码转化为教学notebook。详见 [../content-output/E-content-output.md](../content-output/E-content-output.md) 的「notebook管线」章节。

---

## 2. 闭环流程（Ratchet Loop）

```
┌──────────────────────────────────────────────────────┐
│                  Ratchet Loop                        │
│                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │  写方案   │──→│  执行    │──→│  测试    │        │
│  │ plan-vN  │   │ 构建/更新 │   │ test_vN  │        │
│  └──────────┘   └──────────┘   └──────────┘        │
│                                       │              │
│                                       ↓              │
│                               ┌──────────────┐      │
│                               │   评估       │      │
│                               │ 对比指标     │      │
│                               └──────┬───────┘      │
│                                      │              │
│                              ┌───────┴───────┐      │
│                              ↓               ↓      │
│                        ┌─────────┐   ┌─────────┐   │
│                        │ 改进    │   │ 退步    │   │
│                        │ 保留    │   │ 回退    │   │
│                        │ commit  │   │ revert  │   │
│                        └────┬────┘   └────┬────┘   │
│                             │             │         │
│                             ↓             ↓         │
│                        写新方案 ←── 记录失败原因     │
│                             │                       │
│                             → 回到写方案             │
└──────────────────────────────────────────────────────┘
```

### 每轮产出

| 产出 | 文件位置 | 命名规则 | 说明 |
|------|---------|---------|------|
| 方案文档 | `docs/plan-v{N}.md` | 增量，不覆盖 | 本轮要做什么、为什么、怎么做 |
| 代码 | `src/` | 原地更新，标注版本 | 按方案构建或更新 |
| 测试报告 | `docs/test-report-v{N}.md` | 增量，不覆盖 | 测试结果、发现问题、下轮方向 |
| 实验记录 | `results.tsv` | 追加 | 所有实验（成功+失败） |

---

## 3. 三文件架构（项目代码模式）

借鉴 autoresearch 的 `prepare.py + train.py + program.md`，泛化为任意项目：

| autoresearch | 通用映射 | 职责 | 谁修改 |
|-------------|---------|------|-------|
| `prepare.py` | `core/` | 基础设施、常量、工具函数 | 不修改 |
| `train.py` | `src/` | 项目核心逻辑 | 迭代修改 |
| `program.md` | `program.md` | 迭代策略、评估标准 | 人类编写 |

**核心原则**：
- 基础设施不动（`core/`），保证迭代不会破坏底层
- 只改目标代码（`src/`），范围可控，diff可读
- 人类通过 `program.md` 控制方向，不直接改代码

### program.md 模板

详见 [templates/program.md](templates/program.md)

---

## 4. Phase 1: 写方案

### 4.1 首轮方案（v1）

```markdown
# 方案 v1

## 1. 目标
[一句话描述最终要构建什么]

## 2. 核心架构
[系统的最简设计]

## 3. 渐进式构建步骤
| 步骤 | 功能 | 产出文件 | 依赖 |
|------|------|---------|------|
| Step 01 | ... | 01-xxx.py | 无 |
| ... | ... | ... | ... |

## 4. 正交增量原则
- 每步独立可运行
- 新步不修改旧步代码
- 功能正交，只做增量

## 5. 验证契约

### 5.1 前置条件 P（构建前必须为真）
| 条件 | 含义 | 验证方式 |
|------|------|---------|
| 环境就绪 | 依赖已安装、配置正确 | 运行环境检查脚本 |
| 基线锁定 | 首轮结果已记录为基线 | results.tsv有基线记录 |
| 测试可运行 | 测试脚本本身无bug | 先跑一轮基线测试 |

### 5.2 后置条件 Q（构建后必须为真）
| 条件 | 含义 | 验证方式 |
|------|------|---------|
| 功能正确 | 新功能按预期工作 | 测试用例通过 |
| 指标达标 | 主指标达到目标值 | results.tsv对比 |
| 无副作用 | 改动不超出预期范围 | diff检查 |

### 5.3 不变量 I（全程必须保持为真）
| 条件 | 含义 | 验证方式 |
|------|------|---------|
| 旧功能不坏 | 已有测试仍然通过 | 回归测试 |
| 接口不破 | 对外接口契约不变 | 接口兼容性检查 |
| 约束不违 | program.md的约束未被违反 | 改动范围检查 |

### 5.4 不可验证项（显式标注）
| 功能 | 为什么不可验证 | 替代验证方式 |
|------|--------------|------------|
| [如有] | [原因] | [人工review等] |
```

### 4.2 后续方案（vN, N≥2）

```markdown
# 方案 v{N}

## 1. 上轮问题
[从test-report-v{N-1}.md中提取的问题]

## 2. 本轮改进
| 问题 | 改进方案 | 影响文件 |
|------|---------|---------|
| [问题1] | [方案1] | [文件名] |

## 3. 详细设计
[改进的技术方案，含代码片段]

## 4. 验证契约变更
| 变更类型 | 变更内容 | 原因 |
|---------|---------|------|
| 新增后置条件 | [新增的验收条件] | [为什么需要] |
| 修改不变量 | [修改的不变量] | [为什么修改] |
| 无变更 | — | 契约不变 |

## 5. 评估预期
[本轮改进预期对验证契约各维度的影响]
```

### 4.3 方案原则

- **增量不覆盖**：新方案文件带版本号，旧文件保留
- **问题驱动**：v2+的方案必须基于上轮测试报告的问题
- **最小改动**：只改需要改的，不做额外优化
- **可验证**：每个改进都有对应的测试用例
- **单维度改动**：每次只改一个维度，便于归因
- **契约先行**：方案必须包含验证契约，否则不进入执行阶段
- **契约稳定**：验证契约尽量不变，变更是重大决策需显式标注

---

## 5. Phase 2: 执行

### 5.1 项目结构

```
project-root/
├── program.md              # 迭代策略（人类编写）
├── core/                   # 基础设施（不修改）
│   ├── __init__.py
│   ├── config.py           # 常量、配置
│   └── utils.py            # 工具函数
├── src/                    # 目标代码（迭代修改）
│   ├── __init__.py
│   └── {module}.py
├── tests/                  # 测试文件
│   ├── test_{module}.py
│   └── conftest.py
├── docs/
│   ├── plan-v1.md
│   ├── test-report-v1.md
│   └── ...
├── .env                    # 环境配置（如有）
├── pyproject.toml          # 项目依赖
└── results.tsv             # 评估结果记录
```

### 5.2 执行检查

- [ ] 方案中的每个改进都已实现
- [ ] 更新的文件标注了版本号
- [ ] 只修改了program.md允许的范围
- [ ] 环境配置正确

---

## 6. Phase 3: 验证 + 评估 + 决策（Ratchet核心）

### 6.1 三维验证

验证不是单点测试，而是三个维度的全链路验证：

```
前置条件 P（构建前）──→ 后置条件 Q（构建后）──→ 不变量 I（全程）
     ↓                       ↓                       ↓
  validate_pre()         validate_post()         validate_inv()
```

**执行顺序**：

1. **validate_pre()**：前置条件检查（进入执行前）
   - 环境是否一致？
   - 基线是否锁定？
   - 测试脚本是否可运行？

2. **validate_post()**：后置条件检查（实现完成后）
   - 新功能是否正确？
   - 评估指标是否改善？
   - 改动是否在预期范围内？

3. **validate_inv()**：不变量检查（每轮必须）
   - 旧功能是否仍然通过？
   - 对外接口是否兼容？
   - program.md约束是否被违反？

### 6.2 运行测试

```bash
pytest tests/ -v
```

### 6.3 三维判定逻辑

```
validate_pre() 失败  → 阻断，不进入执行
validate_post() ✅ AND validate_inv() ✅ → 保留（commit）
validate_post() ✅ AND validate_inv() ❌ → 回退（退步被误判为改进）
validate_post() ❌ AND validate_inv() ✅ → 回退（改动无效但未破坏）
validate_post() ❌ AND validate_inv() ❌ → 回退（双重退步）
```

| P | Q | I | 决策 | 动作 |
|---|---|---|------|------|
| ❌ | - | - | **阻断** | 修复前置条件，不进入执行 |
| ✅ | ✅ | ✅ | **保留** | `git commit` + 更新results.tsv |
| ✅ | ✅ | ❌ | **回退** | `git revert HEAD` + 记录不变量失败原因 |
| ✅ | ❌ | ✅ | **回退** | `git revert HEAD` + 记录后置条件失败原因 |
| ✅ | ❌ | ❌ | **回退** | `git revert HEAD` + 记录双重失败原因 |

> **关键洞察**：Q通过但I失败是最危险的场景——新功能看似正确，但悄悄破坏了旧功能。没有不变量检查，退步会被误判为改进，导致棘轮失效。

### 6.4 results.tsv 格式

```tsv
experiment_id	timestamp	change_description	pre_post	post_result	inv_result	kept
001	2026-06-16T10:00	[改动描述]	✅	✅	✅	true
002	2026-06-16T10:15	[改动描述]	✅	✅	❌	false
003	2026-06-16T10:30	[改动描述]	✅	✅	✅	true
```

### 6.5 测试报告模板

```markdown
# 测试报告 v{N}

## 1. 迭代历程总览
| 版本 | 关键发现 | 核心改进 | P | Q | I |

## 2. 三维验证结果
| 维度 | 检查项 | 结果 | 说明 |
|------|-------|------|------|
| P 前置 | 环境一致 | ✅/❌ | |
| P 前置 | 基线锁定 | ✅/❌ | |
| Q 后置 | 功能正确 | ✅/❌ | |
| Q 后置 | 指标改善 | ✅/❌ | |
| I 不变量 | 旧功能通过 | ✅/❌ | |
| I 不变量 | 接口兼容 | ✅/❌ | |

## 3. Ratchet决策
| 改动 | P | Q | I | 决策 | 原因 |

## 4. 关键突破
[详细描述本轮解决的核心问题]

## 5. 待解决问题（下轮方向）
| 问题 | 严重度 | 可能方案 |

## 6. 实验记录
[从results.tsv中提取本轮实验]
```

### 6.6 通用测试原则

- **打印完整过程**：不只是pass/fail，要看到中间状态
- **问题导向**：测试目标是发现问题，不只是验证正确
- **三维全过**：P+Q+I全部通过才保留，任一维度失败则回退
- **不变量必检**：每轮必须运行回归测试，不可跳过
- **改进才提交**：git commit只在三维验证全通过时触发
- **退步必回退**：任一维度失败，必须回退
- **失败也记录**：results.tsv记录所有实验，失败的经验同样有价值

---

## 7. 迭代收敛判断

### 何时停止迭代？

| 条件 | 说明 |
|------|------|
| 测试全部通过 | 无FAIL项 |
| 评估指标达标 | 达到program.md定义的目标值 |
| 连续2轮无改进 | 棘轮不再前进，说明已到当前方案上限 |
| 达到最大轮数 | 强制停止（默认10轮），总结当前状态 |

### 何时继续迭代？

| 信号 | 行动 |
|------|------|
| 测试有FAIL | 修复后重新测试 |
| 发现兼容性问题 | 新增模块或更新方案 |
| 功能不完整 | 继续构建新模块 |
| 主指标未达标 | 继续迭代 |

---

## 8. 通用经验库

### 常见陷阱（跨领域通用）

| 陷阱 | 症状 | 通用解决方案 |
|------|------|-------------|
| 兼容性差异 | 兼容层功能缺失 | 先验证API/接口完整性再使用 |
| 测试脚本bug | 循环导入、环境问题 | 独立测试脚本，不跨文件导入 |
| 连续回退 | 5轮以上无改进 | 暂停迭代，人类审查program.md |
| 过早优化 | 偏离核心目标 | 先跑通再优化 |
| 评估指标模糊 | 无法量化决策 | 退回标准模式，先明确指标 |

### 领域特定经验

不同项目类型有各自的陷阱和经验，在 `program.md` 中补充领域特定内容。参见下方案例。

---

## 9. 案例：AI Agent迭代开发

> 以下是从4轮AI Agent构建迭代中提炼的领域特定经验。
> 仅作为案例参考，非通用方法论。

### Agent领域常见陷阱

| 陷阱 | 症状 | 解决方案 |
|------|------|---------|
| thinking模式 | content为空 | Ollama原生API + think=False |
| 工具调用后无答案 | 只有tool_calls无content | 追加总结轮 |
| 超时 | 大模型推理慢 | 小模型先验证，增大timeout |

### Agent领域：双API策略

| 场景 | API | 参数 |
|------|-----|------|
| 工具调用 | OpenAI兼容 `/v1/chat/completions` | tools参数 |
| 获取thinking | Ollama原生 `/api/chat` | think=True |
| 关闭thinking | Ollama原生 `/api/chat` | think=False |
| 生成总结 | Ollama原生 `/api/chat` | think=False, max_tokens=200 |

### Agent领域：核心代码片段

**Ollama原生API调用**：
```python
def ollama_chat(messages, model=None, think=False, max_tokens=30, timeout=60):
    payload = {
        "model": model or MODEL,
        "messages": messages,
        "stream": False,
        "think": think,
        "options": {"num_predict": max_tokens}
    }
    resp = requests.post(f"{OLLAMA_BASE}/api/chat", json=payload, timeout=timeout)
    data = resp.json()
    msg = data.get("message", {})
    content = msg.get("content", "")
    thinking = msg.get("thinking", "")
    if not content.strip() and thinking.strip():
        content = thinking
    return {"content": content, "thinking": thinking, "duration": data.get("total_duration", 0)/1e9}
```

**总结轮兜底**：
```python
def _generate_summary(self, messages):
    tool_results = [m["content"] for m in messages if isinstance(m, dict) and m.get("role") == "tool"]
    if not tool_results:
        return None
    summary_prompt = f"基于以下工具调用结果，简洁回答用户的问题：\n" + "\n".join(tool_results)
    result = ollama_chat(
        [{"role": "user", "content": summary_prompt}],
        model=self.models[0], think=False, max_tokens=200
    )
    return result['content'] if result['content'].strip() else None
```

### Agent迭代历程

| 版本 | 关键发现 | 核心改进 |
|------|---------|---------|
| v1 | thinking模式导致content为空 | 新增3个课件 |
| v2 | OpenAI兼容API不暴露reasoning_content | Ollama原生API验证 |
| v3 | 双API策略可行 | thinking获取+关闭 |
| v4 | RobustAgent工具调用后无答案 | 总结轮兜底，4/4通过 |

---

## 10. 与本质工坊的关系

本skill是本质工坊项目开发场景（场景C）迭代模式的独立入口。

```
本质工坊场景C（项目开发）
├── 标准模式：设计→实现→交付
└── 迭代模式：设计→实现→测试→评估→保留/回退→下一轮
    └── 即本skill的Ratchet Loop

场景C迭代模式 → 收敛 → 场景B2（蒸馏）→ 沉淀为Skill
```

详细文档：
- 本质工坊项目开发场景：[project-dev/SKILL.md](SKILL.md)
- 迭代模式流程：[C-project-development.md](C-project-development.md)
- 棘轮循环参考：[references/ratchet-loop.md](references/ratchet-loop.md)
- program.md模板：[templates/program.md](templates/program.md)

---

## 11. 执行检查清单

### 每轮开始前

- [ ] 读取上轮测试报告（如有）
- [ ] 读取program.md（项目代码模式）
- [ ] 确认本轮要解决的问题
- [ ] 写方案文档 `docs/plan-v{N}.md`

### 执行中

- [ ] 按方案构建/更新代码
- [ ] 只修改program.md允许的范围
- [ ] 更新的文件标注版本号

### 测试后

- [ ] 运行测试
- [ ] 评估指标 vs 当前最佳
- [ ] 决策：保留（commit）或回退（revert）
- [ ] 更新results.tsv
- [ ] 写测试报告 `docs/test-report-v{N}.md`
- [ ] 提取待解决问题
- [ ] 判断是否需要下一轮

### 迭代收敛后

- [ ] 调用本质工坊蒸馏场景，沉淀为Skill
- [ ] 产出skill文件

---

> 本skill借鉴 autoresearch Ratchet Loop 设计，适用于任何项目的迭代开发
> 方法论：正交增量 + 测试驱动发现 + 版本化沉淀 + Ratchet Loop
> 参考：Karpathy autoresearch (https://github.com/karpathy/autoresearch, March 2026)
