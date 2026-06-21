"""
本质工坊 · 公众号发布管线
一键发布：Markdown → HTML 转换 + 封面生成 + 图片上传 + 推送草稿箱

封面策略：由大模型生成 SVG，再用 svg_to_png 转 PNG。
  如果元素层已有封面 SVG（output/elements/cover.svg），直接使用。
  否则返回 None，由调用方（大模型）负责生成封面 SVG。

用法:
  python wechat_publish.py article.md
  python wechat_publish.py article.md --auto-cover
  python wechat_publish.py article.md --cover cover.png
  python wechat_publish.py article.md --no-upload-images
"""

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

try:
    from .client import WeChatClient
    from .converter import convert_markdown, inspect_article
except ImportError:
    from client import WeChatClient
    from converter import convert_markdown, inspect_article


# ─── 风格约束配置 ───────────────────────────────────────────
# 与 content-output/references/pipeline-wechat.md 保持一致
# frontmatter 中 style 字段使用英文 key，如 style: column

STYLE_CONSTRAINTS = {
    "paper":        {"words": (7000, 8000), "images": 7, "png": 6, "gif": 1, "display": "论文风格"},
    "column":       {"words": (3000, 5000), "images": 5, "png": 4, "gif": 1, "display": "专栏风格"},
    "story":        {"words": (2500, 4500), "images": 5, "png": 4, "gif": 1, "display": "故事风格"},
    "tutorial":     {"words": (1500, 3000), "images": 4, "png": 3, "gif": 1, "display": "教程/清单风格"},
    "opinion":      {"words": (1200, 2500), "images": 3, "png": 2, "gif": 1, "display": "观点/时评风格"},
    "serial-fiction": {"words": (2000, 4000), "images": 5, "png": 4, "gif": 1, "display": "连载小说风格"},
    "dialogue":     {"words": (0, 20000), "images": 0, "png": 0, "gif": 0, "display": "对话风格"},
    "distillation": {"words": (0, 20000), "images": 0, "png": 0, "gif": 0, "display": "蒸馏Skill风格"},
}

DEFAULT_STYLE = "paper"


