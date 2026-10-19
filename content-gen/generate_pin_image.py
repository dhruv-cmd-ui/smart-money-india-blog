"""Generates a single reusable branded Pinterest pin image, saved into docs/ so it's
publicly hosted at a stable GitHub Pages URL."""
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "pin-image.png"
SIZE = (1000, 1500)  # Pinterest's recommended 2:3 aspect ratio
MARGIN = 80


def _font(size, bold=False):
    import matplotlib
    base = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(str(base / name), size)


def _lerp(c1, c2, t):
    def hx(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    a, b = hx(c1), hx(c2)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def main():
    img = Image.new("RGB", SIZE, color="#1A2980")
    draw = ImageDraw.Draw(img)
    for y in range(SIZE[1]):
        draw.line([(0, y), (SIZE[0], y)], fill=_lerp("#1A2980", "#26D0CE", y / SIZE[1]))

    label_font = _font(36, bold=True)
    draw.text((MARGIN, MARGIN), "PERSONAL FINANCE GUIDE", font=label_font, fill="#FFFFFF")
    draw.line([(MARGIN, MARGIN + 60), (SIZE[0] - MARGIN, MARGIN + 60)], fill="#FFFFFF", width=3)

    title_font = _font(70, bold=True)
    for i, line in enumerate(textwrap.wrap("Practical Money Tips for India", width=14)):
        draw.text((MARGIN, 500 + i * 85), line, font=title_font, fill="#FFFFFF")

    sub_font = _font(38)
    draw.text((MARGIN, SIZE[1] - 220), "Read the full guide on", font=sub_font, fill="#F2F2F2")
    draw.text((MARGIN, SIZE[1] - 170), "Smart Money India", font=_font(44, bold=True), fill="#FFEB3B")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT_PATH, format="PNG")
    print("Saved:", OUT_PATH)


if __name__ == "__main__":
    main()
