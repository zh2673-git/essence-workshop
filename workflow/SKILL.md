---
name: 工作流层
description: 具体做事流程的编排层。工作流 = 认知×框架×格式×平台的组合。平台只是工作流的一部分，不以平台去划分。当工作场景固定时，沉淀为工作流。本层记录具体做事的整套流程，产物存放在各工作流的 output/ 目录。
version: 1.1
layer: workflow
---

# 工作流层 · 具体流程编排路由

> **v4.1 工作流层**：本质工坊四层架构的第四层。
> 工作流层根据目标任务，对整个流程进行编排。比如做一个K12课件：先通过框架层选择课件框架，然后选择html形式（符合基础html形式），然后把课件保存到K12工作流的output文件夹。
> 工作流 = 认知 × 框架 × 格式 × 平台 的组合。平台只是工作流的一部分，不以平台去划分。

---

## 架构说明

工作流是"具体做事流程"的编排。工作流层只记录整套流程，不生成认知、不定义框架、不做格式转换（这些由前三层负责）。

工作流分两类：
- **平台交付工作流**：固定交付目标的平台编排（公众号/白板/视频号等）
- **场景流程工作流**：固定场景的流程编排（K12课件/连载小说/项目开发/蒸馏等）

产物存放在各工作流的 `output/` 目录下。

---

## 平台交付工作流（9 个）

| 工作流 | 交付目标 | 路径 |
|--------|---------|------|
| 公众号发布 | 微信公众号草稿/文章 | [wechat-publish/](wechat-publish/SKILL.md) |
| 白板录制 | 白板动画视频 | [whiteboard-recorder/](whiteboard-recorder/SKILL.md) |
| 视频号 | 短视频 | [video-channel/](video-channel/SKILL.md) |
| 浏览器交互 | 交互式HTML | [browser-interactive/](browser-interactive/SKILL.md) |
| Reveal幻灯片 | 演示文稿 | [reveal-slides/](reveal-slides/SKILL.md) |
| PPT/WPS | PPT文件 | [ppt-wps/](ppt-wps/SKILL.md) |
| Jupyter Notebook | 可执行笔记本 | [jupyter-notebook/](jupyter-notebook/SKILL.md) |
| Obsidian知识管理 | Obsidian笔记 | [obsidian-knowledge/](obsidian-knowledge/SKILL.md) |
| 项目交付 | 项目代码+文档 | [project-delivery/](project-delivery/SKILL.md) |

## 场景流程工作流（9 个）

| 工作流 | 流程说明 | 路径 |
|--------|---------|------|
| K12课件工作流 | 拆解→生成HTML→保存到output | [k12-decomposition/](k12-decomposition/A2-knowledge-decomposition.md) |
| 知识探索工作流 | 探索→生成笔记→保存到output | [knowledge-exploration/](knowledge-exploration/A-knowledge-exploration.md) |
| 连载小说工作流 | 世界观→人物→章节→推送 | [serial-fiction/](serial-fiction/SF-serial-fiction.md) |
| 项目开发工作流 | 本质→架构→模块→交付 | [project-dev/](project-dev/C-project-development.md) |
| 项目迭代工作流 | Ratchet Loop迭代循环 | [project-dev/iterative-loop.md](project-dev/iterative-loop.md) |
| 五蕴法口播稿工作流 | 主题→五蕴结构→风格润色→口播稿 | [broadcast-script/](broadcast-script/SKILL.md) |
| 项目解析工作流 | 逆向分析→反推报告 | [project-analysis/](project-analysis/D-project-analysis.md) |
| 法律分析工作流 | 编排法律适用框架12原子skill | [law-analysis/](law-analysis/SKILL.md) |
| 蒸馏工作流 | 人物/话题蒸馏→生成Skill→存output | [distillation/](distillation/B-person-distillation.md) |
| 周易占卜工作流 | 认知×框架×HTML×浏览器→交互占卜 | [iching-divination/](iching-divination/SKILL.md) |

---

## 工作流编排公式

```
工作流 = 认知（选择视角）× 框架（选择内容框架）× 格式（选择输出格式）× 平台（选择交付目标）
```

四因子相乘，缺一不可。前三个因子由前三层提供，平台因子由工作流自身承载。

---

## 示例

- **K12课件工作流** = 认知(通用逻辑) × 框架(K12课件设计) × 格式(HTML) × 平台(浏览器) → output/存HTML课件
- **口播白板录制** = 认知(任意) × 框架(高考作文) × 格式(markdown+白板) × 平台(白板录制器)
- **公众号文章** = 认知(任意) × 框架(任意) × 格式(MD) × 平台(公众号)
- **蒸馏工作流** = 认知(通用逻辑) × 框架(蒸馏框架) × 格式(Skill) × 平台(-) → output/存蒸馏Skill

---

## 与其他层的关系

- **调用**：cognitive/（认知层）、content-framework/（内容框架层）、format/（形式层）
- **本层职责**：只编排具体做事流程，不生成认知、不定义框架、不做格式转换

---

## 共享脚本

[scripts/platforms/](scripts/platforms/) 下有平台实现脚本（`base.py` 基类 + 各平台实现）。

---

*工作流层 · v1.1 · 认知 × 框架 × 格式 × 平台 · 平台工作流9个 + 场景工作流10个*
