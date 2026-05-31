# 视频生成方案 v2（微信视频号）

## 核心原则

**画面服务于内容，技术服务于效率。** 视频号的本质是「用画面+声音传递信息」，不是做精美动画。v2 升级：Stage+Sprite时间切片模型实现元素级动画控制，连续运动叙事消除硬切换，BGM+Ducking混音提升观感，多格式导出满足不同场景，品牌素材协议保证视觉一致性，反AI slop规则确保视觉品味。

---

## 技术架构 v2

```
文章内容 → 拆分镜头(+timeline) → Canvas渲染帧(Sprite驱动) → Playwright录制 → WebM
         ↓                                                                  ↓
品牌素材 → 自动提取 → brand-spec.json                                FFmpeg合并 ← TTS旁白 + BGM
                                                                        ↓
                                                              MP4 / MP4_60fps / GIF
```

### 五步管线 v2

| 步骤 | 输入 | 输出 | 工具 | v2新增 |
|------|------|------|------|--------|
| 1. 镜头拆分 | 文章Markdown | 镜头JSON(+timeline) | Agent自动拆分 | ✅ timeline字段 |
| 2. TTS合成 | 旁白文本 | MP3音频 | Edge TTS | - |
| 3. Canvas渲染+录制 | 镜头JSON + HTML模板(+style) | WebM视频 | Playwright | ✅ style参数 |
| 4. 合并输出 | WebM + 旁白 + BGM | MP4 | FFmpeg | ✅ BGM+Ducking |
| 5. 格式导出 | MP4 | MP4_60fps / GIF | FFmpeg | ✅ 多格式 |

---

## 视频参数规范

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 画幅 | 1080×1920（9:16竖屏） | 视频号主流，手机全屏 |
| 帧率 | 25 fps（默认）/ 60 fps（高帧率模式） | v2支持60fps |
| 时长 | 1-3分钟 | 知识类最佳时长 |
| 编码 | H.264 | 兼容性最好 |
| 码率 | 2-5 Mbps | 平衡清晰度和体积 |
| 文件大小 | ≤50MB | 视频号上传限制 |

---

## 镜头拆分规则

### 拆分原则

1. **每个 ## H2 章节至少1个镜头**
2. **一个镜头 = 一个完整观点**（15-30秒）
3. **镜头类型由内容决定**（见下表）
4. **总镜头数 = 视频时长(秒) / 20**（平均每镜头20秒）

### 镜头类型

| 类型 | 适用内容 | 画面描述 | 时长 |
|------|---------|---------|------|
| **标题卡** | 章节标题、文章标题 | 大字居中，淡入 | 3-5秒 |
| **要点卡** | 核心论点、关键结论 | 标题+要点列表，逐行出现 | 10-20秒 |
| **对比卡** | A vs B 对比 | 左右分栏，对比展示 | 10-15秒 |
| **流程卡** | 步骤、流程、决策链 | 纵向步骤，逐个出现 | 15-25秒 |
| **金句卡** | 一句话核心观点 | 大字居中，强调样式 | 5-8秒 |
| **总结卡** | 章节末尾、全文结尾 | 要点回顾列表 | 10-15秒 |
| **数据卡** | 关键数据、百分比、倍数 | 超大数字+环形进度+标签 | 5-8秒 |
| **图表卡** | 数据对比、分布、排名 | 条形图/环形图+图例 | 10-15秒 |
| **时间线卡** | 时间序列、发展历程 | 纵向时间轴+事件节点 | 10-20秒 |
| **聚焦卡** | 核心概念、关键词强调 | 聚光灯遮罩+放大关键词 | 5-8秒 |
| **问答卡** | Q&A、设问+回答 | 问题→翻转→答案 | 8-12秒 |

### 镜头JSON格式

