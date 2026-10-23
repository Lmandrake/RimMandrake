#!/usr/bin/env python3
"""Grey geometry guides for the bank stake and silt-trap redraws (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS fixes 8 and 10;
owner 2026-10-17 by card: "Commission REVIEW.md items 3,4,6,7,8,9,10 in four styles; judged in game").
Image 1 of each codex edit (generate.sh): it anchors the building camera (orthographic, ~35 deg, lit top faces) and the
proportions. Usage: guides.py <outdir>"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

BG = (205, 205, 205, 255)
TOP, FRONT, DARK, LINE, EARTH = (235, 235, 235, 255), (150, 150, 150, 255), (90, 90, 90, 255), (60, 60, 60, 255), (175, 175, 175, 255)


def ridge_h(out):
    """Levee ridge running left-right, one stake-to-stake span: earth bank with a lit crest, a crib face toward the
    camera, two crib uprights at 1/4 and 3/4 so the whole width is two periods and tiles. 1024x512."""
    W, H = 1024, 512
    im = Image.new("RGBA", (W, H), BG); d = ImageDraw.Draw(im)
    d.polygon([(0, 210), (W, 210), (W, 250), (0, 250)], fill=TOP)          # crest (lit earth top)
    d.line([0, 210, W, 210], fill=LINE, width=4)
    d.rectangle([0, 250, W, 360], fill=FRONT)                              # crib boards facing the camera
    for y in (285, 320):
        d.line([0, y, W, y], fill=LINE, width=3)
    d.rectangle([0, 360, W, 385], fill=DARK)                               # damp foot
    for x in (256, 768):                                                    # crib uprights
        d.rectangle([x - 22, 235, x + 22, 390], fill=DARK, outline=LINE, width=4)
    im.save(out)


def ridge_v(out):
    """Levee ridge running top-bottom (away from the camera), seen from above: shaded west flank, lit crest, east flank
    with crib board ends; two uprights at 1/4 and 3/4 of the height. 512x1024."""
    W, H = 512, 1024
    im = Image.new("RGBA", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([150, 0, 200, H], fill=FRONT)                              # west flank
    d.rectangle([200, 0, 312, H], fill=TOP)                                # crest
    d.rectangle([312, 0, 362, H], fill=FRONT)                              # east flank (crib)
    for y in range(0, H, 64):
        d.line([312, y, 362, y], fill=LINE, width=3)
    for y in (256, 768):
        d.rectangle([228, y - 26, 284, y + 26], fill=DARK, outline=LINE, width=4)
    im.save(out)


def post(out):
    """One lamp-topped stake on a small earth footing: post body, lantern housing, lit top. 1024x1024."""
    W = H = 1024
    im = Image.new("RGBA", (W, H), BG); d = ImageDraw.Draw(im)
    d.ellipse([330, 720, 694, 860], fill=EARTH, outline=LINE, width=5)     # earth footing
    d.rectangle([452, 400, 572, 800], fill=FRONT, outline=LINE, width=6)   # post
    d.ellipse([452, 370, 572, 430], fill=TOP, outline=LINE, width=5)
    d.rectangle([432, 600, 592, 640], fill=DARK)                            # lashing band
    d.rectangle([442, 190, 582, 380], fill=TOP, outline=LINE, width=6)     # lantern housing
    d.rectangle([472, 230, 552, 340], fill=(250, 250, 250, 255))            # lantern glass
    d.polygon([(432, 190), (592, 190), (512, 130)], fill=DARK)              # lantern hood
    im.save(out)


def baffle(out):
    """Silt-trap baffle: a short timber wall left-right, its lower band dark and wet where it stands in the margin water,
    three posts. 1024x1024 (the trap draws 1.2 cells square)."""
    W = H = 1024
    im = Image.new("RGBA", (W, H), BG); d = ImageDraw.Draw(im)
    d.polygon([(120, 380), (904, 380), (904, 420), (120, 420)], fill=TOP)
    d.rectangle([120, 420, 904, 700], fill=FRONT)
    for y in (480, 540, 600):
        d.line([120, y, 904, y], fill=LINE, width=4)
    d.rectangle([120, 640, 904, 720], fill=DARK)                            # wet band at the waterline
    for x in (150, 512, 874):
        d.rectangle([x - 30, 330, x + 30, 740], fill=DARK, outline=LINE, width=5)
    d.ellipse([90, 700, 934, 790], outline=LINE, width=4)                   # ripple ring where it meets the water
    im.save(out)


if __name__ == "__main__":
    o = Path(sys.argv[1]); o.mkdir(parents=True, exist_ok=True)
    ridge_h(o / "guide_ridge_h.png"); ridge_v(o / "guide_ridge_v.png"); post(o / "guide_post.png"); baffle(o / "guide_baffle.png")
