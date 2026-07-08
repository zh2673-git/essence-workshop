---
name: Obsidian适配器
description: |
  Obsidian平台适配：将标准Markdown转为Obsidian兼容格式。
  适配项：图形引用转wiki-links（![[name.svg]]）、callout语法保留、双链支持、标签系统。
  输入：标准Markdown（来自format-pipeline/markdown）。输出：Obsidian兼容.md。
  触发词：「Obsidian」「做笔记」「知识库」。
version: 1.0
layer: platform
adapter: obsidian
---

# Obsidian适配器

> 将标准 Markdown 适配为 Obsidian 兼容格式：wiki-links、callout、双链、标签。Obsidian 是本地优先的知识库工具，适配重点在链接语法而非排版。

## 输入输出

| 项目 | 说明 |
|------|------|
| 输入 | 标准 Markdown（来自 format-pipeline/markdown） |
| 输出 | Obsidian 兼容 .md 文件 |

## 平台约束

| 约束 | 说明 |
|------|------|
| 图形引用 | Obsidian 使用 `![[name.svg]]` 而非标准 `![alt](path/name.svg)` |
| Callout | `> [!NOTE]` / `> [!WARNING]` / `> [!TIP]` 等callout语法 |
| 双链 | `[[笔记名]]` 创建双向链接，Obsidian自动建立反向链接 |
| 标签 | `#tag` 行内标签，支持嵌套 `#parent/child` |
| 附件目录 | 可配置 `attachments/` 或 `assets/`，Obsidian通过设置识别 |
| Frontmatter | 支持 YAML frontmatter，`tags` 字段被Obsidian识别为标签 |

## 适配流程

```
1. 读取标准 Markdown 文件（来自 format-pipeline/markdown）
2. 图形引用转换：![alt](assets/name.svg) → ![[name.svg]]
3. 保留 callout 语法（标准Markdown与Obsidian兼容）
4. （可选）文本内引用转换为双链：[笔记名](笔记名.md) → [[笔记名]]
5. （可选）注入 Obsidian 标签到 frontmatter
6. 输出 Obsidian 兼容 .md
```

## 失败模式

| 现象 | 处理 |
|------|------|
| wiki-link 不生效 | 检查文件名是否与 `[[]]` 内一致（含扩展名） |
| 附件不显示 | 确认附件在 Obsidian vault 目录内 |
| 双链断裂 | 目标笔记不存在时 Obsidian 会标红，需创建或修正链接 |
| frontmatter 不被识别 | 检查 YAML 格式，`tags` 应为列表或空格分隔 |

## 质量自检

| 检查项 | 标准 |
|--------|------|
| 图形引用 | 全部为 `![[name.svg]]` 格式 |
| 附件可达 | 所有附件在 vault 目录内 |
| 双链有效 | `[[]]` 内的笔记名与实际文件名匹配 |
| callout | `> [!TYPE]` 语法正确 |
| 编码 | UTF-8 无 BOM |

## 脚本

Obsidian 适配逻辑归属本适配器实现（标准 Markdown → Obsidian 兼容格式：wiki-links、双链、callout、标签）。上游输入由 `format-pipeline/markdown` 提供标准 Markdown，本适配器执行平台专属转换。

## 与其他适配器的关系

| 适配器 | 输入格式 | 输出 | 与Obsidian的区别 |
|--------|---------|------|-----------------|
| **Obsidian** | 标准.md | Obsidian .md | wiki-links + 双链 + 标签 |
| 公众号 | .md/.html | 受限HTML | 内联样式 + 素材库上传 |
| Reveal | .md/.html | 演示HTML | 幻灯片结构 + CDN |

## references

- Obsidian 官方文档：https://help.obsidian.md/

---

*Obsidian适配器 · 标准.md → Obsidian.md · wiki-links + 双链 + 标签 · 本地知识库*
