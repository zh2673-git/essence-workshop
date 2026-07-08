# 本质工坊内容输出层扩展方案

## 文档信息

- **版本**：1.0
- **日期**：2026-06-21
- **目标**：扩展本质工坊 `content-output` 层的内容风格体系，新增连载小说创作功能，提升公众号场景下的内容多样性与读者完读率。
- **影响范围**：`content-output/` 子系统、根目录 `SKILL.md` 场景路由表。

---

## 一、背景与问题

### 1.1 当前状态

本质工坊当前内容输出层包含三种输出风格：

| 风格 | 定位 | 默认篇幅 |
|------|------|---------|
| 论文风格 | 深度分析、五段式结构 | 7000-8000字 |
| 对话风格 | Q&A结构，播客文字版 | 不定 |
| 蒸馏Skill风格 | 复用人物Skill的表达DNA | 不定 |

公众号管线默认要求纯文本字数达到 **7000-8000字**，配图 **7张**（6 PNG + 1 GIF）。

### 1.2 核心问题

1. **风格单一**：论文风格适合建立专业信任，但不适合所有公众号读者场景。
2. **篇幅过长**：7000-8000字在碎片化阅读场景下完读率低。
3. **缺少叙事型内容**：故事、小说等强情绪钩子内容无法通过现有风格生产。
4. **缺少连载管理能力**：小说/系列内容需要世界观、人物、章节大纲、连载状态等独立资产。

### 1.3 设计原则

- **风格层与管线层解耦**：风格改写发生在管线选择之前，统一输出到元素层。
- **按内容形态分流**：不同风格对应不同的结构模板、字数目标和配图策略。
- **连载小说作为独立子系统**：因其具有多章节、世界观、人物档案、连载状态等特殊需求，不并入普通文章流程。
- **最小破坏原则**：保留现有论文风格、对话风格、蒸馏Skill风格的全部行为，仅做增量扩展。

---

## 二、风格扩展方案

### 2.1 新增风格矩阵

在保留现有三种风格的基础上，新增四种内容风格：

| 风格 | 定位 | 默认篇幅 | 核心结构 | 适用场景 |
|------|------|---------|---------|---------|
| **专栏风格** | 论文的轻量版 | 3000-5000字 | 问题→观点→案例→结论 | 常规公众号文章 |
| **故事风格** | 用叙事包装知识/案例 | 2500-4500字 | 场景→冲突→转折→收束 | 历史、商业、法律案例 |
| **教程/清单风格** | 步骤清晰、直接可用 | 1500-3000字 | 目标→步骤→注意事项→结果 | 工具、操作、方法论 |
| **观点/时评风格** | 立场鲜明、短小犀利 | 1200-2500字 | 现象→立场→论证→呼吁 | 热点、行业动态 |

### 2.2 风格与公众号管线的适配

不同风格在公众号管线中应采用不同的字数与配图标准：

| 风格 | 纯文本字数 | 配图数量 | 封面图重点 |
|------|-----------|---------|-----------|
| 论文风格 | 7000-8000字 | 7张（6 PNG + 1 GIF） | 专业、信息密度高 |
| 专栏风格 | 3000-5000字 | 5张 | 观点鲜明 |
| 故事风格 | 2500-4500字 | 5张 | 情绪、场景感 |
| 教程/清单风格 | 1500-3000字 | 4张 | 结果导向、步骤可视化 |
| 观点/时评风格 | 1200-2500字 | 3张 | 冲突、标题冲击 |
| 连载小说风格 | 2000-4000字/章 | 3-5张 | 悬念、人物/场景 |

### 2.3 风格触发词

| 风格 | 用户触发词 |
|------|-----------|
| 专栏风格 | 「写专栏」「写长文」「写分析文章」 |
| 故事风格 | 「写故事」「故事化」「用故事讲XX」 |
| 教程/清单风格 | 「写教程」「写清单」「怎么做XX」「步骤」 |
| 观点/时评风格 | 「写观点」「评论XX」「怎么看XX」 |

---

## 三、连载小说子系统方案

### 3.1 定位

连载小说作为 `content-output` 层下的独立子系统，触发词为「写连载小说」「小说连载」「连载XX」。

### 3.2 核心工作流

```
步骤0：确定小说类型
步骤1：世界观构建
步骤2：人物设定
步骤3：故事主线设计
步骤4：分季/分章大纲
步骤5：单章写作
步骤6：章节配图生成
步骤7：连载前检查
步骤8：推送到公众号草稿箱
步骤9：更新连载状态
```

