"""生成全模板×全主题展示页面"""
import os
from scripts.elements.svg_themes import (
    render_svg_card, render_svg_stat, render_svg_quote, render_svg_compare,
    render_svg_timeline, render_svg_steps, render_svg_qa, render_svg_focus,
    render_svg_chart, render_svg_summary, render_svg_line_chart,
    render_svg_feature, render_svg_grid, render_svg_hero,
    render_svg_list_detail, render_svg_dashboard,
    render_svg_logic_flow, render_svg_cycle, render_svg_scatter, render_svg_heatmap, render_svg_composite,
    THEMES
)

THEME_NAMES = list(THEMES.keys())

# 所有模板的示例数据
TEMPLATES = [
    ("card", "列举要点 card", lambda tn: dict(
        title="核心能力", items=["系统思维", "批判性思考", "创造性解决", "跨域整合", "快速学习"]
    ), render_svg_card),
    ("stat", "关键数据 stat", lambda tn: dict(
        value="98.6%", label="用户满意度", sublabel="2024年度调研",
        trend="↑ 12.3%", tags=["NPS", "留存率", "活跃度", "推荐度"]
    ), render_svg_stat),
    ("quote", "金句引言 quote", lambda tn: dict(
        text="设计不是外表和感觉，设计是它如何运作的。",
        source="史蒂夫·乔布斯",
        context="2007年iPhone发布会上的经典论述",
        tags=["设计思维", "用户体验", "产品哲学"]
    ), render_svg_quote),
    ("compare", "A vs B compare", lambda tn: dict(
        title="前端框架对比", left_title="React", right_title="Vue",
        left_items=["虚拟DOM", "JSX语法", "生态丰富", "Facebook维护"],
        right_items=["响应式数据", "模板语法", "渐进式框架", "尤雨溪维护"]
    ), render_svg_compare),
    ("timeline", "时间线 timeline", lambda tn: dict(
        title="技术演进", events=[
            {"year": "2010", "title": "移动互联网", "desc": "智能手机普及"},
            {"year": "2014", "title": "微服务", "desc": "架构范式转变"},
            {"year": "2017", "title": "AI复兴", "desc": "深度学习突破"},
            {"year": "2020", "title": "低代码", "desc": "开发民主化"},
            {"year": "2023", "title": "大模型", "desc": "生成式AI爆发"},
        ]
    ), render_svg_timeline),
    ("steps", "步骤流程 steps", lambda tn: dict(
        title="产品开发流程", steps=[
            {"title": "需求分析", "desc": "收集用户痛点与业务目标"},
            {"title": "方案设计", "desc": "架构选型与技术评审"},
            {"title": "迭代开发", "desc": "敏捷冲刺与持续集成"},
            {"title": "测试上线", "desc": "质量保障与灰度发布"},
        ]
    ), render_svg_steps),
    ("qa", "问答 qa", lambda tn: dict(
        question="为什么需要微服务架构？",
        answer="微服务将单体应用拆分为独立部署的小服务，提升开发效率和系统弹性。",
        key_points=["独立部署", "技术异构", "故障隔离"]
    ), render_svg_qa),
    ("focus", "概念聚焦 focus", lambda tn: dict(
        keyword="认知负荷",
        explanation="人在处理信息时工作记忆所承受的负担，过高的认知负荷会导致决策质量下降。",
        tags=["心理学", "UX设计", "信息架构"],
        sub_keywords=["内在负荷", "外在负荷", "相关负荷", "工作记忆"]
    ), render_svg_focus),
    ("chart", "数据图表 chart", lambda tn: dict(
        title="季度营收", data=[
            {"label": "Q1", "value": 320}, {"label": "Q2", "value": 480},
            {"label": "Q3", "value": 560}, {"label": "Q4", "value": 720},
        ]
    ), render_svg_chart),
    ("summary", "总结清单 summary", lambda tn: dict(
        title="关键要点", items=[
            "系统思维是解决复杂问题的核心能力",
            "跨领域整合创造新的价值增长点",
            "持续学习是应对不确定性的最佳策略",
            "简洁是终极的复杂",
        ]
    ), render_svg_summary),
    ("line_chart", "趋势对比 line_chart", lambda tn: dict(
        title="增长趋势", labels=["1月","2月","3月","4月","5月","6月"],
        datasets=[
            {"name": "用户量", "values": [120,180,250,320,410,520]},
            {"name": "营收", "values": [80,110,160,220,290,380]},
        ]
    ), render_svg_line_chart),
    ("feature", "概念详解 feature", lambda tn: dict(
        title="设计原则", features=[
            {"keyword": "一致性", "desc": "保持界面元素和交互模式的统一，降低用户认知负担"},
            {"keyword": "反馈性", "desc": "每个操作都应有明确的视觉或听觉反馈"},
            {"keyword": "容错性", "desc": "允许用户犯错并提供便捷的撤销机制"},
            {"keyword": "效率性", "desc": "为高频操作提供快捷方式，减少操作步骤"},
        ]
    ), render_svg_feature),
    ("grid", "多维网格 grid", lambda tn: dict(
        title="技术栈", cards=[
            {"title": "前端", "desc": "React/Vue/TypeScript"},
            {"title": "后端", "desc": "Node/Python/Go"},
            {"title": "数据", "desc": "PostgreSQL/Redis"},
            {"title": "运维", "desc": "Docker/K8s/CI/CD"},
            {"title": "AI", "desc": "PyTorch/LLM/RAG"},
            {"title": "设计", "desc": "Figma/Design System"},
        ]
    ), render_svg_grid),
    ("hero", "英雄封面 hero", lambda tn: dict(
        title="认知升级", subtitle="从系统思维到跨界整合的完整路径",
        tags=["思维模型", "决策框架", "知识体系"]
    ), render_svg_hero),
    ("duo_card", "双栏对比 duo_card", lambda tn: dict(
        title="新旧架构对比", left_title="单体架构", right_title="微服务架构",
        left_items=["统一部署", "技术单一", "强耦合", "扩展困难", "故障全局"],
        right_items=["独立部署", "技术异构", "松耦合", "弹性扩展", "故障隔离"]
    ), render_svg_compare),
    ("list_detail", "列表详情 list_detail", lambda tn: dict(
        title="核心指标", items=[
            {"keyword": "DAU", "desc": "日活跃用户数，衡量产品粘性的核心指标"},
            {"keyword": "留存率", "desc": "用户回访比例，反映产品长期价值"},
            {"keyword": "NPS", "desc": "净推荐值，衡量用户忠诚度"},
            {"keyword": "ARPU", "desc": "单用户平均收入，衡量变现能力"},
        ]
    ), render_svg_list_detail),
    ("dashboard", "仪表盘 dashboard", lambda tn: dict(
        title="运营概览",
        metrics=[
            {"value": "12.8K", "label": "日活", "trend": "up"},
            {"value": "68%", "label": "留存", "trend": "up"},
            {"value": "¥42", "label": "ARPU", "trend": "down"},
            {"value": "4.8", "label": "评分", "trend": "up"},
        ],
        bar_data=[
            {"label": "1月", "value": 320}, {"label": "2月", "value": 480},
            {"label": "3月", "value": 560}, {"label": "4月", "value": 720},
            {"label": "5月", "value": 650}, {"label": "6月", "value": 890},
        ],
        list_items=[
            {"keyword": "转化率", "desc": "注册到付费", "value": "3.2%"},
            {"keyword": "退款率", "desc": "30天退款", "value": "1.8%"},
            {"keyword": "续费率", "desc": "年度续费", "value": "82%"},
        ]
    ), render_svg_dashboard),
    ("bar_chart", "竖向柱状图 bar_chart", lambda tn: dict(
        title="月度数据", data=[
            {"label": "1月", "value": 320}, {"label": "2月", "value": 480},
            {"label": "3月", "value": 560}, {"label": "4月", "value": 720},
            {"label": "5月", "value": 650}, {"label": "6月", "value": 890},
            {"label": "7月", "value": 780}, {"label": "8月", "value": 920},
        ], direction="vertical"
    ), render_svg_chart),
    ("metric_grid", "指标网格 metric_grid", lambda tn: dict(
        title="核心指标", cards=[
            {"value": "12.8K", "label": "日活", "sub": "↑12%", "mini": "up"},
            {"value": "68%", "label": "留存", "sub": "↑5%", "mini": "up"},
            {"value": "¥42", "label": "ARPU", "sub": "↓3%", "mini": "down"},
            {"value": "4.8", "label": "评分", "sub": "↑0.2", "mini": "up"},
            {"value": "3.2%", "label": "转化", "sub": "↑0.5%", "mini": "up"},
            {"value": "82%", "label": "续费", "sub": "稳定", "mini": "bar"},
        ], mode="metric"
    ), render_svg_grid),
    ("logic_flow", "逻辑推导图 logic_flow", lambda tn: dict(
        title="商业决策推导", steps=[
            {"label": "市场洞察", "desc": "用户需求未被满足", "type": "premise"},
            {"label": "假设验证", "desc": "MVP测试验证核心假设", "type": "inference"},
            {"label": "数据驱动", "desc": "基于留存数据调整策略", "type": "inference"},
            {"label": "规模化增长", "desc": "PMF达成后投入资源", "type": "conclusion"},
        ]
    ), render_svg_logic_flow),
    ("cycle", "循环图 cycle", lambda tn: dict(
        title="敏捷迭代循环", phases=[
            {"label": "计划", "desc": "确定冲刺目标"},
            {"label": "开发", "desc": "编码与单元测试"},
            {"label": "测试", "desc": "集成与回归测试"},
            {"label": "发布", "desc": "灰度上线与监控"},
            {"label": "反馈", "desc": "收集用户反馈"},
        ]
    ), render_svg_cycle),
    ("scatter", "散点图 scatter", lambda tn: dict(
        title="产品矩阵分析", data=[
            {"x": 0.2, "y": 0.8, "label": "核心", "size": 2, "group": 0},
            {"x": 0.15, "y": 0.7, "label": "基础", "size": 1.5, "group": 0},
            {"x": 0.25, "y": 0.9, "label": "关键", "size": 1.8, "group": 0},
            {"x": 0.7, "y": 0.6, "label": "增长", "size": 1.5, "group": 1},
            {"x": 0.8, "y": 0.55, "label": "潜力", "size": 1.3, "group": 1},
            {"x": 0.75, "y": 0.7, "label": "上升", "size": 1.2, "group": 1},
            {"x": 0.5, "y": 0.3, "label": "探索", "size": 1, "group": 2},
            {"x": 0.9, "y": 0.9, "label": "明星", "size": 2.5, "group": 2},
            {"x": 0.3, "y": 0.2, "label": "问题", "size": 1, "group": 2},
            {"x": 0.8, "y": 0.4, "label": "现金牛", "size": 1.8, "group": 2},
            {"x": 0.1, "y": 0.5, "label": "瘦狗", "size": 0.8, "group": 2},
            {"x": 0.6, "y": 0.7, "label": "待定", "size": 1.3, "group": 1},
        ]
    ), render_svg_scatter),
    ("heatmap", "热力图 heatmap", lambda tn: dict(
        title="技能矩阵评估", data={
            "rows": ["前端", "后端", "数据", "设计", "运维"],
            "cols": ["React", "Python", "SQL", "Figma", "Docker"],
            "values": [
                [0.9, 0.3, 0.4, 0.7, 0.5],
                [0.3, 0.9, 0.7, 0.2, 0.6],
                [0.2, 0.8, 0.9, 0.1, 0.4],
                [0.6, 0.1, 0.2, 0.9, 0.1],
                [0.4, 0.6, 0.5, 0.1, 0.9],
            ]
        }
    ), render_svg_heatmap),
    ("composite", "复合图 composite", lambda tn: dict(
        title="产品全景分析", sections=[
            {"type": "concept", "title": "核心概念", "content": "以用户为中心的产品设计方法论，强调快速迭代和数据驱动决策"},
            {"type": "chart", "title": "季度增长", "content": [{"label": "Q1", "value": 320}, {"label": "Q2", "value": 480}, {"label": "Q3", "value": 560}, {"label": "Q4", "value": 720}]},
            {"type": "line", "title": "趋势变化", "content": {"labels": ["1月","2月","3月","4月","5月","6月"], "datasets": [{"label": "用户", "values": [120,180,240,310,420,560]}, {"label": "收入", "values": [80,120,160,220,300,400]}]}},
            {"type": "card", "title": "关键指标", "content": [{"title": "DAU", "desc": "12.8K"}, {"title": "留存", "desc": "68%"}, {"title": "NPS", "desc": "4.8"}, {"title": "ARPU", "desc": "¥42"}]},
        ]
    ), render_svg_composite),
]

