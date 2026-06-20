# 方案 v2

## 目标

修复 v1 中 Demo 视频只显示背景色的问题：React 全局帧控制与 Composition 订阅存在时序竞争，导致画面不随 frame 更新。同时引入 `useSequenceTime()` 让 Sequence 内动画基于相对时间。

## 关键改动

1. 将 `__essence_setFrame` / `__essence_subscribe` 提升到 main.tsx 模块级作用域，确保在 Composition `useEffect` 订阅前已存在。
2. 新增 `useSequenceTime()` Hook，返回 `frame - cumulatedFrom`。
3. 更新 `examples/negative-numbers/VideoProgram.tsx`，ElevatorScene 使用相对帧计算动画。

## 验证契约

- v1 的视频帧中心亮度 bbox 为 0（opacity=0 除外也几乎无内容）。
- v2 的 frame_00030/frame_00135 等采样点必须出现可检测的文本/图形像素块。

## 不可验证项

- 人眼观感（颜色、布局）通过采样像素间接验证。
