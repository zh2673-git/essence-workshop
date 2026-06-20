# 本质工坊 · 视频生成功能增强方案

> 版本：v1.0  
> 日期：2026-06-20  
> 定位：为本质工坊 `content-output` 的视频号管线引入“代码生成 + 帧驱动渲染”能力，形成与现有 HTML 录制管线互补的第二代视频生产方案。  
> 设计方法：本质工坊 · 项目开发三阶方法论（是什么 → 为什么 → 怎么做）

---

## 第1步：是什么（What）—— 定义功能本质

### 1.1 一句话定义

本质工坊的视频生成功能，应当成为 **"让任何能调用 Skill 的 Agent，都能把结构化内容转换为可渲染视频代码，并在本地浏览器中确定性生成 MP4"** 的生产管线。

### 1.2 本质特征（从问题推导）

| 推导要素 | 逻辑分析 | 结论 |
|---------|---------|------|
| **核心问题** | 现有视频管线只能做 HTML 滚动录制和固定 Canvas 模板，动画能力弱、时间控制粗 | 需要一条支持帧级精确控制的视频生产线 |
| **目标用户** | 调用本质工坊 Skill 的 Agent（不绑定任何具体模型） | 方案必须是 Agent-agnostic，只依赖标准接口 |
| **核心价值** | Agent 可以像写 React 组件一样写视频，所见即所得，本地即可渲染 | 视频 = 帧的纯函数 |
| **关键输入** | 结构化内容（文案、分镜、知识点、数据） | 内容必须先经过本质工坊的提炼，再进入视频管线 |
| **关键输出** | MP4/GIF 视频文件 + 可复用的动画组件 | 既交付成品，也沉淀资产 |

### 1.3 关键属性

```
本质特征 "帧级精确控制"      → 属性：Video DSL（代码层）✅ 需深入
本质特征 "Agent 可生成代码"    → 属性：Code Generator（Prompt + 校验）✅ 需深入
本质特征 "本地可渲染"          → 属性：Local Renderer（浏览器截图 + FFmpeg）✅ 需深入
本质特征 "与现有管线互补"      → 属性：Pipeline Router（路由选择）✅ 需深入
本质特征 "沉淀可复用动画资产"  → 属性：Animation Library（组件库）❌
本质特征 "多平台分发"          → 属性：Output Adapter（格式/尺寸适配）❌
```

| 属性名 | 推导来源 | 是否需深入 |
|-------|---------|----------|
| **Video DSL** | 帧级精确控制 | ✅ [[04-video-core-四层设计]] |
| **Code Generator** | Agent 生成代码 | ✅ [[06-video-generator-四层设计]] |
| **Local Renderer** | 本地可渲染 | ✅ [[05-video-renderer-四层设计]] |
| **Pipeline Router** | 与现有 HTML 录制管线互补 | ✅ [[07-pipeline-router-四层设计]] |
| **Animation Library** | 沉淀可复用资产 | ❌ |
| **Output Adapter** | 多平台分发 | ❌ |

### 1.4 区分属性（边界）

- ✅ **做**：
  - 把结构化内容转成视频程序代码
  - 本地浏览器逐帧渲染成 MP4/GIF
  - 与现有 `html_to_video.py` 管线并存，由 Agent 或用户选择
  - 提供竖屏（1080×1920）和横屏（1920×1080）两种默认画幅
  - 支持旁白（TTS）、BGM、简单媒体元素

- ❌ **不做**（MVP 阶段）：
  - 云端分布式渲染
  - 复杂 3D、WebGL、粒子特效
  - 实时预览 Web 编辑器（保留命令行/脚本调用方式）
  - 替代专业剪辑软件的非线性编辑 GUI
  - 绑定某一特定大模型（如 DeepSeek V4）

### 1.5 设计哲学

**内容即代码，代码即视频。**  
Agent 不需要理解 FFmpeg 或浏览器截图，只需要按照 DSL 契约编写组件；渲染管线保证契约执行，输出确定性视频。

---

## 第2步：为什么（Why）—— 架构决策

### 2.1 存在理由

