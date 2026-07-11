---
name: 微信公众号适配器
description: |
  微信公众号平台适配器：将 Markdown/HTML 转为公众号受限 HTML 并推送草稿箱。
  只做平台约束执行与格式转换，不干预内容风格/字数/配图——那些由内容框架层决定。
  输入：Markdown/HTML 格式产物 + 配图素材（来自内容框架）。输出：公众号受限HTML（推送草稿箱）。
  触发词：「写公众号」「发公众号」「推送文章」。
version: 2.0
layer: workflow
adapter: wechat
---

# 微信公众号适配器

> 纯平台适配器：将 Markdown/HTML 适配为公众号受限 HTML 并推送草稿箱。内容风格、字数、配图由内容框架层决定，本适配器只做平台约束执行、格式转换与素材上传。

## 输入与输出

| 项 | 说明 |
|----|------|
| 输入 | Markdown/HTML 格式产物 + 配图素材（SVG/PNG/GIF/封面图，来自内容框架） |
| 输出 | 公众号受限HTML（推送草稿箱） |

## 平台硬性约束

| 约束项 | 说明 |
|--------|------|
| CSS/JS | 不支持外部CSS/JS → 样式必须内联 |
| 图片 | 必须上传素材库后用素材URL引用 |
| 总字符数 | HTML总字符 ≤20000（超出走智能样式去重） |
| 容器 | 禁止 `:::block` 容器语法 |
| 标题 | 正文不用 `# H1`（H1由标题位占用） |
| SVG | 公众号不渲染SVG → 需转为PNG（2x DPI） |
| 封面图 | 1240×770 wide 画幅（平台硬性要求），必须与正文配图不同 |
| GIF | ≥100KB 且 ≤3MB（平台限制） |

## 适配流程

```
1. 读取格式产物（Markdown/HTML + SVG/PNG配图 + 封面图，来自内容框架）
2. SVG → PNG（2x DPI，公众号不渲染SVG）
3. 样式内联化（Markdown/HTML → 公众号受限HTML）
4. 配图插入正文
5. 图片上传素材库，替换为素材URL
6. HTML总字符检查（≤20000，超限则智能样式去重）
7. 封面图尺寸检查（1240×770）
8. 推送草稿箱（必须带 --cover）
```

## 失败模式

| 失败 | 处理 |
|------|------|
| 封面图缺失 | 推送报 `[40007]invalid media_id` → 必须提供封面图 |
| GIF <100KB | 动画未生效 → 重新录制或增加帧数 |
| HTML总字符 >20000 | 智能样式去重（提取重复内联样式为短类名） |
| 封面图格式错误 | API返回JPEG而非PNG → 文件头检查（PNG应为137,80,78,71，JPEG为255,216,255,224），将扩展名改为.jpg |

## 封面图生成标准流程

### API 原理
text_to_image API 基于 **SDXL（Stable Diffusion XL）文生图模型**：
- HTTP GET 请求，传入 `prompt`（画面描述）和 `image_size`（画幅比例）
- 返回 `image/jpeg` 二进制流，应按 prompt 内容生成对应图片
- `image_size=landscape_16_9` 最接近公众号 1240×770（约16:10）

### 历史问题根因（重要）
之前生成的封面"无法显示具体图案和文字"，**并非 SDXL 模型能力不足**，而是 **CDN 缓存问题**：
- API 响应头缺少 `Cache-Control: no-store`，CDN 边缘节点把 API 当静态资源缓存
- CDN 缓存 key 仅用 URL 路径（`/api/ide/v1/text_to_image`），**忽略 query string**
- 所有不同 prompt/image_size 的请求都命中同一份缓存
- 返回 2025-09-12 的固定占位图（MD5: `19a0b822edb11957055e4588c2159058`，1832×1832 正方形）
- 已验证：加 nonce 时间戳、Cache-Control 请求头、改变路径大小写、POST 方式均无法绕过

