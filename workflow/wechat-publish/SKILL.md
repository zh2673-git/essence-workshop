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

### 技术要点
1. **API格式问题**：text_to_image API默认返回JPEG格式（文件头：0xFF,0xD8,0xFF,0xE0），而非PNG（文件头：0x89,'P','N','G'）
2. **文件验证**：生成后必须检查文件头字节，确认真实格式而非扩展名
3. **尺寸要求**：公众号要求1240×770（约16:10比例），landscape_16_9（16:9）接近但略有偏差，需根据实际API输出调整

### 生成流程
```
1. 构建prompt（描述封面主题，使用抽象概念可视化）
2. 调用API：https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt={prompt}&image_size=landscape_16_9
3. 下载文件（默认保存为.png，但实际可能是JPEG）
4. 验证文件头：
   - PNG签名：137,80,78,71 (0x89,0x50,0x4E,0x47)
   - JPEG签名：255,216,255,224 (0xFF,0xD8,0xFF,0xE0)
5. 根据真实格式重命名文件扩展名
6. 检查文件大小（应>100KB）
7. 使用正确扩展名的文件作为封面图推送
```

### 常见错误
- 错误：使用Write工具写入文本到.png文件 → 产生损坏文件
- 正确：使用Invoke-WebRequest下载API响应，然后验证格式
- 错误：假设API返回PNG → 导致文件名与内容不匹配
- 正确：检查文件头字节，根据真实格式调整扩展名

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
    ├── generate_cover.py    # 生成1240×770纯文字封面图
    ├── content_postprocess.py  # 参考文献限量后处理
    └── style_constraints.py    # 平台约束常量
```

## 标准推送流程

```
1. 准备 Markdown 文件（带 frontmatter title）
2. 确保文章包含 Markdown 结构元素：## 小标题、> 引用、**加粗 等，否则 converter 无法注入样式
3. 生成/准备封面图（1240×770，JPEG/PNG）
   - 推荐：python scripts/generate_cover.py
   - 备用：text_to_image API（注意返回的是 JPEG，需按真实扩展名保存）
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
