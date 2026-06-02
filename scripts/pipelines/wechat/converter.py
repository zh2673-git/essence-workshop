"""
本质工坊 · Markdown → 微信公众号 HTML 转换器
基于 md2wechat-py 最新代码，自包含无 wechat-pub 依赖

功能：
- Markdown → 微信兼容 HTML（纯内联样式，无 <style> 标签）
- 3 套主题（essence / claude-warm / claude-clean）
- brand-spec.json 动态主题生成
- Frontmatter 解析
- 标题去重
- HTML 压缩（控制在 20000 字符限制内）
- 文章检查（inspect）
"""

import json
import os
import re

from markdown_it import MarkdownIt


THEMES = {
    "claude-warm": {
        "_root": (
            "max-width:680px;margin:0 auto;padding:24px 16px;"
            "background:#FAF7F2;"
            "font-family:-apple-system,BlinkMacSystemFont,"
            '"PingFang SC","Noto Sans SC",sans-serif;'
            "font-size:16px;line-height:1.8;color:#3D3A36;"
        ),
        "h1": "font-family:'Noto Serif SC',Georgia,serif;font-size:22px;font-weight:700;color:#1F1D1A;margin:36px 0 16px;line-height:1.4;",
        "h2": "font-size:19px;font-weight:600;color:#1F1D1A;margin:36px 0 16px;padding-bottom:8px;border-bottom:1px solid #E8E2DA;",
        "h3": "font-size:17px;font-weight:600;color:#8B5E3C;margin:20px 0 12px;",
        "h4": "font-size:16px;font-weight:600;color:#8B5E3C;margin:14px 0 8px;",
        "p": "margin:0 0 16px;color:#3D3A36;line-height:1.8;",
        "blockquote": "border-left:3px solid #C96442;background:#FEFCF9;margin:28px 0;padding:16px 20px;border-radius:0 10px 10px 0;",
        "ul": "margin:16px 0;padding-left:24px;color:#3D3A36;",
        "ol": "margin:16px 0;padding-left:24px;color:#3D3A36;",
        "li": "margin:8px 0;line-height:1.8;",
        "strong": "font-weight:700;color:#1F1D1A;background:linear-gradient(to top,rgba(212,118,58,0.18) 40%,transparent 40%);padding:0 2px;",
        "em": "font-style:italic;color:#8C8278;",
        "a": "color:#C96442;text-decoration:none;",
        "hr": "border:none;border-top:1px solid #E8E2DA;margin:36px 0;",
        "code": "background:#F5E6DC;color:#8B5E3C;padding:2px 6px;border-radius:4px;font-size:0.9em;",
        "pre": "background:#F5E6DC;color:#3D3A36;padding:16px 20px;border-radius:10px;overflow-x:auto;margin:28px 0;",
        "img": "max-width:100%;height:auto;border-radius:6px;margin:12px 0;",
        "table": "width:100%;border-collapse:collapse;margin:20px 0;",
        "th": "background:#F5E6DC;font-weight:600;padding:10px 14px;border:1px solid #E8E2DA;text-align:left;",
        "td": "padding:10px 14px;border:1px solid #E8E2DA;color:#3D3A36;",
    },
    "claude-clean": {
        "_root": (
            "max-width:680px;margin:0 auto;padding:24px 16px;"
            "background:#FFFFFF;"
            "font-family:-apple-system,BlinkMacSystemFont,"
            '"PingFang SC","Noto Sans SC",sans-serif;'
            "font-size:15px;line-height:1.8;color:#37352F;"
        ),
        "h1": "font-size:21px;font-weight:700;color:#1A1A1A;margin:32px 0 14px;line-height:1.4;",
        "h2": "font-size:18px;font-weight:600;color:#1A1A1A;margin:32px 0 14px;line-height:1.45;padding-bottom:8px;border-bottom:1px solid #ECECEC;",
        "h3": "font-size:16px;font-weight:600;color:#1A1A1A;margin:20px 0 10px;",
        "h4": "font-size:15px;font-weight:600;color:#1A1A1A;margin:14px 0 8px;",
        "p": "margin:0 0 14px;color:#37352F;line-height:1.8;",
        "blockquote": "border-left:3px solid #C96442;background:#FEFEFE;margin:24px 0;padding:16px 20px;border-radius:0 8px 8px 0;color:#1A1A1A;",
        "ul": "margin:14px 0;padding-left:24px;color:#37352F;",
        "ol": "margin:14px 0;padding-left:24px;color:#37352F;",
        "li": "margin:6px 0;line-height:1.8;",
        "strong": "font-weight:700;color:#1A1A1A;background:linear-gradient(to top,rgba(120,140,200,0.12) 40%,transparent 40%);padding:0 2px;",
        "em": "font-style:italic;color:#9B9B9B;",
        "a": "color:#C96442;text-decoration:none;border-bottom:1px solid #FBF4EF;",
        "hr": "border:none;border-top:1px solid #ECECEC;margin:32px 0;",
        "code": "background:#F0F0F2;color:#5A5A6A;padding:2px 6px;border-radius:4px;font-size:0.9em;",
        "pre": "background:#F0F0F2;color:#2A2A2E;padding:16px 20px;border-radius:8px;overflow-x:auto;margin:24px 0;",
        "img": "max-width:100%;height:auto;border-radius:4px;margin:10px 0;",
        "table": "width:100%;border-collapse:collapse;margin:18px 0;font-size:14px;",
        "th": "background:#FBF4EF;color:#1A1A1A;font-weight:600;padding:8px 12px;border:1px solid #ECECEC;text-align:left;",
        "td": "padding:8px 12px;border:1px solid #ECECEC;color:#37352F;",
    },
    "essence": {
        "_root": (
            "max-width:680px;margin:0 auto;padding:28px 16px;"
            "background:#FAFAF8;"
            "font-family:-apple-system,BlinkMacSystemFont,"
            '"PingFang SC","Noto Sans SC",sans-serif;'
            "font-size:15px;line-height:1.8;color:#2C2C2C;"
        ),
        "h1": "font-size:20px;font-weight:700;color:#1A1A1A;margin:32px 0 20px;line-height:1.5;letter-spacing:0.02em;",
        "h2": "font-size:17px;font-weight:600;color:#1A1A1A;margin:28px 0 16px;line-height:1.5;padding-bottom:6px;border-bottom:1px solid #E8E5E0;",
        "h3": "font-size:15px;font-weight:600;color:#444;margin:20px 0 10px;",
        "h4": "font-size:15px;font-weight:600;color:#555;margin:14px 0 8px;",
        "p": "margin:0 0 14px;color:#2C2C2C;line-height:1.8;",
        "blockquote": "border-left:3px solid #C96442;background:linear-gradient(135deg,#FFF8F3,#FEFCF9);margin:24px 0;padding:18px 22px;border-radius:0 8px 8px 0;color:#5A4A3A;font-size:14px;line-height:1.8;",
        "ul": "margin:12px 0;padding-left:22px;color:#2C2C2C;",
        "ol": "margin:12px 0;padding-left:22px;color:#2C2C2C;",
        "li": "margin:6px 0;line-height:1.8;",
        "strong": "font-weight:700;color:#1A1A1A;background:linear-gradient(to top,rgba(201,100,66,0.15) 40%,transparent 40%);padding:0 2px;",
        "em": "font-style:italic;color:#8C7A6A;",
        "a": "color:#C96442;text-decoration:none;border-bottom:1px solid rgba(201,100,66,0.3);",
        "hr": "border:none;border-top:1px solid #E8E5E0;margin:28px 0;",
        "code": "background:#F5F0EB;color:#8B5E3C;padding:1px 5px;border-radius:3px;font-size:0.88em;",
        "pre": "background:#2D2A26;color:#E8E2DA;padding:16px 20px;border-radius:8px;overflow-x:auto;margin:20px 0;font-size:14px;",
        "img": "max-width:100%;height:auto;border-radius:4px;margin:10px 0;",
        "table": "width:100%;border-collapse:collapse;margin:16px 0;font-size:14px;",
        "th": "background:#F5F0EB;font-weight:600;padding:8px 12px;border:1px solid #E8E5E0;text-align:left;color:#1A1A1A;",
        "td": "padding:8px 12px;border:1px solid #E8E5E0;color:#2C2C2C;",
    },
}

