# Excalidraw 元素规格说明

AI生成白板内容时必须遵守此规范，保证输出可以被Excalidraw正确加载。

## 画布规格

- 画布为无限大，不设边界
- 建议每页（讲解单元）内容宽度不超过1600px，高度不超过900px
- 相邻讲解单元之间保留 300px 横向/纵向间距，避免拥挤
- 标准视口尺寸：1920×1080（录制分辨率）

## 通用元素属性

所有Excalidraw元素都必须包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一ID，建议用uuid或自增序号 |
| `type` | string | 元素类型：rectangle/ellipse/diamond/line/arrow/text/freedraw/image |
| `x` | number | 左上角X坐标 |
| `y` | number | 左上角Y坐标 |
| `width` | number | 宽度 |
| `height` | number | 高度 |
| `angle` | number | 旋转角度（弧度），默认0 |
| `strokeColor` | string | 描边颜色，推荐用手绘色板 |
| `backgroundColor` | string | 填充颜色，默认"transparent" |
| `fillStyle` | string | 填充样式：hachure/cross-hatch/solid，默认"hachure"（手绘阴影） |
| `strokeWidth` | number | 线宽：1/2/4，默认2 |
| `strokeStyle` | string | 线型：solid/dashed/dotted，默认"solid" |
| `roughness` | number | 手绘粗糙度：0(规整)/1(自然)/2(非常手绘)，默认1 |
| `opacity` | number | 不透明度：0-100，默认100 |
| `groupIds` | string[] | 分组ID数组，默认[] |
| `seed` | number | 随机种子，影响手绘效果，随便填一个数字即可 |
| `version` | number | 版本号，默认1 |
| `versionNonce` | number | 随机数，随便填 |
| `isDeleted` | boolean | 是否删除，默认false |
| `boundElements` | array | 绑定的元素（比如箭头绑定到形状），默认[] |
| `updated` | number | 时间戳，默认1 |
| `link` | string/null | 链接，默认null |
| `locked` | boolean | 是否锁定，默认false |

## 推荐手绘色板

使用这些颜色保持统一手绘风格：

```
描边色：
- "#1e1e1e" 黑色（主要内容，默认）
- "#e03131" 红色（重点强调、错误）
- "#2f9e44" 绿色（正确、正向）
- "#1971c2" 蓝色（信息、链接）
- "#f08c00" 橙色（警告、提示）
- "#9c36b5" 紫色（特殊概念）

填充色（透明/半透明）：
- "transparent" 透明（默认）
- "#ffc9c9" 浅红填充
- "#b2f2bb" 浅绿填充
- "#a5d8ff" 浅蓝填充
- "#ffec99" 浅黄填充
- "#eebefa" 浅紫填充
```

## 各类型元素特殊属性

### 1. 矩形 (rectangle) / 椭圆 (ellipse) / 菱形 (diamond)

无额外特殊属性，通用属性即可。

### 2. 文本 (text)

| 字段 | 类型 | 说明 |
|------|------|------|
| `text` | string | 文本内容 |
| `fontSize` | number | 字号：16/20/28/36，标题用28/36，正文用20 |
| `fontFamily` | number | 字体：1=手写字体(Virgil)，2=印刷体(Helvetica)，3=等宽字体，**推荐2**（v2修正：fontFamily=1导致中文渲染不稳定，强制用2） |
| `textAlign` | string | 对齐："left"/"center"/"right"，默认"left" |
| `verticalAlign` | string | 垂直对齐："top"/"middle"/"bottom"，默认"top" |
| `containerId` | string/null | **必填**：如果文本在形状内部，必须填形状的id；如果文本独立存在，填null。未设置会导致文本被形状填充遮挡，出现"点击才显示"的问题 |
| `originalText` | string | 和text一样即可 |
| `autoResize` | boolean | 自动调整大小，默认true |
| `lineHeight` | number | 行高，默认1.25 |

**注意**：如果文本要放在矩形/椭圆内部，不需要自己计算坐标，只需要设置containerId为形状id，Excalidraw会自动居中。

