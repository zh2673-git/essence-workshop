"""
本质工坊 · 公众号发布管线
一键发布：Markdown → HTML 转换 + 封面生成 + 图片上传 + 推送草稿箱

基于 md2wechat-py 最新代码，自包含无外部依赖

用法:
  python wechat_publish.py article.md
  python wechat_publish.py article.md --theme claude-clean
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

from wechat_client import WeChatClient
from wechat_converter import convert_markdown, inspect_article


def generate_cover_svg(title, subtitle="", author="", theme="claude-warm", output_path=""):
    colors = {
        "claude-warm": {
            "bg": "#FAF7F2", "accent": "#C96442", "heading": "#1F1D1A",
            "muted": "#8C8278", "border": "#E8E2DA",
        },
        "claude-clean": {
            "bg": "#FFFFFF", "accent": "#C96442", "heading": "#1A1A1A",
            "muted": "#9B9B9B", "border": "#ECECEC",
        },
        "claude-dark": {
            "bg": "#1A1816", "accent": "#D4896C", "heading": "#F0EBE3",
            "muted": "#8C8278", "border": "#3D3A36",
        },
    }
    c = colors.get(theme, colors["claude-warm"])

    display_title = title[:28] + ("..." if len(title) > 28 else "")
    display_author = author[:20] + ("..." if len(author) > 20 else "")
    display_sub = subtitle[:50] + ("..." if len(subtitle) > 50 else "")

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 383">
  <rect width="900" height="383" fill="{c['bg']}"/>
  <rect x="30" y="18" width="840" height="2" fill="{c['accent']}" opacity="0.3"/>
  <rect x="30" y="363" width="840" height="2" fill="{c['accent']}" opacity="0.3"/>
  <line x1="450" y1="140" x2="450" y2="143" stroke="{c['accent']}" stroke-width="3" stroke-linecap="round"/>
  <text x="450" y="120" text-anchor="middle" font-family="PingFang SC, Noto Sans SC, sans-serif"
        font-size="34" font-weight="700" fill="{c['heading']}">{display_title}</text>
  <text x="450" y="175" text-anchor="middle" font-family="PingFang SC, Noto Sans SC, sans-serif"
        font-size="13" fill="{c['muted']}">{display_author}</text>
  <text x="450" y="350" text-anchor="middle" font-family="PingFang SC, Noto Sans SC, sans-serif"
        font-size="11" fill="{c['muted']}" opacity="0.6">{display_sub}</text>
</svg>'''

    if not output_path:
        output_dir = Path.cwd() / "output" / "images"
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_title = "".join(ch for ch in title[:20] if ch.isalnum() or ch in " _-") or "cover"
        output_path = str(output_dir / f"cover_{safe_title}.svg")

    Path(output_path).write_text(svg, encoding="utf-8")
    return output_path


def generate_cover_png(title, subtitle="", author="", theme="claude-warm", output_path=""):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None

    try:
        import math

        w, h = 900, 383
        center_x = 450
        crop_l, crop_r = 259, 641

        if not output_path:
            output_dir = Path.cwd() / "output" / "images"
            output_dir.mkdir(parents=True, exist_ok=True)
            safe_title = "".join(ch for ch in title[:20] if ch.isalnum() or ch in " _-") or "cover"
            output_path = str(output_dir / f"cover_{safe_title}.png")

        bg_main = (28, 25, 23)
        bg_mid = (37, 34, 32)
        bg_deep = (17, 15, 13)
        accent = (201, 100, 66)
        gold = (212, 167, 106)
        gold_light = (232, 201, 138)
        text_main = (245, 240, 235)
        text_sub = (168, 159, 149)

        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        for y_px in range(h):
            t = y_px / h
            t2 = (y_px / h) * 0.3
            r = int(bg_main[0] * (1 - t) + bg_deep[0] * t + (bg_mid[0] - bg_main[0]) * t2)
            g = int(bg_main[1] * (1 - t) + bg_deep[1] * t + (bg_mid[1] - bg_main[1]) * t2)
            b = int(bg_main[2] * (1 - t) + bg_deep[2] * t + (bg_mid[2] - bg_main[2]) * t2)
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            draw.line([(0, y_px), (w, y_px)], fill=(r, g, b))

        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        glow_r = int(h * 0.9)
        for i in range(glow_r, 0, -2):
            t = i / glow_r
            alpha = int(46 * (1 - t) ** 2)
            od.ellipse([center_x - i, 170 - i, center_x + i, 170 + i], fill=accent + (alpha,))

        gr_cx, gr_cy = int(w * 0.78), int(h * 0.15)
        glow_r2 = int(h * 0.8)
        for i in range(glow_r2, 0, -2):
            t = i / glow_r2
            alpha = int(26 * (1 - t) ** 2)
            od.ellipse([gr_cx - i, gr_cy - i, gr_cx + i, gr_cy + i], fill=gold + (alpha,))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)

        bl_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        bld = ImageDraw.Draw(bl_overlay)
        bl_cx, bl_cy = int(w * 0.22), int(h * 0.85)
        glow_r3 = int(h * 0.6)
        for i in range(glow_r3, 0, -2):
            t = i / glow_r3
            alpha = int(30 * (1 - t) ** 2)
            bld.ellipse([bl_cx - i, bl_cy - i, bl_cx + i, bl_cy + i], fill=accent + (alpha,))
        img = Image.alpha_composite(img, bl_overlay)
        draw = ImageDraw.Draw(img)

        draw.line([(w - 60, 40), (w - 60, h - 40)], fill=gold + (46,), width=1)
        draw.line([(w - 45, 60), (w - 45, h - 60)], fill=gold + (26,), width=1)
        draw.line([(60, 40), (60, h - 40)], fill=accent + (38,), width=1)
        draw.line([(45, 60), (45, h - 60)], fill=accent + (20,), width=1)

        orbit_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        od2 = ImageDraw.Draw(orbit_overlay)
        cx, cy = center_x, 175
        rx, ry = 170, 45
        angle1 = math.radians(-8)
        for deg in range(0, 360, 2):
            rad = math.radians(deg)
            px = rx * math.cos(rad)
            py = ry * math.sin(rad)
            x_rot = cx + px * math.cos(angle1) - py * math.sin(angle1)
            y_rot = cy + px * math.sin(angle1) + py * math.cos(angle1)
            od2.ellipse([x_rot - 0.8, y_rot - 0.8, x_rot + 0.8, y_rot + 0.8], fill=gold + (56,))
        angle2 = math.radians(22)
        for deg in range(0, 360, 3):
            rad = math.radians(deg)
            px = rx * math.cos(rad)
            py = ry * math.sin(rad)
            x_rot = cx + px * math.cos(angle2) - py * math.sin(angle2)
            y_rot = cy + px * math.sin(angle2) + py * math.cos(angle2)
            od2.ellipse([x_rot - 0.5, y_rot - 0.5, x_rot + 0.5, y_rot + 0.5], fill=gold + (26,))
        img = Image.alpha_composite(img, orbit_overlay)
        draw = ImageDraw.Draw(img)

        stars = [
            (center_x - 120, 60, 1.8, gold_light + (128,)),
            (center_x + 95, 52, 1.2, gold + (89,)),
            (center_x + 140, 310, 1.5, gold_light + (102,)),
            (center_x - 80, 300, 1.0, gold + (77,)),
            (center_x - 155, 180, 0.8, gold + (51,)),
            (center_x + 60, 250, 1.3, gold_light + (77,)),
            (center_x - 30, 340, 0.7, gold + (64,)),
        ]
        for sx, sy, sr, sc in stars:
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=sc)

        moon_cx, moon_cy, moon_r = crop_r - 45, 52, 10
        draw.ellipse([moon_cx - moon_r, moon_cy - moon_r, moon_cx + moon_r, moon_cy + moon_r], fill=gold + (38,))
        offset = 4
        draw.ellipse([moon_cx + offset - moon_r, moon_cy - offset - moon_r + 1,
                      moon_cx + offset + moon_r, moon_cy - offset + moon_r + 1], fill=bg_main + (217,))

        corner_len = 20
        corner_pad = 12
        corner_alpha = 115
        corner_color = gold + (corner_alpha,)
        draw.line([(crop_l + corner_pad, 8), (crop_l + corner_pad, 8 + corner_len)], fill=corner_color, width=2)
        draw.line([(crop_l + corner_pad, 8), (crop_l + corner_pad + corner_len, 8)], fill=corner_color, width=2)
        draw.line([(crop_r - corner_pad, 8), (crop_r - corner_pad, 8 + corner_len)], fill=corner_color, width=2)
        draw.line([(crop_r - corner_pad - corner_len, 8), (crop_r - corner_pad, 8)], fill=corner_color, width=2)
        draw.line([(crop_l + corner_pad, h - 8), (crop_l + corner_pad, h - 8 - corner_len)], fill=corner_color, width=2)
        draw.line([(crop_l + corner_pad, h - 8), (crop_l + corner_pad + corner_len, h - 8)], fill=corner_color, width=2)
        draw.line([(crop_r - corner_pad, h - 8), (crop_r - corner_pad, h - 8 - corner_len)], fill=corner_color, width=2)
        draw.line([(crop_r - corner_pad - corner_len, h - 8), (crop_r - corner_pad, h - 8)], fill=corner_color, width=2)

        line_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ld = ImageDraw.Draw(line_overlay)
        for x_px in range(30, 870):
            t = (x_px - 30) / 840.0
            bell = max(0, 1.0 - abs(t - 0.5) * 2.5)
            alpha = int(179 * bell)
            ld.line([(x_px, 18), (x_px + 1, 18)], fill=gold + (alpha,), width=1)
            ld.line([(x_px, h - 18), (x_px + 1, h - 18)], fill=gold + (alpha,), width=1)
        img = Image.alpha_composite(img, line_overlay)
        draw = ImageDraw.Draw(img)

        draw.line([(center_x - 60, 148), (center_x + 60, 148)], fill=accent + (204,), width=3)

        font_title = _load_font(34, bold=True)
        font_author = _load_font(13)
        font_sub = _load_font(11)

        display_title = title[:28] + ("..." if len(title) > 28 else "")
        display_author = author[:20] + ("..." if len(author) > 20 else "")
        display_sub = subtitle[:50] + ("..." if len(subtitle) > 50 else "")

        if display_title:
            bbox = draw.textbbox((0, 0), display_title, font=font_title)
            tw = bbox[2] - bbox[0]
            draw.text((center_x - tw // 2, 105), display_title, fill=text_main, font=font_title)
        if display_author:
            bbox = draw.textbbox((0, 0), display_author, font=font_author)
            aw = bbox[2] - bbox[0]
            draw.text((center_x - aw // 2, 165), display_author, fill=text_sub, font=font_author)
        if display_sub:
            bbox = draw.textbbox((0, 0), display_sub, font=font_sub)
            sw_val = bbox[2] - bbox[0]
            draw.text((center_x - sw_val // 2, h - 45), display_sub, fill=text_sub + (153,), font=font_sub)

        img = img.convert("RGB")
        img.save(output_path, "PNG")
        return output_path
    except Exception:
        return None


def _load_font(size, bold=False):
    from PIL import ImageFont
    import os

    candidates = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                font = ImageFont.truetype(path, size, index=0)
                if bold:
                    try:
                        font = ImageFont.truetype(path, size, index=1)
                    except Exception:
                        pass
                return font
            except Exception:
                continue
    return ImageFont.load_default()


def publish(file_path, theme="claude-warm", cover="", title="", author="",
            auto_cover=False, min_chars=19000, upload_images=True, json_output=False):
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"ERROR: 文件不存在: {file_path}")
        return {"success": False, "error": f"文件不存在: {file_path}"}

    result = convert_markdown(
        file_path=str(file_path),
        theme=theme,
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
    if char_count < min_chars:
        print(f"WARNING: 正文仅 {char_count} 字符，未达 {min_chars} 字符要求")
        print(f"  可用 --min-chars 0 跳过检查")
        if not json_output:
            return {"success": False, "error": f"正文仅 {char_count} 字符，需 >= {min_chars} 字符",
                    "char_count": char_count, "min_chars": min_chars}

    cover_path = cover
    if not cover_path and auto_cover:
        print("Generating cover...")

        png_result = generate_cover_png(
            title=article_title,
            subtitle=article_digest,
            author=article_author,
            theme=theme,
        )
        if png_result:
            cover_path = png_result
            print(f"  Cover generated (PIL): {cover_path}")

        if not cover_path:
            try:
                from playwright.sync_api import sync_playwright
                svg_path = generate_cover_svg(
                    title=article_title,
                    subtitle=article_digest,
                    author=article_author,
                    theme=theme,
                )
                png_path = svg_path.replace(".svg", ".png")
                with sync_playwright() as pw:
                    br = pw.chromium.launch()
                    pg = br.new_page(device_scale_factor=2)
                    svg_abs = os.path.abspath(svg_path).replace(os.sep, '/')
                    pg.goto(f'file:///{svg_abs}', timeout=30000)
                    pg.wait_for_timeout(200)
                    pg.screenshot(path=png_path, full_page=True)
                    br.close()
                cover_path = png_path
                print(f"  Cover generated (SVG->PNG via Playwright): {png_path}")
            except Exception:
                pass

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
                            from playwright.sync_api import sync_playwright
                            png_path = local_path.replace('.svg', '_upload.png')
                            with sync_playwright() as pw:
                                br = pw.chromium.launch()
                                pg = br.new_page(device_scale_factor=2)
                                svg_abs = os.path.abspath(local_path).replace(os.sep, '/')
                                pg.goto(f'file:///{svg_abs}', timeout=30000)
                                pg.wait_for_timeout(200)
                                el = pg.query_selector('svg')
                                if el:
                                    box = el.bounding_box()
                                    if box:
                                        pg.set_viewport_size({"width": int(box['width']) + 20, "height": int(box['height']) + 20})
                                pg.screenshot(path=png_path, full_page=True)
                                br.close()
                            upload_path = png_path
                        except Exception as svg_err:
                            print(f"  WARNING: SVG convert failed (Playwright): {img_src} ({svg_err})")
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
    parser.add_argument("--theme", default="claude-warm", help="主题 (claude-warm/clean/dark)")
    parser.add_argument("--cover", default="", help="封面图片路径")
    parser.add_argument("--title", default="", help="覆盖标题")
    parser.add_argument("--author", default="", help="覆盖作者")
    parser.add_argument("--auto-cover", action="store_true", help="自动生成封面")
    parser.add_argument("--min-chars", type=int, default=19000, help="正文最小字符数")
    parser.add_argument("--no-upload-images", action="store_true", help="不上传正文图片")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    publish(
        file_path=args.file,
        theme=args.theme,
        cover=args.cover,
        title=args.title,
        author=args.author,
        auto_cover=args.auto_cover,
        min_chars=args.min_chars,
        upload_images=not args.no_upload_images,
        json_output=args.json,
    )


if __name__ == "__main__":
    main()
