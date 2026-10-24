#!/usr/bin/env python3
"""SPRINKLER_SEAT_FIX_HEAD_BESIDE_ELBOW: the squat sprinkler heads, recomposed from the shipped tall heads.

Owner 2026-10-24: "We likely need to make the sprinkler object be shorter, squatter, and wider so that it looks ok over
any pipe. We need to test it on N/S pipes, E/W pipes, and corner bend pipes."

The tall head (2026-10-21 line_joins art) is a dome on a long stem over a saddle. Each look is cut, by its own alpha width
profile, into those three parts, and recomposed:
  * the dome, widened and flattened (DOME_W x DOME_H);
  * a short neck: the middle NECK_KEEP of the stem (it carries the look's band: hazard stripes, cyan ring), widened;
  * the saddle, widened and flattened into a low clamp that straddles the pipe (SAD_W x SAD_H).
Drawn back-to-front saddle, neck, dome, each overlapping the one below by OVERLAP px so no gap opens.
The result is placed with the seat (where the pipe axis must pass: SEAT_IN_CLAMP down the clamp) at SEAT_Y on a 256 px canvas,
x-centred, so ONE drawOffset z = (SEAT_Y - 128) / 256 serves every look.

Usage: squat_heads.py [--src DIR] [--out DIR]   (default: raw/ in, out/ out)
Writes <out>/<Look>/RM_SprinklerHead.png and <out>/seat.json (seat_y, bbox and part rows per look; a record for a human,
nothing reads it). The installed textures must equal squat(raw/<Look>) pixel for pixel: selftest_fw_offline_art.py
asserts it, which is what makes the Defs' one drawOffset z = (SEAT_Y - 128)/256 true of the shipped art.
"""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
TEX = HERE / "raw"   # the tall 2026-10-21 heads, kept as the source (the shipped textures become the output)
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")

TARGET_W = 92      # px of 256 the clamp spans: 0.36 cell, over 2.5 bore widths (bore 0.136 cell)
DOME_W, DOME_H = 0.95, 0.70  # dome scale relative to the clamp-normalised scale
NECK_KEEP = 0.30   # fraction of the stem's height kept (its middle)
SAD_W, SAD_H = 1.0, 0.62
OVERLAP = 4
SEAT_Y = 140       # canvas row the seat (the pipe axis) lands on
SEAT_IN_CLAMP = 0.3  # the seat's height in the clamp from its top: the clamp's front lip hangs just past the pipe's near rim
ALPHA = 40


def _first(rows, what):
    y = next(rows, None)
    if y is None:
        raise ValueError("squat_heads: no %s row in this head's alpha width profile" % what)
    return y


def parts(im):
    """Rows of (dome, stem, saddle) by the alpha width profile: the dome ends at the first row after its widest that is
    narrower than 60 % of it; the saddle starts where the width climbs past halfway from the stem's narrowest row to the
    saddle's widest (a banded stem, Industrial's stripes, stays stem)."""
    a = np.array(im)[:, :, 3] > ALPHA
    w = a.sum(1)
    rows = np.nonzero(w)[0]
    top, bot = int(rows[0]), int(rows[-1])
    mid = (top + bot) // 2
    dmax = top + int(np.argmax(w[top:mid + 1]))
    dome_end = _first((y for y in range(dmax, bot) if w[y] < 0.6 * w[dmax]), "dome end (60 % of the widest)")
    half = dome_end + (bot - dome_end) // 2
    neck = dome_end + int(np.argmin(w[dome_end:half + 1]))        # the stem's narrowest row
    cut = (w[neck] + w[half:bot + 1].max()) / 2                   # halfway to the saddle's widest
    sad_start = _first((y for y in range(neck, bot) if w[y] > cut and w[y + 1] > cut), "saddle start")
    return top, dome_end, sad_start, bot + 1


def crop_rows(im, y0, y1):
    c = im.crop((0, y0, im.width, y1))
    bb = c.getchannel("A").point(lambda v: 255 if v > ALPHA else 0).getbbox()
    if bb is None:
        raise ValueError("squat_heads: rows %d-%d hold no opaque pixel" % (y0, y1))
    return c.crop((bb[0], 0, bb[2], c.height))


def scaled(im, sx, sy):
    return im.resize((max(1, round(im.width * sx)), max(1, round(im.height * sy))), Image.LANCZOS)


def squat(im):
    top, dome_end, sad_start, bot = parts(im)
    dome = crop_rows(im, top, dome_end)
    stem = crop_rows(im, dome_end, sad_start)
    saddle = crop_rows(im, sad_start, bot)
    k = TARGET_W / saddle.width / SAD_W            # one scale so the clamp spans TARGET_W
    sad = scaled(saddle, k * SAD_W, k * SAD_H)
    s0 = round(stem.height * (1 - NECK_KEEP) / 2)
    neck = stem.crop((0, s0, stem.width, max(s0 + 1, s0 + round(stem.height * NECK_KEEP))))
    neck = scaled(neck, k * 1.15, k * 0.8)
    dome = scaled(dome, k * DOME_W * 1.15, k * DOME_H * 1.15)
    cv = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    sad_y = SEAT_Y - round(sad.height * SEAT_IN_CLAMP)
    neck_y = sad_y - neck.height + OVERLAP
    dome_y = neck_y - dome.height + OVERLAP
    for part, y in ((sad, sad_y), (neck, neck_y), (dome, dome_y)):
        cv.alpha_composite(part, (128 - part.width // 2, y))
    return cv, {"seat_y": SEAT_Y, "bbox": cv.getchannel("A").point(lambda v: 255 if v > ALPHA else 0).getbbox(),
                "parts_rows": [top, dome_end, sad_start, bot]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--src", default=str(TEX))
    ap.add_argument("--out", default=str(HERE / "out"))
    a = ap.parse_args(argv)
    seat = {}
    for look in LOOKS:
        im = Image.open(Path(a.src) / look / "RM_SprinklerHead.png").convert("RGBA")
        out, info = squat(im)
        d = Path(a.out) / look
        d.mkdir(parents=True, exist_ok=True)
        out.save(d / "RM_SprinklerHead.png")
        seat[look] = info
        print(look, info)
    (Path(a.out) / "seat.json").write_text(json.dumps(seat, indent=1))


if __name__ == "__main__":
    main()
