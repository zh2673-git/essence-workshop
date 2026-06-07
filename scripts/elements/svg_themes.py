"""
本质工坊 · SVG 样式模板体系
定义视觉风格契约，所有管线共享同一套主题定义

设计原则：
  - 主题是"视觉风格是什么"的声明，与"怎么渲染"分离
  - 同一内容 + 不同主题 = 不同视觉输出
  - 主题覆盖：背景、色彩、排版、装饰、动画
  - 管线消费：video/Canvas、公众号/SVG、HTML/CSS、PPTX 各取所需

主题 Schema（每个主题必须提供的字段）：
  name        : 主题英文名（唯一标识）
  label       : 主题中文名
  bg          : 背景色组 { bg1, bg2, bg3 }（渐变三色）
  palette     : 色板 { accent, gold, cyan, success, warn }
  text        : 文字色 { primary, secondary, dim, inverse }
  card        : 卡片 { fill, border, radius, shadow }
  decor       : 装饰 { style, opacity, elements }
  font        : 字体 { display, body, mono }
  mood        : 情绪标签（用于自动匹配）
"""

import json
import math
import os
import re

from scripts.elements.shape_primitives import (
    svg_bullet, svg_card, svg_circle, svg_connector,
    svg_icon, svg_line, svg_ring, svg_step_number,
    get_shape_style, get_scene_icon, shape_style_to_video_js,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 主题定义
# card.fill 设计约束:
#   - 深色主题（dark/nature/cyber/indigo）: fill >= 0.10, border >= 0.15
#     低于此值在深色背景上几乎不可见（渲染函数还会叠加 opacity 0.4）
#   - 浅色主题（warm/minimal/ink）: fill >= 0.75, 无可见性问题
THEMES = {
    "dark": {
        "name": "dark",
        "label": "深空",
        "bg": {
            "bg1": "#2B2D42", "bg2": "#3D3F5C", "bg3": "#1E2035",
            "layout": "side-panel",
            "panel_color": "#3A3C58",
            "panel_x": 0.62,
        },
        "palette": {
            "accent": "#EF6461",
            "accentGlow": "rgba(239,100,97,0.18)",
            "gold": "#E4B363",
            "goldDim": "rgba(228,179,99,0.3)",
            "cyan": "#58C4DC",
            "cyanDim": "rgba(88,196,220,0.18)",
            "success": "#4ECDC4",
            "warn": "#FFE66D",
        },
        "text": {
            "primary": "#F2F0ED",
            "secondary": "#B8B5CE",
            "dim": "rgba(242,240,237,0.7)",
            "inverse": "#2B2D42",
        },
        "card": {
            "fill": "rgba(255,255,255,0.10)",
            "border": "rgba(255,255,255,0.15)",
            "radius": 32,
            "shadow": "rgba(239,100,97,0.12)",
        },
        "decor": {
            "style": "circles",
            "opacity": 0.12,
            "density": "rich",
            "gradient_accents": True,
            "elements": ["floating-circles", "grid", "accent-line", "diamonds", "curves", "cross-stars", "dot-matrix"],
        },
        "atmosphere": {
            "glow": [
                {"cx": 0.5, "cy": 0.35, "r": 0.55, "color": "accent", "alpha": 0.14},
                {"cx": 0.82, "cy": 0.15, "r": 0.38, "color": "gold", "alpha": 0.10},
                {"cx": 0.18, "cy": 0.85, "r": 0.32, "color": "cyan", "alpha": 0.08},
            ],
            "gradient_dir": "vertical",
            "grain": 0.012,
        },
        "font": {
            "display": "'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif",
            "body": "'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif",
            "mono": "'JetBrains Mono','Fira Code',monospace",
        },
        "semantic": {
            "item_accent_a": "#EF6461",    # 列表项奇数色（鲜明）
            "item_accent_b": "#58C4DC",    # 列表项偶数色（对比）
            "connector_color": "#E4B363",  # 连接线/箭头色
            "badge_bg": "rgba(239,100,97,0.12)",  # 序号/标签背景
            "divider_accent": "#EF6461",   # 分割线强调色
            "highlight_ring": "#EF6461",   # 高亮圆环色
        },
        "mood": ["技术", "编程", "AI", "工程", "算法", "数据", "深邃", "未来"],
    },
    "warm": {
        "name": "warm",
        "label": "暖阳",
        "bg": {
            "bg1": "#DCC8A8", "bg2": "#D0BC98", "bg3": "#C4B088",
            "layout": "soft-glow",
            "glow_color": "#F5EDE0",
            "glow_cx": 0.78,
            "glow_cy": 0.72,
            "glow_r": 0.4,
            "glow_alpha": 0.3,
        },
        "palette": {
            "accent": "#B86030",
            "accentGlow": "rgba(184,96,48,0.16)",
            "gold": "#7A4820",
            "goldDim": "rgba(122,72,32,0.28)",
            "cyan": "#2E7A6A",
            "cyanDim": "rgba(46,122,106,0.14)",
            "success": "#2E7A6A",
            "warn": "#B86030",
        },
        "text": {
            "primary": "#1A0800",
            "secondary": "#3A1E08",
            "dim": "rgba(26,8,0,0.65)",
            "inverse": "#DCC8A8",
        },
        "card": {
            "fill": "rgba(255,255,255,0.75)",
            "border": "rgba(184,96,48,0.15)",
            "radius": 24,
            "shadow": "rgba(184,96,48,0.10)",
        },
        "decor": {
            "style": "dots",
            "opacity": 0.18,
            "density": "normal",
            "gradient_accents": True,
            "elements": ["dot-grid", "warm-gradient", "accent-corner"],
        },
        "atmosphere": {
            "glow": [
                {"cx": 0.3, "cy": 0.3, "r": 0.48, "color": "accent", "alpha": 0.10},
                {"cx": 0.72, "cy": 0.72, "r": 0.38, "color": "cyan", "alpha": 0.08},
            ],
            "gradient_dir": "diagonal",
            "grain": 0.006,
        },
        "font": {
            "display": "'Noto Serif SC',Georgia,'PingFang SC',serif",
            "body": "'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif",
            "mono": "'JetBrains Mono','Fira Code',monospace",
        },
        "semantic": {
            "item_accent_a": "#B86030",
            "item_accent_b": "#2E7A6A",
            "connector_color": "#7A4820",
            "badge_bg": "rgba(184,96,48,0.12)",
            "divider_accent": "#B86030",
            "highlight_ring": "#B86030",
        },
        "mood": ["温暖", "生活", "教育", "成长", "阅读", "写作", "人文"],
    },
    "minimal": {
        "name": "minimal",
        "label": "极简",
        "bg": {
            "bg1": "#F5F5F0", "bg2": "#EDEDE8", "bg3": "#E4E4DF",
            "layout": "accent-edge",
            "edge_color": "#1A1A2E",
            "edge_width": 4,
        },
        "palette": {
            "accent": "#1A1A2E",
            "accentGlow": "rgba(26,26,46,0.10)",
            "gold": "#C8553D",
            "goldDim": "rgba(200,85,61,0.20)",
            "cyan": "#2B6A7C",
            "cyanDim": "rgba(43,106,124,0.15)",
            "success": "#2D8C3C",
            "warn": "#CC8800",
        },
        "text": {
            "primary": "#1A1A2E",
            "secondary": "#5A5A72",
            "dim": "rgba(26,26,46,0.6)",
            "inverse": "#F5F5F0",
        },
        "card": {
            "fill": "rgba(255,255,255,0.85)",
            "border": "rgba(26,26,46,0.12)",
            "radius": 12,
            "shadow": "rgba(26,26,46,0.08)",
        },
        "decor": {
            "style": "lines",
            "opacity": 0.30,
            "density": "sparse",
            "gradient_accents": False,
            "elements": ["thin-lines", "single-accent", "whitespace"],
        },
        "atmosphere": {
            "glow": [
                {"cx": 0.5, "cy": 0.5, "r": 0.5, "color": "accent", "alpha": 0.04},
            ],
            "gradient_dir": "vertical",
            "grain": 0,
        },
        "font": {
            "display": "'Helvetica Neue','PingFang SC','Microsoft YaHei',sans-serif",
            "body": "'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif",
            "mono": "'JetBrains Mono','Fira Code',monospace",
        },
        "semantic": {
            "item_accent_a": "#C8553D",
            "item_accent_b": "#2B6A7C",
            "connector_color": "#1A1A2E",
            "badge_bg": "rgba(200,85,61,0.10)",
            "divider_accent": "#1A1A2E",
            "highlight_ring": "#C8553D",
        },
        "mood": ["极简", "设计", "美学", "哲学", "禅", "克制", "留白"],
    },
    "nature": {
        "name": "nature",
        "label": "自然",
        "bg": {
            "bg1": "#3A5A40", "bg2": "#4A6B4F", "bg3": "#2D4A34",
            "layout": "curved-horizon",
            "sky_color": "#C8D8C0",
            "sky_alpha": 0.2,
            "horizon_y": 0.55,
            "curve_depth": 0.06,
        },
        "palette": {
            "accent": "#D4A843",
            "accentGlow": "rgba(212,168,67,0.16)",
            "gold": "#8FAA6B",
            "goldDim": "rgba(143,170,107,0.3)",
            "cyan": "#6BA3A0",
            "cyanDim": "rgba(107,163,160,0.16)",
            "success": "#8FAA6B",
            "warn": "#D4A843",
        },
        "text": {
            "primary": "#F0EAD6",
            "secondary": "#D4E2BC",
            "dim": "rgba(240,234,214,0.7)",
            "inverse": "#3A5A40",
        },
        "card": {
            "fill": "rgba(255,255,255,0.10)",
            "border": "rgba(212,168,67,0.18)",
            "radius": 28,
            "shadow": "rgba(212,168,67,0.08)",
        },
        "decor": {
            "style": "organic",
            "opacity": 0.12,
            "density": "normal",
            "gradient_accents": True,
            "elements": ["leaf-curves", "earth-tones", "golden-accent"],
        },
        "atmosphere": {
            "glow": [
                {"cx": 0.5, "cy": 0.4, "r": 0.52, "color": "gold", "alpha": 0.12},
                {"cx": 0.2, "cy": 0.8, "r": 0.32, "color": "accent", "alpha": 0.08},
            ],
            "gradient_dir": "vertical",
            "grain": 0.008,
        },
        "font": {
            "display": "'Noto Serif SC',Georgia,'PingFang SC',serif",
            "body": "'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif",
            "mono": "'JetBrains Mono','Fira Code',monospace",
        },
        "semantic": {
            "item_accent_a": "#D4A843",
            "item_accent_b": "#6BA3A0",
            "connector_color": "#8FAA6B",
            "badge_bg": "rgba(212,168,67,0.12)",
            "divider_accent": "#D4A843",
            "highlight_ring": "#D4A843",
        },
        "mood": ["自然", "生态", "环保", "中医", "养生", "本草", "天地"],
    },
    "ink": {
        "name": "ink",
        "label": "水墨",
        "bg": {
            "bg1": "#F2EDE4", "bg2": "#EAE4D8", "bg3": "#E0DACE",
            "layout": "ink-wash",
            "ink_color": "#2E2820",
            "ink_x": 0.65,
            "ink_opacity": 0.06,
        },
        "palette": {
            "accent": "#B83A2A",
            "accentGlow": "rgba(184,58,42,0.14)",
            "gold": "#C4943C",
            "goldDim": "rgba(196,148,60,0.25)",
            "cyan": "#4A7A72",
            "cyanDim": "rgba(74,122,114,0.15)",
            "success": "#4A7C59",
            "warn": "#B8860B",
        },
        "text": {
            "primary": "#1C1810",
            "secondary": "#5A5248",
            "dim": "rgba(28,24,16,0.65)",
            "inverse": "#F2EDE4",
        },
        "card": {
            "fill": "rgba(255,255,255,0.78)",
            "border": "rgba(184,58,42,0.12)",
            "radius": 16,
            "shadow": "rgba(46,40,32,0.08)",
        },
        "decor": {
            "style": "brush",
            "opacity": 0.24,
            "density": "normal",
            "gradient_accents": False,
            "elements": ["ink-wash", "seal-stamp", "bamboo-line"],
        },
        "atmosphere": {
            "glow": [
                {"cx": 0.5, "cy": 0.5, "r": 0.6, "color": "accent", "alpha": 0.04},
            ],
            "gradient_dir": "vertical",
            "grain": 0.006,
        },
        "font": {
            "display": "'Noto Serif SC','STSong','SimSun',serif",
            "body": "'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif",
            "mono": "'JetBrains Mono','Fira Code',monospace",
        },
        "semantic": {
            "item_accent_a": "#B83A2A",
            "item_accent_b": "#C4943C",
            "connector_color": "#1C1810",
            "badge_bg": "rgba(184,58,42,0.10)",
            "divider_accent": "#B83A2A",
            "highlight_ring": "#B83A2A",
        },
        "mood": ["水墨", "国风", "传统", "书法", "诗词", "古典", "东方"],
    },
    "cyber": {
        "name": "cyber",
        "label": "赛博",
        "bg": {
            "bg1": "#1A1A3E", "bg2": "#252550", "bg3": "#12122E",
            "layout": "diagonal-beam",
            "beam_color": "#FF4D8D",
            "beam_opacity": 0.06,
            "beam_angle": 25,
        },
        "palette": {
            "accent": "#FF4D8D",
            "accentGlow": "rgba(255,77,141,0.18)",
            "gold": "#00E5C8",
            "goldDim": "rgba(0,229,200,0.3)",
            "cyan": "#8B6FFF",
            "cyanDim": "rgba(139,111,255,0.18)",
            "success": "#00E5C8",
            "warn": "#FFD600",
        },
        "text": {
            "primary": "#E8E8FF",
            "secondary": "#A0A0D0",
            "dim": "rgba(232,232,255,0.65)",
            "inverse": "#1A1A3E",
        },
        "card": {
            "fill": "rgba(255,255,255,0.10)",
            "border": "rgba(255,77,141,0.20)",
            "radius": 24,
            "shadow": "rgba(255,77,141,0.10)",
        },
        "decor": {
            "style": "neon",
            "opacity": 0.12,
            "density": "rich",
            "gradient_accents": True,
            "elements": ["neon-lines", "scan-line", "glitch-bar"],
        },
        "atmosphere": {
            "glow": [
                {"cx": 0.5, "cy": 0.3, "r": 0.48, "color": "accent", "alpha": 0.16},
                {"cx": 0.2, "cy": 0.72, "r": 0.32, "color": "cyan", "alpha": 0.10},
            ],
            "gradient_dir": "diagonal",
            "grain": 0.015,
        },
        "font": {
            "display": "'Orbitron','PingFang SC','Microsoft YaHei',sans-serif",
            "body": "'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif",
            "mono": "'JetBrains Mono','Fira Code',monospace",
        },
        "semantic": {
            "item_accent_a": "#FF4D8D",
            "item_accent_b": "#00E5C8",
            "connector_color": "#8B6FFF",
            "badge_bg": "rgba(255,77,141,0.12)",
            "divider_accent": "#FF4D8D",
            "highlight_ring": "#FF4D8D",
        },
        "mood": ["赛博", "未来", "黑客", "元宇宙", "Web3", "区块链", "数字"],
    },
    "indigo": {
        "name": "indigo",
        "label": "靛蓝",
        "bg": {
            "bg1": "#0F0C2A", "bg2": "#1E1A4A", "bg3": "#302B62",
            "layout": "side-panel",
            "panel_color": "#252050",
            "panel_x": 0.65,
        },
        "palette": {
            "accent": "#C96442",
            "accentGlow": "rgba(201,100,66,0.18)",
            "gold": "#E4B363",
            "goldDim": "rgba(228,179,99,0.3)",
            "cyan": "#FF6B6B",
            "cyanDim": "rgba(255,107,107,0.18)",
            "success": "#4ECDC4",
            "warn": "#FFE66D",
        },
        "text": {
            "primary": "#E0E0E0",
            "secondary": "#9B97B0",
            "dim": "rgba(224,224,224,0.7)",
            "inverse": "#0F0C2A",
        },
        "card": {
            "fill": "rgba(255,255,255,0.12)",
            "border": "rgba(255,255,255,0.18)",
            "radius": 32,
            "shadow": "rgba(201,100,66,0.12)",
        },
        "decor": {
            "style": "constellation",
            "opacity": 0.12,
            "density": "rich",
            "gradient_accents": True,
            "elements": ["star-groups", "star-dots", "mind-trails", "nebula"],
        },
        "atmosphere": {
            "glow": [
                {"cx": 0.5, "cy": 0.35, "r": 0.55, "color": "accent", "alpha": 0.10},
                {"cx": 0.82, "cy": 0.72, "r": 0.35, "color": "cyan", "alpha": 0.08},
            ],
            "gradient_dir": "vertical",
            "grain": 0.008,
        },
        "font": {
            "display": "'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif",
            "body": "'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif",
            "mono": "'JetBrains Mono','Fira Code',monospace",
        },
        "semantic": {
            "item_accent_a": "#C96442",
            "item_accent_b": "#FF6B6B",
            "connector_color": "#E4B363",
            "badge_bg": "rgba(201,100,66,0.12)",
            "divider_accent": "#C96442",
            "highlight_ring": "#C96442",
        },
        "mood": ["认知", "思维", "本质", "哲学", "深度", "沉思", "智慧", "洞察"],
    },
}

VALID_THEME_NAMES = set(THEMES.keys())

# 画幅比例预设：所有渲染函数均可通过 width/height 参数使用
ASPECT_RATIOS = {
    "standard": (800, 600),      # 4:3 公众号标准
    "wide": (1240, 770),         # 16:10 宽幅（匹配参考图片风格）
    "cinematic": (1280, 720),    # 16:9 视频号
}


def get_theme(name):
    if name not in THEMES:
        raise ValueError(f"Unknown theme: {name}. Valid: {', '.join(sorted(VALID_THEME_NAMES))}")
    return THEMES[name]


def match_theme(text):
    # 素白(minimal)和水墨(ink)色调过素，不参与自动匹配
    # 如需使用需显式指定 theme_name="minimal" 或 "ink"
    excluded = {"minimal", "ink"}
    scores = {name: 0 for name in THEMES if name not in excluded}
    for name in scores:
        for keyword in THEMES[name]["mood"]:
            scores[name] += text.count(keyword)
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "dark"
    return best


def theme_to_video_js(theme_name):
    t = get_theme(theme_name)
    bg = t["bg"]
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    return {
        "bg1": bg["bg1"], "bg2": bg["bg2"], "bg3": bg["bg3"],
        "accent": p["accent"], "accentGlow": p["accentGlow"],
        "gold": p["gold"], "goldDim": p["goldDim"],
        "cyan": p["cyan"], "cyanDim": p["cyanDim"],
        "white": tx["primary"], "whiteDim": tx["dim"],
        "muted": tx["secondary"],
        "cardBg": c["fill"], "cardBorder": c["border"],
        "success": p["success"], "warn": p["warn"],
    }


def theme_to_brand_spec(theme_name):
    t = get_theme(theme_name)
    bg = t["bg"]
    p = t["palette"]
    tx = t["text"]
    return {
        "colors": {
            "primary": p["accent"],
            "accent": p["accent"],
            "bg": bg["bg2"],
            "fg": tx["primary"],
            "muted": tx["secondary"],
            "border": t["card"]["border"],
            "success": p["success"],
            "warning": p["warn"],
        },
        "derived": {
            "primary-dim": p["accentGlow"],
            "accent-dim": p["accentGlow"],
            "card-bg": t["card"]["fill"],
            "card-border": t["card"]["border"],
        },
        "fonts": {
            "display": t["font"]["display"],
            "body": t["font"]["body"],
            "mono": t["font"]["mono"],
        },
    }


def _svg_decor_circles(t, w, h):
    parts = []
    p = t["palette"]
    op = t["decor"]["opacity"]
    # 语义色：装饰器内部统一使用语义色板
    sa = _s(t, "item_accent_a")   # 主强调色（原 p["accent"]）
    sb = _s(t, "item_accent_b")   # 副强调色（原 p["gold"]）
    sc = _s(t, "connector_color") # 辅助色（原 p["cyan"]）
    # 远景：大圆低透明度
    parts.append(f'<circle cx="{w*0.82}" cy="{h*0.12}" r="55" fill="{sa}" opacity="{op*0.06}"/>')
    parts.append(f'<circle cx="{w*0.15}" cy="{h*0.88}" r="45" fill="{sc}" opacity="{op*0.05}"/>')
    # 中景：圆环（4个，更丰富）
    for i in range(4):
        cx = w * (0.72 + i * 0.08)
        cy = h * (0.15 + (i % 2) * 0.55)
        r = 28 + i * 18
        color = sa if i % 2 == 0 else sc
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="1" opacity="{op}"/>')
    parts.append(f'<circle cx="{w*0.85}" cy="{h*0.2}" r="40" fill="none" stroke="{sb}" stroke-width="0.6" opacity="{op * 0.5}"/>')
    # 近景：小圆点（5个）
    for i in range(5):
        dx = w * (0.65 + i * 0.07)
        dy = h * (0.90 - i * 0.04)
        parts.append(f'<circle cx="{dx}" cy="{dy}" r="2.5" fill="{sa}" opacity="{op*0.5}"/>')
    # 近景：小菱形（3个，多位置）
    for dx, dy, ds, c in [(w*0.88, h*0.42, 8, sb), (w*0.12, h*0.35, 6, sc), (w*0.75, h*0.78, 5, sa)]:
        pts = f"{dx},{dy-ds} {dx+ds},{dy} {dx},{dy+ds} {dx-ds},{dy}"
        parts.append(f'<polygon points="{pts}" fill="none" stroke="{c}" stroke-width="0.7" opacity="{op*0.4}"/>')
    # 近景：曲线（2条）
    parts.append(
        f'<path d="M{w*0.6},{h*0.75} Q{w*0.75},{h*0.68} {w*0.9},{h*0.72}" '
        f'fill="none" stroke="{sc}" stroke-width="0.8" opacity="{op * 0.4}"/>'
    )
    parts.append(
        f'<path d="M{w*0.55},{h*0.35} Q{w*0.68},{h*0.28} {w*0.82},{h*0.32}" '
        f'fill="none" stroke="{sb}" stroke-width="0.6" opacity="{op * 0.3}"/>'
    )
    # 近景：十字星（3个）
    for sx, sy, sl, scc in [(w*0.78, h*0.08, 12, sb), (w*0.22, h*0.15, 8, sc), (w*0.92, h*0.55, 10, sa)]:
        parts.append(f'<line x1="{sx-sl}" y1="{sy}" x2="{sx+sl}" y2="{sy}" stroke="{scc}" stroke-width="0.5" opacity="{op*0.6}"/>')
        parts.append(f'<line x1="{sx}" y1="{sy-sl}" x2="{sx}" y2="{sy+sl}" stroke="{scc}" stroke-width="0.5" opacity="{op*0.6}"/>')
    # 近景：网格点阵（3x3）
    for gx in range(3):
        for gy in range(3):
            px = w * (0.68 + gx * 0.08)
            py = h * (0.50 + gy * 0.10)
            parts.append(f'<circle cx="{px}" cy="{py}" r="1" fill="{t["text"]["secondary"]}" opacity="{op*0.3}"/>')
    return "\n    ".join(parts)


def _svg_decor_dots(t, w, h):
    parts = []
    p = t["palette"]
    op = t["decor"]["opacity"]
    sa = _s(t, "item_accent_a")
    sb = _s(t, "item_accent_b")
    sc = _s(t, "connector_color")
    # 远景：大圆低透明度
    parts.append(f'<circle cx="{w*0.82}" cy="{h*0.15}" r="50" fill="{sa}" opacity="{op*0.06}"/>')
    parts.append(f'<circle cx="{w*0.15}" cy="{h*0.85}" r="40" fill="{sc}" opacity="{op*0.05}"/>')
    # 中景：圆环
    for i in range(3):
        cx = w * (0.70 + i * 0.12)
        cy = h * (0.18 + (i % 2) * 0.50)
        r = 22 + i * 14
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{sa}" stroke-width="0.8" opacity="{op}"/>')
    # 中景：曲线
    parts.append(
        f'<path d="M{w*0.6},{h*0.75} Q{w*0.75},{h*0.68} {w*0.9},{h*0.72}" '
        f'fill="none" stroke="{sc}" stroke-width="0.8" opacity="{op * 0.4}"/>'
    )
    parts.append(
        f'<path d="M{w*0.55},{h*0.35} Q{w*0.68},{h*0.28} {w*0.82},{h*0.32}" '
        f'fill="none" stroke="{sb}" stroke-width="0.6" opacity="{op * 0.3}"/>'
    )
    parts.append(f'<circle cx="{w*0.82}" cy="{h*0.18}" r="30" fill="none" stroke="{sc}" stroke-width="0.5" opacity="{op * 0.35}"/>')
    # 近景：小点
    for i in range(5):
        dx = w * (0.62 + i * 0.07)
        dy = h * (0.88 - i * 0.03)
        parts.append(f'<circle cx="{dx}" cy="{dy}" r="2" fill="{sa}" opacity="{op*0.5}"/>')
    # 近景：小菱形
    dx, dy = w*0.88, h*0.42
    ds = 6
    pts = f"{dx},{dy-ds} {dx+ds},{dy} {dx},{dy+ds} {dx-ds},{dy}"
    parts.append(f'<polygon points="{pts}" fill="{sb}" opacity="{op*0.4}"/>')
    return "\n    ".join(parts)


def _svg_decor_lines(t, w, h):
    parts = []
    p = t["palette"]
    op = t["decor"]["opacity"]
    sa = _s(t, "item_accent_a")
    sb = _s(t, "item_accent_b")
    sc = _s(t, "connector_color")
    # 远景：大矩形低透明度
    parts.append(f'<rect x="{w*0.70}" y="{h*0.06}" width="60" height="40" fill="{sa}" opacity="{op*0.05}" rx="2"/>')
    parts.append(f'<rect x="{w*0.12}" y="{h*0.80}" width="50" height="35" fill="{sc}" opacity="{op*0.04}" rx="2"/>')
    # 中景：线框矩形
    for i in range(2):
        rx = w * (0.68 + i * 0.14)
        ry = h * (0.08 + (i % 2) * 0.40)
        rw = 40 + i * 16
        rh = 28 + i * 12
        parts.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="none" stroke="{sa}" stroke-width="0.8" opacity="{op * 0.7}" rx="2"/>')
    # 中景：十字线
    for i in range(2):
        cx = w * (0.72 + i * 0.15)
        cy = h * (0.60 + (i % 2) * 0.20)
        size = 10 + i * 4
        parts.append(
            f'<line x1="{cx-size}" y1="{cy}" x2="{cx+size}" y2="{cy}" stroke="{sc}" stroke-width="0.8" opacity="{op * 0.6}"/>'
        )
        parts.append(
            f'<line x1="{cx}" y1="{cy-size}" x2="{cx}" y2="{cy+size}" stroke="{sc}" stroke-width="0.8" opacity="{op * 0.6}"/>'
        )
    # 中景：长横线
    parts.append(
        f'<line x1="{w*0.6}" y1="{h*0.52}" x2="{w*0.95}" y2="{h*0.52}" stroke="{sa}" stroke-width="0.5" opacity="{op * 0.4}"/>'
    )
    # 近景：菱形
    dx = w * 0.82
    dy = h * 0.72
    ds = 14
    pts = f"{dx},{dy-ds} {dx+ds},{dy} {dx},{dy+ds} {dx-ds},{dy}"
    parts.append(f'<polygon points="{pts}" fill="none" stroke="{sc}" stroke-width="0.7" opacity="{op * 0.45}"/>')
    # 近景：小点
    for i in range(3):
        dx = w * (0.70 + i * 0.09)
        dy = h * (0.92 - i * 0.03)
        parts.append(f'<circle cx="{dx}" cy="{dy}" r="2" fill="{sa}" opacity="{op*0.4}"/>')
    return "\n    ".join(parts)


def _svg_decor_organic(t, w, h):
    parts = []
    p = t["palette"]
    op = t["decor"]["opacity"]
    sa = _s(t, "item_accent_a")
    sb = _s(t, "item_accent_b")
    sc = _s(t, "connector_color")
    # 远景：大椭圆低透明度
    parts.append(f'<ellipse cx="{w*0.78}" cy="{h*0.20}" rx="50" ry="30" fill="{sb}" opacity="{op*0.06}"/>')
    parts.append(f'<ellipse cx="{w*0.18}" cy="{h*0.82}" rx="40" ry="25" fill="{sa}" opacity="{op*0.05}"/>')
    # 中景：波浪曲线
    for i in range(2):
        cy = h * (0.20 + i * 0.50)
        amp = 20 + i * 10
        parts.append(
            f'<path d="M{w*0.55},{cy} Q{w*0.7},{cy-amp} {w*0.85},{cy} T{w},{cy}" '
            f'fill="none" stroke="{sb}" stroke-width="1" opacity="{op}"/>'
        )
    parts.append(
        f'<path d="M{w*0.6},{h*0.85} Q{w*0.75},{h*0.78} {w*0.9},{h*0.82}" '
        f'fill="none" stroke="{sa}" stroke-width="1" opacity="{op * 0.5}"/>'
    )
    # 近景：叶片形小点
    for i in range(3):
        dx = w * (0.72 + i * 0.08)
        dy = h * (0.92 - i * 0.03)
        parts.append(f'<circle cx="{dx}" cy="{dy}" r="3" fill="{sb}" opacity="{op*0.35}"/>')
    # 近景：小弧线
    parts.append(
        f'<path d="M{w*0.80},{h*0.60} Q{w*0.86},{h*0.56} {w*0.92},{h*0.58}" '
        f'fill="none" stroke="{sa}" stroke-width="0.8" opacity="{op*0.4}"/>'
    )
    return "\n    ".join(parts)


def _svg_decor_brush(t, w, h):
    parts = []
    p = t["palette"]
    op = t["decor"]["opacity"]
    sa = _s(t, "item_accent_a")
    sb = _s(t, "item_accent_b")
    sc = _s(t, "connector_color")
    # 远景：大墨晕
    parts.append(f'<circle cx="{w*0.80}" cy="{h*0.15}" r="45" fill="{sb}" opacity="{op*0.08}"/>')
    parts.append(f'<circle cx="{w*0.14}" cy="{h*0.85}" r="35" fill="{sa}" opacity="{op*0.06}"/>')
    # 中景：墨点
    for i in range(2):
        cx = w * (0.72 + i * 0.15)
        cy = h * (0.18 + (i % 2) * 0.50)
        r = 20 + i * 12
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{sb}" opacity="{op * 0.12}"/>')
    # 中景：笔触曲线
    parts.append(
        f'<path d="M{w*0.6},{h*0.5} Q{w*0.75},{h*0.42} {w*0.9},{h*0.48}" '
        f'fill="none" stroke="{sb}" stroke-width="1.2" opacity="{op * 0.6}" stroke-linecap="round"/>'
    )
    parts.append(
        f'<path d="M{w*0.55},{h*0.70} Q{w*0.70},{h*0.65} {w*0.85},{h*0.68}" '
        f'fill="none" stroke="{sa}" stroke-width="0.8" opacity="{op * 0.4}" stroke-linecap="round"/>'
    )
    # 中景：圆环
    parts.append(f'<circle cx="{w*0.85}" cy="{h*0.15}" r="18" fill="none" stroke="{sa}" stroke-width="0.8" opacity="{op * 0.5}"/>')
    # 近景：小方块（印章感）
    parts.append(f'<rect x="{w*0.82}" y="{h*0.72}" width="14" height="14" fill="{sa}" opacity="{op * 0.3}" rx="2"/>')
    # 近景：小点
    for i in range(3):
        dx = w * (0.70 + i * 0.08)
        dy = h * (0.90 - i * 0.03)
        parts.append(f'<circle cx="{dx}" cy="{dy}" r="2" fill="{sb}" opacity="{op*0.4}"/>')
    return "\n    ".join(parts)


def _svg_decor_neon(t, w, h):
    parts = []
    p = t["palette"]
    op = t["decor"]["opacity"]
    sa = _s(t, "item_accent_a")
    sb = _s(t, "item_accent_b")
    sc = _s(t, "connector_color")
    hex_r = 24
    # 远景：大六边形低透明度
    pts_far = []
    for j in range(6):
        angle = math.pi / 3 * j - math.pi / 6
        px = w * 0.82 + 40 * math.cos(angle)
        py = h * 0.12 + 40 * math.sin(angle)
        pts_far.append(f"{px:.1f},{py:.1f}")
    parts.append(f'<polygon points="{" ".join(pts_far)}" fill="{sa}" opacity="{op*0.06}"/>')
    # 中景：六边形
    for i in range(2):
        cx = w * (0.72 + i * 0.16)
        cy = h * (0.15 + (i % 2) * 0.55)
        pts = []
        for j in range(6):
            angle = math.pi / 3 * j - math.pi / 6
            px = cx + hex_r * (1 + i * 0.15) * math.cos(angle)
            py = cy + hex_r * (1 + i * 0.15) * math.sin(angle)
            pts.append(f"{px:.1f},{py:.1f}")
        points_str = " ".join(pts)
        parts.append(f'<polygon points="{points_str}" fill="none" stroke="{sa}" stroke-width="0.7" opacity="{op * 0.6}"/>')
    # 中景：折线
    parts.append(
        f'<path d="M{w*0.65},{h*0.85} L{w*0.75},{h*0.85} L{w*0.80},{h*0.78} L{w*0.92},{h*0.78}" '
        f'fill="none" stroke="{sa}" stroke-width="0.6" opacity="{op * 0.4}"/>'
    )
    parts.append(f'<circle cx="{w*0.88}" cy="{h*0.2}" r="14" fill="none" stroke="{sb}" stroke-width="0.7" opacity="{op * 0.5}"/>')
    # 近景：小点
    for i in range(4):
        dx = w * (0.68 + i * 0.07)
        dy = h * (0.92 - i * 0.03)
        parts.append(f'<circle cx="{dx}" cy="{dy}" r="2" fill="{sa}" opacity="{op*0.45}"/>')
    # 近景：小三角
    tx, ty = w*0.15, h*0.40
    ts = 8
    parts.append(f'<polygon points="{tx},{ty-ts} {tx+ts},{ty+ts} {tx-ts},{ty+ts}" fill="none" stroke="{sb}" stroke-width="0.6" opacity="{op*0.35}"/>')
    return "\n    ".join(parts)



def _svg_decor_constellation(t, w, h):
    """indigo 专属：星图/星座风格，体现认知与沉思"""
    parts = []
    p = t["palette"]
    op = t["decor"]["opacity"]
    sa = _s(t, "item_accent_a")
    sb = _s(t, "item_accent_b")
    sc = _s(t, "connector_color")
    # 远景：大星云
    parts.append(f'<circle cx="{w*0.75}" cy="{h*0.20}" r="50" fill="{sa}" opacity="{op*0.06}"/>')
    parts.append(f'<circle cx="{w*0.20}" cy="{h*0.80}" r="40" fill="{sc}" opacity="{op*0.05}"/>')
    # 中景：星座连线（3组）
    star_groups = [
        # 第一组：三角形
        [(0.70, 0.12), (0.82, 0.18), (0.76, 0.28)],
        # 第二组：四边形
        [(0.78, 0.55), (0.88, 0.50), (0.90, 0.62), (0.82, 0.66)],
        # 第三组：小三角
        [(0.68, 0.78), (0.78, 0.82), (0.73, 0.90)],
    ]
    for gi, group in enumerate(star_groups):
        color = sa if gi % 2 == 0 else sb
        # 画连线
        for i in range(len(group)):
            x1, y1 = w * group[i][0], h * group[i][1]
            x2, y2 = w * group[(i + 1) % len(group)][0], h * group[(i + 1) % len(group)][1]
            parts.append(
                f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
                f'stroke="{color}" stroke-width="0.6" opacity="{op * 0.5}"/>'
            )
        # 画星点
        for sx, sy in group:
            parts.append(f'<circle cx="{w*sx:.0f}" cy="{h*sy:.0f}" r="2.5" fill="{color}" opacity="{op * 0.8}"/>')
            # 星芒
            parts.append(
                f'<line x1="{w*sx-5:.0f}" y1="{h*sy:.0f}" x2="{w*sx+5:.0f}" y2="{h*sy:.0f}" '
                f'stroke="{color}" stroke-width="0.4" opacity="{op * 0.4}"/>'
            )
            parts.append(
                f'<line x1="{w*sx:.0f}" y1="{h*sy-5:.0f}" x2="{w*sx:.0f}" y2="{h*sy+5:.0f}" '
                f'stroke="{color}" stroke-width="0.4" opacity="{op * 0.4}"/>'
            )
    # 近景：散落星点
    for i in range(6):
        dx = w * (0.65 + i * 0.06)
        dy = h * (0.40 + (i % 3) * 0.18)
        parts.append(f'<circle cx="{dx:.0f}" cy="{dy:.0f}" r="1.2" fill="{sb}" opacity="{op*0.5}"/>')
    # 近景：弧线（思维轨迹）
    parts.append(
        f'<path d="M{w*0.6},{h*0.35} Q{w*0.72},{h*0.30} {w*0.85},{h*0.38}" '
        f'fill="none" stroke="{sb}" stroke-width="0.6" opacity="{op * 0.3}"/>'
    )
    parts.append(
        f'<path d="M{w*0.65},{h*0.70} Q{w*0.78},{h*0.65} {w*0.92},{h*0.72}" '
        f'fill="none" stroke="{sc}" stroke-width="0.5" opacity="{op * 0.25}"/>'
    )
    return "\n    ".join(parts)


_DECOR_RENDERERS = {
    "circles": _svg_decor_circles,
    "dots": _svg_decor_dots,
    "lines": _svg_decor_lines,
    "organic": _svg_decor_organic,
    "brush": _svg_decor_brush,
    "neon": _svg_decor_neon,
    "constellation": _svg_decor_constellation,
}


def render_svg_decor(theme_name, width, height):
    t = get_theme(theme_name)
    style = t["decor"]["style"]
    renderer = _DECOR_RENDERERS.get(style)
    if not renderer:
        return ""
    base_svg = renderer(t, width, height)

    # density 分级增强：rich 模式追加渐变色条 + 额外装饰层
    density = t["decor"].get("density", "normal")
    use_gradient = t["decor"].get("gradient_accents", False)

    if density == "rich" and use_gradient:
        from scripts.elements.shape_primitives import svg_gradient_rect, svg_gradient_line
        p = t["palette"]
        # 顶部渐变色条
        defs1, rect1 = svg_gradient_rect(
            0, 0, width, 4, theme_name,
            direction="horizontal", color_keys=("accent", "gold"),
            opacity=0.35, radius=0, id_suffix="top-bar"
        )
        # 底部渐变色条
        defs2, rect2 = svg_gradient_rect(
            0, height - 4, width, 4, theme_name,
            direction="horizontal", color_keys=("gold", "cyan"),
            opacity=0.20, radius=0, id_suffix="bottom-bar"
        )
        # 右侧渐变竖条
        defs3, rect3 = svg_gradient_rect(
            width - 60, 0, 60, height, theme_name,
            direction="vertical", color_keys=("accent", "cyan"),
            opacity=0.04, radius=0, id_suffix="side-glow"
        )
        base_svg = f"{defs1}\n{defs2}\n{defs3}\n{rect1}\n{rect2}\n{rect3}\n{base_svg}"

    elif density == "rich":
        # rich 但不用渐变：增加额外装饰圆点
        p = t["palette"]
        sa = _s(t, "item_accent_a")
        sb = _s(t, "item_accent_b")
        op = t["decor"]["opacity"]
        extras = []
        for i in range(6):
            dx = width * (0.60 + i * 0.06)
            dy = height * (0.85 - i * 0.04)
            extras.append(f'<circle cx="{dx}" cy="{dy}" r="2" fill="{sa if i%2==0 else sb}" opacity="{op*0.4}"/>')
        base_svg = base_svg + "\n" + "\n".join(extras)

    return base_svg


def _s(theme, key, fallback_key=None):
    """从主题的 semantic 字段取值，缺失时回退到 palette"""
    sem = theme.get("semantic", {})
    val = sem.get(key)
    if val:
        return val
    if fallback_key:
        return theme["palette"].get(fallback_key, theme["palette"]["accent"])
    return theme["palette"]["accent"]


def _item_accent(theme, index):
    """根据索引返回列表项的交替色"""
    return _s(theme, "item_accent_a") if index % 2 == 0 else _s(theme, "item_accent_b")


def _palette(theme, index):
    """多色调色板：从主题语义色中循环取色，支持5+种颜色，适合图表场景

    依次取：accent_a → accent_b → connector → highlight_ring → palette.accent → palette.gold → 循环
    """
    sa = _s(theme, "item_accent_a")
    sb = _s(theme, "item_accent_b")
    sc = _s(theme, "connector_color")
    sh = _s(theme, "highlight_ring")
    p = theme.get("palette", {})
    sd = p.get("accent", sa)
    se = p.get("gold", sb)
    colors = [sa, sb, sc, sh, sd, se]
    return colors[index % len(colors)]


def _svg_item_card(x, y, w, h, theme, index, radius_override=None):
    """生成一个带左侧色条+序号圆点的列表项小卡片"""
    c = theme["card"]
    f = theme["font"]
    color = _item_accent(theme, index)
    badge_bg = _s(theme, "badge_bg")
    r = radius_override if radius_override else c["radius"]
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{c["fill"]}" opacity="0.4"/>\n'
        f'  <rect x="{x}" y="{y}" width="3" height="{h}" rx="1" fill="{color}" opacity="0.7"/>\n'
        f'  <circle cx="{x + 25}" cy="{y + h//2}" r="10" fill="{badge_bg}"/>\n'
        f'  <text x="{x + 25}" y="{y + h//2 + 4}" text-anchor="middle" font-family="{f["body"]}" font-size="12" font-weight="700" fill="{color}">{index+1}</text>'
    )


