"""
连载小说自动续章辅助脚本。

功能：
1. 读取 series-state.json，定位下一个待写章节；
2. 强制读取世界观、人物卡、季大纲、上一章正文、本章大纲；
3. 输出一份结构化的创作上下文，供 Agent 使用；
4. 提供自检清单，帮助 Agent 在生成后验证一致性。

用法（从 content-output 目录执行）：
    python -m scripts.serial-fiction.write_chapter 铁纪 --next
    python -m scripts.serial-fiction.write_chapter 铁纪 --chapter 2
"""

import argparse
import json
import re
import sys
from pathlib import Path


def _series_dir(series_name):
    return Path("serial-fiction/output") / series_name


def _load_text(path):
    if not path.exists():
        return f"[文件不存在: {path}]"
    return path.read_text(encoding="utf-8")


def _load_state(series_name):
    state_path = _series_dir(series_name) / "series-state.json"
    if not state_path.exists():
        print(f"ERROR: 连载状态文件不存在: {state_path}")
        sys.exit(1)
    return json.loads(state_path.read_text(encoding="utf-8"))


def _find_next_chapter(state):
    for ch in state.get("chapters", []):
        if ch.get("status") in ("planned", "draft"):
            return ch
    return None


def _get_chapter(state, number):
    for ch in state.get("chapters", []):
        if ch.get("number") == number:
            return ch
    return None


def _prev_chapter(state, number):
    return _get_chapter(state, number - 1)


def _read_assets(series_name):
    base = _series_dir(series_name)
    assets = {
        "world": base / "world-building.md",
        "season_outline": base / "seasons/season-01/outline.md",
        "characters": list((base / "characters").glob("*.md")) if (base / "characters").exists() else [],
    }
    return assets


def _chapter_paths(series_name, chapter):
    base = _series_dir(series_name)
    season = chapter.get("season", 1)
    number = chapter["number"]
    return {
        "outline": base / f"seasons/season-{season:02d}/chapters/chapter-{number:02d}-outline.md",
        "draft": base / f"seasons/season-{season:02d}/chapters/chapter-{number:02d}.md",
    }


def _collect_context(series_name, chapter, state):
    assets = _read_assets(series_name)
    paths = _chapter_paths(series_name, chapter)
    prev = _prev_chapter(state, chapter["number"])

    ctx = {
        "series_name": series_name,
        "chapter": chapter,
        "prev_chapter": prev,
        "world": _load_text(assets["world"]),
        "season_outline": _load_text(assets["season_outline"]),
        "characters": {p.stem: _load_text(p) for p in assets["characters"]},
        "this_outline": _load_text(paths["outline"]),
    }

    if prev:
        prev_paths = _chapter_paths(series_name, prev)
        ctx["prev_chapter_text"] = _load_text(prev_paths["draft"])
        ctx["prev_outline"] = _load_text(prev_paths["outline"])
    else:
        ctx["prev_chapter_text"] = "[本章为系列首章，无前序章节]"
        ctx["prev_outline"] = ""

    return ctx, paths


def _build_prompt(ctx):
    lines = []
    ch = ctx["chapter"]
    prev = ctx["prev_chapter"]

    lines.append("# 连载小说续章创作上下文")
    lines.append("")
    lines.append(f"## 当前任务")
    lines.append(f"- 系列：{ctx['series_name']}")
    lines.append(f"- 章节：第{ch['number']}章：{ch['title']}")
    lines.append("")

    if prev:
        lines.append(f"## 上一章状态")
        lines.append(f"- 第{prev['number']}章：{prev['title']}")
        lines.append(f"- 状态：{prev.get('status', 'unknown')}")
        lines.append(f"- 字数：{prev.get('word_count', 0)}")
        lines.append("")
        lines.append("### 上一章正文结尾")
        text = ctx["prev_chapter_text"]
        # 取最后 1200 字作为衔接上下文
        tail = text[-1200:] if len(text) > 1200 else text
        lines.append(tail)
        lines.append("")

    lines.append("## 本章大纲")
    lines.append(ctx["this_outline"])
    lines.append("")

    lines.append("## 世界观文档")
    lines.append(ctx["world"])
    lines.append("")

    lines.append("## 人物卡")
    for name, content in ctx["characters"].items():
        lines.append(f"### {name}")
        lines.append(content)
        lines.append("")

    lines.append("## 季级大纲")
    lines.append(ctx["season_outline"])
    lines.append("")

    lines.append("## 创作纪律")
    lines.append("1. 严格依据本章大纲，完成本章正文创作。")
    lines.append("2. 承接上一章结尾状态，保持时间线、人物关系、情绪基调一致。")
    lines.append("3. 人物言行必须符合人物卡中的性格、口头禅、紧张反应。")
    lines.append("4. 结尾必须抛出一个钩子，引导下一章。")
    lines.append("5. 字数控制在 2000-4000 字。")
    lines.append("6. 生成后执行质量自检清单。")
    lines.append("")

    lines.append("## 质量自检清单")
    lines.append("- [ ] 字数在 2000-4000 之间")
    lines.append("- [ ] 人物言行与人物卡一致")
    lines.append("- [ ] 上一章的悬念得到承接")
    lines.append("- [ ] 本章结尾有明确钩子")
    lines.append("- [ ] 纪检监察程序描写符合现实逻辑")
    lines.append("- [ ] 配图需求已在大纲中规划")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="连载小说续章辅助脚本")
    parser.add_argument("series", help="系列名称，如：铁纪")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--next", action="store_true", help="定位下一个待写章节")
    group.add_argument("--chapter", type=int, help="指定章节号")
    args = parser.parse_args()

    state = _load_state(args.series)

    if args.next:
        chapter = _find_next_chapter(state)
        if chapter is None:
            print("没有待写的章节，连载可能已完结。")
            sys.exit(0)
    else:
        chapter = _get_chapter(state, args.chapter)
        if chapter is None:
            print(f"ERROR: 找不到第 {args.chapter} 章")
            sys.exit(1)

    ctx, paths = _collect_context(args.series, chapter, state)
    prompt = _build_prompt(ctx)

    print(prompt)
    print("")
    print("---")
    print(f"提示词已生成。目标文件：{paths['draft']}")
    print(f"完成后请运行：python -m scripts.pipelines.wechat.publish {paths['draft']} --check-only")


if __name__ == "__main__":
    main()
