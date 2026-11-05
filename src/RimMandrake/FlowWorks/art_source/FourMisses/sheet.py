#!/usr/bin/env python3
"""True-scale before/after sheet for FW_ART_POLISH_REDRAW_FOUR_SMALL_MISSES -> sheet.png beside this file.

One row per miss, 128 px per cell (each picture's draw size: debris 1 cell, sign 1.0, bottle 0.75, weir spill one cell
per water cell over its 1x2 section), a vanilla colonist (scale_panel.human_sprite) at the same scale, BEFORE then
AFTER, each also at normal play (32 px/cell). The weir row shows the installed kept spill alone and in a composite
(art_source/Weir/out), then the redrawn staged spill (out_photo, crest_spill) alone and composited on its own body.
Run fix_four_misses.py and Weir/weir_by_photo.py first.
"""
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils/art"))
sys.path.insert(0, str(HERE.parent / "Weir"))
import compose  # noqa: E402
import scale_panel  # noqa: E402

PPC = 128
GROUND = (112, 98, 72, 255)
TEX = HERE.parents[1] / "Textures"


def at(im, cells, ppc=PPC):
    s = max(1, round(cells * ppc))
    return im.convert("RGBa").resize((s, s), Image.BOX).convert("RGBA")


def weir_scene(lo_dir, look):
    compose.OUT = lo_dir
    sc = compose.scene(look, 5, 4, lambda x, z: 2 <= x <= 3, [[(1, 1), (2, 1)], [(3, 1), (4, 1)]], "east")
    return sc.crop((C(1), C(1), C(5), C(3.5)))


def C(n):
    return int(n * PPC)


def main():
    human = scale_panel.human_sprite(PPC)[0]
    chars = [f"RM_ScorchDebris_Char{i}" for i in (0, 2, 5)]
    rows = []
    rows.append(("1 scorch debris (Char0, 2, 5; 1 cell)", [(Image.open(HERE / "before" / f"{n}.png"), 1) for n in chars],
                 [(Image.open(HERE / "out" / f"{n}.png"), 1) for n in chars]))
    rows.append(("2 station sign (drawSize 1.0)", [(Image.open(HERE / "before/RM_StationSign.png"), 1)],
                 [(Image.open(HERE / "out/RM_StationSign.png"), 1)]))
    rows.append(("3 fresh-water bottle, Industrial (drawSize 0.75)", [(Image.open(HERE / "before/RM_Bottle_Industrial.png"), 0.75)],
                 [(Image.open(HERE / "out/RM_Bottle_Industrial.png"), 0.75)]))
    weir = HERE.parent / "Weir"
    tmp = Path("/tmp/fourmisses_weir")
    shutil.rmtree(tmp, ignore_errors=True)
    for v, src in (("kept", weir / "out"), ("new", weir / "out_photo")):
        for look in compose.LOOKS:
            d = tmp / v / look
            d.mkdir(parents=True, exist_ok=True)
            for p in (src / look).glob("*.png"):
                (d / p.name).write_bytes(p.read_bytes())
        for p in (weir / "out").glob("RM_BankWeirWater_*.png"):
            (tmp / v / p.name).write_bytes(p.read_bytes())
    before = [(Image.open(weir / "out/Industrial/RM_BankWeirSpill_east.png"), 1), (weir_scene(tmp / "kept", "Industrial"), None)]
    after = [(Image.open(weir / "out_photo/Industrial/RM_BankWeirSpill_east.png"), 1), (weir_scene(tmp / "new", "Industrial"), None),
             (Image.open(weir / "out_photo/Scrapper/RM_BankWeirSpill_east.png"), 1), (weir_scene(tmp / "new", "Scrapper"), None),
             (Image.open(weir / "out_photo/Modern/RM_BankWeirSpill_east.png"), 1), (weir_scene(tmp / "new", "Modern"), None),
             (Image.open(weir / "out_photo/Futuristic/RM_BankWeirSpill_east.png"), 1), (weir_scene(tmp / "new", "Futuristic"), None)]
    rows.append(("4 weir spill, east (spill alone 1 cell, then in its scene); before = installed kept Industrial; "
                 "after = staged Industrial, Scrapper, Modern, Futuristic", before, after))

    def strip(items):
        ims = [human]
        for im, cells in items:
            ims.append(at(im, cells) if cells else im.convert("RGBA"))
        small = [at(im, cells, 32) if cells else im.convert("RGBA").resize((im.size[0] // 4, im.size[1] // 4), Image.BOX)
                 for im, cells in items]
        w = sum(i.size[0] for i in ims) + 16 * len(ims) + sum(i.size[0] for i in small) + 8 * len(small) + 40
        h = max(i.size[1] for i in ims) + 8
        s = Image.new("RGBA", (w, h), GROUND)
        x = 0
        for i in ims:
            s.alpha_composite(i, (x, h - i.size[1] - 4))
            x += i.size[0] + 16
        x += 40
        for i in small:
            s.alpha_composite(i, (x, h - i.size[1] - 4))
            x += i.size[0] + 8
        return s

    blocks = []
    for label, b, a in rows:
        sb, sa = strip(b), strip(a)
        w = max(sb.size[0], sa.size[0]) + 90
        blk = Image.new("RGBA", (w, sb.size[1] + sa.size[1] + 40), (24, 22, 20, 255))
        dr = ImageDraw.Draw(blk)
        dr.text((6, 4), label, fill=(240, 230, 200, 255))
        dr.text((6, 24 + sb.size[1] // 2), "BEFORE", fill=(255, 160, 140, 255))
        dr.text((6, 34 + sb.size[1] + sa.size[1] // 2), "AFTER", fill=(150, 255, 160, 255))
        blk.alpha_composite(sb, (80, 20))
        blk.alpha_composite(sa, (80, 30 + sb.size[1]))
        blocks.append(blk)
    W = max(b.size[0] for b in blocks)
    sheet = Image.new("RGBA", (W, sum(b.size[1] for b in blocks) + 10 * len(blocks) + 30), (24, 22, 20, 255))
    ImageDraw.Draw(sheet).text((6, 6), "FW_ART_POLISH_REDRAW_FOUR_SMALL_MISSES - true scale, 128 px/cell; vanilla colonist "
                               "(1.5-cell mesh) left of every strip; after the gap, the same at normal play 32 px/cell",
                               fill=(255, 255, 255, 255))
    y = 30
    for b in blocks:
        sheet.alpha_composite(b, (0, y))
        y += b.size[1] + 10
    sheet.save(HERE / "sheet.png")
    print("sheet", sheet.size)


if __name__ == "__main__":
    main()
