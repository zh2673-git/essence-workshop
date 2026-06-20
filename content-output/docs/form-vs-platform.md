# 内容输出架构重构提案：形式（Form）vs 平台（Platform）

> 状态：已落地（视频管线 + html/slides/pptx/notebook 统一调度）/ 2026-06-20  
> 背景：Video DSL 案例完成后，发现现有管线命名以平台为主，容易与内容形式混淆。本方案将 content-output 显式拆分为“形式层”与“平台适配层”。视频管线与其他非视频形式已完成统一调度与平台适配器合并。

## 1. 问题：当前管线的命名惯性

现有 6 条管线：

| 管线名 | 实际输出 | 形式 | 平台 |
|--------|---------|------|------|
| 公众号 | 微信受限 HTML | html | wechat |
| 视频号 | MP4/GIF | video/gif | video-channel |
| HTML交互 | 标准 HTML | html | browser |
| 演示 | Reveal.js HTML | slides | browser |
| PPT | .pptx | pptx | office |
| Notebook | .ipynb | notebook | jupyter |

问题：
- “公众号”和“HTML交互”都输出 HTML，但平台约束不同，无法自然复用。
- “视频号”管线实际输出 video，未来若要支持 B站/抖音需新增管线，而非复用 video 形式。
- Agent 在选择时容易困惑：先决定“做什么”，还是先决定“发哪里”。

## 2. 新模型：先选形式，再选平台

```
┌─────────────────────────────────────────────────────────────┐
│                        元素层（Element）                      │
│  文本元素 / 图形元素 / 动画元素 / 音频元素 / 交互元素            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       形式层（Form）                         │
│  markdown / html / video / image / slides / notebook / pptx  │
│  负责：把元素组装成该形式的“标准表达”，不关心具体平台约束        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      平台适配层（Platform）                   │
│  wechat / obsidian / video-channel / bilibili / browser       │
│  office / jupyter / ...                                      │
│  负责：把标准形式转换为平台接受的成品（尺寸、标签、链接、文件格式） │
└─────────────────────────────────────────────────────────────┘
```

## 3. 形式（Form）定义

形式回答“**内容用什么媒介表达**”。

| 形式 | 标准产物 | 说明 |
|------|---------|------|
| `markdown` | `.md` | 纯文本结构化，可嵌入图片/公式 |
| `html` | `.html` | 标准浏览器 HTML/CSS/JS |
| `video` | `.mp4` / `.mov` | 帧级动画视频 |
| `gif` | `.gif` | 短循环动图 |
| `image` | `.png` / `.jpg` / `.svg` | 静态图 |
| `slides` | `.html` (Reveal.js) | 演示文稿 |
| `pptx` | `.pptx` | PowerPoint 文件 |
| `notebook` | `.ipynb` | Jupyter Notebook |

## 4. 平台（Platform）定义

平台回答“**该媒介在目标环境的约束是什么**”。

| 平台 | 适配目标 | 典型约束 |
|------|---------|---------|
| `wechat` | 微信公众号 | 受限 HTML、图片防盗链、段落间距、字体 |
| `obsidian` | Obsidian 笔记 | wiki-link、callout、本地附件路径 |
| `browser` | 普通浏览器 | 标准 HTML、响应式、无特殊限制 |
| `video-channel` | 微信视频号 | 9:16、竖屏、时长、封面 |
| `bilibili` | B站 | 16:9、分辨率、码率、字幕 |
| `douyin` | 抖音 | 9:16、时长、封面、背景音乐 |
| `office` | PPT/WPS | 幻灯片尺寸、字体嵌入、版式 |
| `jupyter` | Jupyter | 代码单元、Markdown 单元、输出单元 |

## 5. 重构后的调用方式

### CLI

已落地：

```bash
# 旧：以平台为入口（仍兼容）
python -m scripts.cli video VideoProgram.tsx --pipeline dsl --output output/video/

# 新：先形式，后平台
python -m scripts.cli output --form video --platform video-channel \
  --input VideoProgram.tsx --output output/video-channel/

# 同一内容输出为不同平台
python -m scripts.cli output --form video --platform bilibili \
  --input VideoProgram.tsx --output output/bilibili/
```

### Router

```python
from router import select_method
select_method({'platform': 'bilibili', 'hasAnimationRequirements': True})
# → {'method': 'dsl', 'platform': 'bilibili', ...}
```

## 6. 与现有管线的映射