```json
{
  "slides": [
    {
      "type": "title",
      "title": "为什么你的决策总是慢半拍",
      "subtitle": "从诸葛亮的审时度势看决策效率",
      "duration": 5,
      "narration": "为什么你的决策总是慢半拍？今天我们从诸葛亮的审时度势出发，看看决策效率的秘密。"
    },
    {
      "type": "bullet",
      "title": "审时度势的三个维度",
      "items": ["时机判断：什么时候该动", "势能评估：手里有什么牌", "节奏控制：快慢的切换"],
      "duration": 15,
      "narration": "审时度势包含三个维度：时机判断，什么时候该动；势能评估，手里有什么牌；节奏控制，快慢的切换。"
    },
    {
      "type": "quote",
      "text": "善战者，求之于势，不责于人",
      "source": "—— 孙子兵法",
      "duration": 6,
      "narration": "善战者，求之于势，不责于人。这就是审时度势的精髓。"
    },
    {
      "type": "compare",
      "title": "德治 vs 法治",
      "leftLabel": "德治",
      "rightLabel": "法治",
      "left": ["依赖自觉", "内在驱动", "提升上限"],
      "right": ["制度约束", "外在强制", "守住底线"],
      "duration": 12,
      "narration": "德治依赖自觉，法治依靠制度。二者缺一不可。"
    },
    {
      "type": "steps",
      "title": "三步走流程",
      "steps": ["第一步：解蔽求真", "第二步：化性起伪", "第三步：隆礼重法"],
      "duration": 15,
      "narration": "三步走：先解蔽求真，再化性起伪，最后隆礼重法。"
    },
    {
      "type": "summary",
      "title": "核心要点回顾",
      "items": ["化性起伪：逻辑起点", "隆礼重法：制度设计", "解蔽求真：认知前提"],
      "duration": 10,
      "narration": "核心要点：化性起伪是逻辑起点，隆礼重法是制度设计，解蔽求真是认知前提。"
    }
  ]
}
```

### 各类型镜头字段说明

| 类型 | 必填字段 | 可选字段 | 说明 |
|------|---------|---------|------|
| title | type, title, duration, narration | subtitle | 标题卡 |
| bullet | type, title, items, duration, narration | - | 要点卡，items为数组 |
| quote | type, text, duration, narration | source | 金句卡 |
| **compare** | type, title, **left**, **right**, duration, narration | **leftLabel**, **rightLabel** | 对比卡，left/right为数组，leftLabel/rightLabel为列标题（默认"A"/"B"） |
| steps | type, title, steps, duration, narration | - | 流程卡，steps为数组 |
| summary | type, title, items, duration, narration | - | 总结卡，items为数组 |
| **stat** | type, **value**, **label**, duration, narration | sublabel | 数据卡，value为显示数字，label为描述，sublabel为副描述 |
| **chart** | type, title, **data**, duration, narration | chartType | 图表卡，data为[{label,value,color}]，chartType为bar(默认)/donut |
| **timeline** | type, title, **events**, duration, narration | - | 时间线卡，events为[{year,title,desc}] |
| **focus** | type, **keyword**, **explanation**, duration, narration | - | 聚焦卡，keyword为放大关键词，explanation为解释文本 |
| **qa** | type, **question**, **answer**, duration, narration | - | 问答卡，question为问题，answer为答案，自动翻转动画 |

**⚠️ compare 类型特别注意**：字段名必须是 `left` 和 `right`（不是 `items_left` / `items_right`），列标题用 `leftLabel` 和 `rightLabel`（不是 `left_label` / `right_label`）。

---

## Canvas 卡片翻页风格

### 视觉风格定义

**风格：白底卡片 + 赭石色强调 + 简笔画点缀**

与公众号配图保持一致的 claude-warm 配色体系，形成品牌统一感。

### 配色规范（复用 image-generation.md）

| 用途 | 颜色值 | 说明 |
|------|--------|------|
| 背景 | `#FAF7F2` | 奶油白 |
| 主色 | `#C96442` | 赭石橙，标题/强调 |
| 深色 | `#8B5E3C` | 深棕，副标题 |
| 最深 | `#3C2415` | 正文/线条 |
| 浅灰 | `#999` | 辅助文字 |
| 卡片背景 | `#FFF` | 白色卡片，带阴影 |

### 字体规范

| 用途 | 字号 | 字重 | 颜色 |
|------|------|------|------|
| 章节标题 | 56px | bold | #3C2415 |
| 卡片标题 | 44px | bold | #C96442 |
| 正文要点 | 32px | normal | #3C2415 |
| 金句文字 | 52px | bold | #C96442 |
| 来源/注释 | 24px | normal | #999 |

### 动画规范

| 动画 | 时长 | 缓动 | 说明 |
|------|------|------|------|
| 卡片淡入 | 0.6秒 | ease-out | 新镜头进入 |
| 文字出现 | 0.4秒 | ease-out | 逐行出现，间隔0.3秒 |
| 金句放大 | 0.8秒 | ease-out | 从0.8倍放大到1倍 |
| 过渡切换 | 0.5秒 | ease-in-out | 旧卡片淡出+新卡片淡入 |