### generate_cover.py 的修复
脚本已加入占位图检测，命中 CDN 缓存时会报错而非静默使用占位图：
```
RuntimeError: API 返回了 CDN 缓存的固定占位图（MD5 匹配 19a0b822...）
```
当服务端修复 CDN 缓存问题后，脚本可正常生成封面。

### prompt 编写原则
1. **具体、可视化**：描述具体场景/物体/光线/构图，避免抽象概念
   - 好：`A lone traveler walking up a winding mountain path at golden hour, warm sunlight, mist in valley`
   - 差：`growth and patience concept`
2. **不要要求图中文字**：SDXL 对中文（甚至英文）文字渲染能力差，封面的文字由公众号标题位承载，图只负责视觉氛围
3. **英文 prompt**：SDXL 对英文 prompt 理解更准确

### 生成流程
```
1. 编写具体可视化的英文 prompt（场景/物体/光线/构图）
2. 调用 generate_cover.py（内部用 urllib 调用 API + 文件头验证 + 占位图检测）
3. 脚本自动验证：
   - 文件头：JPEG(0xFF,0xD8,0xFF,0xE0) 或 PNG(0x89,0x50,0x4E,0x47)
   - 占位图 MD5 检测（避免使用 CDN 缓存的固定图）
   - 根据真实格式调整扩展名
4. 推送时带 --cover 参数
```

### 常见错误
- 错误：使用Write工具写入文本到图片文件 → 产生损坏文件
- 正确：用 urllib/Invoke-WebRequest 下载 API 二进制响应
- 错误：假设API返回PNG → 导致文件名与内容不匹配
- 正确：检查文件头字节，根据真实格式调整扩展名
- 错误：prompt 包含中文文字要求 → SDXL 无法渲染，生成乱码
- 正确：prompt 只描述视觉画面，文字由公众号标题位承载

## 质量自检（仅平台约束）

- [ ] 封面图已就位（1240×770，与正文配图完全不同）
- [ ] GIF ≥100KB 且 ≤3MB
- [ ] 样式全部内联，无外部CSS/JS引用
- [ ] HTML总字符 ≤20000
- [ ] 图片已上传素材库并以素材URL引用
- [ ] 正文未出现 `# H1`、`:::block` 容器
- [ ] 推送命令带 `--cover` 参数

## 脚本

```
wechat/
└── scripts/
    ├── client.py            # 素材库/草稿箱客户端（上传封面、创建草稿）
    ├── converter.py         # Markdown/HTML → 公众号受限HTML（内联样式）
    ├── wechat_converter.py  # 核心转换器（MarkdownIt + _StyleInjector）
    ├── publish.py           # 推送草稿箱入口
    ├── generate_cover.py    # 调用 text_to_image API 生成封面图（含占位图检测）
    ├── content_postprocess.py  # 参考文献限量后处理
    └── style_constraints.py    # 平台约束常量
```

## 标准推送流程

```
1. 准备 Markdown 文件（带 frontmatter title）
2. 确保文章包含 Markdown 结构元素：## 小标题、> 引用、**加粗 等，否则 converter 无法注入样式
3. 生成/准备封面图（1240×770，JPEG/PNG）
   - 推荐：python scripts/generate_cover.py（调用 text_to_image API + 占位图检测）
   - 若报 CDN 占位图错误：当前 API 因 CDN 缓存返回固定图，需服务端修复
4. 执行推送：
   python publish.py output/article.md --cover output/cover.jpg --author "公众号名"
5. 检查输出：确认 cover media_id 和 draft media_id 都已返回
```

命令示例：

```
python publish.py output/article.md --cover output/cover.jpg --author "本质工坊"
```

## references

- [references.wechat-pipeline.md](references.wechat-pipeline.md) — 管线规范
- [references.wechat-formatting.md](references.wechat-formatting.md) — 排版规范

---

*微信公众号适配器 · Markdown/HTML→公众号受限HTML · 内联样式+素材库+封面图必选*
