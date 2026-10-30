"""Flat-style icons drawn with Pillow (no external assets), used to decorate the text-only pins.

Every icon takes (draw, cx, cy, r): a Draw object on a supersampled layer, centre and 'radius'
(half the icon's footprint). Colours are fixed so the set looks consistent.
"""
import math
from pathlib import Path

from PIL import ImageDraw, ImageFont

FONTS = Path(__file__).resolve().parent / "fonts"

GOLD, GOLD_D = "#FFC93C", "#E09F1F"
BLUE, BLUE_D = "#3B82F6", "#1D4ED8"
GREEN, GREEN_D = "#34C759", "#1E8E3E"
RED, RED_D = "#FF5A5F", "#C2383D"
PINK, PINK_D = "#FF9EB5", "#E8728F"
WHITE, INK = "#FFFFFF", "#1F2937"
SKIN, SKIN_D = "#F2B58A", "#D9946A"


def _rupee(d, cx, cy, size, fill):
    f = ImageFont.truetype(str(FONTS / "DejaVuSans-Bold.ttf"), int(size))
    d.text((cx, cy), "₹", font=f, fill=fill, anchor="mm")


def coin(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD_D)
    d.ellipse([cx - r * .88, cy - r * .88, cx + r * .88, cy + r * .88], fill=GOLD)
    d.ellipse([cx - r * .66, cy - r * .66, cx + r * .66, cy + r * .66], outline=GOLD_D, width=max(2, int(r * .06)))
    _rupee(d, cx, cy + r * .04, r * 1.05, GOLD_D)


def shield(d, cx, cy, r):
    pts = [(cx - r * .8, cy - r * .85), (cx + r * .8, cy - r * .85), (cx + r * .8, cy + r * .05),
           (cx, cy + r), (cx - r * .8, cy + r * .05)]
    d.polygon(pts, fill=BLUE_D)
    inner = [(cx - r * .62, cy - r * .68), (cx + r * .62, cy - r * .68), (cx + r * .62, cy + r * .02),
             (cx, cy + r * .78), (cx - r * .62, cy + r * .02)]
    d.polygon(inner, fill=BLUE)
    d.line([(cx - r * .32, cy - r * .02), (cx - r * .06, cy + r * .26), (cx + r * .36, cy - r * .3)],
           fill=WHITE, width=max(4, int(r * .17)), joint="curve")


def chart(d, cx, cy, r):
    d.rounded_rectangle([cx - r, cy - r, cx + r, cy + r], radius=r * .2, fill=WHITE)
    bw = r * .34
    for i, (h, col) in enumerate([(.5, GREEN), (.95, GREEN), (1.4, GREEN_D)]):
        x = cx - r * .72 + i * (bw + r * .12)
        d.rounded_rectangle([x, cy + r * .72 - h * r * .9, x + bw, cy + r * .72], radius=r * .06, fill=col)
    d.line([(cx - r * .7, cy - r * .1), (cx - r * .15, cy - r * .35), (cx + r * .15, cy - r * .2), (cx + r * .7, cy - r * .62)],
           fill=RED, width=max(4, int(r * .09)), joint="curve")
    d.polygon([(cx + r * .78, cy - r * .7), (cx + r * .45, cy - r * .66), (cx + r * .7, cy - r * .4)], fill=RED)


def calendar(d, cx, cy, r):
    d.rounded_rectangle([cx - r, cy - r * .85, cx + r, cy + r], radius=r * .16, fill=WHITE)
    d.rounded_rectangle([cx - r, cy - r * .85, cx + r, cy - r * .3], radius=r * .16, fill=RED)
    d.rectangle([cx - r, cy - r * .5, cx + r, cy - r * .3], fill=RED)
    for x in (-.5, .5):
        d.rounded_rectangle([cx + x * r - r * .07, cy - r * 1.05, cx + x * r + r * .07, cy - r * .65], radius=r * .05, fill=INK)
    for row in range(3):
        for col in range(4):
            x, y = cx - r * .66 + col * r * .44, cy - r * .08 + row * r * .34
            d.ellipse([x - r * .09, y - r * .09, x + r * .09, y + r * .09], fill=GREEN if (row + col) % 4 == 0 else "#CBD5E1")


def house(d, cx, cy, r):
    d.polygon([(cx - r * 1.05, cy - r * .1), (cx, cy - r * .95), (cx + r * 1.05, cy - r * .1)], fill=RED)
    d.rectangle([cx - r * .8, cy - r * .1, cx + r * .8, cy + r * .85], fill="#FDE68A")
    d.rounded_rectangle([cx - r * .2, cy + r * .25, cx + r * .2, cy + r * .85], radius=r * .06, fill=BLUE_D)
    d.rectangle([cx - r * .62, cy + r * .02, cx - r * .3, cy + r * .32], fill="#93C5FD")
    d.rectangle([cx + r * .3, cy + r * .02, cx + r * .62, cy + r * .32], fill="#93C5FD")


