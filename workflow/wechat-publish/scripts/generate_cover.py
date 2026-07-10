"""
生成公众号封面图（1240×770）
"""
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DEFAULT_WIDTH = 1240
DEFAULT_HEIGHT = 770


def create_cover(
    title: str,
    output_path: str,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    bg_color: tuple = (245, 242, 235),
    accent_color: tuple = (60, 55, 50),
    sub_color: tuple = (120, 115, 110),
):
    """创建纯文字风格封面图，避免抽象概念图在公众号不显示。"""
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # 字体 fallback：依次尝试常见中文字体，最后使用默认字体
    font_candidates = [
        "simhei.ttf",
        "simsun.ttc",
        "msyh.ttc",
        "msyhbd.ttc",
        "NotoSansCJK-Regular.ttc",
        "SourceHanSansCN-Regular.otf",
    ]

    def load_font(size):
        for name in font_candidates:
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()

    font_title = load_font(72)
    font_sub = load_font(36)

    # 标题居中
    bbox = draw.textbbox((0, 0), title, font=font_title)
    text_w = bbox[2] - bbox[0]
    x = (width - text_w) // 2
    y = height // 2 - 80
    draw.text((x, y), title, fill=accent_color, font=font_title)

    # 副标题
    sub = "为什么我们反感被说教"
    bbox_sub = draw.textbbox((0, 0), sub, font=font_sub)
    text_w_sub = bbox_sub[2] - bbox_sub[0]
    x_sub = (width - text_w_sub) // 2
    y_sub = y + 110
    draw.text((x_sub, y_sub), sub, fill=sub_color, font=font_sub)

    # 装饰线
    line_y = y_sub + 80
    draw.line([(width // 2 - 120, line_y), (width // 2 + 120, line_y)], fill=accent_color, width=3)

    img.save(output_path, "JPEG", quality=95)
    return Path(output_path)


if __name__ == "__main__":
    output_dir = Path(__file__).resolve().parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    create_cover(
        title="当\"正确\"成为武器",
        output_path=str(output_dir / "cover_final.jpg"),
    )
