#!/usr/bin/env python3
"""Build fidelity-review composites for CANON_CREATURE_REGEN_1 wave 3.

One PNG per creature: the owner-ruled canon reference image on the left,
the three new east/north/south renders (already generated on 2026-09-18,
found sitting unused in infrastructure/artpipe/_artsrc/) on the right, over
a checkerboard so alpha is visible. Same shape as wave 1/2's <slug>_fidelity.png.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO = Path("/mnt/d/Luke/dev/Rimworld")
OUT_DIR = REPO / "Transient/canon_regen_wave3_2026-09-23"

PANEL_H = 420
PAD = 16
LABEL_H = 28
CHECK = 12  # checkerboard cell size


def checkerboard(w, h):
    im = Image.new("RGB", (w, h), (26, 31, 38))
    d = ImageDraw.Draw(im)
    light = (42, 47, 55)
    for y in range(0, h, CHECK):
        for x in range(0, w, CHECK):
            if ((x // CHECK) + (y // CHECK)) % 2 == 0:
                d.rectangle([x, y, x + CHECK, y + CHECK], fill=light)
    return im


def fit(img: Image.Image, box_w: int, box_h: int) -> Image.Image:
    img = img.convert("RGBA")
    scale = min(box_w / img.width, box_h / img.height)
    nw, nh = max(1, int(img.width * scale)), max(1, int(img.height * scale))
    return img.resize((nw, nh), Image.LANCZOS)


def label(draw, text, x, y, w):
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((x + max(0, (w - tw) // 2), y), text, fill=(230, 226, 227), font=font)


def build(name: str, ref_path: Path, renders: dict, out_path: Path):
    panels = [("REFERENCE (ruled)", ref_path)] + [
        (f"wave 3 - {facing}", renders[facing]) for facing in ("east", "north", "south")
    ]
    n = len(panels)
    panel_w = 420
    total_w = n * panel_w + (n + 1) * PAD
    total_h = PANEL_H + LABEL_H + 2 * PAD

    canvas = checkerboard(total_w, total_h).convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    draw.text((PAD, 6), f"CANON_CREATURE_REGEN_1 wave 3 -- {name}", fill=(255, 180, 84))

    x = PAD
    y = LABEL_H + PAD
    for text, path in panels:
        im = Image.open(path)
        im = fit(im, panel_w - 8, PANEL_H - 8)
        ox = x + (panel_w - im.width) // 2
        oy = y + (PANEL_H - im.height) // 2
        canvas.alpha_composite(im, (ox, oy))
        label(draw, text, x, y + PANEL_H + 2, panel_w)
        x += panel_w + PAD

    canvas.convert("RGB").save(out_path)
    print(f"wrote {out_path}  {canvas.size}")


CREATURES = {
    "hawkbat": {
        "ref": REPO / "design/RimStarWars/canon_references/hawkbat/wookieepedia_legends_infobox.jpg",
        "renders": {
            f: REPO / f"infrastructure/artpipe/_artsrc/canon_hawkbat_v1_{f}/canon_hawkbat_v1_{f}.png"
            for f in ("east", "north", "south")
        },
    },
    "kinrath": {
        "ref": REPO / "design/RimStarWars/canon_references/kinrath/unfinished_tcw_netcasters_conceptclip.png",
        "renders": {
            f: REPO / f"infrastructure/artpipe/_artsrc/canon_kinrath_v1_{f}/canon_kinrath_v1_{f}.png"
            for f in ("east", "north", "south")
        },
    },
    "kreetle": {
        "ref": REPO / "design/RimStarWars/canon_references/kreetle/wookieepedia_infobox.jpg",
        "renders": {
            f: REPO / f"infrastructure/artpipe/_artsrc/canon_kreetle_v1_{f}/canon_kreetle_v1_{f}.png"
            for f in ("east", "north", "south")
        },
    },
}

if __name__ == "__main__":
    for name, spec in CREATURES.items():
        build(name, spec["ref"], spec["renders"], OUT_DIR / f"{name}_fidelity.png")
