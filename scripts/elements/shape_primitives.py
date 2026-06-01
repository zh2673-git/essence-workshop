"""
本质工坊 · 形状原语模板体系
定义形状、线条、轮廓、图标的视觉风格契约

设计原则：
  - 形状原语是"视觉元素长什么样"的声明，与"怎么画"分离
  - 每个主题有自己的形状风格：圆角大小、线条粗细、虚线模式、图标集
  - SVG 和 Canvas 共享同一套形状参数定义
  - 新增主题只需声明形状参数，无需重写渲染逻辑

三层结构：
  shapes    : 形状参数（圆角、线宽、虚线模式、箭头样式）
  icons     : 图标路径定义（13种图标 × 每种主题可自定义）
  contours  : 轮廓/边框样式（实线/虚线/点线/双线）
"""

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SHAPE_STYLES = {
    "dark": {
        "card": {
            "radius": 32,
            "border_width": 2,
            "border_style": "solid",
            "shadow_blur": 60,
            "shadow_opacity": 0.1,
        },
        "circle": {
            "stroke_width": 2,
            "default_radius": 4,
        },
        "ring": {
            "width": 6,
            "line_cap": "round",
            "bg_opacity": 0.05,
        },
        "line": {
            "width": 2,
            "dash_pattern": [],
            "dash_offset": 0,
            "line_cap": "round",
        },
        "connector": {
            "width": 3,
            "dash_pattern": [12, 8],
            "arrow_size": 12,
            "arrow_style": "filled",
        },
        "divider": {
            "width": 2,
            "dash_pattern": [],
            "opacity": 0.3,
        },
        "progress": {
            "height": 4,
            "bg_opacity": 0.06,
            "gradient": True,
        },
        "step_number": {
            "radius": 20,
            "border_width": 2,
            "font_size": 16,
            "font_weight": 700,
        },
        "bullet": {
            "radius": 4,
            "style": "filled",
        },
        "badge": {
            "radius": 6,
            "padding_x": 8,
            "padding_y": 4,
            "font_size": 14,
        },
    },
    "warm": {
        "card": {
            "radius": 24,
            "border_width": 1.5,
            "border_style": "solid",
            "shadow_blur": 40,
            "shadow_opacity": 0.08,
        },
        "circle": {
            "stroke_width": 2,
            "default_radius": 4,
        },
        "ring": {
            "width": 5,
            "line_cap": "round",
            "bg_opacity": 0.05,
        },
        "line": {
            "width": 1.5,
            "dash_pattern": [],
            "dash_offset": 0,
            "line_cap": "round",
        },
        "connector": {
            "width": 2,
            "dash_pattern": [8, 6],
            "arrow_size": 10,
            "arrow_style": "open",
        },
        "divider": {
            "width": 1.5,
            "dash_pattern": [],
            "opacity": 0.2,
        },
        "progress": {
            "height": 3,
            "bg_opacity": 0.08,
            "gradient": True,
        },
        "step_number": {
            "radius": 18,
            "border_width": 2,
            "font_size": 14,
            "font_weight": 700,
        },
        "bullet": {
            "radius": 3,
            "style": "filled",
        },
        "badge": {
            "radius": 8,
            "padding_x": 10,
            "padding_y": 5,
            "font_size": 13,
        },
    },
    "minimal": {
        "card": {
            "radius": 16,
            "border_width": 1,
            "border_style": "solid",
            "shadow_blur": 0,
            "shadow_opacity": 0,
        },
        "circle": {
            "stroke_width": 1.5,
            "default_radius": 3,
        },
        "ring": {
            "width": 4,
            "line_cap": "butt",
            "bg_opacity": 0.04,
        },
        "line": {
            "width": 1,
            "dash_pattern": [],
            "dash_offset": 0,
            "line_cap": "butt",
        },
        "connector": {
            "width": 1.5,
            "dash_pattern": [6, 4],
            "arrow_size": 8,
            "arrow_style": "open",
        },
        "divider": {
            "width": 1,
            "dash_pattern": [],
            "opacity": 0.15,
        },
        "progress": {
            "height": 2,
            "bg_opacity": 0.06,
            "gradient": False,
        },
        "step_number": {
            "radius": 14,
            "border_width": 1.5,
            "font_size": 13,
            "font_weight": 600,
        },
        "bullet": {
            "radius": 2,
            "style": "filled",
        },
        "badge": {
            "radius": 4,
            "padding_x": 6,
            "padding_y": 3,
            "font_size": 12,
        },
    },
    "nature": {
        "card": {
            "radius": 28,
            "border_width": 1.5,
            "border_style": "solid",
            "shadow_blur": 50,
            "shadow_opacity": 0.06,
        },
        "circle": {
            "stroke_width": 2,
            "default_radius": 4,
        },
        "ring": {
            "width": 5,
            "line_cap": "round",
            "bg_opacity": 0.04,
        },
        "line": {
            "width": 1.5,
            "dash_pattern": [],
            "dash_offset": 0,
            "line_cap": "round",
        },
        "connector": {
            "width": 2,
            "dash_pattern": [10, 6],
            "arrow_size": 10,
            "arrow_style": "filled",
        },
        "divider": {
            "width": 1.5,
            "dash_pattern": [4, 4],
            "opacity": 0.15,
        },
        "progress": {
            "height": 3,
            "bg_opacity": 0.05,
            "gradient": True,
        },
        "step_number": {
            "radius": 18,
            "border_width": 2,
            "font_size": 14,
            "font_weight": 700,
        },
        "bullet": {
            "radius": 3,
            "style": "filled",
        },
        "badge": {
            "radius": 6,
            "padding_x": 8,
            "padding_y": 4,
            "font_size": 13,
        },
    },
    "ink": {
        "card": {
            "radius": 20,
            "border_width": 1,
            "border_style": "dashed",
            "shadow_blur": 0,
            "shadow_opacity": 0,
        },
        "circle": {
            "stroke_width": 1.5,
            "default_radius": 3,
        },
        "ring": {
            "width": 3,
            "line_cap": "round",
            "bg_opacity": 0.03,
        },
        "line": {
            "width": 1.5,
            "dash_pattern": [8, 4],
            "dash_offset": 0,
            "line_cap": "round",
        },
        "connector": {
            "width": 1.5,
            "dash_pattern": [6, 4],
            "arrow_size": 8,
            "arrow_style": "open",
        },
        "divider": {
            "width": 1,
            "dash_pattern": [12, 6],
            "opacity": 0.2,
        },
        "progress": {
            "height": 2,
            "bg_opacity": 0.05,
            "gradient": False,
        },
        "step_number": {
            "radius": 16,
            "border_width": 1.5,
            "font_size": 14,
            "font_weight": 700,
        },
        "bullet": {
            "radius": 2,
            "style": "outline",
        },
        "badge": {
            "radius": 2,
            "padding_x": 6,
            "padding_y": 3,
            "font_size": 12,
        },
    },
    "cyber": {
        "card": {
            "radius": 24,
            "border_width": 1.5,
            "border_style": "solid",
            "shadow_blur": 80,
            "shadow_opacity": 0.12,
        },
        "circle": {
            "stroke_width": 2,
            "default_radius": 4,
        },
        "ring": {
            "width": 6,
            "line_cap": "butt",
            "bg_opacity": 0.06,
        },
        "line": {
            "width": 1.5,
            "dash_pattern": [4, 4],
            "dash_offset": 0,
            "line_cap": "butt",
        },
        "connector": {
            "width": 2,
            "dash_pattern": [8, 4],
            "arrow_size": 10,
            "arrow_style": "filled",
        },
        "divider": {
            "width": 1.5,
            "dash_pattern": [4, 4],
            "opacity": 0.25,
        },
        "progress": {
            "height": 3,
            "bg_opacity": 0.08,
            "gradient": True,
        },
        "step_number": {
            "radius": 18,
            "border_width": 2,
            "font_size": 14,
            "font_weight": 700,
        },
        "bullet": {
            "radius": 3,
            "style": "filled",
        },
        "badge": {
            "radius": 4,
            "padding_x": 8,
            "padding_y": 4,
            "font_size": 13,
        },
    },
}

