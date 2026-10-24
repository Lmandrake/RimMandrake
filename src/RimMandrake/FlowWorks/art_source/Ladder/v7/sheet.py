#!/usr/bin/env python3
"""Owner sheet for RAIL_LADDER_REDRAW_FAT_RUNG_FENCE: the wooden rail ladder (RM_Ladder lowered / RM_LadderRaised) in the
ground ladder's pale wood, at true in-game scale beside a colonist (the live pit capture v4/panel.py cleans, padded by
v5/scene.py; 228 px per cell).

    python3 sheet.py <out.png> [scratch_dir]

Stations: 1-2 BEFORE (the steel-era rail set installed before this item, pinned in v7/before/) lowered | raised; 3-4 AFTER lowered | raised (rail_pale.build());
5 the portable ladder (the pale wood he approved) in the same pit; 6 zooms x2 of the north wall, before | after.
"""
import shutil
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "v6"))
import sheet as S6  # noqa: E402  (imports v5/scene.py, which pads the v4 pit; keep)
import rail_pale as R  # noqa: E402

P4 = S6.P4
CANALS = R.FLAT.parent
FACINGS = R.FACINGS


def _stage(tmp, name, files):
    d = Path(tmp) / name
    d.mkdir()
    for f, src in files.items():
        shutil.copy(src, d / ("L_%s.png" % f))
    return d


def _pit(tmp, name, files):
    return P4.scene(_stage(tmp, name, files), {f: "L_%s" % f for f in FACINGS})


BEFORE = Path(__file__).resolve().parent / "before"


def build(out_png, scratch=None, before_dir=BEFORE):
    """before_dir: where the BEFORE RM_Ladder*/RM_LadderRaised* facings are read (pinned copy of the set installed
    before RAIL_LADDER_REDRAW_FAT_RUNG_FENCE; never the working tree, which holds the AFTER once installed)."""
    tmp = tempfile.mkdtemp(dir=scratch)
    try:
        new = Path(tmp) / "new"
        R.build(new)
        sets = []
        for tag, what in (("RM_Ladder", "lowered (slid down: climbable)"), ("RM_LadderRaised", "raised (slid up onto the rim)")):
            sets.append(("BEFORE " + what, tag + " installed before (steel-era rails, not the yellow v5)", {f: Path(before_dir) / ("%s_%s.png" % (tag, f)) for f in FACINGS}))
        for tag, what in (("RM_Ladder", "lowered"), ("RM_LadderRaised", "raised")):
            sets.append(("AFTER %s: pale ground-ladder wood" % what, "same shape as the perspectives you passed; colour only",
                         {f: new / ("%s_%s.png" % (tag, f)) for f in FACINGS}))
        sets.append(("the portable ladder (the pale wood you approved)", "for colour: RM_LadderPortable, installed",
                     {f: CANALS / ("RM_LadderPortable_%s.png" % f) for f in FACINGS}))
        tiles = [S6._station(i, (t1, t2), _pit(tmp, "s%d" % i, files)) for i, (t1, t2, files) in enumerate(sets, 1)]
        X = P4.X0
        ncrop = (X + P4.PPC - 40, 0, X + 2 * P4.PPC + 40, 330)
        zw = ncrop[2] - ncrop[0]
        z = Image.new("RGBA", (4 * (zw * 2) + 3 * 30, 680), (22, 22, 22, 255))
        dd = ImageDraw.Draw(z)
        for j, (k, label) in enumerate(((0, "6a BEFORE lowered"), (2, "6b AFTER lowered"), (1, "6c BEFORE raised"), (3, "6d AFTER raised"))):
            p = _pit(tmp, "z%d" % j, sets[k][2]).crop(ncrop).resize((zw * 2, 660), Image.LANCZOS)
            x = j * (zw * 2 + 30)
            z.alpha_composite(p, (x, 0))
            dd.text((x + 6, 4), label, fill=(255, 255, 0, 255), font=S6._font(18))
        tiles.append(S6._station(6, ("zooms x2", "north wall, before | after, lowered then raised"), z))
        rows = [tiles[0:2] + tiles[4:5], tiles[2:4], tiles[5:6]]
        W = max(sum(t.width for t in r) + 20 * (len(r) - 1) for r in rows)
        H = sum(max(t.height for t in r) for r in rows) + 20 * len(rows) + 60
        sheet = Image.new("RGBA", (W, H), (14, 14, 14, 255))
        ImageDraw.Draw(sheet).text((10, 14), "Wooden rail ladder in the portable ladder's pale wood (RAIL_LADDER_REDRAW_FAT_RUNG_FENCE)",
                                   fill=(255, 255, 255, 255), font=S6._font(24))
        y = 60
        for r in rows:
            x = 0
            for t in r:
                sheet.alpha_composite(t, (x, y))
                x += t.width + 20
            y += max(t.height for t in r) + 20
        sheet.convert("RGB").save(out_png)
        return out_png, sheet.size
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    print(build(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else None))
