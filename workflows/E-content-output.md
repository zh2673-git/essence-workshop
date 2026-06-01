# 场景E：内容输出 · 多管线发布系统

> 将任意内容（场景A/B/C/D产出 / 用户原始内容）按选定风格改写，生成元素层资产，再通过选定管线输出到目标平台。

---

## 触发条件

- 用户说「写公众号」「发布文章」→ 公众号管线
- 用户说「做视频」「生成视频」「视频号」→ 视频号管线
- 用户说「HTML交互」「交互页面」→ HTML交互管线
- 用户说「做演示」「做slides」→ 演示管线
- 用户说「做PPT」→ PPT管线
- 用户给公众号文章链接或说「列出我的文章」
- 场景A/B/C/D执行完成后，用户选择输出
- 用户直接提供内容要求发布

---

## 核心流程

```
步骤0：确定输入来源
步骤1：判断输入类型（完整文章 / AI聊天记录 / 笔记 / 零散想法 / 场景A/B/C/D产出）
步骤2：选择输出风格（论文风格 / 对话风格 / 蒸馏Skill风格 / 预留扩展）
步骤3：风格改写
步骤3.5：材料验证与引用溯源
步骤4：生成元素层资产（文本/图形/动画/音频/交互/数据）
步骤5：选择管线（公众号 / 视频号 / HTML交互 / 演示 / PPT）
步骤6：管线执行 → 平台交付
```

### 管线分流

```
步骤5 选择管线：
├── 公众号管线 → 步骤W1~W8（见「公众号管线」章节）
├── 视频号管线 → 步骤V1~V5（见「视频号管线」章节）
├── HTML交互管线 → 步骤H1~H5（见「HTML交互管线」章节）
├── 演示管线 → 步骤S1~S4（见「演示管线」章节）
└── PPT管线 → 步骤P1~P4（见「PPT管线」章节）
```

### 管线选择决策树

```
用户说了什么？
├── 「公众号」「写文章」「发布」→ 公众号管线
├── 「视频」「视频号」「做视频」→ 视频号管线
├── 「HTML交互」「交互页面」「交互式」→ HTML交互管线
├── 「演示」「slides」「Reveal」→ 演示管线
├── 「PPT」「PowerPoint」→ PPT管线
└── 未指定 → 询问用户选择管线
```

---

## 步骤0：确定输入来源

| 来源 | 处理方式 |
|------|---------|
| 场景A产出（知识笔记） | 作为论文风格版原始素材 |
| 场景B产出（蒸馏Skill） | 可选：直接输出Skill / 用Skill风格写文章 |
| 场景C产出（设计文档+代码） | 提炼为技术文章 |
| 场景D产出（项目解析文档） | 提炼为技术文章 |
| 用户直接提供内容 | 按类型判断 |
| `data/` 文件夹批量 | 扫描分组，逐篇处理 |

### data/ 文件夹批量模式

```
data/
├── 话题A/              ← 子文件夹 → 合并为1篇文章
│   ├── 01_intro.md
│   ├── 02_detail.md
│   └── 03_summary.md
├── 话题B/              ← 子文件夹 → 合并为1篇文章
├── 独立笔记1.md        ← 直接的 .md 文件 → 各生成1篇文章
└── 独立笔记2.md
```

---

## 步骤1：判断输入类型

| 输入类型 | 特征 | 输出策略 |
|---------|------|---------|
| 完整文章 | 有标题、段落分明、结构完整 | 单输出，跳过改写 |
| AI聊天记录 | 多轮人机对话、有"你"/"我"交替、口语化 | **双输出**：对话整理版 + 论文风格版 |
| 笔记文件 | 有结构化标题和要点、非对话形式 | 单输出，论文风格版 |
| 零散想法 | 只有要点或片段、缺结构 | 单输出，论文风格版 |
| 场景产出 | 来自A/B/C/D的结构化文档 | 按场景类型提炼 |

---

## 步骤2：选择输出风格

### 风格选项

| 风格 | 适用场景 | 实现方式 |
|------|---------|---------|
| **论文风格**（默认） | 知识科普、技术文章、深度分析 | 按五段式结构重组，专业严谨 |
| **对话风格** | AI聊天记录整理 | 保留Q&A结构，播客文字版 |
| **蒸馏Skill风格** | 用某人物的思维方式写文章 | 激活examples/中对应人物Skill，以其表达DNA重写 |
| **（预留扩展）** | 后续可添加 | 故事风格、教程风格等 |

