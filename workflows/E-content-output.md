# 场景E：内容输出 · 多渠道发布系统

> 将任意内容（场景A/B/C/D产出 / 用户原始内容）按选定风格改写，自动排版配图，输出到指定渠道。

---

## 触发条件

- 用户说「写公众号」「发布文章」「输出文章」
- 用户说「做视频」「生成视频」「视频号」
- 用户说「把文章做成视频」「文章转视频」
- 用户给公众号文章链接或说「列出我的文章」
- 场景A/B/C/D执行完成后，用户选择输出
- 用户直接提供内容要求发布

---

## 核心流程

```
步骤0：确定输入来源
步骤1：判断输入类型（完整文章 / AI聊天记录 / 笔记 / 零散想法 / 场景A/B/C/D产出）
步骤1.5：选择输出渠道（微信公众号 / 微信视频号）
步骤2：选择输出风格（论文风格 / 对话风格 / 蒸馏Skill风格 / 预留扩展）
步骤3：风格改写
步骤3.5：材料验证与引用溯源
步骤4：渠道适配排版
步骤4.5：自动生成并插入配图（公众号）/ 生成视频画面（视频号）
步骤5：检查文章 / 检查视频
步骤6：字数检查 / 视频时长检查
步骤7：生成封面 / 生成视频封面帧
步骤8：转换+推送
```

### 渠道分流

```
步骤1.5 选择渠道：
├── 微信公众号 → 步骤4~8（图文管线，见下方详细步骤）
└── 微信视频号 → 步骤V1~V5（视频管线，见「视频号输出流程」章节）
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

## 步骤4：渠道适配排版

### 渠道1：微信公众号（当前支持）

详见 [references/wechat-formatting.md](../references/wechat-formatting.md)

**核心约束**：
- 禁止使用 :::block 容器模块
- 正文不用 # H1
- 优先原生 Markdown 语法
- emoji + 加粗辅助视觉

### 渠道2：微信视频号（当前支持）

详见 [references/video-generation.md](../references/video-generation.md)

**核心约束**：
- 视频画幅 1080×1920（9:16竖屏）
- 时长1-3分钟（知识类最佳）
- 必须有TTS旁白
- Canvas卡片翻页风格，复用claude-warm配色

**视频管线**：Canvas渲染 → Playwright录制 → Edge TTS → FFmpeg合并

### 渠道3：（预留扩展）

后续可添加：知乎、掘金、Notion、PDF等渠道适配。

每个渠道有独立的排版规范文件，放在 `references/` 下。

---

## 步骤4.5：自动生成并插入配图

详见 [references/image-generation.md](../references/image-generation.md)

**配图要求**：
- 每个主要章节开头放一张配图
- 每篇文章至少5张配图
- 静态结构用SVG→PNG，变化过程用Canvas→GIF
- 论文风格版优先配图，对话风格版一般不配图

---

## 步骤5：检查文章

```bash
python scripts/wechat_publish.py article.md --auto-cover
```

---

## 步骤6：字数检查

| 指标 | 目标值 |
|------|--------|
| 纯文本字数 | 7000-8000字 |
| 总字符数（含HTML/图片标签） | 19000-20000字符 |

**扩充技巧**：补充类比、添加反例、延伸应用、引入对比、操作细化

---

## 步骤7：生成封面

```bash
python scripts/wechat_publish.py article.md --auto-cover
```

---

## 步骤8：转换+推送

```bash
python scripts/wechat_publish.py article.md --auto-cover --author "公众号名"
```

---

## Agent 规则（场景E专用）

1. **优先扫描 data/ 文件夹**：存在则按分组规则批量处理
2. **风格选择优先询问用户**：特别是蒸馏Skill风格需要用户确认
3. **双输出处理**：AI聊天记录需要生成两个独立Markdown文件
4. **字数优化约束**：纯文本7000-8000字，总字符19000-20000
5. **禁止 :::block 容器模块**
6. **图文并茂是硬要求**：每篇文章至少5张配图
7. **先 inspect 再操作**
8. **确认后再推送**：先 preview 让用户确认效果
9. **文件存放**：改写稿统一保存在 `output/` 文件夹下
10. **避免 AI 味**：严格遵循写作风格规范中的禁用表达列表
11. **渠道选择**：用户说「公众号」走图文管线，说「视频号/视频」走视频管线

---

## 视频号输出流程

> 当步骤1.5选择「微信视频号」时，执行以下流程替代步骤4~8。

详见 [references/video-generation.md](../references/video-generation.md)

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

输出 `slides.json`，格式见 [references/video-generation.md](../references/video-generation.md) 的「镜头JSON格式」章节。

### 步骤V2：TTS旁白生成

```bash
# 使用管线脚本自动生成
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

