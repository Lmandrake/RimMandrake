#!/usr/bin/env python3
"""Grey geometry guides for the weir commission (RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS, owner 2026-10-16:
"(1) but in the four art styles"). Image 1 of each codex edit: anchors the building camera (orthographic, ~35 deg,
lit top face, front band ~1/3 of depth) and the low-wall proportions. Usage: guides.py <outdir>"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

BG = (205, 205, 205, 255)
TOP, FRONT, DARK, LINE = (235, 235, 235, 255), (150, 150, 150, 255), (90, 90, 90, 255), (60, 60, 60, 255)


def h_spill(out):
    """Wall runs left-right; downstream (the spill face) faces the camera. 1536x768 = 2 cells x 1 cell."""
    W, H = 1536, 768
    im = Image.new("RGBA", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([0, 270, W, 360], fill=TOP)                  # crest beam top face (lit)
    d.line([0, 270, W, 270], fill=LINE, width=4)
    d.polygon([(0, 360), (W, 360), (W, 500), (0, 500)], fill=FRONT)   # sloped spill apron, boards
    for x in range(0, W, 96):
        d.line([x, 362, x, 500], fill=LINE, width=3)
    d.rectangle([0, 500, W, 540], fill=DARK)                 # toe sill
    for x in (192, 576, 960, 1344):                          # squat supports in front of the toe
        d.rectangle([x - 34, 470, x + 34, 560], fill=DARK, outline=LINE, width=4)
    im.save(out)


def h_upstream(out):
    """Wall runs left-right; the UPSTREAM plank face faces the camera (spill falls away beyond the crest)."""
    W, H = 1536, 768
    im = Image.new("RGBA", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([0, 300, W, 380], fill=TOP)
    d.line([0, 300, W, 300], fill=LINE, width=4)
    d.rectangle([0, 380, W, 500], fill=FRONT)                # vertical upstream boards
    for x in range(0, W, 96):
        d.line([x, 382, x, 500], fill=LINE, width=3)
    d.rectangle([0, 470, W, 500], fill=DARK)                 # wet waterline band
    for x in (192, 576, 960, 1344):                          # pile heads breaking the crest line
        d.rectangle([x - 30, 285, x + 30, 330], fill=DARK, outline=LINE, width=4)
    im.save(out)


def v_east(out):
    """Wall runs top-bottom (away from camera); the spill apron slopes down to the RIGHT (east). 768x1536."""
    W, H = 768, 1536
    im = Image.new("RGBA", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([270, 0, 330, H], fill=DARK)                 # upstream edge in shade
    d.rectangle([330, 0, 420, H], fill=TOP)                  # crest top face
    d.rectangle([420, 0, 540, H], fill=FRONT)                # apron sloping east
    for y in range(0, H, 96):
        d.line([420, y, 540, y], fill=LINE, width=3)
    d.rectangle([540, 0, 570, H], fill=DARK)                 # toe sill
    for y in (192, 576, 960, 1344):
        d.rectangle([540, y - 34, 610, y + 34], fill=DARK, outline=LINE, width=4)
    im.save(out)


def cap(out):
    """The free end of a run: one stout pile post (seen from the building camera). 1024x1024."""
    W = H = 1024
    im = Image.new("RGBA", (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([392, 380, 632, 760], fill=FRONT, outline=LINE, width=6)   # post body
    d.ellipse([392, 312, 632, 448], fill=TOP, outline=LINE, width=6)       # top face ellipse ~0.56
    d.rectangle([380, 560, 644, 600], fill=DARK)                            # lashing band
    im.save(out)


if __name__ == "__main__":
    o = Path(sys.argv[1]); o.mkdir(parents=True, exist_ok=True)
    h_spill(o / "guide_h_spill.png"); h_upstream(o / "guide_h_upstream.png"); v_east(o / "guide_v_east.png"); cap(o / "guide_cap.png")