---

## Playwright 录制方案

### 录制原理

Playwright 原生支持 `page.video.startRecording()`，直接录制浏览器视窗为视频。

### 录制脚本

```python
import json, os
from playwright.sync_api import sync_playwright

def record_video(slides_json_path, template_html_path, output_video_path, width=1080, height=1920):
    with open(slides_json_path, 'r', encoding='utf-8') as f:
        slides = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={'width': width, 'height': height},
            device_scale_factor=2,
            record_video_dir=os.path.dirname(output_video_path),
            record_video_size={'width': width * 2, 'height': height * 2}
        )
        page = context.new_page()

        page.goto(f'file:///{os.path.abspath(template_html_path)}')

        page.evaluate('window.slidesData = arguments[0]', slides)

        page.evaluate('window.startPresentation()')

        total_duration = sum(s.get('duration', 10) for s in slides['slides'])
        page.wait_for_timeout((total_duration + 2) * 1000)

        page.close()
        context.close()
        browser.close()

        recorded = context.videos[0].path()
        os.rename(recorded, output_video_path)
```

---

## TTS 旁白方案

### Edge TTS（首选，免费）

```python
import asyncio
import edge_tts

async def generate_tts(text, output_path, voice="zh-CN-YunxiNeural", rate="+0%"):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)

def batch_generate_tts(narrations, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for i, text in enumerate(narrations):
        output_path = os.path.join(output_dir, f'narration_{i:03d}.mp3')
        asyncio.run(generate_tts(text, output_path))
```

### 推荐语音

| 语音ID | 风格 | 适用场景 |
|--------|------|---------|
| `zh-CN-YunxiNeural` | 年轻男性，沉稳 | 知识讲解、技术内容 |
| `zh-CN-XiaoxiaoNeural` | 年轻女性，活泼 | 生活类、轻松话题 |
| `zh-CN-YunjianNeural` | 成熟男性，有力 | 观点输出、金句强调 |

### 旁白文本生成规则

1. **每个镜头的 narration 字段就是旁白文本**
2. **口语化**：把书面语转为口语（"因此"→"所以"，"此外"→"还有"）
3. **短句为主**：每句不超过20字
4. **自然停顿**：用逗号和句号控制节奏
5. **不加语气词**：不要"啊""呢""吧"等

---

## FFmpeg 合并方案

### 合并视频+音频

```python
import subprocess

def merge_video_audio(video_path, audio_path, output_path):
    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-i', audio_path,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        '-movflags', '+faststart',
        output_path
    ]
    subprocess.run(cmd, check=True)
```

### 多段旁白拼接

```python
def concat_audios(audio_dir, output_path):
    file_list_path = os.path.join(audio_dir, 'filelist.txt')
    files = sorted([f for f in os.listdir(audio_dir) if f.endswith('.mp3')])
    with open(file_list_path, 'w', encoding='utf-8') as f:
        for fname in files:
            f.write(f"file '{os.path.join(audio_dir, fname)}'\n")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', file_list_path,
        '-c:a', 'aac',
        '-b:a', '128k',
        output_path
    ]
    subprocess.run(cmd, check=True)
```

### 视频压缩（如果超限）

```python
def compress_video(input_path, output_path, target_size_mb=50):
    duration = get_duration(input_path)
    target_bitrate = int((target_size_mb * 8192) / duration * 0.9)
    cmd = [
        'ffmpeg', '-y',
        '-i', input_path,
        '-c:v', 'libx264',
        '-b:v', f'{target_bitrate}k',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        output_path
    ]
    subprocess.run(cmd, check=True)
```

---

## 完整管线脚本

### 一键生成视频

```python
import json, os, asyncio, subprocess
from playwright.sync_api import sync_playwright
import edge_tts

def generate_video(article_json_path, output_dir, template_html_path, voice="zh-CN-YunxiNeural"):
    os.makedirs(output_dir, exist_ok=True)

    with open(article_json_path, 'r', encoding='utf-8') as f:
        slides = json.load(f)

    narrations = [s['narration'] for s in slides['slides'] if s.get('narration')]

    audio_dir = os.path.join(output_dir, 'audio')
    for i, text in enumerate(narrations):
        audio_path = os.path.join(audio_dir, f'narration_{i:03d}.mp3')
        asyncio.run(edge_tts.Communicate(text, voice).save(audio_path))

    concat_path = os.path.join(output_dir, 'narration.mp3')
    concat_audios(audio_dir, concat_path)

    raw_video_path = os.path.join(output_dir, 'raw.webm')
    record_video(article_json_path, template_html_path, raw_video_path)

    final_path = os.path.join(output_dir, 'final.mp4')
    merge_video_audio(raw_video_path, concat_path, final_path)

    print(f"Video generated: {final_path}")
    return final_path
```