**自定义模板**：如需自定义视觉风格，修改 `scripts/video-template.html` 中的配色和字体。

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
# 一键生成视频
python scripts/video_pipeline.py output/slides.json --output output/video/

# 指定语音和压缩
python scripts/video_pipeline.py output/slides.json --output output/video/ --voice zh-CN-YunxiNeural --compress

# 横屏模式
python scripts/video_pipeline.py output/slides.json --output output/video/ --width 1920 --height 1080
```

### 公众号+视频号双输出

当用户需要同时输出公众号文章和视频号视频时：

```
1. 先完成公众号图文管线（步骤4~8），产出 article.md
2. 从 article.md 提取核心内容，执行步骤V1~V5，产出 final.mp4
3. 两者保存在同一 output/ 目录下
```

---

## 文章转视频流程

> 当用户提供公众号文章（URL / 本地文件 / media_id）并要求生成视频时，执行以下流程。

### 步骤F1：拉取文章

**三种方式**（按推荐优先级排列）：

#### 方式一：文章URL抓取（默认推荐）

```bash
# 直接给公众号文章链接
python scripts/article_fetcher.py --url "https://mp.weixin.qq.com/s/xxxxx" --save output/article.md
```

- **推荐理由**：适用于任何公众号的已发布文章，无权限要求，稳定可靠
- 通过抓取页面提取正文，转为Markdown
- 微信改版可能需要适配

#### 方式二：本地Markdown文件

```bash
# 直接指定本地文件
python scripts/article_to_video.py --article output/article.md
```

- 适用于已有Markdown文章的场景
- 无需网络请求

#### 方式三：公众号API（受权限制约）

```bash
# 列出最近文章，用户选择
python scripts/article_fetcher.py --list --count 10

# 按media_id拉取正文
python scripts/article_fetcher.py --media-id XXXXX --save output/article.md
```

**⚠️ API权限制约说明**：

| 接口 | 权限要求 | 能获取的内容 | 限制 |
|------|---------|------------|------|
| `freepublish/batchget` | 认证服务号 | 已发布文章列表 | 订阅号/未认证服务号返回 48001 |
| `material/batchget_material` | 基础权限 | API上传的素材 | 后台直接发布的文章不在其中 |
| `freepublish/getarticle` | 认证服务号 | 已发布文章正文 | 订阅号/未认证服务号返回 48001 |

- 订阅号和未认证服务号**无法通过API获取已发布文章列表**
- 素材管理接口只能看到通过API上传的素材，**后台直接发布的文章不可见**
- 需要配置 `~/.config/essence-workshop/config.yaml`（AppID/AppSecret）
- 代码已实现自动降级：优先使用 freepublish，48001 时降级到 material

### 步骤F2：文章拆镜头

`article_to_video.py` 自动完成：
1. 读取文章Markdown
2. 按 H2/H3 章节拆分
3. 自动分类镜头类型（标题/要点/引言/步骤/总结）
4. 生成口语化旁白
5. 输出 `slides.json`

### 步骤F3：视频生成

自动调用 `video_pipeline.py`：
1. Edge TTS 生成旁白
2. Playwright 录制 Canvas 动画
3. FFmpeg 合并音视频

### 一键命令

```bash
# 从URL抓取文章并生成视频（推荐）
python scripts/article_to_video.py --url "https://mp.weixin.qq.com/s/xxxxx"

# 从本地Markdown生成视频
python scripts/article_to_video.py --article output/article.md

# 从公众号API拉取文章并生成视频（需认证服务号）
python scripts/article_to_video.py --media-id XXXXX

# 指定语音和保存文章
python scripts/article_to_video.py --url "https://mp.weixin.qq.com/s/xxxxx" --voice zh-CN-YunxiNeural --save-article output/article.md

# 压缩视频
python scripts/article_to_video.py --url "https://mp.weixin.qq.com/s/xxxxx" --compress
```

### 完整链路

```
用户说「把这篇文章做成视频」
    ↓
判断来源：
├── 给了URL → article_fetcher.py --url → 正文（推荐，无权限要求）
├── 给了本地文件 → 直接读取
├── 给了media_id → article_fetcher.py --media-id → 正文（需认证服务号）
└── 什么都没给 → 提示用户提供文章URL
    ↓
article_to_video.py 自动执行：
    正文(Markdown) → 拆镜头(slides.json) → TTS + 录制 + 合并 → final.mp4
    ↓
输出到 output/video/YYYYMMDD_HHMMSS/final.mp4
```
