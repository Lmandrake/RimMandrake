#!/usr/bin/env python3
"""Build fidelity-review composites for CANON_CREATURE_REGEN_1 wave 4.

One PNG per creature: the owner-ruled (or, where empty, best-match) canon
reference image on the left, the three new east/north/south renders on the
right, over a checkerboard so alpha is visible. Same shape as waves 1-3's
<slug>_fidelity.png.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO = Path("/mnt/d/Luke/dev/Rimworld")
OUT_DIR = REPO / "Transient/canon_regen_wave4_2026-09-23"

PANEL_H = 420
PAD = 16
LABEL_H = 28
CHECK = 12


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
    panels = [("REFERENCE", ref_path)] + [
        (f"wave 4 - {facing}", renders[facing]) for facing in ("east", "north", "south")
    ]
    n = len(panels)
    panel_w = 420
    total_w = n * panel_w + (n + 1) * PAD
    total_h = PANEL_H + LABEL_H + 2 * PAD

    canvas = checkerboard(total_w, total_h).convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    draw.text((PAD, 6), f"CANON_CREATURE_REGEN_1 wave 4 -- {name}", fill=(255, 180, 84))

    x = PAD
    y = LABEL_H + PAD
    for text, path in panels:
        if not path.exists():
            print(f"  MISSING {path}", file=sys.stderr)
            x += panel_w + PAD
            continue
        im = Image.open(path)
        im = fit(im, panel_w - 8, PANEL_H - 8)
        ox = x + (panel_w - im.width) // 2
        oy = y + (PANEL_H - im.height) // 2
        canvas.alpha_composite(im, (ox, oy))
        label(draw, text, x, y + PANEL_H + 2, panel_w)
        x += panel_w + PAD

    canvas.convert("RGB").save(out_path)
    print(f"wrote {out_path}  {canvas.size}")


def render_paths(job_id):
    return {
        f: REPO / f"infrastructure/artpipe/_artsrc/{job_id}_{f}/{job_id}_{f}.png"
        for f in ("east", "north", "south")
    }


CREATURES = {
    "boma": {
        "ref": REPO / "design/RimStarWars/canon_references/boma/boma_wookieepedia_1.jpg",
        "renders": render_paths("canon_boma_v1"),
    },
    "dewback": {
        "ref": REPO / "design/RimStarWars/canon_references/dewback/wookieepedia_infobox.jpg",
        "renders": render_paths("canon_dewback_v1"),
    },
    "insectomorph": {
        "ref": REPO / "design/RimStarWars/canon_references/insectomorph/wookieepedia_infobox.jpg",
        "renders": render_paths("canon_insectomorph_v1"),
    },
    "shiro": {
        "ref": REPO / "design/RimStarWars/canon_references/shiro/shiros_group_legends.jpg",
        "renders": render_paths("canon_shiro_v1"),
    },
    "vornskyr": {
        "ref": REPO / "design/RimStarWars/canon_references/vornskyr/wookieepedia_alienarchive.jpg",
        "renders": render_paths("canon_vornskyr_v1"),
    },
    "whisperbird": {
        "ref": REPO / "design/RimStarWars/canon_references/whisperbird/wookieepedia_alienarchive.jpg",
        "renders": render_paths("canon_whisperbird_v1"),
    },
    "zakkeg": {
        "ref": REPO / "design/RimStarWars/canon_references/zakkeg/wookieepedia_kotor2_juvenile.png",
        "renders": render_paths("canon_zakkeg_v1"),
    },
}

if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, spec in CREATURES.items():
        build(name, spec["ref"], spec["renders"], OUT_DIR / f"{name}_fidelity.png")
