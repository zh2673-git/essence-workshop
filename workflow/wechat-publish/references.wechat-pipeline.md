# 公众号管线规范（WeChat Official Account Pipeline）

> 从内容框架读取 → 按微信平台约束转换 → 推送草稿箱
> 内容风格/字数/配图由内容框架层决定，本管线只做平台适配与推送。

---

## 管线概览

```
内容产物读取 → 微信平台约束适配 → 排版 → 图片上传 → 平台检查 → 推送草稿箱
```

## 元素消费与转换

| 元素类型 | 转换规则 | 工具 |
|---------|---------|------|
| 文本元素 | Markdown → 微信内联样式HTML | wechat_converter.py |
| SVG图形 | SVG → PNG（2x DPI） | Playwright |
| SVG动画 | SVG动画 → GIF | Playwright录制 |
| Canvas动画 | Canvas → GIF | Playwright录制 |
| 交互元素 | 降级为静态截图（PNG） | Playwright截图 |
| 音频元素 | 不消费 | — |

## 微信平台约束

### 排版约束

- 禁止使用 :::block 容器模块（微信草稿箱会剥离容器样式）
- 正文不用 # H1（H1由标题位占用）
- 正文不要重复出现文章标题
- 优先原生 Markdown 语法：## 标题、**加粗**、> 引用、--- 分割线、- 列表

### 字符数约束

| 指标 | 限制 | 说明 |
|------|------|------|
| HTML总字符数（含标签） | ≤20000 | 微信草稿箱硬性上限 |

### 封面图约束

- 封面图是必选项——微信草稿箱API要求 `thumb_media_id`
- 封面图必须与正文配图完全不同
- 不要在正文中插入封面图
- 画幅比例：wide（1240×770，16:10）
- 封面图由内容框架提供，本管线检查尺寸并上传

### 配图平台约束

配图内容由内容框架生成，本管线只做平台格式检查与上传：

- SVG 需转为 PNG（2x DPI，公众号不渲染SVG）
- GIF 文件大小 ≥100KB 且 ≤3MB
- 所有本地图片必须上传素材库后用素材URL引用

## 执行步骤

1. 读取内容产物（Markdown/HTML + 配图 + 封面图，来自内容框架）
2. SVG → PNG（Playwright渲染，device_scale_factor=2）
3. SVG动画 → GIF
4. Markdown → 微信HTML（wechat_converter.py）
5. 配图插入对应位置
6. 图片上传素材库，替换为素材URL
7. HTML总字符检查（≤20000，超限则智能样式去重）
8. 封面图尺寸检查（1240×770）
9. 推送草稿箱（必须带 `--cover`）

## 命令

```bash
# 完整管线（必须指定封面图）
python publish.py output/article.md --cover output/cover.jpg --author "公众号名"

# 仅检查不推送
python publish.py output/article.md --check-only
```

## 质量自检（仅平台约束）

| 检查项 | 标准 | 异常处理 |
|--------|------|---------|
| SVG→PNG字体 | 非衬线体 | 出现衬线体说明未用Playwright |
| SVG→PNG溢出 | 文字在框内 | 溢出则调整SVG框高度 |
| SVG→PNG清晰度 | 2x DPI | 模糊则检查device_scale_factor |
| GIF文件大小 | ≥100KB且≤3MB | <100KB说明动画未生效 |
| HTML总字符数 | ≤20000 | 超出则智能样式去重，不截断正文 |

---

*公众号管线规范 · 纯平台适配 · 内容风格由框架层决定*