| 旧管线 | 新映射 |
|--------|--------|
| 公众号管线 | `form=html` + `platform=wechat` |
| 视频号管线 | `form=video` + `platform=video-channel` |
| HTML交互管线 | `form=html` + `platform=browser` |
| 演示管线 | `form=slides` + `platform=browser` |
| PPT管线 | `form=pptx` + `platform=office` |
| Notebook管线 | `form=notebook` + `platform=jupyter` |

## 7. 对 Video DSL 的意义

Video DSL 目前默认输出 `form=video`，并硬编码 9:16（视频号）。按新模型：

- `video-core` 属于**形式层**，与平台无关。
- `video-renderer` 渲染出 `video` 形式后，由**平台适配层**决定最终参数：
  - `--platform video-channel` → 9:16, 1080x1920
  - `--platform bilibili` → 16:9, 1920x1080
  - `--platform douyin` → 9:16, 720x1280

这样避免为每个视频平台复制一套 renderer。

## 8. 迁移路径

| 阶段 | 动作 | 状态 | 风险 |
|------|------|------|------|
| 1 | 新增 `form-vs-platform.md` 并更新相关 Skill 文档 | ✅ | 低 |
| 2 | 在视频 `pipeline.py` 中同时支持旧平台名和新 `--form/--platform` 参数 | ✅ | 低 |
| 3 | 新增视频平台适配器（`video-channel` / `bilibili` / `douyin`） | ✅ | 中 |
| 4 | 将 `scripts/pipelines/` 下的其他脚本（html/slides/pptx/notebook）按形式重组 | ✅ | 中 |
| 5 | 合并视频平台适配器与通用平台适配器到统一 `platforms/` 目录 | ✅ | 中 |
| 6 | 实现统一调度器 `dispatcher.py`，按 form + platform 路由并应用约束 | ✅ | 中 |
| 7 | 逐步废弃旧的平台名入口，保留 alias | ⏳ | 低 |
| 8 | 更新 CLI 帮助与路由表 | ✅（视频部分） | 低 |

## 10. 实现细节

### 10.1 统一平台适配器

所有平台适配器已合并到 `content-output/scripts/pipelines/platforms/`：

- 通用平台：`browser` / `wechat` / `office` / `jupyter` / `reveal`
- 视频平台：`video-channel` / `bilibili` / `douyin`
- 基类：`PlatformAdapter`（通用）与 `VideoPlatformAdapter`（视频专用）
- 注册中心：`platforms/__init__.py` 提供 `get_adapter()` / `list_platforms()` / `supported_platforms_for_form()`

### 10.2 统一调度器

`content-output/scripts/pipelines/dispatcher.py` 是形式-平台调度的唯一入口：

```python
dispatch(form='video', platform='bilibili', elements_dir='...', output_dir='...')
dispatch(form='html',  platform='wechat',  elements_dir='...', output_dir='...')
```

为避免 `scripts` / `html` 等通用包名冲突，dispatcher 通过 `importlib` 按文件路径加载各形式生成器，各生成器仍保持独立实现。

### 10.3 形式复用验证

统一调度器与平台适配器上线后，同一 `form` 可被多个 `platform` 复用：

- `form=html` → `browser` / `wechat`
- `form=slides` → `browser` / `reveal`
- `form=pptx` → `office`
- `form=video` → `video-channel` / `bilibili` / `douyin`
- `form=notebook` → `jupyter`

元素层资产保持跨平台不变；平台适配层只修改约束参数，不重建元素。

## 11. 与本质工坊三层架构的对位

| 本质工坊三层 | content-output 对应层 | 职责 |
|-------------|----------------------|------|
| 元素层（Element） | `output/elements/` | 原子资产：文本/图形/动画/音频/数据 |
| 管线层（Pipeline） | `form` 生成器 + `dispatcher` | 把元素组装为形式标准表达 |
| 平台层（Platform） | `platforms/` 适配器 | 按目标平台约束输出成品 |

在此对位下，`form` 不是“底层元素”，而是**元素层之上的第一层抽象**——它定义了元素如何被组织成媒介表达；`platform` 是再上一层，解决“该媒介在特定环境中的约束”。形式的标准化使它可以被多个平台复用，平台适配器则只关心差异约束。

## 12. 不变量

- 旧命令继续可用（兼容性 alias）。
- 元素层资产跨形式/平台复用。
- 现有 `wechat-zh2673` 等案例不受影响。

