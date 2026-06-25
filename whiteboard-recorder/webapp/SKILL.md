---
name: 白板录制
description: 无限画布白板讲解录制系统，AI自动根据内容生成Excalidraw手绘白板图解和提词器脚本，一键启动服务打开浏览器，直接点击录制即可
version: 2.0
scene: E3
pipeline: whiteboard
---

# 白板录制 · Skill（自包含完整版本）

## 核心能力
**一键流程**：提供内容（Markdown文件 / 公众号URL / 网页链接）→ 自动调用AI生成无限画布白板+口语化提词器脚本 → 自动启动前端服务 → 自动打开浏览器加载内容 → 你只需要点击录制按钮即可开始讲解录制。

完全自包含：所有运行代码（前端Web应用+Python生成脚本）都在本skill目录内，不依赖任何外部项目，clone到本地就能用。

## 触发条件

- 「白板录制」「录白板」「白板讲解」「做白板视频」
- 「白板演示」「录制讲解视频」「录课白板」
- 「自动生成白板」「AI画白板」
- 「把这篇文章做成白板视频」「给这个md录个白板讲解」

## 目录结构

```
whiteboard-recorder/
├── SKILL.md                    # 本文件
├── references/
│   ├── excalidraw-element-spec.md
│   └── ai-prompt-guide.md
├── scripts/
│   └── whiteboard_generator.py # 主入口脚本：生成+自动启动服务+打开浏览器
└── webapp/                     # WhiteboardCaster完整前端应用（自包含）
    ├── package.json
    ├── src/
    ├── public/                 # 生成的白板JSON自动输出到这里
    └── ...
```

## 执行流程（自动完成，无需手动操作）

当用户触发白板录制并提供内容后，按以下流程执行：

1. **内容获取**
   - 如果输入是URL：自动抓取公众号/网页正文和标题
   - 如果输入是本地文件：读取Markdown内容
   - 如果是纯文本：直接使用

2. **AI自动生成**
   - 调用LLM深度理解内容语义
   - **无模板限制**：AI自由选择最合适的图示形式（流程图/思维导图/对比图/因果链路/时间线...）
   - 为每个讲解场景生成：手绘Excalidraw元素、小标题、口语化提词脚本、预计时长
   - 自动计算画布坐标，所有场景横向排列在同一个无限画布

3. **自动准备环境**
   - 检查Python依赖，自动安装openai/requests/beautifulsoup4
   - 检查前端npm依赖，首次运行自动npm install
   - 将生成的白板项目输出到 `webapp/public/generated-project.json`

4. **自动启动+打开**
   - 自动执行 `npm run dev` 启动前端开发服务器（端口5173）
   - 等待服务就绪后，自动打开浏览器访问 `http://localhost:5173/?autoload=true`
   - 前端自动加载生成好的白板项目，镜头自动定位到第一个场景，提词器自动加载第一页台词

5. **用户操作（只需要这几步）**
   - 浏览器弹出摄像头/麦克风权限请求时点击允许（如果需要人像录制）
   - 用 `→` 方向键或空格键切换场景，镜头会平滑自动跟随移动到对应区域
   - 用 `←` 返回上一页，`Home`回到开头，`End`跳到最后
   - 点击红色录制按钮，3秒倒计时后开始录制
   - 边看提词器边讲解，讲完一页按空格切下一页，镜头自动跟上
   - 点击停止按钮，录制完成后自动弹出预览，可下载MP4

## 使用方式（手动调用也可以）

在skill根目录下执行：

```bash
# 使用Markdown文件生成
python scripts/whiteboard_generator.py ./my-article.md

# 使用网页URL生成（支持公众号文章）
python scripts/whiteboard_generator.py https://mp.weixin.qq.com/s/xxxxx

# 指定API Key和模型
python scripts/whiteboard_generator.py ./content.md --api-key sk-xxx --model doubao-4

# 只生成不自动启动服务
python scripts/whiteboard_generator.py ./content.md --no-auto-start
```

也可以设置环境变量 `OPENAI_API_KEY` 或 `DOUBAO_API_KEY`，就不需要每次传--api-key。

## 无限画布+镜头跟随特性

- ✅ 所有内容在**同一个无限大Excalidraw画布**上按讲解顺序横向排列，场景间留空白
- ✅ 切换场景时**镜头800ms平滑缓动动画**移动到目标区域，体验流畅
- ✅ 可以随时手动拖动/缩放白板自由浏览上下文，不影响录制
- ✅ AI可以画跨场景箭头表示逻辑关联，因为所有元素都在同一个画布
- ✅ 左侧显示场景导航缩略图，点击直接跳转
- ✅ 提词器面板自动跟随场景切换显示对应台词

## 前端功能（webapp完整包含）

- Excalidraw无限画布手绘编辑，生成后你也可以手动修改调整
- 场景导航栏 + 键盘快捷键控制
- 半透明提词器面板，可调整位置和字体大小
- 摄像头人像叠加：可拖拽位置、调整大小、镜像、圆角
- 光标特效：高亮鼠标位置，点击有波纹效果
- 多分辨率选择（1080p/2K/4K）
- 录制倒计时
- 视频预览和下载

## 参考文档

- [references/excalidraw-element-spec.md](references/excalidraw-element-spec.md) — Excalidraw元素规格
- [references/ai-prompt-guide.md](references/ai-prompt-guide.md) — AI Prompt设计参考
