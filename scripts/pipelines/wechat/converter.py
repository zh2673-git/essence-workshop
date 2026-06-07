"""
本质工坊 · Markdown → 微信公众号 HTML 转换器

核心原则：微信草稿箱会剥离 <style> 标签和 class 属性，
因此所有样式必须 100% 内联，绝不使用 CSS 类或 <style> 块。

功能：
- Markdown → 微信兼容 HTML（纯内联样式）
- 3 套主题（essence / claude-warm / claude-clean）
- brand-spec.json 动态主题生成
- Frontmatter 解析
- 标题去重
- HTML 压缩（控制在 20000 字符限制内，通过精简属性值而非提取 CSS 类）
- 文章检查（inspect）
"""

import json
import os
import re
from html.parser import HTMLParser

from markdown_it import MarkdownIt


# ─── 主题定义 ───────────────────────────────────────────────

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
        "p": "margin:0 0 28px;color:#3D3A36;line-height:1.8;",
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
        "p": "margin:0 0 28px;color:#37352F;line-height:1.8;",
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
        "h1": "font-size:20px;font-weight:700;margin:32px 0 20px;",
        "h2": "font-size:17px;font-weight:600;margin:28px 0 16px;padding-bottom:6px;border-bottom:1px solid #E8E5E0;",
        "h3": "font-weight:600;margin:20px 0 10px;",
        "h4": "font-weight:600;margin:14px 0 8px;",
        "p": "margin-bottom:28px;",
        "blockquote": "border-left:3px solid #C96442;background:#FFF8F3;padding:18px 22px;margin:24px 0;",
        "ul": "padding-left:22px;",
        "ol": "padding-left:22px;",
        "li": "margin:6px 0;",
        "strong": "background:linear-gradient(to top,rgba(201,100,66,0.15) 40%,transparent 40%);",
        "em": "font-style:italic;",
        "a": "color:#C96442;",
        "hr": "border:none;border-top:1px solid #E8E5E0;margin:32px 0 28px;",
        "code": "background:#F5F0EB;padding:1px 5px;font-size:0.88em;",
        "pre": "background:#F5F0EB;padding:16px 20px;overflow-x:auto;margin:20px 0;font-size:14px;",
        "img": "max-width:100%;height:auto;",
        "table": "width:100%;border-collapse:collapse;margin:16px 0;font-size:14px;",
        "th": "background:#F5F0EB;padding:8px 12px;border:1px solid #E8E5E0;text-align:left;",
        "td": "padding:8px 12px;border:1px solid #E8E5E0;",
    },
}

_FM_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
_H2_PATTERN = re.compile(r'^##\s+(.+)\s*$', re.MULTILINE)


# ─── 品牌主题生成 ──────────────────────────────────────────

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
        "p": f"margin:0 0 28px;color:{fg};line-height:1.8;",
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


# ─── Frontmatter 解析 ──────────────────────────────────────

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


# ─── HTML 树遍历式样式注入 ─────────────────────────────────
# 核心改动：用 HTMLParser 逐节点遍历，精准注入内联 style，
# 不依赖正则，不产生 <style> 标签或 class 属性。

