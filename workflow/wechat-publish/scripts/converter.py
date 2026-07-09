"""
本质工坊 · Markdown → 微信公众号 HTML 转换器

微信公众号平台特定的 HTML 转换 + 内容编排。
wechat_converter 核心转换，content_postprocess 内容预处理（图片/参考文献限量）。
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
    _distribute_images_evenly,
    _prioritize_gifs,
    _limit_references,
    _limit_images,
)

__all__ = [
    "convert_markdown",
    "inspect_article",
    "apply_inline_styles",
    "_compress_html",
    "_build_theme",
    "DEFAULT_COLORS",
    "_distribute_images_evenly",
    "_prioritize_gifs",
    "_limit_references",
    "_limit_images",
]
