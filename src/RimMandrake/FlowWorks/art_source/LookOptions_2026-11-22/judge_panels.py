#!/usr/bin/env python3
"""True-scale panels of the 2026-11-22 look options, for the judge and the owner's single images.

Each tank option is drawn beside the vanilla human (scale_panel.human_sprite, the engine's layers) and the accepted Scrapper
tank, all at the same px per cell, over desert terrain. A pipe option is assembled the way the game links it (vanilla
Basic link: atlas tile i = N1+E2+S4+W8, rows from the bottom, displayed cell = inner 3/4 of the tile) into one run with
straights, an elbow, a tee, a cross and end caps, with the matching sprinkler head seated on a pipe cell; this shows tiling
along a run and the joints.

    judge_panels.py OPTIONS_DIR OUT_DIR [--ppc 64]
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
import scale_panel  # noqa: E402

TEX = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks"
TERRAIN = (124, 100, 72, 255)
SCRAPPER_TANK = TEX / "Tank/Scrapper/RM_LiquidTank.png"


def _label(img, text, xy):
    ImageDraw.Draw(img).text(xy, text, fill=(235, 225, 205, 255))


def tank_panel(option_png, ppc, title):
    """human | Scrapper tank (accepted) | option, tank drawSize (2,2) on its 2x2 footprint."""
    hum, m, hoff = scale_panel.human_sprite(ppc)
    tank = 2 * ppc
    scr = Image.open(SCRAPPER_TANK).convert("RGBA").resize((tank, tank), Image.LANCZOS)
    opt = Image.open(option_png).convert("RGBA").resize((tank, tank), Image.LANCZOS)
    pad = ppc // 2
    W = pad + hum.width + pad + tank + pad + tank + pad
    H = 18 + max(hum.height, tank) + pad + 16
    img = Image.new("RGBA", (W, H), TERRAIN)
    base = H - 16 - pad // 2
    x = pad
    img.alpha_composite(hum, (x, base - hum.height)); _label(img, "human", (x, base + 2)); x += hum.width + pad
    img.alpha_composite(scr, (x, base - tank)); _label(img, "Scrapper (accepted)", (x, base + 2)); x += tank + pad
    img.alpha_composite(opt, (x, base - tank)); _label(img, title, (x, base + 2))
    _label(img, f"true scale, {ppc} px per cell", (pad, 3))
    return img


def atlas_tiles(atlas_png, ppc):
    a = Image.open(atlas_png).convert("RGBA")
    T = a.width // 4; P = T // 8; C = T - 2 * P
    tiles = {}
    for i in range(16):
        col, r = i % 4, 3 - i // 4
        t = a.crop((col * T + P, r * T + P, col * T + P + C, r * T + P + C))
        tiles[i] = t.resize((ppc, ppc), Image.LANCZOS)
    return tiles


# a run: a long east-west main with a tee and a cross, a north-south branch, an elbow and two dead ends
RUN = {(x, 2) for x in range(0, 8)} | {(3, y) for y in range(0, 6)} | {(6, y) for y in range(2, 5)} | {(7, 4), (8, 4)}
SPRINKLER_AT = (6, 3)


def pipe_panel(atlas_png, sprinkler_png, ppc, title):
    tiles = atlas_tiles(atlas_png, ppc)
    gw, gh = 9, 6
    hum, m, hoff = scale_panel.human_sprite(ppc)
    pad = ppc // 2
    W = pad + gw * ppc + pad + hum.width + pad
    H = 18 + gh * ppc + pad
    img = Image.new("RGBA", (W, H), TERRAIN)
    oy = 18
    for (x, y) in RUN:
        i = ((x, y - 1) in RUN) * 1 + ((x + 1, y) in RUN) * 2 + ((x, y + 1) in RUN) * 4 + ((x - 1, y) in RUN) * 8
        img.alpha_composite(tiles[i], (pad + x * ppc, oy + y * ppc))
    if sprinkler_png:
        sp = Image.open(sprinkler_png).convert("RGBA").resize((ppc, ppc), Image.LANCZOS)
        sx, sy = SPRINKLER_AT
        img.alpha_composite(sp, (pad + sx * ppc, oy + sy * ppc))
    hx = pad + gw * ppc + pad
    img.alpha_composite(hum, (hx, oy + 3 * ppc - hum.height + ppc // 2))
    _label(img, f"{title}: true scale, {ppc} px per cell", (pad, 3))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("options"); ap.add_argument("out")
    ap.add_argument("--ppc", type=int, default=64)
    a = ap.parse_args()
    src, out = Path(a.options), Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for p in sorted(src.glob("tank_*.png")):
        tank_panel(p, a.ppc, p.stem.replace("tank_", "")).save(out / f"{p.stem}__scale.png")
        print("wrote", out / f"{p.stem}__scale.png")
    shipped = {"pipe": TEX / "Pipe/Modern/UniversalPipe_Atlas.png", "spr": TEX / "Sprinkler/Modern/RM_SprinklerHead.png"}
    pipe_panel(shipped["pipe"], shipped["spr"], a.ppc, "Modern as shipped").save(out / "pipe_modern_SHIPPED__run.png")
    for p in sorted(src.glob("pipe_*.png")):
        letter = p.stem.split("_")[2]                       # pipe_modern_<A|B>_...
        spr = next(iter(sorted(src.glob(f"sprinkler_modern_{letter}_*.png"))), None)
        pipe_panel(p, spr, a.ppc, p.stem.replace("pipe_", "")).save(out / f"{p.stem}__run.png")
        print("wrote", out / f"{p.stem}__run.png")


if __name__ == "__main__":
    main()
