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
| `type` | string | 元素类型：rectangle/ellipse/diamond/line/arrow/text/freedraw |
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
| `fontFamily` | number | 字体：1=手写字体(Virgil)，2=印刷体(Helvetica)，3=等宽字体，推荐1 |
| `textAlign` | string | 对齐："left"/"center"/"right"，默认"left" |
| `verticalAlign` | string | 垂直对齐："top"/"middle"/"bottom"，默认"top" |
| `containerId` | string/null | 如果文本在形状内部，填形状的id，文本会自动居中 |
| `originalText` | string | 和text一样即可 |
| `autoResize` | boolean | 自动调整大小，默认true |
| `lineHeight` | number | 行高，默认1.25 |

**注意**：如果文本要放在矩形/椭圆内部，不需要自己计算坐标，只需要设置containerId为形状id，Excalidraw会自动居中。

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

## 输出格式规范

AI必须输出如下JSON结构：

```json
{
  "title": "内容标题",
  "canvas_layout": "horizontal", // horizontal=横向排列，vertical=纵向排列
  "total_scenes": 5,
  "scenes": [
    {
      "scene_index": 0,
      "scene_title": "封面/标题页",
      "viewport_x": 960, // 镜头中心X坐标
      "viewport_y": 540, // 镜头中心Y坐标
      "viewport_zoom": 1, // 缩放比例，默认1
      "duration_estimate": 60, // 预计讲解秒数
      "teleprompter_script": "口语化讲解文本...",
      "elements": [/* Excalidraw元素数组 */]
    },
    // ... 更多场景
  ]
}
```

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
