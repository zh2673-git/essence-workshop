"""
本质工坊 · 公众号发布管线 v2.0

一键发布：Markdown → HTML 转换 + 图片上传 + 推送草稿箱
v2.0：移除风格分流字数/配图检查，只做平台硬性约束检查。
内容风格、字数、配图由内容框架层决定。

用法:
  python publish.py article.md --cover cover.png
  python publish.py article.md --cover cover.png --author "公众号名"
  python publish.py article.md --check-only
  python publish.py article.md --no-upload-images
"""

import argparse
import json
import os
import re
from pathlib import Path

try:
    from .client import WeChatClient
    from .converter import convert_markdown, inspect_article
except ImportError:
    from client import WeChatClient
    from converter import convert_markdown, inspect_article

from style_constraints import MAX_HTML_CHARS  # noqa: E402


# ─── 文章检查 ───────────────────────────────────────────────

def check_article(file_path, json_output=False):
    """只执行平台硬性约束检查，不转换不推送。"""
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"ERROR: 文件不存在: {file_path}")
        return {"success": False, "error": f"文件不存在: {file_path}"}

    md_content = file_path.read_text(encoding="utf-8")
    md_no_frontmatter = re.sub(r'^---.*?---', '', md_content, flags=re.DOTALL).strip()

    result = {
        "success": True,
        "plain_text_count": 0,
        "image_count": 0,
        "checks": [],
    }

    # 检查 frontmatter title
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', md_content, re.DOTALL)
    title = ""
    if fm_match:
        for line in fm_match.group(1).split("\n"):
            if line.strip().lower().startswith("title:"):
                title = line.split(":", 1)[1].strip()
    if not title:
        result["checks"].append({"level": "error", "message": "frontmatter 缺少 title，推送后标题将显示为「未命名文章」"})
        result["success"] = False
    elif len(title) > 64:
        result["checks"].append({"level": "warning", "message": f"标题超长 ({len(title)}/64)"})

    # 统计纯文本字数（仅报告，不按风格约束判定）
    md_no_img = re.sub(r'!\[.*?\]\(.*?\)', '', md_no_frontmatter)
    md_no_md = re.sub(r'[#*>\-|=`~\[\](){}]', '', md_no_img)
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', md_no_md))
    english_words = len(re.findall(r'[a-zA-Z]+', md_no_md))
    plain_text_count = chinese_chars + english_words
    result["plain_text_count"] = plain_text_count

    # 统计配图数量（仅报告，不按风格约束判定）
    img_tags = re.findall(r'!\[.*?\]\(.*?\)', md_no_frontmatter)
    png_count = sum(1 for t in img_tags if '.png' in t.lower())
    gif_count = sum(1 for t in img_tags if '.gif' in t.lower())
    result["image_count"] = len(img_tags)

    # 检查平台禁止项
    if re.search(r'^:::', md_no_frontmatter, re.MULTILINE):
        result["checks"].append({"level": "error", "message": "包含 :::block 容器，微信草稿箱会剥离容器样式"})
        result["success"] = False

    if re.search(r'^#\s+', md_no_frontmatter, re.MULTILINE):
        result["checks"].append({"level": "warning", "message": "正文包含 # H1，微信中 H1 由标题栏占用"})

    if not json_output:
        print(f"纯文本: {plain_text_count} 字")
        print(f"配图: {png_count} PNG + {gif_count} GIF = {len(img_tags)} 张")
        for c in result["checks"]:
            level = c["level"].upper()
            print(f"  [{level}] {c['message']}")

    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "ALL CHECKS PASSED" if result["success"] else "SOME CHECKS FAILED"
        print(f"\n--- 检查结果: {status} ---")

    return result


# ─── 发布主函数 ─────────────────────────────────────────────