---

## 依赖安装

```bash
pip install playwright edge-tts
playwright install chromium
```

FFmpeg 需要单独安装：
- Windows: `winget install FFmpeg` 或从 https://ffmpeg.org/download.html 下载
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

### ⚠️ 启动时依赖检查

运行视频管线前必须检查以下依赖是否可用，缺失则给出安装命令并退出：

| 依赖 | 检查方式 | 缺失提示 |
|------|---------|---------|
| FFmpeg | `ffmpeg -version` | `winget install FFmpeg` (Windows) / `brew install ffmpeg` (macOS) |
| Playwright | `python -c "from playwright.sync_api import sync_playwright"` | `pip install playwright && playwright install chromium` |
| Edge TTS | `python -c "import edge_tts"` | `pip install edge-tts` |
| Pillow | `python -c "from PIL import Image"` | `pip install Pillow` |

---

## 与公众号方案的对照

| 维度 | 公众号（图文） | 视频号（短视频） |
|------|--------------|----------------|
| 输出格式 | Markdown→HTML | Canvas→MP4 |
| 配图方案 | SVG→PNG / Canvas→GIF | Canvas本身就是视频画面 |
| 音频 | 无 | TTS旁白（必须有） |
| 文字密度 | 高（7000-8000字） | 低（旁白约500-1000字） |
| 阅读方式 | 主动滚动 | 被动观看 |
| 核心挑战 | 排版+配图 | 镜头拆分+节奏控制 |
| 文件输出 | article.md | slides.json + final.mp4 |

---

## 镜头拆分Agent规则

### 拆分流程

```
1. 读取文章内容
2. 按 ## H2 章节拆分
3. 每个章节拆分为1-3个镜头
4. 为每个镜头分配类型（标题卡/要点卡/对比卡/流程卡/金句卡/总结卡）
5. 为每个镜头撰写旁白文本（口语化、短句）
6. 输出 slides.json
```

### 拆分约束

- **标题卡**：每个章节开头必须有
- **金句卡**：每篇文章2-3个，放在最核心观点处
- **总结卡**：文章结尾必须有
- **要点不超过5条**：每个要点卡最多5条要点
- **旁白总字数**：500-1000字（1-3分钟视频）
- **镜头总数**：10-20个

### 旁白字数与时长对照

| 旁白字数 | 大约时长 | 适合场景 |
|---------|---------|---------|
| 300-500字 | 1-1.5分钟 | 金句集、要点速览 |
| 500-800字 | 1.5-2.5分钟 | 知识讲解（推荐） |
| 800-1200字 | 2.5-3.5分钟 | 深度分析 |

---

## v2 新特性

### Stage+Sprite 时间切片模型

每个视觉元素作为独立Sprite，拥有自己的时间线，可实现元素重叠、错开入场、缓动曲线等连续运动叙事效果。

**slides.json 中的 timeline 字段：**

```json
{
  "type": "title",
  "title": "从Vibe Coding到Agentic Engineering",
  "duration": 5,
  "timeline": {
    "duration": 5,
    "elements": [
      {"id": "bg", "enter_at": 0, "exit_at": 5, "easing": "none"},
      {"id": "icon", "enter_at": 0.2, "exit_at": 4.5, "easing": "expoOut"},
      {"id": "title", "enter_at": 0.4, "exit_at": 4.5, "easing": "expoOut"},
      {"id": "accent", "enter_at": 0.7, "exit_at": 4.5, "easing": "expoOut"}
    ]
  }
}
```

**支持的缓动函数：**

| easing | 效果 | 适用场景 |
|--------|------|---------|
| none | 无动画，直接出现/消失 | 背景元素 |
| expoOut | 快速入场，缓慢停止 | 标题、主要元素 |
| easeOut | 平滑入场 | 一般元素 |
| easeOutBack | 入场后微微回弹 | 卡片、列表项 |
| easeIn | 缓慢开始 | 退场动画 |
| expoInOut | 平滑进出 | 过渡元素 |
| linear | 匀速 | 进度条 |

**自动生成：** 如果 slides.json 中没有 timeline 字段，模板会根据镜头类型自动生成默认时间线。