```
因：现有视频管线动画表现力不足，无法满足知识拆解、数据可视化、品牌短视频等场景
果：引入帧驱动、组件化的视频代码生成管线，让 Agent 能生产更灵活、更精确、可版本控制的视频
```

### 2.2 技术选型分析

| 决策项 | 选择 | 推导逻辑 |
|-------|------|---------|
| **视频 DSL** | JSX + TypeScript（类 React 组件） | Agent 熟悉、生态成熟、组件可复用；CSS/SVG/Canvas 可直接用于视频 |
| **时间模型** | 离散帧（frame） | 保证渲染确定性，便于测试、回滚、多平台复用 |
| **渲染器** | Headless Chrome + Playwright | 复用浏览器布局能力，所见即所得；与现有 `html_to_video.py` 技术栈一致 |
| **打包器** | Vite | 启动快、配置简单、HMR 友好，适合本地开发 |
| **编码器** | FFmpeg | 成熟开源，PNG 序列 → MP4 路径清晰 |
| **TTS** | Edge TTS（保持现有） | 现有管线已集成，无需替换 |
| **Agent 接口** | 标准 Prompt 契约 + JSON Schema | 不绑定模型，任何 LLM Agent 只要遵循契约即可生成代码 |

### 2.3 为什么不直接集成 Remotion

| 方案 | 优点 | 缺点 |
|-----|------|------|
| 直接集成 Remotion | 功能完整、生态成熟 | 包体大、包含大量不需要的云端/扩展模块；学习曲线陡峭；与本质工坊现有管线融合成本高 |
| **自研轻量 DSL（本方案）** | 只保留核心能力、与现有 content-output 无缝集成、Agent 可控 | 需要自行维护 DSL 和渲染器 |

决策：**借鉴 Remotion 原理，自研轻量 DSL**，理由如下：
1. 本质工坊只需要“内容 → 视频代码 → 本地 MP4”这一主干能力；
2. 自研 DSL 可以严格控制 Agent 输出格式，降低 prompt 工程难度；
3. 与现有 `html_to_video.py` 共享 Playwright + FFmpeg 技术栈，减少新依赖。

### 2.4 架构设计理由

采用 **“三层 + 两分支”** 架构：

```
┌─────────────────────────────────────────────────────────────┐
│                     输入层：结构化内容                       │
│  （选题/拆解/文案/分镜/数据，来自本质工坊 A/B/C/D 场景产出）   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   生成层：Video Program                      │
│  Code Generator 按 Prompt 契约输出 VideoProgram.tsx          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   渲染层：Local Renderer                     │
│  Vite 打包 → Playwright 逐帧截图 → FFmpeg 合成 → MP4/GIF     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────┐   ┌─────────────────────────────┐
│   视频号管线（新分支）    │   │   视频号管线（现有分支）     │
│   essence-video-dsl     │   │   html_to_video.py          │
│   复杂动画/精确同步      │   │   简单滚动/HTML 内容        │
└─────────────────────────┘   └─────────────────────────────┘
```

---

## 第3步：怎么做（How）—— 模块设计与实现

### 3.1 全局状态设计

```typescript
// packages/video-core/src/types.ts
interface EssenceVideoState {
  composition: {
    id: string;
    width: number;
    height: number;
    fps: number;
    durationInFrames: number;
  };
  currentFrame: number;       // 渲染时的当前帧
  assets: {                   // 媒体资源清单
    audio: string[];
    video: string[];
    images: string[];
  };
  narration: {                // TTS 旁白段落
    sections: Array<{ text: string; startFrame: number; endFrame: number }>;
  };
}
```

### 3.2 模块划分与接口契约

```
essence-workshop/
└── content-output/
    └── video-dsl/                         # 新增：视频 DSL 与渲染管线
        ├── packages/
        │   ├── video-core/                # DSL 核心（类 Remotion 的轻量实现）
        │   ├── video-renderer/            # 本地渲染器（Vite + Playwright + FFmpeg）
        │   └── video-generator/           # Agent 代码生成器（Prompt + Schema + 校验）
        ├── templates/
        │   ├── composition-template.tsx   # Agent 生成代码的模板
        │   └── prompt-template.md         # 标准 Prompt 契约
        ├── examples/
        │   └── negative-numbers/          # 示例：负数科普视频
        └── docs/
            └── api-reference.md           # DSL API 参考
```

