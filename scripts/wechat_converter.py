"""
本质工坊 · Markdown → 微信公众号 HTML 转换器
基于 md2wechat-py 最新代码，自包含无 wechat-pub 依赖

功能：
- Markdown → 微信兼容 HTML（纯内联样式，无 <style> 标签）
- 3 套 Claude 主题（warm / clean / dark）
- Frontmatter 解析
- 标题去重
- HTML 压缩（控制在 20000 字符限制内）
- 文章检查（inspect）
"""

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
        "h1": "font-size:22px;font-weight:700;color:#1F1D1A;margin:36px 0 16px;",
        "h2": "font-size:19px;font-weight:600;color:#1F1D1A;margin:36px 0 16px;padding-bottom:8px;border-bottom:1px solid #E8E2DA;",
        "h3": "font-size:17px;font-weight:600;color:#1F1D1A;margin:20px 0 12px;",
        "p": "margin:0 0 16px;",
        "blockquote": "border-left:3px solid #C96442;background:#FEFCF9;margin:28px 0;padding:16px 20px;border-radius:0 10px 10px 0;",
        "ul": "margin:16px 0;padding-left:24px;",
        "ol": "margin:16px 0;padding-left:24px;",
        "li": "margin:8px 0;",
        "strong": "font-weight:600;",
        "em": "font-style:italic;",
        "a": "color:#C96442;text-decoration:none;",
        "hr": "border:none;border-top:1px solid #E8E2DA;margin:36px 0;",
        "code": "background:#2D2A26;color:#E8E2DA;padding:2px 6px;border-radius:4px;font-size:0.9em;",
        "pre": "background:#2D2A26;color:#E8E2DA;padding:16px 20px;border-radius:10px;overflow-x:auto;margin:28px 0;",
        "img": "max-width:100%;height:auto;border-radius:6px;margin:12px 0;",
        "table": "width:100%;border-collapse:collapse;margin:20px 0;",
        "th": "background:#F5E6DC;font-weight:600;padding:10px 14px;border:1px solid #E8E2DA;",
        "td": "padding:10px 14px;border:1px solid #E8E2DA;",
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
        "strong": "font-weight:600;color:#1A1A1A;",
        "em": "font-style:italic;color:#9B9B9B;",
        "a": "color:#C96442;text-decoration:none;border-bottom:1px solid #FBF4EF;",
        "hr": "border:none;border-top:1px solid #ECECEC;margin:32px 0;",
        "code": "background:#1F1F1F;color:#E0E0E0;padding:2px 6px;border-radius:4px;font-size:0.9em;",
        "pre": "background:#1F1F1F;color:#E0E0E0;padding:16px 20px;border-radius:8px;overflow-x:auto;margin:24px 0;",
        "img": "max-width:100%;height:auto;border-radius:4px;margin:10px 0;",
        "table": "width:100%;border-collapse:collapse;margin:18px 0;font-size:14px;",
        "th": "background:#FBF4EF;color:#1A1A1A;font-weight:600;padding:8px 12px;border:1px solid #ECECEC;text-align:left;",
        "td": "padding:8px 12px;border:1px solid #ECECEC;color:#37352F;",
    },
    "claude-dark": {
        "_root": (
            "max-width:680px;margin:0 auto;padding:24px 16px;"
            "background:#1A1816;"
            "font-family:-apple-system,BlinkMacSystemFont,"
            '"PingFang SC","Noto Sans SC",sans-serif;'
            "font-size:16px;line-height:1.8;letter-spacing:0.01em;color:#D4CFC8;"
        ),
        "h1": "font-size:22px;font-weight:700;color:#F0EBE3;margin:36px 0 16px;line-height:1.4;",
        "h2": "font-size:19px;font-weight:600;color:#F0EBE3;margin:36px 0 16px;line-height:1.45;padding-bottom:8px;border-bottom:1px solid #3D3A36;",
        "h3": "font-size:17px;font-weight:600;color:#F0EBE3;margin:20px 0 12px;",
        "h4": "font-size:16px;font-weight:600;color:#F0EBE3;margin:16px 0 8px;",
        "p": "margin:0 0 16px;color:#D4CFC8;line-height:1.8;",
        "blockquote": "border-left:3px solid #D4896C;background:#242120;margin:28px 0;padding:16px 20px;border-radius:0 10px 10px 0;color:#F0EBE3;",
        "ul": "margin:16px 0;padding-left:24px;color:#D4CFC8;",
        "ol": "margin:16px 0;padding-left:24px;color:#D4CFC8;",
        "li": "margin:8px 0;line-height:1.8;",
        "strong": "font-weight:600;color:#F0EBE3;",
        "em": "font-style:italic;color:#8C8278;",
        "a": "color:#D4896C;text-decoration:none;border-bottom:1px solid #3D2E24;",
        "hr": "border:none;border-top:1px solid #3D3A36;margin:36px 0;",
        "code": "background:#0F0E0D;color:#D4CFC8;padding:2px 6px;border-radius:4px;font-size:0.9em;",
        "pre": "background:#0F0E0D;color:#D4CFC8;padding:16px 20px;border-radius:10px;overflow-x:auto;margin:28px 0;",
        "img": "max-width:100%;height:auto;border-radius:6px;margin:12px 0;",
        "table": "width:100%;border-collapse:collapse;margin:20px 0;font-size:15px;",
        "th": "background:#3D2E24;color:#F0EBE3;font-weight:600;padding:10px 14px;border:1px solid #3D3A36;text-align:left;",
        "td": "padding:10px 14px;border:1px solid #3D3A36;color:#D4CFC8;",
    },
}