def _svg_connector_arrow(x1, y1, x2, y2, theme, horizontal=False):
    """生成一条带箭头的连接线"""
    color = _s(theme, "connector_color")
    if horizontal:
        # 水平箭头
        return (
            f'<line x1="{x1}" y1="{y1}" x2="{x2 - 6}" y2="{y2}" stroke="{color}" stroke-width="2" opacity="0.5"/>\n'
            f'  <polygon points="{x2-10},{y2-4} {x2-10},{y2+4} {x2},{y2}" fill="{color}" opacity="0.4"/>'
        )
    else:
        # 垂直箭头
        return (
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2 - 6}" stroke="{color}" stroke-width="1.5" opacity="0.3"/>\n'
            f'  <polygon points="{x2-4},{y2-10} {x2+4},{y2-10} {x2},{y2}" fill="{color}" opacity="0.3"/>'
        )


def _svg_bottom_bar(width, height, theme):
    """生成底部装饰条"""
    color = _s(theme, "divider_accent")
    return f'<rect x="40" y="{height-44}" width="{width-80}" height="4" rx="2" fill="{color}" opacity="0.15"/>'


def _card_text_layout(cx, cy, cw, ch, elements, padding=14):
    """卡片内文字自适应垂直居中布局

    Args:
        cx, cy, cw, ch: 卡片坐标和尺寸
        elements: list of dict, 每项含:
            - type: 'badge' | 'title' | 'divider' | 'desc' | 'progress' | 'value' | 'label' | 'sub'
            - h: 该元素占用的高度(含间距)
        padding: 卡片内边距

    Returns:
        dict: 每个元素的 (x, y) 坐标，key为元素type+索引
        原则: 所有元素整体在卡片内垂直居中
    """
    total_h = sum(e.get("h", 20) for e in elements)
    start_y = cy + (ch - total_h) // 2
    start_y = max(start_y, cy + padding)  # 不超出卡片顶部

    result = {}
    cur_y = start_y
    for i, e in enumerate(elements):
        etype = e.get("type", f"el_{i}")
        eh = e.get("h", 20)
        result[f"{etype}_{i}"] = (cx + padding, cur_y, cw - 2 * padding, eh)
        cur_y += eh

    return result


