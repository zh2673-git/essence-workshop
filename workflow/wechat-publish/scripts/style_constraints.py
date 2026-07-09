"""
本质工坊 · 文章风格约束配置

属于内容框架层：定义不同写作风格对应的字数与配图约束。
与 content-output/references/pipeline-wechat.md 保持一致。
frontmatter 中 style 字段使用英文 key，如 style: column
"""

import re

# ─── 风格约束配置 ───────────────────────────────────────────

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