### 蒸馏Skill风格执行流程

```
1. 扫描 examples/ 目录，列出可用的人物Skill
2. 用户选择目标人物（或从场景B产出自动关联）
3. 读取该人物Skill的SKILL.md，提取表达DNA
4. 以该人物的：
   - 核心心智模型作为分析框架
   - 决策启发式作为论证逻辑
   - 场景路由作为内容组织方式
   - 表达DNA（语言风格、修辞偏好、节奏特征）作为写作风格
5. 用该人物的视角重写内容
```

### 风格选择决策树

```
内容来源是AI聊天记录？
├── 是 → 默认双输出（对话风格 + 论文风格），可选蒸馏Skill风格
└── 否 → 内容涉及人物/思维/决策？
    ├── 是 → 推荐蒸馏Skill风格
    └── 否 → 默认论文风格
```

---

## 步骤3：风格改写

详见 [references/writing-style-guide.md](../references/writing-style-guide.md)

### 论文风格版改写规则

1. 按「引言/背景 → 核心论点（2-4个）→ 深度分析 → 结论/展望 → 参考文献」五段式组织
2. 提炼论点，每个论点独立成节
3. 去口语化，用书面语替代
4. 补充论证逻辑，但不加虚构内容
5. 专业概念保留术语但加通俗解释
6. 引用标注来源
7. 文末附参考文献列表

### 对话风格版改写规则

1. 保留对话骨架，保持 Q&A 结构
2. 去口语化冗余
3. 精简寒暄
4. 合并相关问答
5. 保留追问深度
6. 标注角色：**「我：」** / **「AI：」**

---

## 步骤3.5：材料验证与引用溯源

详见 [references/fact-checking.md](../references/fact-checking.md)

---

## 步骤4：生成元素层资产

详见 [references/element-spec.md](../references/element-spec.md)

风格改写完成后，将内容拆解为元素层原子资产，供各管线读取。

### 元素生成规则

| 元素类型 | 来源 | 格式 | 存放 |
|---------|------|------|------|
| 文本元素 | 改写后的Markdown | .md | output/elements/text/ |
| 图形元素 | 根据内容生成SVG | .svg | output/elements/graphics/ |
| 动画元素 | 根据变化过程生成 | .svg(SMIL) / .js(Canvas) | output/elements/animations/ |
| 音频元素 | TTS旁白+BGM | .mp3 | output/elements/audio/ |
| 交互元素 | 标准模块实例化 | .html / .js | output/elements/interactions/ |
| 数据元素 | 结构化JSON | .json | output/elements/data/ |

### 图形元素生成决策

```
内容是什么？
├── 结构/关系/对比 → SVG静态图（流程图、架构图、对比图）
├── 变化/过程/循环 → SVG动画 或 Canvas帧序列
├── 数据/统计 → SVG图表
└── 概念示意 → SVG示意图
```

### 图文同步规划

**⚠️ 核心原则：先规划图文布局，再写文章。不要先写完文字再补图。**

**规划方法**：
1. 根据大纲，为每个章节确定配图类型和内容
2. 识别文章中是否有"循环/迭代/状态转换"类概念，有则必须规划动画元素
3. 写完每章后立即生成对应图形元素，不要等全文写完再统一配图

**配图规划模板**：

| 章节 | 配图类型 | 配图内容 | 元素格式 |
|------|---------|---------|---------|
| 引言 | 概念示意图 | 核心概念关系 | SVG→PNG |
| 模型一 | 动态过程图 | 变异→选择→保留循环 | SVG动画→GIF |
| 模型二~五 | 详解图 | 四宫格/多栏对比 | SVG→PNG |
| 启发式 | 列表图 | 七条启发式一览 | SVG→PNG |
| 场景应用 | 对比图 | 三栏对比 | SVG→PNG |
| 根因 | 因果图/时间线 | 经历→模型因果链 | SVG→PNG |
| 边界 | 警示图 | 反模式+边界 | SVG→PNG |

---

## 步骤5：选择管线

根据触发词或用户选择，确定走哪条管线。同一组元素层资产可以被多条管线消费。