_FM_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
_H2_PATTERN = re.compile(r'^##\s+(.+)\s*$', re.MULTILINE)


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


def _style_blockquote_paras(html, theme="claude-warm"):
    bq_p_styles = {
        "claude-warm": "margin:0 0 8px;color:#3D3A36;line-height:1.8;",
        "claude-clean": "margin:0 0 8px;color:#1A1A1A;line-height:1.8;",
        "claude-dark": "margin:0 0 8px;color:#F0EBE3;line-height:1.8;",
    }
    bq_p_style = bq_p_styles.get(theme, bq_p_styles["claude-warm"])

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


def _compress_html(html):
    html = re.sub(r'<!--[\s\S]*?-->', '', html)

    def _compact_style(m):
        val = re.sub(r'\s+', ' ', m.group(1)).strip()
        return f'style="{val}"'
    html = re.sub(r'style="([\s\S]*?)"', _compact_style, html)
    html = re.sub(r'[ \t]+', ' ', html)
    html = re.sub(r'\n\s*\n', '\n', html)
    html = re.sub(r'>\s+<', '><', html)
    return html.strip()


def apply_inline_styles(html, theme="claude-warm"):
    styles = THEMES.get(theme, THEMES["claude-warm"])

    html = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", html, flags=re.IGNORECASE)
    html = re.sub(r'\s+class="[^"]*"', "", html)

    for tag, style in styles.items():
        if tag.startswith("_"):
            continue
        html = _inject_bare_tags(html, tag, style)

    html = _style_blockquote_paras(html, theme)
    html = _style_pre_code(html)

    return html


def convert_markdown(file_path="", markdown="", theme="claude-warm",
                     title="", author="", digest=""):
    if file_path:
        with open(file_path, encoding="utf-8") as f:
            markdown = f.read()

    md_content, metadata = _extract_frontmatter(markdown)

    effective_title = title or metadata.get("title", "")
    if effective_title:
        md_content = _strip_duplicate_title(md_content, effective_title)

    md_parser = MarkdownIt("default", {"html": True})
    body_html = md_parser.render(md_content)

    styled_html = apply_inline_styles(body_html, theme)

    full_html = _compress_html(styled_html)
    full_html = (
        '<section style="max-width:680px;margin:0 auto;padding:24px 16px;background:#FAF7F2;">'
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
