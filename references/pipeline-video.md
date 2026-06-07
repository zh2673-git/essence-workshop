# 视频号管线规范（WeChat Video Account Pipeline）

> 从元素层读取 → Canvas渲染+Playwright录制 → Edge TTS → FFmpeg合并 → MP4

---

## 管线概览

```
元素层读取 → 内容精简+镜头拆分 → TTS旁白 → Canvas渲染+录制 → 音视频合并 → MP4
```

## 元素消费与转换

| 元素类型 | 转换规则 | 工具 |
|---------|---------|------|
| 文本元素 | 精简为旁白 + 拆分为镜头卡片 | slides.json |
| SVG图形 | SVG → Canvas渲染帧 | video-template.html |
| SVG动画 | SVG动画 → Canvas帧 | video-template.html |
| Canvas动画 | 直接渲染 | video-template.html |
| 音频元素 | TTS旁白 + BGM | Edge TTS + FFmpeg |
| 交互元素 | 不消费 | — |
| 数据元素 | slides.json 驱动镜头顺序 | — |

## 视频约束

### 画幅与时长

| 参数 | 标准 | 说明 |
|------|------|------|
| 画幅 | 1080×1920（9:16竖屏） | 默认竖屏，可切换横屏 |
| 时长 | 1-3分钟 | 知识类最佳时长 |
| 帧率 | 30fps | — |
| 编码 | H.264 | 兼容性最好 |

### 镜头约束

- ⚠️ 镜头数量 10-20个
- ⚠️ 旁白总字数 500-1000字
- ⚠️ 每个镜头必须有旁白（narration字段）
- ⚠️ 镜头类型多样性 ≥3种

### 视觉风格

统一黑金配色，由大模型根据内容生成视觉元素：

| 角色 | 色值 | 用途 |
|------|------|------|
| 背景 | `#0A0A0A` | 深黑底色 |
| 主文字 | `#FFFFFF` | 标题、正文 |
| 强调色 | `#FFD700` | 关键词、装饰线、高亮 |
| 辅助色 | `#B0B0B0` | 副文字、说明 |
| 边框 | `#333333` | 分割线、卡片边框 |

> **装饰元素**：由大模型根据内容生成，不使用预定义装饰函数。常见装饰包括：几何线条、圆环、网格点阵、粒子场等，使用黄色(#FFD700)和灰色(#333333)。

### 镜头类型

3种镜头原语，大模型根据内容自行决定视觉形式：

| 原语 | 触发条件 | 大模型自由度 |
|------|---------|-------------|
| **标题** | 章节开头 | 标题+副标题的排版方式由大模型决定 |
| **内容** | 论点/要点/对比/流程/金句/数据等 | 布局、分栏、装饰、字号层级全部由大模型决定 |
| **总结** | 章节末尾/全文结尾 | 回顾方式（列表/关键词/一句话）由大模型决定 |

> 大模型根据内容自动选择最合适的视觉呈现，无需预定义"要点卡""对比卡""金句卡"等子类型。

## 镜头JSON格式

```json
{
  "slides": [
    {
      "type": "title",
      "title": "章节标题",
      "subtitle": "副标题",
      "narration": "口语化旁白文本"
    },
    {
      "type": "content",
      "title": "内容标题",
      "body": "大模型根据内容自由组织的视觉内容描述",
      "narration": "口语化旁白文本"
    },
    {
      "type": "summary",
      "title": "总结",
      "body": "回顾要点",
      "narration": "口语化旁白文本"
    }
  ],
  "config": {
    "width": 1080,
    "height": 1920,
    "voice": "zh-CN-YunxiNeural"
  }
}
```

> `type` 只有3种：`title` / `content` / `summary`。`body` 字段由大模型自由组织，不限制子类型。

## TTS语音选择

| 场景 | 语音ID | 特点 |
|------|--------|------|
| 知识讲解 | zh-CN-YunxiNeural | 年轻男性，沉稳 |
| 生活轻松 | zh-CN-XiaoxiaoNeural | 年轻女性，活泼 |
| 观点输出 | zh-CN-YunjianNeural | 成熟男性，有力 |

## 执行步骤

1. 从 `output/elements/` 读取元素
2. 文本精简 + 镜头拆分 → slides.json
3. Edge TTS 生成旁白 MP3
4. Playwright 录制 Canvas 动画 → WebM
5. FFmpeg 拼接旁白
6. FFmpeg 合并视频+音频 → MP4
7. 质量检查

## 命令

```bash
# 完整管线（统一CLI）
python -m scripts.cli video output/slides.json --output output/video/

# 或直接调用
python -m scripts.pipelines.video.pipeline output/slides.json --output output/video/

# 指定语音
python -m scripts.cli video output/slides.json --output output/video/ --voice zh-CN-YunxiNeural

# 横屏模式
python -m scripts.cli video output/slides.json --output output/video/ --width 1920 --height 1080

# 从文章一键生成
python -m scripts.cli fetch --url "https://mp.weixin.qq.com/s/xxx" --save-article output/article.md
python -m scripts.shared.article_to_video --url "https://mp.weixin.qq.com/s/xxx" --output output/video/
```

## 质量自检

| 检查项 | 标准 | 异常处理 |
|--------|------|---------|
| 视频时长 | 1-3分钟 | 超长则精简，过短则补充 |
| 文件大小 | ≤50MB | 超限则压缩 |
| 画面清晰 | 1080p | 检查 device_scale_factor=2 |
| 旁白完整 | 每个镜头有旁白 | 缺失则补充 |
| 字幕可读 | 文字不溢出 | 调整字号 |
