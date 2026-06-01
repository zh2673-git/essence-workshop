# 本质工坊 v2 管线升级方案：TeachAny + huashu-design 能力迁移

> 基于 TeachAny（互动课件）和 huashu-design（设计交付）两个项目的深度解析，将可迁移的核心能力融入本质工坊现有三层架构，不打破现有管线行为。

---

## 一、前置评估：能否实现参考项目的展示效果？

### 1.1 诚实回答：部分能，部分不能

| 参考项目效果 | 能否实现 | 原因 |
|-------------|---------|------|
| **TeachAny 分页课件**（slide-page + 播放控制栏 + 侧边导航） | ✅ 能 | 模板结构可直接移植，CSS/JS 无技术壁垒 |
| **TeachAny 五件套模块**（AI学伴/TTS/Hints/导师/知识图谱） | ⚠️ 部分 | 交互逻辑可移植，但AI学伴需要后端API，当前只能做前端壳 |
| **TeachAny Hero知识结构图** | ✅ 能 | gen-hero-svg.py 是纯前端SVG生成，可直接移植 |
| **TeachAny 课件验证** | ✅ 能 | 19项基线检查是规则引擎，可直接移植 |
| **huashu-design html2pptx**（精确保位+文本可编辑） | ✅ 能 | 核心是 Playwright DOM 读取 + pptxgenjs，可直接移植 |
| **huashu-design 核心资产协议**（5步品牌采集） | ⚠️ 部分 | 流程可移植，但自动搜索/下载依赖网络环境和品牌官网结构 |
| **huashu-design 设计方向顾问**（5流派×20哲学→3方向） | ✅ 能 | 纯数据+模板渲染，无技术壁垒 |
| **huashu-design Tweaks变体切换**（实时调参面板） | ✅ 能 | CSS变量+localStorage，纯前端实现 |
| **huashu-design Motion Design**（产品发布动画） | ❌ 不能 | 本质工坊的视频管线是教育内容导向，不是产品动画导向，设计语言完全不同 |
| **huashu-design iOS原型**（iPhone边框+可点击） | ❌ 不能 | 这是独立的产品原型能力，与本质工坊的「认知→输出」定位不匹配 |
| **huashu-design 信息图/数据可视化** | ⚠️ 部分 | CSS Grid+精确排版可移植，但印刷级输出（PDF/SVG导出）需要额外工具链 |

### 1.2 关键差距分析

**能实现的效果**与参考项目之间，差距不在技术实现，而在**设计质量**：

1. **TeachAny 的视觉质量**来自：每种页型（cover/concept/quiz/summary）有独立的CSS渐变装饰和布局模板。当前方案只移植了分页结构，还需要移植**内容区块模板**（content-section-templates-v2.html）

2. **huashu-design 的PPT质量**来自：HTML幻灯片本身就是精心设计的（1920×1080精确布局），html2pptx.js只是忠实还原。当前方案需要先让Slides管线输出高质量HTML幻灯片，PPT管线才能产出高质量PPT

3. **两个项目的共同质量来源**：反AI-slop设计规范。当前方案的模板设计需要遵循这些规范，否则产出仍会有"AI味"

### 1.3 结论

> **升级方案能让本质工坊获得参考项目的核心能力骨架和关键交互效果，但展示效果的"最后一公里"取决于模板设计质量，而非代码移植。**
>
> 换言之：代码移植解决"能不能做"，模板设计解决"好不好看"。两者都需要做。

---

## 二、两个参考项目的核心能力清单

### 2.1 TeachAny 可迁移能力

| # | 能力 | 本质 | 迁移价值 |
|---|------|------|---------|
| T1 | **分页课件骨架** (course-skeleton-v2) | slide-page分页结构，每页独立音频，底部播放控制栏+侧边胶囊导航 | ⭐⭐⭐ HTML管线核心升级 |
| T2 | **内容区块模板** (content-section-templates-v2) | 每种页型（cover/interactive/concept/quiz/summary）有独立HTML片段+CSS装饰 | ⭐⭐⭐ 决定视觉质量的关键 |
| T3 | **五件套标准模块** | AI学伴、TTS narrator、section hints、知识图谱、导师卡片 | ⭐⭐ 交互模块从5→10 |
| T4 | **Hero知识结构图** | gen-hero-svg.py 自动生成知识点关系SVG | ⭐⭐ 元素层新增能力 |
| T5 | **TTS引擎** | tts-engine.py，Edge TTS封装，支持多voice/rate/重试/并发 | ⭐⭐ 视频管线增强 |
| T6 | **课件验证** | validate-courseware.cjs，19项基线检查 | ⭐⭐ HTML管线质量门禁 |
| T7 | **知识树+课标检索** | find_nodes.py + 课标数据 | ⭐ 低——本质工坊不面向K12课标 |

### 2.2 huashu-design 可迁移能力

| # | 能力 | 本质 | 迁移价值 |
|---|------|------|---------|
| H1 | **html2pptx.js** | Playwright读取DOM computed style → pptxgenjs精确还原位置/字号/颜色 | ⭐⭐⭐ PPT管线核心升级 |
| H2 | **核心资产协议** | 5步品牌采集（问→搜→下载→验证→固化为brand-spec.md） | ⭐⭐⭐ 全管线品牌一致性 |
| H3 | **设计方向顾问** | 5流派×20哲学→3方向并行Demo | ⭐⭐ HTML/Slides管线风格选择 |
| H4 | **Junior Designer工作流** | 先假设+placeholder→用户确认→迭代 | ⭐⭐ 管线运行模式升级 |
| H5 | **Tweaks变体切换** | CSS变量参数化+localStorage持久化+侧面板切换 | ⭐⭐ HTML管线新能力 |
| H6 | **反AI-slop规则** | 禁止紫渐变/emoji图标/Inter字体等AI味设计 | ⭐⭐ 模板设计规范 |
| H7 | **Motion Design引擎** | Stage+Sprite时间切片+useTime/useSprite/interpolate | ⭐ 视频管线已有类似实现 |
| H8 | **5维度专家评审** | 哲学一致/视觉层级/细节/功能/创新 各10分 | ⭐ 新能力但非核心 |

