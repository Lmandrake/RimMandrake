#!/usr/bin/env python3
"""conform_sprite.py — fit generated art onto a reference's canvas and pose.

Image models do not respect canvas specifications. They do, however, draw the
subject at roughly the right proportions. Packaging is arithmetic, so it is
fixed here rather than argued about in the prompt.

Trims the candidate to its visible subject, scales it to match the reference's
subject extent, and registers it by **maximising mask overlap** rather than by
aligning bounding-box centres - damaged art is missing chunks, so its bbox
centre is not where the object actually sits.

    python conform_sprite.py --reference orig.png --input cut.png --out fit.png

Exit codes: 0 ok, 1 nothing usable in the input, 2 unusable arguments.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]
                       / "generating-images" / "scripts"))
import pnglib  # noqa: E402

# Alpha at or above this counts as subject when PASTING - keep it low so soft
# edges survive into the output.
ALPHA_FLOOR = 8

# ...but measure the bounding box at a higher floor. The box sets the scale
# factor, so a handful of near-invisible stray pixels at the frame edge would
# otherwise decide how big the sprite comes out. Measured on the first real
# smelter run: ~1,900 pixels at alpha 8-31 inflated the box by 20%, and the
# conformed sprite landed 20% undersized while passing every other check.
# At floor 32 and above the measured box was stable, so this sits at the knee.
BBOX_FLOOR = 32

# How far to hunt for the best alignment, as a fraction of canvas. The scale
# step already puts the subject close; this only mops up a few pixels of
# residual offset, and a wider search costs time without finding better fits.
SEARCH_FRACTION = 0.06

# Offsets are tried on this stride first, then refined by 1px around the best
# hit. Pure 1px search over the whole window is needlessly slow.
COARSE_STRIDE = 3


def mask_of(w: int, h: int, px: bytearray, floor: int = ALPHA_FLOOR) -> list[bool]:
    return [px[i * 4 + 3] >= floor for i in range(w * h)]


def bbox_of(w: int, h: int, mask: list[bool]):
    min_x, min_y, max_x, max_y = w, h, -1, -1
    for y in range(h):
        row = y * w
        for x in range(w):
            if mask[row + x]:
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y
    if max_x < 0:
        return None
    return min_x, min_y, max_x, max_y


def crop(w: int, h: int, px: bytearray, box) -> tuple[int, int, bytearray]:
    x0, y0, x1, y1 = box
    cw, ch = x1 - x0 + 1, y1 - y0 + 1
    out = bytearray(cw * ch * 4)
    for y in range(ch):
        src = ((y + y0) * w + x0) * 4
        dst = y * cw * 4
        out[dst:dst + cw * 4] = px[src:src + cw * 4]
    return cw, ch, out


def paste_rgba(cw: int, ch: int, canvas: bytearray,
               sw: int, sh: int, sprite: bytearray, ox: int, oy: int) -> None:
    for y in range(sh):
        ty = y + oy
        if not (0 <= ty < ch):
            continue
        for x in range(sw):
            tx = x + ox
            if not (0 <= tx < cw):
                continue
            s = (y * sw + x) * 4
            d = (ty * cw + tx) * 4
            canvas[d:d + 4] = sprite[s:s + 4]


def overlap_score(rw: int, rh: int, rmask: list[bool],
                  sw: int, sh: int, smask: list[bool], ox: int, oy: int) -> int:
    """Count of pixels where reference and candidate are both solid."""
    score = 0
    for y in range(sh):
        ty = y + oy
        if not (0 <= ty < rh):
            continue
        rrow = ty * rw
        srow = y * sw
        for x in range(sw):
            tx = x + ox
            if 0 <= tx < rw and smask[srow + x] and rmask[rrow + tx]:
                score += 1
    return score


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--reference", required=True)
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-register", action="store_true",
                    help="centre on the reference bbox instead of searching")
    args = ap.parse_args()

    for p in (args.reference, args.input):
        if not Path(p).is_file():
            print(f"ERROR no such file: {p}", file=sys.stderr)
            return 2

    rw, rh, rpx = pnglib.read_png(args.reference)
    cw0, ch0, cpx0 = pnglib.read_png(args.input)

    rmask = mask_of(rw, rh, rpx, BBOX_FLOOR)
    rbox = bbox_of(rw, rh, rmask)
    if rbox is None:
        print("ERROR the reference has no visible subject", file=sys.stderr)
        return 2

    cmask0 = mask_of(cw0, ch0, cpx0, BBOX_FLOOR)
    cbox = bbox_of(cw0, ch0, cmask0)
    if cbox is None:
        print("ERROR the input has no visible subject - did the key removal "
              "eat it?", file=sys.stderr)
        return 1

    # Trim to subject, then scale so the subject fills the same extent as the
    # reference's, preserving aspect so nothing is squashed.
    tw, th, tpx = crop(cw0, ch0, cpx0, cbox)
    ref_w = rbox[2] - rbox[0] + 1
    ref_h = rbox[3] - rbox[1] + 1
    scale = min(ref_w / tw, ref_h / th)
    nw, nh = max(1, round(tw * scale)), max(1, round(th * scale))
    spx = pnglib.resize_rgba(tw, th, tpx, nw, nh)
    smask = mask_of(nw, nh, spx, BBOX_FLOOR)

    # Start centred on the reference's bounding box.
    base_x = rbox[0] + (ref_w - nw) // 2
    base_y = rbox[1] + (ref_h - nh) // 2

    best = (base_x, base_y)
    if not args.no_register:
        span = int(max(rw, rh) * SEARCH_FRACTION)
        best_score = -1
        for dy in range(-span, span + 1, COARSE_STRIDE):
            for dx in range(-span, span + 1, COARSE_STRIDE):
                s = overlap_score(rw, rh, rmask, nw, nh, smask,
                                  base_x + dx, base_y + dy)
                if s > best_score:
                    best_score, best = s, (base_x + dx, base_y + dy)
        # refine by 1px around the coarse winner
        cx, cy = best
        for dy in range(-COARSE_STRIDE, COARSE_STRIDE + 1):
            for dx in range(-COARSE_STRIDE, COARSE_STRIDE + 1):
                s = overlap_score(rw, rh, rmask, nw, nh, smask, cx + dx, cy + dy)
                if s > best_score:
                    best_score, best = s, (cx + dx, cy + dy)

    canvas = bytearray(rw * rh * 4)
    paste_rgba(rw, rh, canvas, nw, nh, spx, best[0], best[1])

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    pnglib.write_rgba(args.out, rw, rh, canvas)

    visible = sum(1 for i in range(3, len(canvas), 4) if canvas[i] >= ALPHA_FLOOR)
    ref_visible = sum(1 for m in rmask if m)
    print(f"reference {rw}x{rh}, subject {ref_w}x{ref_h}")
    print(f"input     {cw0}x{ch0}, subject {tw}x{th} -> scaled {nw}x{nh} "
          f"({scale:.3f}x)")
    print(f"placed at {best}, coverage {visible/(rw*rh):.1%} "
          f"(reference {ref_visible/(rw*rh):.1%})")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