---

### 连续运动叙事（v2.1 核心升级）

**核心理念：禁止PowerPoint式硬切换，元素在画面中流动。**

传统视频模板的镜头切换是「旧卡片完全消失 → 空白帧 → 新卡片出现」，本质是PPT翻页。连续运动叙事要求：**任何时刻画面上都有至少一个活跃元素在运动，不存在"空白帧"。**

#### 三大机制

| 机制 | 作用 | 实现位置 |
|------|------|---------|
| **残留元素** | 前一个slide的元素延伸到下一个slide的前0.8秒 | `autoTimeline()` 的 `residual` 参数 |
| **交叉过渡** | 新slide入场时旧slide仍在退场，形成交叉 | `tick()` 的 `isResidual` 分支 |
| **元素级时序** | 每个元素有独立的enter/exit时间，不跟随卡片同步 | `autoTimeline()` 的逐元素 exit_at 梯度 |

#### 残留元素原理

`autoTimeline(slide, slideIndex, totalSlides)` 为每个元素计算 exit_at 时，不再停在 `dur-0.5`，而是延伸到 `dur + residual`（residual = 0.5秒，最后一个slide为0）：

```
旧方式：所有元素 exit_at = dur - 0.5（卡片消失前统一退场）
新方式：bg exit_at = dur + 0.5, heading exit_at = dur + 0.2, item_0 exit_at = dur + 0.1...
        → 背景残留最久，标题次之，要点最先消失
```

**残留梯度设计**：背景元素残留最久（0.5s），标题次之（0.2-0.25s），内容元素最短（0.05-0.1s），形成「从外到内」的自然消散。

#### 交叉过渡类型

| 过渡类型 | 效果 | 适用镜头 |
|---------|------|---------|
| `morph` | 旧画面微缩+淡出，新画面微放+淡入 | title, compare, stat, qa |
| `slideAndFade` | 旧画面向上滑出+淡出，新画面从下滑入+淡入 | bullet, steps, chart, timeline |
| `crossfade` | 纯透明度交叉渐变 | quote, summary, focus |

#### 渲染循环逻辑

```
tick() 主循环：
1. 计算所有活跃场景（opacity > 0.01）
2. 对每个场景：
   a. 如果 localT > duration → 残留模式，用 crossfade 渐隐
   b. 如果 localT < 0.3 → 入场模式，用对应过渡类型入场
   c. 如果 localT > duration - 0.1 → 退场模式，用对应过渡类型退场
   d. 正常模式 → 摄像机运动 + Sprite更新 + 渲染器绘制
3. 多个场景可以同时可见（交叉过渡）
```

#### 视觉效果对比

| 场景 | 旧效果（PPT翻页） | 新效果（连续流动） |
|------|-----------------|------------------|
| 标题卡 → 要点卡 | 标题淡出 → 空白 → 要点淡入 | 标题向上滑出同时要点从下方滑入，背景持续流动 |
| 要点卡 → 金句卡 | 要点消失 → 金句放大 | 要点逐个淡出，金句从要点位置渐现 |
| 对比卡 → 流程卡 | 左右栏消失 → 步骤出现 | 旧画面微缩淡出，新画面微放淡入 |
| 金句卡 → 总结卡 | 金句缩小 → 总结列表出现 | 金句渐隐，总结从同一位置展开 |

#### ⚠️ 连续叙事硬性规则

1. **禁止全屏空白帧**：任何时刻至少有一个元素可见
2. **残留时间必须 > 0**：非最后一个slide的背景元素 exit_at 必须超过 slide duration
3. **入场和退场必须重叠**：新slide的 enter 和旧slide的 exit 必须有时间交叉
4. **背景元素残留最久**：bg 的 residual 系数为 1.0，内容元素为 0.1-0.4

---

### BGM + Ducking 混音

为视频添加背景音乐，并在旁白播放时自动降低背景音乐音量（sidechain compression）。

```bash
python video_pipeline.py slides.json --bgm music.mp3 --output output/
```

**FFmpeg 混音命令：**

```bash
ffmpeg -i video.mp4 -i bgm.mp3 -i narration.mp3 \
  -filter_complex "\
    [1:a]volume=0.3,atrim=0:{{duration}},afade=t=in:st=0:d=0.3,afade=t=out:st={{duration-1}}:d=1[bgm];\
    [bgm][2:a]sidechaincompress=threshold=0.1:ratio=4:attack=5:release=50[mixed]" \
  -map 0:v -map "[mixed]" -c:v copy -shortest output.mp4
```