---

## 三、迁移优先级排序

按 **影响面 × 实现难度 × 效果可见度** 排序：

| 优先级 | 迁移项 | 来源 | 影响 | 难度 | 效果可见度 | 理由 |
|--------|--------|------|------|------|-----------|------|
| **P0** | html2pptx.js 移植 | H1 | PPT管线质变 | 中 | 高 | 唯一能精确保位+文本可编辑的方案 |
| **P0** | 分页课件骨架 + 内容区块模板 | T1+T2 | HTML管线质变 | 低 | 极高 | 分页结构+页型装饰=TeachAny视觉效果 |
| **P1** | 核心资产协议 | H2 | 全管线品牌一致性 | 中 | 高 | 品牌提取从色值→完整资产 |
| **P1** | 五件套模块 | T3 | HTML交互模块翻倍 | 低 | 高 | 5→10模块，纯前端移植 |
| **P1** | 反AI-slop设计规范 | H6 | 全管线视觉质量 | 低 | 极高 | 零代码成本，纯规范约束 |
| **P2** | 课件验证 | T5 | HTML管线质量 | 中 | 中 | 19项基线检查 |
| **P2** | 设计方向 + Tweaks | H3+H5 | HTML/Slides体验 | 中 | 高 | 风格选择+实时调参 |
| **P3** | TTS引擎增强 | T4 | 视频管线稳定性 | 低 | 中 | 重试+并发 |
| **P3** | Hero知识结构图 | T3 | 元素层新能力 | 低 | 中 | 自动生成知识点SVG |

---

## 四、逐项迁移方案

### P0-1: html2pptx.js 移植 → PPT管线升级

#### 现状

[generator.py](../scripts/pipelines/pptx/generator.py) 用 python-pptx 粗糙生成：
- Markdown正则拆分→默认布局→文本截断2000字
- SVG完全忽略（只处理PNG）
- 品牌色未应用
- 文本不可精确定位

#### 目标

HTML → Playwright读取DOM → pptxgenjs精确还原 → 文本可编辑的.pptx

#### 方案

```
scripts/pipelines/pptx/
├── generator.py          # 保留，增加 --mode 参数
├── html2pptx.js          # 新增：移植huashu-design核心（~500行）
├── bridge.py             # 新增：Python→Node.js桥接
└── __init__.py
```

#### 关键改动

1. **移植 `html2pptx.js`**（从huashu-design `scripts/html2pptx.js`）
   - 核心函数：`extractSlideData(page)` — Playwright读取DOM computed style
   - 核心函数：`addElements(slideData, targetSlide, pres)` — pptxgenjs精确还原
   - 支持：文本（字号/颜色/粗体/斜体/旋转）、图片、形状、列表、合并文本框
   - 支持：CSS渐变背景、box-shadow→PPT阴影、旋转文字
   - 支持：`data-pptx-merge` 容器折叠段落为可编辑文本框
   - 支持：`class="placeholder"` 元素提取位置信息

2. **新增 `bridge.py`**：Python调用Node.js
   ```python
   def html_to_pptx(html_path, output_path, layout='LAYOUT_16x9'):
       result = subprocess.run(
           ['node', HTML2PPTX_JS, html_path, output_path, '--layout', layout],
           capture_output=True, text=True
       )
       return result.returncode == 0
   ```

3. **升级 `generator.py`**：
   - 新增 `--mode simple|precise` 参数
   - `simple`：当前python-pptx行为（默认，向后兼容）
   - `precise`：先通过Slides管线生成HTML幻灯片→html2pptx.js转换
   - 新增 `--layout LAYOUT_16x9|LAYOUT_4x3` 参数

4. **依赖声明**：
   ```json
   // package.json 新增
   {
     "dependencies": {
       "pptxgenjs": "^3.12",
       "sharp": "^0.33"
     }
   }
   ```

#### 不打破现有架构

- `--mode simple` 是默认值，现有调用方式完全不变
- html2pptx.js 是新增文件，不影响现有代码
- bridge.py 是新增文件，只在 `--mode precise` 时调用

#### 效果对比

| 维度 | simple模式（现有） | precise模式（升级后） |
|------|-------------------|---------------------|
| 文本定位 | 默认布局，不可控 | 精确到像素级 |
| 文本可编辑 | 部分可编辑 | 完全可编辑（真实文本框） |
| SVG处理 | 忽略 | SVG→PNG→精确定位 |
| 品牌色 | 未应用 | 从HTML CSS变量自动提取 |
| 字体/字号 | 默认 | 从DOM computed style精确还原 |
| 旋转文字 | 不支持 | 支持任意角度 |
| 阴影 | 不支持 | CSS box-shadow→PPT阴影 |

---

### P0-2: 分页课件骨架 + 内容区块模板 → HTML管线升级

#### 现状

[generator.py](../scripts/pipelines/html/generator.py) 输出连续滚动HTML：
- 无分页，所有内容在一个长页面
- 无页型区分，所有section样式相同
- 无播放控制栏
- 无独立音频支持