_FM_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
_H2_PATTERN = re.compile(r'^##\s+(.+)\s*$', re.MULTILINE)


def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return "0,0,0"
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"{r},{g},{b}"


def build_theme_from_brand_spec(brand_spec_path):
    if not brand_spec_path or not os.path.isfile(brand_spec_path):
        return None

    with open(brand_spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    colors = spec.get("colors", {})
    derived = spec.get("derived", {})
    fonts = spec.get("fonts", {})

    primary = colors.get("primary", "#0F766E")
    accent = colors.get("accent", "#E94560")
    bg = colors.get("bg", "#FAFAFA")
    fg = colors.get("fg", "#1A1A1A")
    muted = colors.get("muted", "#7A7A9E")
    border = colors.get("border", "#E5E7EB")

    primary_rgb = derived.get("primary-rgb", _hex_to_rgb(primary))
    accent_rgb = derived.get("accent-rgb", _hex_to_rgb(accent))

    font_body = fonts.get("body", "-apple-system,BlinkMacSystemFont,'PingFang SC','Noto Sans SC',sans-serif")
    font_display = fonts.get("display", "'Noto Serif SC',Georgia,serif")

    primary_dim = derived.get("primary-dim", f"rgba({primary_rgb},0.08)")
    accent_dim = derived.get("accent-dim", f"rgba({accent_rgb},0.08)")

    theme = {
        "_root": (
            f"max-width:680px;margin:0 auto;padding:24px 16px;"
            f"background:{bg};"
            f"font-family:{font_body};"
            f"font-size:16px;line-height:1.8;color:{fg};"
        ),
        "h1": f"font-family:{font_display};font-size:22px;font-weight:700;color:{fg};margin:36px 0 16px;line-height:1.4;",
        "h2": f"font-size:19px;font-weight:600;color:{fg};margin:36px 0 16px;padding-bottom:8px;border-bottom:1px solid {border};",
        "h3": f"font-size:17px;font-weight:600;color:{primary};margin:20px 0 12px;",
        "p": f"margin:0 0 16px;color:{fg};line-height:1.8;",
        "blockquote": f"border-left:3px solid {primary};background:{primary_dim};margin:28px 0;padding:16px 20px;border-radius:0 10px 10px 0;color:{fg};",
        "ul": f"margin:16px 0;padding-left:24px;color:{fg};",
        "ol": f"margin:16px 0;padding-left:24px;color:{fg};",
        "li": "margin:8px 0;line-height:1.8;",
        "strong": f"font-weight:600;color:{fg};",
        "em": f"font-style:italic;color:{muted};",
        "a": f"color:{primary};text-decoration:none;",
        "hr": f"border:none;border-top:1px solid {border};margin:36px 0;",
        "code": f"background:#2D2A26;color:#E8E2DA;padding:2px 6px;border-radius:4px;font-size:0.9em;",
        "pre": "background:#2D2A26;color:#E8E2DA;padding:16px 20px;border-radius:10px;overflow-x:auto;margin:28px 0;",
        "img": "max-width:100%;height:auto;border-radius:6px;margin:12px 0;",
        "table": f"width:100%;border-collapse:collapse;margin:20px 0;",
        "th": f"background:{primary_dim};font-weight:600;padding:10px 14px;border:1px solid {border};text-align:left;",
        "td": f"padding:10px 14px;border:1px solid {border};color:{fg};",
    }
    return theme


def _extract_frontmatter(md):
    match = _FM_PATTERN.match(md)
    metadata = {"title": "", "author": "", "digest": ""}
    if not match:
        return md, metadata
    body = match.group(1)
    for line in body.split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            metadata[key.strip().lower()] = val.strip()
    return md[match.end():], metadata


def _strip_duplicate_title(md, title):
    if not title:
        return md
    match = _H2_PATTERN.search(md)
    if not match:
        return md
    if match.group(1).strip() == title.strip():
        start = match.start()
        end = match.end()
        while end < len(md) and md[end] == '\n':
            end += 1
            if end - match.end() > 1:
                break
        return md[:start] + md[end:]
    return md


def _inject_bare_tags(html, tag, style):
    if tag in ("hr", "img", "br"):
        pattern = re.compile(rf'<{tag}(\s[^>]*?)?/?>', re.IGNORECASE)
    else:
        pattern = re.compile(rf'<{tag}(\s[^>]*?)?>', re.IGNORECASE)

    def replacer(m):
        full = m.group(0)
        attrs = m.group(1) or ""
        if re.search(r'\bstyle\s*=', attrs, re.IGNORECASE):
            return full
        attrs = attrs.rstrip()
        if attrs:
            return f'<{tag}{attrs} style="{style}">'
        else:
            return f'<{tag} style="{style}">'

    return pattern.sub(replacer, html)


def _style_blockquote_paras(html, theme="essence"):
    bq_p_styles = {
        "claude-warm": "margin:0 0 8px;color:#3D3A36;line-height:1.8;",
        "claude-clean": "margin:0 0 8px;color:#1A1A1A;line-height:1.8;",
        "essence": "margin:0 0 6px;color:#5A4A3A;line-height:1.8;",
    }
    bq_p_style = bq_p_styles.get(theme, bq_p_styles["essence"])

    result = []
    i = 0
    while i < len(html):
        bq_start = html.find("<blockquote", i)
        if bq_start == -1:
            result.append(html[i:])
            break

        result.append(html[i:bq_start])

        depth = 1
        j = html.find(">", bq_start) + 1
        while depth > 0 and j < len(html):
            next_open = html.find("<blockquote", j)
            next_close = html.find("</blockquote>", j)
            if next_close == -1:
                break
            if next_open != -1 and next_open < next_close:
                depth += 1
                j = next_open + 12
            else:
                depth -= 1
                if depth == 0:
                    inner = html[bq_start:next_close + 13]
                    inner = _inject_bare_tags(inner, "p", bq_p_style)
                    result.append(inner)
                    i = next_close + 13
                    break
                j = next_close + 13

        if depth > 0:
            result.append(html[bq_start:])
            break

    return "".join(result)


def _style_pre_code(html, pre_code_style="background:none;padding:0;color:inherit;font-size:inherit;"):
    result = []
    i = 0
    while i < len(html):
        pre_start = html.find("<pre", i)
        if pre_start == -1:
            result.append(html[i:])
            break

        result.append(html[i:pre_start])

        pre_open_end = html.find(">", pre_start) + 1
        pre_close = html.find("</pre>", pre_open_end)
        if pre_close == -1:
            result.append(html[pre_start:])
            break

        inner = html[pre_open_end:pre_close]
        inner = _inject_bare_tags(inner, "code", pre_code_style)

        result.append(html[pre_start:pre_open_end])
        result.append(inner)
        result.append(html[pre_close:pre_close + 6])
        i = pre_close + 6

    return "".join(result)


def _inject_intro_decoration(html, theme="essence"):
    intro_themes = {
        "essence": {
            "wrapper": "margin:0 0 28px;padding:20px 24px;border-radius:8px;background:linear-gradient(135deg,#FFF8F3 0%,#FEFCF9 100%);border-left:3px solid #C96442;position:relative;",
            "icon": "position:absolute;top:-8px;left:12px;font-size:28px;color:#C96442;font-family:Georgia,serif;line-height:1;",
            "text": "margin:0;color:#5A4A3A;font-size:14px;line-height:1.8;letter-spacing:0.02em;",
        },
        "claude-warm": {
            "wrapper": "margin:0 0 28px;padding:20px 24px;border-radius:8px;background:linear-gradient(135deg,#FEFCF9 0%,#FAF7F2 100%);border-left:3px solid #C96442;position:relative;",
            "icon": "position:absolute;top:-8px;left:12px;font-size:28px;color:#C96442;font-family:Georgia,serif;line-height:1;",
            "text": "margin:0;color:#3D3A36;font-size:14px;line-height:1.8;",
        },
        "claude-clean": {
            "wrapper": "margin:0 0 28px;padding:20px 24px;border-radius:6px;background:#FEFEFE;border-left:3px solid #C96442;position:relative;",
            "icon": "position:absolute;top:-8px;left:12px;font-size:28px;color:#C96442;font-family:Georgia,serif;line-height:1;",
            "text": "margin:0;color:#1A1A1A;font-size:14px;line-height:1.8;",
        },
    }

    intro_cfg = intro_themes.get(theme, intro_themes["essence"])

    first_bq = re.search(r'<blockquote\s+style="[^"]*">([\s\S]*?)</blockquote>', html)
    if not first_bq:
        return html

    bq_content = first_bq.group(1)
    bq_full = first_bq.group(0)

    text_only = re.sub(r'<[^>]+>', '', bq_content).strip()
    if len(text_only) > 120:
        return html

    is_first_significant = html.find(bq_full) < len(html) * 0.25
    if not is_first_significant:
        return html

    intro_html = (
        f'<section style="{intro_cfg["wrapper"]}">'
        f'<p style="{intro_cfg["text"]}">{bq_content}</p>'
        f'</section>'
    )

    html = html.replace(bq_full, intro_html, 1)
    return html


def _compress_html(html, char_limit=20000):
    html = re.sub(r'<!--[\s\S]*?-->', '', html)

    def _compact_style(m):
        val = re.sub(r'\s+', ' ', m.group(1)).strip()
        return f'style="{val}"'
    html = re.sub(r'style="([\s\S]*?)"', _compact_style, html)
    html = re.sub(r'[ \t]+', ' ', html)
    html = re.sub(r'\n\s*\n', '\n', html)
    html = re.sub(r'>\s+<', '><', html)
    html = html.strip()

    if len(html) <= char_limit:
        return html

    html = _deduplicate_styles(html)

    if len(html) <= char_limit:
        return html

    html = _strip_redundant_styles(html)

    return html


def _deduplicate_styles(html):
    style_map = {}
    counter = [0]

    def _short_class():
        n = counter[0]
        counter[0] += 1
        chars = "abcdefghijklmnopqrstuvwxyz"
        if n < 26:
            return f"c{chars[n]}"
        return f"c{chars[n // 26 - 1]}{chars[n % 26]}"

    def _replace_style(m):
        style_val = m.group(1)
        if style_val not in style_map:
            style_map[style_val] = _short_class()
        cls = style_map[style_val]
        return f'class="{cls}"'

    new_html = re.sub(r'style="([^"]*)"', _replace_style, html)

    if not style_map:
        return html

    css_lines = []
    for style_val, cls in style_map.items():
        css_lines.append(f".{cls}{{{style_val}}}")
    css_block = "<style>" + "".join(css_lines) + "</style>"

    body_start = new_html.find("<article>")
    if body_start != -1:
        insert_pos = body_start + len("<article>")
        new_html = new_html[:insert_pos] + css_block + new_html[insert_pos:]
    else:
        new_html = css_block + new_html

    return new_html


def _strip_redundant_styles(html):
    html = re.sub(r'style="[^"]*margin:0[^"]*"', '', html)
    html = re.sub(r'style="[^"]*padding:0[^"]*"', '', html)
    html = re.sub(r'style="[^"]*border:none[^"]*"', '', html)
    html = re.sub(r'\s+style=""', '', html)
    return html


def apply_inline_styles(html, theme="essence", brand_spec_path=None):
    if brand_spec_path:
        custom_theme = build_theme_from_brand_spec(brand_spec_path)
        if custom_theme:
            styles = custom_theme
        else:
            styles = THEMES.get(theme, THEMES["essence"])
    else:
        styles = THEMES.get(theme, THEMES["essence"])

    html = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", html, flags=re.IGNORECASE)
    html = re.sub(r'\s+class="[^"]*"', "", html)

    for tag, style in styles.items():
        if tag.startswith("_"):
            continue
        html = _inject_bare_tags(html, tag, style)

    html = _style_blockquote_paras(html, theme)
    html = _style_pre_code(html)
    html = _inject_intro_decoration(html, theme)

    return html


def _reorder_images_for_chapters(md_content):
    lines = md_content.split('\n')
    headings = []
    images = []
    image_line_indices = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'^#{1,3}\s+', stripped):
            headings.append(i)
        if re.match(r'^!\[.*?\]\(.*?\)', stripped):
            images.append(i)
            image_line_indices.append(i)

    if not headings or not images:
        return md_content

    heading_images = {}
    for img_idx in images:
        best_heading = None
        for h_idx in headings:
            if h_idx < img_idx:
                best_heading = h_idx
            else:
                break
        if best_heading is not None:
            heading_images.setdefault(best_heading, []).append(img_idx)

    result_lines = list(lines)
    insertions = {}
    for h_idx, img_indices in heading_images.items():
        img_blocks = []
        for img_idx in sorted(img_indices):
            img_blocks.append(result_lines[img_idx])
        insertions[h_idx] = img_blocks

    for img_idx in sorted(image_line_indices, reverse=True):
        result_lines[img_idx] = None

    final_lines = []
    for i, line in enumerate(result_lines):
        if line is not None:
            final_lines.append(line)
        if i in insertions:
            for img_line in insertions[i]:
                if img_line not in final_lines:
                    final_lines.append(img_line)

    return '\n'.join(final_lines)


