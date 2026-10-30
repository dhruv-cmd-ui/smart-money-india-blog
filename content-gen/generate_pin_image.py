"""Generates a branded Pinterest pin image per article, saved into docs/pins/<slug>.png so it's
publicly hosted at a stable GitHub Pages URL (docs/pin-image.png stays as the generic fallback).

Usage: python generate_pin_image.py            # backfill pins for every article in the manifest
       python generate_pin_image.py <slug>     # one article
"""
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DOCS = Path(__file__).resolve().parent.parent / "docs"
PINS_DIR = DOCS / "pins"
FONTS = Path(__file__).resolve().parent / "fonts"
SIZE = (1000, 1500)  # Pinterest's recommended 2:3 aspect ratio
MARGIN = 70

# (gradient top, gradient bottom, accent highlight) — one palette per article, picked by slug hash.
PALETTES = [
    ("#0F2027", "#2C7A7B", "#FFD93D"),
    ("#1A2980", "#26D0CE", "#FFEB3B"),
    ("#42275A", "#734B6D", "#FFC857"),
    ("#134E5E", "#71B280", "#FFE66D"),
    ("#232526", "#B8860B", "#FFFFFF"),
    ("#0B486B", "#F56217", "#FFF3B0"),
]


def _font(weight, size):
    return ImageFont.truetype(str(FONTS / f"Poppins-{weight}.ttf"), size)


def _dejavu(size):
    """DejaVu Sans Bold (bundled) has the rupee sign, which Poppins lacks."""
    return ImageFont.truetype(str(FONTS / "DejaVuSans-Bold.ttf"), size)


def _hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _gradient(size, top, bottom):
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    a, b = _hx(top), _hx(bottom)
    for y in range(size[1]):
        t = y / size[1]
        draw.line([(0, y), (size[0], y)], fill=tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)))
    return img


def _text_width(draw, text, font):
    return draw.textlength(text, font=font)


def _wrap(draw, text, font, max_width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if _text_width(draw, trial, font) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def make_pin(slug: str, title: str, description: str) -> Path:
    top, bottom, accent = PALETTES[int(hashlib.md5(slug.encode()).hexdigest(), 16) % len(PALETTES)]
    base = _gradient(SIZE, top, bottom).convert("RGBA")

    # Decorative translucent circles + a big rupee watermark for depth.
    overlay = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse([-250, -250, 450, 450], fill=(255, 255, 255, 22))
    od.ellipse([650, 900, 1250, 1500], fill=(255, 255, 255, 20))
    od.ellipse([720, 120, 960, 360], outline=(255, 255, 255, 60), width=6)
    od.text((SIZE[0] - 400, 960), "₹", font=_dejavu(560), fill=(255, 255, 255, 30))
    img = Image.alpha_composite(base, overlay)
    draw = ImageDraw.Draw(img)
    width = SIZE[0] - 2 * MARGIN

    # Brand pill.
    pill_font = _font("Bold", 30)
    label = "SMART MONEY INDIA"
    pw = _text_width(draw, label, pill_font)
    draw.rounded_rectangle([MARGIN, MARGIN, MARGIN + pw + 60, MARGIN + 74], radius=37, fill=accent)
    draw.text((MARGIN + 30, MARGIN + 17), label, font=pill_font, fill="#111111")

    # Title: biggest font that fits in at most 6 lines; first line highlighted in the accent colour.
    for size in (96, 88, 80, 72, 64, 58):
        title_font = _font("ExtraBold", size)
        lines = _wrap(draw, title, title_font, width)
        if len(lines) <= 6:
            break
    line_h = int(size * 1.22)
    y = 330
    for i, line in enumerate(lines):
        draw.text((MARGIN + 3, y + 4), line, font=title_font, fill=(0, 0, 0, 90))  # soft shadow
        draw.text((MARGIN, y), line, font=title_font, fill=accent if i == 0 else "#FFFFFF")
        y += line_h

    # Accent bar + description.
    y += 25
    draw.rounded_rectangle([MARGIN, y, MARGIN + 140, y + 12], radius=6, fill=accent)
    y += 50
    chip_font = _font("Bold", 36)
    for label in ("India-specific numbers", "Simple examples", "5-minute read"):
        cw = _text_width(draw, label, chip_font)
        draw.rounded_rectangle([MARGIN, y, MARGIN + cw + 110, y + 78], radius=39, fill=(255, 255, 255, 235))
        cx, cy = MARGIN + 44, y + 39  # drawn check mark (no font glyph needed)
        draw.line([(cx - 14, cy), (cx - 4, cy + 11), (cx + 16, cy - 12)], fill="#1E8E3E", width=7, joint="curve")
        draw.text((MARGIN + 80, y + 14), label, font=chip_font, fill="#111111")
        y += 100

    # CTA button + footer.
    btn_y = SIZE[1] - 270
    draw.rounded_rectangle([MARGIN, btn_y, SIZE[0] - MARGIN, btn_y + 120], radius=60, fill=accent)
    cta_font = _font("ExtraBold", 44)
    cta = "READ THE FULL GUIDE"
    tw = _text_width(draw, cta, cta_font)
    tx = (SIZE[0] - tw - 70) / 2
    draw.text((tx, btn_y + 30), cta, font=cta_font, fill="#111111")
    ax, ay = tx + tw + 30, btn_y + 60  # drawn arrow
    draw.line([(ax, ay), (ax + 40, ay)], fill="#111111", width=8)
    draw.polygon([(ax + 28, ay - 18), (ax + 52, ay), (ax + 28, ay + 18)], fill="#111111")
    foot_font = _font("Medium", 30)
    foot = "Free guide on Smart Money India"
    draw.text(((SIZE[0] - _text_width(draw, foot, foot_font)) / 2, btn_y + 150), foot, font=foot_font, fill="#FFFFFF")

    PINS_DIR.mkdir(parents=True, exist_ok=True)
    out = PINS_DIR / f"{slug}.png"
    img.convert("RGB").save(out, format="PNG", optimize=True)
    return out


def main():
    manifest = json.loads((DOCS / "manifest.json").read_text(encoding="utf-8"))
    wanted = sys.argv[1:] or [e["slug"] for e in manifest]
    for e in manifest:
        if e["slug"] in wanted:
            print("Saved:", make_pin(e["slug"], e["title"], e["description"]))


if __name__ == "__main__":
    main()