#### 目标

支持分页模式（slide-page），每种页型有独立视觉装饰，底部播放控制栏+侧边导航

#### 方案

```
templates/
├── course-skeleton.html        # 保留：连续滚动模板
├── course-skeleton-v2.html     # 新增：分页模板（移植TeachAny）
├── content-section-templates-v2.html  # 新增：内容区块模板片段
└── reveal-template.html        # 保留
```

#### 关键改动

1. **移植 `course-skeleton-v2.html` 模板**（从TeachAny `skill/templates/`）
   - `<section class="slide-page" data-page-index="0" data-page-type="cover">`
   - 底部播放控制栏：上一页/下一页/页码/播放模式切换
   - 侧边胶囊导航：页码计数器 + 条形指示器
   - 每页独立音频：`<audio data-page="0" src="tts/s01.mp3">`
   - 页面切换动画：CSS transition + JS控制
   - 响应式：桌面端侧边导航，移动端底部导航

2. **移植 `content-section-templates-v2.html`**（从TeachAny `skill/templates/`）
   - 每种页型的HTML片段模板：
     - `cover`：大标题+副标题+背景渐变
     - `interactive`：问题锚点+操作区+反馈区
     - `concept`：核心概念+图示+解释
     - `quiz`：题目+选项+即时反馈
     - `summary`：要点回顾+知识图谱
     - `objectives`：学习目标列表
   - 每种页型有独立的CSS渐变装饰（不同色调/方向/透明度）
   - 片段用 `{{CONTENT_SECTIONS}}` 占位符插入主模板

3. **升级 `generator.py`**：
   - 新增 `--mode scroll|paged` 参数
   - `scroll`：当前行为（默认，向后兼容）
   - `paged`：使用v2模板，自动按页型分配内容
   - 新增 `--page-types` 参数：指定每页的页型
   - 新增 `--audio-dir` 参数：每页独立音频目录

4. **页型自动推断逻辑**：
   ```python
   def infer_page_type(section_index, total_sections, heading):
       if section_index == 0:
           return "cover"
       if section_index == total_sections - 1:
           return "summary"
       if any(kw in heading for kw in ["测试", "练习", "quiz"]):
           return "quiz"
       if any(kw in heading for kw in ["互动", "探究", "实验"]):
           return "interactive"
       if any(kw in heading for kw in ["目标", "目的"]):
           return "objectives"
       return "concept"
   ```

#### 不打破现有架构

- `--mode scroll` 是默认值，现有输出完全不变
- v2模板是新增文件，不影响现有模板
- 内容区块模板是新增文件，只在 `--mode paged` 时使用

#### 效果对比

| 维度 | scroll模式（现有） | paged模式（升级后） |
|------|-------------------|-------------------|
| 页面结构 | 连续滚动 | 分页，每页独立 |
| 页型区分 | 无 | 6种页型，各有视觉装饰 |
| 播放控制 | 无 | 底部控制栏+侧边导航 |
| 独立音频 | 不支持 | 每页独立TTS音频 |
| 页面切换 | 无 | CSS动画过渡 |
| 移动端 | 基础响应式 | 专用移动端导航 |
| 最少页数 | 无限制 | ≥12页（TeachAny基线） |

---

### P1-1: 核心资产协议 → 品牌提取器升级

#### 现状

[brand_extractor.py](../scripts/elements/brand_extractor.py) 只从文章中抽取色值，输出 `brand-spec.json`

#### 目标

5步品牌采集（问→搜→下载→验证→固化），输出完整 `brand-spec.md`

#### 方案

```
scripts/elements/
├── brand_extractor.py    # 保留，增加 --protocol full 模式
└── __init__.py
```

#### 关键改动

1. **新增 `--protocol simple|full` 参数**
   - `simple`：当前行为（默认，向后兼容）
   - `full`：5步品牌资产协议

2. **5步协议实现**（移植huashu-design核心资产协议）：

   **Step 1 · 问**：交互式资产清单
   ```
   关于 <brand>，请提供以下资料（按优先级）：
   1. Logo（SVG / 高清PNG）
   2. 产品图 / 官方渲染图
   3. UI截图 / 界面素材
   4. 色值清单（HEX / RGB）
   5. 字体清单（Display / Body）
   6. Brand guidelines / 官网链接
   ```

   **Step 2 · 搜**：自动搜索官方渠道
   - `<brand>.com/brand` · `<brand>.com/press` · `brand.<brand>.com`
   - 官网header的inline SVG提取logo
   - 官网CSS提取色值

   **Step 3 · 下载**：按资产类型三条兜底路径
   - Logo：独立文件 → HTML提取inline SVG → 社交媒体avatar
   - 产品图：官方产品页 → press kit → YouTube截帧
   - UI截图：App Store截图 → 官网screenshots → 视频截帧

   **Step 4 · 验证**：5-10-2-8原则
   - 搜索5轮，找10个素材，选2个好的，每个≥8分
   - 评分维度：分辨率/版权/气质契合/风格一致/独立叙事

   **Step 5 · 固化**：输出 `brand-spec.md`
   ```markdown
   # <Brand> · Brand Spec
   ## 核心资产
   ### Logo
   - 主版本：assets/<brand>-brand/logo.svg
   - 浅底反色版：assets/<brand>-brand/logo-white.svg
   ### 产品图
   - 主视角：assets/<brand>-brand/product-hero.png
   ### UI截图
   - 主页：assets/<brand>-brand/ui-home.png
   ## 辅助资产
   ### 色板
   - Primary: #XXXXXX
   - Background: #XXXXXX
   ### 字型
   - Display: <font stack>
   - Body: <font stack>
   ### 气质关键词
   - <3-5个形容词>
   ### 禁区
   - <明确不能做的>
   ```

