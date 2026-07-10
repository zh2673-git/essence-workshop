"""
本质工坊 · Markdown → 微信公众号 HTML 转换器（平台适配层）

核心原则：微信草稿箱会剥离 <style> 标签和 class 属性，
因此所有样式必须 100% 内联，绝不使用 CSS 类或 <style> 块。

v2.0：只做平台格式适配（内联样式、HTML压缩、Frontmatter解析、标题去重），
不干预内容风格/字数/配图。参考文献限量保留（防止HTML超20000字符上限）。
"""

import json
import os
import re
from html.parser import HTMLParser

from markdown_it import MarkdownIt

# 平台约束相关后处理 — 同目录模块
from content_postprocess import _limit_references


# ─── 默认配色方案 ───────────────────────────────────────────
# 浅色背景 + 深色文字 + 强调色
# 微信公众号在手机端阅读，浅色方案更符合阅读习惯
# accent 默认为暖陶土色，可由上层 --brand-spec 覆盖

DEFAULT_COLORS = {
    "bg": "#FFFFFF",
    "bg_alt": "#F7F7F7",
    "bg_code": "#F5F5F5",
    "fg": "#333333",
    "accent": "#D97757",
    "muted": "#666666",
    "border": "#E8E8E8",
}


def _build_theme(colors=None):
    """根据配色字典构建内联样式主题。"""
    c = {**DEFAULT_COLORS, **(colors or {})}
    return {
        "_root": (
            "max-width:680px;margin:0 auto;padding:24px 16px;"
            f"background:{c['bg']};"
            "font-family:-apple-system,BlinkMacSystemFont,"
            '"PingFang SC","Noto Sans SC",sans-serif;'
            f"font-size:16px;line-height:1.8;color:{c['fg']};"
        ),
        "h1": f"font-size:22px;font-weight:700;color:{c['accent']};margin:36px 0 16px;",
        "h2": f"font-size:19px;font-weight:600;color:{c['accent']};margin:36px 0 16px;border-bottom:1px solid {c['border']};",
        "h3": f"font-size:17px;font-weight:600;color:{c['accent']};margin:20px 0 12px;",
        "h4": f"font-size:16px;font-weight:600;color:{c['muted']};margin:14px 0 8px;",
        "p": "",
        "blockquote": f"border-left:3px solid {c['accent']};background:{c['bg_alt']};margin:28px 0;padding:16px 20px;color:{c['muted']};",
        "ul": "margin:16px 0;padding-left:24px;",
        "ol": "margin:16px 0;padding-left:24px;",
        "li": "margin:8px 0;",
        "strong": f"color:{c['accent']};",
        "em": "",
        "a": "",
        "hr": "",
        "code": f"color:{c['accent']};",
        "pre": f"background:{c['bg_code']};padding:16px 20px;border-radius:10px;margin:28px 0;white-space:pre-wrap;word-break:break-all;overflow-wrap:break-word;max-width:100%;box-sizing:border-box;",
        "img": "max-width:100%;height:auto;margin:12px 0;",
        "table": "width:100%;border-collapse:collapse;margin:20px 0;",
        "th": f"background:{c['bg_code']};font-weight:600;padding:10px 14px;border:1px solid {c['border']};text-align:left;color:{c['accent']};",
        "td": f"padding:10px 14px;border:1px solid {c['border']};",
    }


def _load_colors_from_brand_spec(brand_spec_path):
    """从 brand-spec.json 加载配色，返回颜色字典。"""
    if not brand_spec_path or not os.path.isfile(brand_spec_path):
        return None
    try:
        with open(brand_spec_path, "r", encoding="utf-8") as f:
            brand = json.load(f)
        colors = brand.get("colors", {})
        mapping = {
            "bg": colors.get("background", DEFAULT_COLORS["bg"]),
            "bg_alt": colors.get("background_alt", DEFAULT_COLORS["bg_alt"]),
            "bg_code": DEFAULT_COLORS["bg_code"],
            "fg": colors.get("text_primary", DEFAULT_COLORS["fg"]),
            "accent": colors.get("primary", DEFAULT_COLORS["accent"]),
            "muted": colors.get("text_secondary", DEFAULT_COLORS["muted"]),
            "border": DEFAULT_COLORS["border"],
        }
        return mapping
    except (json.JSONDecodeError, KeyError):
        return None

_FM_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
_H2_PATTERN = re.compile(r'^##\s+(.+)\s*$', re.MULTILINE)


# ─── Frontmatter 解析 ──────────────────────────────────────

