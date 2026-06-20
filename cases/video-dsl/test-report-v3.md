# 测试报告 v3

## 结论

| 维度 | 结果 | 说明 |
|------|------|------|
| P 前置 | ✅ | edge-tts 与 FFmpeg 可用 |
| Q 后置 | ✅ | audio.m4a 9.00s，final.mp4 含 AAC 音频流 |
| I 不变量 | ✅ | 无现有接口破坏 |

## 关键数据

| 检查项 | 结果 |
|--------|------|
| audio.m4a duration | 00:00:09.00 |
| final.mp4 video stream | 2160x3840 @ 30fps |
| final.mp4 audio stream | AAC, 24000 Hz, mono |

## 已知问题与修复

| 问题 | 修复 |
|------|------|
| ADTS muxer 不支持 MP3 codec | 拼接中间文件改用 `.mp3`，最终再混码为 `.m4a` |
| Windows 下 os.rename 目标存在报错 | 先删除已存在文件 |
| TTS 总时长不足视频时长 | 使用 `apad` filter pad 到目标时长 |

## Ratchet 决策

保留并进入 v4。
