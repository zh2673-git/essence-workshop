# 配图方案

## 核心原则

**图文相辅，不为配图而配图。** 配图是为了帮助读者理解复杂概念、建立视觉记忆，而不是装饰。每张图都必须有"为什么这里需要一张图"的理由。

---

## 三种方案

| 方案 | 适用场景 | 优点 | 优先级 |
|------|---------|------|--------|
| **方案A：SVG 直出 → PNG** | 结构图、流程图、数据图、层级图、概念示意图 | 精确可控、文字清晰、文件小、公众号渲染友好 | **首选** |
| **方案B：Canvas 动画 → GIF** | 状态转换、运动过程、流动路径、力度衰减等变化过程 | 微信支持 GIF 动图、动态过程比静态图直观10倍 | **动态过程必选** |
| **方案C：image_gen AI 生图** | 需要实际照片风格、写实场景、复杂视觉效果 | 视觉丰富、可处理复杂构图 | **最后备选** |

**决策核心：内容是否包含时间维度？**
- 静态结构/关系/对比 → 方案A（SVG→PNG）
- 有变化过程/状态转换/运动 → 方案B（Canvas→GIF）
- 需要写实照片风格 → 方案C（AI生图）

---

## 配图触发条件

| 场景 | 配图类型 | 说明 |
|------|---------|------|
| 文章解释**层级/递归/嵌套结构** | 结构示意图（方案A） | 将抽象的层级关系可视化 |
| 文章描述**流程/步骤/决策链** | 流程图（方案A） | 帮助读者跟随逻辑推进 |
| 文章涉及**多个维度对比** | 对比图/矩阵图（方案A） | 表格不够直观时用图 |
| 核心概念需要**直观理解** | 概念示意图（方案A） | 用图形帮助读者建立直觉 |
| 文章有**前后对比/演变** | 前后对比图（方案A） | 展示变化结果 |
| 文章描述**变化过程/状态转换** | 动态过程图（方案B） | 必须通过动画展示 |
| 文章涉及**运动/流动/生长** | 动态过程图（方案B） | 运动轨迹、数据流动 |
| 需要**写实照片风格** | AI 生图（方案C） | 无法用几何图形表达 |

---

## 不需要配图的场景

- 纯观点/评论类内容（配图反而分散注意力）
- 已有表格清晰展示数据
- 短文（< 1000字），图片会打断阅读节奏
- 概念本身足够简单，文字已能清晰传达

---

## 配图数量原则

- **图文并茂是硬要求**：文章必须包含配图，纯文字文章体验差
- **⚠️ 7000-8000字长文硬性配图规则：必须5张配图（4 PNG + 1 GIF）**
  - 4张静态PNG：覆盖各核心章节，每个章节开头至少1张
  - 1张动态GIF：放在最核心的"变化过程/状态转换"处
  - 此规则不可省略，不可用5张PNG替代（GIF是必选项）
- **封面不算在内**：封面是独立的，配图指正文中的插图
- **论文风格版优先配图**：对话版一般不配图（保持对话节奏）
- **图文比例协调**：图片间距均匀，不要集中在一个章节

---

## 配图位置规则（重要）

- **每个章节开头放一张配图**：文章的每个主要章节（## H2 级别）开头都应放置一张与该章节内容相关的配图，图片紧跟在章节标题之后、正文文字之前
- **长章节灵活添加**：如果某个章节文字超过1500字，除了章节开头的配图外，可在章节中间适当位置再添加1张配图
- **配图与内容协调**：每张配图必须与所在章节的内容直接相关

---

## 方案A：SVG 直出 → PNG（首选）

### ⚠️ 微信图片要点

