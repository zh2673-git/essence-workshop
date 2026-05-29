"""
本质工坊 · 公众号文章转视频
从公众号文章（URL抓取或API拉取）自动生成视频号短视频

完整链路：
  文章正文 → 拆分为镜头(slides.json) → TTS旁白 → Canvas录制 → FFmpeg合并 → MP4

文章获取方式：
  1. URL方式（默认推荐）：提供公众号文章链接，抓取正文
     - 适用于任何公众号的已发布文章，无权限要求
  2. API方式（受权限制约）：通过media_id拉取
     - 需认证服务号才能使用 freepublish 接口
     - 订阅号/未认证服务号只能看到API上传的素材
  3. 本地文件：直接提供Markdown文件路径

用法:
  python article_to_video.py --url https://mp.weixin.qq.com/s/xxx      从URL抓取文章并生成视频（推荐）
  python article_to_video.py --article output/article.md               从本地Markdown生成视频
  python article_to_video.py --media-id XXXXX                          从公众号拉取文章并生成视频（需API权限）
  python article_to_video.py --url https://mp.weixin.qq.com/s/xxx --voice zh-CN-YunxiNeural
  python article_to_video.py --url https://mp.weixin.qq.com/s/xxx --save-article output/article.md
"""

import argparse
import json
import os
import re
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def split_into_slides(markdown, title=""):
    slides = []
    lines = markdown.split("\n")
    current_section = {"heading": "", "content": []}

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        h_match = re.match(r'^(#{1,4})\s+(.+)', stripped)
        if h_match:
            if current_section["heading"] or current_section["content"]:
                slides.append(current_section)
            current_section = {"heading": h_match.group(2).strip(), "content": []}
        elif stripped.startswith("> "):
            current_section["content"].append(("quote", stripped[2:].strip()))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            current_section["content"].append(("bullet", stripped[2:].strip()))
        elif re.match(r'^\d+[.、)]\s*', stripped):
            text = re.sub(r'^\d+[.、)]\s*', '', stripped)
            current_section["content"].append(("step", text.strip()))
        elif stripped == "---":
            if current_section["heading"] or current_section["content"]:
                slides.append(current_section)
            current_section = {"heading": "", "content": []}
        else:
            current_section["content"].append(("text", stripped))

    if current_section["heading"] or current_section["content"]:
        slides.append(current_section)

    return slides


def classify_slide_type(section):
    content = section["content"]
    has_bullets = any(c[0] == "bullet" for c in content)
    has_steps = any(c[0] == "step" for c in content)
    has_quotes = any(c[0] == "quote" for c in content)

    if has_steps and not has_bullets:
        return "steps"
    if has_bullets:
        return "bullet"
    if has_quotes and len(content) <= 2:
        return "quote"
    if len(content) == 0 and section["heading"]:
        return "title"
    return "bullet"


def detect_visual_style(sections):
    text = "\n".join(
        s["heading"] + " " + " ".join(c[1] for c in s["content"])
        for s in sections
    )

    tech_keywords = ["AI", "编程", "代码", "算法", "技术", "Agent", "API", "模型",
                     "训练", "推理", "部署", "架构", "框架", "开源", "GPT", "LLM",
                     "深度学习", "机器学习", "神经网络", "transformer"]
    edu_keywords = ["教育", "学习", "成长", "阅读", "写作", "学校", "课程",
                    "方法", "练习", "习惯", "知识", "技能", "提升", "入门"]
    compare_keywords = ["对比", "vs", "差异", "优劣", "选择", "比较", "区别",
                        "哪个", "更好", "替代", "竞品", "优劣", "分析"]
    philosophy_keywords = ["哲学", "思考", "本质", "意义", "价值", "人生",
                          "存在", "意识", "自由", "真理", "智慧", "境界"]

    scores = {
        "tech": sum(text.count(k) for k in tech_keywords),
        "edu": sum(text.count(k) for k in edu_keywords),
        "compare": sum(text.count(k) for k in compare_keywords),
        "philosophy": sum(text.count(k) for k in philosophy_keywords),
    }

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "tech"

    return best