class _StyleInjector(HTMLParser):
    """遍历 HTML 节点，为每个目标标签注入内联 style 属性。

    微信草稿箱会剥离 <style> 标签和 class 属性，
    因此所有样式必须 100% 内联。
    """

    # 自闭合标签
    VOID_TAGS = frozenset([
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr',
    ])

    def __init__(self, styles, blockquote_p_style, pre_code_style, intro_config):
        super().__init__(convert_charrefs=False)
        self.styles = styles              # tag -> inline style string
        self.bq_p_style = blockquote_p_style
        self.pre_code_style = pre_code_style
        self.intro_config = intro_config

        self.output = []
        self._tag_stack = []              # 追踪嵌套的标签
        self._in_blockquote = 0           # blockquote 嵌套深度
        self._in_pre = False              # 是否在 <pre> 内
        self._first_bq_handled = False    # 引言装饰是否已处理
        self._bq_buffer = []              # 缓存第一个 blockquote 用于引言装饰
        self._buffering_bq = False        # 是否正在缓存 blockquote

    def _current_tag(self):
        return self._tag_stack[-1] if self._tag_stack else None

    def _get_style(self, tag):
        """获取标签对应的内联样式，考虑上下文（blockquote 内的 p、pre 内的 code）。"""
        if tag == 'p' and self._in_blockquote > 0:
            return self.bq_p_style
        if tag == 'code' and self._in_pre:
            return self.pre_code_style
        return self.styles.get(tag)

    def _build_tag(self, tag, attrs, self_closing=False):
        """重建标签 HTML，注入 style 属性。"""
        style = self._get_style(tag)

        # 过滤已有属性
        filtered = []
        has_style = False
        for k, v in attrs:
            if k == 'style':
                has_style = True
                if style:
                    # 已有 style 则追加，不覆盖
                    filtered.append(('style', v.rstrip(';') + ';' + style))
                else:
                    filtered.append(('style', v))
            elif k == 'class':
                # 微信不支持 class，直接丢弃
                pass
            else:
                filtered.append((k, v))

        if not has_style and style:
            filtered.append(('style', style))

        # 构建属性字符串
        attr_str = ''
        for k, v in filtered:
            if v is None:
                attr_str += f' {k}'
            else:
                attr_str += f' {k}="{v}"'

        if tag in self.VOID_TAGS:
            return f'<{tag}{attr_str} />'
        elif self_closing:
            return f'<{tag}{attr_str}></{tag}>'
        else:
            return f'<{tag}{attr_str}>'

    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()

        # 追踪 blockquote 嵌套
        if tag_lower == 'blockquote':
            self._in_blockquote += 1
            # 检查是否需要引言装饰（第一个 blockquote，且在文章前 25%）
            if (self._in_blockquote == 1
                    and not self._first_bq_handled
                    and self.intro_config
                    and not self._buffering_bq):
                self._buffering_bq = True
                self._bq_buffer = []
                # 不直接输出，开始缓存
                self._bq_buffer.append(self._build_tag(tag_lower, attrs))
                self._tag_stack.append(tag_lower)
                return

        # 追踪 pre
        if tag_lower == 'pre':
            self._in_pre = True

        self._tag_stack.append(tag_lower)
        rendered = self._build_tag(tag_lower, attrs)

        if self._buffering_bq:
            self._bq_buffer.append(rendered)
        else:
            self.output.append(rendered)

    def handle_endtag(self, tag):
        tag_lower = tag.lower()

        if tag_lower == 'blockquote':
            if self._buffering_bq and self._in_blockquote == 1:
                # 结束引言缓存，生成装饰后的引言
                self._bq_buffer.append(f'</{tag_lower}>')
                bq_inner = ''.join(self._bq_buffer)
                # 提取 blockquote 内部内容（去掉开闭标签）
                inner_start = bq_inner.find('>')
                inner_end = bq_inner.rfind('</')
                if inner_start != -1 and inner_end != -1:
                    inner_content = bq_inner[inner_start + 1:inner_end]
                else:
                    inner_content = bq_inner

                # 生成引言装饰 HTML
                cfg = self.intro_config
                intro_html = (
                    f'<section style="{cfg["wrapper"]}">'
                    f'<p style="{cfg["text"]}">{inner_content}</p>'
                    f'</section>'
                )
                self.output.append(intro_html)
                self._buffering_bq = False
                self._first_bq_handled = True
                self._bq_buffer = []
                self._in_blockquote -= 1
                if self._tag_stack and self._tag_stack[-1] == tag_lower:
                    self._tag_stack.pop()
                return

            self._in_blockquote = max(0, self._in_blockquote - 1)

        if tag_lower == 'pre':
            self._in_pre = False

        if self._tag_stack and self._tag_stack[-1] == tag_lower:
            self._tag_stack.pop()

        closing = f'</{tag_lower}>'
        if self._buffering_bq:
            self._bq_buffer.append(closing)
        else:
            self.output.append(closing)

    def handle_startendtag(self, tag, attrs):
        tag_lower = tag.lower()
        rendered = self._build_tag(tag_lower, attrs, self_closing=True)
        if self._buffering_bq:
            self._bq_buffer.append(rendered)
        else:
            self.output.append(rendered)

    def handle_data(self, data):
        if self._buffering_bq:
            self._bq_buffer.append(data)
        else:
            self.output.append(data)

    def handle_entityref(self, name):
        text = f'&{name};'
        if self._buffering_bq:
            self._bq_buffer.append(text)
        else:
            self.output.append(text)

    def handle_charref(self, name):
        text = f'&#{name};'
        if self._buffering_bq:
            self._bq_buffer.append(text)
        else:
            self.output.append(text)

    def handle_comment(self, data):
        pass  # 丢弃注释

    def get_result(self):
        return ''.join(self.output)