3. **向后兼容**：
   - `--protocol simple` 输出 `brand-spec.json`（现有格式）
   - `--protocol full` 输出 `brand-spec.md`（新格式）
   - 所有管线同时支持读取两种格式

#### 不打破现有架构

- `--protocol simple` 是默认值
- 管线读取品牌规格时，同时支持 `.json` 和 `.md` 格式

---

### P1-2: 五件套模块 → 交互模块扩展

#### 现状

5个模块：slope-navigator, three-stage-progress, knowledge-graph, card-flip, comparison-table

#### 目标

新增5个TeachAny标准模块

#### 方案

```
modules/
├── card-flip/            # 保留
├── comparison-table/     # 保留
├── knowledge-graph/      # 保留
├── slope-navigator/      # 保留
├── three-stage-progress/ # 保留
├── ai-companion/         # 新增：AI学伴
│   ├── index.html
│   ├── script.js
│   └── style.css
├── tts-narrator/         # 新增：TTS旁白播放器
│   ├── index.html
│   ├── script.js
│   └── style.css
├── section-hints/        # 新增：段落提示
│   ├── index.html
│   ├── script.js
│   └── style.css
├── mentor-card/          # 新增：导师卡片
│   ├── index.html
│   ├── script.js
│   └── style.css
└── quiz-widget/          # 新增：互动测验
    ├── index.html
    ├── script.js
    └── style.css
```

#### 各模块设计

| 模块 | 功能 | 交互方式 | 移植来源 |
|------|------|---------|---------|
| **ai-companion** | 浮动AI学伴，可提问 | 点击展开对话框，输入问题 | TeachAny AI学伴（前端壳，无后端） |
| **tts-narrator** | 页面TTS播放控制 | 播放/暂停/语速/语音选择 | TeachAny TTS narrator |
| **section-hints** | 段落级提示气泡 | 悬停/点击显示提示 | TeachAny section hints |
| **mentor-card** | 导师信息卡片 | 点击展开/折叠 | TeachAny 导师卡片 |
| **quiz-widget** | 互动测验组件 | 选择/判断/填空+即时反馈 | TeachAny 评估模块 |

#### 不打破现有架构

- 纯新增模块，不影响现有5个
- `generator.py` 的 `AVAILABLE_MODULES` 列表自动扩展
- 现有模块调用方式不变

---

### P1-3: 反AI-slop设计规范 → 模板质量保障

#### 现状

模板设计无规范约束，可能产出"AI味"设计

#### 目标

将huashu-design的反AI-slop规则固化为模板设计规范

#### 方案

在 `references/` 中新增设计规范文件，所有模板必须遵循。

#### 核心规则（移植自huashu-design）

| 规则 | 禁止 | 推荐 |
|------|------|------|
| **配色** | 紫色渐变、彩虹渐变、低饱和暖色堆叠 | oklch色彩空间、品牌色+中性色、1个accent色 |
| **图标** | emoji图标、SVG简笔画人形 | 精选icon库（Lucide/Phosphor）、或不用图标 |
| **布局** | 圆角+左边框accent、卡片堆砌 | CSS Grid精确排版、`text-wrap: pretty` |
| **字体** | Inter作为display字体 | 精选serif display字体 + 系统sans-serif body |
| **图片** | CSS剪影代替真实产品图 | 真实图片引用，或诚实placeholder（灰块+标签） |
| **装饰** | 过度圆角、阴影堆叠、毛玻璃滥用 | 克制装饰、信息密度优先、留白即设计 |

#### 不打破现有架构

- 纯规范文件，不修改任何代码
- 后续新建/修改模板时遵循此规范

---

### P2-1: 课件验证 → HTML管线质量门禁

#### 方案

```
scripts/pipelines/html/
├── generator.py
├── validator.py          # 新增：HTML输出验证
└── __init__.py
```

#### 检查项

| # | 检查项 | 标准 | 级别 |
|---|--------|------|------|
| 1 | 文件大小 | ≤ 5MB | 错误 |
| 2 | SVG可渲染 | 无语法错误 | 错误 |
| 3 | 交互模块JS | 无语法错误 | 错误 |
| 4 | viewport设置 | 有meta viewport | 错误 |
| 5 | 品牌色变量 | --primary已定义 | 警告 |
| 6 | 移动端布局 | @media查询存在 | 警告 |
| 7 | 分页模式 | ≥12页（paged模式） | 警告 |
| 8 | 页型覆盖 | 至少含cover+concept+summary | 警告 |
| 9 | 音频文件 | 每页有对应音频（paged模式） | 提示 |
| 10 | 无障碍 | 图片有alt属性 | 提示 |

#### 不打破现有架构

- 验证器是新增文件
- `generator.py` 生成后可选调用验证（`--validate` 参数）

---

### P2-2: 设计方向顾问 + Tweaks变体切换

#### 方案

```
scripts/pipelines/html/
├── generator.py
├── direction_advisor.py  # 新增：设计方向顾问
├── tweaks_injector.py    # 新增：Tweaks面板注入
└── __init__.py
```

#### 设计方向顾问

移植huashu-design的5流派×20哲学：