def publish(file_path, cover="", title="", author="",
            max_chars=MAX_HTML_CHARS, upload_images=True, json_output=False):
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"ERROR: 文件不存在: {file_path}")
        return {"success": False, "error": f"文件不存在: {file_path}"}

    result = convert_markdown(
        file_path=str(file_path),
        title=title,
        author=author,
    )
    if not result["success"]:
        print(f"ERROR: 转换失败: {result.get('error', 'unknown')}")
        return result

    article_title = result["title"] or title or ""
    if not article_title:
        print("ERROR: frontmatter 中 title 为空，推送后标题将显示为「未命名文章」")
        print("  请在 Markdown 文件头部添加 frontmatter:")
        print("  ---")
        print("  title: 你的文章标题")
        print("  ---")
        return {"success": False, "error": "frontmatter title 为空，推送前必须补充"}
    article_author = result["author"] or author or ""
    article_digest = result["digest"] or ""
    html = result["html"]

    plain_text = re.sub(r"<[^>]+>", "", html)
    char_count = len(plain_text)
    html_size = len(html)
    if html_size > max_chars:
        print(f"WARNING: HTML 总字符 {html_size}，超过 {max_chars} 字符上限")
        if not json_output:
            return {"success": False, "error": f"HTML 总字符 {html_size}，需 <= {max_chars} 字符",
                    "html_size": html_size, "max_chars": max_chars}

    img_replacements = []
    if upload_images:
        try:
            client = WeChatClient()
            if client.is_configured():
                img_tags = re.findall(r'<img[^>]+src="([^"]+)"', html)
                for img_src in img_tags:
                    if img_src.startswith("http") or img_src.startswith("data:"):
                        continue

                    found_path = None
                    for try_path in [img_src, str(Path(img_src)), str(file_path.parent / img_src)]:
                        p = Path(try_path)
                        if p.exists() and p.is_file():
                            found_path = str(p)
                            break

                    if not found_path:
                        print(f"  WARNING: Image not found: {img_src}")
                        continue

                    local_path = found_path
                    upload_path = local_path

                    if local_path.lower().endswith('.svg'):
                        try:
                            from scripts.elements.svg_to_png import svg_to_png
                            png_path = local_path.replace('.svg', '_upload.png')
                            svg_to_png(local_path, png_path, dpi=2)
                            upload_path = png_path
                        except Exception as svg_err:
                            print(f"  ERROR: SVG convert failed after retries: {img_src} ({svg_err})")
                            continue

                    try:
                        cdn_url = client.upload_content_image(upload_path)
                        img_replacements.append((img_src, cdn_url))
                        print(f"  Uploaded: {img_src} -> CDN")
                    except Exception as e:
                        print(f"  WARNING: Upload failed: {img_src} ({e})")

                    if upload_path != local_path:
                        try:
                            Path(upload_path).unlink(missing_ok=True)
                        except Exception:
                            pass

                for old_src, new_src in img_replacements:
                    html = html.replace(f'src="{old_src}"', f'src="{new_src}"')
                    html = html.replace(f"src='{old_src}'", f"src='{new_src}'")
        except Exception as e:
            print(f"  WARNING: Image upload error: {e}")

    draft_media_id = ""
    try:
        client = WeChatClient()
        if not client.is_configured():
            print("WARNING: WeChat credentials not configured, HTML only.")
            print("  Create ~/.config/essence-workshop/config.yaml with app_id and app_secret")
        else:
            thumb_media_id = ""
            if cover:
                print("Uploading cover...")
                upload = client.upload_image(cover, "thumb")
                thumb_media_id = upload.media_id
                print(f"  Cover media_id: {thumb_media_id}")

            print("Pushing draft to WeChat...")
            draft_result = client.create_draft(
                title=article_title[:64],
                content=html,
                thumb_media_id=thumb_media_id,
                author=article_author[:16],
                digest=article_digest[:128],
                show_cover_pic=0,
            )
            draft_media_id = draft_result.media_id
            print(f"Draft pushed! media_id: {draft_media_id}")
    except Exception as e:
        print(f"ERROR: Draft push failed: {e}")
        if json_output:
            return {"success": False, "error": str(e)}

    img_count = len(img_replacements)
    output = {
        "success": True,
        "html_length": len(html),
        "char_count": char_count,
        "images_uploaded": img_count,
        "draft_created": bool(draft_media_id),
        "draft_media_id": draft_media_id,
        "cover_used": cover or "",
        "title": article_title,
    }

    if json_output:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"\nDone! Title: {article_title}")
        print(f"  Chars: {char_count}")
        if img_count > 0:
            print(f"  Images uploaded: {img_count}")
        if draft_media_id:
            print(f"  Draft media_id: {draft_media_id}")
        if cover:
            print(f"  Cover: {cover}")
        print(f"  HTML size: {len(html)} chars")

    return output


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · 公众号发布管线")
    parser.add_argument("file", help="Markdown 文件路径")
    parser.add_argument("--cover", default="", help="封面图片路径")
    parser.add_argument("--title", default="", help="覆盖标题")
    parser.add_argument("--author", default="", help="覆盖作者")
    parser.add_argument("--max-chars", type=int, default=MAX_HTML_CHARS, help="HTML总字符上限")
    parser.add_argument("--no-upload-images", action="store_true", help="不上传正文图片")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--check-only", action="store_true", help="只执行平台检查，不转换不推送")

    args = parser.parse_args()

    if args.check_only:
        check_article(file_path=args.file, json_output=args.json)
        return

    publish(
        file_path=args.file,
        cover=args.cover,
        title=args.title,
        author=args.author,
        max_chars=args.max_chars,
        upload_images=not args.no_upload_images,
        json_output=args.json,
    )


if __name__ == "__main__":
    main()
