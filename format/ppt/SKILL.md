---
name: PPT管线
description: |
  PPT格式管线：将认知产物转为.pptx演示文件。
  支持simple(python-pptx直接生成)和precise(HTML→pptxgenjs精确还原)两种模式。
  PPT不支持SVG/JS交互，富媒体元素需降级为PNG截图。
  输入：认知产物（文本+图形元素）。输出：.pptx文件。
  触发词：「做PPT」「做演示」「生成pptx」。
version: 1.0
layer: format
pipeline: ppt
---

# PPT管线

> 将认知产物转为 `.pptx` 演示文件。PPT 不支持 SVG 与 JS 交互，富媒体元素需降级为 PNG 截图。仅在客户明确要求 `.pptx` 或需企业模板时使用，其他场景推荐 Reveal 演示管线。

## 输入输出

- **输入**：认知产物的文本元素与图形元素（SVG 需降级为 PNG）
- **输出**：`.pptx` 文件（PowerPoint 2007+ 兼容），路径 `output/pptx/output.pptx`

## 两种模式

| 模式 | 实现 | 优点 | 缺点 |
|------|------|------|------|
| `simple`（默认） | python-pptx 直接生成 | Python生态一致 | 布局控制较粗 |
| `precise` | HTML → Playwright 读取 DOM → pptxgenjs 精确还原 | 布局精细 | 需 Node.js 环境 |

## 降级规则

PPT 不支持 SVG / JS 交互，所有富媒体元素必须降级：

| 元素 | 降级方案 | 保留信息 |
|------|---------|---------|
| SVG 图谱/流程图 | → PNG 截图（2x DPI） | 结构关系、流程步骤 |
| SVG 动画 | → 关键帧截图 | 关键状态 |
| Canvas 动画 | → 关键帧截图 | 关键帧 |
| 交互模块 | → 静态截图 | 外观布局 |

## 幻灯片结构映射

| Markdown | PPT幻灯片 | 说明 |
|----------|----------|------|
| H1 | 封面幻灯片 | 标题+副标题 |
| H2 | 章节分隔幻灯片 | 章节标题 |
| H3 | 内容幻灯片 | 正文内容 |
| 段落 | 文本框 | 正文 |
| 列表 | 要点列表 | 编号/项目符号 |
| 代码块 | 等宽字体文本框 | 代码 |
| 图片 | 图片占位 | PNG嵌入 |

## 生成流程

```
1. 从 output/elements/ 读取元素
2. SVG → PNG（Playwright 渲染，2x DPI）
3. SVG 动画 / Canvas → 关键帧截图
4. 文本元素 → 按 H1/H2/H3 拆分幻灯片
5. 加载 PPT 模板（可选企业 .potx）
6. 注入文本和图片
7. 输出 .pptx
```

## 格式约束

| 参数 | 标准 |
|------|------|
| 画幅 | 16:9（默认）或 4:3 |
| 文件大小 | ≤ 20MB |
| 字体 | 系统字体（不依赖外部字体） |

> 幻灯片页数、版式风格等由上层工作流决定，形式层只保证 .pptx 结构正确可打开。

## 失败模式

| 现象 | 处理 |
|------|------|
| python-pptx 未安装 | `pip install python-pptx` |
| 图片模糊 | 提高渲染分辨率（>2x DPI） |
| 文字溢出文本框 | 调整字号或精简文字 |
| 文件 > 20MB | 压缩图片 |
| 幻灯片过少/过多 | 合并或拆分 |

## 适用场景

客户明确要求 `.pptx`、需套用企业 `.potx` 模板、离线无浏览器、需他人编辑幻灯片。平台选择由上层场景层决定。

## 与其他管线的关系

- **HTML管线**：PPT = HTML − 交互 − SVG − 动画（HTML的降级版本）
- **Markdown管线**：提供文本来源，按 H1/H2/H3 拆分幻灯片
- **演示适配器（Reveal）**：另一种演示方案，平台选择由上层决定

## 脚本与命令

- 脚本：[scripts/generator.py](scripts/generator.py)（支持 `--mode simple/precise`、`--template`、`--brand-spec`）、[scripts/bridge.py](scripts/bridge.py)、[scripts/html2pptx.js](scripts/html2pptx.js)
- 命令：

```bash
python -m scripts.cli pptx --elements output/elements/ --output output/pptx/
python -m scripts.cli pptx --elements output/elements/ --output output/pptx/ --template corporate.potx
```

- references：[references.pptx-pipeline.md](references.pptx-pipeline.md)

## 质量自检

| 检查项 | 标准 |
|--------|------|
| 图片清晰度 | PNG 2x DPI |
| 文字可读 | 不溢出文本框 |
| 文件大小 | ≤ 20MB |
| 字体 | 系统字体 |

---

*PPT管线 · 文本+图形元素 → .pptx · 两种模式·富媒体降级为PNG*