def generate_timeline(slide):
    dur = slide.get("duration", 10)
    elements = []
    stype = slide.get("type", "bullet")

    if stype == "title":
        elements.append({"id": "bg", "enter_at": 0, "exit_at": dur, "easing": "none"})
        elements.append({"id": "icon", "enter_at": 0.2, "exit_at": dur - 0.5, "easing": "expoOut"})
        elements.append({"id": "title", "enter_at": 0.4, "exit_at": dur - 0.5, "easing": "expoOut"})
        elements.append({"id": "accent", "enter_at": 0.7, "exit_at": dur - 0.5, "easing": "expoOut"})
        if slide.get("subtitle"):
            elements.append({"id": "subtitle", "enter_at": 0.9, "exit_at": dur - 0.5, "easing": "expoOut"})
    elif stype == "bullet":
        elements.append({"id": "bg", "enter_at": 0, "exit_at": dur, "easing": "none"})
        elements.append({"id": "heading", "enter_at": 0.1, "exit_at": dur - 0.5, "easing": "expoOut"})
        elements.append({"id": "accent", "enter_at": 0.3, "exit_at": dur - 0.5, "easing": "expoOut"})
        for i, _ in enumerate(slide.get("items", [])):
            elements.append({"id": f"item_{i}", "enter_at": 0.4 + i * 0.25, "exit_at": dur - 0.5, "easing": "easeOutBack"})
    elif stype == "quote":
        elements.append({"id": "bg", "enter_at": 0, "exit_at": dur, "easing": "none"})
        elements.append({"id": "openQuote", "enter_at": 0.2, "exit_at": dur - 0.5, "easing": "expoOut"})
        elements.append({"id": "card", "enter_at": 0.3, "exit_at": dur - 0.5, "easing": "expoOut"})
        elements.append({"id": "text", "enter_at": 0.6, "exit_at": dur - 0.5, "easing": "expoOut"})
        if slide.get("source"):
            elements.append({"id": "source", "enter_at": 0.9, "exit_at": dur - 0.5, "easing": "expoOut"})
    elif stype == "compare":
        elements.append({"id": "bg", "enter_at": 0, "exit_at": dur, "easing": "none"})
        elements.append({"id": "heading", "enter_at": 0.1, "exit_at": dur - 0.5, "easing": "expoOut"})
        elements.append({"id": "accent", "enter_at": 0.3, "exit_at": dur - 0.5, "easing": "expoOut"})
        elements.append({"id": "leftCol", "enter_at": 0.4, "exit_at": dur - 0.5, "easing": "expoOut"})
        elements.append({"id": "rightCol", "enter_at": 0.5, "exit_at": dur - 0.5, "easing": "expoOut"})
        left_items = slide.get("left", [])
        right_items = slide.get("right", [])
        max_items = max(len(left_items), len(right_items))
        for i in range(max_items):
            if i < len(left_items):
                elements.append({"id": f"left_{i}", "enter_at": 0.6 + i * 0.12, "exit_at": dur - 0.5, "easing": "easeOut"})
            if i < len(right_items):
                elements.append({"id": f"right_{i}", "enter_at": 0.6 + i * 0.12, "exit_at": dur - 0.5, "easing": "easeOut"})
    elif stype == "steps":
        elements.append({"id": "bg", "enter_at": 0, "exit_at": dur, "easing": "none"})
        elements.append({"id": "heading", "enter_at": 0.1, "exit_at": dur - 0.5, "easing": "expoOut"})
        elements.append({"id": "accent", "enter_at": 0.3, "exit_at": dur - 0.5, "easing": "expoOut"})
        for i, _ in enumerate(slide.get("steps", [])):
            elements.append({"id": f"step_{i}", "enter_at": 0.4 + i * 0.3, "exit_at": dur - 0.5, "easing": "easeOutBack"})
    elif stype == "summary":
        elements.append({"id": "bg", "enter_at": 0, "exit_at": dur, "easing": "none"})
        elements.append({"id": "icon", "enter_at": 0.1, "exit_at": dur - 0.5, "easing": "expoOut"})
        elements.append({"id": "heading", "enter_at": 0.2, "exit_at": dur - 0.5, "easing": "expoOut"})
        elements.append({"id": "accent", "enter_at": 0.4, "exit_at": dur - 0.5, "easing": "expoOut"})
        for i, _ in enumerate(slide.get("items", [])):
            elements.append({"id": f"item_{i}", "enter_at": 0.5 + i * 0.15, "exit_at": dur - 0.5, "easing": "easeOut"})
    else:
        elements.append({"id": "bg", "enter_at": 0, "exit_at": dur, "easing": "none"})
        elements.append({"id": "heading", "enter_at": 0.1, "exit_at": dur - 0.5, "easing": "expoOut"})

    return {"duration": dur, "elements": elements}


