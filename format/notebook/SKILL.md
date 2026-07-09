---
name: Notebook管线
description: |
  Jupyter Notebook格式管线：将认知产物或项目代码转化为可交互的教学/演示Notebook。
  核心价值：项目代码是源，notebook是视图。支持3种教学结构（项目开发类/知识探索类/蒸馏类）。
  输入：认知产物或项目代码。输出：.ipynb文件。
  触发词：「做notebook」「教学notebook」「可执行文档」。
version: 1.0
layer: format
pipeline: notebook
---

# Notebook管线

> 将认知产物或项目代码转化为可运行的教学/演示 Jupyter Notebook。核心定位：项目代码是源，notebook 是视图——notebook 不是开发模式，而是开发成果的表达形式。

## 输入输出

- **输入**：认知产物或项目代码（来源由上层场景指定）

- **输出**：`.ipynb` 文件，命名规则 `{序号}-{项目名}.ipynb`（如 `01-build-agent.ipynb`）

## Cell类型规范

| Cell类型 | 用途 | 规则 |
|---------|------|------|
| Markdown Cell | 解释「为什么」而非「做了什么」 | 含步骤序号、设计决策说明 |
| Code Cell | 可运行代码片段 | 每 cell 只做一件事、可独立运行、关键步骤后有 print/assert、import 集中在最前 |
| Output Cell | 代码运行结果 | 必须实际运行生成，不手写；失败输出保留（教学价值） |

## 3种教学结构模板

> 模板由上层通过 `--template` 参数指定，格式层不自行选择。以下为可选模板：

### 项目开发类（场景C/D）
环境准备 → 核心概念（解释+最小实现+验证）→ ... → 完整系统（组合+端到端测试）→ 总结

### 知识探索类（场景A/A2）
直觉理解（类比+演示）→ 形式化定义（数学+从零实现）→ 验证与实验（参数变化+边界条件）→ 总结

### 蒸馏类（场景B）
思维模型（核心心智模型）→ 决策启发式（规则+案例演示）→ 场景应用（路由+验证）→ 总结

## 生成流程

```
1. 读取上层指定的模板类型（--template 参数）
2. 加载对应教学结构模板
3. 提取核心概念与代码片段
4. 按模板组织 cell（Markdown + Code 交替）
5. 清理非教学代码（日志、边界处理、异常捕获）
6. 验证可运行性（从头到尾顺序执行）
7. 输出 .ipynb
```

## 技术约束

- **可运行**：所有 Code cell 从头到尾顺序运行无报错
- **渐进式**：每个 cell 建立在前一个之上
- **有验证**：关键步骤后有 `assert` 或 `print`
- **有解释**：Markdown cell 解释「为什么」
- **可修改**：读者修改参数后能观察不同结果
- **无冗余**：删除非教学代码
- **import 集中**：所有 import 在最前面的 cell

## 失败模式

| 现象 | 原因 | 处理 |
|------|------|------|
| 代码不可运行 | 依赖顺序错误或缺失 | 检查 import 顺序与前序 cell |
| 缺解释 | 只有 Code 无 Markdown | 补 Markdown cell 说明设计决策 |
| cell 过大 | 一个 cell 做多件事 | 拆分为多个单一职责 cell |
| 输出手写 | Output Cell 与代码不一致 | 实际运行生成输出 |

## 与其他管线的关系

- **Markdown管线**：提供文本来源，可转为 Markdown Cell
- **HTML管线**：知识拆解HTML可作为 A2 场景输入
- **平台适配**：项目代码来自 `workflow/project-delivery`，notebook 可视为其教学视图

## 脚本与references

- 脚本：[scripts/generator.py](scripts/generator.py)
- references：[references.notebook-pipeline.md](references.notebook-pipeline.md)

## 质量自检

| 检查项 | 标准 |
|--------|------|
| 可运行 | 从头到尾顺序运行无报错 |
| 渐进式 | cell 之间有递进关系 |
| 有验证 | 关键步骤后有 assert/print |
| 有解释 | Markdown 解释「为什么」 |
| 无冗余 | 非教学代码已删除 |
| import集中 | 所有 import 在最前 cell |

---

*Notebook管线 · 认知产物/项目代码 → .ipynb · 项目代码是源·notebook是视图*
