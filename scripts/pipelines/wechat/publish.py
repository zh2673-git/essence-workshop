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

from .client import WeChatClient
from .converter import convert_markdown, inspect_article


def generate_cover_svg(title, subtitle="", author="", theme="claude-warm", output_path=""):
    from scripts.elements.svg_themes import render_svg_cover, save_svg, match_theme

    theme_map = {
        "claude-warm": "warm",
        "claude-clean": "minimal",
        "claude-dark": "dark",
    }
    theme_name = theme_map.get(theme, "warm")

    svg = render_svg_cover(title, subtitle, author, theme_name=theme_name)

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

        layout = _get_cover_layout(theme)
        palette = layout["palette"]

        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        for element_name in layout["elements"]:
            renderer = _COVER_ELEMENTS.get(element_name)
            if renderer:
                img, draw = renderer(img, draw, w, h, palette, layout.get("element_config", {}))

        font_title = _load_font(layout["title_font_size"], bold=True)
        font_author = _load_font(layout["author_font_size"])
        font_sub = _load_font(layout["sub_font_size"])

        display_title = title[:28] + ("..." if len(title) > 28 else "")
        display_author = author[:20] + ("..." if len(author) > 20 else "")
        display_sub = subtitle[:50] + ("..." if len(subtitle) > 50 else "")

        if display_title:
            bbox = draw.textbbox((0, 0), display_title, font=font_title)
            tw = bbox[2] - bbox[0]
            draw.text((center_x - tw // 2, layout["title_y"]), display_title, fill=palette["text_main"], font=font_title)
        if display_author:
            bbox = draw.textbbox((0, 0), display_author, font=font_author)
            aw = bbox[2] - bbox[0]
            draw.text((center_x - aw // 2, layout["author_y"]), display_author, fill=palette["text_sub"], font=font_author)
        if display_sub:
            bbox = draw.textbbox((0, 0), display_sub, font=font_sub)
            sw_val = bbox[2] - bbox[0]
            draw.text((center_x - sw_val // 2, h - 45), display_sub, fill=palette["text_sub"] + (153,), font=font_sub)

        img = img.convert("RGB")
        img.save(output_path, "PNG")
        return output_path
    except Exception:
        return None


def _get_cover_layout(theme):
    layouts = {
        "space": {
            "palette": {
                "bg_main": (28, 25, 23),
                "bg_mid": (37, 34, 32),
                "bg_deep": (17, 15, 13),
                "accent": (201, 100, 66),
                "gold": (212, 167, 106),
                "gold_light": (232, 201, 138),
                "text_main": (245, 240, 235),
                "text_sub": (168, 159, 149),
            },
            "elements": [
                "gradient_bg",
                "center_glow",
                "topright_glow",
                "bottomleft_glow",
                "side_lines",
                "orbit_rings",
                "star_field",
                "crescent_moon",
                "corner_marks",
                "bell_lines",
                "title_divider",
            ],
            "element_config": {
                "center_glow": {"cx_ratio": 0.5, "cy_ratio": 0.44, "r_ratio": 0.9, "max_alpha": 46},
                "topright_glow": {"cx_ratio": 0.78, "cy_ratio": 0.15, "r_ratio": 0.8, "max_alpha": 26},
                "bottomleft_glow": {"cx_ratio": 0.22, "cy_ratio": 0.85, "r_ratio": 0.6, "max_alpha": 30},
                "orbit_rings": {"cx_ratio": 0.5, "cy_ratio": 0.46, "rx": 170, "ry": 45, "angles": [-8, 22]},
                "star_field": {
                    "stars": [
                        (-120, 60, 1.8, "gold_light", 128),
                        (95, 52, 1.2, "gold", 89),
                        (140, 310, 1.5, "gold_light", 102),
                        (-80, 300, 1.0, "gold", 77),
                        (-155, 180, 0.8, "gold", 51),
                        (60, 250, 1.3, "gold_light", 77),
                        (-30, 340, 0.7, "gold", 64),
                    ]
                },
                "crescent_moon": {"offset_x": -45, "offset_y": 52, "radius": 10, "crescent_offset": 4},
                "corner_marks": {"length": 20, "padding": 12, "alpha": 115, "crop_l": 259, "crop_r": 641},
                "bell_lines": {"y_top": 18, "y_bot_offset": 18, "x_start": 30, "x_end": 870, "max_alpha": 179},
                "title_divider": {"half_width": 60, "y_ratio": 0.386, "width": 3, "alpha": 204},
            },
            "title_y": 105,
            "author_y": 165,
            "title_font_size": 34,
            "author_font_size": 13,
            "sub_font_size": 11,
        },
        "warm_space": {
            "palette": {
                "bg_main": (45, 35, 28),
                "bg_mid": (55, 42, 33),
                "bg_deep": (30, 22, 16),
                "accent": (212, 118, 58),
                "gold": (240, 194, 127),
                "gold_light": (255, 220, 160),
                "text_main": (250, 242, 232),
                "text_sub": (180, 165, 145),
            },
            "elements": [
                "gradient_bg",
                "center_glow",
                "topright_glow",
                "orbit_rings",
                "star_field",
                "corner_marks",
                "bell_lines",
                "title_divider",
            ],
            "element_config": {
                "center_glow": {"cx_ratio": 0.5, "cy_ratio": 0.44, "r_ratio": 0.85, "max_alpha": 40},
                "topright_glow": {"cx_ratio": 0.75, "cy_ratio": 0.2, "r_ratio": 0.7, "max_alpha": 22},
                "orbit_rings": {"cx_ratio": 0.5, "cy_ratio": 0.46, "rx": 150, "ry": 40, "angles": [-5, 18]},
                "star_field": {
                    "stars": [
                        (-100, 70, 1.5, "gold_light", 100),
                        (80, 45, 1.0, "gold", 70),
                        (120, 290, 1.2, "gold_light", 80),
                        (-60, 280, 0.8, "gold", 55),
                    ]
                },
                "corner_marks": {"length": 18, "padding": 14, "alpha": 90, "crop_l": 259, "crop_r": 641},
                "bell_lines": {"y_top": 18, "y_bot_offset": 18, "x_start": 30, "x_end": 870, "max_alpha": 150},
                "title_divider": {"half_width": 50, "y_ratio": 0.386, "width": 2, "alpha": 180},
            },
            "title_y": 105,
            "author_y": 165,
            "title_font_size": 34,
            "author_font_size": 13,
            "sub_font_size": 11,
        },
        "minimal_space": {
            "palette": {
                "bg_main": (22, 22, 26),
                "bg_mid": (30, 30, 36),
                "bg_deep": (14, 14, 18),
                "accent": (120, 140, 200),
                "gold": (160, 170, 200),
                "gold_light": (200, 210, 230),
                "text_main": (230, 230, 240),
                "text_sub": (140, 140, 160),
            },
            "elements": [
                "gradient_bg",
                "center_glow",
                "star_field",
                "bell_lines",
                "title_divider",
            ],
            "element_config": {
                "center_glow": {"cx_ratio": 0.5, "cy_ratio": 0.44, "r_ratio": 0.7, "max_alpha": 25},
                "star_field": {
                    "stars": [
                        (-80, 50, 1.0, "gold_light", 80),
                        (60, 40, 0.8, "gold", 50),
                        (100, 300, 0.9, "gold_light", 60),
                    ]
                },
                "bell_lines": {"y_top": 20, "y_bot_offset": 20, "x_start": 40, "x_end": 860, "max_alpha": 100},
                "title_divider": {"half_width": 40, "y_ratio": 0.386, "width": 2, "alpha": 140},
            },
            "title_y": 105,
            "author_y": 165,
            "title_font_size": 32,
            "author_font_size": 12,
            "sub_font_size": 10,
        },
    }

    theme_map = {
        "claude-warm": "warm_space",
        "claude-clean": "minimal_space",
        "claude-dark": "space",
    }
    layout_name = theme_map.get(theme, "space")
    return layouts[layout_name]


def _cover_gradient_bg(img, draw, w, h, palette, config):
    bg_main = palette["bg_main"]
    bg_mid = palette["bg_mid"]
    bg_deep = palette["bg_deep"]
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
    return img, draw


def _cover_center_glow(img, draw, w, h, palette, config):
    from PIL import Image, ImageDraw
    cfg = config.get("center_glow", {})
    cx = int(w * cfg.get("cx_ratio", 0.5))
    cy = int(h * cfg.get("cy_ratio", 0.44))
    glow_r = int(h * cfg.get("r_ratio", 0.9))
    max_alpha = cfg.get("max_alpha", 46)
    color = palette["accent"]

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(glow_r, 0, -2):
        t = i / glow_r
        alpha = int(max_alpha * (1 - t) ** 2)
        od.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color + (alpha,))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    return img, draw


def _cover_topright_glow(img, draw, w, h, palette, config):
    from PIL import Image, ImageDraw
    cfg = config.get("topright_glow", {})
    cx = int(w * cfg.get("cx_ratio", 0.78))
    cy = int(h * cfg.get("cy_ratio", 0.15))
    glow_r = int(h * cfg.get("r_ratio", 0.8))
    max_alpha = cfg.get("max_alpha", 26)
    color = palette["gold"]

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(glow_r, 0, -2):
        t = i / glow_r
        alpha = int(max_alpha * (1 - t) ** 2)
        od.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color + (alpha,))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    return img, draw


def _cover_bottomleft_glow(img, draw, w, h, palette, config):
    from PIL import Image, ImageDraw
    cfg = config.get("bottomleft_glow", {})
    cx = int(w * cfg.get("cx_ratio", 0.22))
    cy = int(h * cfg.get("cy_ratio", 0.85))
    glow_r = int(h * cfg.get("r_ratio", 0.6))
    max_alpha = cfg.get("max_alpha", 30)
    color = palette["accent"]

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(glow_r, 0, -2):
        t = i / glow_r
        alpha = int(max_alpha * (1 - t) ** 2)
        od.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color + (alpha,))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    return img, draw


def _cover_side_lines(img, draw, w, h, palette, config):
    gold = palette["gold"]
    accent = palette["accent"]
    draw.line([(w - 60, 40), (w - 60, h - 40)], fill=gold + (46,), width=1)
    draw.line([(w - 45, 60), (w - 45, h - 60)], fill=gold + (26,), width=1)
    draw.line([(60, 40), (60, h - 40)], fill=accent + (38,), width=1)
    draw.line([(45, 60), (45, h - 60)], fill=accent + (20,), width=1)
    return img, draw


def _cover_orbit_rings(img, draw, w, h, palette, config):
    import math
    from PIL import Image, ImageDraw
    cfg = config.get("orbit_rings", {})
    cx = int(w * cfg.get("cx_ratio", 0.5))
    cy = int(h * cfg.get("cy_ratio", 0.46))
    rx = cfg.get("rx", 170)
    ry = cfg.get("ry", 45)
    angles = cfg.get("angles", [-8, 22])
    gold = palette["gold"]

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for idx, angle_deg in enumerate(angles):
        angle = math.radians(angle_deg)
        step = 2 if idx == 0 else 3
        alpha = 56 if idx == 0 else 26
        dot_r = 0.8 if idx == 0 else 0.5
        for deg in range(0, 360, step):
            rad = math.radians(deg)
            px = rx * math.cos(rad)
            py = ry * math.sin(rad)
            x_rot = cx + px * math.cos(angle) - py * math.sin(angle)
            y_rot = cy + px * math.sin(angle) + py * math.cos(angle)
            od.ellipse([x_rot - dot_r, y_rot - dot_r, x_rot + dot_r, y_rot + dot_r], fill=gold + (alpha,))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    return img, draw


def _cover_star_field(img, draw, w, h, palette, config):
    import math
    cfg = config.get("star_field", {})
    center_x = w // 2
    color_map = {
        "gold": palette["gold"],
        "gold_light": palette["gold_light"],
    }

    for star in cfg.get("stars", []):
        dx, dy, sr, color_name, alpha = star
        color = color_map.get(color_name, palette["gold"])
        sx = center_x + dx
        sy = dy
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=color + (alpha,))

    import random
    random.seed(42)
    for _ in range(30):
        sx = random.randint(30, w - 30)
        sy = random.randint(10, h - 10)
        sr = random.uniform(0.3, 0.7)
        alpha = random.randint(20, 50)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=palette["gold"] + (alpha,))
    return img, draw


def _cover_crescent_moon(img, draw, w, h, palette, config):
    cfg = config.get("crescent_moon", {})
    crop_r = cfg.get("crop_r", 641)
    moon_cx = crop_r + cfg.get("offset_x", -45)
    moon_cy = cfg.get("offset_y", 52)
    moon_r = cfg.get("radius", 10)
    crescent_offset = cfg.get("crescent_offset", 4)
    gold = palette["gold"]
    bg_main = palette["bg_main"]

    draw.ellipse([moon_cx - moon_r, moon_cy - moon_r, moon_cx + moon_r, moon_cy + moon_r], fill=gold + (38,))
    draw.ellipse([moon_cx + crescent_offset - moon_r, moon_cy - crescent_offset - moon_r + 1,
                  moon_cx + crescent_offset + moon_r, moon_cy - crescent_offset + moon_r + 1], fill=bg_main + (217,))
    return img, draw


def _cover_corner_marks(img, draw, w, h, palette, config):
    cfg = config.get("corner_marks", {})
    crop_l = cfg.get("crop_l", 259)
    crop_r = cfg.get("crop_r", 641)
    corner_len = cfg.get("length", 20)
    corner_pad = cfg.get("padding", 12)
    corner_alpha = cfg.get("alpha", 115)
    corner_color = palette["gold"] + (corner_alpha,)

    draw.line([(crop_l + corner_pad, 8), (crop_l + corner_pad, 8 + corner_len)], fill=corner_color, width=2)
    draw.line([(crop_l + corner_pad, 8), (crop_l + corner_pad + corner_len, 8)], fill=corner_color, width=2)
    draw.line([(crop_r - corner_pad, 8), (crop_r - corner_pad, 8 + corner_len)], fill=corner_color, width=2)
    draw.line([(crop_r - corner_pad - corner_len, 8), (crop_r - corner_pad, 8)], fill=corner_color, width=2)
    draw.line([(crop_l + corner_pad, h - 8), (crop_l + corner_pad, h - 8 - corner_len)], fill=corner_color, width=2)
    draw.line([(crop_l + corner_pad, h - 8), (crop_l + corner_pad + corner_len, h - 8)], fill=corner_color, width=2)
    draw.line([(crop_r - corner_pad, h - 8), (crop_r - corner_pad, h - 8 - corner_len)], fill=corner_color, width=2)
    draw.line([(crop_r - corner_pad - corner_len, h - 8), (crop_r - corner_pad, h - 8)], fill=corner_color, width=2)
    return img, draw


def _cover_bell_lines(img, draw, w, h, palette, config):
    from PIL import Image, ImageDraw
    cfg = config.get("bell_lines", {})
    y_top = cfg.get("y_top", 18)
    y_bot = h - cfg.get("y_bot_offset", 18)
    x_start = cfg.get("x_start", 30)
    x_end = cfg.get("x_end", 870)
    max_alpha = cfg.get("max_alpha", 179)
    gold = palette["gold"]

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(overlay)
    span = x_end - x_start
    for x_px in range(x_start, x_end):
        t = (x_px - x_start) / span
        bell = max(0, 1.0 - abs(t - 0.5) * 2.5)
        alpha = int(max_alpha * bell)
        ld.line([(x_px, y_top), (x_px + 1, y_top)], fill=gold + (alpha,), width=1)
        ld.line([(x_px, y_bot), (x_px + 1, y_bot)], fill=gold + (alpha,), width=1)
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    return img, draw


def _cover_title_divider(img, draw, w, h, palette, config):
    cfg = config.get("title_divider", {})
    center_x = w // 2
    half_w = cfg.get("half_width", 60)
    y = int(h * cfg.get("y_ratio", 0.386))
    line_w = cfg.get("width", 3)
    alpha = cfg.get("alpha", 204)
    accent = palette["accent"]

    draw.line([(center_x - half_w, y), (center_x + half_w, y)], fill=accent + (alpha,), width=line_w)
    return img, draw


_COVER_ELEMENTS = {
    "gradient_bg": _cover_gradient_bg,
    "center_glow": _cover_center_glow,
    "topright_glow": _cover_topright_glow,
    "bottomleft_glow": _cover_bottomleft_glow,
    "side_lines": _cover_side_lines,
    "orbit_rings": _cover_orbit_rings,
    "star_field": _cover_star_field,
    "crescent_moon": _cover_crescent_moon,
    "corner_marks": _cover_corner_marks,
    "bell_lines": _cover_bell_lines,
    "title_divider": _cover_title_divider,
}


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
            auto_cover=False, min_chars=19000, upload_images=True, json_output=False,
            check_plain_text=True, check_images=True, brand_spec_path=None):
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"ERROR: 文件不存在: {file_path}")
        return {"success": False, "error": f"文件不存在: {file_path}"}

    md_content = file_path.read_text(encoding="utf-8")

    if check_plain_text:
        md_no_frontmatter = re.sub(r'^---.*?---', '', md_content, flags=re.DOTALL).strip()
        md_no_img = re.sub(r'!\[.*?\]\(.*?\)', '', md_no_frontmatter)
        md_no_md = re.sub(r'[#*>\-|=`~\[\](){}]', '', md_no_img)
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', md_no_md))
        english_words = len(re.findall(r'[a-zA-Z]+', md_no_md))
        plain_text_count = chinese_chars + english_words
        if plain_text_count < 7000:
            print(f"WARNING: 纯文本仅 {plain_text_count} 字，未达 7000 字硬性要求")
            print(f"  可用 --skip-plain-check 跳过检查")
            if not json_output:
                return {"success": False, "error": f"纯文本仅 {plain_text_count} 字，需 >= 7000 字",
                        "plain_text_count": plain_text_count}
        elif plain_text_count > 8000:
            print(f"WARNING: 纯文本 {plain_text_count} 字，超过 8000 字上限，建议精简")

    if check_images:
        img_tags = re.findall(r'!\[.*?\]\(.*?\)', md_no_frontmatter if check_plain_text else md_content)
        png_count = sum(1 for t in img_tags if '.png' in t.lower())
        gif_count = sum(1 for t in img_tags if '.gif' in t.lower())
        total_images = len(img_tags)
        if total_images < 7:
            print(f"WARNING: 配图仅 {total_images} 张，未达 7 张硬性要求（6 PNG + 1 GIF）")
            if not json_output:
                return {"success": False, "error": f"配图仅 {total_images} 张，需 7 张（6 PNG + 1 GIF）",
                        "image_count": total_images, "png_count": png_count, "gif_count": gif_count}
        if png_count < 6:
            print(f"WARNING: PNG 配图仅 {png_count} 张，至少需要 6 张 PNG")
            if not json_output:
                return {"success": False, "error": f"PNG 配图仅 {png_count} 张，需 >= 6 张 PNG",
                        "image_count": total_images, "png_count": png_count, "gif_count": gif_count}
        if gif_count < 1:
            print(f"WARNING: 缺少 GIF 动图，至少需要 1 张 GIF")
            if not json_output:
                return {"success": False, "error": "缺少 GIF 动图，至少需要 1 张 GIF",
                        "image_count": total_images, "png_count": png_count, "gif_count": gif_count}
        if png_count > 6 or gif_count > 1:
            print(f"INFO: 配图超出限制（{png_count} PNG + {gif_count} GIF），将截断为 6 PNG + 1 GIF")
        print(f"  配图检查通过: {png_count} PNG + {gif_count} GIF = {total_images} 张")

    result = convert_markdown(
        file_path=str(file_path),
        theme=theme,
        title=title,
        author=author,
        brand_spec_path=brand_spec_path,
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
                from scripts.elements.svg_to_png import svg_to_png
                svg_path = generate_cover_svg(
                    title=article_title,
                    subtitle=article_digest,
                    author=article_author,
                    theme=theme,
                )
                png_path = svg_path.replace(".svg", ".png")
                svg_to_png(svg_path, png_path, dpi=2)
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
                            from scripts.elements.svg_to_png import svg_to_png
                            png_path = local_path.replace('.svg', '_upload.png')
                            svg_to_png(local_path, png_path, dpi=2)
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
    parser.add_argument("--theme", default="essence", help="主题 (essence/claude-warm/claude-clean/claude-dark)")
    parser.add_argument("--brand-spec", default="", help="品牌配置文件路径 (brand-spec.json)")
    parser.add_argument("--cover", default="", help="封面图片路径")
    parser.add_argument("--title", default="", help="覆盖标题")
    parser.add_argument("--author", default="", help="覆盖作者")
    parser.add_argument("--auto-cover", action="store_true", help="自动生成封面")
    parser.add_argument("--min-chars", type=int, default=19000, help="正文最小字符数")
    parser.add_argument("--no-upload-images", action="store_true", help="不上传正文图片")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--skip-plain-check", action="store_true", help="跳过纯文本字数检查")
    parser.add_argument("--skip-image-check", action="store_true", help="跳过配图数量检查")

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
        check_plain_text=not args.skip_plain_check,
        check_images=not args.skip_image_check,
        brand_spec_path=args.brand_spec or None,
    )


if __name__ == "__main__":
    main()
