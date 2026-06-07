"""生成全主题展示页面：4个增强模板 × 7个主题"""
import os
from scripts.elements.svg_themes import (
    render_svg_stat, render_svg_quote, render_svg_qa, render_svg_focus,
    THEMES
)

THEME_NAMES = list(THEMES.keys())

# 统一内容数据
STAT_DATA = {
    "value": "98.6%", "label": "用户满意度", "sublabel": "2024年度调研",
    "trend": "↑ 12.3%", "tags": ["NPS", "留存率", "活跃度", "推荐度"],
}
QUOTE_DATA = {
    "text": "设计不是外表和感觉，设计是它如何运作的。",
    "source": "史蒂夫·乔布斯",
    "context": "2007年iPhone发布会上的经典论述",
    "tags": ["设计思维", "用户体验", "产品哲学"],
}
QA_DATA = {
    "question": "为什么需要微服务架构？",
    "answer": "微服务将单体应用拆分为独立部署的小服务，提升开发效率和系统弹性。",
    "key_points": ["独立部署", "技术异构", "故障隔离"],
}
FOCUS_DATA = {
    "keyword": "认知负荷",
    "explanation": "人在处理信息时工作记忆所承受的负担，过高的认知负荷会导致决策质量下降。",
    "tags": ["心理学", "UX设计", "信息架构"],
    "sub_keywords": ["内在负荷", "外在负荷", "相关负荷", "工作记忆"],
}

TEMPLATES = [
    ("stat", "关键数据 stat", STAT_DATA, render_svg_stat),
    ("quote", "金句引言 quote", QUOTE_DATA, render_svg_quote),
    ("qa", "问答 qa", QA_DATA, render_svg_qa),
    ("focus", "概念聚焦 focus", FOCUS_DATA, render_svg_focus),
]

out_dir = os.path.join(os.path.dirname(__file__), "output", "contrast_demo")
os.makedirs(out_dir, exist_ok=True)

# 生成所有SVG
svg_paths = {}
for tpl_key, tpl_label, data, render_fn in TEMPLATES:
    for theme in THEME_NAMES:
        fname = f"{tpl_key}_{theme}.svg"
        svg = render_fn(**data, theme_name=theme)
        fpath = os.path.join(out_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(svg)
        svg_paths[(tpl_key, theme)] = fname

# 生成HTML展示页
rows_html = ""
for tpl_key, tpl_label, data, render_fn in TEMPLATES:
    cells = ""
    for theme in THEME_NAMES:
        fname = svg_paths[(tpl_key, theme)]
        cells += f'<div class="cell"><div class="theme-label">{theme}</div><img src="{fname}" /></div>\n'
    rows_html += f'<div class="row"><h2>{tpl_label}</h2><div class="grid">{cells}</div></div>\n'

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>增强模板 · 全主题对比</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #111; color: #eee; font-family: 'PingFang SC','Microsoft YaHei',sans-serif; padding: 24px; }}
h1 {{ text-align: center; font-size: 28px; margin-bottom: 32px; color: #fff; }}
h2 {{ font-size: 20px; margin: 24px 0 12px; color: #ccc; border-bottom: 1px solid #333; padding-bottom: 8px; }}
.row {{ margin-bottom: 40px; }}
.grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }}
.cell {{ background: #1a1a1a; border-radius: 8px; overflow: hidden; }}
.cell img {{ width: 100%; height: auto; display: block; }}
.theme-label {{ text-align: center; padding: 6px 0; font-size: 13px; color: #888; background: #222; }}
</style>
</head>
<body>
<h1>增强模板 · 全主题对比展示</h1>
<p style="text-align:center;color:#666;margin-bottom:24px;">4个低密度模板 × 7个主题 = 28张SVG，所有辅助参数均已填入</p>
{rows_html}
</body>
</html>'''

html_path = os.path.join(out_dir, "index.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Done: {html_path}")
