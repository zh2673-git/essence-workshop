# PPT管线规范（PPTX Pipeline）

> 从元素层读取 → 降级转换 → python-pptx/PptxGenJS → .pptx

---

## 管线概览

```
元素层读取 → 幻灯片结构生成 → 元素降级转换 → PPT生成 → .pptx文件
```

## 元素消费与转换

| 元素类型 | 转换规则 | 说明 |
|---------|---------|------|
| 文本元素 | Markdown → PPT文本框 | H1→封面，H2→分隔，H3→内容 |
| SVG图形 | SVG → PNG → PPT图片 | SVG无法直接嵌入pptx |
| SVG动画 | 截取关键帧 → PPT图片 | PPT不支持SVG动画 |
| Canvas动画 | 截取关键帧 → PPT图片 | PPT不支持Canvas |
| 交互元素 | 降级为静态截图 → PPT图片 | PPT不支持JS交互 |
| 音频元素 | 不消费 | — |
| 数据元素 | JSON 驱动幻灯片顺序 | — |

## PPT约束

### 格式约束

| 参数 | 标准 | 说明 |
|------|------|------|
| 画幅 | 16:9（默认）或 4:3 | 可选 |
| 幻灯片数量 | 10-30页 | — |
| 文件大小 | ≤20MB | 过大则压缩图片 |
| 字体 | 系统字体 | 不依赖外部字体 |

### 降级规则

PPT不支持SVG和JS交互，所有富媒体元素必须降级：

| 元素 | 降级方案 | 保留信息 |
|------|---------|---------|
| SVG图谱 | → PNG截图 | 结构关系 |
| SVG流程图 | → PNG截图 | 流程步骤 |
| SVG动画 | → 关键帧截图 | 关键状态 |
| Canvas动画 | → 关键帧截图 | 关键帧 |
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

## 技术方案

### 方案一：python-pptx（推荐）

```python
# scripts/pptx_generator.py
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()  # 16:9 默认
slide_layout = prs.slide_layouts[0]  # 封面布局
slide = prs.slides.add_slide(slide_layout)
```

**优点**：Python生态，与现有脚本一致
**缺点**：布局控制较粗

### 方案二：PptxGenJS

```javascript
const pptx = new PptxGenJS();
const slide = pptx.addSlide();
slide.addText('标题', { x: 1, y: 1, fontSize: 32 });
```

**优点**：布局控制精细，前端生态
**缺点**：需要Node.js环境

### 企业模板支持

```bash
# 套用企业 .potx 模板
python scripts/pptx_generator.py --elements output/elements/ --output output/pptx/ --template corporate.potx
```

## 执行步骤

1. 从 `output/elements/` 读取元素
2. SVG → PNG（Playwright渲染，2x DPI）
3. SVG动画/Canvas → 关键帧截图
4. 文本元素 → 按 H1/H2/H3 拆分幻灯片
5. 加载PPT模板（可选企业.potx）
6. 注入文本和图片
7. 输出 .pptx

## 命令

```bash
# 基本生成
python scripts/pptx_generator.py --elements output/elements/ --output output/pptx/

# 套用企业模板
python scripts/pptx_generator.py --elements output/elements/ --output output/pptx/ --template corporate.potx

# 指定品牌色
python scripts/pptx_generator.py --elements output/elements/ --output output/pptx/ --brand-spec brand-spec.json
```

## 输出

- 路径：`output/pptx/output.pptx`
- 格式：.pptx（PowerPoint 2007+兼容）

## 适用场景

仅在以下场景使用 PPT管线：
- 客户/公司明确要求 .pptx 格式
- 需要套用企业 .potx 模板
- 离线环境无浏览器
- 需要他人编辑幻灯片内容

其他场景推荐使用**演示管线（Reveal.js）**。

## 质量自检

| 检查项 | 标准 | 异常处理 |
|--------|------|---------|
| 幻灯片数量 | 10-30页 | 过少则合并，过多则拆分 |
| 图片清晰度 | PNG 2x DPI | 模糊则提高渲染分辨率 |
| 文字可读 | 不溢出文本框 | 调整字号或精简文字 |
| 文件大小 | ≤20MB | 过大则压缩图片 |
| 字体 | 系统字体 | 避免外部字体依赖 |
