# 视频生成方案（微信视频号）

## 核心原则

**画面服务于内容，技术服务于效率。** 视频号的本质是「用画面+声音传递信息」，不是做精美动画。最简方案 = 卡片翻页 + TTS旁白，把文字内容以最直接的方式呈现给观众。

---

## 技术架构

```
文章内容 → 拆分镜头 → Canvas渲染帧 → Playwright录制 → WebM
                                                        ↓
文章内容 → TTS旁白脚本 → Edge TTS合成 → MP3 ──────────→ FFmpeg合并 → MP4
```

### 四步管线

| 步骤 | 输入 | 输出 | 工具 |
|------|------|------|------|
| 1. 镜头拆分 | 文章Markdown | 镜头JSON | Agent自动拆分 |
| 2. Canvas渲染+录制 | 镜头JSON + HTML模板 | WebM视频 | Playwright |
| 3. TTS合成 | 旁白文本 | MP3音频 | Edge TTS |
| 4. 合并输出 | WebM + MP3 | 最终MP4 | FFmpeg |

---

## 视频参数规范

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 画幅 | 1080×1920（9:16竖屏） | 视频号主流，手机全屏 |
| 帧率 | 30 fps | 流畅度够用 |
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
    }
  ]
}
```

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