def _get_blockquote_p_style(theme):
    styles = {
        "claude-warm": "margin:0 0 8px;line-height:1.8;",
        "claude-clean": "margin:0 0 8px;line-height:1.8;",
        "essence": "margin:0 0 6px;line-height:1.8;",
    }
    return styles.get(theme, styles["essence"])


def _get_intro_config(theme):
    """返回引言装饰配置，如果不需要引言装饰则返回 None。"""
    configs = {
        "essence": {
            "wrapper": "margin:0 0 28px;padding:20px 24px;border-left:3px solid #C96442;background:#FFF8F3;",
            "text": "margin:0;line-height:1.8;",
        },
        "claude-warm": {
            "wrapper": "margin:0 0 28px;padding:20px 24px;border-left:3px solid #C96442;background:#FEFCF9;",
            "text": "margin:0;line-height:1.8;",
        },
        "claude-clean": {
            "wrapper": "margin:0 0 28px;padding:20px 24px;border-left:3px solid #C96442;background:#FEFEFE;",
            "text": "margin:0;line-height:1.8;",
        },
    }
    return configs.get(theme, configs["essence"])


def apply_inline_styles(html, theme="essence", brand_spec_path=None):
    """将主题样式注入 HTML，100% 内联，不使用 <style> 或 class。"""
    if brand_spec_path:
        custom_theme = build_theme_from_brand_spec(brand_spec_path)
        styles = custom_theme if custom_theme else THEMES.get(theme, THEMES["essence"])
    else:
        styles = THEMES.get(theme, THEMES["essence"])

    # 清理已有的 <style> 和 class（来自 markdown_it 或其他来源）
    html = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", html, flags=re.IGNORECASE)

    # 构建不含 _root 的样式映射
    tag_styles = {k: v for k, v in styles.items() if not k.startswith("_")}

    bq_p_style = _get_blockquote_p_style(theme)
    pre_code_style = "background:none;padding:0;color:inherit;font-size:inherit;"
    intro_config = _get_intro_config(theme)

    injector = _StyleInjector(tag_styles, bq_p_style, pre_code_style, intro_config)
    injector.feed(html)
    return injector.get_result()


# ─── HTML 压缩 ─────────────────────────────────────────────
# 核心原则：绝不使用 <style> 标签或 class。
# 两阶段策略：基础压缩（始终执行）→ 紧凑模式（超限时一步到位）

# 从外层 section 继承的属性，子元素无需重复声明
_INHERITED_PROPS_CLEAN = [
    'color:#37352F', 'color:#2C2C2C', 'color:#3D3A36', 'color:#1A1A1A',
    'color:#1F1D1A', 'color:#444', 'color:#555',
    'line-height:1.8',
]

# strong 半高亮：gradient 简化映射（微信不支持 box-shadow，必须保留 gradient）
# 策略：缩短 gradient 参数（0.15→.15, transparent→transparent 等）
_GRADIENT_SHORTEN = [
    # essence: rgba(201,100,66,0.15) → rgba(201,100,66,.15)
    (
        'background:linear-gradient(to top,rgba(201,100,66,0.15) 40%,transparent 40%)',
        'background:linear-gradient(to top,rgba(201,100,66,.15) 40%,transparent 40%)',
    ),
    # claude-warm
    (
        'background:linear-gradient(to top,rgba(212,118,58,0.18) 40%,transparent 40%)',
        'background:linear-gradient(to top,rgba(212,118,58,.18) 40%,transparent 40%)',
    ),
    # claude-clean
    (
        'background:linear-gradient(to top,rgba(120,140,200,0.12) 40%,transparent 40%)',
        'background:linear-gradient(to top,rgba(120,140,200,.12) 40%,transparent 40%)',
    ),
]

# 引言 section 渐变背景 → 纯色（微信渲染差异极小）
# 注意：essence 主题已直接使用纯色，此处仅保留 warm 的映射
_INTRO_GRADIENT_TO_SOLID = [
    ('background:linear-gradient(135deg,#FEFCF9 0%,#FAF7F2 100%)', 'background:#FEFCF9'),
]