| 流派 | 代表 | 核心哲学 | 视觉特征 |
|------|------|---------|---------|
| 信息建筑 | Pentagram | 结构即设计 | 精确网格、信息密度高 |
| 运动诗学 | Field.io | 动态即表达 | 流动动画、渐变过渡 |
| 东方极简 | Kenya Hara | 空即充盈 | 大留白、单色系、serif |
| 实验先锋 | Sagmeister | 规则即打破 | 不对称、拼贴、手写体 |
| 功能理性 | Dieter Rams | 少即多 | 严格网格、无装饰、system font |

输出：3个差异化方向的Demo HTML，用户选择后继续

#### Tweaks变体切换

在HTML中注入侧面板：
- CSS变量参数化（颜色/字号/间距/圆角/阴影）
- 实时预览切换
- localStorage持久化
- 导出当前参数为brand-spec

#### 不打破现有架构

- 新增文件，不影响现有代码
- `generator.py` 新增 `--directions` 和 `--tweaks` 参数
- 默认不启用

---

### P3-1: TTS引擎增强

#### 方案

在视频管线 `pipeline.py` 的 `generate_tts` 函数中增强：
- 重试机制：已有，但增加指数退避（2^n秒）
- 并发生成：当前是串行，改为 `asyncio.gather` 并发
- 进度条：显示当前/总数

#### 不打破现有架构

- 修改现有函数内部实现，接口不变

---

### P3-2: Hero知识结构图

#### 方案

```
scripts/elements/
├── brand_extractor.py
├── svg_to_png.py
├── record_gif.py
├── hero_graph.py         # 新增：Hero知识结构图生成
└── __init__.py
```

移植TeachAny的 `gen-hero-svg.py`：
- 输入：知识点列表+关系定义（JSON）
- 输出：SVG知识结构图
- 特性：节点可点击、hover高亮、自动布局

#### 不打破现有架构

- 新增文件，不影响现有代码
- 作为元素层新能力，管线可选择性读取

---

## 五、架构影响全景图

```
现有架构（不变）                              新增/升级内容
─────────────────────                        ─────────────────────

Element Layer                                Element Layer
  brand_extractor.py  ───── 升级 ────→        + --protocol full 5步资产协议
  svg_to_png.py                               (不变)
  record_gif.py                               (不变)
                                              + hero_graph.py (Hero知识结构图)

Pipeline Layer                               Pipeline Layer
  html/generator.py   ───── 升级 ────→        + --mode paged 分页模式
                                              + --directions 设计方向
                                              + --tweaks 变体面板
                                              + --validate 质量验证
                                              + validator.py
                                              + direction_advisor.py
                                              + tweaks_injector.py

  slides/generator.py                         (不变)

  pptx/generator.py   ───── 升级 ────→        + --mode precise (html2pptx.js)
                                              + html2pptx.js (Node.js)
                                              + bridge.py (Python→Node)

  video/pipeline.py   ───── 增强 ────→        TTS并发+退避优化

  wechat/publish.py                           (不变)

Platform Layer                               Platform Layer
  cli.py              ───── 扩展 ────→        新子命令透传新参数

Shared                                       Shared
  article_fetcher.py                          (不变)
  article_to_video.py                         (不变)

Templates                                    Templates
  course-skeleton.html                        (保留)
                                              + course-skeleton-v2.html (分页)
                                              + content-section-templates-v2.html
  reveal-template.html                        (保留)

Modules                                      Modules
  5个现有模块                                  (保留)
                                              + ai-companion/
                                              + tts-narrator/
                                              + section-hints/
                                              + mentor-card/
                                              + quiz-widget/

References                                   References
                                              + design-standards.md (反AI-slop规范)
```

---

## 六、实施路线图

### Phase 1：P0 核心升级（效果最显著）

| 任务 | 新增/修改文件 | 效果 |
|------|-------------|------|
| 移植html2pptx.js | 新增2文件，修改1文件 | PPT管线从骨架→可用 |
| 移植分页课件骨架+内容区块模板 | 新增2文件，修改1文件 | HTML管线视觉效果质变 |
| 反AI-slop设计规范 | 新增1文件 | 模板设计质量保障 |

### Phase 2：P1 品牌与交互（体验提升）

| 任务 | 新增/修改文件 | 效果 |
|------|-------------|------|
| 核心资产协议 | 修改1文件 | 品牌提取从色值→完整资产 |
| 五件套模块 | 新增15文件（5×3） | 交互模块翻倍 |
| 模块注册到generator | 修改1文件 | 新模块可用 |

### Phase 3：P2 质量与体验（锦上添花）

| 任务 | 新增/修改文件 | 效果 |
|------|-------------|------|
| 课件验证器 | 新增1文件 | HTML输出质量门禁 |
| 设计方向顾问 | 新增1文件 | 风格选择 |
| Tweaks变体切换 | 新增1文件 | 实时调参 |

### Phase 4：P3 增强与扩展（可选）

| 任务 | 新增/修改文件 | 效果 |
|------|-------------|------|
| TTS引擎增强 | 修改1文件 | 视频管线稳定性 |
| Hero知识结构图 | 新增1文件 | 元素层新能力 |

---

## 七、皮肉详细实现方案：视觉质量升级

> 骨架（分页结构、页型模板、交互模块、PPTX转换）已移植完成。本节补充"皮肉"——决定最终视觉质量的CSS装饰、品牌驱动、跨管线一致性。

### 7.1 皮肉是什么

