#!/usr/bin/env python3
"""Dense numbered owner sheet for PIT_SPIKES_FIX_OVER_WALL_AND_SUBMERGE, from the offline scene (Tools/fw_scenes_spikes.py,
which runs the same layout / floor / fade math as Building_RM_Spikes; parity held by SpikeDrawChecks).

    python3 sheet.py <out.png>

Stations: 1 BEFORE (shipped whole-cell sprite) | 2 AFTER, on a 4 m pit with a 2 m shelf and a water row; 3 zoom of the
far-wall corner, before | after; 4 the water series 0 / 0.5 / 1 / 1.5 / 2 m, before and after; 5 stepped floors
(2 / 2.5 / 3 / 4 m side by side); 6 the three art variants on open floor; 7 the settings: outline off, wall faces off.
Each station's caption carries the check numbers for that scene.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "Tools"))
import fw_scenes_spikes as spk  # noqa: E402

BG = (22, 22, 22, 255)


def _font(sz):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", sz)
    except OSError:
        return ImageFont.load_default()


def _station(n, title, sub, im):
    im = im.convert("RGBA")
    out = Image.new("RGBA", (max(im.width, 700), im.height + 60), BG)
    out.alpha_composite(im, (0, 60))
    d = ImageDraw.Draw(out)
    d.rectangle((0, 0, 44, 44), fill=(230, 190, 60, 255))
    d.text((8 if n < 10 else 2, 6), str(n), fill=(0, 0, 0, 255), font=_font(28))
    d.text((54, 4), title, fill=(240, 240, 240, 255), font=_font(20))
    d.text((54, 32), sub, fill=(190, 190, 190, 255), font=_font(15))
    return out


def _row(ims, gap=16, labels=None):
    W = sum(i.width for i in ims) + gap * (len(ims) - 1)
    H = max(i.height for i in ims) + (26 if labels else 0)
    out = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(out)
    x = 0
    for k, im in enumerate(ims):
        out.alpha_composite(im.convert("RGBA"), (x, 26 if labels else 0))
        if labels:
            d.text((x + 4, 2), labels[k], fill=(255, 255, 0, 255), font=_font(17))
        x += im.width + gap
    return out


def _col(ims, gap=10):
    W = max(i.width for i in ims)
    out = Image.new("RGBA", (W, sum(i.height for i in ims) + gap * (len(ims) - 1)), BG)
    y = 0
    for im in ims:
        out.alpha_composite(im.convert("RGBA"), (0, y))
        y += im.height + gap
    return out


def _pit(res, margin=0.3, marks=None):
    """The scene cropped to the dug cells plus `margin` cell of ground; `marks` = {(x, z): text} drawn above a cell."""
    P, pit = res["P"], res["pit"]
    xs = [x for z in range(pit.H) for x in range(pit.W) if pit.d[z][x] > 0]
    zs = [z for z in range(pit.H) for x in range(pit.W) if pit.d[z][x] > 0]
    m = round(margin * P)
    c0, c1 = min(xs) * P - m, (max(xs) + 1) * P + m
    r0, r1 = (pit.H - max(zs) - 1) * P - m, (pit.H - min(zs)) * P + m
    im = res["img"].crop((c0, r0, c1, r1)).convert("RGBA")
    d = ImageDraw.Draw(im)
    for (x, z), t in (marks or {}).items():
        d.text((x * P - c0 + 6, (pit.H - z - 1) * P - r0 + 6), t, fill=(150, 220, 255, 255), font=_font(16),
               stroke_width=2, stroke_fill=(0, 0, 0, 255))
    return im


def _verdicts(res):
    ok, why = spk.spikes_over_wall(res)
    return "over wall %s: %s" % ("PASS" if ok else "FAIL", why.split(" over the wall")[0])


def build(out_png):
    tiles = []
    P = 150
    res = {m: spk.render(spk.check_pit(), m, P=P) for m in ("before", "after")}
    for n, m in ((1, "before"), (2, "after")):
        sub = spk.spikes_submerged(res[m])
        tiles.append(_station(n, "%s: 4 m pit, 2 m shelf (east), water row along the south" % m.upper(),
                              "%s; submerge %s" % (_verdicts(res[m]), "PASS" if sub[0] else "FAIL"),
                              _pit(res[m], marks={(x, 1): "%.1f m" % (f * 0.5) for x, f in zip(range(2, 6), (1, 2, 3, 4))})))
    # 3: zoom on the north-west corner, cells x 1..2 of the north row (z 3), x2
    crops = []
    for m in ("before", "after"):
        im = res[m]["img"]
        c = im.crop((P - 30, P - 30, 3 * P + 30, 2 * P + 30))
        crops.append(c.resize((c.width * 2, c.height * 2), Image.LANCZOS))
    tiles.append(_station(3, "zoom x2: far wall + west wall corner", "pale far wall, side bevel and black rim line; before | after",
                          _row(crops, labels=["3a BEFORE", "3b AFTER"])))
    # 4: water series, one 4 m-deep cell per depth inside a 2 m-wide trench (so each has walls round it)
    fills = [0, 1, 2, 3, 4]
    depth = [[0] * 7, [0] + [8] * 5 + [0], [0] + [8] * 5 + [0], [0] * 7]
    fill = [[0] * 7, [0] * 7, [0] + fills + [0], [0] * 7]
    series = []
    for m in ("before", "after"):
        r = spk.render(spk.Pit(depth, fill, [(x, z) for x in range(1, 6) for z in (1, 2)]), m, P=150)
        sub = spk.spikes_submerged(r)
        series.append((_pit(r, marks={(x, 1): "%.1f m" % (f * 0.5) for x, f in zip(range(1, 6), fills)}), "4%s %s  submerge %s: %s" % ("a" if m == "before" else "b", m.upper(),
                                                              "PASS" if sub[0] else "FAIL", sub[1].split(" | ")[-1])))
    col = []
    for im, t in series:
        cap = Image.new("RGBA", (im.width, 24), BG)
        ImageDraw.Draw(cap).text((4, 2), t, fill=(255, 255, 0, 255), font=_font(16))
        col += [cap, im]
    tiles.append(_station(4, "water series: north row dry, south row 0 / 0.5 / 1 / 1.5 / 2 m",
                          "after: each stake a quarter at 0.5 m (overlapping stakes add up), gone from 1 m", _col(col, gap=4)))
    # 5: stepped floors, 2 / 2.5 / 3 / 4 m cells side by side, dry
    steps = [[0] * 6, [0, 4, 5, 6, 8, 0], [0, 4, 5, 6, 8, 0], [0] * 6]
    r5 = spk.render(spk.Pit(steps, None, [(x, z) for x in range(1, 5) for z in (1, 2)]), "after", P=150)
    tiles.append(_station(5, "AFTER stepped floors 2 / 2.5 / 3 / 4 m (west to east)",
                          "the far wall and each step's bevel; " + _verdicts(r5), _pit(r5)))
    # 6: the three variants, one open 3x3 D8 pit each (the centre cell has no wall at all)
    vims = []
    for v in range(3):
        dep = [[0] * 5] + [[0, 8, 8, 8, 0] for _ in range(3)] + [[0] * 5]
        cells = [(x, z) for x in range(1, 4) for z in range(1, 4)]
        vims.append(_pit(spk.render(spk.Pit(dep, None, cells, variant_of={c: v for c in cells}), "after", P=120)))
    tiles.append(_station(6, "AFTER the three art variants (RM_Spikes_a / _b / _c)", "the stakes are each variant's own, cut from the shipped PNG",
                          _row(vims, labels=["6a variant a", "6b variant b", "6c variant c"])))
    # 7: settings
    sims = []
    for faces, outline in ((True, False), (False, False)):
        r = spk.render(spk.check_pit(), "after", P=130, faces=faces, outline=outline)
        sims.append((_pit(r), "7%s %s" % ("a" if faces else "b", "outline OFF" if faces else "wall faces OFF")))
    tiles.append(_station(7, "AFTER with the mod settings off", "outline off: stakes reach the outline's place; faces off: the whole cell",
                          _row([i for i, _ in sims], labels=[t for _, t in sims])))
    t = dict(zip(range(1, 8), tiles))
    rows = [[t[1], t[2], t[4]], [t[3], t[6]], [t[5], t[7]]]
    W = max(sum(t.width for t in r) + 20 * (len(r) - 1) for r in rows)
    H = sum(max(t.height for t in r) for r in rows) + 20 * len(rows) + 60
    sheet = Image.new("RGBA", (W, H), (14, 14, 14, 255))
    ImageDraw.Draw(sheet).text((10, 14), "Pit spikes: kept off the pit walls, sink fast in water (PIT_SPIKES_FIX_OVER_WALL_AND_SUBMERGE)",
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
    print(build(Path(sys.argv[1])))
