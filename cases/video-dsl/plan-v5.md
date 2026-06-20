# 方案 v5

## 目标

沉淀动画组件库，降低 Agent 写动画代码的心智负担。新增 FadeIn、FlyIn、Counter、Timeline、Compare 组件，并在 Demo 中使用 FadeIn/FlyIn。

## 关键改动

1. `video-core/src/components/` 新增 5 个组件。
2. `video-core/src/index.ts` 导出组件。
3. `examples/negative-numbers/VideoProgram.tsx` 改用 FadeIn/FlyIn。

## 验证契约

- TypeScript 编译通过。
- Demo 渲染成功且组件库文件出现在打包产物中。
