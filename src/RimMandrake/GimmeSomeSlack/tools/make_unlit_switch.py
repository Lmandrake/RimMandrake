#!/usr/bin/env python3
"""make_unlit_switch.py: the Futuristic power switch with its glow out, derived from the kept closed art.

    python3 src/RimMandrake/GimmeSomeSlack/tools/make_unlit_switch.py <out dir>

The Futuristic closed art (Styles/Futuristic/PowerSwitch*.png) carries a baked cyan glow, which stayed lit on a switch with
no power beside the dark lamp (polish, art judge 2026-11-20). This writes PowerSwitch_Unlit*.png, one per closed picture: the
same picture with every glowing cyan pixel turned to dark glass. Nothing else moves, so the kept art is not redrawn. The mod
draws the unlit picture over the switch only while its lamp is dark (SwitchLightDraw). Install with art.py install.
"""
import colorsys, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "Textures", "RimMandrake", "GimmeSomeSlack", "Styles", "Futuristic")


def unlit(im):
    im = im.convert("RGBA"); px = im.load(); n = 0
    hsv = {}
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a:
                hsv[x, y] = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    # the glow: strongly cyan pixels, and the pale core of the glow (near white, a cyan tint) within 2 pixels of one
    strong = {q for q, (h, s, v) in hsv.items() if 0.44 <= h <= 0.58 and s >= 0.35 and v >= 0.35}
    for (x, y), (h, s, v) in hsv.items():
        near = any((x + dx, y + dy) in strong for dx in range(-2, 3) for dy in range(-2, 3))
        if (x, y) in strong or (0.44 <= h <= 0.58 and s >= 0.22 and v >= 0.35):
            k = min(1.0, (s - 0.16) / 0.14)
        elif near and 0.40 <= h <= 0.62 and s >= 0.05 and v >= 0.55:
            k = 1.0
        else:
            continue
        r, g, b, a = px[x, y]
        r2, g2, b2 = colorsys.hsv_to_rgb(0.58, 0.12, 0.20 + 0.10 * v)     # dark glass keeps a little of its shading
        px[x, y] = (int(r * (1 - k) + 255 * r2 * k), int(g * (1 - k) + 255 * g2 * k), int(b * (1 - k) + 255 * b2 * k), a)
        n += 1
    return im, n


def main(out):
    os.makedirs(out, exist_ok=True)
    made = 0
    for f in sorted(os.listdir(SRC)):
        if not f.startswith("PowerSwitch") or "_Off" in f or "_Unlit" in f or not f.endswith(".png"):
            continue
        im, n = unlit(Image.open(os.path.join(SRC, f)))
        name = f.replace("PowerSwitch", "PowerSwitch_Unlit", 1)
        im.save(os.path.join(out, name)); made += 1
        print("%s: %d pixels put out -> %s" % (f, n, name))
    print("made %d" % made)
    return 0 if made else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