```
骨架 = 结构（元素放在哪）
皮肉 = 视觉（看起来怎么样）

具体包括：
1. 页型CSS装饰 —— 每种页型的渐变背景、装饰元素、边框线条
2. 品牌色驱动 —— 所有配色从brand-spec.json的CSS变量派生
3. 排版规范 —— 字号层级、行高、间距、对齐
4. 装饰克制规则 —— 反AI-slop约束，防止过度设计
5. 跨管线视觉一致性 —— 同一内容在HTML/视频/公众号/PPT中视觉统一
```

### 7.2 页型CSS装饰规格

每种页型需要独立的视觉装饰，当前模板只有结构没有装饰。以下为每种页型的装饰规格：

#### cover（封面页）

```css
.slide-page[data-page-type="cover"] {
  background: linear-gradient(135deg, var(--primary-dim) 0%, var(--bg) 60%);
  position: relative;
  overflow: hidden;
}
.slide-page[data-page-type="cover"]::before {
  content: '';
  position: absolute;
  top: -20%; right: -10%;
  width: 50%; height: 80%;
  background: radial-gradient(circle, var(--accent-dim) 0%, transparent 70%);
  pointer-events: none;
}
.slide-page[data-page-type="cover"]::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent), transparent);
}
.slide-page[data-page-type="cover"] h1 {
  font-size: 2.4em;
  font-weight: 800;
  line-height: 1.2;
  color: var(--fg);
  margin-bottom: 0.5em;
}
.slide-page[data-page-type="cover"] .subtitle {
  font-size: 1.1em;
  color: var(--muted);
  font-weight: 400;
}
```

#### concept（概念页）

```css
.slide-page[data-page-type="concept"] {
  background: var(--bg);
  border-left: 3px solid var(--accent);
}
.slide-page[data-page-type="concept"] h2 {
  font-size: 1.6em;
  font-weight: 700;
  color: var(--fg);
  padding-bottom: 0.3em;
  border-bottom: 1px solid var(--border);
}
.slide-page[data-page-type="concept"] .key-point {
  margin-top: 1.5em;
  padding: 1em 1.2em;
  background: var(--accent-dim);
  border-radius: 8px;
  border-left: 3px solid var(--accent);
}
```

#### quiz（测验页）

```css
.slide-page[data-page-type="quiz"] {
  background: var(--bg);
  position: relative;
}
.slide-page[data-page-type="quiz"]::before {
  content: '?';
  position: absolute;
  top: 8%; right: 6%;
  font-size: 8em;
  font-weight: 900;
  color: var(--accent-dim);
  line-height: 1;
  pointer-events: none;
}
.slide-page[data-page-type="quiz"] .quiz-options {
  margin-top: 1em;
}
.slide-page[data-page-type="quiz"] .quiz-option {
  padding: 0.8em 1em;
  margin: 0.5em 0;
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.slide-page[data-page-type="quiz"] .quiz-option:hover {
  border-color: var(--accent);
  background: var(--accent-dim);
}
```

#### interactive（互动页）

```css
.slide-page[data-page-type="interactive"] {
  background: linear-gradient(180deg, var(--bg) 0%, var(--primary-dim) 100%);
}
.slide-page[data-page-type="interactive"] h2::after {
  content: '互动';
  display: inline-block;
  margin-left: 0.5em;
  font-size: 0.5em;
  padding: 0.2em 0.6em;
  background: var(--accent);
  color: white;
  border-radius: 4px;
  vertical-align: middle;
}
```

#### summary（总结页）

```css
.slide-page[data-page-type="summary"] {
  background: var(--bg);
  border-top: 3px solid var(--accent);
}
.slide-page[data-page-type="summary"] h2 {
  font-size: 1.6em;
  font-weight: 700;
  color: var(--fg);
}
.slide-page[data-page-type="summary"] li {
  padding: 0.4em 0;
  padding-left: 1.2em;
  position: relative;
}
.slide-page[data-page-type="summary"] li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--accent);
  font-weight: 700;
}
```

#### objectives（目标页）

```css
.slide-page[data-page-type="objectives"] {
  background: var(--bg);
}
.slide-page[data-page-type="objectives"] .objective-list li {
  padding: 0.6em 0 0.6em 2em;
  position: relative;
  border-bottom: 1px solid var(--border);
}
.slide-page[data-page-type="objectives"] .objective-list li::before {
  content: counter(list-item);
  position: absolute;
  left: 0;
  width: 1.5em; height: 1.5em;
  background: var(--accent);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8em;
  font-weight: 700;
}
```

### 7.3 品牌色驱动系统

当前问题：各管线配色硬编码，互不关联。升级后所有配色从 `brand-spec.json` 统一派生。

#### brand-spec.json 扩展

```json
{
  "name": "品牌名",
  "colors": {
    "primary": "#0F766E",
    "accent": "#E94560",
    "bg": "#FAFAFA",
    "fg": "#1A1A1A",
    "muted": "#7A7A9E",
    "border": "#E5E7EB"
  },
  "derived": {
    "primary-dim": "rgba(15,118,110,0.08)",
    "accent-dim": "rgba(233,69,96,0.08)",
    "card-bg": "rgba(255,255,255,0.7)",
    "card-border": "rgba(0,0,0,0.06)"
  },
  "fonts": {
    "display": "'Noto Serif SC', Georgia, serif",
    "body": "-apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif",
    "mono": "'JetBrains Mono', 'Fira Code', monospace"
  },
  "spacing": {
    "page-padding": "48px 64px",
    "section-gap": "48px",
    "content-max-width": "800px"
  }
}
```

#### CSS变量注入

所有模板通过CSS变量消费品牌规格：