out_dir = os.path.join(os.path.dirname(__file__), "output", "all_templates_demo")
os.makedirs(out_dir, exist_ok=True)

# 生成所有SVG
svg_paths = {}
for tpl_key, tpl_label, data_fn, render_fn in TEMPLATES:
    for theme in THEME_NAMES:
        fname = f"{tpl_key}_{theme}.svg"
        data = data_fn(theme)
        svg = render_fn(**data, theme_name=theme)
        fpath = os.path.join(out_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(svg)
        svg_paths[(tpl_key, theme)] = fname

# 生成HTML展示页
rows_html = ""
for tpl_key, tpl_label, data_fn, render_fn in TEMPLATES:
    cells = ""
    for theme in THEME_NAMES:
        fname = svg_paths[(tpl_key, theme)]
        cells += f'<div class="cell"><div class="theme-label">{theme}</div><img src="{fname}" loading="lazy"/></div>\n'
    rows_html += f'<div class="row"><h2>{tpl_label}</h2><div class="grid">{cells}</div></div>\n'

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>全模板 · 全主题对比展示</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #111; color: #eee; font-family: 'PingFang SC','Microsoft YaHei',sans-serif; padding: 24px; }}
h1 {{ text-align: center; font-size: 28px; margin-bottom: 8px; color: #fff; }}
.subtitle {{ text-align: center; color: #666; margin-bottom: 32px; font-size: 14px; }}
h2 {{ font-size: 18px; margin: 32px 0 12px; color: #ccc; border-bottom: 1px solid #333; padding-bottom: 8px; }}
.row {{ margin-bottom: 16px; }}
.grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }}
.cell {{ background: #1a1a1a; border-radius: 8px; overflow: hidden; }}
.cell img {{ width: 100%; height: auto; display: block; }}
.theme-label {{ text-align: center; padding: 4px 0; font-size: 12px; color: #888; background: #222; }}
</style>
</head>
<body>
<h1>全模板 · 全主题对比展示</h1>
<p class="subtitle">19个渲染函数 × 7个主题 = 133张SVG</p>
{rows_html}
</body>
</html>'''

html_path = os.path.join(out_dir, "index.html")
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Done: {html_path}")
print(f"Total SVGs: {len(svg_paths)}")
