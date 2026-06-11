# 视频号管线规范（WeChat Video Account Pipeline）

> HTML直接录制 + Edge TTS旁白 + FFmpeg合并 → MP4

---

## 管线概览

```
HTML文件 → Playwright滚动录制 → Edge TTS旁白 → FFmpeg合并 → MP4
```

核心思路：HTML本身就是最好的视觉呈现，不需要再转换到Canvas卡片模板。直接录制HTML页面的滚动过程，配合TTS旁白，生成视频。

---

## 适用场景

- 知本（K12知识拆解）生成的七维拆解HTML
- 项目式学习路径HTML
- 任何交互式HTML内容
- 已有高质量视觉呈现的HTML页面

## 元素消费与转换

| 输入 | 转换规则 | 工具 |
|------|---------|------|
| HTML文件 | 直接加载，Playwright录制滚动过程 | html_to_video.py |
| 旁白文本 | Edge TTS生成MP3 | edge-tts |
| BGM | FFmpeg混音（带ducking） | ffmpeg |

## 录制策略

1. **自动检测section**：扫描HTML中的 `.dimension-card`、`.group`、`.question-overview` 等语义元素，确定滚动停止点
2. **按section停留**：每个section停留时间由对应TTS旁白时长决定，无旁白则默认5秒
3. **平滑滚动**：使用 `scrollTo({behavior: 'smooth'})` 实现自然滚动效果
4. **首尾处理**：开头停留1秒，结尾回到顶部停留2秒

## 视频约束

| 参数 | 标准 | 说明 |
|------|------|------|
| 画幅 | 1080×1920（9:16竖屏） | 默认竖屏，可切换横屏 |
| 帧率 | 30fps | Playwright默认 |
| 编码 | H.264 | 兼容性最好 |
| 设备像素比 | 2 | 保证清晰度 |
| 时长 | 由HTML内容量和旁白长度决定 | 通常1-5分钟 |

## 旁白生成

支持三种方式：

1. **单段旁白**：`--narration "完整旁白文本"`
2. **多段旁白**：`--narration-file narration.txt`（每行一段，对应一个section）
3. **代码传入**：`narration_sections=["段落1", "段落2", ...]`

每段旁白对应HTML中的一个section，TTS时长决定该section的停留时间。

## 命令

```bash
# 从HTML生成视频（无旁白）
python -m scripts.pipelines.video.html_to_video output/负数.html --output output/video/

# 指定旁白
python -m scripts.pipelines.video.html_to_video output/负数.html --output output/video/ --narration "负数是什么？让我们从生活中找到答案..."

# 从文件读取旁白
python -m scripts.pipelines.video.html_to_video output/负数.html --output output/video/ --narration-file narration.txt

# 添加BGM
python -m scripts.pipelines.video.html_to_video output/负数.html --output output/video/ --bgm bgm.mp3

# 横屏模式
python -m scripts.pipelines.video.html_to_video output/负数.html --output output/video/ --width 1920 --height 1080

# 导出GIF
python -m scripts.pipelines.video.html_to_video output/负数.html --output output/video/ --format gif
```

## TTS语音选择

| 场景 | 语音ID | 特点 |
|------|--------|------|
| 知识讲解 | zh-CN-YunxiNeural | 年轻男性，沉稳 |
| 生活轻松 | zh-CN-XiaoxiaoNeural | 年轻女性，活泼 |
| 观点输出 | zh-CN-YunjianNeural | 成熟男性，有力 |

## 质量自检

| 检查项 | 标准 | 异常处理 |
|--------|------|---------|
| 视频时长 | 1-5分钟 | 超长则分段，过短则补充 |
| 文件大小 | ≤50MB | 超限则压缩 |
| 画面清晰 | 1080p | 检查 device_scale_factor=2 |
| 旁白完整 | 每个section有旁白 | 缺失则补充 |
| 滚动流畅 | 无卡顿 | 调整scroll_speed |
| 内容完整 | HTML所有section都被录制 | 检查section检测逻辑 |
