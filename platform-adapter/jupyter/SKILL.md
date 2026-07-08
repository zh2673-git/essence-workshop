---
name: Jupyter平台
description: |
  Jupyter平台适配器：将Notebook格式产物（.ipynb）适配为Jupyter环境可运行的成品。
  关注cell结构、kernel规范、输出清理、依赖说明。
  输入：Notebook格式产物（.ipynb）。输出：Jupyter可运行的.ipynb成品。
  触发词：「做notebook」「Jupyter版」「教学notebook」。
version: 1.0
layer: platform
adapter: jupyter
---

# Jupyter平台适配器

> 将Notebook格式产物适配为Jupyter环境可运行的交互式教学成品。

## 平台约束

| 约束项 | 说明 |
|--------|------|
| 格式 | .ipynb（Jupyter Notebook 4.x+） |
| Kernel | Python 3（默认）；需标注所需kernel和依赖 |
| Cell结构 | Markdown cell（讲解）+ Code cell（示例）交替；每个Code cell后有Output cell |
| 输出 | 分发版清除所有Output（用户运行后生成）；教学版保留关键Output |
| 依赖 | 首个cell必须含 `!pip install` 或 requirements说明 |
| 文件大小 | 建议<10MB（含图片） |

## Notebook结构规范

Cell结构（内容编排）由 format-pipeline/notebook 按上层指定的模板生成，本适配器不定义cell内容结构，只负责平台兼容性处理（kernel/依赖/输出清理）。

## 适配流程

```
1. Notebook格式产物（.ipynb）→ 检查cell结构
2. 验证kernel规范（Python 3）
3. 注入依赖安装cell（首个code cell）
4. 清理Output（分发版）或保留关键Output（教学版）
5. 检查Markdown cell的格式（标题/列表/代码块）
6. 导出 .ipynb 成品
```

## 与格式管线的关系

| 层级 | 职责 |
|------|------|
| **格式管线（notebook/）** | 从认知产物生成.ipynb文件（内容+cell结构） |
| **平台适配（本适配器）** | 将.ipynb适配为Jupyter可运行成品（kernel+依赖+输出） |

## 脚本

```
jupyter/
└── scripts/                    # 适配脚本（规划中）
    └── adapter.py              # .ipynb→Jupyter可运行.ipynb
```

格式管线脚本：[../../format-pipeline/notebook/scripts/generator.py](../../format-pipeline/notebook/scripts/generator.py)
共享平台脚本：[../scripts/platforms/jupyter.py](../scripts/platforms/jupyter.py)

## 使用场景

- 知识探索的可执行教学notebook
- 项目开发后的教学转化
- 迭代开发收敛后的经验沉淀

---

*Jupyter平台 · .ipynb→Jupyter可运行.ipynb · Python 3 kernel*