ICON_PATHS = {
    "brain": {
        "svg": (
            'M{x-0.15*s},{y-0.08*s} A{s*0.28},{s*0.28} 0 1,1 {x+0.15*s},{y-0.08*s} '
            'M{x-0.08*s},{y-0.36*s} Q{x},{y-0.18*s} {x+0.08*s},{y-0.36*s} '
            'M{x-0.22*s},{y+0.15*s} Q{x},{y+0.32*s} {x+0.22*s},{y+0.15*s}'
        ),
        "canvas": "arc;arc;curve;curve",
    },
    "lightbulb": {
        "svg": (
            'M{x},{y-0.4*s} A{s*0.3},{s*0.3} 0 1,1 {x},{y-0.4*s} '
            'L{x+0.12*s},{y+0.2*s} L{x-0.12*s},{y+0.2*s} Z '
            'M{x-0.1*s},{y+0.24*s} L{x+0.1*s},{y+0.24*s} '
            'M{x-0.08*s},{y+0.3*s} L{x+0.08*s},{y+0.3*s}'
        ),
        "canvas": "arc;line;line;line",
    },
    "target": {
        "svg": (
            'M{x-s*0.35},{y} A{s*0.35},{s*0.35} 0 1,1 {x+s*0.35},{y} A{s*0.35},{s*0.35} 0 1,1 {x-s*0.35},{y} '
            'M{x-s*0.2},{y} A{s*0.2},{s*0.2} 0 1,1 {x+s*0.2},{y} A{s*0.2},{s*0.2} 0 1,1 {x-s*0.2},{y} '
            'M{x-s*0.06},{y} A{s*0.06},{s*0.06} 0 1,1 {x+s*0.06},{y} A{s*0.06},{s*0.06} 0 1,1 {x-s*0.06},{y}'
        ),
        "canvas": "circle;circle;circle",
    },
    "layers": {
        "svg": (
            'M{x-s*0.28},{y-s*0.2*s} L{x},{y-s*0.3*s} L{x+s*0.28},{y-s*0.2*s} L{x},{y-s*0.1*s} Z '
            'M{x-s*0.28},{y-s*0.04*s} L{x},{y-0.14*s} L{x+s*0.28},{y-0.04*s} L{x},{y+0.06*s} Z '
            'M{x-s*0.28},{y+0.12*s} L{x},{y+0.02*s} L{x+s*0.28},{y+0.12*s} L{x},{y+0.22*s} Z'
        ),
        "canvas": "polygon;polygon;polygon",
    },
    "zap": {
        "svg": (
            'M{x+0.05*s},{y-0.32*s} L{x-0.12*s},{y+0.02*s} L{x+0.02*s},{y+0.02*s} '
            'L{x-0.05*s},{y+0.32*s} L{x+0.12*s},{y-0.02*s} L{x-0.02*s},{y-0.02*s} Z'
        ),
        "canvas": "polygon",
    },
    "check": {
        "svg": (
            'M{x-s*0.35},{y} A{s*0.35},{s*0.35} 0 1,1 {x+s*0.35},{y} A{s*0.35},{s*0.35} 0 1,1 {x-s*0.35},{y} '
            'M{x-0.15*s},{y} L{x-0.02*s},{y+0.15*s} L{x+0.18*s},{y-0.12*s}'
        ),
        "canvas": "circle;polyline",
    },
    "arrow": {
        "svg": (
            'M{x-0.2*s},{y} L{x+0.2*s},{y} '
            'M{x+0.06*s},{y-0.12*s} L{x+0.22*s},{y} L{x+0.06*s},{y+0.12*s}'
        ),
        "canvas": "line;polyline",
    },
    "diamond": {
        "svg": (
            'M{x},{y-0.3*s} L{x+0.2*s},{y} L{x},{y+0.3*s} L{x-0.2*s},{y} Z '
            'M{x},{y+0.06*s}'
        ),
        "canvas": "polygon;circle",
    },
    "hexagon": {
        "svg": (
            'M{x+s*0.26},{y-0.15*s} L{x+s*0.26},{y+0.15*s} '
            'L{x},{y+0.3*s} L{x-s*0.26},{y+0.15*s} L{x-s*0.26},{y-0.15*s} L{x},{y-0.3*s} Z'
        ),
        "canvas": "polygon",
    },
    "scale": {
        "svg": (
            'M{x-0.25*s},{y-0.1*s} L{x+0.25*s},{y-0.1*s} '
            'M{x},{y-0.1*s} L{x},{y+0.2*s} '
            'M{x-0.25*s},{y-0.1*s} A{s*0.1},{s*0.1} 0 0,1 {x-0.05*s},{y-0.1*s} '
            'M{x+0.05*s},{y-0.1*s} A{s*0.1},{s*0.1} 0 0,1 {x+0.25*s},{y-0.1*s} '
            'M{x-0.15*s},{y+0.2*s} L{x+0.15*s},{y+0.2*s}'
        ),
        "canvas": "line;line;arc;arc;line",
    },
    "flag": {
        "svg": (
            'M{x-0.15*s},{y-0.3*s} L{x-0.15*s},{y+0.3*s} '
            'M{x-0.15*s},{y-0.3*s} L{x+0.2*s},{y-0.2*s} L{x-0.15*s},{y-0.1*s}'
        ),
        "canvas": "line;polygon",
    },
    "plus": {
        "svg": (
            'M{x},{y-0.28*s} L{x},{y+0.28*s} '
            'M{x-0.28*s},{y} L{x+0.28*s},{y}'
        ),
        "canvas": "line;line",
    },
    "magnifier": {
        "svg": (
            'M{x-s*0.22},{y-s*0.02} A{s*0.22},{s*0.22} 0 1,1 {x+s*0.22},{y-s*0.02} A{s*0.22},{s*0.22} 0 1,1 {x-s*0.22},{y-s*0.02} '
            'M{x+0.16*s},{y+0.16*s} L{x+0.28*s},{y+0.28*s}'
        ),
        "canvas": "circle;line",
    },
}