```css
:root {
  --primary: {{colors.primary}};
  --accent: {{colors.accent}};
  --bg: {{colors.bg}};
  --fg: {{colors.fg}};
  --muted: {{colors.muted}};
  --border: {{colors.border}};
  --primary-dim: {{derived.primary-dim}};
  --accent-dim: {{derived.accent-dim}};
  --card-bg: {{derived.card-bg}};
  --card-border: {{derived.card-border}};
  --font-display: {{fonts.display}};
  --font-body: {{fonts.body}};
  --font-mono: {{fonts.mono}};
}
```

### 7.4 跨管线视觉一致性映射

同一内容在不同管线中的视觉对应关系：

| 视觉元素 | HTML分页课件 | 视频号 | 公众号 | PPTX |
|---------|------------|--------|--------|------|
| **主色** | `--primary` CSS变量 | `C.accent` 主题色 | `color:#C96442` 内联 | 主题色XML |
| **背景** | CSS渐变 | Canvas渐变 | `background:#FAF7F2` | 幻灯片背景 |
| **标题字号** | 2.4em | 72*S px | 22px | 36pt |
| **正文行高** | 1.8 | 1.6 | 1.8 | 1.5 |
| **圆角** | 8px | drawRRect 8*S | border-radius:6px | 无（PPT限制） |
| **卡片** | CSS box-shadow | drawGlassCard | border+background | 形状+填充 |
| **accent装饰线** | border-left:3px | ctx.fillRect 3*S | border-left:3px | 形状线条 |
| **代码块** | pre+code深色背景 | 不适用 | pre内联深色背景 | 等宽字体文本框 |

#### 跨管线品牌色同步机制

```
brand-spec.json（唯一真相源）
       │
       ├──→ HTML管线：注入CSS变量 → 模板消费
       │
       ├──→ 视频管线：读取JSON → 映射到THEMES对象
       │    C = {
       │      accent: spec.colors.accent,
       │      bg1: spec.colors.bg,
       │      fg: spec.colors.fg,
       │      ...
       │    }
       │
       ├──→ 公众号管线：读取JSON → 映射到THEMES内联样式
       │    THEMES["brand"] = {
       │      "h1": f"font-size:22px;color:{spec.colors.fg};",
       │      "blockquote": f"border-left:3px solid {spec.colors.accent};",
       │      ...
       │    }
       │
       └──→ PPTX管线：读取JSON → 映射到pptxgenjs主题
            slide.background = { fill: spec.colors.bg }
            text.color = spec.colors.fg
```

### 7.5 皮肉对公众号和视频管线的提升分析

#### 公众号管线提升

| 维度 | 当前 | 升级后 | 提升幅度 |
|------|------|--------|---------|
| 配色 | 3套硬编码主题（warm/clean/dark） | 品牌色驱动，无限主题 | ⭐⭐⭐ |
| 排版 | 固定字号/行高 | 品牌规格驱动 | ⭐⭐ |
| 视觉一致性 | 与HTML/视频无关 | 同一brand-spec统一 | ⭐⭐⭐ |
| 装饰 | 基础border-left | 页型感知装饰（测验页/概念页差异化） | ⭐⭐ |
| 反AI味 | 无约束 | 反AI-slop规则过滤 | ⭐⭐⭐ |

**关键提升点**：公众号管线当前最大的问题是3套固定主题无法适配不同品牌。品牌色驱动后，用户只需提供品牌色，公众号文章自动匹配——这意味着从"3种选择"变成"无限定制"。

#### 视频管线提升

| 维度 | 当前 | 升级后 | 提升幅度 |
|------|------|--------|---------|
| 配色 | 4套硬编码主题（dark/warm/minimal/nature） | 品牌色驱动，自动派生 | ⭐⭐⭐ |
| 视觉一致性 | 与HTML/公众号无关 | 同一brand-spec统一 | ⭐⭐⭐ |
| 页型装饰 | 无（所有slide-type样式类似） | 页型感知Canvas装饰 | ⭐⭐ |
| 反AI味 | 无约束 | 反AI-slop规则约束配色 | ⭐⭐ |
| 动画质量 | 已有Sprite系统，质量尚可 | 不变 | ⭐ |

**关键提升点**：视频管线当前4套主题的配色是硬编码的，如果用户品牌是绿色系，只能选nature主题（勉强接近）。品牌色驱动后，THEMES对象从brand-spec.json动态生成，视频配色与HTML课件/公众号文章完全一致。

#### 跨管线一致性的实际意义

```
场景：用户用"本质工坊"品牌（主色 #0F766E 青绿色）生成内容

当前：
  HTML课件 → 用了默认蓝紫色（--primary: #3B82F6）
  公众号文章 → 用了claude-warm主题（#C96442 橙色）
  视频号视频 → 用了dark主题（#E94560 红色）
  → 三个渠道视觉完全不一致，像三个不同产品

升级后：
  HTML课件 → --primary: #0F766E（从brand-spec读取）
  公众号文章 → accent: #0F766E（从brand-spec读取）
  视频号视频 → C.accent: #0F766E（从brand-spec读取）
  → 三个渠道视觉统一，品牌感强
```

### 7.6 实现文件清单

| 文件 | 改动类型 | 说明 |
|------|---------|------|
| `templates/course-skeleton-v2.html` | 修改 | 注入7.2节页型CSS装饰 |
| `templates/brand-spec.json` | 修改 | 扩展为7.3节品牌规格格式 |
| `scripts/pipelines/html/generator.py` | 修改 | 品牌色CSS变量注入逻辑 |
| `scripts/pipelines/wechat/converter.py` | 修改 | 新增brand-spec驱动的动态主题生成 |
| `scripts/pipelines/video/template.html` | 修改 | THEMES对象从brand-spec.json动态生成 |
| `scripts/pipelines/pptx/generator.py` | 修改 | 品牌色注入PPT主题 |
| `references/design-standards.md` | 新增 | 反AI-slop设计规范（7.7节） |