def _prioritize_gifs(md_content, min_text_gap=8):
    lines = md_content.split('\n')
    total_lines = len(lines)
    threshold = int(total_lines * 0.3)

    gif_lines = []
    gif_indices = []
    png_indices = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'^!\[.*?\]\(.*?\.gif\)', stripped, re.IGNORECASE):
            gif_lines.append(line)
            gif_indices.append(i)
        elif re.match(r'^!\[.*?\]\(.*?\)', stripped):
            png_indices.append(i)

    if not gif_lines:
        return md_content

    need_move = [idx for idx in gif_indices if idx > threshold]
    if not need_move:
        return md_content

    def _count_text_lines_between(a, b):
        count = 0
        lo, hi = min(a, b), max(a, b)
        for j in range(lo + 1, hi):
            if j < len(lines) and lines[j].strip() and not re.match(r'^!\[.*?\]\(.*?\)', lines[j].strip()) and not re.match(r'^#{1,3}\s+', lines[j].strip()):
                count += 1
        return count

    first_heading = None
    for i, line in enumerate(lines):
        if re.match(r'^#{1,3}\s+', line.strip()):
            first_heading = i
            break

    best_pos = None
    if first_heading is not None:
        search_start = first_heading + 2
    else:
        search_start = min(5, threshold)

    for pos in range(search_start, threshold + 1):
        if png_indices and min(abs(pos - pi) for pi in png_indices) < min_text_gap:
            continue
        nearby_text = sum(1 for j in range(max(0, pos - min_text_gap), min(len(lines), pos + min_text_gap))
                          if lines[j].strip() and not re.match(r'^!\[.*?\]\(.*?\)', lines[j].strip()))
        if nearby_text >= min_text_gap:
            best_pos = pos
            break

    if best_pos is None:
        best_pos = search_start

    for idx in sorted(need_move, reverse=True):
        lines[idx] = None

    result = []
    inserted = False
    for i, line in enumerate(lines):
        if line is not None:
            result.append(line)
        if not inserted and i >= best_pos:
            for gl in gif_lines:
                result.append(gl)
            inserted = True

    return '\n'.join(result)