def _auto_layout(n_items, area_x, area_y, area_w, area_h, cols=1, min_item_h=60, gap=10):
    """自适应布局：根据内容数量自动计算卡片大小和起始位置，使内容居中铺满

    返回: list of (x, y, w, h) 每个卡片的坐标和尺寸
    原则:
    - 内容少时：卡片放大，整体居中
    - 内容多时：卡片缩小，均匀铺满
    - 始终保持视觉匀称
    """
    if n_items <= 0:
        return []

    rows = max(1, (n_items + cols - 1) // cols)
    actual_rows = min(rows, 6)  # 最多6行
    actual_items = min(n_items, cols * actual_rows)

    # 计算可用空间
    total_gap_x = gap * max(cols - 1, 0)
    total_gap_y = gap * max(actual_rows - 1, 0)
    avail_w = area_w - total_gap_x
    avail_h = area_h - total_gap_y

    item_w = avail_w // cols
    # 每项高度：先按均分算，但不低于min_item_h
    item_h = max(min_item_h, avail_h // actual_rows)

    # 如果内容不够铺满，计算实际内容块的总高度，然后居中
    content_block_h = actual_rows * item_h + total_gap_y
    if content_block_h < area_h:
        # 内容块偏移，使其垂直居中
        offset_y = (area_h - content_block_h) // 2
    else:
        offset_y = 0
        item_h = avail_h // actual_rows  # 重新均分

    # 内容块水平居中（当列数少于可用列时）
    content_block_w = cols * item_w + total_gap_x
    offset_x = (area_w - content_block_w) // 2

    positions = []
    for i in range(actual_items):
        col = i % cols
        row = i // cols
        x = area_x + offset_x + col * (item_w + gap)
        y = area_y + offset_y + row * (item_h + gap)
        positions.append((x, y, item_w, item_h))

    return positions


def _svg_title_underline(width, theme):
    """生成标题下方装饰线"""
    color = _s(theme, "divider_accent")
    return f'<rect x="{width*0.3}" y="72" width="{width*0.4}" height="2" rx="1" fill="{color}" opacity="0.3"/>'


def _wrap_text(text, max_chars_per_line):
    """将长文本按指定字数自动换行，返回行列表"""
    lines = []
    remaining = text
    while remaining:
        lines.append(remaining[:max_chars_per_line])
        remaining = remaining[max_chars_per_line:]
    return lines


def _render_multiline_text(x, y, text, font_family, font_size, fill, max_chars_per_line=20, line_height=None, text_anchor="start", font_weight=""):
    """渲染支持自动换行的多行文本SVG"""
    if line_height is None:
        line_height = font_size * 1.6
    lines = _wrap_text(text, max_chars_per_line)
    parts = []
    weight_attr = f' font-weight="{font_weight}"' if font_weight else ""
    for i, line in enumerate(lines):
        ly = y + i * line_height
        parts.append(
            f'<text x="{x}" y="{ly}" text-anchor="{text_anchor}" '
            f'font-family="{font_family}" font-size="{font_size}"{weight_attr} fill="{fill}">{line}</text>'
        )
    return "\n  ".join(parts), len(lines)


def render_svg_atmosphere_defs(theme_name, width, height):
    t = get_theme(theme_name)
    atm = t.get("atmosphere", {})
    p = t["palette"]
    bg = t["bg"]
    parts = []

    # 纯色背景（bg1），不再使用渐变，确保文字对比度稳定
    parts.append(
        f'<solidColor id="bg-grad" color="{bg["bg1"]}"/>'
    )

    for i, glow in enumerate(atm.get("glow", [])):
        color_key = glow.get("color", "accent")
        color_val = p.get(color_key, p["accent"])
        # glow 透明度降低一半，仅作为微纹理
        alpha = glow.get("alpha", 0.06) * 0.4
        cx = glow.get("cx", 0.5) * width
        cy = glow.get("cy", 0.5) * height
        r = glow.get("r", 0.4) * max(width, height)
        parts.append(
            f'<radialGradient id="glow-{i}" cx="{cx}" cy="{cy}" r="{r}" gradientUnits="userSpaceOnUse">\n'
            f'  <stop offset="0%" stop-color="{color_val}" stop-opacity="{alpha}"/>\n'
            f'  <stop offset="100%" stop-color="{color_val}" stop-opacity="0"/>\n'
            f'</radialGradient>'
        )

    grain = atm.get("grain", 0)
    if grain > 0:
        parts.append(
            f'<filter id="grain">\n'
            f'  <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/>\n'
            f'  <feColorMatrix type="saturate" values="0"/>\n'
            f'  <feComponentTransfer><feFuncA type="linear" slope="{grain}"/></feComponentTransfer>\n'
            f'  <feBlend in="SourceGraphic" mode="overlay"/>\n'
            f'</filter>'
        )

    return "\n  ".join(parts)


def render_svg_atmosphere_body(theme_name, width, height):
    t = get_theme(theme_name)
    atm = t.get("atmosphere", {})
    parts = []

    for i, glow in enumerate(atm.get("glow", [])):
        parts.append(
            f'<rect width="{width}" height="{height}" fill="url(#glow-{i})"/>'
        )

    grain = atm.get("grain", 0)
    if grain > 0:
        parts.append(
            f'<rect width="{width}" height="{height}" filter="url(#grain)" opacity="0.5"/>'
        )

    return "\n  ".join(parts)


def _render_bg_layout(t, width, height):
    bg = t["bg"]
    layout = bg.get("layout", "solid")
    parts = []
    defs = []

    if layout == "side-panel":
        # 改为柔和渐变，不再有硬边竖线
        px = int(width * bg.get("panel_x", 0.62))
        pc = bg.get("panel_color", "#3A3C58")
        grad_id = "bg-side-grad"
        defs.append(
            f'<linearGradient id="{grad_id}" x1="{px}" y1="0" x2="{width}" y2="0" gradientUnits="userSpaceOnUse">\n'
            f'  <stop offset="0%" stop-color="{pc}" stop-opacity="0"/>\n'
            f'  <stop offset="40%" stop-color="{pc}" stop-opacity="0.08"/>\n'
            f'  <stop offset="100%" stop-color="{pc}" stop-opacity="0.12"/>\n'
            f'</linearGradient>'
        )
        parts.append(f'<rect width="{width}" height="{height}" fill="url(#{grad_id})"/>')

    elif layout == "soft-glow":
        gc = bg.get("glow_color", "#F5EDE0")
        gcx = bg.get("glow_cx", 0.78)
        gcy = bg.get("glow_cy", 0.72)
        gr = bg.get("glow_r", 0.4)
        ga = bg.get("glow_alpha", 0.3) * 0.3  # 降低透明度
        cx = int(width * gcx)
        cy = int(height * gcy)
        r = int(max(width, height) * gr)
        grad_id = "bg-layout-glow"
        defs.append(
            f'<radialGradient id="{grad_id}" cx="{cx}" cy="{cy}" r="{r}" gradientUnits="userSpaceOnUse">\n'
            f'  <stop offset="0%" stop-color="{gc}" stop-opacity="{ga}"/>\n'
            f'  <stop offset="100%" stop-color="{gc}" stop-opacity="0"/>\n'
            f'</radialGradient>'
        )
        parts.append(f'<rect width="{width}" height="{height}" fill="url(#{grad_id})"/>')

    elif layout == "accent-edge":
        ec = bg.get("edge_color", "#2A2A40")
        ew = bg.get("edge_width", 3)
        parts.append(f'<rect x="0" y="0" width="{ew}" height="{height}" fill="{ec}"/>')

    elif layout == "curved-horizon":
        sc = bg.get("sky_color", "#C8D8C0")
        sa = bg.get("sky_alpha", 0.2) * 0.3  # 降低透明度
        hy = bg.get("horizon_y", 0.55)
        cd = bg.get("curve_depth", 0.06)
        curve_y = int(height * hy)
        dip = int(height * cd)
        grad_id = "bg-sky-grad"
        defs.append(
            f'<linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">\n'
            f'  <stop offset="0%" stop-color="{sc}" stop-opacity="{sa}"/>\n'
            f'  <stop offset="70%" stop-color="{sc}" stop-opacity="{sa * 0.3}"/>\n'
            f'  <stop offset="100%" stop-color="{sc}" stop-opacity="0"/>\n'
            f'</linearGradient>'
        )
        parts.append(
            f'<path d="M0,0 L{width},0 L{width},{curve_y} Q{width//2},{curve_y + dip} 0,{curve_y} Z" fill="url(#{grad_id})"/>'
        )

    elif layout == "ink-wash":
        ic = bg.get("ink_color", "#2E2820")
        ix = bg.get("ink_x", 0.65)
        io = bg.get("ink_opacity", 0.08) * 0.4  # 降低透明度
        cx = int(width * ix)
        r = int(min(width, height) * 0.45)
        parts.append(f'<circle cx="{cx}" cy="{int(height * 0.4)}" r="{r}" fill="{ic}" opacity="{io}"/>')
        parts.append(f'<circle cx="{cx + 50}" cy="{int(height * 0.55)}" r="{int(r * 0.5)}" fill="{ic}" opacity="{io * 0.6}"/>')

    elif layout == "diagonal-beam":
        bc = bg.get("beam_color", "#FF4D8D")
        bo = bg.get("beam_opacity", 0.06) * 0.4  # 降低透明度
        bw = int(width * 0.22)
        parts.append(
            f'<polygon points="0,0 {bw},0 {width},{height} {width - bw},{height}" fill="{bc}" opacity="{bo}"/>'
        )

    body = "\n  ".join(parts)
    defs_str = "\n  ".join(defs)
    return defs_str, body


def _svg_header(theme_name, width, height):
    atm_defs = render_svg_atmosphere_defs(theme_name, width, height)
    atm_body = render_svg_atmosphere_body(theme_name, width, height)
    t = get_theme(theme_name)
    bg_defs, bg_layout = _render_bg_layout(t, width, height)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">\n'
        f'  <defs>\n'
        f'    {atm_defs}\n'
        f'    {bg_defs}\n'
        f'  </defs>\n'
        f'  <rect width="{width}" height="{height}" fill="url(#bg-grad)"/>\n'
        f'  {bg_layout}\n'
        f'  {atm_body}'
    )


def render_svg_cover(title, subtitle="", author="", theme_name="dark", width=900, height=383):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    f = t["font"]

    display_title = title[:28] + ("..." if len(title) > 28 else "")
    display_author = author[:20] + ("..." if len(author) > 20 else "")
    display_sub = subtitle[:50] + ("..." if len(subtitle) > 50 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    accent_x = 50
    accent_w = 60
    accent_y = height * 0.28

    svg = f'''{header}
  {decor_svg}
  <rect x="{accent_x}" y="{accent_y}" width="{accent_w}" height="3" fill="{_s(t, "divider_accent")}" rx="1.5"/>
  <text x="{accent_x}" y="{accent_y + 38}" font-family="{f["display"]}" font-size="32" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  <text x="{accent_x}" y="{accent_y + 62}" font-family="{f["body"]}" font-size="15" fill="{tx["secondary"]}">{display_author}</text>
  <line x1="{accent_x}" y1="{height - 50}" x2="{width - 50}" y2="{height - 50}" stroke="{_s(t, "divider_accent")}" stroke-width="0.6" opacity="0.25"/>
  <text x="{accent_x}" y="{height - 28}" font-family="{f["body"]}" font-size="12" fill="{tx["secondary"]}" opacity="0.8">{display_sub}</text>
  <circle cx="{width - 55}" cy="{height - 30}" r="3" fill="{_s(t, "highlight_ring")}" opacity="0.5"/>
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_card(title, items, theme_name="dark", width=800, height=600, cols=None, highlight=False):
    """列举要点卡 / 总结清单：自适应铺满 + 大号背景序号 + 每项含描述/进度条 + 装饰层

    布局：标题区 → 自适应条目区(内容少时放大居中，多时均匀铺满) → 高亮总结块(可选) → 底部标签
    特点：_auto_layout自动居中铺满、每项有进度条和描述、背景装饰
    参数：
        cols: 列数，None自动(>4项双列)，1强制单列，2强制双列
        highlight: 是否显示高亮总结块
    """
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    # ── 装饰层 ──
    bg_num = f'<text x="{width - 30}" y="100" text-anchor="end" font-family="{f["display"]}" font-size="120" font-weight="900" fill="{_s(t, "divider_accent")}" opacity="0.04">{len(items)}</text>'
    deco_circle = f'<circle cx="50" cy="{height - 50}" r="50" fill="{_s(t, "highlight_ring")}" opacity="0.03"/>'

    # 标题区
    margin = 35
    title_area = (
        f'<text x="{margin}" y="42" font-family="{f["display"]}" font-size="22" font-weight="700" fill="{tx["primary"]}">{display_title}</text>\n'
        f'  <rect x="{margin}" y="52" width="60" height="3" rx="1" fill="{_s(t, "divider_accent")}" opacity="0.6"/>\n'
        f'  <text x="{margin + 70}" y="55" font-family="{f["body"]}" font-size="12" fill="{tx["dim"]}">共 {len(items)} 项</text>'
    )

    # ── 自适应条目区 ──
    n_items = min(len(items), 8)
    # 自动决定列数
    if cols is None:
        actual_cols = 2 if n_items > 4 else 1
    else:
        actual_cols = cols
    # 底部预留空间
    bottom_reserve = 90 if highlight else 55
    # 内容区：从y=70到y=height-bottom_reserve
    positions = _auto_layout(n_items, margin, 70, width - 2 * margin, height - 70 - bottom_reserve, cols=actual_cols, min_item_h=55, gap=8)

    items_svg = []
    for i, (ix, iy, iw, ih) in enumerate(positions):
        num_color = _item_accent(t, i)
        item = items[i]
        item_text = (item[:22] + ("..." if len(item) > 22 else "")) if isinstance(item, str) else str(item)[:22]
        desc = ""
        if isinstance(item, dict):
            item_text = item.get("title", item.get("text", ""))[:22]
            desc = item.get("desc", "")[:35]

        # 卡片内部文字自适应垂直居中
        el_defs = [
            {"type": "title", "h": 22},
            {"type": "desc", "h": 16 if (desc and ih > 40) else 0},
            {"type": "spacer", "h": max(4, ih // 8)},
            {"type": "progress", "h": 12},
        ]
        layout = _card_text_layout(ix + 50, iy, iw - 55, ih, el_defs, padding=10)

        # 大号背景序号
        items_svg.append(
            f'<text x="{ix + 8}" y="{iy + ih - 8}" font-family="{f["display"]}" font-size="{min(48, ih - 5)}" font-weight="900" fill="{num_color}" opacity="0.08">{i+1:02d}</text>'
        )

        # 内容卡片
        ic_x = ix + 50
        ic_w = iw - 55
        items_svg.append(
            f'<rect x="{ic_x}" y="{iy}" width="{ic_w}" height="{ih}" rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.4"/>\n'
            f'  <rect x="{ic_x}" y="{iy}" width="3" height="{ih}" rx="1" fill="{num_color}" opacity="0.7"/>'
        )

        # 标题文字
        _, t_y, t_w, _ = layout["title_0"]
        items_svg.append(
            f'<text x="{ic_x + 16}" y="{t_y + 16}" font-family="{f["body"]}" font-size="15" font-weight="600" fill="{tx["primary"]}">{item_text}</text>'
        )

        # 描述文字
        if desc and ih > 40:
            _, d_y, d_w, _ = layout["desc_1"]
            items_svg.append(
                f'<text x="{ic_x + 16}" y="{d_y + 12}" font-family="{f["body"]}" font-size="11" fill="{tx["secondary"]}">{desc}</text>'
            )

        # 进度条
        _, p_y, p_w, _ = layout["progress_3"]
        progress_pct = 40 + (i * 17) % 55
        items_svg.append(
            f'<rect x="{ic_x + 16}" y="{p_y + 4}" width="{p_w - 16}" height="4" rx="2" fill="{c["fill"]}" opacity="0.6"/>\n'
            f'  <rect x="{ic_x + 16}" y="{p_y + 4}" width="{int((p_w - 16) * progress_pct / 100)}" height="4" rx="2" fill="{num_color}" opacity="0.35"/>'
        )

    items_joined = "\n  ".join(items_svg)

    # 高亮总结块（可选）
    highlight_block = ""
    if highlight:
        hl_y = height - bottom_reserve + 5
        highlight_block = (
            f'<rect x="{margin}" y="{hl_y}" width="{width - 2 * margin}" height="32" rx="{c["radius"]}" fill="{_s(t, "highlight_ring")}" opacity="0.06"/>\n'
            f'  <rect x="{margin}" y="{hl_y}" width="4" height="32" rx="2" fill="{_s(t, "highlight_ring")}" opacity="0.4"/>\n'
            f'  <text x="{margin + 14}" y="{hl_y + 21}" font-family="{f["body"]}" font-size="13" font-weight="600" fill="{tx["primary"]}">核心总结 · {len(items)} 项关键要点</text>'
        )

    # 底部标签组
    tag_labels = [str(items[i])[:8] for i in range(min(4, len(items)))]
    if len(items) > 4:
        tag_labels[-1] = f"共{len(items)}项"
    tags_svg_parts = []
    total_tag_w = sum(len(tg) * 12 + 20 for tg in tag_labels) + 10 * max(len(tag_labels) - 1, 0)
    tx_start = (width - total_tag_w) / 2
    tags_y = height - 48
    for i, tg in enumerate(tag_labels):
        tw = len(tg) * 12 + 20
        tags_svg_parts.append(
            f'<rect x="{tx_start}" y="{tags_y}" width="{tw}" height="22" rx="11" fill="{_s(t, "badge_bg")}"/>\n'
            f'  <text x="{tx_start + tw/2}" y="{tags_y + 16}" text-anchor="middle" font-family="{f["body"]}" font-size="11" fill="{tx["primary"]}">{tg}</text>'
        )
        tx_start += tw + 10
    tags_joined = "\n  ".join(tags_svg_parts)

    svg = f'''{header}
  {decor_svg}
  {bg_num}
  {deco_circle}
  {title_area}
  {items_joined}
  {highlight_block}
  {tags_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_stat(value, label, sublabel="", trend="", tags=None, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_value = value[:14] + ("..." if len(value) > 14 else "")
    display_label = label[:30] + ("..." if len(label) > 30 else "")
    display_sub = sublabel[:40] + ("..." if len(sublabel) > 40 else "")
    tags = tags or []

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    # 背景大卡片
    stat_card = svg_card(60, height * 0.12, width - 120, height * 0.76, theme_name)

    # 装饰环
    ring1 = svg_circle(width / 2, height * 0.33, 90, theme_name, stroke=_s(t, "highlight_ring"))
    ring2 = svg_circle(width / 2, height * 0.33, 110, theme_name, stroke=_s(t, "item_accent_b"))

    # 顶部小标签
    tag_w = len(display_label) * 14 + 24
    tag_x = (width - tag_w) / 2

    sublabel_svg = ""
    if display_sub:
        sublabel_svg = f'<text x="{width/2}" y="{height*0.52}" text-anchor="middle" font-family="{f["body"]}" font-size="14" fill="{tx["secondary"]}">{display_sub}</text>'

    # 趋势指示
    trend_svg = ""
    if trend:
        trend_display = trend[:10]
        trend_svg = f'<text x="{width/2}" y="{height*0.60}" text-anchor="middle" font-family="{f["mono"]}" font-size="16" font-weight="600" fill="{_s(t, "success")}">{trend_display}</text>'

    # 底部标签组（最多4个）
    tags_svg_parts = []
    if tags:
        tag_labels = [tg[:8] for tg in tags[:4]]
        total_tag_w = sum(len(tg) * 12 + 20 for tg in tag_labels) + 10 * (len(tag_labels) - 1)
        tx_start = (width - total_tag_w) / 2
        for i, tg in enumerate(tag_labels):
            tw = len(tg) * 12 + 20
            tags_svg_parts.append(
                f'<rect x="{tx_start}" y="{height*0.68}" width="{tw}" height="26" rx="13" fill="{_s(t, "badge_bg")}"/>\n'
                f'  <text x="{tx_start + tw/2}" y="{height*0.68+18}" text-anchor="middle" font-family="{f["body"]}" font-size="12" fill="{tx["primary"]}">{tg}</text>'
            )
            tx_start += tw + 10
    tags_joined = "\n  ".join(tags_svg_parts)

    svg = f'''{header}
  {decor_svg}
  {stat_card}
  {ring2}
  {ring1}
  <text x="{width/2}" y="{height*0.35}" text-anchor="middle" font-family="{f["display"]}" font-size="72" font-weight="800" fill="{_s(t, "highlight_ring")}">{display_value}</text>
  <rect x="{tag_x}" y="{height*0.44}" width="{tag_w}" height="28" rx="14" fill="{_s(t, "badge_bg")}"/>
  <text x="{width/2}" y="{height*0.49}" text-anchor="middle" font-family="{f["body"]}" font-size="18" font-weight="600" fill="{tx["primary"]}">{display_label}</text>
  {sublabel_svg}
  {trend_svg}
  {tags_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_quote(text, source="", context="", tags=None, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_text = text[:200] + ("..." if len(text) > 200 else "")
    display_source = source[:30] + ("..." if len(source) > 30 else "")
    display_context = context[:60] + ("..." if len(context) > 60 else "")
    tags = tags or []

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    # 引言卡片背景
    quote_card = svg_card(60, height * 0.10, width - 120, height * 0.80, theme_name)

    # 多行文本自动换行
    text_svg, text_lines = _render_multiline_text(
        width / 2, height * 0.30, display_text,
        f["display"], 22, tx["primary"],
        max_chars_per_line=18, line_height=36,
        text_anchor="middle", font_weight="700"
    )

    # 根据行数调整出处位置
    source_y = height * 0.30 + text_lines * 36 + 20
    source_svg = ""
    if display_source:
        source_svg = f'<text x="{width/2}" y="{source_y}" text-anchor="middle" font-family="{f["body"]}" font-size="14" fill="{tx["secondary"]}">—— {display_source}</text>'

    # 上下文描述
    context_svg = ""
    if display_context:
        ctx_y = source_y + 30 if display_source else source_y + 10
        context_svg = f'<text x="{width/2}" y="{ctx_y}" text-anchor="middle" font-family="{f["body"]}" font-size="13" fill="{tx["dim"]}">{display_context}</text>'

    # 底部标签组（最多4个）
    tags_svg_parts = []
    if tags:
        tag_labels = [tg[:8] for tg in tags[:4]]
        total_tag_w = sum(len(tg) * 12 + 20 for tg in tag_labels) + 10 * (len(tag_labels) - 1)
        tx_start = (width - total_tag_w) / 2
        tags_y = height * 0.82
        for i, tg in enumerate(tag_labels):
            tw = len(tg) * 12 + 20
            tags_svg_parts.append(
                f'<rect x="{tx_start}" y="{tags_y}" width="{tw}" height="24" rx="12" fill="{_s(t, "badge_bg")}"/>\n'
                f'  <text x="{tx_start + tw/2}" y="{tags_y+17}" text-anchor="middle" font-family="{f["body"]}" font-size="11" fill="{tx["primary"]}">{tg}</text>'
            )
            tx_start += tw + 10
    tags_joined = "\n  ".join(tags_svg_parts)

    svg = f'''{header}
  {decor_svg}
  {quote_card}
  <text x="{width*0.12}" y="{height*0.24}" font-family="{f["display"]}" font-size="60" fill="{_s(t, "highlight_ring")}" opacity="0.25">"</text>
  {text_svg}
  {source_svg}
  {context_svg}
  {tags_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_compare(title, left_title, right_title, left_items, right_items, theme_name="dark", width=800, height=600):
    """A vs B 对比卡：自适应双栏铺满 + 评分徽章 + 每项含图标/进度条 + 高亮结论 + 装饰层

    布局：标题 → 自适应左右双栏(条目自动铺满高度) → VS徽章 → 高亮结论
    特点：_auto_layout让条目自动铺满、内容少时居中放大
    """
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")
    left_accent = _s(t, "item_accent_a")
    right_accent = _s(t, "item_accent_b")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    # 布局参数
    margin = 30
    title_h = 60
    bottom_h = 55
    gap = 14
    col_w = (width - 2 * margin - gap) // 2
    col_top = title_h
    col_h = height - title_h - bottom_h - margin
    left_x = margin
    right_x = margin + col_w + gap

    # ── 装饰层 ──
    bg_vs = f'<text x="{width/2}" y="{height/2 + 30}" text-anchor="middle" font-family="{f["display"]}" font-size="180" font-weight="900" fill="{_s(t, "divider_accent")}" opacity="0.03">VS</text>'
    deco_l = f'<circle cx="{margin + 20}" cy="{title_h + 30}" r="35" fill="{left_accent}" opacity="0.04"/>'
    deco_r = f'<circle cx="{width - margin - 20}" cy="{title_h + 30}" r="35" fill="{right_accent}" opacity="0.04"/>'

    # 标题区
    title_area = (
        f'<text x="{width/2}" y="38" text-anchor="middle" font-family="{f["display"]}" font-size="22" font-weight="700" fill="{tx["primary"]}">{display_title}</text>\n'
        f'  <rect x="{width*0.35}" y="48" width="{width*0.3}" height="2" rx="1" fill="{_s(t, "divider_accent")}" opacity="0.3"/>'
    )

    # 左栏卡片
    left_card = svg_card(left_x, col_top, col_w, col_h, theme_name)
    left_top_bar = f'<rect x="{left_x}" y="{col_top}" width="{col_w}" height="4" rx="2" fill="{left_accent}" opacity="0.5"/>'
    left_score = min(len(left_items) * 20, 95)
    left_title_svg = (
        f'<text x="{left_x + 16}" y="{col_top + 32}" font-family="{f["display"]}" font-size="18" font-weight="700" fill="{left_accent}">{left_title[:12]}</text>\n'
        f'  <rect x="{left_x + col_w - 50}" y="{col_top + 16}" width="38" height="22" rx="11" fill="{left_accent}" opacity="0.15"/>\n'
        f'  <text x="{left_x + col_w - 31}" y="{col_top + 32}" text-anchor="middle" font-family="{f["mono"]}" font-size="12" font-weight="700" fill="{left_accent}">{left_score}</text>\n'
        f'  <rect x="{left_x + 16}" y="{col_top + 42}" width="{col_w - 32}" height="1" fill="{left_accent}" opacity="0.15"/>'
    )

    # 右栏卡片
    right_card = svg_card(right_x, col_top, col_w, col_h, theme_name)
    right_top_bar = f'<rect x="{right_x}" y="{col_top}" width="{col_w}" height="4" rx="2" fill="{right_accent}" opacity="0.5"/>'
    right_score = min(len(right_items) * 20, 95)
    right_title_svg = (
        f'<text x="{right_x + 16}" y="{col_top + 32}" font-family="{f["display"]}" font-size="18" font-weight="700" fill="{right_accent}">{right_title[:12]}</text>\n'
        f'  <rect x="{right_x + col_w - 50}" y="{col_top + 16}" width="38" height="22" rx="11" fill="{right_accent}" opacity="0.15"/>\n'
        f'  <text x="{right_x + col_w - 31}" y="{col_top + 32}" text-anchor="middle" font-family="{f["mono"]}" font-size="12" font-weight="700" fill="{right_accent}">{right_score}</text>\n'
        f'  <rect x="{right_x + 16}" y="{col_top + 42}" width="{col_w - 32}" height="1" fill="{right_accent}" opacity="0.15"/>'
    )

    # ── 自适应左栏条目 ──
    n_left = min(len(left_items), 5)
    left_positions = _auto_layout(n_left, left_x + 10, col_top + 50, col_w - 20, col_h - 60, cols=1, min_item_h=40, gap=6)

    left_items_svg = []
    for i, (ix, iy, iw, ih) in enumerate(left_positions):
        txt = left_items[i][:18] + ("..." if len(left_items[i]) > 18 else "")
        # 卡片内部文字自适应垂直居中
        el_defs = [
            {"type": "text", "h": 20},
            {"type": "spacer", "h": max(4, ih // 6)},
            {"type": "progress", "h": 10},
        ]
        layout = _card_text_layout(ix, iy, iw, ih, el_defs, padding=8)
        # 条目卡片
        left_items_svg.append(
            f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.3"/>\n'
            f'  <rect x="{ix}" y="{iy}" width="3" height="{ih}" rx="1" fill="{left_accent}" opacity="0.5"/>'
        )
        # 圆点图标 + 文字
        _, t_y, t_w, _ = layout["text_0"]
        left_items_svg.append(
            f'<circle cx="{ix + 16}" cy="{t_y + 10}" r="5" fill="{left_accent}" opacity="0.15"/>\n'
            f'  <circle cx="{ix + 16}" cy="{t_y + 10}" r="2" fill="{left_accent}" opacity="0.6"/>'
        )
        left_items_svg.append(
            f'<text x="{ix + 28}" y="{t_y + 14}" font-family="{f["body"]}" font-size="13" fill="{tx["primary"]}">{txt}</text>'
        )
        # 进度条
        _, p_y, p_w, _ = layout["progress_2"]
        bar_pct = 35 + (i * 19) % 60
        left_items_svg.append(
            f'<rect x="{ix + 16}" y="{p_y + 4}" width="{p_w - 16}" height="3" rx="1" fill="{c["fill"]}" opacity="0.5"/>\n'
            f'  <rect x="{ix + 16}" y="{p_y + 4}" width="{int((p_w - 16) * bar_pct / 100)}" height="3" rx="1" fill="{left_accent}" opacity="0.3"/>'
        )

    # ── 自适应右栏条目 ──
    n_right = min(len(right_items), 5)
    right_positions = _auto_layout(n_right, right_x + 10, col_top + 50, col_w - 20, col_h - 60, cols=1, min_item_h=40, gap=6)

    right_items_svg = []
    for i, (ix, iy, iw, ih) in enumerate(right_positions):
        txt = right_items[i][:18] + ("..." if len(right_items[i]) > 18 else "")
        el_defs = [
            {"type": "text", "h": 20},
            {"type": "spacer", "h": max(4, ih // 6)},
            {"type": "progress", "h": 10},
        ]
        layout = _card_text_layout(ix, iy, iw, ih, el_defs, padding=8)
        right_items_svg.append(
            f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.3"/>\n'
            f'  <rect x="{ix}" y="{iy}" width="3" height="{ih}" rx="1" fill="{right_accent}" opacity="0.5"/>'
        )
        _, t_y, t_w, _ = layout["text_0"]
        right_items_svg.append(
            f'<circle cx="{ix + 16}" cy="{t_y + 10}" r="5" fill="{right_accent}" opacity="0.15"/>\n'
            f'  <circle cx="{ix + 16}" cy="{t_y + 10}" r="2" fill="{right_accent}" opacity="0.6"/>'
        )
        right_items_svg.append(
            f'<text x="{ix + 28}" y="{t_y + 14}" font-family="{f["body"]}" font-size="13" fill="{tx["primary"]}">{txt}</text>'
        )
        _, p_y, p_w, _ = layout["progress_2"]
        bar_pct = 40 + (i * 13) % 55
        right_items_svg.append(
            f'<rect x="{ix + 16}" y="{p_y + 4}" width="{p_w - 16}" height="3" rx="1" fill="{c["fill"]}" opacity="0.5"/>\n'
            f'  <rect x="{ix + 16}" y="{p_y + 4}" width="{int((p_w - 16) * bar_pct / 100)}" height="3" rx="1" fill="{right_accent}" opacity="0.3"/>'
        )

    left_joined = "\n  ".join(left_items_svg)
    right_joined = "\n  ".join(right_items_svg)

    # VS 徽章
    vs_cx = width / 2
    vs_cy = col_top + col_h / 2
    vs_badge = (
        f'<circle cx="{vs_cx}" cy="{vs_cy}" r="22" fill="{c["fill"]}" stroke="{_s(t, "highlight_ring")}" stroke-width="2" opacity="0.9"/>\n'
        f'  <circle cx="{vs_cx}" cy="{vs_cy}" r="16" fill="{_s(t, "highlight_ring")}" opacity="0.06"/>\n'
        f'  <text x="{vs_cx}" y="{vs_cy + 5}" text-anchor="middle" font-family="{f["display"]}" font-size="13" font-weight="800" fill="{_s(t, "highlight_ring")}">VS</text>'
    )

    # 底部高亮结论块
    bottom_y = height - bottom_h
    bottom_card = f'<rect x="{margin}" y="{bottom_y}" width="{width - 2 * margin}" height="42" rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.35"/>'
    winner = left_title[:8] if left_score >= right_score else right_title[:8]
    bottom_text = (
        f'<rect x="{margin + 12}" y="{bottom_y + 10}" width="4" height="22" rx="2" fill="{_s(t, "highlight_ring")}" opacity="0.5"/>\n'
        f'  <text x="{margin + 24}" y="{bottom_y + 27}" font-family="{f["body"]}" font-size="13" font-weight="600" fill="{tx["primary"]}">综合对比 · {winner} 更优</text>\n'
        f'  <text x="{width - margin - 12}" y="{bottom_y + 27}" text-anchor="end" font-family="{f["body"]}" font-size="12" fill="{tx["dim"]}">共 {len(left_items) + len(right_items)} 项</text>'
    )

    svg = f'''{header}
  {decor_svg}
  {bg_vs}
  {deco_l}
  {deco_r}
  {title_area}
  {left_card}
  {right_card}
  {left_top_bar}
  {right_top_bar}
  {left_title_svg}
  {right_title_svg}
  {left_joined}
  {right_joined}
  {vs_badge}
  {bottom_card}
  {bottom_text}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_timeline(title, events, theme_name="dark", width=800, height=600):
    """时间线：自适应铺满 + 交替左右大卡片 + 装饰连接 + 统计摘要

    布局：标题 → 中轴时间线 → 自适应交替左右卡片(自动铺满高度) → 底部统计
    特点：_auto_layout让事件自动铺满、内容少时卡片放大居中
    """
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    margin = 30
    title_h = 65
    bottom_h = 55
    line_x = width // 2
    content_h = height - title_h - bottom_h - margin

    # ── 装饰层 ──
    first_year = events[0].get("year", "")[:4] if events else ""
    bg_year = f'<text x="{width - 40}" y="120" text-anchor="end" font-family="{f["display"]}" font-size="140" font-weight="900" fill="{_s(t, "divider_accent")}" opacity="0.03">{first_year}</text>'
    deco_dots_l = []
    for di in range(10):
        dy = title_h + 20 + di * 45
        if dy < height - bottom_h - 20:
            deco_dots_l.append(f'<circle cx="{margin - 5}" cy="{dy}" r="1.5" fill="{_s(t, "connector_color")}" opacity="0.1"/>')
    deco_dots_l_joined = "\n  ".join(deco_dots_l)

    # 标题区
    title_area = (
        f'<text x="{width/2}" y="40" text-anchor="middle" font-family="{f["display"]}" font-size="22" font-weight="700" fill="{tx["primary"]}">{display_title}</text>\n'
        f'  <rect x="{width*0.35}" y="50" width="{width*0.3}" height="2" rx="1" fill="{_s(t, "divider_accent")}" opacity="0.3"/>\n'
        f'  <text x="{width/2}" y="60" text-anchor="middle" font-family="{f["body"]}" font-size="11" fill="{tx["dim"]}">共 {len(events)} 个关键节点</text>'
    )

    # 时间轴主线
    axis_top = title_h + 10
    axis_bottom = height - bottom_h - 10
    timeline_axis = (
        f'<line x1="{line_x}" y1="{axis_top}" x2="{line_x}" y2="{axis_bottom}" stroke="{_s(t, "connector_color")}" stroke-width="2" opacity="0.2"/>\n'
        f'  <circle cx="{line_x}" cy="{axis_top}" r="4" fill="{_s(t, "connector_color")}" opacity="0.3"/>\n'
        f'  <circle cx="{line_x}" cy="{axis_bottom}" r="4" fill="{_s(t, "connector_color")}" opacity="0.3"/>'
    )

    # ── 自适应事件卡片 ──
    n_events = min(len(events), 5)
    card_w = (width - 2 * margin - 50) // 2
    # 用 _auto_layout 计算每个事件卡片的垂直位置和高度
    positions = _auto_layout(n_events, margin, axis_top + 5, width - 2 * margin, content_h - 15, cols=1, min_item_h=60, gap=6)

    events_svg = []
    for i, (ix, iy, iw, ih) in enumerate(positions):
        ev = events[i]
        year = ev.get("year", str(i + 1))[:10]
        ev_title = ev.get("title", "")[:16]
        ev_desc = ev.get("desc", "")[:30]
        dot_color = _item_accent(t, i)

        # 节点：外圈光晕 + 内圈实心
        events_svg.append(
            f'<circle cx="{line_x}" cy="{iy + ih // 2}" r="14" fill="{dot_color}" opacity="0.08"/>\n'
            f'  <circle cx="{line_x}" cy="{iy + ih // 2}" r="6" fill="{dot_color}" opacity="0.9"/>\n'
            f'  <circle cx="{line_x}" cy="{iy + ih // 2}" r="3" fill="{c["fill"]}" opacity="0.8"/>'
        )

        is_left = i % 2 == 0
        if is_left:
            card_x = margin
            text_x = card_x + 16
            conn_x1 = card_x + card_w
            conn_x2 = line_x - 14
        else:
            card_x = line_x + 25
            text_x = card_x + 16
            conn_x1 = line_x + 14
            conn_x2 = card_x

        # 连接线
        events_svg.append(
            f'<line x1="{conn_x1}" y1="{iy + ih // 2}" x2="{conn_x2}" y2="{iy + ih // 2}" stroke="{dot_color}" stroke-width="1.5" opacity="0.25" stroke-dasharray="4,3"/>'
        )

        # 卡片背景
        events_svg.append(
            f'<rect x="{card_x}" y="{iy}" width="{card_w}" height="{ih}" rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.4"/>\n'
            f'  <rect x="{card_x}" y="{iy}" width="3" height="{ih}" rx="1" fill="{dot_color}" opacity="0.6"/>'
        )

        # 年份标签徽章（固定在右上角）
        events_svg.append(
            f'<rect x="{card_x + card_w - 55}" y="{iy + 6}" width="48" height="18" rx="9" fill="{dot_color}" opacity="0.12"/>\n'
            f'  <text x="{card_x + card_w - 31}" y="{iy + 19}" text-anchor="middle" font-family="{f["mono"]}" font-size="11" font-weight="700" fill="{dot_color}">{year}</text>'
        )

        # 卡片内部文字自适应垂直居中
        el_defs = [
            {"type": "title", "h": 22},
            {"type": "desc", "h": 18 if ev_desc else 0},
            {"type": "spacer", "h": max(4, ih // 8)},
            {"type": "tag", "h": 16},
        ]
        layout = _card_text_layout(card_x, iy, card_w, ih, el_defs, padding=12)

        # 标题
        _, t_y, t_w, _ = layout["title_0"]
        events_svg.append(
            f'<text x="{text_x}" y="{t_y + 16}" font-family="{f["display"]}" font-size="15" font-weight="700" fill="{tx["primary"]}">{ev_title}</text>'
        )

        # 描述
        if ev_desc:
            _, d_y, d_w, _ = layout["desc_1"]
            events_svg.append(
                f'<text x="{text_x}" y="{d_y + 12}" font-family="{f["body"]}" font-size="12" fill="{tx["secondary"]}">{ev_desc}</text>'
            )

        # 底部标签
        _, tag_y, tag_w, _ = layout["tag_3"]
        tag_text = f"节点 {i+1}"
        events_svg.append(
            f'<rect x="{text_x}" y="{tag_y}" width="{len(tag_text) * 10 + 14}" height="16" rx="8" fill="{dot_color}" opacity="0.08"/>\n'
            f'  <text x="{text_x + 7}" y="{tag_y + 12}" font-family="{f["body"]}" font-size="9" fill="{tx["dim"]}">{tag_text}</text>'
        )

    events_joined = "\n  ".join(events_svg)

    # 底部统计摘要区
    bottom_y = height - bottom_h
    bottom_card = f'<rect x="{margin}" y="{bottom_y}" width="{width - 2 * margin}" height="42" rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.35"/>'
    year_range = f"{events[0].get('year','')}-{events[n_events-1].get('year','')}" if n_events > 1 else events[0].get("year", "")
    stat_items_svg = []
    stat_labels = [f"跨度 {year_range}", f"共 {n_events} 节点", "持续演进"]
    stat_w = (width - 2 * margin - 40) // 3
    for si, sl in enumerate(stat_labels):
        sx = margin + 20 + si * stat_w
        stat_items_svg.append(
            f'<rect x="{sx}" y="{bottom_y + 8}" width="4" height="26" rx="2" fill="{_item_accent(t, si)}" opacity="0.4"/>\n'
            f'  <text x="{sx + 12}" y="{bottom_y + 28}" font-family="{f["body"]}" font-size="12" fill="{tx["primary"]}">{sl}</text>'
        )
    stat_joined = "\n  ".join(stat_items_svg)

    svg = f'''{header}
  {decor_svg}
  {bg_year}
  {deco_dots_l_joined}
  {title_area}
  {timeline_axis}
  {events_joined}
  {bottom_card}
  {stat_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_steps(title, steps, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    steps_svg = []
    for i, step in enumerate(steps[:6]):
        step_title = step.get("title", "")[:16]
        step_desc = step.get("desc", "")[:35]
        y = 130 + i * 80
        num_color = _item_accent(t, i)
        badge_bg = _s(t, "badge_bg")
        step_card_x = 100
        step_card_w = width - 140
        step_card_y = y - 18
        step_card_h = 56
        steps_svg.append(
            f'<rect x="{step_card_x}" y="{step_card_y}" width="{step_card_w}" height="{step_card_h}" rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.35"/>\n'
            f'  <rect x="{step_card_x}" y="{step_card_y}" width="3" height="{step_card_h}" rx="1" fill="{num_color}" opacity="0.6"/>\n'
            f'  <circle cx="{step_card_x + 30}" cy="{y + 8}" r="14" fill="{badge_bg}"/>\n'
            f'  <text x="{step_card_x + 30}" y="{y + 13}" text-anchor="middle" font-family="{f["display"]}" font-size="14" font-weight="700" fill="{num_color}">{i+1}</text>\n'
            f'  <text x="{step_card_x + 55}" y="{y + 5}" font-family="{f["body"]}" font-size="16" font-weight="600" fill="{tx["primary"]}">{step_title}</text>\n'
            f'  <text x="{step_card_x + 55}" y="{y + 24}" font-family="{f["body"]}" font-size="12" fill="{tx["secondary"]}">{step_desc}</text>'
        )
        if i < min(len(steps), 6) - 1:
            steps_svg.append(_svg_connector_arrow(step_card_x + 30, step_card_y + step_card_h, step_card_x + 30, step_card_y + step_card_h + 20, t))

    steps_joined = "\n  ".join(steps_svg)
    svg = f'''{header}
  {decor_svg}
  <text x="{width/2}" y="55" text-anchor="middle" font-family="{f["display"]}" font-size="24" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {_svg_title_underline(width, t)}
  {steps_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_qa(question, answer, key_points=None, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_q = question[:40] + ("..." if len(question) > 40 else "")
    display_a = answer[:80] + ("..." if len(answer) > 80 else "")
    key_points = key_points or []

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    qa_card = svg_card(50, height * 0.06, width - 100, height * 0.88, theme_name, border=_s(t, "divider_accent"))
    qa_divider = svg_line(width * 0.15, height * 0.40, width * 0.85, height * 0.40, theme_name, color=_s(t, "divider_accent"), element="divider")

    # 问题多行
    q_svg, q_lines = _render_multiline_text(
        width / 2, height * 0.22, display_q,
        f["display"], 20, tx["primary"],
        max_chars_per_line=16, line_height=32,
        text_anchor="middle", font_weight="700"
    )

    # 答案多行
    a_start_y = height * 0.48
    a_svg, a_lines = _render_multiline_text(
        width / 2, a_start_y, display_a,
        f["body"], 16, tx["primary"],
        max_chars_per_line=20, line_height=28,
        text_anchor="middle"
    )

    # 关键要点列表（最多3个）
    points_svg_parts = []
    if key_points:
        pts = [pt[:20] for pt in key_points[:3]]
        pts_start_y = height * 0.72
        for i, pt in enumerate(pts):
            py = pts_start_y + i * 30
            dot_color = _item_accent(t, i)
            points_svg_parts.append(
                f'<circle cx="{width*0.25}" cy="{py-4}" r="4" fill="{dot_color}"/>\n'
                f'  <text x="{width*0.25+14}" y="{py}" font-family="{f["body"]}" font-size="13" fill="{tx["secondary"]}">{pt}</text>'
            )
    points_joined = "\n  ".join(points_svg_parts)

    svg = f'''{header}
  {decor_svg}
  {qa_card}
  <text x="{width*0.1}" y="{height*0.16}" font-family="{f["display"]}" font-size="40" fill="{_s(t, "divider_accent")}" opacity="0.25">?</text>
  {q_svg}
  {qa_divider}
  {a_svg}
  {points_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_focus(keyword, explanation, tags=None, sub_keywords=None, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_keyword = keyword[:12] + ("..." if len(keyword) > 12 else "")
    display_exp = explanation[:80] + ("..." if len(explanation) > 80 else "")
    tags = tags or []
    sub_keywords = sub_keywords or []

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    # 外圈装饰
    outer_ring = svg_circle(width / 2, height * 0.26, 80, theme_name, stroke=_s(t, "highlight_ring"))
    inner_ring = svg_circle(width / 2, height * 0.26, 60, theme_name, stroke=_s(t, "highlight_ring"))

    # 解释多行
    exp_svg, exp_lines = _render_multiline_text(
        width / 2, height * 0.48, display_exp,
        f["body"], 16, tx["primary"],
        max_chars_per_line=20, line_height=28,
        text_anchor="middle"
    )

    # 子关键词列表（最多4个，左右各2个）
    sub_kw_svg_parts = []
    if sub_keywords:
        kws = [kw[:8] for kw in sub_keywords[:4]]
        kw_y = height * 0.65
        kw_spacing = 140
        start_x = width / 2 - (min(len(kws), 2) - 1) * kw_spacing / 2
        for i, kw in enumerate(kws):
            col = i % 2
            row = i // 2
            kx = start_x + col * kw_spacing
            ky = kw_y + row * 34
            dot_color = _item_accent(t, i)
            sub_kw_svg_parts.append(
                f'<rect x="{kx-50}" y="{ky-14}" width="100" height="28" rx="14" fill="{c["fill"]}" opacity="0.35"/>\n'
                f'  <circle cx="{kx-36}" cy="{ky}" r="4" fill="{dot_color}"/>\n'
                f'  <text x="{kx-24}" y="{ky+5}" font-family="{f["body"]}" font-size="13" font-weight="600" fill="{tx["primary"]}">{kw}</text>'
            )
    sub_kw_joined = "\n  ".join(sub_kw_svg_parts)

    # 底部标签组（最多4个）
    tags_svg_parts = []
    if tags:
        tag_labels = [tg[:8] for tg in tags[:4]]
        total_tag_w = sum(len(tg) * 12 + 20 for tg in tag_labels) + 10 * (len(tag_labels) - 1)
        tx_start = (width - total_tag_w) / 2
        tags_y = height * 0.80
        for i, tg in enumerate(tag_labels):
            tw = len(tg) * 12 + 20
            tags_svg_parts.append(
                f'<rect x="{tx_start}" y="{tags_y}" width="{tw}" height="24" rx="12" fill="{_s(t, "badge_bg")}"/>\n'
                f'  <text x="{tx_start + tw/2}" y="{tags_y+17}" text-anchor="middle" font-family="{f["body"]}" font-size="11" fill="{tx["primary"]}">{tg}</text>'
            )
            tx_start += tw + 10
    tags_joined = "\n  ".join(tags_svg_parts)

    svg = f'''{header}
  {decor_svg}
  {outer_ring}
  {inner_ring}
  <text x="{width/2}" y="{height*0.28}" text-anchor="middle" font-family="{f["display"]}" font-size="38" font-weight="800" fill="{_s(t, "highlight_ring")}">{display_keyword}</text>
  {exp_svg}
  {sub_kw_joined}
  {tags_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_chart(title, data, theme_name="dark", width=800, height=600, direction="horizontal"):
    """数据图表：横向/竖向柱状图，自适应布局

    Args:
        title: 标题
        data: 数据系列 [{"label":"1月","value":85}]，最多12个
        direction: "horizontal" 横向柱图 | "vertical" 竖向柱图
    """
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    if direction == "vertical":
        # ── 竖向柱状图 ──
        margin = 50
        title_area_h = 80
        chart_pad_left = 70
        chart_pad_right = 40
        chart_pad_top = 30
        chart_pad_bottom = 60
        chart_x = margin + chart_pad_left
        chart_y = title_area_h + chart_pad_top
        chart_w = width - 2 * margin - chart_pad_left - chart_pad_right
        chart_h = height - chart_y - chart_pad_bottom - 50

        card_svg = (
            f'<rect x="{margin}" y="{title_area_h - 10}" width="{width - 2*margin}" height="{height - title_area_h - 35}" '
            f'rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.3"/>'
        )

        bar_count = min(len(data), 12)
        bars_svg = []
        if bar_count > 0:
            max_val = max((d.get("value", 0) for d in data[:12]), default=1) or 1
            bar_gap = max(6, chart_w // bar_count // 5)
            single_bar_w = (chart_w - (bar_count - 1) * bar_gap) // bar_count
            base_y = chart_y + chart_h

            for j in range(6):
                ratio = j / 5
                line_y = base_y - ratio * chart_h
                val = int(max_val * ratio)
                bars_svg.append(
                    f'<line x1="{chart_x - 8}" y1="{line_y}" x2="{chart_x + chart_w}" y2="{line_y}" '
                    f'stroke="{c["border"]}" stroke-width="0.5" opacity="0.25"/>'
                )
                bars_svg.append(
                    f'<text x="{chart_x - 14}" y="{line_y + 4}" text-anchor="end" '
                    f'font-family="{f["mono"]}" font-size="10" fill="{tx["dim"]}">{val}</text>'
                )

            for i, d in enumerate(data[:12]):
                label = d.get("label", "")[:5]
                value = d.get("value", 0)
                bar_h = (value / max_val) * chart_h
                bx = chart_x + i * (single_bar_w + bar_gap)
                by = base_y - bar_h
                bar_color = _palette(t, i)

                # 柱体渐变ID
                gid = f"bar_v_{i}"
                bars_svg.append(
                    f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
                    f'<stop offset="0%" stop-color="{bar_color}" stop-opacity="0.7"/>'
                    f'<stop offset="100%" stop-color="{bar_color}" stop-opacity="0.25"/>'
                    f'</linearGradient></defs>'
                )
                # 柱体（渐变填充）
                bars_svg.append(
                    f'<rect x="{bx}" y="{by}" width="{single_bar_w}" height="{bar_h}" '
                    f'rx="3" fill="url(#{gid})"/>'
                )
                # 顶部高亮线
                bars_svg.append(
                    f'<rect x="{bx}" y="{by}" width="{single_bar_w}" height="2" rx="1" fill="{bar_color}" opacity="0.6"/>'
                )
                # 底部微光
                bars_svg.append(
                    f'<rect x="{bx - 2}" y="{base_y - 3}" width="{single_bar_w + 4}" height="3" '
                    f'rx="1" fill="{bar_color}" opacity="0.08"/>'
                )
                # 数值标签
                bars_svg.append(
                    f'<text x="{bx + single_bar_w/2}" y="{by - 8}" text-anchor="middle" '
                    f'font-family="{f["mono"]}" font-size="11" font-weight="500" fill="{tx["secondary"]}">{value}</text>'
                )
                bars_svg.append(
                    f'<text x="{bx + single_bar_w/2}" y="{base_y + 20}" text-anchor="middle" '
                    f'font-family="{f["body"]}" font-size="12" fill="{tx["secondary"]}">{label}</text>'
                )

        bars_joined = "\n  ".join(bars_svg)
        svg = f'''{header}
  {decor_svg}
  <text x="{margin}" y="45" font-family="{f["display"]}" font-size="24" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  <rect x="{margin}" y="55" width="50" height="3" rx="1" fill="{_s(t, "divider_accent")}" opacity="0.6"/>
  {card_svg}
  {bars_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
        return svg
    else:
        # ── 横向柱状图 ──
        max_val = max((d.get("value", 0) for d in data), default=1) or 1
        bar_area_x = 160
        bar_area_w = width - 220
        bar_h = 30
        bars_svg = []
        for i, d in enumerate(data[:6]):
            label = d.get("label", "")[:14]
            value = d.get("value", 0)
            y = 130 + i * 70
            bar_w = (value / max_val) * bar_area_w
            bar_color = _palette(t, i)
            gid = f"bar_h_{i}"
            bars_svg.append(
                f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">'
                f'<stop offset="0%" stop-color="{bar_color}" stop-opacity="0.6"/>'
                f'<stop offset="100%" stop-color="{bar_color}" stop-opacity="0.2"/>'
                f'</linearGradient></defs>'
            )
            bars_svg.append(
                f'<rect x="{bar_area_x}" y="{y}" width="{bar_area_w}" height="{bar_h}" rx="4" fill="{c["fill"]}" opacity="0.2"/>\n'
                f'  <text x="{bar_area_x-10}" y="{y+bar_h/2+5}" text-anchor="end" font-family="{f["body"]}" font-size="14" fill="{tx["primary"]}">{label}</text>\n'
                f'  <rect x="{bar_area_x}" y="{y}" width="{bar_w}" height="{bar_h}" rx="4" fill="url(#{gid})"/>\n'
                f'  <rect x="{bar_area_x}" y="{y}" width="2" height="{bar_h}" rx="1" fill="{bar_color}" opacity="0.5"/>\n'
                f'  <text x="{bar_area_x+bar_w+10}" y="{y+bar_h/2+5}" font-family="{f["mono"]}" font-size="13" fill="{tx["secondary"]}">{value}</text>'
            )

        bars_joined = "\n  ".join(bars_svg)
        svg = f'''{header}
  {decor_svg}
  <text x="{width/2}" y="55" text-anchor="middle" font-family="{f["display"]}" font-size="24" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {_svg_title_underline(width, t)}
  {bars_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
        return svg


def render_svg_summary(title, items, theme_name="dark", width=800, height=600):
    """总结清单（已合并到 render_svg_card，此为兼容别名）"""
    return render_svg_card(title, items, theme_name=theme_name, width=width, height=height, cols=None, highlight=True)


def render_svg_line_chart(title, labels, datasets, theme_name="dark", width=800, height=600):
    """折线图：支持多条数据线，含渐变填充、数据点光晕、平滑曲线"""
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")
    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    # 图表区域
    chart_x, chart_y = 100, 120
    chart_w, chart_h = width - 160, height - 220

    # 找最大值
    all_values = [v for ds in datasets for v in ds.get("values", [])]
    max_val = max(all_values) if all_values else 1
    if max_val == 0:
        max_val = 1

    # 图表卡片背景
    card_svg = (
        f'<rect x="50" y="{chart_y - 30}" width="{width - 100}" height="{chart_h + 80}" '
        f'rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.3"/>'
    )

    # Y轴刻度线
    grid_svg = []
    for i in range(5):
        gy = chart_y + chart_h - (i / 4) * chart_h
        val = int(max_val * i / 4)
        grid_svg.append(
            f'<line x1="{chart_x}" y1="{gy}" x2="{chart_x + chart_w}" y2="{gy}" '
            f'stroke="{c["border"]}" stroke-width="0.5" opacity="0.15" stroke-dasharray="4,4"/>'
        )
        grid_svg.append(
            f'<text x="{chart_x - 10}" y="{gy + 4}" text-anchor="end" '
            f'font-family="{f["body"]}" font-size="11" fill="{tx["dim"]}">{val}</text>'
        )

    # X轴标签
    n = len(labels)
    x_labels_svg = []
    for i, label in enumerate(labels[:8]):
        lx = chart_x + (i / max(n - 1, 1)) * chart_w
        short_label = label[:6] + ("..." if len(label) > 6 else "")
        x_labels_svg.append(
            f'<text x="{lx}" y="{chart_y + chart_h + 25}" text-anchor="middle" '
            f'font-family="{f["body"]}" font-size="12" fill="{tx["secondary"]}">{short_label}</text>'
        )
        # X轴刻度线
        x_labels_svg.append(
            f'<line x1="{lx}" y1="{chart_y + chart_h}" x2="{lx}" y2="{chart_y + chart_h + 5}" stroke="{c["border"]}" stroke-width="0.5" opacity="0.3"/>'
        )

    # 数据线
    lines_svg = []
    dots_svg = []
    legend_svg = []
    for di, ds in enumerate(datasets[:3]):
        values = ds.get("values", [])
        ds_label = ds.get("label", "")[:8]
        color = _palette(t, di)

        # 折线路径
        points = []
        for i, v in enumerate(values[:8]):
            px = chart_x + (i / max(n - 1, 1)) * chart_w
            py = chart_y + chart_h - (v / max_val) * chart_h
            points.append((px, py))

        if len(points) >= 2:
            # 渐变填充ID
            gid = f"line_fill_{di}"
            lines_svg.append(
                f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0%" stop-color="{color}" stop-opacity="0.12"/>'
                f'<stop offset="100%" stop-color="{color}" stop-opacity="0.01"/>'
                f'</linearGradient></defs>'
            )
            # 填充区域
            fill_path = f"M{points[0][0]},{chart_y + chart_h} L" + " L".join(f"{p[0]},{p[1]}" for p in points) + f" L{points[-1][0]},{chart_y + chart_h} Z"
            lines_svg.append(
                f'<path d="{fill_path}" fill="url(#{gid})"/>'
            )
            # 折线
            path_d = "M" + " L".join(f"{p[0]},{p[1]}" for p in points)
            lines_svg.append(
                f'<path d="{path_d}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.8"/>'
            )

        # 数据点
        for px, py in points:
            # 光晕
            dots_svg.append(
                f'<circle cx="{px}" cy="{py}" r="7" fill="{color}" opacity="0.06"/>'
            )
            # 外圈
            dots_svg.append(
                f'<circle cx="{px}" cy="{py}" r="4" fill="{c["fill"]}" stroke="{color}" stroke-width="1.5" opacity="0.8"/>'
            )
            # 内点
            dots_svg.append(
                f'<circle cx="{px}" cy="{py}" r="2" fill="{color}" opacity="0.7"/>'
            )

        # 图例
        legend_x = chart_x + di * 120
        legend_y = chart_y - 35
        legend_svg.append(
            f'<circle cx="{legend_x + 6}" cy="{legend_y + 6}" r="5" fill="{color}" opacity="0.5"/>\n'
            f'  <text x="{legend_x + 16}" y="{legend_y + 10}" font-family="{f["body"]}" font-size="12" fill="{tx["primary"]}">{ds_label}</text>'
        )

    grid_joined = "\n  ".join(grid_svg)
    labels_joined = "\n  ".join(x_labels_svg)
    lines_joined = "\n  ".join(lines_svg)
    dots_joined = "\n  ".join(dots_svg)
    legend_joined = "\n  ".join(legend_svg)

    svg = f'''{header}
  {decor_svg}
  <text x="{width/2}" y="45" text-anchor="middle" font-family="{f["display"]}" font-size="22" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {card_svg}
  {legend_joined}
  {grid_joined}
  {lines_joined}
  {dots_joined}
  {labels_joined}
  <rect x="{chart_x}" y="{chart_y + chart_h}" width="{chart_w}" height="1" fill="{c["border"]}" opacity="0.3"/>
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_feature(title, features, theme_name="dark", width=800, height=600):
    """组合布局：核心概念详解，左侧关键词+右侧说明，适合多维度解析"""
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")
    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    features_svg = []
    for i, feat in enumerate(features[:4]):
        keyword = feat.get("keyword", "")[:10] + ("..." if len(feat.get("keyword", "")) > 10 else "")
        desc = feat.get("desc", "")[:40] + ("..." if len(feat.get("desc", "")) > 40 else "")
        y = 140 + i * 110
        kw_color = _item_accent(t, i)
        # 左侧关键词卡片（带色条+图标圆点）
        kw_card_x, kw_card_y = 40, y - 20
        kw_card_w, kw_card_h = 180, 80
        features_svg.append(
            f'<rect x="{kw_card_x}" y="{kw_card_y}" width="{kw_card_w}" height="{kw_card_h}" '
            f'rx="{c["radius"]}" fill="{c["fill"]}" stroke="{c["border"]}" stroke-width="1"/>'
        )
        features_svg.append(
            f'<rect x="{kw_card_x}" y="{kw_card_y}" width="4" height="{kw_card_h}" rx="2" fill="{kw_color}" opacity="0.7"/>'
        )
        features_svg.append(
            f'<circle cx="{kw_card_x + 25}" cy="{kw_card_y + 25}" r="10" fill="{kw_color}" opacity="0.12"/>'
        )
        features_svg.append(
            f'<text x="{kw_card_x + 25}" y="{kw_card_y + 30}" text-anchor="middle" font-family="{f["display"]}" font-size="11" font-weight="700" fill="{kw_color}">{i+1}</text>'
        )
        features_svg.append(
            f'<text x="{kw_card_x + kw_card_w/2 + 8}" y="{kw_card_y + kw_card_h/2 + 6}" '
            f'text-anchor="middle" font-family="{f["display"]}" font-size="18" font-weight="700" fill="{kw_color}">{keyword}</text>'
        )
        # 右侧说明（带小卡片背景）
        desc_x = kw_card_x + kw_card_w + 25
        desc_w = width - desc_x - 40
        features_svg.append(
            f'<rect x="{desc_x - 8}" y="{kw_card_y}" width="{desc_w + 8}" height="{kw_card_h}" rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.25"/>'
        )
        features_svg.append(
            f'<text x="{desc_x + 8}" y="{kw_card_y + 35}" '
            f'font-family="{f["body"]}" font-size="15" fill="{tx["primary"]}">{desc}</text>'
        )
        # 连接线（带箭头）
        features_svg.append(_svg_connector_arrow(kw_card_x + kw_card_w, kw_card_y + kw_card_h//2, kw_card_x + kw_card_w + 22, kw_card_y + kw_card_h//2, t, horizontal=True))

    features_joined = "\n  ".join(features_svg)
    svg = f'''{header}
  {decor_svg}
  <text x="{width/2}" y="55" text-anchor="middle" font-family="{f["display"]}" font-size="24" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {_svg_title_underline(width, t)}
  {features_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_grid(title, cards, theme_name="dark", width=800, height=600, mode="card"):
    """组合布局 / 指标网格：自适应网格居中铺满 + 装饰层

    布局：标题 → 自适应网格(内容少时卡片放大居中，多时均匀铺满) → 底部
    特点：_auto_layout自动居中、背景装饰
    参数：
        mode: "card" 文字卡片网格(序号/标题/描述/进度条) | "metric" 指标网格(大数值/标签/迷你图/进度条)
    """
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")
    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    n_cards = min(len(cards), 6)
    cols = 2 if n_cards > 2 else 1
    if n_cards >= 5:
        cols = 3

    # ── 装饰层 ──
    bg_text = f'<text x="{width - 30}" y="100" text-anchor="end" font-family="{f["display"]}" font-size="100" font-weight="900" fill="{_s(t, "divider_accent")}" opacity="0.03">GRID</text>'

    # 标题区
    title_area = (
        f'<text x="{width/2}" y="50" text-anchor="middle" font-family="{f["display"]}" font-size="22" font-weight="700" fill="{tx["primary"]}">{display_title}</text>\n'
        f'  <rect x="{width*0.35}" y="60" width="{width*0.3}" height="2" rx="1" fill="{_s(t, "divider_accent")}" opacity="0.3"/>\n'
        f'  <text x="{width/2}" y="72" text-anchor="middle" font-family="{f["body"]}" font-size="11" fill="{tx["dim"]}">共 {n_cards} 项</text>'
    )

    # 自适应布局
    positions = _auto_layout(n_cards, 35, 85, width - 70, height - 135, cols=cols, min_item_h=80, gap=14)

    if mode == "metric":
        # ── 指标网格模式 ──
        cards_svg = []
        for i, (cx, cy, cw, ch) in enumerate(positions):
            card = cards[i]
            value = str(card.get("value", card.get("title", "")))[:10]
            label = card.get("label", card.get("title", ""))[:14]
            sub = card.get("sub", "")[:20]
            accent_color = _item_accent(t, i)

            # 卡片内部文字自适应垂直居中
            el_defs = [
                {"type": "value", "h": 36},
                {"type": "label", "h": 18},
                {"type": "sub", "h": 14 if sub else 0},
                {"type": "spacer", "h": max(6, ch // 6)},
                {"type": "progress", "h": 10},
            ]
            layout = _card_text_layout(cx, cy, cw, ch, el_defs, padding=14)

            # 卡片背景
            cards_svg.append(
                f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" '
                f'rx="{c["radius"]}" fill="{c["fill"]}" stroke="{c["border"]}" stroke-width="1"/>'
            )
            cards_svg.append(
                f'<rect x="{cx}" y="{cy}" width="{cw}" height="3" rx="1" fill="{accent_color}" opacity="0.5"/>'
            )

            # 大数值
            _, v_y, v_w, _ = layout["value_0"]
            cards_svg.append(
                f'<text x="{cx + cw//2}" y="{v_y + 28}" text-anchor="middle" font-family="{f["display"]}" font-size="28" font-weight="800" fill="{accent_color}">{value}</text>'
            )

            # 标签
            _, l_y, l_w, _ = layout["label_1"]
            cards_svg.append(
                f'<text x="{cx + cw//2}" y="{l_y + 12}" text-anchor="middle" font-family="{f["body"]}" font-size="13" fill="{tx["primary"]}">{label}</text>'
            )

            # 副标签
            if sub:
                _, s_y, s_w, _ = layout["sub_2"]
                cards_svg.append(
                    f'<text x="{cx + cw//2}" y="{s_y + 10}" text-anchor="middle" font-family="{f["body"]}" font-size="11" fill="{tx["secondary"]}">{sub}</text>'
                )

            # 迷你折线
            _, p_y, p_w, _ = layout["progress_4"]
            line_y = p_y
            pts = []
            for j in range(5):
                px = cx + 14 + j * (p_w - 28) // 4
                py = line_y + (10 if j % 2 == 0 else 0) + (i * 3 + j * 2) % 8
                pts.append(f"{px},{py}")
            cards_svg.append(
                f'<polyline points="{" ".join(pts)}" fill="none" stroke="{accent_color}" stroke-width="1.5" opacity="0.4"/>'
            )

        cards_joined = "\n  ".join(cards_svg)
    else:
        # ── 文字卡片模式 ──
        cards_svg = []
        for i, (cx, cy, cw, ch) in enumerate(positions):
            card = cards[i]
            card_title = card.get("title", "")[:12] + ("..." if len(card.get("title", "")) > 12 else "")
            card_desc = card.get("desc", "")[:30] + ("..." if len(card.get("desc", "")) > 30 else "")
            accent_color = _item_accent(t, i)

            # 卡片内部文字自适应垂直居中
            pad = 14
            el_defs = [
                {"type": "badge_title", "h": 28},
                {"type": "divider", "h": 12},
                {"type": "desc", "h": 20},
                {"type": "spacer", "h": max(10, ch // 6)},
                {"type": "progress", "h": 10},
            ]
            layout = _card_text_layout(cx, cy, cw, ch, el_defs, padding=pad)

            cards_svg.append(
                f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" '
                f'rx="{c["radius"]}" fill="{c["fill"]}" stroke="{c["border"]}" stroke-width="1"/>'
            )
            cards_svg.append(
                f'<rect x="{cx}" y="{cy}" width="{cw}" height="3" rx="1" fill="{accent_color}" opacity="0.5"/>'
            )
            cards_svg.append(
                f'<rect x="{cx}" y="{cy + 6}" width="4" height="{ch - 12}" rx="2" fill="{accent_color}" opacity="0.6"/>'
            )

            _, bt_y, bt_w, _ = layout["badge_title_0"]
            badge_x = cx + pad
            cards_svg.append(
                f'<rect x="{badge_x}" y="{bt_y}" width="30" height="22" rx="11" fill="{accent_color}" opacity="0.1"/>\n'
                f'  <text x="{badge_x + 15}" y="{bt_y + 16}" text-anchor="middle" font-family="{f["mono"]}" font-size="13" font-weight="700" fill="{accent_color}">{i+1:02d}</text>'
            )
            cards_svg.append(
                f'<text x="{badge_x + 38}" y="{bt_y + 16}" font-family="{f["body"]}" font-size="16" font-weight="600" '
                f'fill="{tx["primary"]}">{card_title}</text>'
            )

            _, div_y, div_w, _ = layout["divider_1"]
            cards_svg.append(
                f'<line x1="{cx + pad}" y1="{div_y + 6}" x2="{cx + cw - pad}" y2="{div_y + 6}" stroke="{c["border"]}" stroke-width="0.5" opacity="0.4"/>'
            )

            _, desc_y, desc_w, _ = layout["desc_2"]
            cards_svg.append(
                f'<text x="{cx + pad + 4}" y="{desc_y + 14}" font-family="{f["body"]}" font-size="13" '
                f'fill="{tx["secondary"]}">{card_desc}</text>'
            )

            _, prog_y, prog_w, _ = layout["progress_4"]
            bar_pct = 30 + (i * 19) % 65
            cards_svg.append(
                f'<rect x="{cx + pad + 4}" y="{prog_y}" width="{prog_w - 8}" height="4" rx="2" fill="{c["fill"]}" opacity="0.5"/>\n'
                f'  <rect x="{cx + pad + 4}" y="{prog_y}" width="{int((prog_w - 8) * bar_pct / 100)}" height="4" rx="2" fill="{accent_color}" opacity="0.35"/>'
            )

        cards_joined = "\n  ".join(cards_svg)

    svg = f'''{header}
  {decor_svg}
  {bg_text}
  {title_area}
  {cards_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


# ── 新增渲染函数 ──────────────────────────────────────────


def render_svg_hero(title, subtitle="", tags=None, theme_name="dark",
                    width=1240, height=770):
    """英雄区卡片：大标题+渐变装饰+标签，适合文章开头/封面

    Args:
        title: 主标题，最多20字
        subtitle: 副标题，最多40字
        tags: 标签列表，最多5个，每个8字
    """
    from scripts.elements.shape_primitives import svg_gradient_rect, svg_gradient_text, svg_gradient_line

    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]
    tags = tags or []

    display_title = title[:20] + ("..." if len(title) > 20 else "")
    display_sub = subtitle[:40] + ("..." if len(subtitle) > 40 else "")

    card_x, card_y = 50, 50
    card_w, card_h = width - 100, height - 100

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    # 渐变色条（左侧竖条）
    defs_g1, bar1 = svg_gradient_rect(
        card_x, card_y + 20, 6, card_h - 40, theme_name,
        direction="vertical", color_keys=("accent", "gold"),
        opacity=0.6, radius=3, id_suffix="hero-left-bar"
    )
    # 渐变标题
    use_gradient = t["decor"].get("gradient_accents", False)
    if use_gradient:
        defs_g2, title_svg = svg_gradient_text(
            display_title, card_x + 40, card_y + 80, theme_name,
            font_size=42, font_weight="800", id_suffix="hero-title"
        )
    else:
        defs_g2 = ""
        title_svg = (
            f'<text x="{card_x + 40}" y="{card_y + 80}" '
            f'font-family="{f["display"]}" font-size="42" font-weight="800" '
            f'fill="{tx["primary"]}">{display_title}</text>'
        )

    # 副标题
    sub_svg = ""
    if display_sub:
        sub_svg = (
            f'<text x="{card_x + 40}" y="{card_y + 120}" '
            f'font-family="{f["body"]}" font-size="18" '
            f'fill="{tx["secondary"]}">{display_sub}</text>'
        )

    # 标签胶囊
    tags_svg = []
    tag_x = card_x + 40
    for i, tag in enumerate(tags[:5]):
        tag_text = tag[:8]
        tw = len(tag_text) * 14 + 24
        tag_color = _item_accent(t, i)
        tags_svg.append(
            f'<rect x="{tag_x}" y="{card_y + 145}" width="{tw}" height="28" rx="14" '
            f'fill="{tag_color}" opacity="0.15"/>\n'
            f'  <text x="{tag_x + tw/2}" y="{card_y + 164}" text-anchor="middle" '
            f'font-family="{f["body"]}" font-size="13" font-weight="600" '
            f'fill="{tag_color}">{tag_text}</text>'
        )
        tag_x += tw + 10

    tags_joined = "\n  ".join(tags_svg)

    # 渐变底部装饰线
    defs_g3, bottom_line = svg_gradient_line(
        card_x + 40, card_y + card_h - 30,
        card_x + card_w - 40, card_y + card_h - 30,
        theme_name, stroke_width=2,
        color_keys=("accent", "gold"), opacity=0.3,
        id_suffix="hero-bottom-line"
    )

    # 右侧装饰区域：渐变光晕
    defs_g4, glow_rect = svg_gradient_rect(
        width * 0.6, card_y + 30, width * 0.35, card_h - 60, theme_name,
        direction="diagonal", color_keys=("accent", "cyan"),
        opacity=0.05, radius=24, id_suffix="hero-right-glow"
    )

    card_shape = svg_card(card_x, card_y, card_w, card_h, theme_name)
    all_defs = f"{defs_g1}\n{defs_g2}\n{defs_g3}\n{defs_g4}"

    svg = f'''{header}
  <defs>
    {all_defs}
  </defs>
  {decor_svg}
  {card_shape}
  {bar1}
  {glow_rect}
  {title_svg}
  {sub_svg}
  {tags_joined}
  {bottom_line}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_duo_card(title, left_title, right_title, left_items, right_items,
                        theme_name="dark", width=1240, height=770):
    """双栏信息卡（已合并到 render_svg_compare，此为兼容别名）"""
    return render_svg_compare(title, left_title, right_title, left_items, right_items,
                              theme_name=theme_name, width=width, height=height)


def render_svg_list_detail(title, items, theme_name="dark",
                           width=1240, height=770):
    """列表详情卡：每项带关键词+描述，信息密度更高

    Args:
        title: 标题
        items: 列表项，每项 {"keyword": "关键词", "desc": "描述"}，最多6项
    """
    from scripts.elements.shape_primitives import svg_gradient_rect, svg_gradient_line

    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")

    card_x, card_y = 50, 50
    card_w, card_h = width - 100, height - 100

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)
    card_shape = svg_card(card_x, card_y, card_w, card_h, theme_name)

    # 顶部渐变色条
    use_gradient = t["decor"].get("gradient_accents", False)
    if use_gradient:
        defs_g1, top_bar = svg_gradient_rect(
            card_x, card_y, card_w, 5, theme_name,
            direction="horizontal", color_keys=("accent", "gold"),
            opacity=0.5, radius=0, id_suffix="list-top-bar"
        )
    else:
        defs_g1 = ""
        top_bar = f'<rect x="{card_x}" y="{card_y}" width="{card_w}" height="3" rx="1" fill="{p["accent"]}" opacity="0.3"/>'

    # 列表项
    items_svg = []
    start_y = card_y + 90
    row_h = (card_h - 130) / max(len(items), 1)
    for i, item in enumerate(items[:6]):
        kw = item.get("keyword", "")[:10]
        desc = item.get("desc", "")[:40] + ("..." if len(item.get("desc", "")) > 40 else "")
        y = start_y + i * row_h
        num_color = _item_accent(t, i)

        # 序号 + 关键词（大字）+ 描述（小字）
        items_svg.append(
            f'<text x="{card_x + 30}" y="{y}" '
            f'font-family="{f["display"]}" font-size="22" font-weight="800" '
            f'fill="{num_color}" opacity="0.25">{i+1:02d}</text>\n'
            f'  <text x="{card_x + 70}" y="{y}" '
            f'font-family="{f["display"]}" font-size="18" font-weight="700" '
            f'fill="{tx["primary"]}">{kw}</text>\n'
            f'  <text x="{card_x + 70}" y="{y + 22}" '
            f'font-family="{f["body"]}" font-size="13" '
            f'fill="{tx["secondary"]}">{desc}</text>'
        )
        # 分隔线（非最后一项）
        if i < len(items[:6]) - 1:
            items_svg.append(
                f'<line x1="{card_x + 30}" y1="{y + row_h/2}" '
                f'x2="{card_x + card_w - 30}" y2="{y + row_h/2}" '
                f'stroke="{c["border"]}" stroke-width="0.5" opacity="0.3"/>'
            )

    items_joined = "\n  ".join(items_svg)

    svg = f'''{header}
  <defs>
    {defs_g1}
  </defs>
  {decor_svg}
  {card_shape}
  {top_bar}
  <text x="{width/2}" y="{card_y + 50}" text-anchor="middle" font-family="{f["display"]}" font-size="24" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {_svg_title_underline(width, t)}
  {items_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_dashboard(title, metrics=None, bar_data=None, list_items=None,
                         theme_name="dark", width=1240, height=770):
    """仪表盘：多指标卡片 + 竖向柱状图 + 列表，信息密度极高

    布局：顶部标题 → 指标卡片行(3-4个) → 左侧柱状图 + 右侧列表
    参考风格：数据可视化仪表盘，卡片铺满屏幕

    Args:
        title: 标题，最多20字
        metrics: 指标列表 [{"value":"1.2k","label":"用户数","trend":"+12%"}]，最多4个
        bar_data: 柱状图数据 [{"label":"1月","value":85}]，最多8个
        list_items: 右侧列表 [{"keyword":"增长","desc":"月活增长12%"}]，最多5个
    """
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]
    metrics = metrics or []
    bar_data = bar_data or []
    list_items = list_items or []

    display_title = title[:20] + ("..." if len(title) > 20 else "")
    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    # ── 布局参数 ──
    margin = 40
    top_y = 55  # 标题区
    metric_y = 90  # 指标卡片起始y
    metric_h = 72  # 指标卡片高度
    content_y = metric_y + metric_h + 18  # 下方内容区起始
    content_h = height - content_y - 55  # 下方内容区高度

    # ── 指标卡片行 ──
    metric_count = min(len(metrics), 4)
    metric_gap = 16
    metric_w = (width - 2 * margin - (metric_count - 1) * metric_gap) // max(metric_count, 1)
    metrics_svg = []
    for i, m in enumerate(metrics[:4]):
        mx = margin + i * (metric_w + metric_gap)
        val = m.get("value", "")[:10]
        label = m.get("label", "")[:8]
        trend = m.get("trend", "")[:6]
        accent = _item_accent(t, i)
        # 卡片背景
        metrics_svg.append(
            f'<rect x="{mx}" y="{metric_y}" width="{metric_w}" height="{metric_h}" '
            f'rx="{c["radius"]}" fill="{c["fill"]}" stroke="{c["border"]}" stroke-width="1"/>'
        )
        # 顶部色条
        metrics_svg.append(
            f'<rect x="{mx}" y="{metric_y}" width="{metric_w}" height="3" rx="1" fill="{accent}" opacity="0.7"/>'
        )
        # 数值（大字）
        metrics_svg.append(
            f'<text x="{mx + 18}" y="{metric_y + 32}" font-family="{f["mono"]}" font-size="24" font-weight="800" '
            f'fill="{tx["primary"]}">{val}</text>'
        )
        # 标签
        metrics_svg.append(
            f'<text x="{mx + 18}" y="{metric_y + 52}" font-family="{f["body"]}" font-size="12" '
            f'fill="{tx["secondary"]}">{label}</text>'
        )
        # 趋势标签
        if trend:
            is_up = trend.startswith("+") or trend.startswith("↑")
            trend_color = p.get("success", accent) if is_up else p.get("warn", accent)
            tw = len(trend) * 9 + 16
            metrics_svg.append(
                f'<rect x="{mx + metric_w - tw - 12}" y="{metric_y + 42}" width="{tw}" height="20" rx="10" '
                f'fill="{trend_color}" opacity="0.12"/>'
            )
            metrics_svg.append(
                f'<text x="{mx + metric_w - tw/2 - 12}" y="{metric_y + 56}" text-anchor="middle" '
                f'font-family="{f["mono"]}" font-size="11" font-weight="600" fill="{trend_color}">{trend}</text>'
            )

    metrics_joined = "\n  ".join(metrics_svg)

    # ── 左侧竖向柱状图 ──
    bar_area_w = int((width - 2 * margin - 20) * 0.55)
    bar_area_h = content_h - 10
    bar_card_x = margin
    bar_card_y = content_y

    # 柱状图卡片背景
    bar_card_svg = (
        f'<rect x="{bar_card_x}" y="{bar_card_y}" width="{bar_area_w}" height="{bar_area_h}" '
        f'rx="{c["radius"]}" fill="{c["fill"]}" stroke="{c["border"]}" stroke-width="1"/>'
    )
    # 柱状图标题
    bar_title_svg = (
        f'<text x="{bar_card_x + 20}" y="{bar_card_y + 28}" font-family="{f["body"]}" '
        f'font-size="14" font-weight="600" fill="{tx["secondary"]}">数据趋势</text>'
    )

    # 竖向柱状图
    bars_svg = []
    bar_count = min(len(bar_data), 8)
    if bar_count > 0:
        max_val = max((d.get("value", 0) for d in bar_data[:8]), default=1) or 1
        bar_pad_x = 50
        bar_pad_bottom = 35
        bar_pad_top = 50
        bar_total_w = bar_area_w - 2 * bar_pad_x
        bar_gap = 8
        single_bar_w = (bar_total_w - (bar_count - 1) * bar_gap) // bar_count
        chart_base_y = bar_card_y + bar_area_h - bar_pad_bottom
        chart_max_h = bar_area_h - bar_pad_top - bar_pad_bottom

        # 水平参考线
        for j in range(5):
            line_y = chart_base_y - j * chart_max_h / 4
            bars_svg.append(
                f'<line x1="{bar_card_x + bar_pad_x - 10}" y1="{line_y}" '
                f'x2="{bar_card_x + bar_area_w - bar_pad_x + 10}" y2="{line_y}" '
                f'stroke="{c["border"]}" stroke-width="0.5" opacity="0.3"/>'
            )

        for i, d in enumerate(bar_data[:8]):
            label = d.get("label", "")[:4]
            value = d.get("value", 0)
            bar_h = (value / max_val) * chart_max_h
            bx = bar_card_x + bar_pad_x + i * (single_bar_w + bar_gap)
            by = chart_base_y - bar_h
            bar_color = _item_accent(t, i)
            # 柱体
            bars_svg.append(
                f'<rect x="{bx}" y="{by}" width="{single_bar_w}" height="{bar_h}" '
                f'rx="3" fill="{bar_color}" opacity="0.75"/>'
            )
            # 数值
            bars_svg.append(
                f'<text x="{bx + single_bar_w/2}" y="{by - 6}" text-anchor="middle" '
                f'font-family="{f["mono"]}" font-size="10" fill="{tx["secondary"]}">{value}</text>'
            )
            # 标签
            bars_svg.append(
                f'<text x="{bx + single_bar_w/2}" y="{chart_base_y + 16}" text-anchor="middle" '
                f'font-family="{f["body"]}" font-size="11" fill="{tx["dim"]}">{label}</text>'
            )

    bars_joined = "\n  ".join(bars_svg)

    # ── 右侧列表区 ──
    list_x = margin + bar_area_w + 20
    list_w = width - list_x - margin
    list_card_svg = (
        f'<rect x="{list_x}" y="{content_y}" width="{list_w}" height="{bar_area_h}" '
        f'rx="{c["radius"]}" fill="{c["fill"]}" stroke="{c["border"]}" stroke-width="1"/>'
    )
    list_title_svg = (
        f'<text x="{list_x + 20}" y="{content_y + 28}" font-family="{f["body"]}" '
        f'font-size="14" font-weight="600" fill="{tx["secondary"]}">关键指标</text>'
    )

    list_svg = []
    item_start_y = content_y + 48
    item_h = min(50, (bar_area_h - 60) // max(len(list_items), 1))
    for i, item in enumerate(list_items[:5]):
        kw = item.get("keyword", "")[:8]
        desc = item.get("desc", "")[:20]
        val_text = item.get("value", "")[:8]
        iy = item_start_y + i * item_h
        accent = _item_accent(t, i)
        # 小色点
        list_svg.append(
            f'<circle cx="{list_x + 22}" cy="{iy + 12}" r="5" fill="{accent}" opacity="0.7"/>'
        )
        # 关键词
        list_svg.append(
            f'<text x="{list_x + 36}" y="{iy + 16}" font-family="{f["body"]}" font-size="14" font-weight="600" '
            f'fill="{tx["primary"]}">{kw}</text>'
        )
        # 数值
        if val_text:
            list_svg.append(
                f'<text x="{list_x + list_w - 18}" y="{iy + 16}" text-anchor="end" '
                f'font-family="{f["mono"]}" font-size="14" font-weight="700" fill="{accent}">{val_text}</text>'
            )
        # 描述
        list_svg.append(
            f'<text x="{list_x + 36}" y="{iy + 32}" font-family="{f["body"]}" font-size="11" '
            f'fill="{tx["secondary"]}">{desc}</text>'
        )
        # 分隔线
        if i < len(list_items[:5]) - 1:
            list_svg.append(
                f'<line x1="{list_x + 16}" y1="{iy + item_h - 2}" '
                f'x2="{list_x + list_w - 16}" y2="{iy + item_h - 2}" '
                f'stroke="{c["border"]}" stroke-width="0.5" opacity="0.3"/>'
            )

    list_joined = "\n  ".join(list_svg)

    svg = f'''{header}
  {decor_svg}
  <text x="{margin}" y="{top_y}" font-family="{f["display"]}" font-size="22" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  <rect x="{margin}" y="{top_y + 10}" width="50" height="3" rx="1" fill="{_s(t, "divider_accent")}" opacity="0.6"/>
  {metrics_joined}
  {bar_card_svg}
  {bar_title_svg}
  {bars_joined}
  {list_card_svg}
  {list_title_svg}
  {list_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_bar_chart(title, data=None, labels=None, show_values=True,
                         theme_name="dark", width=1240, height=770):
    """竖向柱状图（已合并到 render_svg_chart，此为兼容别名）"""
    return render_svg_chart(title, data or [], theme_name=theme_name, width=width, height=height, direction="vertical")


def render_svg_metric_grid(title, metrics=None, cols=3, theme_name="dark",
                           width=1240, height=770):
    """指标网格（已合并到 render_svg_grid，此为兼容别名）"""
    return render_svg_grid(title, metrics or [], theme_name=theme_name, width=width, height=height, mode="metric")


# ── 新增图表模板 ──────────────────────────────────────────


def render_svg_logic_flow(title, steps, theme_name="dark", width=800, height=600):
    """逻辑推导图：从前提→推导→结论的流程链，含箭头连接和条件标注

    Args:
        title: 标题
        steps: 推导步骤 [{"label":"前提","desc":"描述","type":"premise|inference|conclusion"}]，最多6步
    """
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")
    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    n = min(len(steps), 6)
    margin = 40
    title_h = 70

    # ── 装饰层 ──
    bg_text = f'<text x="{width - 30}" y="100" text-anchor="end" font-family="{f["display"]}" font-size="100" font-weight="900" fill="{_s(t, "divider_accent")}" opacity="0.03">LOGIC</text>'

    # 标题区
    title_area = (
        f'<text x="{margin}" y="42" font-family="{f["display"]}" font-size="22" font-weight="700" fill="{tx["primary"]}">{display_title}</text>\n'
        f'  <rect x="{margin}" y="52" width="60" height="3" rx="1" fill="{_s(t, "divider_accent")}" opacity="0.6"/>\n'
        f'  <text x="{margin + 70}" y="55" font-family="{f["body"]}" font-size="12" fill="{tx["dim"]}">{n} 步推导</text>'
    )

    # ── 自适应布局 ──
    content_h = height - title_h - 60
    positions = _auto_layout(n, margin, title_h, width - 2 * margin, content_h, cols=1, min_item_h=60, gap=10)

    steps_svg = []
    for i, (ix, iy, iw, ih) in enumerate(positions):
        step = steps[i]
        label = step.get("label", f"步骤{i+1}")[:14]
        desc = step.get("desc", "")[:30]
        stype = step.get("type", "inference")
        accent = _item_accent(t, i)

        # 类型颜色
        if stype == "premise":
            type_color = p.get("accent", accent)
            type_label = "前提"
        elif stype == "conclusion":
            type_color = p.get("gold", accent)
            type_label = "结论"
        else:
            type_color = accent
            type_label = "推导"

        # 卡片内部文字自适应垂直居中
        el_defs = [
            {"type": "header", "h": 22},
            {"type": "desc", "h": 16 if desc else 0},
            {"type": "spacer", "h": max(4, ih // 8)},
        ]
        layout = _card_text_layout(ix, iy, iw, ih, el_defs, padding=12)

        # 步骤卡片
        steps_svg.append(
            f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.4"/>'
        )
        # 左侧色条
        steps_svg.append(
            f'<rect x="{ix}" y="{iy}" width="4" height="{ih}" rx="2" fill="{type_color}" opacity="0.7"/>'
        )

        # 序号+类型徽章
        _, h_y, h_w, _ = layout["header_0"]
        steps_svg.append(
            f'<rect x="{ix + 14}" y="{h_y}" width="24" height="20" rx="10" fill="{type_color}" opacity="0.12"/>\n'
            f'  <text x="{ix + 26}" y="{h_y + 14}" text-anchor="middle" font-family="{f["mono"]}" font-size="11" font-weight="700" fill="{type_color}">{i+1}</text>'
        )
        # 标签
        steps_svg.append(
            f'<text x="{ix + 46}" y="{h_y + 15}" font-family="{f["body"]}" font-size="14" font-weight="600" fill="{tx["primary"]}">{label}</text>'
        )
        # 类型标签
        steps_svg.append(
            f'<rect x="{ix + iw - 50}" y="{h_y + 2}" width="38" height="16" rx="8" fill="{type_color}" opacity="0.1"/>\n'
            f'  <text x="{ix + iw - 31}" y="{h_y + 14}" text-anchor="middle" font-family="{f["body"]}" font-size="9" fill="{type_color}">{type_label}</text>'
        )

        # 描述
        if desc:
            _, d_y, d_w, _ = layout["desc_1"]
            steps_svg.append(
                f'<text x="{ix + 46}" y="{d_y + 12}" font-family="{f["body"]}" font-size="12" fill="{tx["secondary"]}">{desc}</text>'
            )

        # 箭头连接线（除最后一个）
        if i < n - 1:
            next_iy = positions[i + 1][1]
            arrow_x = ix + iw // 2
            arrow_top = iy + ih
            arrow_bottom = next_iy
            mid_y = (arrow_top + arrow_bottom) // 2
            steps_svg.append(
                f'<line x1="{arrow_x}" y1="{arrow_top}" x2="{arrow_x}" y2="{arrow_bottom - 6}" stroke="{type_color}" stroke-width="1.5" opacity="0.3" stroke-dasharray="4,3"/>\n'
                f'  <polygon points="{arrow_x - 5},{arrow_bottom - 8} {arrow_x + 5},{arrow_bottom - 8} {arrow_x},{arrow_bottom}" fill="{type_color}" opacity="0.4"/>'
            )
            # 条件标注
            cond_text = f"∴" if stype == "premise" else f"→"
            steps_svg.append(
                f'<circle cx="{arrow_x}" cy="{mid_y}" r="10" fill="{c["fill"]}" stroke="{type_color}" stroke-width="1" opacity="0.6"/>\n'
                f'  <text x="{arrow_x}" y="{mid_y + 4}" text-anchor="middle" font-family="{f["display"]}" font-size="10" fill="{type_color}">{cond_text}</text>'
            )

    steps_joined = "\n  ".join(steps_svg)

    svg = f'''{header}
  {decor_svg}
  {bg_text}
  {title_area}
  {steps_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_cycle(title, phases, theme_name="dark", width=800, height=600):
    """循环图：环形排列的循环阶段，含弧形箭头连接

    Args:
        title: 标题
        phases: 循环阶段 [{"label":"阶段名","desc":"描述"}]，3-6个
    """
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")
    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    n = min(max(len(phases), 3), 6)

    # ── 装饰层 ──
    bg_text = f'<text x="{width - 30}" y="100" text-anchor="end" font-family="{f["display"]}" font-size="100" font-weight="900" fill="{_s(t, "divider_accent")}" opacity="0.03">CYCLE</text>'

    # 标题区
    title_area = (
        f'<text x="{width/2}" y="42" text-anchor="middle" font-family="{f["display"]}" font-size="22" font-weight="700" fill="{tx["primary"]}">{display_title}</text>\n'
        f'  <rect x="{width*0.35}" y="52" width="{width*0.3}" height="2" rx="1" fill="{_s(t, "divider_accent")}" opacity="0.3"/>'
    )

    # ── 环形布局 ──
    cx_center = width / 2
    cy_center = height / 2 + 20
    radius_x = min(width - 200, 300) / 2
    radius_y = min(height - 200, 280) / 2

    import math
    phase_svg = []
    for i in range(n):
        angle = -math.pi / 2 + 2 * math.pi * i / n
        px = cx_center + radius_x * math.cos(angle)
        py = cy_center + radius_y * math.sin(angle)
        phase = phases[i]
        label = phase.get("label", f"阶段{i+1}")[:10]
        desc = phase.get("desc", "")[:16]
        accent = _item_accent(t, i)

        # 节点卡片
        node_w = 110
        node_h = 56
        nx = px - node_w / 2
        ny = py - node_h / 2

        phase_svg.append(
            f'<rect x="{nx}" y="{ny}" width="{node_w}" height="{node_h}" rx="{c["radius"]}" fill="{c["fill"]}" stroke="{accent}" stroke-width="1.5" opacity="0.8"/>'
        )
        phase_svg.append(
            f'<rect x="{nx}" y="{ny}" width="{node_w}" height="3" rx="1" fill="{accent}" opacity="0.5"/>'
        )

        # 序号圆
        phase_svg.append(
            f'<circle cx="{nx + 16}" cy="{ny + 20}" r="10" fill="{accent}" opacity="0.12"/>\n'
            f'  <text x="{nx + 16}" y="{ny + 24}" text-anchor="middle" font-family="{f["mono"]}" font-size="10" font-weight="700" fill="{accent}">{i+1}</text>'
        )
        # 标签
        phase_svg.append(
            f'<text x="{nx + 32}" y="{ny + 24}" font-family="{f["body"]}" font-size="12" font-weight="600" fill="{tx["primary"]}">{label}</text>'
        )
        # 描述
        if desc:
            phase_svg.append(
                f'<text x="{nx + node_w/2}" y="{ny + 44}" text-anchor="middle" font-family="{f["body"]}" font-size="10" fill="{tx["secondary"]}">{desc}</text>'
            )

        # 弧形箭头到下一节点
        next_i = (i + 1) % n
        next_angle = -math.pi / 2 + 2 * math.pi * next_i / n
        mid_angle = angle + math.pi / n
        # 控制点在弧中间偏外
        ctrl_r = 1.15
        ctrl_x = cx_center + radius_x * ctrl_r * math.cos(mid_angle)
        ctrl_y = cy_center + radius_y * ctrl_r * math.sin(mid_angle)
        # 起点和终点在节点边缘
        start_r = 0.75
        end_r = 0.75
        sx = cx_center + radius_x * start_r * math.cos(angle)
        sy = cy_center + radius_y * start_r * math.sin(angle)
        ex = cx_center + radius_x * end_r * math.cos(next_angle)
        ey = cy_center + radius_y * end_r * math.sin(next_angle)

        phase_svg.append(
            f'<path d="M {sx},{sy} Q {ctrl_x},{ctrl_y} {ex},{ey}" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.25" stroke-dasharray="4,3"/>'
        )
        # 箭头
        arr_angle = math.atan2(ey - ctrl_y, ex - ctrl_x)
        arr_len = 6
        phase_svg.append(
            f'<polygon points="{ex},{ey} {ex - arr_len * math.cos(arr_angle - 0.4)},{ey - arr_len * math.sin(arr_angle - 0.4)} {ex - arr_len * math.cos(arr_angle + 0.4)},{ey - arr_len * math.sin(arr_angle + 0.4)}" fill="{accent}" opacity="0.4"/>'
        )

    # 中心装饰
    phase_svg.append(
        f'<circle cx="{cx_center}" cy="{cy_center}" r="30" fill="{c["fill"]}" opacity="0.3"/>\n'
        f'  <circle cx="{cx_center}" cy="{cy_center}" r="20" fill="{_s(t, "highlight_ring")}" opacity="0.06"/>\n'
        f'  <text x="{cx_center}" y="{cy_center + 5}" text-anchor="middle" font-family="{f["display"]}" font-size="11" font-weight="700" fill="{tx["primary"]}">循环</text>'
    )

    phases_joined = "\n  ".join(phase_svg)

    svg = f'''{header}
  {decor_svg}
  {bg_text}
  {title_area}
  {phases_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_scatter(title, data, theme_name="dark", width=800, height=600):
    """散点图：X-Y坐标系上的数据点分布，含趋势线、象限标注、聚类区域

    Args:
        title: 标题
        data: 数据点 [{"x":0.3,"y":0.7,"label":"A","size":1,"group":0}]，x/y为0-1归一化值，最多30个点
    """
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")
    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    margin = 50
    chart_pad = 30
    title_h = 65
    chart_x = margin + chart_pad + 30
    chart_y = title_h + chart_pad
    chart_w = width - 2 * margin - 2 * chart_pad - 30
    chart_h = height - chart_y - chart_pad - 60

    # ── 装饰层 ──
    bg_text = f'<text x="{width - 30}" y="100" text-anchor="end" font-family="{f["display"]}" font-size="100" font-weight="900" fill="{_s(t, "divider_accent")}" opacity="0.03">DATA</text>'

    # 标题区
    title_area = (
        f'<text x="{margin}" y="42" font-family="{f["display"]}" font-size="22" font-weight="700" fill="{tx["primary"]}">{display_title}</text>\n'
        f'  <rect x="{margin}" y="52" width="60" height="3" rx="1" fill="{_s(t, "divider_accent")}" opacity="0.6"/>\n'
        f'  <text x="{margin + 70}" y="55" font-family="{f["body"]}" font-size="12" fill="{tx["dim"]}">{len(data)} 个数据点</text>'
    )

    # 图表卡片背景
    card_svg = (
        f'<rect x="{margin}" y="{title_h - 10}" width="{width - 2*margin}" height="{height - title_h - 35}" '
        f'rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.3"/>'
    )

    # ── 象限标注 ──
    mid_x = chart_x + chart_w / 2
    mid_y = chart_y + chart_h / 2
    quadrant_svg = []
    # 十字虚线
    quadrant_svg.append(
        f'<line x1="{mid_x}" y1="{chart_y}" x2="{mid_x}" y2="{chart_y + chart_h}" stroke="{c["border"]}" stroke-width="0.8" opacity="0.15" stroke-dasharray="6,4"/>'
    )
    quadrant_svg.append(
        f'<line x1="{chart_x}" y1="{mid_y}" x2="{chart_x + chart_w}" y2="{mid_y}" stroke="{c["border"]}" stroke-width="0.8" opacity="0.15" stroke-dasharray="6,4"/>'
    )
    # 象限标签
    q_labels = [
        (chart_x + chart_w * 0.25, chart_y + 18, "低投入·高回报"),
        (chart_x + chart_w * 0.75, chart_y + 18, "高投入·高回报"),
        (chart_x + chart_w * 0.25, chart_y + chart_h - 8, "低投入·低回报"),
        (chart_x + chart_w * 0.75, chart_y + chart_h - 8, "高投入·低回报"),
    ]
    for qx, qy, ql in q_labels:
        quadrant_svg.append(
            f'<text x="{qx}" y="{qy}" text-anchor="middle" font-family="{f["body"]}" font-size="9" fill="{tx["dim"]}" opacity="0.4">{ql}</text>'
        )

    # 网格线
    grid_svg = []
    for j in range(6):
        ratio = j / 5
        gy = chart_y + chart_h - ratio * chart_h
        grid_svg.append(
            f'<line x1="{chart_x}" y1="{gy}" x2="{chart_x + chart_w}" y2="{gy}" stroke="{c["border"]}" stroke-width="0.5" opacity="0.15"/>'
        )
        grid_svg.append(
            f'<text x="{chart_x - 8}" y="{gy + 4}" text-anchor="end" font-family="{f["mono"]}" font-size="9" fill="{tx["dim"]}">{int(ratio * 100)}</text>'
        )
        gx = chart_x + ratio * chart_w
        grid_svg.append(
            f'<line x1="{gx}" y1="{chart_y}" x2="{gx}" y2="{chart_y + chart_h}" stroke="{c["border"]}" stroke-width="0.5" opacity="0.15"/>'
        )
        grid_svg.append(
            f'<text x="{gx}" y="{chart_y + chart_h + 16}" text-anchor="middle" font-family="{f["mono"]}" font-size="9" fill="{tx["dim"]}">{int(ratio * 100)}</text>'
        )

    # 坐标轴
    grid_svg.append(
        f'<line x1="{chart_x}" y1="{chart_y}" x2="{chart_x}" y2="{chart_y + chart_h}" stroke="{c["border"]}" stroke-width="1" opacity="0.3"/>'
    )
    grid_svg.append(
        f'<line x1="{chart_x}" y1="{chart_y + chart_h}" x2="{chart_x + chart_w}" y2="{chart_y + chart_h}" stroke="{c["border"]}" stroke-width="1" opacity="0.3"/>'
    )

    # ── 聚类区域（按group分组） ──
    import math
    groups = {}
    for i, d in enumerate(data[:30]):
        g = d.get("group", i % 3)
        if g not in groups:
            groups[g] = []
        dx = d.get("x", 0.5)
        dy = d.get("y", 0.5)
        groups[g].append((dx, dy))

    cluster_svg = []
    for gi, (gk, pts) in enumerate(groups.items()):
        if len(pts) < 2:
            continue
        gcolor = _palette(t, gi)
        # 计算聚类中心
        avg_x = sum(p[0] for p in pts) / len(pts)
        avg_y = sum(p[1] for p in pts) / len(pts)
        # 计算半径（最大距离）
        max_dist = max(math.sqrt((p[0] - avg_x)**2 + (p[1] - avg_y)**2) for p in pts)
        cluster_r = max(0.08, min(0.25, max_dist + 0.05))
        ccx = chart_x + avg_x * chart_w
        ccy = chart_y + chart_h - avg_y * chart_h
        cr = cluster_r * min(chart_w, chart_h)
        cluster_svg.append(
            f'<ellipse cx="{ccx}" cy="{ccy}" rx="{cr * 1.2}" ry="{cr}" fill="{gcolor}" opacity="0.04"/>'
        )
        cluster_svg.append(
            f'<ellipse cx="{ccx}" cy="{ccy}" rx="{cr * 0.8}" ry="{cr * 0.7}" fill="{gcolor}" opacity="0.04"/>'
        )

    # ── 趋势线（简单线性回归） ──
    trend_svg = []
    if len(data) >= 3:
        xs = [d.get("x", 0.5) for d in data[:30]]
        ys = [d.get("y", 0.5) for d in data[:30]]
        n_pts = len(xs)
        sum_x = sum(xs)
        sum_y = sum(ys)
        sum_xy = sum(x * y for x, y in zip(xs, ys))
        sum_x2 = sum(x * x for x in xs)
        denom = n_pts * sum_x2 - sum_x * sum_x
        if denom != 0:
            slope = (n_pts * sum_xy - sum_x * sum_y) / denom
            intercept = (sum_y - slope * sum_x) / n_pts
            # 趋势线端点
            tx1, ty1 = 0.05, slope * 0.05 + intercept
            tx2, ty2 = 0.95, slope * 0.95 + intercept
            # 裁剪到图表范围
            ty1 = max(0, min(1, ty1))
            ty2 = max(0, min(1, ty2))
            px1 = chart_x + tx1 * chart_w
            py1 = chart_y + chart_h - ty1 * chart_h
            px2 = chart_x + tx2 * chart_w
            py2 = chart_y + chart_h - ty2 * chart_h
            trend_color = _s(t, "connector_color")
            trend_svg.append(
                f'<line x1="{px1}" y1="{py1}" x2="{px2}" y2="{py2}" stroke="{trend_color}" stroke-width="1.5" opacity="0.2" stroke-dasharray="8,4"/>'
            )

    # 数据点
    points_svg = []
    for i, d in enumerate(data[:30]):
        dx = d.get("x", 0.5)
        dy = d.get("y", 0.5)
        label = d.get("label", "")[:6]
        size = d.get("size", 1)
        group = d.get("group", i % 3)
        # 按组取色
        group_idx = list(groups.keys()).index(group) if group in groups else i
        accent = _palette(t, group_idx)

        px = chart_x + dx * chart_w
        py = chart_y + chart_h - dy * chart_h
        r = max(4, min(12, size * 6))

        # 光晕
        points_svg.append(
            f'<circle cx="{px}" cy="{py}" r="{r + 4}" fill="{accent}" opacity="0.06"/>'
        )
        # 实心点
        points_svg.append(
            f'<circle cx="{px}" cy="{py}" r="{r}" fill="{accent}" opacity="0.4"/>'
        )
        # 内核
        points_svg.append(
            f'<circle cx="{px}" cy="{py}" r="{max(2, r // 2)}" fill="{accent}" opacity="0.7"/>'
        )
        # 标签
        if label:
            points_svg.append(
                f'<text x="{px}" y="{py - r - 4}" text-anchor="middle" font-family="{f["body"]}" font-size="9" fill="{tx["secondary"]}">{label}</text>'
            )

    # ── 图例 ──
    legend_svg = []
    for gi, gk in enumerate(groups.keys()):
        gcolor = _palette(t, gi)
        lx = chart_x + chart_w - 100
        ly = chart_y + 12 + gi * 18
        legend_svg.append(
            f'<circle cx="{lx}" cy="{ly}" r="4" fill="{gcolor}" opacity="0.5"/>\n'
            f'  <text x="{lx + 10}" y="{ly + 4}" font-family="{f["body"]}" font-size="10" fill="{tx["dim"]}">组{gi+1}</text>'
        )

    grid_joined = "\n  ".join(grid_svg)
    quadrant_joined = "\n  ".join(quadrant_svg)
    cluster_joined = "\n  ".join(cluster_svg)
    trend_joined = "\n  ".join(trend_svg)
    points_joined = "\n  ".join(points_svg)
    legend_joined = "\n  ".join(legend_svg)

    svg = f'''{header}
  {decor_svg}
  {bg_text}
  {title_area}
  {card_svg}
  {grid_joined}
  {quadrant_joined}
  {cluster_joined}
  {trend_joined}
  {points_joined}
  {legend_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_heatmap(title, data, theme_name="dark", width=800, height=600):
    """热力图：矩阵色块展示二维数据强度

    Args:
        title: 标题
        data: {"rows":["A","B","C"],"cols":["X","Y","Z"],"values":[[0.8,0.3,0.6],[0.2,0.9,0.4],[0.5,0.7,0.1]]}
              rows/cols为标签，values为0-1归一化值矩阵
    """
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")
    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    rows = data.get("rows", ["R1", "R2", "R3"])
    cols = data.get("cols", ["C1", "C2", "C3"])
    values = data.get("values", [[0.5]*len(cols)]*len(rows))

    n_rows = min(len(rows), 8)
    n_cols = min(len(cols), 8)

    margin = 50
    title_h = 65
    label_pad = 50
    chart_x = margin + label_pad
    chart_y = title_h + label_pad
    chart_w = width - 2 * margin - label_pad - 20
    chart_h = height - chart_y - 60

    cell_w = chart_w / n_cols
    cell_h = chart_h / n_rows

    # ── 装饰层 ──
    bg_text = f'<text x="{width - 30}" y="100" text-anchor="end" font-family="{f["display"]}" font-size="100" font-weight="900" fill="{_s(t, "divider_accent")}" opacity="0.03">HEAT</text>'

    # 标题区
    title_area = (
        f'<text x="{margin}" y="42" font-family="{f["display"]}" font-size="22" font-weight="700" fill="{tx["primary"]}">{display_title}</text>\n'
        f'  <rect x="{margin}" y="52" width="60" height="3" rx="1" fill="{_s(t, "divider_accent")}" opacity="0.6"/>\n'
        f'  <text x="{margin + 70}" y="55" font-family="{f["body"]}" font-size="12" fill="{tx["dim"]}">{n_rows}×{n_cols} 矩阵</text>'
    )

    # 图表卡片背景
    card_svg = (
        f'<rect x="{margin}" y="{title_h - 10}" width="{width - 2*margin}" height="{height - title_h - 35}" '
        f'rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.3"/>'
    )

    # 热力色：从冷色到暖色
    accent_a = _s(t, "item_accent_a")
    accent_b = _s(t, "item_accent_b")

    cells_svg = []
    for ri in range(n_rows):
        # 行标签
        ry = chart_y + ri * cell_h + cell_h / 2
        cells_svg.append(
            f'<text x="{chart_x - 8}" y="{ry + 4}" text-anchor="end" font-family="{f["body"]}" font-size="11" fill="{tx["secondary"]}">{rows[ri][:6]}</text>'
        )
        for ci in range(n_cols):
            # 列标签（仅第一行）
            if ri == 0:
                cx = chart_x + ci * cell_w + cell_w / 2
                cells_svg.append(
                    f'<text x="{cx}" y="{chart_y - 8}" text-anchor="middle" font-family="{f["body"]}" font-size="11" fill="{tx["secondary"]}">{cols[ci][:6]}</text>'
                )

            val = 0.5
            if ri < len(values) and ci < len(values[ri]):
                val = max(0, min(1, values[ri][ci]))

            cx = chart_x + ci * cell_w
            cy = chart_y + ri * cell_h

            # 色块：用accent色+透明度表示强度
            opacity = 0.1 + val * 0.6
            cells_svg.append(
                f'<rect x="{cx + 2}" y="{cy + 2}" width="{cell_w - 4}" height="{cell_h - 4}" rx="3" fill="{accent_a if val > 0.5 else accent_b}" opacity="{opacity}"/>'
            )
            # 数值标注
            if cell_w > 30 and cell_h > 20:
                display_val = f"{val:.1f}" if isinstance(val, float) else str(val)
                cells_svg.append(
                    f'<text x="{cx + cell_w/2}" y="{cy + cell_h/2 + 4}" text-anchor="middle" font-family="{f["mono"]}" font-size="10" fill="{tx["primary"]}" opacity="{0.4 + val * 0.4}">{display_val}</text>'
                )

    # 色阶图例
    legend_svg = []
    legend_x = chart_x + chart_w + 10
    legend_y = chart_y
    legend_h = chart_h
    legend_w = 16
    for li in range(10):
        ratio = li / 9
        ly = legend_y + legend_h - (li + 1) * (legend_h / 10)
        lo = 0.1 + ratio * 0.6
        lc = accent_a if ratio > 0.5 else accent_b
        legend_svg.append(
            f'<rect x="{legend_x}" y="{ly}" width="{legend_w}" height="{legend_h / 10 + 1}" fill="{lc}" opacity="{lo}"/>'
        )
    legend_svg.append(
        f'<text x="{legend_x + legend_w/2}" y="{legend_y - 4}" text-anchor="middle" font-family="{f["mono"]}" font-size="8" fill="{tx["dim"]}">1.0</text>'
    )
    legend_svg.append(
        f'<text x="{legend_x + legend_w/2}" y="{legend_y + legend_h + 12}" text-anchor="middle" font-family="{f["mono"]}" font-size="8" fill="{tx["dim"]}">0.0</text>'
    )

    cells_joined = "\n  ".join(cells_svg)
    legend_joined = "\n  ".join(legend_svg)

    svg = f'''{header}
  {decor_svg}
  {bg_text}
  {title_area}
  {card_svg}
  {cells_joined}
  {legend_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_composite(title, sections, theme_name="dark", width=800, height=600):
    """复合图：概念+图表+卡片+折线+热力混排，多区域布局

    Args:
        title: 标题
        sections: 区域列表 [{"type":"concept|chart|card|line|heat","title":"区域标题","content":...}]
                  concept: content为文字描述
                  chart: content为 [{"label":"A","value":80}]
                  card: content为 [{"title":"项1","desc":"描述"}]
                  line: content为 {"labels":["1月","2月"],"datasets":[{"label":"L","values":[10,20]}]}
                  heat: content为 {"rows":["A"],"cols":["X"],"values":[[0.5]]}
                  最多4个区域，自动2×2网格布局
    """
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")
    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    n = min(len(sections), 4)
    margin = 35
    title_h = 65

    # ── 装饰层 ──
    bg_text = f'<text x="{width - 30}" y="100" text-anchor="end" font-family="{f["display"]}" font-size="80" font-weight="900" fill="{_s(t, "divider_accent")}" opacity="0.03">MIX</text>'

    # 标题区
    title_area = (
        f'<text x="{margin}" y="42" font-family="{f["display"]}" font-size="22" font-weight="700" fill="{tx["primary"]}">{display_title}</text>\n'
        f'  <rect x="{margin}" y="52" width="60" height="3" rx="1" fill="{_s(t, "divider_accent")}" opacity="0.6"/>\n'
        f'  <text x="{margin + 70}" y="55" font-family="{f["body"]}" font-size="12" fill="{tx["dim"]}">{n} 个区域</text>'
    )

    # 自适应2×2布局
    cols = 2 if n > 1 else 1
    positions = _auto_layout(n, margin, title_h, width - 2 * margin, height - title_h - 55, cols=cols, min_item_h=100, gap=12)

    sections_svg = []
    for i, (sx, sy, sw, sh) in enumerate(positions):
        sec = sections[i]
        sec_type = sec.get("type", "concept")
        sec_title = sec.get("title", f"区域{i+1}")[:14]
        content = sec.get("content", "")
        # 每个区域使用不同颜色
        accent = _palette(t, i)

        # 区域卡片背景
        sections_svg.append(
            f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="{c["radius"]}" fill="{c["fill"]}" stroke="{c["border"]}" stroke-width="0.5" opacity="0.9"/>'
        )
        # 顶部色条
        sections_svg.append(
            f'<rect x="{sx}" y="{sy}" width="{sw}" height="3" rx="1" fill="{accent}" opacity="0.4"/>'
        )

        # 区域标题
        sections_svg.append(
            f'<text x="{sx + 14}" y="{sy + 22}" font-family="{f["body"]}" font-size="13" font-weight="600" fill="{accent}">{sec_title}</text>'
        )
        # 类型标签
        type_labels = {"concept": "概念", "chart": "图表", "card": "卡片", "line": "趋势", "heat": "热力"}
        tl = type_labels.get(sec_type, "区域")
        sections_svg.append(
            f'<rect x="{sx + sw - 42}" y="{sy + 8}" width="30" height="16" rx="8" fill="{accent}" opacity="0.1"/>\n'
            f'  <text x="{sx + sw - 27}" y="{sy + 20}" text-anchor="middle" font-family="{f["body"]}" font-size="9" fill="{accent}">{tl}</text>'
        )

        # 分割线
        sections_svg.append(
            f'<line x1="{sx + 14}" y1="{sy + 30}" x2="{sx + sw - 14}" y2="{sy + 30}" stroke="{c["border"]}" stroke-width="0.5" opacity="0.3"/>'
        )

        content_y = sy + 38
        content_h = sh - 46

        if sec_type == "concept":
            # 概念区：文字描述 + 装饰圆点
            text = str(content)[:80] if content else "暂无描述"
            line_w = sw - 28
            chars_per_line = max(10, line_w // 8)
            lines = [text[j:j+chars_per_line] for j in range(0, len(text), chars_per_line)]
            for li, line in enumerate(lines[:4]):
                ly = content_y + 14 + li * 16
                if ly < sy + sh - 10:
                    sections_svg.append(
                        f'<text x="{sx + 14}" y="{ly}" font-family="{f["body"]}" font-size="12" fill="{tx["secondary"]}">{line}</text>'
                    )
            # 装饰：右下角淡色圆
            sections_svg.append(
                f'<circle cx="{sx + sw - 20}" cy="{sy + sh - 20}" r="15" fill="{accent}" opacity="0.04"/>'
            )

        elif sec_type == "chart":
            # 图表区：迷你柱图（渐变）
            data = content if isinstance(content, list) else []
            if data:
                max_val = max((d.get("value", 0) for d in data[:8]), default=1) or 1
                bar_area_w = sw - 28
                bar_area_h = content_h - 10
                bar_count = min(len(data), 8)
                bar_gap = max(3, bar_area_w // bar_count // 5)
                single_w = (bar_area_w - (bar_count - 1) * bar_gap) // bar_count
                base_y = content_y + bar_area_h

                for bi, d in enumerate(data[:8]):
                    bv = d.get("value", 0)
                    bl = d.get("label", "")[:3]
                    bh = (bv / max_val) * bar_area_h * 0.8
                    bx = sx + 14 + bi * (single_w + bar_gap)
                    by = base_y - bh
                    bar_c = _palette(t, bi)
                    gid = f"comp_bar_{i}_{bi}"
                    sections_svg.append(
                        f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
                        f'<stop offset="0%" stop-color="{bar_c}" stop-opacity="0.6"/>'
                        f'<stop offset="100%" stop-color="{bar_c}" stop-opacity="0.15"/>'
                        f'</linearGradient></defs>'
                    )
                    sections_svg.append(
                        f'<rect x="{bx}" y="{by}" width="{single_w}" height="{bh}" rx="2" fill="url(#{gid})"/>'
                    )
                    sections_svg.append(
                        f'<text x="{bx + single_w/2}" y="{base_y + 12}" text-anchor="middle" font-family="{f["body"]}" font-size="8" fill="{tx["dim"]}">{bl}</text>'
                    )

        elif sec_type == "card":
            # 卡片区：小卡片列表
            items = content if isinstance(content, list) else []
            for ci, item in enumerate(items[:4]):
                item_title = item.get("title", str(item))[:12] if isinstance(item, dict) else str(item)[:12]
                item_desc = item.get("desc", "")[:10] if isinstance(item, dict) else ""
                iy = content_y + ci * min(24, content_h // 4)
                if iy < sy + sh - 10:
                    ic = _palette(t, ci)
                    sections_svg.append(
                        f'<rect x="{sx + 14}" y="{iy}" width="4" height="14" rx="2" fill="{ic}" opacity="0.5"/>'
                    )
                    sections_svg.append(
                        f'<text x="{sx + 24}" y="{iy + 11}" font-family="{f["body"]}" font-size="11" fill="{tx["primary"]}">{item_title}</text>'
                    )
                    if item_desc:
                        sections_svg.append(
                            f'<text x="{sx + sw - 16}" y="{iy + 11}" text-anchor="end" font-family="{f["mono"]}" font-size="9" fill="{tx["dim"]}">{item_desc}</text>'
                        )

        elif sec_type == "line":
            # 迷你折线图
            line_data = content if isinstance(content, dict) else {}
            labels = line_data.get("labels", [])
            datasets = line_data.get("datasets", [])
            if datasets:
                all_vals = [v for ds in datasets for v in ds.get("values", [])]
                if all_vals:
                    max_v = max(all_vals) or 1
                    line_area_w = sw - 28
                    line_area_h = content_h - 10
                    n_pts = len(labels) or len(datasets[0].get("values", []))
                    for di, ds in enumerate(datasets[:2]):
                        vals = ds.get("values", [])
                        lc = _palette(t, di + 2)
                        pts = []
                        for vi, v in enumerate(vals[:8]):
                            px = sx + 14 + (vi / max(n_pts - 1, 1)) * line_area_w
                            py = content_y + line_area_h - (v / max_v) * line_area_h * 0.8
                            pts.append((px, py))
                        if len(pts) >= 2:
                            path_d = "M" + " L".join(f"{p[0]},{p[1]}" for p in pts)
                            sections_svg.append(
                                f'<path d="{path_d}" fill="none" stroke="{lc}" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>'
                            )
                            for px, py in pts:
                                sections_svg.append(
                                    f'<circle cx="{px}" cy="{py}" r="2" fill="{lc}" opacity="0.5"/>'
                                )

        elif sec_type == "heat":
            # 迷你热力图
            heat_data = content if isinstance(content, dict) else {}
            rows = heat_data.get("rows", ["R1"])
            cols = heat_data.get("cols", ["C1"])
            values = heat_data.get("values", [[0.5]])
            n_rows = min(len(rows), 5)
            n_cols = min(len(cols), 5)
            heat_area_w = sw - 28
            heat_area_h = content_h - 10
            cell_w = heat_area_w / n_cols
            cell_h = heat_area_h / n_rows
            for ri in range(n_rows):
                for ci in range(n_cols):
                    val = 0.5
                    if ri < len(values) and ci < len(values[ri]):
                        val = max(0, min(1, values[ri][ci]))
                    cx = sx + 14 + ci * cell_w
                    cy = content_y + ri * cell_h
                    hc = _palette(t, 3) if val > 0.5 else _palette(t, 4)
                    ho = 0.1 + val * 0.5
                    sections_svg.append(
                        f'<rect x="{cx + 1}" y="{cy + 1}" width="{cell_w - 2}" height="{cell_h - 2}" rx="2" fill="{hc}" opacity="{ho}"/>'
                    )
                    if cell_w > 25 and cell_h > 18:
                        sections_svg.append(
                            f'<text x="{cx + cell_w/2}" y="{cy + cell_h/2 + 3}" text-anchor="middle" font-family="{f["mono"]}" font-size="8" fill="{tx["primary"]}" opacity="{0.3 + val * 0.4}">{val:.1f}</text>'
                        )

    sections_joined = "\n  ".join(sections_svg)

    svg = f'''{header}
  {decor_svg}
  {bg_text}
  {title_area}
  {sections_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


SVG_RENDERERS = {
    "title": lambda s, t: render_svg_cover(s.get("title", ""), s.get("subtitle", ""), theme_name=t),
    "stat": lambda s, t: render_svg_stat(s.get("value", ""), s.get("label", ""), s.get("sublabel", ""), theme_name=t),
    "bullet": lambda s, t: render_svg_card(s.get("title", ""), s.get("items", []), theme_name=t),
    "chart": lambda s, t: render_svg_chart(s.get("title", ""), s.get("data", []), theme_name=t),
    "quote": lambda s, t: render_svg_quote(s.get("text", ""), s.get("source", ""), theme_name=t),
    "timeline": lambda s, t: render_svg_timeline(s.get("title", ""), s.get("events", []), theme_name=t),
    "focus": lambda s, t: render_svg_focus(s.get("keyword", ""), s.get("explanation", ""), theme_name=t),
    "steps": lambda s, t: render_svg_steps(s.get("title", ""), s.get("steps", []), theme_name=t),
    "qa": lambda s, t: render_svg_qa(s.get("question", ""), s.get("answer", ""), theme_name=t),
    "compare": lambda s, t: render_svg_compare(
        s.get("title", ""), s.get("leftTitle", "A"), s.get("rightTitle", "B"),
        s.get("left", []), s.get("right", []), theme_name=t
    ),
    "summary": lambda s, t: render_svg_summary(s.get("title", ""), s.get("items", []), theme_name=t),
    "feature": lambda s, t: render_svg_feature(s.get("title", ""), s.get("features", []), theme_name=t),
    "grid": lambda s, t: render_svg_grid(s.get("title", ""), s.get("cards", []), theme_name=t),
    "line_chart": lambda s, t: render_svg_line_chart(
        s.get("title", ""), s.get("labels", []), s.get("datasets", []), theme_name=t
    ),
    "hero": lambda s, t: render_svg_hero(
        s.get("title", ""), s.get("subtitle", ""), s.get("tags", []),
        theme_name=t
    ),
    "duo_card": lambda s, t: render_svg_compare(
        s.get("title", ""), s.get("leftTitle", "A"), s.get("rightTitle", "B"),
        s.get("left", []), s.get("right", []), theme_name=t
    ),
    "list_detail": lambda s, t: render_svg_list_detail(
        s.get("title", ""), s.get("items", []), theme_name=t
    ),
    "dashboard": lambda s, t: render_svg_dashboard(
        s.get("title", ""), s.get("metrics", []), s.get("barData", []),
        s.get("listItems", []), theme_name=t
    ),
    "bar_chart": lambda s, t: render_svg_chart(
        s.get("title", ""), s.get("data", []), theme_name=t, direction="vertical"
    ),
    "metric_grid": lambda s, t: render_svg_grid(
        s.get("title", ""), s.get("metrics", []), theme_name=t, mode="metric"
    ),
    "logic_flow": lambda s, t: render_svg_logic_flow(
        s.get("title", ""), s.get("steps", []), theme_name=t
    ),
    "cycle": lambda s, t: render_svg_cycle(
        s.get("title", ""), s.get("phases", []), theme_name=t
    ),
    "scatter": lambda s, t: render_svg_scatter(
        s.get("title", ""), s.get("data", []), theme_name=t
    ),
    "heatmap": lambda s, t: render_svg_heatmap(
        s.get("title", ""), s.get("data", {}), theme_name=t
    ),
    "composite": lambda s, t: render_svg_composite(
        s.get("title", ""), s.get("sections", []), theme_name=t
    ),
}


def render_slide_svg(slide, theme_name="dark", width=800, height=600):
    stype = slide.get("type", "")
    renderer = SVG_RENDERERS.get(stype)
    if not renderer:
        return render_svg_cover(
            slide.get("title", "未知类型"),
            theme_name=theme_name, width=width, height=height
        )
    return renderer(slide, theme_name)


def save_svg(svg_content, output_path):
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    return output_path
