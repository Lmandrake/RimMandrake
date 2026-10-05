"""round7_reel_fix.py -- MessyConduit art round 7: Scrapper laid reel inlet points DOWN.

Owner (2026-10-04, r7 shot 20261004223832_1): "The junk-built reel (when deployed) shows an open
connector pointed at the camera rather than it pointing down and plugged in like the others."

Hand edit of the round-6 picture (canvas/anchor unchanged):
  1. the open brass socket on the drum face is painted out with drum pixels cloned from the
     same rows either side (rust noise hides the seam);
  2. a rusty junk inlet stub is drawn from the drum's centre bottom DOWN into the base bar,
     like the Industrial/Modern/Futuristic laid reels: welded collar at the drum, wire
     lashing, a bodged clamp band, plugged into the frame.

    python3 src/RimMandrake/Utils/mockups/messy_conduit/round7_reel_fix.py <src.png> <out.png>
Install goes through `art install` only (see Transient/mc_art_round7_report.md).
"""
import random
import sys

from PIL import Image

HOLE = (142, 108, 176, 146)          # x0, y0, x1, y1 of the socket + its shadow ring
CX = 159                             # drum centre x (code aims the hose here)
PIPE_TOP, PIPE_BOT = 153, 185        # drum lower edge -> into the base bar
R = 7                                # pipe half-width

OUTLINE = (28, 18, 12, 255)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


def main(src, out):
    im = Image.open(src).convert("RGBA")
    px = im.load()
    rnd = random.Random(7)

    # 1. paint out the socket: left half from 18 px left, right half from 20 px right, cross-fade.
    x0, y0, x1, y1 = HOLE
    mid = (x0 + x1) / 2
    orig = im.copy().load()
    for y in range(y0, y1):
        for x in range(x0, x1):
            a = orig[x - 18, y]
            b = orig[x + 20, y]
            t = min(1, max(0, (x - (mid - 6)) / 12))
            c = lerp(a, b, t)
            # soft edge into the untouched drum
            e = min(x - x0, x1 - 1 - x, y - y0, y1 - 1 - y)
            if e < 3:
                c = lerp(orig[x, y], c, (e + 1) / 4)
            px[x, y] = c[:3] + (255,)

    # 2. inlet stub: cylinder shading with sampled rust tones.
    dark, mid_c, lite = (58, 30, 18), (122, 62, 34), (176, 104, 62)
    for y in range(PIPE_TOP, PIPE_BOT):
        for x in range(CX - R - 1, CX + R + 2):
            d = (x - CX) / (R + 0.5)
            if abs(x - CX) > R:
                px[x, y] = OUTLINE
                continue
            s = 1 - abs(d + 0.35)                       # light from upper-left
            c = lerp(dark, mid_c, min(1, s * 1.6)) if s < 0.62 else lerp(mid_c, lite, (s - 0.62) / 0.38)
            n = rnd.randint(-12, 12)
            if rnd.random() < 0.08:                     # rust pitting
                n -= 30
            px[x, y] = tuple(max(0, min(255, v + n)) for v in c) + (255,)

    def band(yc, h, col, hi, w):
        for y in range(yc, yc + h):
            for x in range(CX - w - 1, CX + w + 2):
                if abs(x - CX) > w or y in (yc, yc + h - 1):
                    px[x, y] = OUTLINE
                else:
                    t = 1 - abs((x - CX) / (w + 0.5) + 0.35)
                    px[x, y] = lerp(col, hi, max(0, t)) + (255,)

    band(PIPE_TOP - 2, 6, (70, 52, 40), (150, 130, 110), R + 3)       # welded collar at drum
    band(PIPE_TOP + 9, 4, (110, 84, 40), (196, 160, 90), R + 1)        # brass wire lashing
    band(PIPE_TOP + 14, 3, (110, 84, 40), (196, 160, 90), R + 1)
    band(PIPE_BOT - 9, 5, (78, 84, 80), (150, 160, 150), R + 2)        # bodged grey clamp band
    # clamp bolt
    for (x, y) in ((CX + R + 3, PIPE_BOT - 8), (CX + R + 3, PIPE_BOT - 7)):
        px[x, y] = (40, 36, 30, 255)
    # weld bead dots under the collar
    for x in range(CX - R, CX + R + 1, 2):
        px[x, PIPE_TOP + 4] = (196, 150, 110, 255)
    im.save(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