| 模块名 | 路径 | 职责 | 接口契约 |
|-------|------|------|---------|
| **video-core** | `video-dsl/packages/video-core/` | 提供 `useCurrentFrame`、`useVideoConfig`、`interpolate`、`Sequence`、`AbsoluteFill`、`Video`、`Audio`、`Img` | npm 包导出 React Hooks 和组件 |
| **video-renderer** | `video-dsl/packages/video-renderer/` | Vite 打包、Playwright 截图、FFmpeg 合成 | CLI：`essence-render <entry.tsx> --output out.mp4` |
| **video-generator** | `video-dsl/packages/video-generator/` | 接收结构化内容，调用 Agent 生成 `VideoProgram.tsx` | 输入：`ContentSpec` JSON；输出：`VideoProgram.tsx` + `manifest.json` |
| **pipeline router** | `content-output/scripts/pipelines/video/` | 根据内容特征选择走 DSL 还是 HTML 录制 | 新增 `dsl_video_pipeline.py` |

### 3.3 模块四层设计（以 video-core 为例）

#### 数据规矩

```typescript
// 帧号范围、输出配置、动画插值参数
interface CompositionConfig {
  id: string;
  width: number;           // 1080 | 1920
  height: number;          // 1920 | 1080
  fps: number;             // 30
  durationInFrames: number;
}

interface InterpolateOptions {
  easing?: (t: number) => number;
  extrapolateLeft?: 'extend' | 'clamp' | 'identity';
  extrapolateRight?: 'extend' | 'clamp' | 'identity';
}
```

#### 数据存储

- 全局状态：`TimelineContext`（React Context）
- 局部状态：`SequenceContext` 维护当前 Sequence 的相对帧偏移
- 媒体资源：运行时通过 `staticFile()` 引用，渲染前收集到 `assets` 清单

#### 数据流转

```
Agent 生成 VideoProgram.tsx
        ↓
Vite 打包为可运行页面
        ↓
Renderer 循环 frame = 0 .. durationInFrames-1
        ↓
TimelineContext 更新 currentFrame → React 重渲染
        ↓
组件树根据 frame 计算样式/显隐
        ↓
Playwright 截图 PNG
        ↓
FFmpeg 合并 PNG 序列 + 音频 → MP4
```

#### 接口层

```typescript
// video-core 对外 API
export function useCurrentFrame(): number;
export function useVideoConfig(): CompositionConfig;
export function interpolate(
  input: number,
  inputRange: [number, number],
  outputRange: [number, number],
  options?: InterpolateOptions
): number;

export const Composition: React.FC<CompositionProps>;
export const Sequence: React.FC<SequenceProps>;
export const AbsoluteFill: React.FC<AbsoluteFillProps>;
export const Video: React.FC<VideoProps>;
export const Audio: React.FC<AudioProps>;
export const Img: React.FC<ImgProps>;
export function staticFile(path: string): string;
```

### 3.4 Code Generator 设计

为了让任何 Agent 都能使用，定义标准输入/输出契约：

#### 输入：`VideoGenerationSpec`

```json
{
  "title": "负数是什么",
  "aspectRatio": "9:16",
  "durationSeconds": 60,
  "fps": 30,
  "style": "edu-cartoon",
  "sections": [
    {
      "type": "title",
      "heading": "负数是什么？",
      "subheading": "从生活到数学",
      "durationFrames": 90,
      "narration": "负数是什么？让我们从生活中找到答案。"
    },
    {
      "type": "scene",
      "heading": "电梯里的负数",
      "content": "地下一层用 -1 表示",
      "visualHint": "电梯按钮从 1 楼下降到 -1 楼",
      "durationFrames": 180,
      "narration": "坐电梯到地下一层，我们会看到负一。"
    }
  ],
  "assets": {
    "bgm": "public/bgm-edu.mp3",
    "images": ["public/elevator.png"]
  }
}
```

#### 输出：`VideoProgram.tsx`