def _compress_html(html, char_limit=20000):
    """压缩 HTML，确保不超过字符限制，绝不使用 <style> 或 class。

    两阶段策略：
    1. 基础压缩（始终执行）：移除注释、精简空白、移除继承/零值属性
    2. 紧凑模式（超限时一步到位）：gradient参数简化、简化装饰、移除非核心样式

    注意：publish.py 会在上传图片后将本地路径替换为 CDN URL，
    本地路径约 25 字符，CDN URL 约 150 字符，每张图多约 125 字符。
    7 张图共多约 875 字符，需要预留空间。
    """
    # 预留 CDN URL 替换空间
    img_count = len(re.findall(r'<img[^>]+src="[^h][^t]', html))
    cdn_overhead = img_count * 130
    effective_limit = char_limit - cdn_overhead

    # ── 阶段一：基础压缩（始终执行）──

    # 移除 HTML 注释
    html = re.sub(r'<!--[\s\S]*?-->', '', html)

    # 精简 style 属性值中的多余空白
    def _compact_style(m):
        val = re.sub(r'\s+', ' ', m.group(1)).strip()
        return f'style="{val}"'
    html = re.sub(r'style="([\s\S]*?)"', _compact_style, html)

    # 精简标签间空白
    html = re.sub(r'[ \t]+', ' ', html)
    html = re.sub(r'\n\s*\n', '\n', html)
    html = re.sub(r'>\s+<', '><', html)
    html = html.strip()

    # 移除继承属性（color/line-height 与根元素重复）
    html = _remove_inherited_styles(html)

    # 移除零值属性（margin:0 / padding:0 / border:none）
    html = _shorten_styles(html)

    # margin:0 0 Xpx → margin-bottom:Xpx（更短，始终有益）
    html = re.sub(r'margin:0\s+0\s+(\d+)px', r'margin-bottom:\1px', html)
    html = re.sub(r'margin:0\s+(\d+)px\s+0', r'margin-left:\1px', html)

    if len(html) <= effective_limit:
        return html

    # ── 阶段二：紧凑模式（超限时一步到位）──
    # 保留的核心视觉：橙色半高亮(gradient)、段落间距(margin-bottom)、引言块(边框+背景)
    # 移除的非核心：h2装饰线、em/hr/img样式、strong padding、外层包装等
    html = _apply_compact_mode(html)

    return html


def _remove_inherited_styles(html):
    """移除子元素中与外层容器重复的继承属性（如 color、line-height）。"""
    def _clean_style(m):
        prefix = m.group(1) or ''
        style_val = m.group(2)
        suffix = m.group(3) or ''

        # 对于 section/article 保留所有样式
        if prefix and re.search(r'<(section|article)\s*$', prefix, re.IGNORECASE):
            return m.group(0)

        # 移除继承属性
        for prop in _INHERITED_PROPS_CLEAN:
            style_val = style_val.replace(prop + ';', '')
            style_val = style_val.replace(prop, '')

        style_val = re.sub(r';\s*;', ';', style_val)
        style_val = style_val.strip('; ')
        if not style_val:
            return prefix.rstrip() + suffix
        return f'{prefix}style="{style_val}"{suffix}'

    html = re.sub(r'(<[^>]*?)style="([^"]*)"([^>]*?>)', _clean_style, html)
    html = re.sub(r'\s+style=""', '', html)
    return html


def _shorten_styles(html):
    """精简 style 属性值：移除零值属性。"""
    def _clean_style(m):
        prefix = m.group(1) or ''
        style_val = m.group(2)
        suffix = m.group(3) or ''

        if prefix and re.search(r'<(section|article)\s*$', prefix, re.IGNORECASE):
            return m.group(0)

        style_val = re.sub(r'\bmargin:0;', '', style_val)
        style_val = re.sub(r'\bpadding:0;', '', style_val)
        style_val = re.sub(r'\bborder:none;', '', style_val)
        style_val = re.sub(r';\s*;', ';', style_val)
        style_val = style_val.strip('; ')
        if not style_val:
            return prefix.rstrip() + suffix
        return f'{prefix}style="{style_val}"{suffix}'

    html = re.sub(r'(<[^>]*?)style="([^"]*)"([^>]*?>)', _clean_style, html)
    html = re.sub(r'\s+style=""', '', html)
    return html


