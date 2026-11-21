#!/usr/bin/env python3
"""The switch lamp (bar switch_light_reads_state) composed on every Gimme Some Slack switch look, offline, for the art judge.

The lamp's pixels come from the mod's own Core/SwitchLampArt.cs through the SelfTest (`selftest_gimmesomeslack.py --no-export
--switchlamp-dump <dir>`), so this sheet shows the bytes the game draws, placed and sized by the same constants (lamp.json).
Each look's art (closed art with the closed states, open art with the open states) is drawn on a sand floor at three zooms
(px per cell); the halo is added (additive, as ShaderDatabase.MoteGlow draws it) under the lens, the lens alpha-blended on top.
Not covered: vanilla's own switch art (its texture is inside the game's asset bundles; the live row sc_switch_light shows it).

    python3 src/RimMandrake/GimmeSomeSlack/tools/switch_lamp_mock.py <pixel dir> <out.png>
"""
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(HERE, "Textures", "RimMandrake", "GimmeSomeSlack")
LOOKS = [("Scrapper", ""), ("Industrial", "Styles/Industrial/"), ("Modern", "Styles/Modern/"), ("Futuristic", "Styles/Futuristic/")]
# (art state, lamp state, caption)
CASES = [("", "Green", "closed, powered: GREEN"), ("", "Dark", "closed, unpowered: dark"),
         ("_Off", "Red", "open, powered: RED"), ("_Off", "Dark", "open, unpowered: dark")]
ZOOMS = [36, 56, 112]
SAND = (196, 170, 128, 255)


def rgba(path, px):
    im = Image.frombytes("RGBA", (px, px), open(path, "rb").read())
    return im.transpose(Image.FLIP_TOP_BOTTOM)          # Unity rows run bottom-up


def tile(look_dir, art, lamp, cell, px, meta, pix):
    can = Image.new("RGBA", (cell * 2, cell * 2), SAND)
    sw = Image.open(os.path.join(TEX, look_dir + "PowerSwitch" + art + ".png")).convert("RGBA").resize((cell, cell), Image.LANCZOS)
    o = cell // 2
    can.alpha_composite(sw, (o, o))
    cx, cz = o + cell / 2 + meta["offX"] * cell, o + cell / 2 - meta["offZ"] * cell
    hp = os.path.join(pix, "halo_%s.rgba" % lamp)
    if os.path.exists(hp):
        s = max(1, round(meta["halo"] * cell))
        h = rgba(hp, px).resize((s, s), Image.BILINEAR)
        a = h.split()[3]
        add = Image.merge("RGB", [ImageChops.multiply(c, a) for c in h.convert("RGB").split()])
        base = can.convert("RGB")
        box = (round(cx - s / 2), round(cz - s / 2))
        region = base.crop((box[0], box[1], box[0] + s, box[1] + s))
        base.paste(ImageChops.add(region, add), box)
        can = base.convert("RGBA")
    s = max(1, round(meta["lens"] * cell))
    lens = rgba(os.path.join(pix, "lens_%s.rgba" % lamp), px).resize((s, s), Image.LANCZOS)
    can.alpha_composite(lens, (round(cx - s / 2), round(cz - s / 2)))
    if "Industrial" in look_dir and art == "":   # the unlit cap over the Industrial closed art's baked LED (SwitchLightDraw.CapsBakedLed)
        s = max(1, round(meta["ledCap"] * cell))
        cap = rgba(os.path.join(pix, "lens_Dark.rgba"), px).resize((s, s), Image.LANCZOS)
        lx, lz = o + cell / 2 + meta["ledX"] * cell, o + cell / 2 - meta["ledZ"] * cell
        can.alpha_composite(cap, (round(lx - s / 2), round(lz - s / 2)))
    return can


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    pix, out = argv
    meta = json.load(open(os.path.join(pix, "lamp.json")))
    px = meta["px"]
    rows = []
    for name, d in LOOKS:
        for cell in ZOOMS:
            tiles = [tile(d, art, lamp, cell, px, meta, pix) for art, lamp, _ in CASES]
            rows.append((name, cell, tiles))
    pad, lab = 8, 150
    w = lab + sum(t.width for t in rows[-1][2]) + pad * (len(CASES) + 1)
    hs = [max(t.height for t in r[2]) + pad for r in rows]
    sheet = Image.new("RGBA", (w, 30 + sum(hs)), (40, 40, 40, 255))
    dr = ImageDraw.Draw(sheet)
    x = lab + pad
    big = rows[-1][2][0].width
    for _, _, cap in CASES:
        dr.text((x, 8), cap, fill=(240, 240, 240, 255))
        x += big + pad
    y = 30
    for (name, cell, tiles), h in zip(rows, hs):
        dr.text((8, y + 6), "%s\n%d px per cell" % (name, cell), fill=(240, 240, 240, 255))
        x = lab + pad
        for t in tiles:
            sheet.alpha_composite(t, (x, y))
            x += big + pad
        y += h
    sheet.save(out)
    print("SHEET %s (%d looks x %d zooms x %d states)" % (out, len(LOOKS), len(ZOOMS), len(CASES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
