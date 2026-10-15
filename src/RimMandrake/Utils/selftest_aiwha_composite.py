#!/usr/bin/env python3
"""Selftest for aiwha_composite.py: the geometry is what the canon check will measure."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aiwha_composite as ac  # noqa: E402

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def piece(w, h, pad=20):
    im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((pad, pad, pad + w - 1, pad + h - 1), fill=(90, 110, 100, 255))
    return im


def opaque_box(im):
    return im.getchannel("A").point(lambda a: 255 if a > ac.ALPHA_T else 0).getbbox()


# east: a 1400x120 wing blade and a 300x90 body
out, geo = ac.composite(piece(1400, 120), piece(300, 90), (768, 384), ratio=6.0, margin=8)
check(out.size == (768, 384), f"canvas {out.size}")
check(geo["wingspan_px"] == 752, f"span {geo['wingspan_px']} != 752")
check(abs(geo["body_len_px"] - 752 / 6) <= 1, f"body {geo['body_len_px']}")
check(abs(geo["ratio"] - 6.0) < 0.06, f"ratio {geo['ratio']}")
check(abs(geo["root"][0] - geo["shoulder"][0]) <= 1 and abs(geo["root"][1] - geo["shoulder"][1]) <= 1,
      f"shoulder {geo['shoulder']} not on root {geo['root']}")
b = opaque_box(out)
check(b[0] >= 7 and b[2] <= 761, f"opaque x {b} outside margin")
top, bot = b[1], 384 - b[3]
check(abs(top - bot) <= 2, f"not vertically centred: {top} vs {bot}")
check(out.getpixel(tuple(int(v) for v in geo["shoulder"]))[3] > 0, "shoulder pixel transparent")

# a body too big for the canvas height must refuse, not clip
try:
    ac.composite(piece(1400, 120), piece(100, 900), (768, 384), ratio=6.0)
    fails.append("oversize body did not refuse")
except ValueError:
    pass

# north: vertical body, head up; shoulder measured from the tail (bottom)
out, geo = ac.composite(piece(1400, 120), piece(90, 300), (768, 384), ratio=6.0, facing="north", head="up")
check(abs(geo["body_len_px"] - 752 / 6) <= 1, f"north body {geo['body_len_px']}")
bb = geo["body_box"]
frac_from_top = (geo["shoulder"][1] - bb[1]) / (bb[3] - bb[1])
check(abs(frac_from_top - 0.4) < 0.02, f"north shoulder at {frac_from_top:.2f} from top, want 0.40")

# wing squash narrows the chord, never the span
_, g1 = ac.composite(piece(1400, 120), piece(300, 90), (768, 384), ratio=6.0)
_, g2 = ac.composite(piece(1400, 120), piece(300, 90), (768, 384), ratio=6.0, wing_squash=0.5)
h1, h2 = g1["wing_box"][3] - g1["wing_box"][1], g2["wing_box"][3] - g2["wing_box"][1]
check(g2["wingspan_px"] == g1["wingspan_px"], "squash changed the span")
check(abs(h2 - h1 * 0.5) <= 2, f"squash chord {h2} vs {h1}")

# hue match rotates the wings onto the body's hue
def solid(w, h, rgb):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((0, 0, w - 1, h - 1), fill=rgb + (255,))
    return im
blue, green = solid(1400, 120, (60, 90, 160)), solid(300, 90, (70, 140, 60))
out, g = ac.composite(blue, green, (768, 384), ratio=6.0, match_hue=True)
wing_px = out.getpixel((g["wing_box"][0] + 40, (g["wing_box"][1] + g["wing_box"][3]) // 2))
hb, hw = ac.mean_hue(green), ac.mean_hue(solid(10, 10, wing_px[:3]))
check(abs(((hb - hw + 128) % 256) - 128) < 6, f"hue not matched: body {hb:.1f} wing {hw:.1f}")

print("selftest_aiwha_composite:", "FAIL" if fails else "PASS", *fails, sep="\n  " if fails else " ")
sys.exit(1 if fails else 0)