> ⚠️ **严重警告**：若文本位于形状内部但未设置 `containerId`，Excalidraw 会将其视为独立浮动元素。当形状设置了 `backgroundColor`（填充色）时，文本会被填充层遮挡，表现为"点击才显示"的问题。所有放在形状内部的文本必须设置 `containerId`，并在对应形状的 `boundElements` 中添加 `{id: text_id, type: "text"}` 双向绑定。
>
> ⚠️ **一对一原则**：每个形状（rectangle/ellipse/diamond）最多只能绑定一个文本元素。若多个文本共享同一个 `containerId`，所有绑定到该容器的文本都无法渲染。需要在一个形状内展示多行内容时，应使用单个 text 元素，通过 `\n` 换行，并设置 `textAlign: "center"` 和 `verticalAlign: "middle"`。

### 3. 箭头/直线 (arrow/line)

| 字段 | 类型 | 说明 |
|------|------|------|
| `points` | array | 点坐标数组，格式 [[0,0], [dx1, dy1], [dx2, dy2]...]，第一个点永远是[0,0]，后续点是相对于起点的偏移 |
| `startBinding` | object/null | 起点绑定到某个元素：{elementId: "xxx", ...} |
| `endBinding` | object/null | 终点绑定到某个元素：{elementId: "xxx", gap: 5, ...} |
| `startArrowhead` | string/null | 起点箭头：null/"arrow"/"bar"/"dot"/"triangle"，箭头默认null |
| `endArrowhead` | string/null | 终点箭头，arrow类型默认"arrow"，line类型默认null |

**注意**：points坐标是相对于元素自身x,y的偏移，不是绝对坐标！比如从(100,100)画到(300,100)的横线，应该是：
```json
{
  "type": "arrow",
  "x": 100,
  "y": 100,
  "points": [[0,0], [200, 0]]
}
```

### 4. 图片 (image)

用于嵌入外部图片（如其他场景生成的SVG图解、知识图谱、架构图等）。配合 `scripts/svg_to_whiteboard.py` 使用。

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 图片状态："saved"（已保存到files）/"pending"，默认"saved" |
| `fileId` | string | 关联到顶层 files 字段的图片ID，如 "file_scene0_0" |
| `scale` | number[] | 缩放比例，格式 [1, 1] 表示不缩放 |

**image元素完整结构**：

```json
{
  "type": "image",
  "id": "img_scene0_0",
  "x": 100,
  "y": 200,
  "width": 800,
  "height": 600,
  "angle": 0,
  "strokeColor": "transparent",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "groupIds": [],
  "seed": 12345,
  "version": 1,
  "versionNonce": 12345,
  "isDeleted": false,
  "boundElements": [],
  "updated": 1,
  "link": null,
  "locked": false,
  "status": "saved",
  "fileId": "file_scene0_0",
  "scale": [1, 1]
}
```

**配套的顶层 files 字段**（必须放在 .whiteboard.json 的顶层）：

```json
"files": {
  "file_scene0_0": {
    "mimeType": "image/png",
    "id": "file_scene0_0",
    "dataURL": "data:image/png;base64,<base64编码的PNG数据>"
  }
}
```

**重要约束**：
1. image元素的 `fileId` 必须能在顶层 files 字段中找到对应条目
2. dataURL 必须包含完整的 MIME 前缀：`data:image/png;base64,`
3. 默认 `strokeColor` 和 `backgroundColor` 都是 "transparent"（图片本身有内容，不需要描边）
4. `fillStyle` 用 "solid"（image不支持hachure等手绘填充）
5. `scale` 通常保持 [1, 1]，缩放通过 width/height 控制

### SVG→PNG→image 混合渲染方案

针对其他场景（K12拆解、知识图谱、HTML管线、演示管线等）生成的SVG，使用 `scripts/svg_to_whiteboard.py` 桥接：

```
SVG文件
  ↓ svg_to_png.py (Playwright渲染，确保中文字体正确)
PNG文件
  ↓ base64编码
image元素 + files字段
  ↓ 合并到 .whiteboard.json
完整白板项目
```