def piggy(d, cx, cy, r):
    d.polygon([(cx + r * .12, cy - r * .5), (cx + r * .34, cy - r * .98), (cx + r * .58, cy - r * .38)], fill=PINK_D)
    for x in (-.5, .45):
        d.rounded_rectangle([cx + x * r - r * .12, cy + r * .4, cx + x * r + r * .12, cy + r * .85], radius=r * .06, fill=PINK_D)
    d.ellipse([cx - r, cy - r * .62, cx + r * .88, cy + r * .62], fill=PINK)
    d.ellipse([cx + r * .55, cy - r * .22, cx + r * 1.1, cy + r * .28], fill=PINK_D)
    for x in (.76, .9):
        d.ellipse([cx + r * x - r * .045, cy + r * .02 - r * .06, cx + r * x + r * .045, cy + r * .02 + r * .06], fill=INK)
    d.ellipse([cx + r * .38 - r * .07, cy - r * .22 - r * .07, cx + r * .38 + r * .07, cy - r * .22 + r * .07], fill=INK)
    d.rounded_rectangle([cx - r * .35, cy - r * .5, cx + r * .1, cy - r * .4], radius=r * .05, fill=PINK_D)
    d.ellipse([cx - r * .27, cy - r * 1.1, cx + r * .03, cy - r * .8], fill=GOLD)


def heart(d, cx, cy, r):
    d.ellipse([cx - r, cy - r * .85, cx, cy + r * .15], fill=RED)
    d.ellipse([cx, cy - r * .85, cx + r, cy + r * .15], fill=RED)
    d.polygon([(cx - r * .97, cy - r * .12), (cx + r * .97, cy - r * .12), (cx, cy + r * .95)], fill=RED)
    d.ellipse([cx - r * .62, cy - r * .62, cx - r * .32, cy - r * .32], fill="#FFB4B7")


def umbrella(d, cx, cy, r):
    d.line([(cx, cy - r * .2), (cx, cy + r * .85)], fill=INK, width=max(4, int(r * .08)))
    d.arc([cx - r * .3, cy + r * .6, cx + r * .02, cy + r * 1.0], 0, 180, fill=INK, width=max(4, int(r * .08)))
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=GOLD)
    for i in range(1, 4):
        a = math.radians(180 + i * 45)
        d.line([(cx, cy), (cx + math.cos(a) * r, cy + math.sin(a) * r)], fill=GOLD_D, width=max(2, int(r * .04)))


def lock(d, cx, cy, r):
    d.arc([cx - r * .5, cy - r * 1.0, cx + r * .5, cy], 180, 360, fill=INK, width=max(5, int(r * .16)))
    d.line([(cx - r * .5, cy - r * .5), (cx - r * .5, cy - r * .1)], fill=INK, width=max(5, int(r * .16)))
    d.line([(cx + r * .5, cy - r * .5), (cx + r * .5, cy - r * .1)], fill=INK, width=max(5, int(r * .16)))
    d.rounded_rectangle([cx - r * .85, cy - r * .1, cx + r * .85, cy + r * .9], radius=r * .16, fill=GOLD)
    d.ellipse([cx - r * .12, cy + r * .2, cx + r * .12, cy + r * .44], fill=INK)
    d.rectangle([cx - r * .05, cy + r * .36, cx + r * .05, cy + r * .66], fill=INK)


def gauge(d, cx, cy, r):
    box = [cx - r, cy - r, cx + r, cy + r]
    for i, col in enumerate([RED, "#FF9F43", GOLD, "#A3D977", GREEN]):
        d.pieslice(box, 180 + i * 36, 216 + i * 36, fill=col)
    d.pieslice([cx - r * .55, cy - r * .55, cx + r * .55, cy + r * .55], 180, 360, fill=WHITE)
    a = math.radians(325)
    d.line([(cx, cy), (cx + math.cos(a) * r * .85, cy + math.sin(a) * r * .85)], fill=INK, width=max(5, int(r * .1)))
    d.ellipse([cx - r * .12, cy - r * .12, cx + r * .12, cy + r * .12], fill=INK)


def goldbar(d, cx, cy, r):
    def bar(x, y, s):
        d.polygon([(x - s, y + s * .4), (x + s, y + s * .4), (x + s * .75, y - s * .35), (x - s * .75, y - s * .35)], fill=GOLD)
        d.polygon([(x - s * .75, y - s * .35), (x + s * .75, y - s * .35), (x + s * .55, y - s * .55), (x - s * .55, y - s * .55)], fill="#FFE08A")
    bar(cx - r * .5, cy + r * .45, r * .62)
    bar(cx + r * .5, cy + r * .45, r * .62)
    bar(cx, cy - r * .1, r * .62)


