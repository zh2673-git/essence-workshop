# 公众号管线规范（WeChat Official Account Pipeline）

> 从元素层读取 → 按微信约束转换 → 推送草稿箱

---

## 管线概览

```
元素层读取 → 微信约束适配 → 排版 → 配图插入 → 质量自检 → 推送草稿箱
```

## 元素消费与转换

| 元素类型 | 转换规则 | 工具 |
|---------|---------|------|
| 文本元素 | Markdown → 微信内联样式HTML | wechat_converter.py |
| SVG图形 | SVG → PNG（2x DPI） | Playwright |
| SVG动画 | SVG动画 → GIF | Playwright录制 |
| Canvas动画 | Canvas → GIF | Playwright录制 |
| 交互元素 | 降级为静态截图（PNG） | Playwright截图 |
| 音频元素 | 不消费 | — |
| 数据元素 | 读取结构数据驱动排版 | — |

## 微信约束

### 主题系统

**排版主题**（控制文章样式）：

| 主题 | 风格 | 适用场景 |
|------|------|---------|
| **essence**（默认） | 简洁重点突出：加粗带橙色底线高亮、引言装饰、正文留白充足 | 知识类文章 |
| claude-warm | 暖色系全装饰：暖橙底线高亮、奶油背景、暖色代码块 | 情感/生活类 |
| claude-clean | 极简白底：冷蓝灰底线高亮、最小装饰、冷灰代码块 | 技术/学术类 |

**配图主题**（控制 SVG 图片风格，独立于排版主题）：

| 主题 | 情绪关键词 | 适用场景 |
|------|-----------|---------|
| dark（深空，默认） | 技术、编程、AI、工程 | 技术类文章 |
| warm（暖阳） | 温暖、生活、教育、成长 | 生活/情感类 |
| minimal（极简） | 极简、设计、美学、禅 | 设计/哲学类 |
| nature（自然） | 自然、生态、中医、养生 | 中医/自然类 |
| ink（水墨） | 水墨、国风、传统、诗词 | 传统文化类 |
| cyber（赛博） | 赛博、未来、黑客、Web3 | 科技前沿类 |
| indigo（靛蓝） | 认知、思维、本质、深度 | 认知/思维类 |

> **自动匹配**：`match_theme()` 根据文章标题+副标题的情绪关键词自动选择配图主题。也可通过 `svg_theme` 参数手动指定。排版主题和配图主题独立选择，不绑定。

> **引言装饰**：文章前25%位置的blockquote（≤120字）自动装饰为引言样式——渐变背景+左上角大号引号图标+独立section区块。

### 排版约束

详见 [wechat-formatting.md](wechat-formatting.md)

- ⚠️ 禁止使用 :::block 容器模块
- ⚠️ 正文不用 # H1
- ⚠️ 优先原生 Markdown 语法
- ⚠️ emoji + 加粗辅助视觉

### 字数约束

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 纯文本字数 | 7000-8000字 | 内容充实度指标 |
| 总字符数（含HTML/图片标签） | ≤20000字符 | 微信草稿箱硬性上限 |

### 配图约束

- ⚠️ 每篇文章必须7张配图（6 PNG + 1 GIF）
- ⚠️ GIF 不可省略，文件大小 ≥100KB
- ⚠️ 每个主要章节开头放一张配图
- ⚠️ 连续无图文字 ≤1500字

## 图文同步规划

**⚠️ 核心原则：先规划图文布局，再写文章。**

**配图规划模板**：

| 章节 | 配图类型 | 配图内容 | 方案 |
|------|---------|---------|------|
| 引言 | 概念示意图 | 核心概念关系 | SVG→PNG |
| 模型一 | 动态过程图 | 变化循环 | SVG动画→GIF |
| 模型二~五 | 详解图 | 四宫格/多栏对比 | SVG→PNG |
| 启发式 | 列表图 | 一览 | SVG→PNG |
| 场景应用 | 对比图 | 三栏对比 | SVG→PNG |
| 根因 | 因果图/时间线 | 因果链 | SVG→PNG |

## 执行步骤

1. 从 `output/elements/` 读取元素
2. SVG → PNG（Playwright渲染，device_scale_factor=2）
3. SVG动画 → GIF（Playwright录制）
4. Markdown → 微信HTML（wechat_converter.py）
5. 配图插入对应位置
6. 图文间距检查
7. 字数检查
8. 生成封面
9. 推送前检查
10. 推送草稿箱

## 命令

```bash
# 完整管线（统一CLI）
python -m scripts.cli publish article.md --auto-cover --author "公众号名"

# 或直接调用
python -m scripts.pipelines.wechat.publish article.md --auto-cover --author "公众号名"

# 仅转换不推送
python -m scripts.pipelines.wechat.converter article.md --theme essence
```

## 质量自检

| 检查项 | 标准 | 异常处理 |
|--------|------|---------|
| SVG→PNG字体 | 非衬线体 | 出现衬线体说明未用Playwright |
| SVG→PNG溢出 | 文字在框内 | 溢出则调整SVG框高度 |
| SVG→PNG清晰度 | 2x DPI | 模糊则检查device_scale_factor |
| GIF文件大小 | ≥100KB且≤3MB | <100KB说明动画未生效 |
| 连续无图文字 | ≤1500字 | 超过则补图 |
| 总字符数 | ≤20000 | 超出则智能样式去重（提取重复内联样式为CSS类+短类名），不截断正文 |