```tsx
import { Composition, Sequence, AbsoluteFill, useCurrentFrame, interpolate, staticFile } from '@essence/video-core';

const ElevatorScene = () => {
  const frame = useCurrentFrame();
  const y = interpolate(frame, [0, 120], [0, 200]);
  return (
    <AbsoluteFill style={{ background: '#1a1a2e' }}>
      <img src={staticFile('elevator.png')} style={{ transform: `translateY(${y}px)` }} />
      <div style={{ color: '#fff', fontSize: 60 }}>地下一层 = -1</div>
    </AbsoluteFill>
  );
};

export const VideoProgram = () => (
  <Composition
    id="NegativeNumbers"
    component={ElevatorScene}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={810}
  />
);
```

#### Agent Prompt 契约（节选）

```markdown
# Role
你是一名 Video DSL 程序员。请根据输入的 VideoGenerationSpec，生成一个 TypeScript React 组件文件。

# 必须遵守的规则
1. 所有动画必须基于 `useCurrentFrame()` 返回的 frame 计算。
2. 使用 `interpolate(frame, [start, end], [from, to])` 计算数值属性。
3. 使用 `<Sequence from={...} durationInFrames={...}>` 控制元素出现时间。
4. 使用 `<AbsoluteFill>` 作为根布局容器。
5. 媒体文件必须使用 `staticFile('relative/path')` 引用。
6. 禁止使用 CSS animation、transition、requestAnimationFrame。
7. 所有视觉变化必须能从 frame 推导，保证渲染确定性。

# 输出格式
只输出完整的 VideoProgram.tsx 文件内容，不要解释。
```

### 3.5 Pipeline Router 设计

在 `content-output/scripts/pipelines/video/` 下新增路由：

```python
def select_pipeline(content_spec: dict) -> str:
    """
    根据内容特征选择视频生成管线。
    """
    if content_spec.get("visualComplexity") == "high":
        return "dsl"          # 复杂动画 → 代码生成 + 帧渲染
    if content_spec.get("hasStructuredHTML"):
        return "html_record"  # 已有高质量 HTML → 滚动录制
    if content_spec.get("source") == "wechat_article":
        return "article_to_video"  # 公众号文章 → slides 模板
    return "dsl"              # 默认走 DSL
```

### 3.6 与现有管线的关系

```
content-output 视频号管线
├── html_to_video.py        # 保留：HTML 滚动录制
├── article_to_video.py     # 保留：公众号文章转视频
└── dsl_video_pipeline.py   # 新增：代码生成 + 帧渲染
```

- 不删除、不替换现有管线；
- 新增 DSL 管线作为“高精度动画”分支；
- 由 Agent 根据内容特征自动选择，或让用户手动指定。

---

## 第4步：实施路线图

### Phase 1：最小可用（MVP，1-2 周）

- [ ] 实现 `video-core`：useCurrentFrame、interpolate、Sequence、AbsoluteFill、Img
- [ ] 实现 `video-renderer`：Vite 打包 + Playwright 截图 + FFmpeg 合成
- [ ] 实现 `video-generator`：Prompt 模板 + 输出 VideoProgram.tsx
- [ ] 跑通 1 个案例（如“负数是什么”或“一个概念科普”）
- [ ] 编写 DSL API 文档和 Agent Prompt 模板

### Phase 2：接入本质工坊（2-3 周）

- [ ] 在 `content-output/scripts/pipelines/video/` 下实现 `dsl_video_pipeline.py`
- [ ] 与选题/拆解/文案流程打通，自动生成 `VideoGenerationSpec`
- [ ] 支持 TTS 旁白、BGM、竖屏/横屏切换
- [ ] 支持 Video/Audio 组件和媒体资源同步
- [ ] 添加管线选择路由

### Phase 3：沉淀与扩展（持续）

- [ ] 建立常用动画组件库（FadeIn、FlyIn、Counter、Timeline、Compare）
- [ ] 让 Agent 在生成代码时引用组件库
- [ ] 支持 GIF 输出
- [ ] 增加渲染质量预设（fast / standard / high）

---

## 第5步：验证契约

### 前置条件 P

