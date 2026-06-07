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
- ⚠️ 不要生成封面图（封面由微信后台单独上传，不在正文中插入）

### 配图渲染函数选择

根据文章内容选择合适的渲染函数，不要每种类型各生成一张，而是根据内容需要灵活组合：

| 内容类型 | 渲染函数 | 参数格式 | 容量 |
|---------|---------|---------|------|
| 列举要点 | `render_svg_card` | title, items[] | 7条×30字 |
| 关键数据 | `render_svg_stat` | value, label, sublabel, trend, tags[] | 大数字+标签+趋势+标签组 |
| 金句引言 | `render_svg_quote` | text, source, context, tags[] | 200字引言+上下文+标签组 |
| A vs B | `render_svg_compare` | title, leftTitle, rightTitle, left[], right[] | 5条×25字 |
| 时间线 | `render_svg_timeline` | title, events[{year,title,desc}] | 6事件 |
| 步骤流程 | `render_svg_steps` | title, steps[{title,desc}] | 6步 |
| 概念聚焦 | `render_svg_focus` | keyword, explanation, tags[], sub_keywords[] | 12字关键词+60字说明+标签+子关键词 |
| 数据图表 | `render_svg_chart` | title, data[{label,value}] | 6条柱 |
| 总结清单 | `render_svg_summary` | title, items[] | 7条×35字 |
| 问答 | `render_svg_qa` | question, answer, key_points[] | 40字+80字+3要点 |
| **概念详解** | `render_svg_feature` | title, features[{keyword,desc}] | 4组：10字关键词+40字说明 |
| **多维网格** | `render_svg_grid` | title, cards[{title,desc}] | 2×2或2×3网格 |
| **趋势对比** | `render_svg_line_chart` | title, labels[], datasets[{name,values[]}] | 多数据线对比，最多3条线 |
| **英雄封面** | `render_svg_hero` | title, subtitle, tags[] | 20字标题+40字副标题+5标签×8字 |
| **双栏对比** | `render_svg_duo_card` | title, leftTitle, rightTitle, left[], right[] | 左右各5条×25字 |
| **列表详情** | `render_svg_list_detail` | title, items[{keyword,desc}] | 6组：10字关键词+40字描述 |
| **仪表盘** | `render_svg_dashboard` | title, metrics[{value,label,trend}], barData[{label,value}], listItems[{keyword,desc,value}] | 4指标+8柱+5列表项，信息密度极高 |
| **竖向柱状图** | `render_svg_bar_chart` | title, data[{label,value}], showValues | 12柱大画幅，网格参考线+数值标注 |
| **指标网格** | `render_svg_metric_grid` | title, metrics[{value,label,sub,mini}], cols | 3×3网格，每卡含迷你图(up/down/bar/dot) |
| **混排信息卡** | `render_svg_composite` | title, sections[{type,content}] | 概念+图表+卡片混排，信息密度极高 |
| **逻辑推导链** | `render_svg_logic_flow` | title, steps[{label,desc,type}] | 前提→推理→结论链，带类型标记 |
| **循环/辩证** | `render_svg_cycle` | title, phases[{label,desc}] | 环形布局展示循环/辩证过程 |
| **散点图** | `render_svg_scatter` | title, data[{label,x,y,group}] | 二维分布/象限分析 |
| **热力图** | `render_svg_heatmap` | title, data[{row,col,value}] | 矩阵关系/交叉分析 |
| **自由绘制** | `render_svg_custom` | title, svg_body | LLM根据内容自由绘制SVG，模板仅提供框架 |

> **规划原则**：
> 1. **以 `render_svg_custom` 自由绘制为主，预设模板为保底**——每张图优先考虑用custom根据内容定制绘制，只有当内容恰好是标准信息结构时才用预设模板
> 2. **每篇文章至少5张使用 `render_svg_custom`**，最多2张用预设模板
> 3. **禁止连续使用相同类型的渲染函数**——相邻两张图必须是不同类型
> 4. **密度优先**：低密度模板（stat/focus/quote/qa）不超过2张，且仅用于核心金句/关键概念等必须聚焦的场景
> 5. 低密度模板传入辅助信息（如stat的trend/focus的tags/quote的context）以充实画面，避免大面积留白
> 6. **hero 仅用于封面，不在正文中使用**（hero卡片信息密度低，留白过多）
> 7. **grid 类型文字容易溢出**，优先用 card 或 list_detail 替代；如必须用 grid，每项文字不超过15字
> 8. **GIF动画**：使用HTML+CSS动画录制，分辨率800×500@2x，帧数≥8，帧延迟120ms，最终GIF不超过2MB