### 管线能力对比

| 能力 | 公众号 | 视频号 | HTML交互 | 演示 | PPT |
|------|-------|-------|---------|------|-----|
| 文本 | ✅受限HTML | ✅卡片文字 | ✅完整 | ✅幻灯片 | ✅文本框 |
| 图形 | PNG内联 | Canvas帧 | SVG直接 | SVG嵌入 | PNG嵌入 |
| 动画 | GIF | 视频帧 | CSS/SVG/JS | CSS/SVG | 关键帧截图 |
| 交互 | ❌ | ❌ | ✅完整 | ❌ | ❌ |
| 音频 | ❌ | ✅TTS+BGM | ✅可嵌入 | ❌ | ❌ |
| 输出格式 | 微信HTML | MP4 | HTML | Reveal.js | .pptx |

---

## 公众号管线

> 详见 [references/pipeline-wechat.md](../references/pipeline-wechat.md)

### 步骤W1：字数规划

写文章前先规划各章节目标字数，确保纯文本总量达到7000-8000字目标。

**参考字数分配**（以8000字为例）：

| 章节 | 目标字数 | 说明 |
|------|---------|------|
| 引言/背景 | 600-800 | 建立问题意识 |
| 核心模型/论点（3-5个） | 每个1000-1500 | 文章主体，占60%+ |
| 决策启发式/方法论 | 600-800 | 可操作的建议 |
| 场景应用 | 400-600 | 连接现实 |
| 根因/边界 | 400-600 | 深度和诚实 |
| 结语 | 200-300 | 行动号召 |

### 步骤W2：渠道适配排版

详见 [references/wechat-formatting.md](../references/wechat-formatting.md)

**核心约束**：
- 禁止使用 :::block 容器模块
- 正文不用 # H1
- 优先原生 Markdown 语法
- emoji + 加粗辅助视觉

### 步骤W3：元素转换

从元素层读取 → 按微信约束转换：

| 元素 | 转换规则 |
|------|---------|
| 文本元素 | Markdown → 微信内联样式HTML |
| SVG图形 | SVG → PNG（Playwright渲染，2x DPI） |
| SVG动画 | SVG动画 → GIF（Playwright录制） |
| Canvas动画 | Canvas → GIF |
| 交互元素 | 降级为静态截图（PNG） |

### 步骤W4：图文间距检查 + 质量自检

| 检查项 | 标准 | 处理方式 |
|--------|------|---------|
| 连续无图文字 | ≤1500字 | 超过1500字无图则必须在该区域补图 |
| 每章是否有图 | 每个## H2章节至少1张 | 无图章节必须补图 |
| GIF动画 | 必须1个，文件≥100KB | 无GIF则为核心变化过程生成 |
| SVG→PNG字体 | 非衬线体 | 出现衬线体说明未用Playwright |
| SVG→PNG溢出 | 文字在框内 | 溢出则调整SVG框高度 |

### 步骤W5：字数检查

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 纯文本字数 | 7000-8000字 | 内容充实度指标 |
| 总字符数（含HTML/图片标签） | ≤20000字符 | 微信草稿箱硬性上限 |

### 步骤W6：生成封面

```bash
python scripts/wechat_publish.py article.md --auto-cover
```

### 步骤W7：推送前检查

| 检查项 | 标准 | 修复方式 |
|--------|------|---------|
| frontmatter title | 非空 | 添加 `title: 文章标题` |
| frontmatter author | 非空（可选） | 添加 `author: 作者名` |
| 配图数量 | 必须5张（4 PNG + 1 GIF） | 不足则补充 |
| 参考文献数量 | 3-5条 | 过多则精简 |

### 步骤W8：转换+推送

```bash
python scripts/wechat_publish.py article.md --auto-cover --author "公众号名"
```

---

## 视频号管线

> 详见 [references/pipeline-video.md](../references/pipeline-video.md)

### 步骤V1：内容精简与镜头拆分

**核心任务**：把7000-8000字的文章精简为500-1000字的旁白，拆分为10-20个镜头。

#### 拆分规则

1. 按 ## H2 章节拆分，每个章节1-3个镜头
2. 每个镜头分配类型：标题卡 / 要点卡 / 对比卡 / 流程卡 / 金句卡 / 总结卡
3. 每个镜头撰写口语化旁白（短句、每句不超过20字）
4. 旁白总字数控制在500-1000字