def _detect_style(md_content):
    """从 frontmatter 解析 style 字段，未指定则返回默认风格。"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', md_content, re.DOTALL)
    if not match:
        return DEFAULT_STYLE
    for line in match.group(1).split("\n"):
        if line.lower().startswith("style:"):
            style = line.split(":", 1)[1].strip().lower()
            if style in STYLE_CONSTRAINTS:
                return style
            # 兼容中文风格名（如"故事风格"→"story"）
            mapping = {
                "论文风格": "paper",
                "专栏风格": "column",
                "故事风格": "story",
                "教程风格": "tutorial",
                "清单风格": "tutorial",
                "教程/清单风格": "tutorial",
                "观点风格": "opinion",
                "时评风格": "opinion",
                "观点/时评风格": "opinion",
                "对话风格": "dialogue",
                "蒸馏skill风格": "distillation",
                "连载小说风格": "serial-fiction",
                "连载小说": "serial-fiction",
            }
            if style in mapping:
                return mapping[style]
    return DEFAULT_STYLE


def _get_style_constraint(style):
    """获取风格约束，未知风格使用默认值。"""
    return STYLE_CONSTRAINTS.get(style, STYLE_CONSTRAINTS[DEFAULT_STYLE])


# ─── 封面生成 ───────────────────────────────────────────────
# 封面由大模型生成 SVG，本函数负责查找已有 SVG 并转为 PNG

def generate_cover_png(title, subtitle="", author="", output_path="", elements_dir=""):
    """查找元素层封面SVG并转为PNG，或返回None由大模型生成。

    查找顺序：
    1. elements_dir/cover.svg（元素层已有封面）
    2. output/elements/cover.svg（默认元素目录）
    找到则用 svg_to_png 转 PNG，否则返回 None。
    """
    # 查找封面 SVG
    cover_svg = None
    search_paths = []
    if elements_dir:
        search_paths.append(os.path.join(elements_dir, "cover.svg"))
    search_paths.append(os.path.join(os.path.dirname(output_path) if output_path else "", "cover.svg"))
    search_paths.append(os.path.join(os.getcwd(), "output", "elements", "cover.svg"))

    for path in search_paths:
        if os.path.isfile(path):
            cover_svg = path
            break

    if not cover_svg:
        return None

    # SVG → PNG
    if not output_path:
        output_dir = Path.cwd() / "output" / "images"
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_title = "".join(ch for ch in title[:20] if ch.isalnum() or ch in " _-") or "cover"
        output_path = str(output_dir / f"cover_{safe_title}.png")

    try:
        from scripts.elements.svg_to_png import svg_to_png
        svg_to_png(cover_svg, output_path, dpi=2)
        return output_path
    except Exception as e:
        print(f"  WARNING: Cover SVG→PNG failed: {e}")
        return None


# ─── 文章检查 ───────────────────────────────────────────────

def check_article(file_path, check_plain_text=True, check_images=True, json_output=False, style=None):
    """只执行质量检查（字数+配图），不转换不推送。

    若未指定 style，自动从文件 frontmatter 解析。
    """
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"ERROR: 文件不存在: {file_path}")
        return {"success": False, "error": f"文件不存在: {file_path}"}

    md_content = file_path.read_text(encoding="utf-8")
    md_no_frontmatter = re.sub(r'^---.*?---', '', md_content, flags=re.DOTALL).strip()

    if style is None:
        style = _detect_style(md_content)
    constraint = _get_style_constraint(style)
    min_words, max_words = constraint["words"]
    target_images = constraint["images"]
    target_png = constraint["png"]
    target_gif = constraint["gif"]

    if not json_output:
        print(f"检测风格: {constraint['display']} ({style})")

    result = {
        "success": True,
        "style": style,
        "style_display": constraint["display"],
        "plain_text_count": 0,
        "image_count": 0,
        "png_count": 0,
        "gif_count": 0,
    }

    if check_plain_text:
        md_no_img = re.sub(r'!\[.*?\]\(.*?\)', '', md_no_frontmatter)
        md_no_md = re.sub(r'[#*>\-|=`~\[\](){}]', '', md_no_img)
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', md_no_md))
        english_words = len(re.findall(r'[a-zA-Z]+', md_no_md))
        plain_text_count = chinese_chars + english_words
        result["plain_text_count"] = plain_text_count

        if min_words > 0 and plain_text_count < min_words:
            print(f"FAIL: 纯文本仅 {plain_text_count} 字，未达 {constraint['display']} 的 {min_words} 字要求（差 {min_words - plain_text_count} 字）")
            result["success"] = False
        elif max_words > 0 and plain_text_count > max_words:
            print(f"WARN: 纯文本 {plain_text_count} 字，超过 {constraint['display']} 的 {max_words} 字上限，建议精简")
        else:
            target_label = f"{min_words}-{max_words}" if max_words > 0 else "不限"
            print(f"PASS: 纯文本 {plain_text_count} 字（目标 {target_label}）")

    if check_images:
        img_tags = re.findall(r'!\[.*?\]\(.*?\)', md_no_frontmatter)
        png_count = sum(1 for t in img_tags if '.png' in t.lower())
        gif_count = sum(1 for t in img_tags if '.gif' in t.lower())
        total_images = len(img_tags)
        result["image_count"] = total_images
        result["png_count"] = png_count
        result["gif_count"] = gif_count

        if target_images > 0 and total_images < target_images:
            print(f"FAIL: 配图仅 {total_images} 张，未达 {constraint['display']} 的 {target_images} 张要求")
            result["success"] = False
        if target_png > 0 and png_count < target_png:
            print(f"FAIL: PNG 配图仅 {png_count} 张，{constraint['display']} 至少需要 {target_png} 张 PNG")
            result["success"] = False
        if target_gif > 0 and gif_count < target_gif:
            print(f"FAIL: 缺少 GIF 动图，{constraint['display']} 至少需要 {target_gif} 张 GIF")
            result["success"] = False
        if result["success"] and target_images > 0:
            print(f"PASS: 配图 {png_count} PNG + {gif_count} GIF = {total_images} 张")
        elif target_images == 0:
            print(f"PASS: {constraint['display']} 不强制配图要求")

    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "ALL CHECKS PASSED" if result["success"] else "SOME CHECKS FAILED"
        print(f"\n--- 检查结果: {status} ---")

    return result


# ─── 发布主函数 ─────────────────────────────────────────────

def publish(file_path, cover="", title="", author="",
            auto_cover=False, max_chars=20000, upload_images=True, json_output=False,
            check_plain_text=True, check_images=True):
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"ERROR: 文件不存在: {file_path}")
        return {"success": False, "error": f"文件不存在: {file_path}"}

    md_content = file_path.read_text(encoding="utf-8")
    style = _detect_style(md_content)
    constraint = _get_style_constraint(style)
    min_words, max_words = constraint["words"]
    target_images = constraint["images"]
    target_png = constraint["png"]
    target_gif = constraint["gif"]

    if not json_output:
        print(f"检测风格: {constraint['display']} ({style})")

    if check_plain_text:
        md_no_frontmatter = re.sub(r'^---.*?---', '', md_content, flags=re.DOTALL).strip()
        md_no_img = re.sub(r'!\[.*?\]\(.*?\)', '', md_no_frontmatter)
        md_no_md = re.sub(r'[#*>\-|`~\[\](){}]', '', md_no_img)
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', md_no_md))
        english_words = len(re.findall(r'[a-zA-Z]+', md_no_md))
        plain_text_count = chinese_chars + english_words
        if min_words > 0 and plain_text_count < min_words:
            print(f"WARNING: 纯文本仅 {plain_text_count} 字，未达 {constraint['display']} 的 {min_words} 字要求")
            print(f"  可用 --skip-plain-check 跳过检查")
            if not json_output:
                return {"success": False, "error": f"纯文本仅 {plain_text_count} 字，{constraint['display']} 需 >= {min_words} 字",
                        "plain_text_count": plain_text_count, "style": style}
        elif max_words > 0 and plain_text_count > max_words:
            print(f"WARNING: 纯文本 {plain_text_count} 字，超过 {constraint['display']} 的 {max_words} 字上限，建议精简")

    if check_images:
        img_tags = re.findall(r'!\[.*?\]\(.*?\)', md_no_frontmatter if check_plain_text else md_content)
        png_count = sum(1 for t in img_tags if '.png' in t.lower())
        gif_count = sum(1 for t in img_tags if '.gif' in t.lower())
        total_images = len(img_tags)
        if target_images > 0 and total_images < target_images:
            print(f"WARNING: 配图仅 {total_images} 张，未达 {constraint['display']} 的 {target_images} 张要求")
            if not json_output:
                return {"success": False, "error": f"配图仅 {total_images} 张，{constraint['display']} 需 {target_images} 张",
                        "image_count": total_images, "png_count": png_count, "gif_count": gif_count, "style": style}
        if target_png > 0 and png_count < target_png:
            print(f"WARNING: PNG 配图仅 {png_count} 张，{constraint['display']} 至少需要 {target_png} 张 PNG")
            if not json_output:
                return {"success": False, "error": f"PNG 配图仅 {png_count} 张，{constraint['display']} 需 >= {target_png} 张",
                        "image_count": total_images, "png_count": png_count, "gif_count": gif_count, "style": style}
        if target_gif > 0 and gif_count < target_gif:
            print(f"WARNING: 缺少 GIF 动图，{constraint['display']} 至少需要 {target_gif} 张 GIF")
            if not json_output:
                return {"success": False, "error": f"{constraint['display']} 缺少 GIF 动图，需 >= {target_gif} 张",
                        "image_count": total_images, "png_count": png_count, "gif_count": gif_count, "style": style}
        if target_png > 0 and target_gif > 0 and (png_count > target_png or gif_count > target_gif):
            print(f"INFO: 配图超出 {constraint['display']} 限制（{png_count} PNG + {gif_count} GIF），将截断为 {target_png} PNG + {target_gif} GIF")
        if target_images > 0:
            print(f"  配图检查通过: {png_count} PNG + {gif_count} GIF = {total_images} 张")
        else:
            print(f"  {constraint['display']} 不强制配图要求")

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

    cover_path = cover
    if not cover_path and auto_cover:
        print("Generating cover...")
        png_result = generate_cover_png(
            title=article_title,
            subtitle=article_digest,
            author=article_author,
        )
        if png_result:
            cover_path = png_result
            print(f"  Cover generated: {cover_path}")

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
            if cover_path:
                print("Uploading cover...")
                upload = client.upload_image(cover_path, "thumb")
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
        "cover_used": cover_path or "",
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
        if cover_path:
            print(f"  Cover: {cover_path}")
        print(f"  HTML size: {len(html)} chars")

    return output


def main():
    parser = argparse.ArgumentParser(description="本质工坊 · 公众号发布管线")
    parser.add_argument("file", help="Markdown 文件路径")
    parser.add_argument("--cover", default="", help="封面图片路径")
    parser.add_argument("--title", default="", help="覆盖标题")
    parser.add_argument("--author", default="", help="覆盖作者")
    parser.add_argument("--auto-cover", action="store_true", help="自动生成封面")
    parser.add_argument("--max-chars", type=int, default=20000, help="HTML总字符上限（微信草稿箱限制）")
    parser.add_argument("--no-upload-images", action="store_true", help="不上传正文图片")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--skip-plain-check", action="store_true", help="跳过纯文本字数检查")
    parser.add_argument("--skip-image-check", action="store_true", help="跳过配图数量检查")
    parser.add_argument("--check-only", action="store_true", help="只执行质量检查（字数+配图），不转换不推送")

    args = parser.parse_args()

    if args.check_only:
        check_article(
            file_path=args.file,
            check_plain_text=not args.skip_plain_check,
            check_images=not args.skip_image_check,
            json_output=args.json,
        )
        return

    publish(
        file_path=args.file,
        cover=args.cover,
        title=args.title,
        author=args.author,
        auto_cover=args.auto_cover,
        max_chars=args.max_chars,
        upload_images=not args.no_upload_images,
        json_output=args.json,
        check_plain_text=not args.skip_plain_check,
        check_images=not args.skip_image_check,
    )


if __name__ == "__main__":
    main()