### 7.7 反AI-slop设计规范（design-standards.md）

```markdown
# 反AI-slop设计规范

## 禁止清单

| 类别 | 禁止 | 原因 |
|------|------|------|
| 配色 | 紫色渐变、彩虹渐变 | AI生成标志性配色 |
| 配色 | 低饱和暖色堆叠（米黄+浅橙+淡粉） | "温馨AI味" |
| 配色 | oklch之外的非标准色值 | 不可预测渲染 |
| 图标 | emoji作为图标 | 非专业感 |
| 图标 | SVG简笔画人形 | AI生成标志 |
| 字体 | Inter作为display字体 | "AI默认字体" |
| 字体 | 超过2种display字体 | 视觉混乱 |
| 布局 | 圆角+左边框accent的卡片堆砌 | "AI卡片模板" |
| 布局 | 三列等宽卡片 | "AI对比模板" |
| 装饰 | 过度圆角（>12px） | "AI圆润感" |
| 装饰 | 阴影堆叠（>2层） | "AI浮动感" |
| 装饰 | 毛玻璃滥用 | "iOS AI味" |
| 图片 | CSS剪影代替真实产品图 | 不诚实 |

## 推荐清单

| 类别 | 推荐 | 原因 |
|------|------|------|
| 配色 | 品牌色+中性色，1个accent | 克制即专业 |
| 配色 | oklch色彩空间 | 可预测、可插值 |
| 字体 | 1种serif display + 系统sans body | 层次感 |
| 布局 | CSS Grid精确排版 | 信息密度优先 |
| 布局 | text-wrap: pretty | 避免孤字 |
| 装饰 | 留白即设计 | 呼吸感 |
| 装饰 | 1px细线分隔 | 精致感 |
| 图片 | 真实图片引用，或诚实placeholder（灰块+标签） | 诚实 |

## 质量自检

生成任何视觉输出后，对照以下清单：
- [ ] 配色是否含紫色渐变？→ 改为品牌色+中性色
- [ ] 是否有emoji图标？→ 替换为文字或精选icon
- [ ] 圆角是否>12px？→ 降至8px
- [ ] 阴影是否>2层？→ 保留1层
- [ ] 字体是否为Inter？→ 替换为serif display
- [ ] 是否有毛玻璃效果？→ 移除或改为半透明纯色
- [ ] 卡片是否等宽三列？→ 改为不等宽Grid
```

### 7.8 皮肉实施优先级

| 顺序 | 任务 | 影响管线 | 效果 |
|------|------|---------|------|
| 1 | 品牌色CSS变量注入 | HTML | HTML课件视觉质变 |
| 2 | 页型CSS装饰 | HTML | 每种页型视觉差异化 |
| 3 | 公众号动态主题 | 公众号 | 从3主题→无限定制 |
| 4 | 视频品牌色驱动 | 视频 | 视频配色与品牌统一 |
| 5 | PPT品牌色注入 | PPTX | PPT配色与品牌统一 |
| 6 | 反AI-slop规范 | 全管线 | 视觉质量底线保障 |

---

## 八、核心约束：所有升级通过参数切换，默认行为不变

| 管线 | 现有默认行为 | 升级后默认行为 | 新参数 |
|------|------------|-------------|--------|
| HTML | `--mode scroll`（连续滚动） | `--mode scroll`（不变） | `--mode paged` 启用分页 |
| PPT | `--mode simple`（python-pptx） | `--mode simple`（不变） | `--mode precise` 启用精确定位 |
| Brand | `--protocol simple`（色值抽取） | `--protocol simple`（不变） | `--protocol full` 启用5步协议 |
| 验证 | 无 | 无 | `--validate` 启用质量检查 |
| 方向 | 无 | 无 | `--directions` 启用方向顾问 |
| Tweaks | 无 | 无 | `--tweaks` 启用变体面板 |

**向后兼容保证**：任何现有调用命令，不加新参数，输出与升级前完全一致。

---

## 九、风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| html2pptx.js需要Node.js环境 | 高 | PPT管线precise模式不可用 | simple模式始终可用；package.json声明依赖 |
| 分页模板CSS与现有模块冲突 | 中 | paged模式下模块样式异常 | 模块CSS使用scoped选择器；v2模板增加隔离层 |
| 核心资产协议依赖网络环境 | 中 | full模式搜索/下载失败 | 每步有fallback；缺失资产用placeholder |
| 新增模块JS体积过大 | 低 | HTML文件超5MB | 模块按需加载；异步注入 |
| TeachAny模板AGPL许可证限制 | 低 | 不可直接复制模板代码 | 只移植结构设计，CSS/JS重写 |

---

## 十、与已有文档的关系

本文档是 [html-rich-media-upgrade-plan.md](./html-rich-media-upgrade-plan.md) 的**落地执行方案**：

| 文档 | 定位 | 关系 |
|------|------|------|
| html-rich-media-upgrade-plan.md | 架构设计：三层架构的"为什么"和"是什么" | 上位文档，定义架构原则 |
| **本文档** | 执行方案：从参考项目迁移能力的"怎么做" | 下位文档，按架构原则执行 |

两个文档共同指导本质工坊从v1→v2的升级。

---

*本质工坊 · v2管线升级方案 · 三层架构 × 参考项目迁移 × 向后兼容*