#### 镜头类型选择决策

```
内容是什么？
├── 章节标题 → 标题卡
├── 列举要点（3-5条）→ 要点卡
├── A vs B 对比 → 对比卡
├── 步骤/流程 → 流程卡
├── 一句话核心观点 → 金句卡
└── 章节末尾/全文结尾 → 总结卡
```

#### 输出格式

输出 `slides.json`，格式见 [references/pipeline-video.md](../references/pipeline-video.md) 的「镜头JSON格式」章节。

### 步骤V2：TTS旁白生成

```bash
python scripts/video_pipeline.py slides.json --output output/video/ --voice zh-CN-YunxiNeural
```

**语音选择**：
- 知识讲解类 → `zh-CN-YunxiNeural`（年轻男性，沉稳）
- 生活轻松类 → `zh-CN-XiaoxiaoNeural`（年轻女性，活泼）
- 观点输出类 → `zh-CN-YunjianNeural`（成熟男性，有力）

### 步骤V3：Canvas渲染+录制

管线脚本自动完成：
1. 读取 `slides.json`
2. 加载 `scripts/video-template.html` 模板
3. Playwright 录制 Canvas 动画为 WebM

### 步骤V4：音频合成+合并

管线脚本自动完成：
1. Edge TTS 生成每段旁白 MP3
2. FFmpeg 拼接所有旁白
3. 根据音频时长自动调整镜头时长
4. FFmpeg 合并视频+音频为最终 MP4

### 步骤V5：质量检查

| 检查项 | 标准 | 处理方式 |
|--------|------|---------|
| 视频时长 | 1-3分钟 | 超长则精简镜头，过短则补充 |
| 文件大小 | ≤50MB | 超限则用 `--compress` 压缩 |
| 画面清晰 | 1080p | 确保 device_scale_factor=2 |
| 旁白完整 | 每个镜头有旁白 | 缺失则补充 narration 字段 |
| 字幕可读 | 文字不溢出 | 调整字号或精简文字 |

### 完整命令

```bash
# 纯模板（默认，最简单）
python scripts/video_pipeline.py output/slides.json --output output/video/ --style warm

# 模板+品牌微调
python scripts/video_pipeline.py output/slides.json --output output/video/ --style warm --brand-spec output/brand-spec.json

# 纯品牌
python scripts/video_pipeline.py output/slides.json --output output/video/ --brand-spec output/brand-spec.json

# 指定语音和压缩
python scripts/video_pipeline.py output/slides.json --output output/video/ --voice zh-CN-YunxiNeural --compress

# 横屏模式
python scripts/video_pipeline.py output/slides.json --output output/video/ --width 1920 --height 1080
```

---

## HTML交互管线

> 详见 [references/pipeline-html.md](../references/pipeline-html.md)

HTML交互管线是**能力最完整的管线**——SVG直接嵌入、交互模块接入、CSS/JS动画保留，无降级。

### 步骤H1：选择课程骨架模板

从 `templates/course-skeleton.html` 加载HTML课程骨架，或根据内容类型选择合适模板。

**骨架模板包含**：
- 导航栏 + 侧边目录
- 坡度导航器模块
- 三阶进度条模块
- 内容区域容器

### 步骤H2：元素直接嵌入

从元素层读取 → 直接嵌入（无转换）：

| 元素 | 嵌入方式 |
|------|---------|
| 文本元素 | Markdown → HTML，保留完整结构 |
| SVG图形 | `<svg>` 标签直接嵌入，保留交互 |
| SVG动画 | SMIL/CSS动画直接嵌入 |
| Canvas动画 | `<canvas>` + JS 直接嵌入 |
| 交互模块 | `modules/` 中的标准模块实例化嵌入 |
| 音频元素 | `<audio>` 标签嵌入 |

### 步骤H3：交互模块接入

根据内容需要，从 `modules/` 中选择标准交互模块：

| 模块 | 适用场景 | 说明 |
|------|---------|------|
| slope-navigator | 长文导航 | 坡度理解渐进式导航 |
| three-stage-progress | 三阶内容 | 是什么→为什么→怎么做进度条 |
| knowledge-graph | 知识体系 | 可交互的知识图谱浏览器 |
| card-flip | 对比/正反 | 点击翻转查看正反面 |
| comparison-table | 多维对比 | 可排序/筛选的对比表格 |

