"""Writes the two procedural textures of the round 7 water look (RIMMANDRAKE_PROVE_UNDER_LIQUID_LAW_LIVE):

- Things/Building/RM_SunkVent.png: a soft dark hole, no pale ring, clear corners. A vent under liquid prints it under the
  liquid's sheet instead of vanilla's geyser art (RM_SubmergeDraw.SunkVentMat).
- Things/Mote/RM_VentFroth.png: a soft white ring of froth, speckled inside (RM_Fleck_VentFroth).

    python3 round7_vent_art.py <out_dir>     writes both under <out_dir>/Things/...; install with art.py install --file
Deterministic (seeded). The census (selftest_flowworks_pit_draw_census.py, sunk_vent_art) pins the hole's look.
"""
import math
import os
import random
import sys

from PIL import Image

N = 128


def smooth(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def vent():
    im = Image.new("RGBA", (N, N))
    px = im.load()
    for y in range(N):
        for x in range(N):
            r = math.hypot(x + 0.5 - N / 2, y + 0.5 - N / 2) / (N / 2)
            a = 0.95 * (1 - smooth(0.18, 1.0, r)) ** 1.6
            k = smooth(0.0, 0.9, r)
            c = (0.05 + 0.09 * k, 0.045 + 0.08 * k, 0.04 + 0.07 * k)
            px[x, y] = tuple(int(round(v * 255)) for v in c) + (int(round(a * 255)),)
    return im


def froth():
    random.seed(7)
    im = Image.new("RGBA", (N, N))
    px = im.load()
    for y in range(N):
        for x in range(N):
            r = math.hypot(x + 0.5 - N / 2, y + 0.5 - N / 2) / (N / 2)
            ring = 0.62 * math.exp(-((r - 0.72) / 0.13) ** 2)
            fill = 0.22 * (1 - smooth(0.55, 0.8, r)) * (0.55 + 0.45 * random.random())
            a = min(1.0, ring + fill) * (1 - smooth(0.92, 1.0, r))
            px[x, y] = (255, 255, 255, int(round(a * 255)))
    return im


def main(out):
    for rel, im in (("Things/Building/RM_SunkVent.png", vent()), ("Things/Mote/RM_VentFroth.png", froth())):
        p = os.path.join(out, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        im.save(p)
        print(p)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
