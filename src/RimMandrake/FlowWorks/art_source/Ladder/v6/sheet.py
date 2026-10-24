#!/usr/bin/env python3
"""Dense numbered owner sheet for LADDER_PORTABLE_REDRAW_NORTH_FROM_GROUND, at true in-game scale beside a colonist (the
live pit capture v4/panel.py cleans, padded by v5/scene.py; 228 px per cell).

    python3 sheet.py <out.png> [scratch_dir]

Stations: 1 BEFORE (shipped); 2-4 AFTER north + south from the ground sprite, east/west = GPT v2 | ground tilt A | ground tilt B;
5 zooms of the north and south, before/after; 6 the ground sprite itself (the source).
"""
import shutil
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "v5"))
import scene as S5  # noqa: E402  (importing it pads the v4 pit: it patches P4.clean_pit and P4.X0; keep the import)
import portable_from_ground as G  # noqa: E402

P4 = S5.P4
GPT_V2 = HERE.parent / "v5" / "out"
BEFORE = HERE / "before"
FACINGS = ("north", "east", "west", "south")


def _font(sz):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", sz)
    except OSError:
        return ImageFont.load_default()


def _stage(tmp, name, files):
    d = Path(tmp) / name
    d.mkdir()
    for f, src in files.items():
        shutil.copy(src, d / ("RM_LadderPortable_%s.png" % f))
    return d


def _station(n, title, im):
    out = Image.new("RGBA", (im.width, im.height + 56), (22, 22, 22, 255))
    out.alpha_composite(im, (0, 56))
    d = ImageDraw.Draw(out)
    d.rectangle((0, 0, 44, 44), fill=(230, 190, 60, 255))
    d.text((10, 6), str(n), fill=(0, 0, 0, 255), font=_font(28))
    d.text((54, 4), title[0], fill=(240, 240, 240, 255), font=_font(20))
    d.text((54, 30), title[1], fill=(190, 190, 190, 255), font=_font(15))
    return out


def build(out_png, scratch=None):
    tmp = tempfile.mkdtemp(dir=scratch)
    try:
        return _build(out_png, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _build(out_png, tmp):
    new = Path(tmp) / "new"
    G.build(new)
    sets = [
        ("BEFORE: N/S shipped until 2026-10-24 (v6/before)", "N squeezed upright redraw, S short ladder stub; E/W v4 (still installed)",
         {f: BEFORE / ("RM_LadderPortable_%s.png" % f) for f in FACINGS}),
        ("AFTER N+S from the ground ladder; E/W = GPT v2", "the E/W you saw on portable_v2",
         {"north": new / "RM_LadderPortable_north.png", "south": new / "RM_LadderPortable_south.png",
          "east": GPT_V2 / "RM_LadderPortable_east.png", "west": GPT_V2 / "RM_LadderPortable_west.png"}),
    ]
    for k, t in G.TILTS.items():
        sets.append(("AFTER N+S from ground; E/W = ground ladder raised %d deg" % t, "candidate %s for E/W" % k.upper(),
                     {"north": new / "RM_LadderPortable_north.png", "south": new / "RM_LadderPortable_south.png",
                      "east": new / ("RM_LadderPortable_east_%s.png" % k), "west": new / ("RM_LadderPortable_west_%s.png" % k)}))
    tiles = []
    for i, (t1, t2, files) in enumerate(sets, 1):
        d = _stage(tmp, "s%d" % i, files)
        tiles.append(_station(i, (t1, t2), P4.scene(d, {f: "RM_LadderPortable_%s" % f for f in FACINGS})))
    # 5: zooms (north top half + south rim strip), before | after, 2x
    pits = [P4.scene(_stage(tmp, "z%d" % j, files), {f: "RM_LadderPortable_%s" % f for f in FACINGS})
            for j, files in ((0, sets[0][2]), (1, sets[1][2]))]
    X = P4.X0
    ncrop = (X + P4.PPC - 40, 0, X + 2 * P4.PPC + 40, 330)
    scrop = (X + P4.PPC - 40, P4.Y0 + 3 * P4.PPC - 120, X + 2 * P4.PPC + 40, P4.Y0 + 3 * P4.PPC + 40)
    zw = ncrop[2] - ncrop[0]
    z = Image.new("RGBA", (4 * zw + 30, 680 + 320), (22, 22, 22, 255))
    dd = ImageDraw.Draw(z)
    for j, p in enumerate(pits):
        n = p.crop(ncrop).resize((zw * 2, 660), Image.LANCZOS)
        s = p.crop(scrop).resize((zw * 2, 320), Image.LANCZOS)
        x = j * (zw * 2 + 30)
        z.alpha_composite(n, (x, 0))
        z.alpha_composite(s, (x, 680))
        dd.text((x + 6, 4), ("5a BEFORE north" if j == 0 else "5b AFTER north (ground ladder upright)"), fill=(255, 255, 0, 255), font=_font(18))
        dd.text((x + 6, 684), ("5c BEFORE south" if j == 0 else "5d AFTER south: stringer tips only"), fill=(255, 255, 0, 255), font=_font(18))
    tiles.append(_station(5, ("zooms x2", "north top / south near rim, before | after"), z))
    # 6: the source sprite at the same scale as stations 1-4
    fl = Image.open(G.FLAT).convert("RGBA").resize((P4.PPC, P4.PPC), Image.LANCZOS)
    six = Image.new("RGBA", (520, 300), (60, 52, 44, 255))
    six.alpha_composite(fl, (20, 36))
    six.alpha_composite(fl.rotate(90), (272, 36))
    ImageDraw.Draw(six).text((20, 6), "on the ground (kept)        turned upright = the north", fill=(240, 240, 240, 255), font=_font(16))
    tiles.append(_station(6, ("source: the ground ladder", "RM_LadderPortableFlat, same scale"), six))
    rows = [tiles[0:3], tiles[3:6]]
    W = max(sum(t.width for t in r) + 20 * (len(r) - 1) for r in rows)
    H = sum(max(t.height for t in r) for r in rows) + 20 + 60
    sheet = Image.new("RGBA", (W, H), (14, 14, 14, 255))
    ImageDraw.Draw(sheet).text((10, 14), "Portable ladder: installed facings from the lying-on-ground sprite (LADDER_PORTABLE_REDRAW_NORTH_FROM_GROUND)",
                               fill=(255, 255, 255, 255), font=_font(24))
    y = 60
    for r in rows:
        x = 0
        for t in r:
            sheet.alpha_composite(t, (x, y))
            x += t.width + 20
        y += max(t.height for t in r) + 20
    sheet.convert("RGB").save(out_png)
    return out_png, sheet.size


if __name__ == "__main__":
    print(build(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else None))