ICON_SETS = {
    "dark": ["brain", "zap", "diamond", "hexagon", "layers", "target"],
    "warm": ["lightbulb", "layers", "check", "arrow", "target", "flag"],
    "minimal": ["plus", "arrow", "check", "diamond", "magnifier", "layers"],
    "nature": ["diamond", "lightbulb", "brain", "scale", "layers", "flag"],
    "ink": ["diamond", "lightbulb", "scale", "target", "layers", "plus"],
    "cyber": ["hexagon", "zap", "brain", "magnifier", "layers", "diamond"],
}

CONTOUR_STYLES = {
    "solid": {"dash_array": "", "dash_offset": 0},
    "dashed": {"dash_array": "8,4", "dash_offset": 0},
    "dotted": {"dash_array": "2,4", "dash_offset": 0},
    "dashdot": {"dash_array": "8,4,2,4", "dash_offset": 0},
    "longdash": {"dash_array": "12,6", "dash_offset": 0},
    "double": {"dash_array": "", "dash_offset": 0, "gap": 3},
}


def get_shape_style(theme_name, element="card"):
    from scripts.elements.svg_themes import VALID_THEME_NAMES
    if theme_name not in SHAPE_STYLES:
        theme_name = "dark"
    theme_shapes = SHAPE_STYLES[theme_name]
    return theme_shapes.get(element, {})


