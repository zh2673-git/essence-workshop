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
        "bg": {"bg1": "#0F0F23", "bg2": "#1A1A2E", "bg3": "#16213E"},
        "palette": {
            "accent": "#E94560",
            "accentGlow": "rgba(233,69,96,0.15)",
            "gold": "#F0C27F",
            "goldDim": "rgba(240,194,127,0.3)",
            "cyan": "#00D2FF",
            "cyanDim": "rgba(0,210,255,0.15)",
            "success": "#4ECDC4",
            "warn": "#FFE66D",
        },
        "text": {
            "primary": "#F0F0F0",
            "secondary": "#7A7A9E",
            "dim": "rgba(240,240,240,0.6)",
            "inverse": "#1A1A2E",
        },
        "card": {
            "fill": "rgba(255,255,255,0.04)",
            "border": "rgba(255,255,255,0.08)",
            "radius": 32,
            "shadow": "rgba(233,69,96,0.1)",
        },
        "decor": {
            "style": "circles",
            "opacity": 0.03,
            "elements": ["floating-circles", "grid", "accent-line"],
        },
        "atmosphere": {
            "glow": [
                {"cx": 0.5, "cy": 0.35, "r": 0.5, "color": "accent", "alpha": 0.08},
                {"cx": 0.8, "cy": 0.15, "r": 0.35, "color": "gold", "alpha": 0.05},
                {"cx": 0.2, "cy": 0.85, "r": 0.3, "color": "cyan", "alpha": 0.04},
            ],
            "gradient_dir": "vertical",
            "grain": 0.015,
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
        "bg": {"bg1": "#FDF6EC", "bg2": "#FAF0E1", "bg3": "#F5E6D0"},
        "palette": {
            "accent": "#D4763A",
            "accentGlow": "rgba(212,118,58,0.12)",
            "gold": "#8B5E3C",
            "goldDim": "rgba(139,94,60,0.25)",
            "cyan": "#5B8C5A",
            "cyanDim": "rgba(91,140,90,0.12)",
            "success": "#5B8C5A",
            "warn": "#D4763A",
        },
        "text": {
            "primary": "#3C2415",
            "secondary": "#8B7355",
            "dim": "rgba(60,36,21,0.6)",
            "inverse": "#FAF0E1",
        },
        "card": {
            "fill": "rgba(255,255,255,0.7)",
            "border": "rgba(139,94,60,0.12)",
            "radius": 24,
            "shadow": "rgba(212,118,58,0.08)",
        },
        "decor": {
            "style": "dots",
            "opacity": 0.06,
            "elements": ["dot-grid", "warm-gradient", "accent-corner"],
        },
        "atmosphere": {
            "glow": [
                {"cx": 0.3, "cy": 0.3, "r": 0.45, "color": "accent", "alpha": 0.06},
                {"cx": 0.7, "cy": 0.7, "r": 0.35, "color": "gold", "alpha": 0.04},
            ],
            "gradient_dir": "diagonal",
            "grain": 0.008,
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
        "bg": {"bg1": "#FFFFFF", "bg2": "#FAFAFA", "bg3": "#F5F5F5"},
        "palette": {
            "accent": "#333333",
            "accentGlow": "rgba(51,51,51,0.08)",
            "gold": "#666666",
            "goldDim": "rgba(102,102,102,0.2)",
            "cyan": "#888888",
            "cyanDim": "rgba(136,136,136,0.1)",
            "success": "#2D8C3C",
            "warn": "#CC8800",
        },
        "text": {
            "primary": "#111111",
            "secondary": "#999999",
            "dim": "rgba(17,17,17,0.6)",
            "inverse": "#FFFFFF",
        },
        "card": {
            "fill": "rgba(0,0,0,0.02)",
            "border": "rgba(0,0,0,0.06)",
            "radius": 16,
            "shadow": "rgba(0,0,0,0.04)",
        },
        "decor": {
            "style": "lines",
            "opacity": 0.04,
            "elements": ["thin-lines", "single-accent", "whitespace"],
        },
        "atmosphere": {
            "glow": [],
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
        "bg": {"bg1": "#0D1F0D", "bg2": "#142814", "bg3": "#1A331A"},
        "palette": {
            "accent": "#C9A84C",
            "accentGlow": "rgba(201,168,76,0.12)",
            "gold": "#8FAA6B",
            "goldDim": "rgba(143,170,107,0.25)",
            "cyan": "#6BA3A0",
            "cyanDim": "rgba(107,163,160,0.12)",
            "success": "#8FAA6B",
            "warn": "#C9A84C",
        },
        "text": {
            "primary": "#E8E4D8",
            "secondary": "#7A8B6A",
            "dim": "rgba(232,228,216,0.6)",
            "inverse": "#142814",
        },
        "card": {
            "fill": "rgba(255,255,255,0.04)",
            "border": "rgba(201,168,76,0.1)",
            "radius": 28,
            "shadow": "rgba(201,168,76,0.06)",
        },
        "decor": {
            "style": "organic",
            "opacity": 0.04,
            "elements": ["leaf-curves", "earth-tones", "golden-accent"],
        },
        "atmosphere": {
            "glow": [
                {"cx": 0.5, "cy": 0.4, "r": 0.5, "color": "gold", "alpha": 0.06},
                {"cx": 0.2, "cy": 0.8, "r": 0.3, "color": "accent", "alpha": 0.04},
            ],
            "gradient_dir": "vertical",
            "grain": 0.01,
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
        "bg": {"bg1": "#F5F0E8", "bg2": "#EDE6D8", "bg3": "#E0D5C3"},
        "palette": {
            "accent": "#2C2C2C",
            "accentGlow": "rgba(44,44,44,0.08)",
            "gold": "#8B4513",
            "goldDim": "rgba(139,69,19,0.2)",
            "cyan": "#5B7A7A",
            "cyanDim": "rgba(91,122,122,0.1)",
            "success": "#4A7C59",
            "warn": "#B8860B",
        },
        "text": {
            "primary": "#1A1A1A",
            "secondary": "#6B6B6B",
            "dim": "rgba(26,26,26,0.5)",
            "inverse": "#F5F0E8",
        },
        "card": {
            "fill": "rgba(255,255,255,0.5)",
            "border": "rgba(44,44,44,0.08)",
            "radius": 20,
            "shadow": "rgba(44,44,44,0.04)",
        },
        "decor": {
            "style": "brush",
            "opacity": 0.05,
            "elements": ["ink-wash", "seal-stamp", "bamboo-line"],
        },
        "atmosphere": {
            "glow": [
                {"cx": 0.5, "cy": 0.5, "r": 0.6, "color": "gold", "alpha": 0.03},
            ],
            "gradient_dir": "vertical",
            "grain": 0.012,
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
        "bg": {"bg1": "#0A0A1A", "bg2": "#111128", "bg3": "#0D0D2B"},
        "palette": {
            "accent": "#FF0080",
            "accentGlow": "rgba(255,0,128,0.15)",
            "gold": "#00FFCC",
            "goldDim": "rgba(0,255,204,0.25)",
            "cyan": "#7B61FF",
            "cyanDim": "rgba(123,97,255,0.15)",
            "success": "#00FFCC",
            "warn": "#FFD600",
        },
        "text": {
            "primary": "#E0E0FF",
            "secondary": "#6B6B9E",
            "dim": "rgba(224,224,255,0.5)",
            "inverse": "#0A0A1A",
        },
        "card": {
            "fill": "rgba(255,255,255,0.03)",
            "border": "rgba(255,0,128,0.12)",
            "radius": 24,
            "shadow": "rgba(255,0,128,0.08)",
        },
        "decor": {
            "style": "neon",
            "opacity": 0.04,
            "elements": ["neon-lines", "scan-line", "glitch-bar"],
        },
        "atmosphere": {
            "glow": [
                {"cx": 0.5, "cy": 0.3, "r": 0.45, "color": "accent", "alpha": 0.1},
                {"cx": 0.2, "cy": 0.7, "r": 0.3, "color": "cyan", "alpha": 0.06},
            ],
            "gradient_dir": "diagonal",
            "grain": 0.02,
        },
        "font": {
            "display": "'Orbitron','PingFang SC','Microsoft YaHei',sans-serif",
            "body": "'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif",
            "mono": "'JetBrains Mono','Fira Code',monospace",
        },
        "mood": ["赛博", "未来", "黑客", "元宇宙", "Web3", "区块链", "数字"],
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
    for i in range(5):
        cx = w * (0.15 + i * 0.18)
        cy = h * (0.3 + (i % 3) * 0.15)
        r = 40 + i * 25
        color = p["accent"] if i % 2 == 0 else p["cyan"]
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="1" opacity="{t["decor"]["opacity"]}"/>')
    return "\n    ".join(parts)


def _svg_decor_dots(t, w, h):
    parts = []
    p = t["palette"]
    spacing = 40
    for x in range(spacing, int(w), spacing):
        for y in range(spacing, int(h), spacing):
            if (x + y) % (spacing * 3) == 0:
                parts.append(f'<circle cx="{x}" cy="{y}" r="1.5" fill="{p["accent"]}" opacity="{t["decor"]["opacity"]}"/>')
    return "\n    ".join(parts[:30])


def _svg_decor_lines(t, w, h):
    parts = []
    p = t["palette"]
    for i in range(3):
        y = h * (0.25 + i * 0.25)
        parts.append(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="{p["accent"]}" stroke-width="0.5" opacity="{t["decor"]["opacity"]}"/>')
    return "\n    ".join(parts)


def _svg_decor_organic(t, w, h):
    parts = []
    p = t["palette"]
    for i in range(3):
        cy = h * (0.2 + i * 0.3)
        parts.append(
            f'<path d="M0,{cy} Q{w*0.25},{cy-30} {w*0.5},{cy} T{w},{cy}" '
            f'fill="none" stroke="{p["gold"]}" stroke-width="1" opacity="{t["decor"]["opacity"]}"/>'
        )
    return "\n    ".join(parts)


def _svg_decor_brush(t, w, h):
    parts = []
    p = t["palette"]
    parts.append(
        f'<path d="M{w*0.1},{h*0.85} Q{w*0.3},{h*0.82} {w*0.5},{h*0.85} T{w*0.9},{h*0.83}" '
        f'fill="none" stroke="{p["accent"]}" stroke-width="2" opacity="{t["decor"]["opacity"]*2}"/>'
    )
    stamp_x, stamp_y = w * 0.85, h * 0.12
    parts.append(
        f'<rect x="{stamp_x-15}" y="{stamp_y-15}" width="30" height="30" fill="{p["accent"]}" opacity="{t["decor"]["opacity"]*3}" rx="2"/>'
    )
    return "\n    ".join(parts)


def _svg_decor_neon(t, w, h):
    parts = []
    p = t["palette"]
    for i in range(4):
        y = h * (0.15 + i * 0.22)
        parts.append(
            f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="{p["accent"]}" stroke-width="0.5" opacity="{t["decor"]["opacity"]}"/>'
        )
    parts.append(
        f'<rect x="{w*0.02}" y="{h*0.02}" width="{w*0.96}" height="{h*0.96}" fill="none" '
        f'stroke="{p["accent"]}" stroke-width="1" opacity="{t["decor"]["opacity"]*0.5}" rx="4"/>'
    )
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


def _svg_header(theme_name, width, height):
    atm_defs = render_svg_atmosphere_defs(theme_name, width, height)
    atm_body = render_svg_atmosphere_body(theme_name, width, height)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">\n'
        f'  <defs>\n'
        f'    {atm_defs}\n'
        f'  </defs>\n'
        f'  <rect width="{width}" height="{height}" fill="url(#bg-grad)"/>\n'
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

    accent_line_y_top = 18
    accent_line_y_bot = height - 18
    accent_line_w = width - 60

    svg = f'''{header}
  <rect x="30" y="{accent_line_y_top}" width="{accent_line_w}" height="2" fill="{p["accent"]}" opacity="0.3"/>
  <rect x="30" y="{accent_line_y_bot}" width="{accent_line_w}" height="2" fill="{p["accent"]}" opacity="0.3"/>
  {decor_svg}
  <line x1="{width/2}" y1="{height*0.35}" x2="{width/2}" y2="{height*0.35+3}" stroke="{p["accent"]}" stroke-width="3" stroke-linecap="round"/>
  <text x="{width/2}" y="{height*0.30}" text-anchor="middle" font-family="{f["display"]}" font-size="34" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  <text x="{width/2}" y="{height*0.45}" text-anchor="middle" font-family="{f["body"]}" font-size="13" fill="{tx["secondary"]}">{display_author}</text>
  <text x="{width/2}" y="{height*0.90}" text-anchor="middle" font-family="{f["body"]}" font-size="11" fill="{tx["secondary"]}" opacity="0.6">{display_sub}</text>
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
    svg = f'''{header}
  {decor_svg}
  {card_shape}
  <text x="{width/2}" y="{card_y+55}" text-anchor="middle" font-family="{f["display"]}" font-size="26" font-weight="700" fill="{tx["primary"]}">{display_title}</text>
  {divider}
  {items_joined}
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
