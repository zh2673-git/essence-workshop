---
name: PPT/WPS平台
description: |
  PPT/WPS平台适配器：将PPT格式产物（.pptx）适配为PowerPoint/WPS兼容的演示成品。
  关注字体嵌入、幻灯片尺寸、WPS兼容性、模板适配。
  输入：PPT格式产物（.pptx）。输出：平台兼容的.pptx成品。
  触发词：「做PPT」「做幻灯片」「WPS版」。
version: 1.0
layer: workflow
adapter: ppt-wps
---

# PPT/WPS平台适配器

> 将PPT格式产物适配为PowerPoint/WPS兼容的演示成品。

## 平台约束

| 约束项 | 说明 |
|--------|------|
| 格式 | .pptx（兼容PowerPoint 2016+ 和 WPS 2019+） |
| 幻灯片尺寸 | 16:9（33.87cm × 19.05cm）或 4:3（25.4cm × 19.05cm） |
| 字体 | 建议嵌入字体（EmbedFonts）；中文用微软雅黑/思源黑体，避免Mac专属字体 |
| 图片 | 分辨率≥150DPI，格式PNG/JPEG；透明背景用PNG |
| 动画 | WPS对部分PowerPoint动画兼容性差，复杂动画建议简化 |
| 文件大小 | 建议<50MB |

## 适配流程

```
1. PPT格式产物（.pptx）→ 检查幻灯片尺寸
2. 检查字体可用性 → 嵌入字体或替换为通用字体
3. 检查图片分辨率和格式
4. 验证WPS兼容性（动画/过渡/SmartArt）
5. （可选）应用品牌模板（brand-spec.json）
6. 导出 .pptx 成品
```

## 与格式管线的关系

| 层级 | 职责 |
|------|------|
| **格式管线（ppt/）** | 从认知产物生成.pptx文件（内容+布局） |
| **平台适配（本适配器）** | 将.pptx适配为PowerPoint/WPS兼容成品（字体+兼容性） |

## 脚本

```
ppt-wps/
└── scripts/                    # 适配脚本（规划中）
    └── adapter.py              # .pptx→平台兼容.pptx
```

格式管线脚本：[../../format/ppt/scripts/generator.py](../../format/ppt/scripts/generator.py)
共享平台脚本：[../scripts/platforms/office.py](../scripts/platforms/office.py)

## 使用场景

- 知识探索的演示文稿输出
- 项目开发的设计评审PPT
- 任何需要PowerPoint/WPS演示的成品

---

*PPT/WPS平台 · .pptx→平台兼容.pptx · PowerPoint+WPS双兼容*