def get_icon_set(theme_name):
    return ICON_SETS.get(theme_name, ICON_SETS["dark"])


def get_scene_icon(theme_name, scene_type, index=0):
    icon_set = get_icon_set(theme_name)
    scene_icon_map = {
        "title": 0, "bullet": 1, "stat": 2, "quote": 3,
        "compare": 4, "steps": 5, "qa": 0, "timeline": 1,
        "focus": 2, "chart": 3, "summary": 4,
    }
    base = scene_icon_map.get(scene_type, 0)
    return icon_set[(base + index) % len(icon_set)]


def get_contour_svg(theme_name, element="card"):
    shapes = get_shape_style(theme_name, element)
    border_style = shapes.get("border_style", "solid")
    contour = CONTOUR_STYLES.get(border_style, CONTOUR_STYLES["solid"])
    return contour


def svg_card(x, y, w, h, theme_name="dark", fill=None, border=None, extra_attrs=""):
    from scripts.elements.svg_themes import get_theme
    t = get_theme(theme_name)
    c = t["card"]
    shapes = get_shape_style(theme_name, "card")
    radius = shapes.get("radius", 24)
    border_width = shapes.get("border_width", 1.5)
    contour = get_contour_svg(theme_name, "card")

    dash_attr = ""
    if contour.get("dash_array"):
        dash_attr = f' stroke-dasharray="{contour["dash_array"]}"'
    if contour.get("dash_offset"):
        dash_attr += f' stroke-dashoffset="{contour["dash_offset"]}"'

    fill_val = fill or c["fill"]
    border_val = border or c["border"]

    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
        f'fill="{fill_val}" stroke="{border_val}" stroke-width="{border_width}"{dash_attr}{extra_attrs}/>'
    )