def slides_to_json(sections, article_title=""):
    slides = []

    if article_title:
        title_slide = {
            "type": "title",
            "title": article_title,
            "subtitle": "",
            "duration": 6,
            "narration": article_title,
        }
        title_slide["timeline"] = generate_timeline(title_slide)
        slides.append(title_slide)

    for section in sections:
        slide_type = classify_slide_type(section)
        heading = section["heading"]
        content = section["content"]

        if slide_type == "title":
            slide = {
                "type": "title",
                "title": heading,
                "subtitle": "",
                "duration": 5,
                "narration": heading,
            }
            slide["timeline"] = generate_timeline(slide)
            slides.append(slide)

        elif slide_type == "quote":
            quote_text = " ".join(c[1] for c in content if c[0] == "quote")
            slide = {
                "type": "quote",
                "text": quote_text,
                "source": heading,
                "duration": 6,
                "narration": quote_text,
            }
            slide["timeline"] = generate_timeline(slide)
            slides.append(slide)

        elif slide_type == "steps":
            steps = []
            for c in content:
                if c[0] == "step":
                    steps.append({"title": c[1][:20], "desc": c[1]})
                elif c[0] == "text" and len(steps) > 0:
                    steps[-1]["desc"] += " " + c[1]
            if steps:
                narration = "，".join(s["desc"] for s in steps)
                slide = {
                    "type": "steps",
                    "title": heading or "步骤",
                    "steps": steps[:5],
                    "duration": max(8, len(steps) * 4),
                    "narration": narration,
                }
                slide["timeline"] = generate_timeline(slide)
                slides.append(slide)

        elif slide_type == "bullet":
            items = []
            for c in content:
                if c[0] == "bullet":
                    items.append(c[1][:60])
                elif c[0] == "text" and items:
                    items[-1] += c[1][:20]
                elif c[0] == "quote":
                    items.append(c[1][:60])

            if items:
                narration = "，".join(items)
                slide = {
                    "type": "bullet",
                    "title": heading or "要点",
                    "items": items[:5],
                    "duration": max(8, len(items) * 4),
                    "narration": narration,
                }
                slide["timeline"] = generate_timeline(slide)
                slides.append(slide)

    if len(slides) > 1:
        summary_items = []
        for s in slides[1:]:
            if s["type"] == "title" and s.get("title"):
                summary_items.append(s["title"])
            elif s["type"] == "bullet" and s.get("title"):
                summary_items.append(s["title"])
            elif s["type"] == "quote" and s.get("text"):
                summary_items.append(s["text"][:30])

        if summary_items:
            summary_slide = {
                "type": "summary",
                "title": "总结",
                "items": summary_items[:4],
                "duration": 10,
                "narration": "总结一下。" + "，".join(summary_items[:4]),
            }
            summary_slide["timeline"] = generate_timeline(summary_slide)
            slides.append(summary_slide)

    return {"slides": slides}


def fetch_article_by_media_id(media_id):
    from article_fetcher import get_article_content, html_to_markdown

    articles = get_article_content(media_id)
    if not articles:
        print("ERROR: Article not found.")
        return None

    a = articles[0]
    markdown = html_to_markdown(a.get("content", ""))
    return {
        "title": a.get("title", ""),
        "author": a.get("author", ""),
        "markdown": markdown,
        "url": a.get("url", ""),
    }


def fetch_article_by_url(url):
    from article_fetcher import fetch_article_by_url as fetch_url

    article = fetch_url(url)
    if not article:
        return None

    return {
        "title": article.get("title", ""),
        "author": article.get("author", ""),
        "markdown": article.get("content_markdown", ""),
        "url": url,
    }