1. SVG 不能直接在微信文章中显示（微信仅支持 JPG/PNG/GIF）
2. 本地路径图片不能直接显示，必须上传到微信 CDN
3. **⚠️ SVG→PNG 转换必须用 Playwright 渲染**——cairosvg 无法正确渲染中文字体（会回退为衬线字体）。Playwright 不可用时才降级到 cairosvg
4. **⚠️ Playwright 必须使用 base64 编码方式加载 SVG**，不要用 `file:///` 方式（部分 SVG 渲染异常）
5. SVG 封面生成使用纯 Python 实现，无需外部依赖

### SVG 通用模板

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 {height}" width="800" height="{height}">
  <rect width="800" height="{height}" fill="#FAF7F2" rx="12"/>
  <style>
    .title   { font-family: 'PingFang SC','Microsoft YaHei',sans-serif; font-size: 22px; font-weight: bold; fill: #3C2415; text-anchor: middle; }
    .sub     { font-family: 'PingFang SC','Microsoft YaHei',sans-serif; font-size: 14px; fill: #666; text-anchor: middle; }
    .box-title { font-family: 'PingFang SC','Microsoft YaHei',sans-serif; font-size: 18px; font-weight: bold; fill: #fff; text-anchor: middle; }
    .box-desc  { font-family: 'PingFang SC','Microsoft YaHei',sans-serif; font-size: 14px; fill: rgba(255,255,255,0.9); text-anchor: middle; }
  </style>
  <text x="400" y="40" class="title">{图标题}</text>
</svg>
```

### SVG 配色规范

| 用途 | 颜色值 | 说明 |
|------|--------|------|
| 背景 | `#FAF7F2` | 奶油白，全图背景 |
| 一级底色（主色） | `#C96442` | 赭石橙，主层级/主要步骤 |
| 二级底色（深色） | `#8B5E3C` | 深棕，次级层级/步骤 |
| 三级底色（最深） | `#3C2415` | 最深色，最高级/汇总 |
| 上涨阳线 | `#A3D4A0` | K线图中上涨 |
| 下跌阴线 | `#E8836B` | K线图中下跌 |
| 文字（主） | `#3C2415` | 标题文字 |
| 文字（次） | `#666` | 正文说明文字 |

### SVG 文字溢出检查规则（重要）

SVG 手写时容易出现文字超出框外的问题，必须遵循以下规则：

1. **框高度计算**：框高度 ≥ 文字行数 × 行高 + 上下 padding（至少各 20px）
2. **多行文字用 `<tspan>`**：使用 `<tspan x="..." dy="行高">` 逐行排列，而非绝对 y 坐标，避免行间距不一致
3. **文字宽度检查**：长文本用浏览器开发者工具检查是否超出框边界
4. **生成后视觉验证**：SVG→PNG 后必须检查文字是否在框内、字体是否正确

### SVG→PNG 转换脚本

```python
import os, glob, re, base64

svgs = sorted(glob.glob('0*.svg'))

try:
    from playwright.sync_api import sync_playwright
    print("Using Playwright for SVG→PNG conversion...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for svg_file in svgs:
            png_file = svg_file.replace('.svg', '.png')
            with open(svg_file, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            m = re.search(r'width="(\d+)".*?height="(\d+)"', svg_content)
            w, h = int(m.group(1)), int(m.group(2))
            page = browser.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2)
            svg_b64 = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
            page.goto(f'data:image/svg+xml;base64,{svg_b64}', timeout=60000)
            page.wait_for_timeout(500)
            page.screenshot(path=png_file, timeout=60000)
            page.close()
        browser.close()
except ImportError:
    import cairosvg
    print("WARNING: Playwright not available, falling back to cairosvg (中文字体可能异常)...")
    for svg_file in svgs:
        png_file = svg_file.replace('.svg', '.png')
        cairosvg.svg2png(url=svg_file, write_to=png_file, scale=3)
```

---

## 方案B：Canvas 动画录制为 GIF（动态过程必选）

### ⚠️ 微信公众号动态内容限制

微信不支持 JavaScript（Canvas 无法运行）、不支持 `<video>` 自动播放、不支持 SVG 动画。**GIF 动图是公众号中展示动态内容的唯一方式。**

### 触发条件

1. 文章内容描述了一个**变化过程**（循环/迭代/状态转换/运动）
2. 静态图**无法完整表达**该过程的语义
3. **⚠️ 强制规则**：如果文章描述了"循环/迭代/状态转换"类概念（如自然选择的变异→选择→保留循环），**必须**生成至少1个GIF，不能用静态图替代

### GIF 参数约束

| 参数 | 推荐值 | 最大值 | 说明 |
|------|--------|--------|------|
| 时长 | 3-6秒 | 8秒 | 越短越好 |
| 帧率 | 8-10 fps | 15 fps | 公众号场景不需要高帧率 |
| Canvas逻辑尺寸 | 800×500 | 800×600 | 逻辑尺寸，实际渲染为2x |
| DPR（设备像素比） | 2 | 2 | 确保文字清晰、不模糊 |
| 实际像素尺寸 | 1600×1000 | 1600×1200 | 逻辑尺寸 × DPR |
| 颜色 | 128色 | 256色 | 减少文件体积 |
| 文件大小 | ≤1.5MB | 3MB | 高清GIF允许稍大 |
| 每篇数量 | 0-1个 | 2个 | GIF是稀缺资源 |

### Canvas 高清渲染标准（重要）

为确保GIF中文字清晰、不溢出、不重叠，Canvas动画必须遵循以下标准：

**1. DPR 2x 渲染**
```javascript
const DPR = 2;
const W = 800, H = 500;  // 逻辑尺寸
canvas.width = W * DPR;   // 实际像素 1600×1000
canvas.height = H * DPR;
canvas.style.width = W + 'px';
canvas.style.height = H + 'px';
ctx.scale(DPR, DPR);      // 所有绘制使用逻辑坐标
```

**2. 文字不溢出原则**
- 所有文字使用 `textBaseline` 明确对齐方式（推荐 `'top'` 或 `'middle'`）
- 文字位置计算时预留至少20px边距
- 长文本使用 `ctx.measureText()` 检测宽度，超宽则换行或缩小字号
- 圆角矩形内的文字，x坐标从 `rect.x + 20` 开始，不超过 `rect.x + rect.w - 20`

**3. 文字不重叠原则**
- 相邻文字行间距至少24px（15px字号）或28px（16px字号）
- 标题与正文间距至少30px
- 使用 `ctx.save()/ctx.restore()` 管理状态，避免 `globalAlpha` 污染

**4. 录制时 viewport 设置**
```python
page = browser.new_page(
    viewport={'width': 800, 'height': 500},  # 与Canvas逻辑尺寸一致
    device_scale_factor=2  # 2x渲染
)
```

### ⚠️ 帧步进模式（必须使用）

**为什么不能用 requestAnimationFrame 自动播放？**

`requestAnimationFrame` 以约60fps运行，40帧动画在0.67秒内就跑完了。而截图脚本通常每200ms截一次，6秒内只能捕获3-4个不同的动画帧，剩余截图都是静态最终帧——GIF看起来就是一张静态图片。

**必须使用帧步进模式**：HTML动画暴露 `window.stepFrame(f)` 和 `window.getTotalFrames()` 接口，由Python脚本精确控制每一帧的渲染。

### Canvas 帧步进 HTML 模板

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body { margin: 0; background: #FAF7F2; display: flex; justify-content: center; align-items: center; height: 100vh; }
  canvas { display: block; }
</style>
</head>
<body>
<canvas id="canvas"></canvas>
<script>
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const DPR = 2;
const W = 800, H = 500;
canvas.width = W * DPR;
canvas.height = H * DPR;
canvas.style.width = W + 'px';
canvas.style.height = H + 'px';
ctx.scale(DPR, DPR);

const TOTAL_FRAMES = 60;
let currentFrame = 0;

function drawFrame(f) {
  ctx.clearRect(0, 0, W, H);
  const progress = f / TOTAL_FRAMES;
  // ... 绘制逻辑（使用逻辑坐标，DPR已通过scale处理）
  // progress 从 0 到 1，控制动画进度
}

// 帧步进接口（必须暴露）
window.stepFrame = function(f) {
  currentFrame = Math.max(0, Math.min(f, TOTAL_FRAMES - 1));
  drawFrame(currentFrame);
};

window.getTotalFrames = function() {
  return TOTAL_FRAMES;
};

// 绘制首帧
drawFrame(0);
</script>
</body>
</html>
```

### GIF 录制脚本（帧步进模式）

```python
import os
from PIL import Image
from playwright.sync_api import sync_playwright

def record_gif(html_path, output_path, frame_delay_ms=120, pause_frames=15):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={'width': 800, 'height': 500},
            device_scale_factor=2
        )
        page.goto(f'file:///{os.path.abspath(html_path)}', timeout=60000)
        page.wait_for_timeout(500)

        total_frames = page.evaluate('window.getTotalFrames()')
        frames = []

        for i in range(total_frames):
            page.evaluate(f'window.stepFrame({i})')
            page.wait_for_timeout(50)
            screenshot = page.screenshot(timeout=60000)
            from io import BytesIO
            img = Image.open(BytesIO(screenshot))
            frames.append(img.convert('RGB'))

        for _ in range(pause_frames):
            frames.append(frames[-1].copy())

        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=frame_delay_ms,
            loop=0,
            optimize=True
        )

        browser.close()

    file_size_kb = os.path.getsize(output_path) / 1024
    print(f"GIF saved: {output_path} ({file_size_kb:.1f} KB, {len(frames)} frames)")

    if file_size_kb < 100:
        print(f"⚠️ WARNING: GIF is only {file_size_kb:.1f} KB — animation may not be working!")

if __name__ == '__main__':
    import sys
    html_path = sys.argv[1] if len(sys.argv) > 1 else 'animation.html'
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'output.gif'
    record_gif(html_path, output_path)
```

### GIF 生成后质量自检

生成GIF后必须执行以下检查：

| 检查项 | 标准 | 异常处理 |
|--------|------|---------|
| 文件大小 | ≥100KB | <100KB 说明动画帧未正确捕获，需检查帧步进接口 |
| 文件大小 | ≤3MB | >3MB 需减少帧数或降低分辨率 |
| 帧数 | ≥20帧 | 帧数过少动画不流畅 |
| 首帧内容 | 非空白 | 首帧空白说明 drawFrame(0) 有问题 |
| 字体渲染 | 非衬线体 | 出现衬线体说明 DPR 设置有误 |

### Canvas 动画设计规范

| 规范 | 说明 |
|------|------|
| **帧步进模式** | ⚠️ 必须使用帧步进模式，禁止 requestAnimationFrame 自动播放 |
| **循环播放** | GIF 设置 `loop=0`（无限循环），末尾加 pause_frames 帧暂停 |
| **配色一致** | 使用 claude-warm 主题配色 |
| **文字标注** | 关键状态/步骤用文字标注在 Canvas 上 |
| **简洁聚焦** | 一个 GIF 只展示一个变化过程 |
| **首帧有意义** | GIF 第一帧就应该是有意义的状态 |

---

## 方案C：image_gen AI 生图（最后备选）

当内容需要写实风格的图时，使用 image_gen 工具直接生成 PNG 格式图片。大多数场景应优先使用方案A或方案B。

### prompt 编写规范

**好的 prompt**（具体、可执行）：
```
"一张缠论级别递归结构示意图：底部是5根K线重叠构成一笔，3笔构成线段，
3段线段重叠构成中枢，箭头从下往上连接各层级，标注'K线→笔→线段→中枢'，
每个层级用不同颜色区分（赭石橙/深棕/暖灰），背景为奶白色，风格简洁现代"
```

**prompt 核心要素**：图类型、核心要素、布局、配色（claude-warm: 赭石橙+奶油白）、风格（简洁现代）
