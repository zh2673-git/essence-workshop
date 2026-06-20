# 测试报告 v4

## 结论

| 维度 | 结果 | 说明 |
|------|------|------|
| P 前置 | ✅ | 同 v3 |
| Q 后置 | ✅ | `python -m scripts.cli video ... --pipeline dsl` 生成 final.mp4 |
| I 不变量 | ✅ | 原 HTML/公众号分支仍可调用 |

## 关键数据

| 检查项 | 结果 |
|--------|------|
| CLI 自动 TTS | 从 spec.json 生成 audio.m4a |
| CLI 渲染 | 270 帧，输出 final.mp4 |
| 视频含音频 | 是 |

## Ratchet 决策

保留并进入 v5。