def _apply_compact_mode(html):
    """紧凑模式：超限时一步到位的样式精简。

    保留的核心视觉（不可删除）：
    - strong 的橙色半高亮（gradient，微信不支持box-shadow）
    - p 的 margin-bottom（段落间距）
    - 引言块（intro section）的边框和背景
    - h2/h3 的 font-size 和 font-weight
    - article 的 padding（左右页边距，防止文章贴边）

    移除的非核心（微信默认合理或视觉影响极小）：
    - strong: gradient参数简化(0.15→.15), 移除 font-weight/padding
    - h2: 移除 border-bottom/padding-bottom/line-height/color
    - h3: 移除 color
    - em/hr/img: 移除全部样式
    - 引言 section: 渐变→纯色, 移除 border-radius/letter-spacing
    - 外层 section 包装（max-width/background），padding 转移到 article
    """
    # 1. strong 半高亮：gradient 参数简化（0.15→.15，每处省1字符）
    for original, shortened in _GRADIENT_SHORTEN:
        html = html.replace(original, shortened)

    # 1b. 限制 strong gradient 数量：均匀分布保留 MAX_HIGHLIGHT 个，其余降级为普通加粗
    # 每个 gradient 约75字符，降级后省约84字符
    MAX_HIGHLIGHT = 20
    total_strongs = len(re.findall(r'<strong\s', html))
    if total_strongs > MAX_HIGHLIGHT:
        step = total_strongs / MAX_HIGHLIGHT  # 如 42/20=2.1，约每2个保留1个
        strong_idx = 0
        # 预计算哪些序号保留gradient（均匀分布）
        keep_indices = set(round(i * step) for i in range(MAX_HIGHLIGHT))
        def _limit_strong_gradient(m):
            nonlocal strong_idx
            keep = strong_idx in keep_indices
            strong_idx += 1
            if keep:
                return m.group(0)
            # 降级：移除整个 style 属性，保留 <strong> 本身的加粗语义
            return m.group(1).rstrip() + m.group(2)
        html = re.sub(r'(<strong\s+)style="[^"]*"([^>]*>)', _limit_strong_gradient, html)

    # 2. 引言 section：渐变背景 → 纯色
    for gradient, solid in _INTRO_GRADIENT_TO_SOLID:
        html = html.replace(gradient, solid)

    # 3. 逐标签精简样式
    def _clean_style(m):
        prefix = m.group(1) or ''
        style_val = m.group(2)
        suffix = m.group(3) or ''

        # section/article 保留所有样式（外层包装另有处理）
        if prefix and re.search(r'<(section|article)\s*$', prefix, re.IGNORECASE):
            return m.group(0)

        # strong：保留 gradient 半高亮，移除 font-weight/padding
        if re.search(r'<strong\s*$', prefix, re.IGNORECASE):
            style_val = re.sub(r'font-weight:[\d]+;?', '', style_val)
            style_val = re.sub(r'padding:0\s*\d+px;?', '', style_val)

        # h2：保留 font-size/font-weight/margin，移除装饰线/行高/颜色
        elif re.search(r'<h2\s*$', prefix, re.IGNORECASE):
            style_val = re.sub(r'padding-bottom:[^;]+;?', '', style_val)
            style_val = re.sub(r'border-bottom:[^;]+;?', '', style_val)
            style_val = re.sub(r'line-height:[^;]+;?', '', style_val)
            style_val = re.sub(r'color:#1A1A1A;?', '', style_val)

        # h3：移除 color（与根色接近）
        elif re.search(r'<h3\s*$', prefix, re.IGNORECASE):
            style_val = re.sub(r'color:#444;?', '', style_val)

        # li：移除 line-height（从 ul/ol 继承）
        elif re.search(r'<li\s*$', prefix, re.IGNORECASE):
            style_val = re.sub(r'line-height:[\d.]+;?', '', style_val)

        # th：移除 font-weight
        elif re.search(r'<th\s*$', prefix, re.IGNORECASE):
            style_val = re.sub(r'font-weight:[\d]+;?', '', style_val)

        # ul/ol：移除 margin（微信默认有间距）
        elif re.search(r'<(ul|ol)\s*$', prefix, re.IGNORECASE):
            style_val = re.sub(r'margin:[^;]+;?', '', style_val)

        # img：移除全部样式（微信默认合理）
        elif re.search(r'<img\s*$', prefix, re.IGNORECASE):
            style_val = ''

        # em：移除全部样式（非核心视觉）
        elif re.search(r'<em\s*$', prefix, re.IGNORECASE):
            style_val = ''

        # hr：移除全部样式（微信默认有分隔线）
        elif re.search(r'<hr\s*$', prefix, re.IGNORECASE):
            style_val = ''

        # 移除 font-size:15px（与根元素相同）
        style_val = re.sub(r'font-size:15px;?', '', style_val)

        # p 的 margin-bottom 保留：段落间距是核心视觉，不可省略

        style_val = re.sub(r';\s*;', ';', style_val)
        style_val = style_val.strip('; ')
        if not style_val:
            return prefix.rstrip() + suffix
        return f'{prefix}style="{style_val}"{suffix}'

    html = re.sub(r'(<[^>]*?)style="([^"]*)"([^>]*?>)', _clean_style, html)
    html = re.sub(r'\s+style=""', '', html)

    # 4. 引言 section：移除 border-radius 和 letter-spacing（非核心装饰）
    html = html.replace('border-radius:8px;', '')
    html = html.replace('letter-spacing:0.02em;', '')

    # 5. gradient 方向简写：to top → 0deg（省4字符/个，微信支持）
    html = html.replace('linear-gradient(to top,', 'linear-gradient(0deg,')

    # 6. p 段落间距简写：margin-bottom:28px → margin:0 0 28px（省3字符/个）
    html = html.replace('margin-bottom:28px', 'margin:0 0 28px')

    # 7. 移除 section 外层包装，但保留页边距到 article 上（微信不需要 max-width/background，但 padding 是核心阅读体验）
    # 注意：只移除 max-width 外层 section，保留引言块等有样式的 section
    html = re.sub(r'<section style="max-width:[^"]*">', '', html)
    # 将 padding 从被移除的 section 转移到 article 上（左右16px页边距，防止文章贴边）
    html = html.replace('<article>', '<article style="padding:0 16px">')
    # 移除末尾的 </section>（外层包装的闭合标签）
    html = re.sub(r'</section>\s*$', '', html)

    return html


