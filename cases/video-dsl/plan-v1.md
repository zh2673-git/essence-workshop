# 方案 v1

## 1. 目标

在 `content-output` 中新增一条 Video DSL 管线，让 Agent 能把结构化内容转换为 `VideoProgram.tsx`，再经本地浏览器逐帧渲染为 MP4。本轮（v1）聚焦 Phase 1 MVP：实现 video-core、video-renderer、video-generator 的最小闭环，并跑通一个 Demo。

## 2. 核心架构

```
content-output/video-dsl/
├── packages/
│   ├── video-core/        # DSL API：Hooks + 组件
│   ├── video-renderer/    # Vite 打包 + Playwright 截图 + FFmpeg 合成
│   └── video-generator/   # Prompt 模板 + 代码校验
├── examples/
│   └── negative-numbers/  # 端到端 Demo
└── docs/
    ├── plan-v1.md
    └── test-report-v1.md
```

## 3. 渐进式构建步骤

| 步骤 | 功能 | 产出文件 | 依赖 |
|------|------|---------|------|
| Step 01 | 初始化 video-core 包 | packages/video-core/package.json, tsconfig.json, src/index.ts | 无 |
| Step 02 | 实现 Timeline/Sequence 上下文与核心 API | packages/video-core/src/*.ts | Step 01 |
| Step 03 | 初始化 video-renderer 包与 CLI | packages/video-renderer/package.json, src/renderer.ts, src/cli.ts | Step 02 |
| Step 04 | 实现 Vite 打包、Playwright 截图、FFmpeg 合成 | packages/video-renderer/src/*.ts | Step 03 |
| Step 05 | 初始化 video-generator 包 | packages/video-generator/package.json, src/index.ts, templates/prompt-template.md | Step 02 |
| Step 06 | 实现 Spec→Prompt→代码→校验流程 | packages/video-generator/src/*.ts | Step 05 |
| Step 07 | 创建 negative-numbers Demo | examples/negative-numbers/VideoProgram.tsx, spec.json | Step 04, 06 |
| Step 08 | 编写测试与验证脚本 | tests/test_*.py, tests/test_*.ts | Step 01-07 |

## 4. 正交增量原则

- 每步独立可运行，优先保证 video-core 类型正确；
- video-renderer 不修改 video-core 源码，只调用其 API；
- video-generator 不依赖具体 Agent，通过 `AgentClient` 接口注入；
- 不修改现有 `content-output/scripts/pipelines/video/html_to_video.py`。

## 5. 验证契约

### 5.1 前置条件 P

| 条件 | 含义 | 验证方式 |
|------|------|---------|
| Node.js 18+ | 运行 Vite 和 renderer | `node --version` |
| Playwright + Chromium | 无头浏览器截图 | `npx playwright install chromium` |
| FFmpeg（imageio-ffmpeg） | 视频编码 | Python 调用 imageio_ffmpeg |
| TypeScript 编译器 | 校验 Agent 代码 | `tsc --noEmit` |

### 5.2 后置条件 Q

| 条件 | 含义 | 验证方式 |
|------|------|---------|
| video-core 类型通过 | API 实现符合设计 | `tsc --noEmit` |
| video-renderer 能渲染 Demo | 输出 MP4 文件 | `os.path.getsize() > 0` |
| video-generator 校验拦截非法代码 | 禁止 CSS animation / requestAnimationFrame | 单元测试 |
| 不破坏现有 HTML 录制管线 | 现有脚本仍可导入 | Python 导入测试 |

### 5.3 不变量 I

| 条件 | 含义 | 验证方式 |
|------|------|---------|
| 现有 content-output 接口不破 | 其他管线仍可运行 | 回归测试 |
| 用户源码不被修改 | renderer 只写输出目录 | 目录隔离 |
| DSL Prompt 契约向后兼容 | 旧 Spec 结构继续有效 | Schema 测试 |

### 5.4 不可验证项

| 功能 | 为什么不可验证 | 替代验证方式 |
|------|--------------|------------|
| 真实 Agent 生成代码 | 环境无固定 LLM 密钥 | 使用 mock AgentClient + 预写 Demo 代码 |
| 音画同步 < 200ms | 需要人工听辨 | MVP 阶段仅验证音频文件存在并可合并 |