### 步骤H4：样式与响应式

- 使用CSS变量统一配色
- 响应式布局（移动端适配）
- 打印样式优化

### 步骤H5：输出与质量检查

| 检查项 | 标准 | 处理方式 |
|--------|------|---------|
| SVG渲染 | 所有SVG正确显示 | 检查viewBox和命名空间 |
| 交互功能 | 所有模块可交互 | 测试点击/拖拽/翻转 |
| 响应式 | 移动端正常显示 | 检查断点布局 |
| 文件大小 | 单个HTML ≤5MB | 过大则拆分或压缩SVG |

输出：`output/html/index.html`（单文件，所有资源内联）

---

## 演示管线

> 详见 [references/pipeline-slides.md](../references/pipeline-slides.md)

### 步骤S1：幻灯片结构生成

从元素层读取文本 → 拆分为 Reveal.js 幻灯片 section：

| Markdown | 幻灯片 |
|----------|--------|
| H1 | 封面幻灯片（标题+副标题） |
| H2 | 章节分隔幻灯片 |
| H3 | 内容幻灯片 |
| 代码块 | 代码高亮幻灯片 |
| 列表 | 要点幻灯片 |

### 步骤S2：图形嵌入

从元素层读取图形 → 嵌入对应幻灯片：

| 元素 | 嵌入方式 |
|------|---------|
| SVG图形 | `<svg>` 直接嵌入幻灯片 |
| SVG动画 | SMIL/CSS动画嵌入，自动播放 |
| Canvas动画 | `<canvas>` + JS 嵌入 |

### 步骤S3：模板应用

从 `templates/reveal-template.html` 加载 Reveal.js 模板，注入幻灯片内容。

**模板特性**：
- 演讲者备注支持
- PDF导出支持
- 代码高亮
- 响应式布局

### 步骤S4：输出与质量检查

| 检查项 | 标准 | 处理方式 |
|--------|------|---------|
| 幻灯片数量 | 10-30页 | 过少则合并，过多则拆分 |
| 图文比例 | 每页≤50%纯文字 | 文字过多则拆分或加图 |
| 动画流畅 | 过渡效果正常 | 检查CSS动画兼容性 |

输出：`output/slides/index.html`

---

## PPT管线

> 详见 [references/pipeline-pptx.md](../references/pipeline-pptx.md)

### 步骤P1：幻灯片结构生成

从元素层读取文本 → 拆分为 PPT 幻灯片：

| Markdown | PPT幻灯片 |
|----------|----------|
| H1 | 封面幻灯片（标题+副标题） |
| H2 | 章节分隔幻灯片 |
| H3 | 内容幻灯片 |
| 代码块 | 等宽字体文本框 |
| 列表 | 要点列表 |

### 步骤P2：元素降级转换

PPT不支持SVG和JS交互，需要降级：

| 元素 | 转换规则 |
|------|---------|
| SVG图形 | SVG → PNG → PPT图片 |
| SVG动画 | 截取关键帧 → PPT图片序列 |
| Canvas动画 | 截取关键帧 → PPT图片 |
| 交互元素 | 降级为静态截图 → PPT图片 |
| 代码块 | 等宽字体文本框 |

### 步骤P3：PPT生成

使用 `scripts/pptx_generator.py` 生成 .pptx 文件：

```bash
python scripts/pptx_generator.py --elements output/elements/ --output output/pptx/ --template brand-spec.json
```

**可选**：套用企业 .potx 模板。

### 步骤P4：输出与质量检查

| 检查项 | 标准 | 处理方式 |
|--------|------|---------|
| 幻灯片数量 | 10-30页 | 过少则合并，过多则拆分 |
| 图片清晰度 | PNG 2x DPI | 模糊则提高渲染分辨率 |
| 文字可读 | 不溢出文本框 | 调整字号或精简文字 |
| 文件大小 | ≤20MB | 过大则压缩图片 |

输出：`output/pptx/output.pptx`

---

## 文章转视频流程

> 当用户提供公众号文章（URL / 本地文件 / media_id）并要求生成视频时，执行以下流程。