def load_article_from_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    title = ""
    title_match = re.match(r'^#\s+(.+)', content)
    if title_match:
        title = title_match.group(1).strip()

    return {
        "title": title,
        "author": "",
        "markdown": content,
        "url": "",
    }


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · 公众号文章转视频")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", type=str, help="公众号文章URL（推荐，无权限要求）")
    group.add_argument("--article", type=str, help="本地Markdown文章路径")
    group.add_argument("--media-id", type=str, help="公众号文章media_id（需API权限，认证服务号）")

    parser.add_argument("--output", "-o", default="output/video/", help="视频输出目录")
    parser.add_argument("--voice", "-v", default="zh-CN-YunxiNeural",
                        choices=["zh-CN-YunxiNeural", "zh-CN-XiaoxiaoNeural", "zh-CN-YunjianNeural"],
                        help="TTS语音")
    parser.add_argument("--rate", "-r", default="+0%", help="TTS语速")
    parser.add_argument("--width", default=1080, type=int, help="视频宽度")
    parser.add_argument("--height", default=1920, type=int, help="视频高度")
    parser.add_argument("--compress", action="store_true", help="压缩视频至50MB")
    parser.add_argument("--save-article", type=str, default="", help="同时保存文章为Markdown")
    parser.add_argument("--save-slides", action="store_true", help="保存slides.json到输出目录")
    parser.add_argument("--template", "-t", default=None, help="自定义HTML模板路径")
    parser.add_argument("--style", default="dark", choices=["dark", "warm", "minimal", "nature"],
                        help="视觉风格: dark(深色), warm(暖色), minimal(极简), nature(自然)")
    parser.add_argument("--visual-style", default="auto", choices=["auto", "tech", "edu", "compare", "philosophy"],
                        dest="visual_style",
                        help="Cinematic视觉语言: auto(自动推断), tech, edu, compare, philosophy")
    parser.add_argument("--bgm", default=None,
                        help="背景音乐文件路径(MP3/WAV)，旁白时自动降低音量")
    parser.add_argument("--sfx-dir", default=None, dest="sfx_dir",
                        help="SFX音效目录(包含whoosh.mp3, sparkle.mp3等)")
    parser.add_argument("--format", default="mp4", choices=["mp4", "mp4_60fps", "gif"],
                        help="输出格式: mp4(25fps), mp4_60fps(60帧), gif")

    args = parser.parse_args()

    print("[1/3] Fetching article...")
    if args.url:
        article = fetch_article_by_url(args.url)
    elif args.article:
        article = load_article_from_file(args.article)
    elif args.media_id:
        article = fetch_article_by_media_id(args.media_id)
    else:
        print("ERROR: No article source specified.")
        sys.exit(1)

    if not article or not article["markdown"]:
        print("ERROR: Could not fetch article content.")
        sys.exit(1)

    print(f"  Title: {article['title']}")
    print(f"  Content length: {len(article['markdown'])} chars")

    if args.save_article:
        from article_fetcher import save_article
        save_article({
            "title": article["title"],
            "author": article["author"],
            "content_markdown": article["markdown"],
            "url": article.get("url", ""),
        }, args.save_article)

    print("\n[2/3] Splitting article into slides...")
    sections = split_into_slides(article["markdown"], article["title"])
    slides_data = slides_to_json(sections, article["title"])

    num_slides = len(slides_data["slides"])
    total_duration = sum(s["duration"] for s in slides_data["slides"])
    print(f"  Generated {num_slides} slides, estimated {total_duration}s")

    if num_slides < 3:
        print("WARNING: Too few slides generated. The article may not be suitable for video.")
    if num_slides > 20:
        print("WARNING: Too many slides. Consider condensing the content.")

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(args.output, timestamp)
    os.makedirs(output_dir, exist_ok=True)

    slides_path = os.path.join(output_dir, "slides.json")
    with open(slides_path, "w", encoding="utf-8") as f:
        json.dump(slides_data, f, ensure_ascii=False, indent=2)
    print(f"  Slides saved: {slides_path}")

    print("\n[3/3] Generating video...")
    from video_pipeline import generate_video

    visual_style = args.visual_style
    if visual_style == "auto":
        visual_style = detect_visual_style(sections)
        print(f"  [VISUAL] Auto-detected visual style: {visual_style}")

    final_path = generate_video(
        slides_path=slides_path,
        output_dir=args.output,
        template_html=args.template,
        voice=args.voice,
        rate=args.rate,
        width=args.width,
        height=args.height,
        compress=args.compress,
        style=args.style,
        bgm=args.bgm,
        fmt=args.format,
        visual_style=visual_style,
        sfx_dir=args.sfx_dir,
    )

    print(f"\n[DONE] Article → Video complete!")
    print(f"  Article: {article['title']}")
    print(f"  Video: {final_path}")

    return final_path


if __name__ == "__main__":
    main()
