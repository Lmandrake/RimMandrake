"""fungalsoil_standin.py -- derive RUT_FungalSoil stack-count item art (FungalSoilTrade) from the Rot's owned
MycelialSoil terrain texture (FUNGAL_SOIL_RESCUE_RETIRED_MOD_ART).

Usage: python3 src/RimMandrake/Utils/art/fungalsoil_standin.py <MycelialSoil.png> <out_dir>
Writes RUT_FungalSoil_a/_b/_c.png (128x128 RGBA): one mound, two, and a heap. Deterministic (fixed seeds);
install the outputs with `art.py install FungalSoilTrade <rel> --file <png> --reason script:<this path>`.
"""
import math
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

SIZE = 128
SS = 4  # supersample


def mound_mask(cx, cy, rx, ry, seed):
    rnd = random.Random(seed)
    big = SIZE * SS
    m = Image.new("L", (big, big), 0)
    d = ImageDraw.Draw(m)
    pts = []
    harm = [(rnd.uniform(0, 6.28), rnd.uniform(0.03, 0.08), k) for k in (3, 5, 7)]
    for i in range(96):
        a = 2 * math.pi * i / 96
        r = 1.0 + sum(amp * math.sin(k * a + ph) for ph, amp, k in harm)
        # flatter base: squash the lower half a little
        yy = math.sin(a) * ry * r * (0.8 if math.sin(a) > 0 else 1.0)
        pts.append(((cx + math.cos(a) * rx * r) * SS, (cy + yy) * SS))
    d.polygon(pts, fill=255)
    return m.resize((SIZE, SIZE), Image.LANCZOS)


def shade(cx, cy, rx, ry):
    """Light from the upper left: bright top, dark base."""
    g = Image.new("L", (SIZE, SIZE))
    px = g.load()
    for y in range(SIZE):
        for x in range(SIZE):
            nx = (x - cx) / max(rx, 1)
            ny = (y - cy) / max(ry, 1)
            v = 1.0 - 0.55 * (ny + 0.35 * nx) - 0.25 * (nx * nx + ny * ny)
            px[x, y] = max(0, min(255, int(150 * v + 40)))
    return g


def build(src, mounds, seed):
    tex = src.convert("RGB").resize((256, 256), Image.LANCZOS)
    rnd = random.Random(seed)
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    for i, (cx, cy, rx, ry) in enumerate(sorted(mounds, key=lambda m: m[1])):
        ox, oy = rnd.randint(0, 127), rnd.randint(0, 127)
        patch = tex.crop((ox, oy, ox + SIZE, oy + SIZE))
        lit = ImageChops.multiply(patch, Image.merge("RGB", [shade(cx, cy, rx, ry)] * 3))
        lit = ImageChops.multiply(Image.eval(lit, lambda v: min(255, int(v * 1.6))), Image.new("RGB", (SIZE, SIZE), (150, 118, 96)))
        mask = mound_mask(cx, cy, rx, ry, seed * 31 + i)
        # dark rim: a slightly grown mask under the body
        rim = mask.filter(ImageFilter.MaxFilter(3))
        rim_layer = Image.new("RGBA", (SIZE, SIZE), (22, 16, 14, 255))
        canvas.paste(rim_layer, (0, 0), rim)
        body = lit.convert("RGBA")
        canvas.paste(body, (0, 0), mask)
    return canvas


def main():
    src = Image.open(sys.argv[1])
    out = sys.argv[2]
    sets = {
        "a": [(64, 72, 26, 18)],
        "b": [(50, 66, 22, 15), (78, 78, 24, 16)],
        "c": [(46, 58, 22, 15), (82, 60, 22, 15), (64, 82, 32, 20)],
    }
    for i, (k, m) in enumerate(sets.items()):
        build(src, m, 7 + i).save(f"{out}/RUT_FungalSoil_{k}.png")


if __name__ == "__main__":
    main()