def plant(d, cx, cy, r):
    d.polygon([(cx - r * .55, cy + r * .1), (cx + r * .55, cy + r * .1), (cx + r * .38, cy + r * .95), (cx - r * .38, cy + r * .95)], fill="#C2703D")
    d.line([(cx, cy + r * .1), (cx, cy - r * .55)], fill=GREEN_D, width=max(4, int(r * .1)))
    d.ellipse([cx - r * .85, cy - r * .85, cx - r * .02, cy - r * .2], fill=GREEN)
    d.ellipse([cx + r * .02, cy - r * 1.0, cx + r * .85, cy - r * .35], fill=GREEN_D)


def person(d, cx, cy, r, shirt=BLUE, hair=INK):
    d.rounded_rectangle([cx - r * .75, cy + r * .1, cx + r * .75, cy + r * 1.3], radius=r * .35, fill=shirt)
    d.rectangle([cx - r * .12, cy - r * .05, cx + r * .12, cy + r * .2], fill=SKIN_D)
    d.ellipse([cx - r * .55, cy - r * .95, cx + r * .55, cy + r * .15], fill=SKIN)
    d.pieslice([cx - r * .6, cy - r * 1.02, cx + r * .6, cy + r * .1], 180, 360, fill=hair)
    for x in (-.2, .2):
        d.ellipse([cx + r * x - r * .05, cy - r * .42, cx + r * x + r * .05, cy - r * .32], fill=INK)
    d.arc([cx - r * .25, cy - r * .35, cx + r * .25, cy - r * .02], 20, 160, fill=INK, width=max(3, int(r * .06)))


ICONS = dict(coin=coin, shield=shield, chart=chart, calendar=calendar, house=house, piggy=piggy, heart=heart,
             umbrella=umbrella, lock=lock, gauge=gauge, goldbar=goldbar, plant=plant, person=person)

# slug -> (hero icon, [satellite icons]); anything unlisted falls back to DEFAULT.
SCENES = {
    "emergency-fund-india": ("piggy", ["umbrella", "calendar", "lock", "shield", "coin"]),
    "sip-vs-lumpsum": ("chart", ["calendar", "coin", "piggy", "plant", "person"]),
    "best-tax-saving-investments-80c": ("shield", ["coin", "house", "chart", "piggy", "heart"]),
    "credit-score-improve-india": ("gauge", ["coin", "shield", "calendar", "chart", "person"]),
    "index-funds-beginners-india": ("plant", ["chart", "coin", "house", "calendar", "person"]),
    "health-insurance-sum-insured": ("heart", ["shield", "house", "coin", "person", "umbrella"]),
    "retirement-planning-30s-india": ("person", ["house", "coin", "plant", "calendar", "chart"]),
    "home-loan-prepayment-strategy": ("house", ["coin", "calendar", "piggy", "lock", "chart"]),
    "mutual-fund-direct-vs-regular": ("chart", ["coin", "person", "shield", "piggy", "plant"]),
    "first-salary-financial-plan": ("person", ["coin", "piggy", "shield", "chart", "calendar"]),
    "nps-vs-mutual-funds-retirement": ("chart", ["person", "shield", "coin", "house", "plant"]),
    "gold-investment-options-india": ("goldbar", ["coin", "shield", "chart", "lock", "heart"]),
    "term-insurance-how-much-cover": ("umbrella", ["shield", "heart", "house", "coin", "person"]),
    "debt-funds-explained-india": ("shield", ["chart", "coin", "lock", "calendar", "plant"]),
    "budgeting-methods-compared": ("piggy", ["coin", "calendar", "chart", "person", "shield"]),
}
DEFAULT = ("coin", ["chart", "shield", "piggy", "calendar", "plant"])


def draw_scene(layer_draw, slug, w, h):
    """Draws the hero icon in a big translucent circle plus five satellite badges, all within a w x h box."""
    hero, sats = SCENES.get(slug, DEFAULT)
    cx, cy = w / 2, h * .52
    R = min(w, h) * .33
    layer_draw.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(255, 255, 255, 46))
    layer_draw.ellipse([cx - R * .82, cy - R * .82, cx + R * .82, cy + R * .82], fill=(255, 255, 255, 40))
    ICONS[hero](layer_draw, cx, cy - R * .02, R * (.52 if hero == "person" else .6))
    slots = [(-.98, -.62), (.98, -.55), (-1.1, .35), (1.08, .4), (0.02, 1.08)]
    for (sx, sy), name in zip(slots, sats):
        bx, by, br = cx + sx * R, cy + sy * R, R * .30
        layer_draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(255, 255, 255, 235))
        ICONS[name](layer_draw, bx, by - br * .02, br * (.5 if name == "person" else .58))
