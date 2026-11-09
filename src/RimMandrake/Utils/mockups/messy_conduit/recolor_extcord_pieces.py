"""recolor_extcord_pieces.py -- extension-cord connection pieces in every cord colour (owner review 2026-10-04, B14).

    python3 src/RimMandrake/Utils/mockups/messy_conduit/recolor_extcord_pieces.py           # write the variants
    python3 src/RimMandrake/Utils/mockups/messy_conduit/recolor_extcord_pieces.py --check   # exit 1 if any is stale/wrong

Owner, 2026-10-04: *"When I selected "brown everywhere" the T junction boxes still show orange connections going into
the brown as well as the lightbulb connectors"*. The shipped Styles/ExtCord pieces (Plug, Junction_T, Junction_X,
StubWall, StubRock, EndFrayed_Dead) carry ORANGE cord stubs. This writes Styles/ExtCord/<Colour>/<slot>.png for the
other four cord colours: every orange cord pixel (hue 8-45 deg, saturation >= 0.45) takes the colour's hue, its
saturation and value scaled by the colour strand's mean over the orange strand's mean; every other pixel (the
beige box, the screws, the socket) is left untouched, and alpha is copied exactly. CordMaterials picks the variant
matching each net's strand. Derived art: re-run after the source pieces change (--check says when). The necked T and X junctions are not derived here (NECKED).
"""
import colorsys
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
EXT = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack", "Textures", "RimMandrake", "GimmeSomeSlack", "Styles", "ExtCord")
SLOTS = ["Plug", "Junction_T", "Junction_X", "StubWall", "StubRock", "EndFrayed_Dead"]
COLOURS = ["Green", "Brown", "Yellow", "Blue"]


def is_orange(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    return 8 / 360.0 <= h <= 45 / 360.0 and s >= 0.45 and v >= 0.12


def mean_hsv(path):
    im = Image.open(path).convert("RGBA")
    px = [p for p in im.getdata() if p[3] > 128]
    r, g, b = (sum(p[i] for p in px) / len(px) for i in range(3))
    return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)


def recolor(src, colour):
    oh, os_, ov = mean_hsv(os.path.join(EXT, "Strand_Orange.png"))
    th, ts, tv = mean_hsv(os.path.join(EXT, "Strand_%s.png" % colour))
    im = Image.open(src).convert("RGBA")
    out = im.copy()
    a, b = im.load(), out.load()
    changed = 0
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, bl, al = a[x, y]
            if al == 0 or not is_orange(r, g, bl):
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, bl / 255.0)
            s2 = min(1.0, s * ts / max(os_, 1e-6))
            v2 = min(1.0, v * tv / max(ov, 1e-6))
            nr, ng, nb = colorsys.hsv_to_rgb(th, s2, v2)
            b[x, y] = (int(round(nr * 255)), int(round(ng * 255)), int(round(nb * 255)), al)
            changed += 1
    return out, changed


def orange_left(im):
    return sum(1 for p in im.getdata() if p[3] > 128 and is_orange(*p[:3]))


# GSS_RECOLOR_CHECK_FIX_NECKED_JUNCTIONS: these variants are judged art. art_source/junction_necks_2026-11-05/make_necks.py necked each one from
# its OWN colour's strand, so they equal no recolour of the orange base and this writer must never overwrite them. What B14 owes
# for them is: the cord pixels are not the base's orange, and the same shape as the base (a variant from before the necks differs by far more).
NECKED = ("Junction_T", "Junction_X")
NECKED_SHAPE_SLACK = 0.03


def necked_ok(dst, base):
    if not os.path.exists(dst):
        return False
    a, b = Image.open(dst).convert("RGBA"), Image.open(base).convert("RGBA")
    if a.size != b.size:
        return False
    pairs = list(zip(a.getdata(), b.getdata()))
    off = sum(1 for p, q in pairs if abs(p[3] - q[3]) > 24)
    # Brown and Yellow lie inside the orange hue band, so "no orange" cannot read them: the variant must not be the base's own
    # cord pixels (validation.py B14 reads its hue against the strand's)
    recoloured = sum(1 for p, q in pairs if p[3] > 128 and q[3] > 128 and is_orange(*q[:3]) and p[:3] != q[:3])
    return off <= NECKED_SHAPE_SLACK * a.width * a.height and recoloured >= 100


def main(argv):
    check = "--check" in argv
    bad = 0
    for c in COLOURS:
        os.makedirs(os.path.join(EXT, c), exist_ok=True)
        for s in SLOTS:
            dst = os.path.join(EXT, c, s + ".png")
            if s in NECKED:
                if check and not necked_ok(dst, os.path.join(EXT, s + ".png")):
                    bad += 1
                    print("STALE %s/%s" % (c, s))
                continue
            want, n = recolor(os.path.join(EXT, s + ".png"), c)
            if check:
                ok = os.path.exists(dst) and list(Image.open(dst).convert("RGBA").getdata()) == list(want.getdata())
                if not ok:
                    bad += 1
                    print("STALE %s/%s" % (c, s))
                continue
            want.save(dst)
            print("%s/%s: %d cord pixels recoloured, %d orange left" % (c, s, n, orange_left(want)))
    if check:
        print("extcord piece variants: %d stale of %d" % (bad, len(COLOURS) * len(SLOTS)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