**使用场景**：
- K12拆解的复杂知识图谱SVG → 嵌入白板作为参考图
- 项目解析的架构图SVG → 嵌入白板作为背景图
- HTML管线的交互演示SVG → 嵌入白板作为静态参考

**与原生Excalidraw元素的关系**：
- image元素是**补充手段**，不是替代
- AI生成的手绘图解（rectangle/arrow/text）仍然是主线，承担"顿悟触发点"和"本质定义金句框"
- image元素用于嵌入"难以用Excalidraw原生元素表达"的复杂图解

## 输出格式规范

AI必须输出如下JSON结构（v2扩展字段已加入）：

```json
{
  "title": "内容标题",
  "canvas_layout": "horizontal",
  "methodology_version": "v2",
  "total_scenes": 5,
  "scenes": [
    {
      "scene_index": 0,
      "scene_phase": "stage1_what",
      "scene_title": "阶段1·是什么：[本质点破]",
      "essence_definition": "本质定义一句话（揭底式）",
      "essence_check": "本质检验通过说明",
      "viewport_x": 960,
      "viewport_y": 540,
      "viewport_zoom": 1,
      "duration_estimate": 60,
      "epiphany_trigger": "顿悟触发点金句",
      "teleprompter_script": "口语化讲解文本...",
      "elements": [/* Excalidraw元素数组 */]
    },
    {
      "scene_index": 1,
      "scene_phase": "stage2_why",
      "scene_title": "阶段2·为什么：[反常识根因]",
      "causal_chain": "因果链一句话总结",
      "counterintuitive_root": "反常识根因",
      "structural_metaphor": "结构性比喻",
      "viewport_x": 3180,
      "viewport_y": 540,
      "viewport_zoom": 1,
      "duration_estimate": 60,
      "epiphany_trigger": "反常识根因金句",
      "teleprompter_script": "讲解文本（含反常识根因）...",
      "elements": []
    },
    {
      "scene_index": 2,
      "scene_phase": "stage3_how",
      "scene_title": "阶段3·怎么做：[视角升级]",
      "perspective_upgrade": "视角升级金句",
      "viewport_x": 5400,
      "viewport_y": 540,
      "viewport_zoom": 1,
      "duration_estimate": 60,
      "epiphany_trigger": "视角升级金句",
      "teleprompter_script": "讲解文本（含视角升级收尾）...",
      "elements": []
    }
  ],
  "files": {}
}
```

**v2 扩展字段说明**：

| 字段 | 必填 | 说明 |
|------|------|------|
| `methodology_version` | 是 | 固定值 "v2" |
| `scene_phase` | 是 | "stage1_what" / "stage2_why" / "stage3_how" |
| `essence_definition` | 阶段1必填 | 本质定义一句话（揭底式，非描述性） |
| `essence_check` | 阶段1可选 | 本质检验说明 |
| `causal_chain` | 阶段2必填 | 因果链总结 |
| `counterintuitive_root` | 阶段2必填 | 反常识根因 |
| `structural_metaphor` | 阶段2可选 | 结构性比喻 |
| `perspective_upgrade` | 阶段3必填 | 视角升级金句 |
| `epiphany_trigger` | 全部阶段必填 | 顿悟触发点金句 |
| `files` | 顶层可选 | image元素对应的图片数据（base64 dataURL），无image元素时为空对象 |

## 布局建议（非强制）

1. **标题页**：大标题居中，副标题在下方，字体大一点
2. **内容排布**：相关元素靠近，不相关元素之间留足空白
3. **流程/步骤**：用箭头按顺序连接，左→右或上→下
4. **对比关系**：左右/上下并排摆放，中间可以加竖线分隔
5. **包含关系**：外面一个大矩形，内部放小元素
6. **层级关系**：从上到下或从中心向外放射
7. **重点强调**：大字号 + 红色/橙色描边 + 浅背景填充
8. **箭头绑定**：箭头尽量绑定到形状上，不要悬空

## 手绘风格原则

- 不需要太规整，稍微歪一点更有手绘感（roughness=1默认就好）
- 文字不要太长，用关键词和短句，不要写大段文字
- 线条可以有适当的弯曲，不用画得笔直
- 不要填满整个区域，适当留白