| 条件 | 验证方式 |
|-----|---------|
| Node.js 18+ 已安装 | `node --version` |
| Chrome 可被 Playwright 启动 | `npx playwright install chromium` |
| FFmpeg 可用 | `ffmpeg -version` |
| Agent 能输出符合契约的 TypeScript | 编译通过 |

### 后置条件 Q

| 条件 | 目标值 |
|-----|-------|
| DSL 管线能成功渲染 60 秒竖屏视频 | 输出 MP4 文件 |
| 视频帧与代码描述一致 | 人工抽检 5 个关键帧 |
| 旁白与画面时间对齐误差 | < 200ms |
| 不破坏现有 HTML 录制管线 | 现有测试用例通过 |

### 不变量 I

| 条件 | 验证方式 |
|-----|---------|
| 现有公众号/视频号/HTML 管线功能不变 | 回归测试 |
| `content-output` 对外接口不破 | 接口契约检查 |
| Agent Prompt 契约保持向后兼容 | Schema 校验 |

---

## 第6步：失败模式

| 步骤 | 失败场景 | 处理动作 |
|------|---------|---------|
| Agent 生成代码 | 输出不符合 DSL 契约，编译失败 | 返回错误给 Agent，附带契约规范和修复示例，要求重试 |
| Agent 生成代码 | 使用了 CSS animation / requestAnimationFrame | 静态检查拦截，提示改用 useCurrentFrame + interpolate |
| 渲染阶段 | Playwright 截图超时 | 增加等待策略，或提示用户降低 composition 复杂度 |
| 渲染阶段 | FFmpeg 合成失败 | 检查音频/视频资源路径，fallback 到无声视频 |
| 长视频 | 渲染时间超长 | 默认限制 MVP 阶段视频时长 ≤ 90 秒，超出提示分段 |
| 环境缺失 | Chrome/FFmpeg 未安装 | 前置检查失败，输出安装指南 |

---

## 附录 A：最小 DSL 示例

```tsx
import {
  Composition,
  Sequence,
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
} from '@essence/video-core';

const TitleScene = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 1]);

  return (
    <AbsoluteFill style={{ background: '#0f172a', justifyContent: 'center', alignItems: 'center' }}>
      <h1 style={{ color: '#fff', fontSize: 80, opacity }}>负数是什么？</h1>
    </AbsoluteFill>
  );
};

export const Root = () => (
  <Composition
    id="Demo"
    component={TitleScene}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={90}
  />
);
```

---

## 附录 B：Agent 调用示例

```python
from content_output.video_dsl import generate_video

result = generate_video(
    content_spec={
        "title": "负数是什么",
        "aspectRatio": "9:16",
        "durationSeconds": 30,
        "sections": [...],
    },
    agent_client=my_agent_client,  # 任何遵循契约的 Agent
    output_dir="output/video/"
)
# result: { "video": "output/video/final.mp4", "code": "output/video/VideoProgram.tsx" }
```

---

## 附录 C：与 Remotion 的对比

| 维度 | Remotion | 本质工坊 Video DSL |
|-----|----------|-------------------|
| 定位 | 全功能程序化视频框架 | 本质工坊内容输出的一个管线分支 |
| 体积 | 大（monorepo + 多扩展包） | 极小（只保留核心） |
| 云端渲染 | 原生支持 Lambda/CloudRun | 本地优先，云端未来可选 |
| 学习成本 | 高 | 低（只学几个 Hook/组件） |
| Agent 可控性 | 中（完整 Remotion API 较宽） | 高（ narrowed API + Prompt 契约） |
| 与现有管线集成 | 需额外适配 | 原生集成 content-output |

---

## 深入模块文档索引

| 模块 | 文档 |
|-----|------|
| Video DSL 核心 | [[04-video-core-四层设计]] |
| 本地渲染器 | [[05-video-renderer-四层设计]] |
| Agent 代码生成器 | [[06-video-generator-四层设计]] |
| 管线路由器 | [[07-pipeline-router-四层设计]] |
| 实施路线与验证契约 | [[08-实施路线图与验证契约]] |

---

*本方案由本质工坊 · 项目开发 Skill 生成，遵循三阶方法论与基础设施四层设计原则。*
