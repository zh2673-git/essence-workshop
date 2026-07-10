"""
本质工坊 · Markdown → 微信公众号 HTML 转换器

微信公众号平台特定的 HTML 转换。
wechat_converter 核心转换，content_postprocess 参考文献限量。
对外保持 convert_markdown / inspect_article 接口不变。
"""

from wechat_converter import (  # noqa: E402
    convert_markdown,
    inspect_article,
    apply_inline_styles,
    _compress_html,
    _build_theme,
    DEFAULT_COLORS,
)
from content_postprocess import (  # noqa: E402
    _limit_references,
)

__all__ = [
    "convert_markdown",
    "inspect_article",
    "apply_inline_styles",
    "_compress_html",
    "_build_theme",
    "DEFAULT_COLORS",
    "_limit_references",
]
