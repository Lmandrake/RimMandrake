#!/usr/bin/env python3
"""LINE_WIDTH_JUDGE_ARMS_NOT_INCLUDED — offline judgement material (not the in-game look, which stays owed).

Draws each line kind at TRUE scale beside the vanilla colonist (scale_panel.human_sprite), at the width shipped today
(read from code/art below) and at the width the 2026-10-20 card ruled (design/RimMandrake/flowworks_line_widths_2026-10-20.md:
1 cell ~ 1.41 m; pipe 30 cm, hose about half the pipe, cord = GSS wire). Real textures: the Industrial pipe atlas's
straight E-W tile, the hose's Strand_Flat / Strand_Plump strips, GSS's ground-cord and aerial span strands.
    python3 line_widths_panel.py  -> line_widths_128.png, line_widths_32.png (beside this file)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
import scale_panel as SP  # noqa: E402

FW = REPO / "src/RimMandrake/FlowWorks/Textures/RimMandrake/FlowWorks"
GSS = Path("/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/GimmeSomeSlack/Textures/RimMandrake/GimmeSomeSlack")
CELL_M = 1.41
cm = lambda cells: round(cells * CELL_M * 100)

# (label, source, width in cells, where the number comes from)
ROWS = [
    ("rigid pipe, SHIPPED", "pipe", 18 / 132, "Pipe/<Look>/UniversalPipe_Atlas: 18 px of the 132-px displayed cell (PIPE_GIRTH_TUNE_HALF_AS_THICK, owner 2026-10-21 'half as thick')"),
    ("rigid pipe, CARD SPEC", "pipe", 0.30 / CELL_M, "card 2026-10-20: pipe 30 cm"),
    ("hose empty, SHIPPED", "hose_flat", 0.18, "HoseMath.FlatVisible 0.18 x WidthScale 1 (owner 2026-10-22 'twice as thick')"),
    ("hose full, SHIPPED", "hose_plump", 0.23, "FlatVisible 0.18 + PlumpExtra 0.05"),
    ("hose, CARD SPEC", "hose_flat", 0.15 / CELL_M, "card 2026-10-20: about half the pipe, ~15 cm"),
    ("ground cord (GSS), SHIPPED", "cord", 0.08, "GSS SectionLayer_RM_MessyCords.StrandWidth 0.08"),
    ("overhead wire (GSS), SHIPPED", "wire", 0.10, "GSS AerialMaterials.WidthOf Industrial 0.10 (Scrapper 0.14, others 0.095)"),
]
RUN_CELLS = 5


def strip(kind):
    if kind == "pipe":
        a = Image.open(FW / "Pipe/Industrial/UniversalPipe_Atlas.png").convert("RGBA")
        t = a.crop((2 * 176, 1 * 176, 3 * 176, 2 * 176))  # the straight E-W tile (link bits E+W)
        al = np.array(t)[..., 3][:, 88] > 16
        rows = np.nonzero(al)[0]
        return t.crop((22, rows[0], 154, rows[-1] + 1))
    if kind == "hose_flat":
        return Image.open(FW / "Hose/Styles/Industrial/Strand_Flat.png").convert("RGBA") if (FW / "Hose/Styles/Industrial/Strand_Flat.png").exists() else Image.open(FW / "Hose/Strand_Flat.png").convert("RGBA")
    if kind == "hose_plump":
        p = FW / "Hose/Styles/Industrial/Strand_Plump.png"
        return Image.open(p if p.exists() else FW / "Hose/Strand_Plump.png").convert("RGBA")
    if kind == "cord":
        return Image.open(GSS / "Styles/ExtCord/Strand_Brown.png").convert("RGBA")
    if kind == "wire":
        return Image.open(GSS / "Aerial/SpanWire.png").convert("RGBA")
    raise KeyError(kind)


def run(kind, width_cells, ppc):
    s = strip(kind)
    h = max(1, round(width_cells * ppc))
    seg_w = max(1, round(s.width * h / s.height))
    seg = SP._premul_resize(s, seg_w, h)
    out = Image.new("RGBA", (RUN_CELLS * ppc, h), (0, 0, 0, 0))
    x = 0
    while x < out.width:
        out.alpha_composite(seg, (x, 0)) if x + seg_w <= out.width else out.alpha_composite(seg.crop((0, 0, out.width - x, h)), (x, 0))
        x += seg_w
    return out


def panel(ppc, label_px):
    f = SP._font(label_px)
    human, mesh, hoff = SP.human_sprite(ppc)
    rowh = max(ppc, label_px * 3)
    W = 30 + human.width + 40 + RUN_CELLS * ppc + 30 + label_px * 34
    H = 60 + rowh * len(ROWS) + 20
    im = Image.new("RGBA", (W, H), (120, 104, 80, 255))  # sand ground
    d = ImageDraw.Draw(im)
    x0 = 30 + human.width + 40
    # cell grid over the runs
    for c in range(RUN_CELLS + 1):
        d.line([(x0 + c * ppc, 50), (x0 + c * ppc, H - 20)], fill=(100, 86, 66, 255))
    d.text((10, 10), f"true scale, {ppc} px per cell (1 cell ~ {CELL_M} m); vanilla colonist for scale", fill=(255, 245, 225, 255), font=f)
    hy = 60 + (rowh * 2 - human.height) // 2
    im.alpha_composite(human, (30, max(50, hy)))
    for i, (lab, kind, wc, src) in enumerate(ROWS):
        y = 60 + i * rowh
        r = run(kind, wc, ppc)
        im.alpha_composite(r, (x0, y + (rowh - r.height) // 2))
        d.text((x0 + RUN_CELLS * ppc + 20, y + rowh // 2 - label_px), f"{lab}: {wc:.3f} cell ~ {cm(wc)} cm",
               fill=(255, 245, 225, 255), font=f)
        d.text((x0 + RUN_CELLS * ppc + 20, y + rowh // 2 + 2), src[:110], fill=(225, 210, 185, 255), font=SP._font(max(9, label_px - 4)))
    return im


if __name__ == "__main__":
    panel(128, 16).convert("RGB").save(HERE / "line_widths_128.png")
    panel(32, 13).convert("RGB").save(HERE / "line_widths_32.png")
    print("wrote", HERE / "line_widths_128.png", HERE / "line_widths_32.png")