# ─── Markdown 预处理 ──────────────────────────────────────

def _distribute_images_evenly(md_content):
    """将图片均匀分布到各章节标题下方，每章节最多一张图。
    
    逻辑：
    1. 按章节（## 标题）分组，收集所有图片
    2. 按章节在文章中的位置比例，等间距分配图片
    3. 每个章节最多放一张图，放在标题下方第一个空行后
    4. 如果图片数 > 章节数，多余的图放在最长的无图章节中
    """
    lines = md_content.split('\n')
    total_lines = len(lines)

    # 收集章节标题行索引（仅 ## 二级标题）
    heading_indices = []
    for i, line in enumerate(lines):
        if re.match(r'^##\s+', line.strip()):
            heading_indices.append(i)

    # 收集图片行索引和内容
    img_indices = []
    img_contents = []
    for i, line in enumerate(lines):
        if re.match(r'^!\[.*?\]\(.*?\)', line.strip()):
            img_indices.append(i)
            img_contents.append(line)

    if not heading_indices or not img_indices:
        return md_content

    num_imgs = len(img_contents)
    num_headings = len(heading_indices)

    # 计算每个章节的行范围（从标题到下一个标题或文末）
    section_ranges = []
    for si, h_idx in enumerate(heading_indices):
        start = h_idx
        end = heading_indices[si + 1] if si + 1 < num_headings else total_lines
        section_ranges.append((start, end))

    # 等间距分配：在章节中均匀选取目标位置
    # 例如 8 张图 6 个章节 → 每章节 1 张，多出 2 张放最长章节
    target_sections = []
    if num_imgs <= num_headings:
        # 图片少于等于章节数：等间距选章节
        step = num_headings / num_imgs
        for k in range(num_imgs):
            target_sections.append(int(k * step))
    else:
        # 图片多于章节数：每章节至少一张，多出的放最长章节
        for k in range(num_headings):
            target_sections.append(k)
        remaining = num_imgs - num_headings
        # 按章节长度排序，最长的多放
        sections_by_len = sorted(range(num_headings),
                                  key=lambda s: section_ranges[s][1] - section_ranges[s][0],
                                  reverse=True)
        for k in range(remaining):
            target_sections.append(sections_by_len[k])

    target_sections.sort()

    # 先移除所有原始图片行
    result_lines = list(lines)
    for idx in sorted(img_indices, reverse=True):
        result_lines[idx] = None

    # 在目标章节标题下方插入图片
    insertions = {}  # heading_index -> [img_line, ...]
    for img_idx_in_list, section_idx in enumerate(target_sections):
        if img_idx_in_list >= num_imgs:
            break
        h_idx = heading_indices[section_idx]
        insertions.setdefault(h_idx, []).append(img_contents[img_idx_in_list])

    final_lines = []
    for i, line in enumerate(result_lines):
        if line is not None:
            final_lines.append(line)
        # 在标题行后插入分配的图片
        if i in insertions:
            for img_line in insertions[i]:
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

    # ── 解析参考文献列表，构建编号→简要描述的映射 ──
    ref_lines = ref_body.split('\n')
    kept = []
    removed_refs = {}  # {编号: 简要描述}
    count = 0
    for line in ref_lines:
        stripped = line.strip()
        if not stripped:
            kept.append(line)
            continue
        ref_match = re.match(r'^\[(\d+)\]\s*(.+)', stripped)
        if ref_match:
            count += 1
            if count <= max_refs:
                kept.append(line)
            else:
                # 超限参考文献：提取简要描述（作者+书名/文章名，截取前20字）
                desc = ref_match.group(2).strip()
                desc = re.sub(r'^\d+\.\s*', '', desc)
                short_desc = desc[:20] + ('…' if len(desc) > 20 else '')
                removed_refs[int(ref_match.group(1))] = short_desc
        elif re.match(r'^[\-\*\d]+[.\s]', stripped):
            count += 1
            if count <= max_refs:
                kept.append(line)
            else:
                short_desc = stripped[:20] + ('…' if len(stripped) > 20 else '')
                removed_refs[count] = short_desc
        else:
            kept.append(line)

    if count < min_refs:
        return md_content

    new_ref_body = '\n'.join(kept)

    # ── 处理正文中超限的引用标记 [N] ──
    # 将 [6], [7] 等替换为行内备注，如（见亚里士多德《形而上学》…）
    def replace_overflow_citation(m):
        num = int(m.group(1))
        if num in removed_refs:
            return f"（见{removed_refs[num]}）"
        elif num > max_refs:
            # 编号不在参考文献列表中（可能被合并），直接删除标记
            return ""
        return m.group(0)  # 保留范围内的引用

    before_section = re.sub(r'\[(\d+)\]', replace_overflow_citation, before_section)

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


