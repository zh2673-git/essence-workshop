"""
本质工坊 · 公众号文章转视频
从公众号文章（API拉取或URL抓取）自动生成视频号短视频

完整链路：
  文章正文 → 拆分为镜头(slides.json) → TTS旁白 → Canvas录制 → FFmpeg合并 → MP4

用法:
  python article_to_video.py --media-id XXXXX                          从公众号拉取文章并生成视频
  python article_to_video.py --url https://mp.weixin.qq.com/s/xxx      从URL抓取文章并生成视频
  python article_to_video.py --article output/article.md               从本地Markdown生成视频
  python article_to_video.py --media-id XXXXX --voice zh-CN-YunxiNeural
  python article_to_video.py --media-id XXXXX --save-article output/article.md  同时保存文章
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


def slides_to_json(sections, article_title=""):
    slides = []

    if article_title:
        slides.append({
            "type": "title",
            "title": article_title,
            "subtitle": "",
            "duration": 6,
            "narration": article_title,
        })

    for section in sections:
        slide_type = classify_slide_type(section)
        heading = section["heading"]
        content = section["content"]

        if slide_type == "title":
            slides.append({
                "type": "title",
                "title": heading,
                "subtitle": "",
                "duration": 5,
                "narration": heading,
            })

        elif slide_type == "quote":
            quote_text = " ".join(c[1] for c in content if c[0] == "quote")
            slides.append({
                "type": "quote",
                "text": quote_text,
                "source": heading,
                "duration": 6,
                "narration": quote_text,
            })

        elif slide_type == "steps":
            steps = []
            for c in content:
                if c[0] == "step":
                    steps.append({"title": c[1][:20], "desc": c[1]})
                elif c[0] == "text" and len(steps) > 0:
                    steps[-1]["desc"] += " " + c[1]
            if steps:
                narration = "，".join(s["desc"] for s in steps)
                slides.append({
                    "type": "steps",
                    "title": heading or "步骤",
                    "steps": steps[:5],
                    "duration": max(8, len(steps) * 4),
                    "narration": narration,
                })

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
                slides.append({
                    "type": "bullet",
                    "title": heading or "要点",
                    "items": items[:5],
                    "duration": max(8, len(items) * 4),
                    "narration": narration,
                })

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
            slides.append({
                "type": "summary",
                "title": "总结",
                "items": summary_items[:4],
                "duration": 10,
                "narration": "总结一下。" + "，".join(summary_items[:4]),
            })

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
    group.add_argument("--media-id", type=str, help="公众号文章media_id（API拉取）")
    group.add_argument("--url", type=str, help="公众号文章URL（链接抓取）")
    group.add_argument("--article", type=str, help="本地Markdown文章路径")

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

    args = parser.parse_args()

    print("[1/3] Fetching article...")
    if args.media_id:
        article = fetch_article_by_media_id(args.media_id)
    elif args.url:
        article = fetch_article_by_url(args.url)
    elif args.article:
        article = load_article_from_file(args.article)
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

    final_path = generate_video(
        slides_path=slides_path,
        output_dir=args.output,
        template_html=args.template,
        voice=args.voice,
        rate=args.rate,
        width=args.width,
        height=args.height,
        compress=args.compress,
    )

    print(f"\n[DONE] Article → Video complete!")
    print(f"  Article: {article['title']}")
    print(f"  Video: {final_path}")

    return final_path


if __name__ == "__main__":
    main()
