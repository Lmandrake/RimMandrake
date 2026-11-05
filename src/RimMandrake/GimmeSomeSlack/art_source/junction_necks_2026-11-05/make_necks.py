#!/usr/bin/env python3
"""GSS_JUNCTION_REDRAW_BODY_WIDER_THAN_CORD: compact Modern (ExtCord) and Futuristic (Cybertek) T/X junctions.

The shipped boxes (orig/, copied before this change) span the whole 128 px canvas, drawn 1.15 cells wide
(CordBuilder.JunctionScale), with sleeves 18-26 px thick = 0.16-0.23 cells against a 0.08-cell strand. This
shrinks each box (housing + sleeves, the painted art unchanged) by SCALE about its arm-meeting point
(CordBuilder.TapeAnchorZ: the T's arms meet 0.152 canvas above centre, the X's at the centre) and paints a
cable neck from each shrunken sleeve out to the original port tip, cut from the style's own strand texture:
the whole strand texture squeezed so its painted band is NECK_PAINT px (0.076 cell; judge note 2026-11-05: a neck cut
from the opaque band alone stood visibly wider than the cord). Port positions and directions do not move.

    python3 make_necks.py --out <dir inside the clone>    then, per PNG, `art.py install GimmeSomeSlack
    Textures/RimMandrake/GimmeSomeSlack/Styles/<folder>/<slot>.png --file <dir>/<folder>/<slot>.png --reason script:<this>`
    (art goes through the art ledger only; never write the Textures tree directly)
Proof: ../../selftest_gss_junction_necks.py
"""
import argparse
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
STYLES = os.path.normpath(os.path.join(HERE, "..", "..", "Textures", "RimMandrake", "GimmeSomeSlack", "Styles"))
SCALE = 0.62
NECK_PAINT = 8.5  # painted neck width, px: 0.076 cells, inside +-20% of the 0.08 strand
SS = 4  # necks are laid at 4x and downsampled, so width and centre are not rounded to whole pixels
OVERLAP = 4  # neck runs this far under the sleeve so no gap shows
ARM = 64.0   # every arm tip lies 64 px from the meeting point (measured on the shipped art)

# (folder, strand texture) -- the root ExtCord junction is the orange one (ConduitStyles.Colours[0])
SETS = [("ExtCord", "ExtCord/Strand_Orange"), ("ExtCord/Blue", "ExtCord/Strand_Blue"),
        ("ExtCord/Brown", "ExtCord/Strand_Brown"), ("ExtCord/Green", "ExtCord/Strand_Green"),
        ("ExtCord/Yellow", "ExtCord/Strand_Yellow"), ("Cybertek", "Cybertek/Strand")]
# meeting point (image px, x right / y down) and arm directions (dx, dy) per slot
SLOTS = {"Junction_T": ((63.5, 44.5), [(-1, 0), (1, 0), (0, 1)]),
         "Junction_X": ((63.5, 63.5), [(-1, 0), (1, 0), (0, -1), (0, 1)])}


def strand_strip(path, length):
    """A horizontal piece of the strand texture drawn as the game draws the cord: the whole texture (transparent
    margins included) squeezed to the quad height that paints NECK_PAINT px, at SS x resolution."""
    s = Image.open(path).convert("RGBA")
    a = s.getchannel("A")
    band = [y for y in range(s.height) if a.crop((0, y, s.width, y + 1)).getextrema()[1] > 40]
    # the quad height that paints NECK_PAINT px of this strand's band (Brown paints 24 of 32 rows, Green 30)
    quad = round(NECK_PAINT * s.height / len(band) * SS)
    n = length // s.width + 1
    long_ = Image.new("RGBA", (s.width * n, s.height))
    for i in range(n):
        long_.paste(s, (i * s.width, 0))
    return long_.crop((0, 0, length, s.height)).resize((length * SS, quad), Image.LANCZOS)


def make(orig_png, strand_png, slot):
    src = Image.open(orig_png).convert("RGBA")
    (mx, my), arms = SLOTS[slot]
    W = src.width
    cx, cy = mx + 0.5, my + 0.5  # the meeting point in pixel-edge coordinates
    body = src.resize((round(W * SCALE), round(W * SCALE)), Image.LANCZOS)
    necks = Image.new("RGBA", (W * SS, W * SS), (0, 0, 0, 0))
    inner = ARM * SCALE - OVERLAP  # neck start, from the meeting point
    length = int(round(ARM - inner)) + 1
    for dx, dy in arms:
        strip = strand_strip(strand_png, length)  # runs +x from its left end
        hw = strip.height / 2
        if dx == 1:
            piece, ox, oy = strip, (cx + inner) * SS, cy * SS - hw
        elif dx == -1:
            piece, ox, oy = strip.transpose(Image.FLIP_LEFT_RIGHT), (cx - inner) * SS - strip.width, cy * SS - hw
        elif dy == 1:
            piece, ox, oy = strip.transpose(Image.ROTATE_270), cx * SS - hw, (cy + inner) * SS
        else:
            piece, ox, oy = strip.transpose(Image.ROTATE_90), cx * SS - hw, (cy - inner) * SS - strip.width
        necks.alpha_composite(piece, (int(round(ox)), int(round(oy))))
    out = necks.resize((W, W), Image.LANCZOS)
    # nothing past the shipped arm tips (ARM px from the meeting point)
    clip = Image.new("L", (W, W), 0)
    for dx, dy in arms:
        x0 = cx - 8 if dx == 0 else (cx if dx == 1 else cx - ARM)
        x1 = cx + 8 if dx == 0 else (cx + ARM if dx == 1 else cx)
        y0 = cy - 8 if dy == 0 else (cy if dy == 1 else cy - ARM)
        y1 = cy + 8 if dy == 0 else (cy + ARM if dy == 1 else cy)
        clip.paste(255, (int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))))
    out.putalpha(Image.composite(out.getchannel("A"), Image.new("L", (W, W), 0), clip))
    # the shrunken box over the necks, its meeting point kept where it was
    out.alpha_composite(body, (int(round(cx - cx * SCALE)), int(round(cy - cy * SCALE))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    for folder, strand in SETS:
        for slot in SLOTS:
            orig = os.path.join(HERE, "orig", folder.replace("/", "_") + "_" + slot + ".png")
            dst = os.path.join(a.out, folder, slot + ".png")
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            make(orig, os.path.join(STYLES, strand + ".png"), slot).save(dst)
            print("wrote", dst)


if __name__ == "__main__":
    main()