# ─── 主转换函数 ─────────────────────────────────────────────

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
    # _distribute_images_evenly 已禁用：该函数会覆盖 Markdown 中手动指定的图片位置，
    # 导致多张图片被重新分配到相邻章节而贴在一起
    # md_content = _distribute_images_evenly(md_content)
    md_content = _limit_references(md_content)
    md_content = _limit_images(md_content)

    md_parser = MarkdownIt("default", {"html": True})
    body_html = md_parser.render(md_content)

    styled_html = apply_inline_styles(body_html, theme, brand_spec_path)

    # 获取背景色
    theme_styles = THEMES.get(theme, THEMES["essence"])
    if brand_spec_path:
        custom_theme = build_theme_from_brand_spec(brand_spec_path)
        if custom_theme:
            theme_styles = custom_theme
    root_style = theme_styles.get("_root", "")
    bg_match = re.search(r'background:([^;]+)', root_style)
    bg_color = bg_match.group(1).strip() if bg_match else "#FAFAFA"

    # 外层容器 + 压缩（绝不使用 <style> 或 class）
    # 先加外层容器，再整体压缩——紧凑模式会在超限时自动移除它
    wrapped_html = (
        f'<section style="max-width:680px;margin:0 auto;padding:24px 16px;background:{bg_color};">'
        '<article>'
        f'{styled_html}'
        '</article>'
        '</section>'
    )
    full_html = _compress_html(wrapped_html)

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
