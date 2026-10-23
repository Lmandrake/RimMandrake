"""FOUNTAIN_LOOP_BUILD_PUMPS_ITS_OWN_RAIN: grey camera blockouts (image 1 of an edit) for the v1 fountain candidates.
Camera (design/RimMandrake/building_camera_perspective_2026-10-14.md): orthographic, ~35 deg, every round rim an
ellipse 0.56 tall for its width, top faces lit, height extends north. Canvas 1024x1536 = drawSize (1,1.5) at
1024 px/cell; the 1x1 footprint is the lower 1024x1024, the basin's base on its south part.
Water is drawn in its true plane (art_judge_brief C6): basin water = a horizontal ellipse inside the rim; jets and
falling curtains vertical.  usage: guide.py <out_dir>   -> guide_A.png guide_B.png guide_C.png"""
import os
import sys
from PIL import Image, ImageDraw

K = 0.56
W, H = 1024, 1536
CX = 512
LINE = (55, 55, 55)
WATER = (120, 165, 205)


def cyl(d, cx, a, top, bot, shade=170, rim=True, top_fill=(225, 225, 225)):
    """An upright drum: top ellipse centre at `top`, bottom ellipse centre at `bot`."""
    b = a * K
    for x in range(int(cx - a), int(cx + a) + 1):
        u = (x - cx) / a
        v = int(shade - 25 + 60 * max(0, 1 - abs(u + 0.25) * 1.3))
        yb = bot + b * max(0, 1 - u * u) ** 0.5
        d.line([x, top, x, yb], fill=(v, v, v))
    d.arc([cx - a, bot - b, cx + a, bot + b], 0, 180, fill=LINE, width=5)
    d.line([cx - a, top, cx - a, bot], fill=LINE, width=5)
    d.line([cx + a, top, cx + a, bot], fill=LINE, width=5)
    if rim:
        d.ellipse([cx - a, top - b, cx + a, top + b], fill=top_fill, outline=LINE, width=5)


def basin(d, cx, a, top, bot, wall=0.12):
    """A round basin: outer drum, a rim band, the water surface ellipse inside (true horizontal plane)."""
    cyl(d, cx, a, top, bot)
    ia = a * (1 - wall)
    d.ellipse([cx - ia, top - ia * K, cx + ia, top + ia * K], fill=WATER, outline=LINE, width=4)


def jet(d, x, y0, y1, w=18):
    d.rectangle([x - w / 2, y1, x + w / 2, y0], fill=(200, 225, 245), outline=(90, 130, 170), width=3)


def guide_a(d):
    """A: tiered bowl — wide low basin, a pedestal, a small upper bowl overflowing, a short jet."""
    basin(d, CX, 470, 1180, 1330)
    cyl(d, CX, 70, 640, 1180, rim=False)                       # pedestal column, base hidden in the water
    basin(d, CX, 230, 600, 660, wall=0.15)                     # upper bowl
    for x in (CX - 160, CX + 160, CX):                         # curtains falling from the bowl lip to the basin water
        d.rectangle([x - 22, 690, x + 22, 1170], fill=(190, 215, 240), outline=(90, 130, 170), width=3)
    jet(d, CX, 600, 300)


def guide_b(d):
    """B: pillar of spouts — a square-ish low basin ring, a column with four spout heads, arcs into the basin."""
    basin(d, CX, 470, 1180, 1330)
    cyl(d, CX, 95, 430, 1180)                                  # column with a lit cap
    for sx in (-1, 1):                                         # two visible spouts, arcs falling outward to the water
        x0 = CX + sx * 95
        d.line([x0, 560, x0 + sx * 70, 560], fill=LINE, width=26)
        pts = [(x0 + sx * 70 + sx * t * 220, 560 + (t * t) * 560) for t in [i / 20 for i in range(21)]]
        d.line(pts, fill=(170, 205, 240), width=26)
    jet(d, CX, 430 - 95 * K, 180)


def guide_c(d):
    """C: cairn spring — a low ring of fitted stones, a stacked-rock cairn, water welling from the top, trickling."""
    basin(d, CX, 470, 1180, 1290, wall=0.10)
    for i, (a, top, bot) in enumerate([(260, 980, 1180), (190, 820, 980), (130, 680, 820), (80, 570, 680)]):
        cyl(d, CX + (i % 2) * 14 - 7, a, top, bot, shade=150 + i * 8)
    d.ellipse([CX - 40, 570 - 40 * K, CX + 40, 570 + 40 * K], fill=WATER, outline=LINE, width=4)
    for x in (CX - 30, CX + 50):
        d.line([(x, 590), (x - 10, 760), (x + 15, 950), (x, 1170)], fill=(170, 205, 240), width=16)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    for name, fn in (("A", guide_a), ("B", guide_b), ("C", guide_c)):
        im = Image.new("RGB", (W, H + 90), (255, 255, 255))
        d = ImageDraw.Draw(im)
        fn(d)
        im = im.crop((0, 90, W, H + 90))                                            # lift 90 px: the basin's lower arc fits
        p = os.path.join(out, "guide_%s.png" % name)
        im.save(p)
        print(p)


if __name__ == "__main__":
    main()