**参数说明：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| bgm_volume | 0.3 | BGM基础音量 |
| duck_threshold | 0.1 | 触发压制的音量阈值 |
| duck_ratio | 4 | 压制比例（4=旁白时BGM降到1/4） |
| attack | 5ms | 压制启动时间 |
| release | 50ms | 压制恢复时间 |

---

### 多格式导出

```bash
# 默认MP4 (25fps)
python video_pipeline.py slides.json --format mp4

# 60fps高帧率（适合运动较多的视频）
python video_pipeline.py slides.json --format mp4_60fps

# GIF动图（适合公众号文章内嵌）
python video_pipeline.py slides.json --format gif
```

| 格式 | 帧率 | 分辨率 | 适用场景 |
|------|------|--------|---------|
| mp4 | 25fps | 1080×1920 | 视频号上传（默认） |
| mp4_60fps | 60fps | 1080×1920 | 高帧率需求 |
| gif | 10fps | 540×N | 公众号文章内嵌 |

---

### 多风格模板（--style）

4套精心设计的视觉风格，通过 `--style` 参数切换：

```bash
python video_pipeline.py slides.json --style dark     # 深色科技风（默认）
python video_pipeline.py slides.json --style warm     # 暖色人文风
python video_pipeline.py slides.json --style minimal  # 极简黑白风
python video_pipeline.py slides.json --style nature   # 自然深绿风
```

| 风格 | 主色 | 背景 | 适用内容 |
|------|------|------|---------|
| dark | #E94560 珊瑚红 | #0F0F23 深蓝黑 | 技术、AI、编程 |
| warm | #D4763A 赭石橙 | #FDF6EC 奶油白 | 人文、教育、生活 |
| minimal | #333333 纯黑 | #FFFFFF 纯白 | 设计、哲学、极简 |
| nature | #C9A84C 金色 | #0D1F0D 深绿 | 中医、养生、自然 |

---

### 品牌素材协议

三步协议规范品牌素材的采集和使用：

1. **问** - 扫描文章中的品牌信号（标题、配色、关键词）
2. **提取** - 从信号中提炼品牌要素（颜色、字体、图标偏好）
3. **固化** - 生成 brand-spec.json，供视频模板和图片生成使用

```bash
# 从文章自动提取品牌素材
python brand_extractor.py --article output/article.md
python brand_extractor.py --url https://mp.weixin.qq.com/s/xxx
```

**brand-spec.json 结构：**

```json
{
  "brand": { "name": "", "tagline": "", "description": "" },
  "colors": { "primary": "#E94560", "secondary": "#F0C27F", ... },
  "fonts": { "heading": "...", "body": "...", "mono": "..." },
  "icons": { "style": "stroke", "preferred": ["brain", "lightbulb"] },
  "rules": {
    "no_gradient_text": true,
    "no_emoji_icons": true,
    "no_purple_primary": true,
    "max_colors_per_slide": 3,
    "min_contrast_ratio": 4.5
  }
}
```

---

### 反AI Slop 视觉规则

避免生成具有典型AI风格缺陷的视频：

| 规则 | 说明 |
|------|------|
| 禁止紫色渐变 | 不使用紫色作为主色或渐变 |
| 禁止emoji图标 | 用线条图标替代emoji |
| 每帧最多3色 | 控制色彩数量，避免花哨 |
| 卡片必须有边框 | 避免无边框的悬浮感 |
| 背景必须有纹理 | 网格/渐变/圆环，避免纯色平面 |
| 最小对比度4.5:1 | 确保文字可读性 |
| 禁止渐变文字 | 文字用纯色，不用渐变填充 |

---

## v2 完整用法

```bash
# 基础用法（与v1兼容）
python article_to_video.py --url https://mp.weixin.qq.com/s/xxx

# 指定风格
python article_to_video.py --url https://mp.weixin.qq.com/s/xxx --style warm

# 添加BGM
python article_to_video.py --url https://mp.weixin.qq.com/s/xxx --bgm music.mp3

# 导出GIF
python article_to_video.py --url https://mp.weixin.qq.com/s/xxx --format gif

# 60fps + BGM + 暖色风格
python article_to_video.py --url https://mp.weixin.qq.com/s/xxx --style warm --bgm music.mp3 --format mp4_60fps

# 直接用slides.json生成视频
python video_pipeline.py output/slides.json --style dark --bgm bgm.mp3 --format mp4
```