### 3.3 资产结构

```
content-output/serial-fiction/output/{series-name}/
├── world-building.md           # 世界观文档
├── characters/                 # 人物档案
│   ├── protagonist.md
│   ├── antagonist.md
│   └── supporting/
├── seasons/
│   └── season-01/
│       ├── outline.md          # 季级大纲
│       └── chapters/
│           ├── chapter-01-outline.md
│           ├── chapter-01.md
│           ├── chapter-02-outline.md
│           └── chapter-02.md
├── assets/
│   ├── characters-relation.svg
│   └── covers/
│       ├── chapter-01-cover.svg
│       └── chapter-02-cover.svg
└── series-state.json           # 连载状态
```

### 3.4 单章规范

- **字数**：2000-4000字
- **开头**：直接进入场景或冲突，不先铺垫世界观
- **结尾**：必须留悬念或情绪钩子，附加「下章预告」
- **段落节奏**：一段1-3句话，适配手机屏幕
- **叙事驱动**：对话和动作优先，减少作者旁白
- **配图**：每章至少1张人物卡/场景图 + 1张章节封面

### 3.5 连载状态规范

`series-state.json` 示例：

```json
{
  "series_name": "示例连载",
  "status": "ongoing",
  "current_season": 1,
  "total_chapters_planned": 20,
  "chapters": [
    {"number": 1, "title": "开篇", "status": "published", "word_count": 3200},
    {"number": 2, "title": "入局", "status": "draft", "word_count": 0}
  ]
}
```

---

## 四、文件修改清单

### 4.1 修改现有文件

| 文件 | 修改内容 |
|------|---------|
| `content-output/SKILL.md` | 输出风格表新增专栏/故事/教程/观点四种风格；版本号升级 |
| `content-output/E-content-output.md` | 步骤2风格选项、风格选择决策树、各风格字数规划 |
| `content-output/references/writing-style-guide.md` | 新增四种风格的详细写作规范 |
| `content-output/references/pipeline-wechat.md` | 按风格分流字数目标、配图数量、封面图规则 |
| `SKILL.md` | 场景路由表新增 E2: 连载小说 |

### 4.2 新增文件

| 文件 | 用途 |
|------|------|
| `content-output/docs/style-expansion-and-serial-fiction-plan.md` | 本方案文档 |
| `content-output/serial-fiction/SKILL.md` | 子系统说明与触发条件 |
| `content-output/serial-fiction/SF-serial-fiction.md` | 完整工作流 |
| `content-output/serial-fiction/references/fiction-style-guide.md` | 小说风格规范 |
| `content-output/serial-fiction/references/world-building-guide.md` | 世界观构建方法 |
| `content-output/serial-fiction/references/character-card-template.md` | 人物卡模板 |
| `content-output/serial-fiction/references/chapter-outline-template.md` | 分章大纲模板 |
| `content-output/serial-fiction/references/series-state-spec.md` | 连载状态规范 |
| `content-output/serial-fiction/templates/world-building-template.md` | 世界观文档模板 |
| `content-output/serial-fiction/templates/character-card-template.md` | 人物卡Markdown模板 |
| `content-output/serial-fiction/templates/chapter-template.md` | 章节正文模板 |

---

## 五、实施步骤

1. 创建本方案文档。
2. 修改 `content-output/SKILL.md` 风格表。
3. 修改 `content-output/E-content-output.md` 风格选择流程。
4. 扩展 `content-output/references/writing-style-guide.md`。
5. 修改 `content-output/references/pipeline-wechat.md` 分流规则。
6. 创建 `content-output/serial-fiction/` 子系统全部文档与模板。
7. 修改根目录 `SKILL.md` 添加 E2 路由。
8. 执行质量自检：确认所有新增文件被正确引用，风格表与规范一致。

---

## 六、验收标准

- [ ] `content-output/SKILL.md` 中输出风格表包含7种风格。
- [ ] `E-content-output.md` 风格选择决策树覆盖新增风格。
- [ ] `writing-style-guide.md` 中新增四种风格的结构、语气、禁用表达、字数目标完整。
- [ ] `pipeline-wechat.md` 按风格分流字数与配图数量。
- [ ] `serial-fiction/` 子系统文档完整，包含工作流、规范、模板。
- [ ] 根目录 `SKILL.md` 场景路由表包含 E2: 连载小说。
- [ ] 所有新增文档中的文件引用路径正确。
