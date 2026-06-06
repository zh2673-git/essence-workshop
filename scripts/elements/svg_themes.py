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
            "fill": "rgba(255,255,255,0.06)",
            "border": "rgba(255,255,255,0.1)",
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
        "mood": ["温暖", "生活", "教育", "成长", "阅读", "写作", "人文"],
    },
    "minimal": {
        "name": "minimal",
        "label": "极简",
        "bg": {
            "bg1": "#E8E8EE", "bg2": "#DDDEE6", "bg3": "#D2D3DC",
            "layout": "accent-edge",
            "edge_color": "#2A2A40",
            "edge_width": 3,
        },
        "palette": {
            "accent": "#2A2A40",
            "accentGlow": "rgba(42,42,64,0.12)",
            "gold": "#50506A",
            "goldDim": "rgba(80,80,106,0.25)",
            "cyan": "#4A6A8A",
            "cyanDim": "rgba(74,106,138,0.15)",
            "success": "#2D8C3C",
            "warn": "#CC8800",
        },
        "text": {
            "primary": "#0E0E1E",
            "secondary": "#3A3A52",
            "dim": "rgba(14,14,30,0.6)",
            "inverse": "#E8E8EE",
        },
        "card": {
            "fill": "rgba(255,255,255,0.65)",
            "border": "rgba(42,42,64,0.08)",
            "radius": 16,
            "shadow": "rgba(42,42,64,0.06)",
        },
        "decor": {
            "style": "lines",
            "opacity": 0.22,
            "elements": ["thin-lines", "single-accent", "whitespace"],
        },
        "atmosphere": {
            "glow": [
                {"cx": 0.5, "cy": 0.5, "r": 0.5, "color": "accent", "alpha": 0.06},
            ],
            "gradient_dir": "vertical",
            "grain": 0,
        },
        "font": {
            "display": "'Helvetica Neue','PingFang SC','Microsoft YaHei',sans-serif",
            "body": "'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif",
            "mono": "'JetBrains Mono','Fira Code',monospace",
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
            "fill": "rgba(255,255,255,0.06)",
            "border": "rgba(212,168,67,0.12)",
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
        "mood": ["自然", "生态", "环保", "中医", "养生", "本草", "天地"],
    },
    "ink": {
        "name": "ink",
        "label": "水墨",
        "bg": {
            "bg1": "#E8E2D6", "bg2": "#DED8CA", "bg3": "#D4CEC0",
            "layout": "ink-wash",
            "ink_color": "#2E2820",
            "ink_x": 0.65,
            "ink_opacity": 0.08,
        },
        "palette": {
            "accent": "#943828",
            "accentGlow": "rgba(148,56,40,0.14)",
            "gold": "#2E2820",
            "goldDim": "rgba(46,40,32,0.30)",
            "cyan": "#5A6A72",
            "cyanDim": "rgba(90,106,114,0.14)",
            "success": "#4A7C59",
            "warn": "#B8860B",
        },
        "text": {
            "primary": "#1E1A14",
            "secondary": "#4A4238",
            "dim": "rgba(30,26,20,0.6)",
            "inverse": "#E8E2D6",
        },
        "card": {
            "fill": "rgba(255,255,255,0.55)",
            "border": "rgba(148,56,40,0.10)",
            "radius": 20,
            "shadow": "rgba(46,40,32,0.06)",
        },
        "decor": {
            "style": "brush",
            "opacity": 0.18,
            "elements": ["ink-wash", "seal-stamp", "bamboo-line"],
        },
        "atmosphere": {
            "glow": [
                {"cx": 0.5, "cy": 0.5, "r": 0.6, "color": "accent", "alpha": 0.06},
            ],
            "gradient_dir": "vertical",
            "grain": 0.008,
        },
        "font": {
            "display": "'Noto Serif SC','STSong','SimSun',serif",
            "body": "'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif",
            "mono": "'JetBrains Mono','Fira Code',monospace",
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
            "fill": "rgba(255,255,255,0.05)",
            "border": "rgba(255,77,141,0.15)",
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
            "fill": "rgba(255,255,255,0.06)",
            "border": "rgba(255,255,255,0.1)",
            "radius": 32,
            "shadow": "rgba(201,100,66,0.12)",
        },
        "decor": {
            "style": "circles",
            "opacity": 0.12,
            "elements": ["floating-circles", "accent-line", "diamonds", "curves", "cross-stars", "dot-matrix"],
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
        "mood": ["认知", "思维", "本质", "哲学", "深度", "沉思", "智慧", "洞察"],
    },
}

VALID_THEME_NAMES = set(THEMES.keys())


def get_theme(name):
    if name not in THEMES:
        raise ValueError(f"Unknown theme: {name}. Valid: {', '.join(sorted(VALID_THEME_NAMES))}")
    return THEMES[name]


def match_theme(text):
    scores = {name: 0 for name in THEMES}
    for name, theme in THEMES.items():
        for keyword in theme["mood"]:
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
    # 远景：大圆低透明度
    parts.append(f'<circle cx="{w*0.82}" cy="{h*0.12}" r="55" fill="{p["accent"]}" opacity="{op*0.06}"/>')
    parts.append(f'<circle cx="{w*0.15}" cy="{h*0.88}" r="45" fill="{p["cyan"]}" opacity="{op*0.05}"/>')
    # 中景：圆环（4个，更丰富）
    for i in range(4):
        cx = w * (0.72 + i * 0.08)
        cy = h * (0.15 + (i % 2) * 0.55)
        r = 28 + i * 18
        color = p["accent"] if i % 2 == 0 else p["cyan"]
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="1" opacity="{op}"/>')
    parts.append(f'<circle cx="{w*0.85}" cy="{h*0.2}" r="40" fill="none" stroke="{p["gold"]}" stroke-width="0.6" opacity="{op * 0.5}"/>')
    # 近景：小圆点（5个）
    for i in range(5):
        dx = w * (0.65 + i * 0.07)
        dy = h * (0.90 - i * 0.04)
        parts.append(f'<circle cx="{dx}" cy="{dy}" r="2.5" fill="{p["accent"]}" opacity="{op*0.5}"/>')
    # 近景：小菱形（3个，多位置）
    for dx, dy, ds, c in [(w*0.88, h*0.42, 8, p["gold"]), (w*0.12, h*0.35, 6, p["cyan"]), (w*0.75, h*0.78, 5, p["accent"])]:
        pts = f"{dx},{dy-ds} {dx+ds},{dy} {dx},{dy+ds} {dx-ds},{dy}"
        parts.append(f'<polygon points="{pts}" fill="none" stroke="{c}" stroke-width="0.7" opacity="{op*0.4}"/>')
    # 近景：曲线（2条）
    parts.append(
        f'<path d="M{w*0.6},{h*0.75} Q{w*0.75},{h*0.68} {w*0.9},{h*0.72}" '
        f'fill="none" stroke="{p["cyan"]}" stroke-width="0.8" opacity="{op * 0.4}"/>'
    )
    parts.append(
        f'<path d="M{w*0.55},{h*0.35} Q{w*0.68},{h*0.28} {w*0.82},{h*0.32}" '
        f'fill="none" stroke="{p["gold"]}" stroke-width="0.6" opacity="{op * 0.3}"/>'
    )
    # 近景：十字星（3个）
    for sx, sy, sl, sc in [(w*0.78, h*0.08, 12, p["gold"]), (w*0.22, h*0.15, 8, p["cyan"]), (w*0.92, h*0.55, 10, p["accent"])]:
        parts.append(f'<line x1="{sx-sl}" y1="{sy}" x2="{sx+sl}" y2="{sy}" stroke="{sc}" stroke-width="0.5" opacity="{op*0.6}"/>')
        parts.append(f'<line x1="{sx}" y1="{sy-sl}" x2="{sx}" y2="{sy+sl}" stroke="{sc}" stroke-width="0.5" opacity="{op*0.6}"/>')
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
    # 远景：大圆低透明度
    parts.append(f'<circle cx="{w*0.82}" cy="{h*0.15}" r="50" fill="{p["accent"]}" opacity="{op*0.06}"/>')
    parts.append(f'<circle cx="{w*0.15}" cy="{h*0.85}" r="40" fill="{p["cyan"]}" opacity="{op*0.05}"/>')
    # 中景：圆环
    for i in range(3):
        cx = w * (0.70 + i * 0.12)
        cy = h * (0.18 + (i % 2) * 0.50)
        r = 22 + i * 14
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{p["accent"]}" stroke-width="0.8" opacity="{op}"/>')
    # 中景：曲线
    parts.append(
        f'<path d="M{w*0.6},{h*0.75} Q{w*0.75},{h*0.68} {w*0.9},{h*0.72}" '
        f'fill="none" stroke="{p["cyan"]}" stroke-width="0.8" opacity="{op * 0.4}"/>'
    )
    parts.append(
        f'<path d="M{w*0.55},{h*0.35} Q{w*0.68},{h*0.28} {w*0.82},{h*0.32}" '
        f'fill="none" stroke="{p["gold"]}" stroke-width="0.6" opacity="{op * 0.3}"/>'
    )
    parts.append(f'<circle cx="{w*0.82}" cy="{h*0.18}" r="30" fill="none" stroke="{p["cyan"]}" stroke-width="0.5" opacity="{op * 0.35}"/>')
    # 近景：小点
    for i in range(5):
        dx = w * (0.62 + i * 0.07)
        dy = h * (0.88 - i * 0.03)
        parts.append(f'<circle cx="{dx}" cy="{dy}" r="2" fill="{p["accent"]}" opacity="{op*0.5}"/>')
    # 近景：小菱形
    dx, dy = w*0.88, h*0.42
    ds = 6
    pts = f"{dx},{dy-ds} {dx+ds},{dy} {dx},{dy+ds} {dx-ds},{dy}"
    parts.append(f'<polygon points="{pts}" fill="{p["gold"]}" opacity="{op*0.4}"/>')
    return "\n    ".join(parts)


def _svg_decor_lines(t, w, h):
    parts = []
    p = t["palette"]
    op = t["decor"]["opacity"]
    # 远景：大矩形低透明度
    parts.append(f'<rect x="{w*0.70}" y="{h*0.06}" width="60" height="40" fill="{p["accent"]}" opacity="{op*0.05}" rx="2"/>')
    parts.append(f'<rect x="{w*0.12}" y="{h*0.80}" width="50" height="35" fill="{p["cyan"]}" opacity="{op*0.04}" rx="2"/>')
    # 中景：线框矩形
    for i in range(2):
        rx = w * (0.68 + i * 0.14)
        ry = h * (0.08 + (i % 2) * 0.40)
        rw = 40 + i * 16
        rh = 28 + i * 12
        parts.append(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="none" stroke="{p["accent"]}" stroke-width="0.8" opacity="{op * 0.7}" rx="2"/>')
    # 中景：十字线
    for i in range(2):
        cx = w * (0.72 + i * 0.15)
        cy = h * (0.60 + (i % 2) * 0.20)
        size = 10 + i * 4
        parts.append(
            f'<line x1="{cx-size}" y1="{cy}" x2="{cx+size}" y2="{cy}" stroke="{p["cyan"]}" stroke-width="0.8" opacity="{op * 0.6}"/>'
        )
        parts.append(
            f'<line x1="{cx}" y1="{cy-size}" x2="{cx}" y2="{cy+size}" stroke="{p["cyan"]}" stroke-width="0.8" opacity="{op * 0.6}"/>'
        )
    # 中景：长横线
    parts.append(
        f'<line x1="{w*0.6}" y1="{h*0.52}" x2="{w*0.95}" y2="{h*0.52}" stroke="{p["accent"]}" stroke-width="0.5" opacity="{op * 0.4}"/>'
    )
    # 近景：菱形
    dx = w * 0.82
    dy = h * 0.72
    ds = 14
    pts = f"{dx},{dy-ds} {dx+ds},{dy} {dx},{dy+ds} {dx-ds},{dy}"
    parts.append(f'<polygon points="{pts}" fill="none" stroke="{p["cyan"]}" stroke-width="0.7" opacity="{op * 0.45}"/>')
    # 近景：小点
    for i in range(3):
        dx = w * (0.70 + i * 0.09)
        dy = h * (0.92 - i * 0.03)
        parts.append(f'<circle cx="{dx}" cy="{dy}" r="2" fill="{p["accent"]}" opacity="{op*0.4}"/>')
    return "\n    ".join(parts)


def _svg_decor_organic(t, w, h):
    parts = []
    p = t["palette"]
    op = t["decor"]["opacity"]
    # 远景：大椭圆低透明度
    parts.append(f'<ellipse cx="{w*0.78}" cy="{h*0.20}" rx="50" ry="30" fill="{p["gold"]}" opacity="{op*0.06}"/>')
    parts.append(f'<ellipse cx="{w*0.18}" cy="{h*0.82}" rx="40" ry="25" fill="{p["accent"]}" opacity="{op*0.05}"/>')
    # 中景：波浪曲线
    for i in range(2):
        cy = h * (0.20 + i * 0.50)
        amp = 20 + i * 10
        parts.append(
            f'<path d="M{w*0.55},{cy} Q{w*0.7},{cy-amp} {w*0.85},{cy} T{w},{cy}" '
            f'fill="none" stroke="{p["gold"]}" stroke-width="1" opacity="{op}"/>'
        )
    parts.append(
        f'<path d="M{w*0.6},{h*0.85} Q{w*0.75},{h*0.78} {w*0.9},{h*0.82}" '
        f'fill="none" stroke="{p["accent"]}" stroke-width="1" opacity="{op * 0.5}"/>'
    )
    # 近景：叶片形小点
    for i in range(3):
        dx = w * (0.72 + i * 0.08)
        dy = h * (0.92 - i * 0.03)
        parts.append(f'<circle cx="{dx}" cy="{dy}" r="3" fill="{p["gold"]}" opacity="{op*0.35}"/>')
    # 近景：小弧线
    parts.append(
        f'<path d="M{w*0.80},{h*0.60} Q{w*0.86},{h*0.56} {w*0.92},{h*0.58}" '
        f'fill="none" stroke="{p["accent"]}" stroke-width="0.8" opacity="{op*0.4}"/>'
    )
    return "\n    ".join(parts)


def _svg_decor_brush(t, w, h):
    parts = []
    p = t["palette"]
    op = t["decor"]["opacity"]
    # 远景：大墨晕
    parts.append(f'<circle cx="{w*0.80}" cy="{h*0.15}" r="45" fill="{p["gold"]}" opacity="{op*0.08}"/>')
    parts.append(f'<circle cx="{w*0.14}" cy="{h*0.85}" r="35" fill="{p["accent"]}" opacity="{op*0.06}"/>')
    # 中景：墨点
    for i in range(2):
        cx = w * (0.72 + i * 0.15)
        cy = h * (0.18 + (i % 2) * 0.50)
        r = 20 + i * 12
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{p["gold"]}" opacity="{op * 0.12}"/>')
    # 中景：笔触曲线
    parts.append(
        f'<path d="M{w*0.6},{h*0.5} Q{w*0.75},{h*0.42} {w*0.9},{h*0.48}" '
        f'fill="none" stroke="{p["gold"]}" stroke-width="1.2" opacity="{op * 0.6}" stroke-linecap="round"/>'
    )
    parts.append(
        f'<path d="M{w*0.55},{h*0.70} Q{w*0.70},{h*0.65} {w*0.85},{h*0.68}" '
        f'fill="none" stroke="{p["accent"]}" stroke-width="0.8" opacity="{op * 0.4}" stroke-linecap="round"/>'
    )
    # 中景：圆环
    parts.append(f'<circle cx="{w*0.85}" cy="{h*0.15}" r="18" fill="none" stroke="{p["accent"]}" stroke-width="0.8" opacity="{op * 0.5}"/>')
    # 近景：小方块（印章感）
    parts.append(f'<rect x="{w*0.82}" y="{h*0.72}" width="14" height="14" fill="{p["accent"]}" opacity="{op * 0.3}" rx="2"/>')
    # 近景：小点
    for i in range(3):
        dx = w * (0.70 + i * 0.08)
        dy = h * (0.90 - i * 0.03)
        parts.append(f'<circle cx="{dx}" cy="{dy}" r="2" fill="{p["gold"]}" opacity="{op*0.4}"/>')
    return "\n    ".join(parts)


def _svg_decor_neon(t, w, h):
    parts = []
    p = t["palette"]
    op = t["decor"]["opacity"]
    hex_r = 24
    # 远景：大六边形低透明度
    pts_far = []
    for j in range(6):
        angle = math.pi / 3 * j - math.pi / 6
        px = w * 0.82 + 40 * math.cos(angle)
        py = h * 0.12 + 40 * math.sin(angle)
        pts_far.append(f"{px:.1f},{py:.1f}")
    parts.append(f'<polygon points="{" ".join(pts_far)}" fill="{p["accent"]}" opacity="{op*0.06}"/>')
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
        parts.append(f'<polygon points="{points_str}" fill="none" stroke="{p["accent"]}" stroke-width="0.7" opacity="{op * 0.6}"/>')
    # 中景：折线
    parts.append(
        f'<path d="M{w*0.65},{h*0.85} L{w*0.75},{h*0.85} L{w*0.80},{h*0.78} L{w*0.92},{h*0.78}" '
        f'fill="none" stroke="{p["accent"]}" stroke-width="0.6" opacity="{op * 0.4}"/>'
    )
    parts.append(f'<circle cx="{w*0.88}" cy="{h*0.2}" r="14" fill="none" stroke="{p["gold"]}" stroke-width="0.7" opacity="{op * 0.5}"/>')
    # 近景：小点
    for i in range(4):
        dx = w * (0.68 + i * 0.07)
        dy = h * (0.92 - i * 0.03)
        parts.append(f'<circle cx="{dx}" cy="{dy}" r="2" fill="{p["accent"]}" opacity="{op*0.45}"/>')
    # 近景：小三角
    tx, ty = w*0.15, h*0.40
    ts = 8
    parts.append(f'<polygon points="{tx},{ty-ts} {tx+ts},{ty+ts} {tx-ts},{ty+ts}" fill="none" stroke="{p["gold"]}" stroke-width="0.6" opacity="{op*0.35}"/>')
    return "\n    ".join(parts)


_DECOR_RENDERERS = {
    "circles": _svg_decor_circles,
    "dots": _svg_decor_dots,
    "lines": _svg_decor_lines,
    "organic": _svg_decor_organic,
    "brush": _svg_decor_brush,
    "neon": _svg_decor_neon,
}


def render_svg_decor(theme_name, width, height):
    t = get_theme(theme_name)
    style = t["decor"]["style"]
    renderer = _DECOR_RENDERERS.get(style)
    if not renderer:
        return ""
    return renderer(t, width, height)


def render_svg_atmosphere_defs(theme_name, width, height):
    t = get_theme(theme_name)
    atm = t.get("atmosphere", {})
    p = t["palette"]
    bg = t["bg"]
    parts = []

    grad_dir = atm.get("gradient_dir", "vertical")
    if grad_dir == "diagonal":
        parts.append(
            f'<linearGradient id="bg-grad" x1="0" y1="0" x2="1" y2="1">\n'
            f'  <stop offset="0%" stop-color="{bg["bg1"]}"/>\n'
            f'  <stop offset="50%" stop-color="{bg["bg2"]}"/>\n'
            f'  <stop offset="100%" stop-color="{bg["bg3"]}"/>\n'
            f'</linearGradient>'
        )
    elif grad_dir == "radial":
        parts.append(
            f'<radialGradient id="bg-grad" cx="50%" cy="40%" r="70%">\n'
            f'  <stop offset="0%" stop-color="{bg["bg2"]}"/>\n'
            f'  <stop offset="60%" stop-color="{bg["bg1"]}"/>\n'
            f'  <stop offset="100%" stop-color="{bg["bg3"]}"/>\n'
            f'</radialGradient>'
        )
    else:
        parts.append(
            f'<linearGradient id="bg-grad" x1="0" y1="0" x2="0" y2="1">\n'
            f'  <stop offset="0%" stop-color="{bg["bg1"]}"/>\n'
            f'  <stop offset="50%" stop-color="{bg["bg2"]}"/>\n'
            f'  <stop offset="100%" stop-color="{bg["bg3"]}"/>\n'
            f'</linearGradient>'
        )

    for i, glow in enumerate(atm.get("glow", [])):
        color_key = glow.get("color", "accent")
        color_val = p.get(color_key, p["accent"])
        alpha = glow.get("alpha", 0.06)
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
        px = int(width * bg.get("panel_x", 0.62))
        pc = bg.get("panel_color", "#3A3C58")
        parts.append(f'<rect x="{px}" y="0" width="{width - px}" height="{height}" fill="{pc}" opacity="0.35"/>')

    elif layout == "soft-glow":
        gc = bg.get("glow_color", "#F5EDE0")
        gcx = bg.get("glow_cx", 0.78)
        gcy = bg.get("glow_cy", 0.72)
        gr = bg.get("glow_r", 0.4)
        ga = bg.get("glow_alpha", 0.3)
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
        sa = bg.get("sky_alpha", 0.2)
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
        io = bg.get("ink_opacity", 0.08)
        cx = int(width * ix)
        r = int(min(width, height) * 0.45)
        parts.append(f'<circle cx="{cx}" cy="{int(height * 0.4)}" r="{r}" fill="{ic}" opacity="{io}"/>')
        parts.append(f'<circle cx="{cx + 50}" cy="{int(height * 0.55)}" r="{int(r * 0.5)}" fill="{ic}" opacity="{io * 0.6}"/>')

    elif layout == "diagonal-beam":
        bc = bg.get("beam_color", "#FF4D8D")
        bo = bg.get("beam_opacity", 0.06)
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
  <rect x="{accent_x}" y="{accent_y}" width="{accent_w}" height="3" fill="{p["accent"]}" rx="1.5"/>
  <text x="{accent_x}" y="{accent_y + 38}" font-family="{f["display"]}" font-size="32" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  <text x="{accent_x}" y="{accent_y + 62}" font-family="{f["body"]}" font-size="15" fill="{tx["secondary"]}">{display_author}</text>
  <line x1="{accent_x}" y1="{height - 50}" x2="{width - 50}" y2="{height - 50}" stroke="{p["accent"]}" stroke-width="0.6" opacity="0.25"/>
  <text x="{accent_x}" y="{height - 28}" font-family="{f["body"]}" font-size="12" fill="{tx["secondary"]}" opacity="0.8">{display_sub}</text>
  <circle cx="{width - 55}" cy="{height - 30}" r="3" fill="{p["accent"]}" opacity="0.5"/>
  <rect x="0" y="{height - 4}" width="{width}" height="4" fill="{p["accent"]}" opacity="0.15"/>
</svg>'''
    return svg


def render_svg_card(title, items, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    f = t["font"]

    display_title = title[:15] + ("..." if len(title) > 15 else "")
    card_x, card_y = 40, 40
    card_w, card_h = width - 80, height - 80

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    items_svg = []
    start_y = card_y + 100
    for i, item in enumerate(items[:5]):
        item_text = item[:20] + ("..." if len(item) > 20 else "")
        y = start_y + i * 60
        bullet_svg = svg_bullet(card_x + 40, y, theme_name)
        items_svg.append(
            f'{bullet_svg}\n'
            f'  <text x="{card_x+60}" y="{y+5}" font-family="{f["body"]}" font-size="18" fill="{tx["primary"]}">{item_text}</text>'
        )

    items_joined = "\n  ".join(items_svg)
    card_shape = svg_card(card_x, card_y, card_w, card_h, theme_name)
    divider = svg_line(card_x + 30, card_y + 75, card_x + card_w - 30, card_y + 75, theme_name, color=p["accent"], element="divider")
    # 底部装饰条
    bottom_bar = f'<rect x="{card_x}" y="{card_y+card_h-4}" width="{card_w}" height="4" rx="2" fill="{p["accent"]}" opacity="0.2"/>'
    svg = f'''{header}
  {decor_svg}
  {card_shape}
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

    display_value = value[:10] + ("..." if len(value) > 10 else "")
    display_label = label[:20] + ("..." if len(label) > 20 else "")
    display_sub = sublabel[:30] + ("..." if len(sublabel) > 30 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    sublabel_svg = ""
    if display_sub:
        sublabel_svg = f'<text x="{width/2}" y="{height*0.72}" text-anchor="middle" font-family="{f["body"]}" font-size="14" fill="{tx["secondary"]}">{display_sub}</text>'

    svg = f'''{header}
  {decor_svg}
  <text x="{width/2}" y="{height*0.40}" text-anchor="middle" font-family="{f["display"]}" font-size="80" font-weight="800" fill="{p["accent"]}">{display_value}</text>
  <text x="{width/2}" y="{height*0.55}" text-anchor="middle" font-family="{f["body"]}" font-size="22" fill="{tx["primary"]}">{display_label}</text>
  {sublabel_svg}
  <rect x="{width*0.3}" y="{height*0.82}" width="{width*0.4}" height="3" rx="1.5" fill="{p["accent"]}" opacity="0.2"/>
</svg>'''
    return svg


def render_svg_quote(text, source="", theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_text = text[:120] + ("..." if len(text) > 120 else "")
    display_source = source[:20] + ("..." if len(source) > 20 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    source_svg = ""
    if display_source:
        source_svg = f'<text x="{width/2}" y="{height*0.75}" text-anchor="middle" font-family="{f["body"]}" font-size="14" fill="{tx["secondary"]}">—— {display_source}</text>'

    svg = f'''{header}
  {decor_svg}
  <text x="{width*0.1}" y="{height*0.30}" font-family="{f["display"]}" font-size="60" fill="{p["accent"]}" opacity="0.3">"</text>
  <text x="{width/2}" y="{height*0.48}" text-anchor="middle" font-family="{f["display"]}" font-size="24" font-weight="700" fill="{tx["primary"]}">{display_text}</text>
  {source_svg}
  <rect x="{width*0.3}" y="{height*0.85}" width="{width*0.4}" height="3" rx="1.5" fill="{p["accent"]}" opacity="0.15"/>
</svg>'''
    return svg


def render_svg_compare(title, left_title, right_title, left_items, right_items, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:15] + ("..." if len(title) > 15 else "")
    col_w = (width - 120) / 2
    left_x = 40
    right_x = 40 + col_w + 40

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    left_items_svg = []
    for i, item in enumerate(left_items[:4]):
        txt = item[:18] + ("..." if len(item) > 18 else "")
        y = 230 + i * 55
        left_items_svg.append(
            f'<text x="{left_x+20}" y="{y}" font-family="{f["body"]}" font-size="16" fill="{tx["primary"]}">• {txt}</text>'
        )

    right_items_svg = []
    for i, item in enumerate(right_items[:4]):
        txt = item[:18] + ("..." if len(item) > 18 else "")
        y = 230 + i * 55
        right_items_svg.append(
            f'<text x="{right_x+20}" y="{y}" font-family="{f["body"]}" font-size="16" fill="{tx["primary"]}">• {txt}</text>'
        )

    left_items_joined = "\n  ".join(left_items_svg)
    right_items_joined = "\n  ".join(right_items_svg)
    left_card = svg_card(left_x, 100, col_w, height - 140, theme_name)
    right_card = svg_card(right_x, 100, col_w, height - 140, theme_name)
    center_divider = svg_line(width / 2, 90, width / 2, height - 40, theme_name, color=c["border"], element="connector")
    left_divider = svg_line(left_x + 20, 160, left_x + col_w - 20, 160, theme_name, color=p["accent"], element="divider")
    right_divider = svg_line(right_x + 20, 160, right_x + col_w - 20, 160, theme_name, color=p["cyan"], element="divider")
    svg = f'''{header}
  {decor_svg}
  <text x="{width/2}" y="60" text-anchor="middle" font-family="{f["display"]}" font-size="24" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {center_divider}
  {left_card}
  {right_card}
  <text x="{left_x+col_w/2}" y="140" text-anchor="middle" font-family="{f["display"]}" font-size="18" font-weight="700" fill="{p["accent"]}">{left_title}</text>
  <text x="{right_x+col_w/2}" y="140" text-anchor="middle" font-family="{f["display"]}" font-size="18" font-weight="700" fill="{p["cyan"]}">{right_title}</text>
  {left_divider}
  {right_divider}
  {left_items_joined}
  {right_items_joined}
</svg>'''
    return svg


def render_svg_timeline(title, events, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:15] + ("..." if len(title) > 15 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    line_x = 120
    events_svg = []
    for i, ev in enumerate(events[:5]):
        y = 140 + i * 90
        year = ev.get("year", str(i + 1))[:8]
        ev_title = ev.get("title", "")[:15]
        ev_desc = ev.get("desc", "")[:20]
        dot_color = p["accent"] if i % 2 == 0 else p["cyan"]
        dot_svg = svg_circle(line_x, y, 6, theme_name, fill=dot_color)
        events_svg.append(
            f'{dot_svg}\n'
            f'  <text x="{line_x-15}" y="{y+5}" text-anchor="end" font-family="{f["display"]}" font-size="14" font-weight="700" fill="{tx["secondary"]}">{year}</text>\n'
            f'  <text x="{line_x+20}" y="{y+5}" font-family="{f["body"]}" font-size="16" font-weight="600" fill="{tx["primary"]}">{ev_title}</text>\n'
            f'  <text x="{line_x+20}" y="{y+22}" font-family="{f["body"]}" font-size="12" fill="{tx["secondary"]}">{ev_desc}</text>'
        )

    last_y = 140 + min(len(events), 5) * 90 - 90
    events_joined = "\n  ".join(events_svg)
    timeline_axis = svg_line(line_x, 100, line_x, last_y, theme_name, color=c["border"])
    svg = f'''{header}
  {decor_svg}
  <text x="{width/2}" y="60" text-anchor="middle" font-family="{f["display"]}" font-size="24" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {timeline_axis}
  {events_joined}
</svg>'''
    return svg


def render_svg_steps(title, steps, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:15] + ("..." if len(title) > 15 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    steps_svg = []
    for i, step in enumerate(steps[:5]):
        step_title = step.get("title", "")[:12]
        step_desc = step.get("desc", "")[:25]
        y = 130 + i * 90
        num_color = p["accent"] if i % 2 == 0 else p["cyan"]
        step_num_svg = svg_step_number(80, y, i + 1, theme_name, color=num_color)
        steps_svg.append(
            f'{step_num_svg}\n'
            f'  <text x="120" y="{y}" font-family="{f["body"]}" font-size="18" font-weight="600" fill="{tx["primary"]}">{step_title}</text>\n'
            f'  <text x="120" y="{y+22}" font-family="{f["body"]}" font-size="13" fill="{tx["secondary"]}">{step_desc}</text>'
        )

    steps_joined = "\n  ".join(steps_svg)
    svg = f'''{header}
  {decor_svg}
  <text x="{width/2}" y="60" text-anchor="middle" font-family="{f["display"]}" font-size="24" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {steps_joined}
</svg>'''
    return svg


def render_svg_qa(question, answer, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_q = question[:30] + ("..." if len(question) > 30 else "")
    display_a = answer[:50] + ("..." if len(answer) > 50 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    qa_card = svg_card(60, height * 0.15, width - 120, height * 0.30, theme_name, border=p["accent"])
    qa_divider = svg_line(width * 0.2, height * 0.52, width * 0.8, height * 0.52, theme_name, color=p["accent"], element="divider")
    svg = f'''{header}
  {decor_svg}
  {qa_card}
  <text x="{width*0.1}" y="{height*0.22}" font-family="{f["display"]}" font-size="40" fill="{p["accent"]}" opacity="0.3">?</text>
  <text x="{width/2}" y="{height*0.33}" text-anchor="middle" font-family="{f["display"]}" font-size="22" font-weight="700" fill="{tx["primary"]}">{display_q}</text>
  {qa_divider}
  <text x="{width/2}" y="{height*0.68}" text-anchor="middle" font-family="{f["body"]}" font-size="18" fill="{tx["primary"]}">{display_a}</text>
</svg>'''
    return svg


def render_svg_focus(keyword, explanation, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_keyword = keyword[:8] + ("..." if len(keyword) > 8 else "")
    display_exp = explanation[:40] + ("..." if len(explanation) > 40 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    outer_ring = svg_circle(width / 2, height * 0.38, 80, theme_name, stroke=p["accent"])
    inner_ring = svg_circle(width / 2, height * 0.38, 60, theme_name, stroke=p["accent"])
    svg = f'''{header}
  {decor_svg}
  {outer_ring}
  {inner_ring}
  <text x="{width/2}" y="{height*0.40}" text-anchor="middle" font-family="{f["display"]}" font-size="42" font-weight="800" fill="{p["accent"]}">{display_keyword}</text>
  <text x="{width/2}" y="{height*0.65}" text-anchor="middle" font-family="{f["body"]}" font-size="18" fill="{tx["primary"]}">{display_exp}</text>
</svg>'''
    return svg


def render_svg_chart(title, data, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:15] + ("..." if len(title) > 15 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    max_val = max((d.get("value", 0) for d in data), default=1) or 1
    bar_area_x = 160
    bar_area_w = width - 220
    bar_h = 30
    bars_svg = []
    for i, d in enumerate(data[:5]):
        label = d.get("label", "")[:10]
        value = d.get("value", 0)
        y = 130 + i * 70
        bar_w = (value / max_val) * bar_area_w
        bar_color = p["accent"] if i % 2 == 0 else p["cyan"]
        bars_svg.append(
            f'<text x="{bar_area_x-10}" y="{y+bar_h/2+5}" text-anchor="end" font-family="{f["body"]}" font-size="14" fill="{tx["primary"]}">{label}</text>\n'
            f'  <rect x="{bar_area_x}" y="{y}" width="{bar_w}" height="{bar_h}" rx="4" fill="{bar_color}" opacity="0.8"/>\n'
            f'  <text x="{bar_area_x+bar_w+10}" y="{y+bar_h/2+5}" font-family="{f["mono"]}" font-size="13" fill="{tx["secondary"]}">{value}</text>'
        )

    bars_joined = "\n  ".join(bars_svg)
    svg = f'''{header}
  {decor_svg}
  <text x="{width/2}" y="60" text-anchor="middle" font-family="{f["display"]}" font-size="24" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {bars_joined}
</svg>'''
    return svg


def render_svg_summary(title, items, theme_name="dark", width=800, height=600):
    t = get_theme(theme_name)
    p = t["palette"]
    tx = t["text"]
    c = t["card"]
    f = t["font"]

    display_title = title[:15] + ("..." if len(title) > 15 else "")

    decor_svg = render_svg_decor(theme_name, width, height)
    header = _svg_header(theme_name, width, height)

    items_svg = []
    for i, item in enumerate(items[:5]):
        txt = item[:25] + ("..." if len(item) > 25 else "")
        y = 140 + i * 70
        num_color = p["accent"] if i % 2 == 0 else p["gold"]
        step_svg = svg_step_number(75, y, i + 1, theme_name, color=num_color)
        items_svg.append(
            f'{step_svg}\n'
            f'  <text x="110" y="{y+5}" font-family="{f["body"]}" font-size="18" fill="{tx["primary"]}">{txt}</text>'
        )

    summary_items_joined = "\n  ".join(items_svg)
    summary_divider = svg_line(60, 85, width - 60, 85, theme_name, color=p["accent"], element="divider")
    svg = f'''{header}
  {decor_svg}
  <text x="{width/2}" y="60" text-anchor="middle" font-family="{f["display"]}" font-size="24" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {summary_divider}
  {summary_items_joined}
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