def svg_circle(cx, cy, r, theme_name="dark", fill=None, stroke=None):
    from scripts.elements.svg_themes import get_theme
    t = get_theme(theme_name)
    shapes = get_shape_style(theme_name, "circle")
    stroke_width = shapes.get("stroke_width", 2)

    fill_val = fill or "none"
    stroke_val = stroke or t["palette"]["accent"]

    stroke_attr = f' stroke="{stroke_val}" stroke-width="{stroke_width}"' if stroke_val else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill_val}"{stroke_attr}/>'


def svg_ring(cx, cy, r, progress, theme_name="dark", color=None):
    from scripts.elements.svg_themes import get_theme
    t = get_theme(theme_name)
    shapes = get_shape_style(theme_name, "ring")
    width = shapes.get("width", 5)
    line_cap = shapes.get("line_cap", "round")
    bg_opacity = shapes.get("bg_opacity", 0.05)
    ring_color = color or t["palette"]["accent"]

    circumference = 2 * 3.14159 * r
    dash_len = circumference * progress
    gap_len = circumference * (1 - progress)

    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
        f'stroke="rgba(255,255,255,{bg_opacity})" stroke-width="{width}"/>\n'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
        f'stroke="{ring_color}" stroke-width="{width}" stroke-linecap="{line_cap}" '
        f'stroke-dasharray="{dash_len},{gap_len}" '
        f'transform="rotate(-90 {cx} {cy})"/>'
    )


def svg_line(x1, y1, x2, y2, theme_name="dark", color=None, element="line"):
    from scripts.elements.svg_themes import get_theme
    t = get_theme(theme_name)
    shapes = get_shape_style(theme_name, element)
    width = shapes.get("width", 2)
    dash_pattern = shapes.get("dash_pattern", [])
    line_cap = shapes.get("line_cap", "round")
    opacity = shapes.get("opacity", 1)
    line_color = color or t["palette"]["accent"]

    dash_attr = ""
    if dash_pattern:
        dash_attr = f' stroke-dasharray="{",".join(str(d) for d in dash_pattern)}"'

    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{line_color}" stroke-width="{width}" stroke-linecap="{line_cap}" '
        f'opacity="{opacity}"{dash_attr}/>'
    )