### 步骤F1：拉取文章

**三种方式**（按推荐优先级排列）：

#### 方式一：文章URL抓取（默认推荐）

```bash
python scripts/article_fetcher.py --url "https://mp.weixin.qq.com/s/xxxxx" --save output/article.md
```

#### 方式二：本地Markdown文件

```bash
python scripts/article_to_video.py --article output/article.md
```

#### 方式三：公众号API（受权限制约）

```bash
python scripts/article_fetcher.py --list --count 10
python scripts/article_fetcher.py --media-id XXXXX --save output/article.md
```

**⚠️ API权限制约说明**：

| 接口 | 权限要求 | 能获取的内容 | 限制 |
|------|---------|------------|------|
| `freepublish/batchget` | 认证服务号 | 已发布文章列表 | 订阅号/未认证服务号返回 48001 |
| `material/batchget_material` | 基础权限 | API上传的素材 | 后台直接发布的文章不在其中 |
| `freepublish/getarticle` | 认证服务号 | 已发布文章正文 | 订阅号/未认证服务号返回 48001 |

#### ⚠️ 抓取质量验证

| 检查项 | 标准 | 不达标处理 |
|--------|------|-----------|
| 标题 | 非空 | 标题为空则提示用户提供标题 |
| H2章节数量 | ≥3个 | <3个说明结构丢失，提示用户手动提供Markdown文件 |
| 正文字数 | ≥500字 | <500字说明抓取不完整，提示用户手动提供 |

### 步骤F2：文章拆镜头

`article_to_video.py` 自动完成：
1. 读取文章Markdown
2. 按 H2/H3 章节拆分
3. 自动分类镜头类型
4. 生成口语化旁白
5. 输出 `slides.json`

#### ⚠️ 镜头拆分质量检查

| 检查项 | 标准 | 不达标处理 |
|--------|------|-----------|
| 镜头数量 | ≥5个 | <5个判定为拆分失败，需手动设计 |
| 镜头类型多样性 | ≥3种类型 | 只有1种类型说明分类逻辑有误 |
| 旁白总字数 | 500-1000字 | 过少则补充，过多则精简 |
| 每个镜头有旁白 | 100% | 缺失则补充 narration 字段 |

### 步骤F3：视频生成

自动调用 `video_pipeline.py`。

### 一键命令

```bash
# 从URL一键生成视频
python scripts/article_to_video.py --url "https://mp.weixin.qq.com/s/xxx" --output output/video/

# 从本地文章一键生成视频
python scripts/article_to_video.py --article output/article.md --output output/video/

# 自动从文章提取品牌素材并应用
python scripts/article_to_video.py --url "https://mp.weixin.qq.com/s/xxx" --auto-brand
```

---

## 多管线组合输出

同一内容可走多条管线，元素层资产只需生成一次：

### 公众号+视频号双输出

```
1. 生成元素层资产
2. 公众号管线：元素 → 微信HTML → 推送草稿箱
3. 视频号管线：元素 → Canvas帧+TTS → MP4
```

### 全管线输出

```
1. 生成元素层资产（一次）
2. 公众号管线 → 微信HTML
3. 视频号管线 → MP4
4. HTML交互管线 → 完整交互HTML
5. 演示管线 → Reveal.js
6. PPT管线 → .pptx
```

---

## Agent 规则（场景E专用）

1. **优先扫描 data/ 文件夹**：存在则按分组规则批量处理
2. **风格选择优先询问用户**：特别是蒸馏Skill风格需要用户确认
3. **双输出处理**：AI聊天记录需要生成两个独立Markdown文件
4. **管线选择**：根据触发词自动选择管线，未指定则询问用户
5. **元素层先行**：先完成元素层资产生成，再进入管线执行
6. **禁止 :::block 容器模块**（公众号管线）
7. **图文并茂是硬要求**（公众号管线）：每篇文章必须5张配图（4 PNG + 1 GIF）
8. **先 inspect 再操作**
9. **确认后再推送**：先 preview 让用户确认效果
10. **文件存放**：元素资产保存在 `output/elements/`，管线输出保存在 `output/{管线名}/`
11. **避免 AI 味**：严格遵循写作风格规范中的禁用表达列表
12. **管线切换**：用户可在同一内容上切换管线，元素层资产复用
