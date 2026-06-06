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
            "secondary": "#A8A5BE",
            "dim": "rgba(242,240,237,0.6)",
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
            "dim": "rgba(26,8,0,0.55)",
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
            "dim": "rgba(26,26,46,0.5)",
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
            "secondary": "#A8BF8E",
            "dim": "rgba(240,234,214,0.6)",
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
            "dim": "rgba(28,24,16,0.55)",
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
            "secondary": "#9090C0",
            "dim": "rgba(232,232,255,0.55)",
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
            "dim": "rgba(224,224,224,0.6)",
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
    return renderer(t, width, height)


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


def render_svg_card(title, items, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")
    card_x, card_y = 40, 40
    card_w, card_h = width - 80, height - 80

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    items_svg = []
    start_y = card_y + 100
    for i, item in enumerate(items[:7]):
        item_text = item[:30] + ("..." if len(item) > 30 else "")
        y = start_y + i * 60
        item_card_y = y - 18
        item_card_h = 44
        num_color = _item_accent(t, i)
        badge_bg = _s(t, "badge_bg")
        items_svg.append(
            f'<rect x="{card_x + 25}" y="{item_card_y}" width="{card_w - 50}" height="{item_card_h}" rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.4"/>\n'
            f'  <rect x="{card_x + 25}" y="{item_card_y}" width="3" height="{item_card_h}" rx="1" fill="{num_color}" opacity="0.7"/>\n'
            f'  <circle cx="{card_x + 50}" cy="{y}" r="10" fill="{badge_bg}"/>\n'
            f'  <text x="{card_x + 50}" y="{y + 4}" text-anchor="middle" font-family="{f["body"]}" font-size="12" font-weight="700" fill="{num_color}">{i+1}</text>\n'
            f'  <text x="{card_x + 72}" y="{y + 4}" font-family="{f["body"]}" font-size="16" fill="{tx["primary"]}">{item_text}</text>'
        )

    items_joined = "\n  ".join(items_svg)
    card_shape = svg_card(card_x, card_y, card_w, card_h, theme_name)
    divider = svg_line(card_x + 30, card_y + 75, card_x + card_w - 30, card_y + 75, theme_name, color=_s(t, "divider_accent"), element="divider")
    top_dots = (
        f'<circle cx="{card_x + 30}" cy="{card_y + 30}" r="4" fill="{_s(t, "item_accent_a")}" opacity="0.4"/>\n'
        f'  <circle cx="{card_x + 46}" cy="{card_y + 30}" r="4" fill="{_s(t, "item_accent_b")}" opacity="0.3"/>\n'
        f'  <circle cx="{card_x + 62}" cy="{card_y + 30}" r="4" fill="{_s(t, "item_accent_b")}" opacity="0.3"/>'
    )
    bottom_bar = f'<rect x="{card_x}" y="{card_y+card_h-4}" width="{card_w}" height="4" rx="2" fill="{_s(t, "divider_accent")}" opacity="0.2"/>'
    svg = f'''{header}
  {decor_svg}
  {card_shape}
  {top_dots}
  <text x="{width/2}" y="{card_y+55}" text-anchor="middle" font-family="{f["display"]}" font-size="26" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {divider}
  {items_joined}
  {bottom_bar}
</svg>'''
    return svg


def render_svg_stat(value, label, sublabel="", theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_value = value[:14] + ("..." if len(value) > 14 else "")
    display_label = label[:30] + ("..." if len(label) > 30 else "")
    display_sub = sublabel[:40] + ("..." if len(sublabel) > 40 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    # 背景大卡片
    stat_card = svg_card(60, height * 0.15, width - 120, height * 0.70, theme_name)

    # 装饰环
    ring1 = svg_circle(width / 2, height * 0.38, 90, theme_name, stroke=_s(t, "highlight_ring"))
    ring2 = svg_circle(width / 2, height * 0.38, 110, theme_name, stroke=_s(t, "item_accent_b"))

    # 顶部小标签
    tag_w = len(display_label) * 14 + 24
    tag_x = (width - tag_w) / 2

    sublabel_svg = ""
    if display_sub:
        sublabel_svg = f'<text x="{width/2}" y="{height*0.72}" text-anchor="middle" font-family="{f["body"]}" font-size="14" fill="{tx["secondary"]}">{display_sub}</text>'

    svg = f'''{header}
  {decor_svg}
  {stat_card}
  {ring2}
  {ring1}
  <text x="{width/2}" y="{height*0.40}" text-anchor="middle" font-family="{f["display"]}" font-size="72" font-weight="800" fill="{_s(t, "highlight_ring")}">{display_value}</text>
  <rect x="{tag_x}" y="{height*0.52}" width="{tag_w}" height="28" rx="14" fill="{_s(t, "badge_bg")}"/>
  <text x="{width/2}" y="{height*0.57}" text-anchor="middle" font-family="{f["body"]}" font-size="18" font-weight="600" fill="{tx["primary"]}">{display_label}</text>
  {sublabel_svg}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_quote(text, source="", theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_text = text[:200] + ("..." if len(text) > 200 else "")
    display_source = source[:30] + ("..." if len(source) > 30 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    # 引言卡片背景
    quote_card = svg_card(60, height * 0.15, width - 120, height * 0.55, theme_name)

    # 多行文本自动换行
    text_svg, text_lines = _render_multiline_text(
        width / 2, height * 0.35, display_text,
        f["display"], 22, tx["primary"],
        max_chars_per_line=18, line_height=36,
        text_anchor="middle", font_weight="700"
    )

    # 根据行数调整出处位置
    source_y = height * 0.35 + text_lines * 36 + 30
    source_svg = ""
    if display_source:
        source_svg = f'<text x="{width/2}" y="{source_y}" text-anchor="middle" font-family="{f["body"]}" font-size="14" fill="{tx["secondary"]}">—— {display_source}</text>'

    svg = f'''{header}
  {decor_svg}
  {quote_card}
  <text x="{width*0.12}" y="{height*0.28}" font-family="{f["display"]}" font-size="60" fill="{_s(t, "highlight_ring")}" opacity="0.25">"</text>
  {text_svg}
  {source_svg}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_compare(title, left_title, right_title, left_items, right_items, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")
    col_w = (width - 130) / 2
    left_x = 40
    right_x = 40 + col_w + 50
    left_accent = _s(t, "item_accent_a")
    right_accent = _s(t, "item_accent_b")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    left_items_svg = []
    for i, item in enumerate(left_items[:5]):
        txt = item[:25] + ("..." if len(item) > 25 else "")
        y = 240 + i * 60
        item_y = y - 16
        left_items_svg.append(
            f'<rect x="{left_x+10}" y="{item_y}" width="{col_w-20}" height="40" rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.35"/>\n'
            f'  <rect x="{left_x+10}" y="{item_y}" width="3" height="40" rx="1" fill="{left_accent}" opacity="0.6"/>\n'
            f'  <text x="{left_x+26}" y="{y+4}" font-family="{f["body"]}" font-size="15" fill="{tx["primary"]}">{txt}</text>'
        )

    right_items_svg = []
    for i, item in enumerate(right_items[:5]):
        txt = item[:25] + ("..." if len(item) > 25 else "")
        y = 240 + i * 60
        item_y = y - 16
        right_items_svg.append(
            f'<rect x="{right_x+10}" y="{item_y}" width="{col_w-20}" height="40" rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.35"/>\n'
            f'  <rect x="{right_x+10}" y="{item_y}" width="3" height="40" rx="1" fill="{right_accent}" opacity="0.6"/>\n'
            f'  <text x="{right_x+26}" y="{y+4}" font-family="{f["body"]}" font-size="15" fill="{tx["primary"]}">{txt}</text>'
        )

    left_items_joined = "\n  ".join(left_items_svg)
    right_items_joined = "\n  ".join(right_items_svg)
    left_card = svg_card(left_x, 100, col_w, height - 140, theme_name)
    right_card = svg_card(right_x, 100, col_w, height - 140, theme_name)
    vs_cx = width / 2
    vs_cy = height / 2
    center_divider = svg_line(width / 2, 90, width / 2, height - 40, theme_name, color=c["border"], element="connector")
    left_divider = svg_line(left_x + 20, 170, left_x + col_w - 20, 170, theme_name, color=left_accent, element="divider")
    right_divider = svg_line(right_x + 20, 170, right_x + col_w - 20, 170, theme_name, color=right_accent, element="divider")
    svg = f'''{header}
  {decor_svg}
  <text x="{width/2}" y="55" text-anchor="middle" font-family="{f["display"]}" font-size="24" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {_svg_title_underline(width, t)}
  {center_divider}
  {left_card}
  {right_card}
  <circle cx="{vs_cx}" cy="{vs_cy}" r="22" fill="{c["fill"]}" stroke="{_s(t, "highlight_ring")}" stroke-width="1.5" opacity="0.8"/>
  <text x="{vs_cx}" y="{vs_cy + 6}" text-anchor="middle" font-family="{f["display"]}" font-size="14" font-weight="700" fill="{_s(t, "highlight_ring")}">VS</text>
  <text x="{left_x+col_w/2}" y="148" text-anchor="middle" font-family="{f["display"]}" font-size="18" font-weight="700" fill="{left_accent}">{left_title}</text>
  <text x="{right_x+col_w/2}" y="148" text-anchor="middle" font-family="{f["display"]}" font-size="18" font-weight="700" fill="{right_accent}">{right_title}</text>
  {left_divider}
  {right_divider}
  {left_items_joined}
  {right_items_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_timeline(title, events, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    line_x = 130
    events_svg = []
    for i, ev in enumerate(events[:6]):
        y = 140 + i * 75
        year = ev.get("year", str(i + 1))[:10]
        ev_title = ev.get("title", "")[:20]
        ev_desc = ev.get("desc", "")[:30]
        dot_color = _item_accent(t, i)
        # 事件小卡片
        card_left = line_x + 25
        card_w = width - card_left - 40
        events_svg.append(
            f'<circle cx="{line_x}" cy="{y}" r="8" fill="{dot_color}" opacity="0.15"/>\n'
            f'  <circle cx="{line_x}" cy="{y}" r="4" fill="{dot_color}"/>\n'
            f'  <text x="{line_x-18}" y="{y+5}" text-anchor="end" font-family="{f["display"]}" font-size="13" font-weight="700" fill="{dot_color}">{year}</text>\n'
            f'  <rect x="{card_left}" y="{y-16}" width="{card_w}" height="40" rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.35"/>\n'
            f'  <rect x="{card_left}" y="{y-16}" width="3" height="40" rx="1" fill="{dot_color}" opacity="0.5"/>\n'
            f'  <text x="{card_left+14}" y="{y+2}" font-family="{f["body"]}" font-size="15" font-weight="600" fill="{tx["primary"]}">{ev_title}</text>\n'
            f'  <text x="{card_left+14}" y="{y+18}" font-family="{f["body"]}" font-size="11" fill="{tx["secondary"]}">{ev_desc}</text>'
        )

    last_y = 140 + min(len(events), 6) * 75 - 75
    events_joined = "\n  ".join(events_svg)
    timeline_axis = svg_line(line_x, 100, line_x, last_y, theme_name, color=_s(t, "connector_color"))
    svg = f'''{header}
  {decor_svg}
  <text x="{width/2}" y="55" text-anchor="middle" font-family="{f["display"]}" font-size="24" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {_svg_title_underline(width, t)}
  {timeline_axis}
  {events_joined}
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


def render_svg_qa(question, answer, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_q = question[:40] + ("..." if len(question) > 40 else "")
    display_a = answer[:80] + ("..." if len(answer) > 80 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    qa_card = svg_card(50, height * 0.10, width - 100, height * 0.80, theme_name, border=_s(t, "divider_accent"))
    qa_divider = svg_line(width * 0.15, height * 0.45, width * 0.85, height * 0.45, theme_name, color=_s(t, "divider_accent"), element="divider")

    # 问题多行
    q_svg, q_lines = _render_multiline_text(
        width / 2, height * 0.28, display_q,
        f["display"], 20, tx["primary"],
        max_chars_per_line=16, line_height=32,
        text_anchor="middle", font_weight="700"
    )

    # 答案多行
    a_start_y = height * 0.52
    a_svg, a_lines = _render_multiline_text(
        width / 2, a_start_y, display_a,
        f["body"], 16, tx["primary"],
        max_chars_per_line=20, line_height=28,
        text_anchor="middle"
    )

    svg = f'''{header}
  {decor_svg}
  {qa_card}
  <text x="{width*0.1}" y="{height*0.20}" font-family="{f["display"]}" font-size="40" fill="{_s(t, "divider_accent")}" opacity="0.25">?</text>
  {q_svg}
  {qa_divider}
  {a_svg}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_focus(keyword, explanation, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_keyword = keyword[:12] + ("..." if len(keyword) > 12 else "")
    display_exp = explanation[:80] + ("..." if len(explanation) > 80 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    # 外圈装饰
    outer_ring = svg_circle(width / 2, height * 0.32, 80, theme_name, stroke=_s(t, "highlight_ring"))
    inner_ring = svg_circle(width / 2, height * 0.32, 60, theme_name, stroke=_s(t, "highlight_ring"))

    # 解释多行
    exp_svg, exp_lines = _render_multiline_text(
        width / 2, height * 0.58, display_exp,
        f["body"], 16, tx["primary"],
        max_chars_per_line=20, line_height=28,
        text_anchor="middle"
    )

    svg = f'''{header}
  {decor_svg}
  {outer_ring}
  {inner_ring}
  <text x="{width/2}" y="{height*0.34}" text-anchor="middle" font-family="{f["display"]}" font-size="38" font-weight="800" fill="{_s(t, "highlight_ring")}">{display_keyword}</text>
  {exp_svg}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_chart(title, data, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

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
        bar_color = _item_accent(t, i)
        # 背景条
        bars_svg.append(
            f'<rect x="{bar_area_x}" y="{y}" width="{bar_area_w}" height="{bar_h}" rx="4" fill="{c["fill"]}" opacity="0.2"/>\n'
            f'  <text x="{bar_area_x-10}" y="{y+bar_h/2+5}" text-anchor="end" font-family="{f["body"]}" font-size="14" fill="{tx["primary"]}">{label}</text>\n'
            f'  <rect x="{bar_area_x}" y="{y}" width="{bar_w}" height="{bar_h}" rx="4" fill="{bar_color}" opacity="0.8"/>\n'
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
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    items_svg = []
    for i, item in enumerate(items[:7]):
        txt = item[:35] + ("..." if len(item) > 35 else "")
        y = 140 + i * 65
        num_color = _item_accent(t, i)
        # 每条用小卡片 + 左侧色条
        item_y = y - 16
        item_h = 42
        items_svg.append(
            f'<rect x="60" y="{item_y}" width="{width-120}" height="{item_h}" rx="{c["radius"]}" fill="{c["fill"]}" opacity="0.35"/>\n'
            f'  <rect x="60" y="{item_y}" width="3" height="{item_h}" rx="1" fill="{num_color}" opacity="0.6"/>\n'
            f'  <circle cx="88" cy="{y + 4}" r="12" fill="{num_color}" opacity="0.12"/>\n'
            f'  <text x="88" y="{y + 9}" text-anchor="middle" font-family="{f["display"]}" font-size="12" font-weight="700" fill="{num_color}">{i+1}</text>\n'
            f'  <text x="110" y="{y + 9}" font-family="{f["body"]}" font-size="16" fill="{tx["primary"]}">{txt}</text>'
        )

    summary_items_joined = "\n  ".join(items_svg)
    summary_divider = svg_line(60, 85, width - 60, 85, theme_name, color=_s(t, "divider_accent"), element="divider")
    svg = f'''{header}
  {decor_svg}
  <text x="{width/2}" y="55" text-anchor="middle" font-family="{f["display"]}" font-size="24" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {_svg_title_underline(width, t)}
  {summary_divider}
  {summary_items_joined}
  {_svg_bottom_bar(width, height, t)}
</svg>'''
    return svg


def render_svg_line_chart(title, labels, datasets, theme_name="dark", width=800, height=600):
    """折线图：支持多条数据线，适合趋势对比"""
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
    line_colors = [_s(t, "item_accent_a"), _s(t, "item_accent_b"), _s(t, "connector_color")]

    # 找最大值
    all_values = [v for ds in datasets for v in ds.get("values", [])]
    max_val = max(all_values) if all_values else 1
    if max_val == 0:
        max_val = 1

    # Y轴刻度线
    grid_svg = []
    for i in range(5):
        gy = chart_y + chart_h - (i / 4) * chart_h
        val = int(max_val * i / 4)
        grid_svg.append(
            f'<line x1="{chart_x}" y1="{gy}" x2="{chart_x + chart_w}" y2="{gy}" '
            f'stroke="{c["border"]}" stroke-width="0.5" stroke-dasharray="4,4"/>'
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

    # 数据线
    lines_svg = []
    dots_svg = []
    legend_svg = []
    for di, ds in enumerate(datasets[:3]):
        values = ds.get("values", [])
        ds_label = ds.get("label", "")[:8]
        color = line_colors[di % len(line_colors)]

        # 折线路径
        points = []
        for i, v in enumerate(values[:8]):
            px = chart_x + (i / max(n - 1, 1)) * chart_w
            py = chart_y + chart_h - (v / max_val) * chart_h
            points.append(f"{px},{py}")
            dots_svg.append(
                f'<circle cx="{px}" cy="{py}" r="4" fill="{color}" opacity="0.9"/>'
            )

        if len(points) >= 2:
            path_d = "M" + " L".join(points)
            # 填充区域
            fill_path = f"M{chart_x},{chart_y + chart_h} L" + " L".join(points) + f" L{chart_x + chart_w},{chart_y + chart_h} Z"
            lines_svg.append(
                f'<path d="{fill_path}" fill="{color}" opacity="0.08"/>'
            )
            lines_svg.append(
                f'<path d="{path_d}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
            )

        # 图例
        legend_x = chart_x + di * 120
        legend_y = chart_y - 35
        legend_svg.append(
            f'<rect x="{legend_x}" y="{legend_y}" width="12" height="12" rx="2" fill="{color}"/>'
        )
        legend_svg.append(
            f'<text x="{legend_x + 18}" y="{legend_y + 10}" font-family="{f["body"]}" font-size="12" fill="{tx["primary"]}">{ds_label}</text>'
        )

    grid_joined = "\n  ".join(grid_svg)
    labels_joined = "\n  ".join(x_labels_svg)
    lines_joined = "\n  ".join(lines_svg)
    dots_joined = "\n  ".join(dots_svg)
    legend_joined = "\n  ".join(legend_svg)

    svg = f'''{header}
  {decor_svg}
  <text x="{width/2}" y="45" text-anchor="middle" font-family="{f["display"]}" font-size="22" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {legend_joined}
  {grid_joined}
  {lines_joined}
  {dots_joined}
  {labels_joined}
  <rect x="{chart_x}" y="{chart_y + chart_h}" width="{chart_w}" height="1" fill="{c["border"]}"/>
  <rect x="50" y="{height-44}" width="{width-100}" height="4" rx="2" fill="{_s(t, "divider_accent")}" opacity="0.15"/>
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


def render_svg_grid(title, cards, theme_name="dark", width=800, height=600):
    """组合布局：2×2或2×3卡片网格，适合多维对比或多要点展示"""
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:20] + ("..." if len(title) > 20 else "")
    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    cols = 2
    rows = min((len(cards) + 1) // 2, 3)
    card_count = min(len(cards), cols * rows)
    margin_x, margin_y = 40, 100
    gap = 20
    card_w = (width - 2 * margin_x - gap) // cols
    card_h = (height - margin_y - margin_y - gap * (rows - 1)) // rows

    cards_svg = []
    for i in range(card_count):
        card = cards[i]
        card_title = card.get("title", "")[:10] + ("..." if len(card.get("title", "")) > 10 else "")
        card_desc = card.get("desc", "")[:25] + ("..." if len(card.get("desc", "")) > 25 else "")
        col = i % cols
        row = i // cols
        cx = margin_x + col * (card_w + gap)
        cy = margin_y + row * (card_h + gap)
        accent_color = _item_accent(t, i)
        # 卡片背景
        cards_svg.append(
            f'<rect x="{cx}" y="{cy}" width="{card_w}" height="{card_h}" '
            f'rx="{c["radius"]}" fill="{c["fill"]}" stroke="{c["border"]}" stroke-width="1"/>'
        )
        # 左侧色条
        cards_svg.append(
            f'<rect x="{cx}" y="{cy}" width="4" height="{card_h}" rx="2" fill="{accent_color}" opacity="0.6"/>'
        )
        # 顶部色条
        cards_svg.append(
            f'<rect x="{cx}" y="{cy}" width="{card_w}" height="3" rx="1" fill="{accent_color}" opacity="0.5"/>'
        )
        # 序号圆点
        cards_svg.append(
            f'<circle cx="{cx + 30}" cy="{cy + 35}" r="14" fill="{accent_color}" opacity="0.1"/>'
        )
        cards_svg.append(
            f'<text x="{cx + 30}" y="{cy + 40}" text-anchor="middle" font-family="{f["display"]}" font-size="16" font-weight="800" '
            f'fill="{accent_color}" opacity="0.6">0{i+1}</text>'
        )
        # 标题
        cards_svg.append(
            f'<text x="{cx + 55}" y="{cy + 40}" font-family="{f["body"]}" font-size="17" font-weight="600" '
            f'fill="{tx["primary"]}">{card_title}</text>'
        )
        # 分割线
        cards_svg.append(
            f'<line x1="{cx + 15}" y1="{cy + 55}" x2="{cx + card_w - 15}" y2="{cy + 55}" stroke="{c["border"]}" stroke-width="0.5" opacity="0.5"/>'
        )
        # 描述
        cards_svg.append(
            f'<text x="{cx + 20}" y="{cy + 78}" font-family="{f["body"]}" font-size="13" '
            f'fill="{tx["secondary"]}">{card_desc}</text>'
        )

    cards_joined = "\n  ".join(cards_svg)
    svg = f'''{header}
  {decor_svg}
  <text x="{width/2}" y="55" text-anchor="middle" font-family="{f["display"]}" font-size="24" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {_svg_title_underline(width, t)}
  {cards_joined}
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
