---
name: Markdown管线
description: |
  Markdown格式管线：将认知产物的文本元素和图形元素转换为标准Markdown文档。
  最通用的跨平台管线，是其他管线的文本来源。产出标准Markdown，平台特定适配（如Obsidian wiki-links）由工作流层处理。
  输入：认知产物（文本+SVG元素）。输出：标准.md文件。
  触发词：「写文档」「做笔记」「Markdown输出」。
version: 1.0
layer: format
pipeline: markdown
---

# Markdown管线

> 将认知产物的文本与图形元素合并为标准 Markdown 文档。作为最通用的跨平台管线，是其他管线的文本来源。本管线只产出标准 Markdown，平台特定适配（如 Obsidian wiki-links）由工作流层处理。

## 输入输出

- **输入**：元素层中的文本元素（`elements/text/*.md`）与图形元素（`elements/graphics/*.svg`）
- **输出**：标准 `index.md` 文件，结构为 `frontmatter + 标题 + 正文 + 图形引用`，SVG 附件归档到 `assets/` 子目录

## 生成流程

```
1. 读取 elements/text/*.md 文本元素（按文件名排序）
2. 读取 elements/graphics/*.svg 图形元素
3. SVG 复制到 assets/ 子目录，文件名 sanitize
4. 合并文本 sections（保持原序）
5. 文末追加「## 图形」段落，注入标准图形引用 ![alt](assets/name.svg)
6. 拼接 frontmatter + H1标题 + 正文
7. 输出 index.md
```

## 技术约束

- **附件存放**：所有 SVG 存放到 `assets/` 子目录（可通过 `--attachment-dir` 配置）
- **文件名 sanitize**：保留中文/字母/数字/连字符，其他字符替换为 `_`（正则 `[^\w\-\.\u4e00-\u9fff]`）
- **标题提取**：从首份文本的首个 `# ` 行提取；缺失时回退为「笔记」
- **frontmatter**：必含 `title` 字段
- **编码**：UTF-8
- **图形引用**：使用标准 Markdown 语法 `![alt](assets/name.svg)`，平台特定转换（如 Obsidian `![[name.svg]]`）由工作流层处理

## 风格支持

支持全部 8 种输出风格：论文 / 专栏 / 故事 / 教程 / 观点 / 对话 / 蒸馏Skill / 连载。风格由认知层决定，管线层仅负责格式化落地。

## 失败模式

| 现象 | 原因 | 处理 |
|------|------|------|
| 文本元素为空 | `elements/text/` 不存在或无 `.md` | 检查元素层产出 |
| SVG 引用失效 | 文件名含特殊字符未 sanitize | 走 `_sanitize_filename` 规范化 |
| 标题回退为「笔记」 | 文本无 `# ` 行 | 显式传入 `--title` |

## 与其他管线的关系

- **定位**：最通用管线，是其他管线的文本来源
- **下游复用**：产物可被 HTML / PPT / Notebook 等管线复用为文本基础
- **音频管线**：Markdown 文本是音频脚本的来源
- **平台适配**：标准 .md 交付到工作流层（Obsidian 适配器做 wiki-links 转换、公众号适配器做排版适配等）

## 脚本与命令

- 脚本：[scripts/generator.py](scripts/generator.py)
- 命令：

```bash
python -m scripts.pipelines.markdown.generator \
  --elements output/elements/ \
  --output output/markdown/ \
  --title "笔记标题"
```

## 质量自检

| 检查项 | 标准 |
|--------|------|
| 标题正确 | frontmatter 与 H1 一致 |
| 图形引用 | 所有 SVG 在 `assets/` 且被标准语法引用 |
| 编码 | UTF-8 无 BOM |
| 标准Markdown | 无平台特定语法（wiki-links等） |

---

*Markdown管线 · 文本+SVG元素 → 标准.md · 最通用跨平台文本来源 · 平台适配交给平台层*