def _limit_references(md_content, min_refs=3, max_refs=5):
    ref_section_pattern = re.compile(
        r'^(#{1,3}\s+(?:参考文献|参考资料|References?))\s*$',
        re.MULTILINE
    )
    match = ref_section_pattern.search(md_content)
    if not match:
        return md_content

    section_start = match.start()
    before_section = md_content[:section_start]
    section_header = match.group(0)
    after_header = md_content[match.end():]

    next_heading = re.search(r'^#{1,3}\s+', after_header, re.MULTILINE)
    if next_heading:
        ref_body = after_header[:next_heading.start()]
        after_section = after_header[next_heading.start():]
    else:
        ref_body = after_header
        after_section = ""

    ref_lines = ref_body.split('\n')
    kept = []
    count = 0
    for line in ref_lines:
        stripped = line.strip()
        if not stripped:
            kept.append(line)
            continue
        if re.match(r'^[\-\*\d]+[.\s]', stripped) or re.match(r'^\[\d+\]', stripped):
            count += 1
            if count <= max_refs:
                kept.append(line)
        else:
            kept.append(line)

    if count < min_refs:
        return md_content

    new_ref_body = '\n'.join(kept)
    return before_section + section_header + '\n' + new_ref_body + '\n' + after_section


def _limit_images(md_content, max_png=6, max_gif=1):
    lines = md_content.split('\n')
    png_count = 0
    gif_count = 0
    result = []

    for line in lines:
        stripped = line.strip()
        img_match = re.match(r'^!\[.*?\]\(.*?(\.\w+)\)', stripped)
        if img_match:
            ext = img_match.group(1).lower()
            if ext == '.gif':
                if gif_count < max_gif:
                    gif_count += 1
                    result.append(line)
            elif ext == '.png':
                if png_count < max_png:
                    png_count += 1
                    result.append(line)
            else:
                if png_count < max_png:
                    png_count += 1
                    result.append(line)
        else:
            result.append(line)

    return '\n'.join(result)