### 画幅比例

渲染函数支持通过 `width`/`height` 参数选择画幅比例：

| 比例名 | 尺寸 | 适用场景 |
|--------|------|---------|
| standard | 800×600 (4:3) | 公众号标准配图（默认） |
| wide | 1240×770 (16:10) | 宽幅封面/英雄区卡片 |
| cinematic | 1280×720 (16:9) | 视频号封面 |

```python
from scripts.elements.svg_themes import ASPECT_RATIOS
w, h = ASPECT_RATIOS["wide"]  # (1240, 770)
render_svg_hero(title="标题", width=w, height=h)
```

### 渐变与装饰密度

7个主题通过声明式参数控制渐变和装饰密度：

| 主题 | density | gradient_accents | 效果 |
|------|---------|-----------------|------|
| dark | rich | True | 渐变色条+渐变标题+密集装饰 |
| warm | normal | True | 暖色渐变点缀+适度装饰 |
| minimal | sparse | False | 无渐变+极简装饰+大量留白 |
| nature | normal | True | 自然渐变+有机装饰 |
| ink | normal | False | 无渐变+水墨笔触装饰 |
| cyber | rich | True | 霓虹渐变+密集装饰 |
| indigo | rich | True | 星云渐变+密集装饰 |

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
3. SVG动画 → GIF（见下方GIF生成流程）
4. Markdown → 微信HTML（wechat_converter.py）
5. 配图插入对应位置
6. 图文间距检查
7. 字数检查
8. 生成封面
9. 推送前检查
10. 推送草稿箱

### GIF 生成流程

GIF 必须使用 `scripts/elements/record_gif.py` 脚本录制，步骤如下：

1. **创建 HTML 动画文件**：在 `output/wechat/images/` 下创建 `xxx_anim.html`，实现以下接口：
   - `window.getTotalFrames()` — 返回总帧数（推荐 10-15 帧）
   - `window.stepFrame(f)` — 渲染第 f 帧（f 从 0 到 getTotalFrames()-1）
2. **执行录制**：
   ```bash
   python -m scripts.elements.record_gif "path/to/xxx_anim.html" "path/to/output.gif" --delay 200 --pause 8
   ```
3. **文件大小检查**：GIF 必须 ≥100KB 且 ≤3MB。若超过 3MB：
   - 减少 `getTotalFrames()` 返回值（减少帧数）
   - 在 HTML 中设置较小的 viewport（如 `width: 400px; height: 250px`）
   - 使用自定义 Playwright 脚本设置 `device_scale_factor=1`（默认为 2）

**HTML 动画模板要点**：
- **禁用CSS transition/animation**：`stepFrame(f)` 中直接设置元素的最终样式（opacity、transform、width等），不使用CSS过渡动画。原因：录制时每帧只等~100ms，但transition通常设500ms，会截取到中间过渡帧，产生半透明混合色闪烁
- **禁用渐变和半透明色**：所有颜色必须用纯色（`#RRGGBB`），禁止 `rgba()`、`linear-gradient`、`radial-gradient`。原因：GIF仅支持256色，渐变和半透明在量化后产生严重色彩抖动和闪烁
- `stepFrame(f)` 中通过 JS 直接控制元素显隐和样式变化
- 保持背景与 SVG 主题一致（深色背景 + 品牌色装饰）
- 文字使用系统字体（Microsoft YaHei / PingFang SC）

**GIF录制脚本要点**：
- 使用统一全局调色板：从所有帧采样生成一个全局调色板，所有帧共用（避免帧间调色板突变闪烁）
- `optimize=False`：不使用PIL的optimize（它会为每帧生成独立局部调色板，导致帧间闪烁）
- `disposal=1`：保留上一帧，只存差异部分（减少体积）
- `device_scale_factor=1.5`：800x500@1.5x=1200x750，清晰度和体积的平衡点

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