def _extract_frontmatter(md):
    match = _FM_PATTERN.match(md)
    metadata = {"title": "", "author": "", "digest": "", "style": ""}
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
                # inner_content 本身已包含 <p> 标签，直接放入 section 避免嵌套
                cfg = self.intro_config
                inner_content = re.sub(r'<p\b[^>]*>', f'<p style="{cfg["text"]}">', inner_content)
                intro_html = (
                    f'<section style="{cfg["wrapper"]}">'
                    f'{inner_content}'
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


def _get_blockquote_p_style(theme=None):
    return "margin:0 0 8px;line-height:1.8;"


def _get_intro_config(theme=None):
    """返回引言装饰配置。"""
    return {
        "wrapper": "margin:0 0 28px;padding:20px 24px;border-left:3px solid #D97757;background:#F7F7F7;",
        "text": "margin:0;line-height:1.8;color:#666666;",
    }


def apply_inline_styles(html, theme=None, brand_spec_path=None):
    """将主题样式注入 HTML，100% 内联，不使用 <style> 或 class。"""
    colors = _load_colors_from_brand_spec(brand_spec_path)
    styles = _build_theme(colors)

    # 清理已有的 <style> 和 class（来自 markdown_it 或其他来源）
    html = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", html, flags=re.IGNORECASE)

    # 构建不含 _root 的样式映射
    tag_styles = {k: v for k, v in styles.items() if not k.startswith("_")}

    bq_p_style = _get_blockquote_p_style()
    pre_code_style = "background:none;padding:0;color:inherit;font-size:inherit;"
    intro_config = _get_intro_config()

    injector = _StyleInjector(tag_styles, bq_p_style, pre_code_style, intro_config)
    injector.feed(html)
    return injector.get_result()


# ─── HTML 压缩 ─────────────────────────────────────────────
# 核心原则：绝不使用 <style> 标签或 class。
# 两阶段策略：基础压缩（始终执行）→ 紧凑模式（超限时一步到位）

# 从外层 section 继承的属性，子元素无需重复声明
_INHERITED_PROPS_CLEAN = [
    'color:#333333', 'color:#666666',
    'line-height:1.8',
]

# strong 高亮：半高淡橙色 gradient，参数简化映射
_GRADIENT_SHORTEN = [
    ('0.15)', '.15)'),
]

# 引言 section：浅色主题已使用纯色，无需渐变映射
_INTRO_GRADIENT_TO_SOLID = []


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
            style_val = re.sub(r'color:#FFFFFF;?', '', style_val)

        # h3：移除 color（与根色接近）
        elif re.search(r'<h3\s*$', prefix, re.IGNORECASE):
            style_val = re.sub(r'color:#FFD700;?', '', style_val)

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


# ─── 主转换函数 ─────────────────────────────────────────────

def convert_markdown(file_path="", markdown="", theme=None,
                     title="", author="", digest="", brand_spec_path=None):
    if file_path:
        with open(file_path, encoding="utf-8") as f:
            markdown = f.read()

    md_content, metadata = _extract_frontmatter(markdown)

    effective_title = title or metadata.get("title", "")
    if effective_title:
        md_content = _strip_duplicate_title(md_content, effective_title)

    md_content = _limit_references(md_content)

    md_parser = MarkdownIt("default", {"html": True})
    body_html = md_parser.render(md_content)

    # 修复：markdown_it 对段首长文本 **bold** 转换不完整的后处理
    # 将 HTML 中残留的 **text** 标记转换为 <strong>text</strong>
    body_html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', body_html)

    styled_html = apply_inline_styles(body_html, theme, brand_spec_path)

    # 获取背景色
    colors = _load_colors_from_brand_spec(brand_spec_path) or DEFAULT_COLORS
    theme_styles = _build_theme(colors)
    root_style = theme_styles.get("_root", "")
    bg_match = re.search(r'background:([^;]+)', root_style)
    bg_color = bg_match.group(1).strip() if bg_match else colors.get("bg", "#0A0A0A")

    # 外层容器 + 压缩（绝不使用 <style> 或 class）
    # 先加外层容器，再整体压缩——紧凑模式会在超限时自动移除它
    wrapped_html = (
        f'<section style="max-width:680px;margin:0 auto;padding:8px 16px 24px;background:{bg_color};">'
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
        "style": metadata.get("style", ""),
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
        "metadata": {"title": title, "author": author, "digest": digest, "style": metadata.get("style", "")},
        "readiness": readiness,
        "checks": checks,
    }