def svg_connector(x1, y1, x2, y2, theme_name="dark", color=None):
    from scripts.elements.svg_themes import get_theme
    t = get_theme(theme_name)
    shapes = get_shape_style(theme_name, "connector")
    width = shapes.get("width", 2)
    dash_pattern = shapes.get("dash_pattern", [12, 8])
    arrow_size = shapes.get("arrow_size", 10)
    arrow_style = shapes.get("arrow_style", "filled")
    line_color = color or t["palette"]["accent"]

    dash_attr = ""
    if dash_pattern:
        dash_attr = f' stroke-dasharray="{",".join(str(d) for d in dash_pattern)}"'

    line_svg = (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{line_color}" stroke-width="{width}"{dash_attr}/>'
    )

    dx = x2 - x1
    dy = y2 - y1
    length = max(1, (dx**2 + dy**2) ** 0.5)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux

    ax = x2 - ux * arrow_size
    ay = y2 - uy * arrow_size

    if arrow_style == "filled":
        arrow_svg = (
            f'<polygon points="{x2},{y2} {ax+px*arrow_size*0.4},{ay+py*arrow_size*0.4} '
            f'{ax-px*arrow_size*0.4},{ay-py*arrow_size*0.4}" fill="{line_color}"/>'
        )
    else:
        arrow_svg = (
            f'<polyline points="{ax+px*arrow_size*0.4},{ay+py*arrow_size*0.4} {x2},{y2} '
            f'{ax-px*arrow_size*0.4},{ay-py*arrow_size*0.4}" '
            f'fill="none" stroke="{line_color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'
        )

    return f"{line_svg}\n{arrow_svg}"


def svg_bullet(cx, cy, theme_name="dark", color=None):
    from scripts.elements.svg_themes import get_theme
    t = get_theme(theme_name)
    shapes = get_shape_style(theme_name, "bullet")
    radius = shapes.get("radius", 3)
    style = shapes.get("style", "filled")
    bullet_color = color or t["palette"]["accent"]

    if style == "outline":
        return f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{bullet_color}" stroke-width="1.5"/>'
    return f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{bullet_color}"/>'


def svg_step_number(cx, cy, num, theme_name="dark", color=None):
    from scripts.elements.svg_themes import get_theme
    t = get_theme(theme_name)
    shapes = get_shape_style(theme_name, "step_number")
    radius = shapes.get("radius", 18)
    border_width = shapes.get("border_width", 2)
    font_size = shapes.get("font_size", 14)
    font_weight = shapes.get("font_weight", 700)
    num_color = color or t["palette"]["accent"]

    return (
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{t["card"]["fill"]}" stroke="{num_color}" stroke-width="{border_width}"/>\n'
        f'<text x="{cx}" y="{cy + font_size * 0.35}" text-anchor="middle" '
        f'font-family="{t["font"]["display"]}" font-size="{font_size}" font-weight="{font_weight}" fill="{num_color}">{num}</text>'
    )


def svg_icon(icon_name, cx, cy, size, theme_name="dark", color=None):
    from scripts.elements.svg_themes import get_theme
    t = get_theme(theme_name)
    icon_color = color or t["palette"]["accent"]
    shapes = get_shape_style(theme_name, "line")
    stroke_width = shapes.get("width", 2)
    line_cap = shapes.get("line_cap", "round")

    icon_def = ICON_PATHS.get(icon_name)
    if not icon_def:
        return svg_circle(cx, cy, size * 0.3, theme_name, fill=icon_color)

    path_template = icon_def["svg"]
    path = path_template.replace("{x}", str(cx)).replace("{y}", str(cy)).replace("{s}", str(size))

    return (
        f'<g fill="none" stroke="{icon_color}" stroke-width="{stroke_width}" '
        f'stroke-linecap="{line_cap}" stroke-linejoin="round">\n'
        f'  <path d="{path}"/>\n'
        f'</g>'
    )


def shape_style_to_video_js(theme_name):
    shapes = SHAPE_STYLES.get(theme_name, SHAPE_STYLES["dark"])
    result = {}
    for element, params in shapes.items():
        result[element] = params
    result["iconSet"] = ICON_SETS.get(theme_name, ICON_SETS["dark"])
    return result