def convert_markdown(file_path="", markdown="", theme="essence",
                     title="", author="", digest="", brand_spec_path=None):
    if file_path:
        with open(file_path, encoding="utf-8") as f:
            markdown = f.read()

    md_content, metadata = _extract_frontmatter(markdown)

    effective_title = title or metadata.get("title", "")
    if effective_title:
        md_content = _strip_duplicate_title(md_content, effective_title)

    md_content = _prioritize_gifs(md_content)
    md_content = _reorder_images_for_chapters(md_content)
    md_content = _limit_references(md_content)
    md_content = _limit_images(md_content)

    md_parser = MarkdownIt("default", {"html": True})
    body_html = md_parser.render(md_content)

    styled_html = apply_inline_styles(body_html, theme, brand_spec_path)

    bg_color = "#FAFAFA"
    theme_styles = THEMES.get(theme, THEMES["essence"])
    if brand_spec_path:
        custom_theme = build_theme_from_brand_spec(brand_spec_path)
        if custom_theme:
            theme_styles = custom_theme
    root_style = theme_styles.get("_root", "")
    bg_match = re.search(r'background:([^;]+)', root_style)
    if bg_match:
        bg_color = bg_match.group(1).strip()

    full_html = _compress_html(styled_html)
    full_html = (
        f'<section style="max-width:680px;margin:0 auto;padding:24px 16px;background:{bg_color};">'
        '<article>'
        f'{full_html}'
        '</article>'
        '</section>'
    )

    return {
        "success": True,
        "html": full_html,
        "title": metadata.get("title", "") or title,
        "author": metadata.get("author", "") or author,
        "digest": metadata.get("digest", "") or digest,
    }


def inspect_article(file_path):
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    _, metadata = _extract_frontmatter(content)
    title = metadata.get("title", "") or "未命名文章"
    author = metadata.get("author", "")
    digest = metadata.get("digest", "")

    checks = []
    if not title or title == "未命名文章":
        checks.append({"level": "warning", "message": "标题未设置"})
    if len(title) > 64:
        checks.append({"level": "warning", "message": f"标题超长 ({len(title)}/64)"})
    if not digest:
        checks.append({"level": "info", "message": "摘要未设置，将自动从正文生成"})

    has_error = any(c["level"] == "error" for c in checks)
    has_warning = any(c["level"] == "warning" for c in checks)
    readiness = "error" if has_error else ("warning" if has_warning else "ready")

    return {
        "metadata": {"title": title, "author": author, "digest": digest},
        "readiness": readiness,
        "checks": checks,
    }
