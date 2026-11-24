#!/usr/bin/env python3
"""make_unlit_switch.py: the Futuristic power switch with its glow out, derived from the kept closed art.

    python3 src/RimMandrake/GimmeSomeSlack/tools/make_unlit_switch.py <out dir>

The Futuristic closed art (Styles/Futuristic/PowerSwitch*.png) carries a baked cyan glow, which stayed lit on a switch with
no power beside the dark lamp (polish, art judge 2026-11-20). This writes PowerSwitch_Unlit*.png, one per closed picture: the
same picture with every glowing cyan pixel turned to dark glass. Nothing else moves, so the kept art is not redrawn. The mod
draws the unlit picture over the switch only while its lamp is dark (SwitchLightDraw). Install with art.py install.
"""
import os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "Textures", "RimMandrake", "GimmeSomeSlack", "Styles", "Futuristic")


def cyan_excess(r, g, b):
    """How cyan a pixel is: its green and blue over its red. White, grey and steel casing read about 0 to 15; the glow, its pale
    core and its dim teal edge read 30 and up."""
    return min(g, b) - r


def unlit(im):
    im = im.convert("RGBA"); px = im.load(); n = 0
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            c = cyan_excess(r, g, b)
            if c < 18:
                continue                                              # casing: never touched
            k = min(1.0, (c - 18) / 14.0)                             # all glow from an excess of 32
            v = max(r, g, b) / 255.0
            d = int(255 * (0.17 + 0.10 * v))                          # dark glass keeps a little of its shading
            dr, dg, db = d - 4, d, d + 5                              # a cool grey, excess under 10
            px[x, y] = (int(r * (1 - k) + dr * k), int(g * (1 - k) + dg * k), int(b * (1 - k) + db * k), a)
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
