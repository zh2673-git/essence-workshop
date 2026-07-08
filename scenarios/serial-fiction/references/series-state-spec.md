# 连载状态规范

## 文件位置

```
serial-fiction/output/{series-name}/series-state.json
```

## 数据格式

```json
{
  "series_name": "连载名称",
  "status": "ongoing",
  "current_season": 1,
  "total_seasons_planned": 3,
  "total_chapters_planned": 60,
  "created_at": "2026-06-21",
  "updated_at": "2026-06-21",
  "chapters": [
    {
      "season": 1,
      "number": 1,
      "title": "开篇",
      "status": "published",
      "word_count": 3200,
      "published_at": "2026-06-21",
      "file_path": "seasons/season-01/chapters/chapter-01.md"
    },
    {
      "season": 1,
      "number": 2,
      "title": "入局",
      "status": "draft",
      "word_count": 0,
      "published_at": null,
      "file_path": "seasons/season-01/chapters/chapter-02.md"
    }
  ]
}
```

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `series_name` | string | 连载名称 |
| `status` | string | 连载状态：`planning`/`ongoing`/`completed`/`paused` |
| `current_season` | integer | 当前季数 |
| `total_seasons_planned` | integer | 计划总季数 |
| `total_chapters_planned` | integer | 计划总章数 |
| `created_at` | string | 创建日期 |
| `updated_at` | string | 最后更新日期 |
| `chapters` | array | 章节列表 |

## 章节状态

| 状态 | 说明 |
|------|------|
| `planned` | 已规划，尚未开始写作 |
| `draft` | 已有草稿 |
| `review` | 待审核 |
| `published` | 已发布 |
| `archived` | 已归档 |

## 更新规则

1. 每次创建新章时，添加章节记录，状态为 `planned`。
2. 完成单章写作后，更新 `word_count`，状态改为 `draft`。
3. 推送发布后，更新 `published_at`，状态改为 `published`。
4. 任何时候修改连载信息，都要更新 `updated_at`。
