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

### 镜头类型

| 类型 | 适用内容 | 视觉样式 |
|------|---------|---------|
| 标题卡 | 章节标题 | 大字居中 |
| 要点卡 | 列举要点（3-5条） | 编号列表 |
| 对比卡 | A vs B | 左右分栏 |
| 流程卡 | 步骤/流程 | 步骤编号+箭头 |
| 金句卡 | 一句话核心观点 | 大字引用 |
| 总结卡 | 章节末尾/全文结尾 | 要点回顾 |

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
      "type": "points",
      "title": "要点标题",
      "items": ["要点1", "要点2", "要点3"],
      "narration": "口语化旁白文本"
    }
  ],
  "config": {
    "width": 1080,
    "height": 1920,
    "voice": "zh-CN-YunxiNeural",
    "style": "warm"
  }
}
```

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
# 完整管线
python scripts/video_pipeline.py output/slides.json --output output/video/ --style warm

# 指定语音
python scripts/video_pipeline.py output/slides.json --output output/video/ --voice zh-CN-YunxiNeural

# 横屏模式
python scripts/video_pipeline.py output/slides.json --output output/video/ --width 1920 --height 1080

# 从文章一键生成
python scripts/article_to_video.py --url "https://mp.weixin.qq.com/s/xxx" --output output/video/
```

## 品牌素材路由

| 模式 | 命令 | 适用场景 |
|------|------|---------|
| 纯模板 | `--style warm` | 快速出片 |
| 模板+品牌 | `--style warm --brand-spec xxx.json` | 有品牌素材 |
| 纯品牌 | `--brand-spec xxx.json` | 完全由品牌决定 |

## 质量自检

| 检查项 | 标准 | 异常处理 |
|--------|------|---------|
| 视频时长 | 1-3分钟 | 超长则精简，过短则补充 |
| 文件大小 | ≤50MB | 超限则压缩 |
| 画面清晰 | 1080p | 检查 device_scale_factor=2 |
| 旁白完整 | 每个镜头有旁白 | 缺失则补充 |
| 字幕可读 | 文字不溢出 | 调整字号 |
