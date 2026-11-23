#!/usr/bin/env python3
"""The owner's pick image for the Modern pipe's straight-run variants (RIMMANDRAKE_INSTALL_TANK_SPRINKLER_PICKS_REDO_MODERN_PIPE_TOO_REPETITIVE).

Each row: the same laid run (a 12-cell main, a tee, a branch and an elbow; render_pipe_run.RUN) drawn as the game draws it,
large (128 px per cell, 2x the 64 px texture ratio) with a vanilla colonist at the same scale; then all four at play zoom
(32 px per cell). Style follows the earlier PICK_TANK_*.png pages.

Usage: build_pick_modern_pipe.py STRAIGHTS_DIR OUT.png   (STRAIGHTS_DIR holds pipe_modern_straights_{A,B,C}.png)
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
import render_pipe_run as R  # noqa: E402
import scale_panel as SP  # noqa: E402

ATLAS = HERE.parents[1] / "Textures/RimMandrake/FlowWorks/Pipe/Modern/UniversalPipe_Atlas.png"
BG = (58, 42, 30)
TXT = (236, 224, 204)
DIM = (186, 170, 150)
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BIG, PLAY = 128, 32
PAD = 28

OPTIONS = [
    ("in game today", "", None),
    ("A", "dusty, mostly clean", "A"),
    ("B", "faded, grimy, chipped", "B"),
    ("C", "clamps and couplings", "C"),
]


def main(argv):
    sdir, out = Path(argv[1]), Path(argv[2])
    tf, lf, wf, sf = (ImageFont.truetype(FB, 34), ImageFont.truetype(FB, 28), ImageFont.truetype(F, 26),
                      ImageFont.truetype(F, 20))
    hum, m, hoff = SP.human_sprite(BIG)
    hum = hum.crop(hum.getchannel("A").getbbox())
    runs = [(lab, words, R.run_image(ATLAS, sdir / f"pipe_modern_straights_{o}.png" if o else None, BIG, pad=32),
             R.run_image(ATLAS, sdir / f"pipe_modern_straights_{o}.png" if o else None, PLAY, pad=8)) for lab, words, o in OPTIONS]
    rw, rh = runs[0][2].size
    lab_h = 56
    title_h = 70
    play_w, play_h = runs[0][3].size
    PG = 24
    W = PAD * 2 + max(rw, 4 * play_w + 3 * PG)
    H = title_h + len(runs) * (rh + lab_h) + 20 + play_h + 44 + PAD
    page = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(page)
    d.text((PAD, 18), "Modern pipe, laid run: pick one", font=tf, fill=TXT)
    y = title_h
    for lab, words, big, _ in runs:
        panel = big.copy()
        # colonist standing on the ground cells south-west of the tee (col 1, rows 1-2), same 128 px per cell
        panel.alpha_composite(hum, (32 + int(1.2 * BIG), 32 + 3 * BIG - hum.height - 8))
        page.alpha_composite(panel, (PAD, y))
        ly = y + rh + 8
        d.text((PAD + 4, ly), lab, font=lf, fill=TXT)
        if words:
            d.text((PAD + 4 + d.textlength(lab + "  ", font=lf), ly + 2), words, font=wf, fill=TXT)
        y += rh + lab_h
    y += 20
    gap = PG
    x = PAD
    for lab, _, _, small in runs:
        page.alpha_composite(small, (x, y))
        short = "today" if lab.startswith("in game") else lab
        tw = d.textlength(short, font=sf)
        d.text((x + (play_w - tw) / 2, y + play_h + 8), short, font=sf, fill=DIM)
        x += play_w + gap
    out.parent.mkdir(parents=True, exist_ok=True)
    page.convert("RGB").save(out, optimize=True)
    print(out, page.size)


if __name__ == "__main__":
    main(sys.argv)
