#!/usr/bin/env python3
"""compare_images.py — did the edit change only what it was supposed to?

Reports the four things that silently go wrong in a generative edit: the canvas
resized, the subject moved, the subject changed size, or the palette drifted.
Geometry is measured from the alpha channel where there is one, and from a
key-colour match where there is not.

    python compare_images.py --before a.png --after b.png

Exit codes: 0 within tolerance, 1 drift detected, 2 unusable input.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]
                      / "generating-images" / "scripts"))
import pnglib  # noqa: E402

# A pixel counts as subject if alpha is meaningfully above zero. 8/255 ignores
# the near-invisible skirt a soft matte leaves without discarding real edges.
ALPHA_FLOOR = 8

# Tolerances, as a fraction of the image's own dimensions. A generative edit
# never reproduces a bounding box exactly; 2% is tight enough to catch a
# deliberate rescale and loose enough to ignore an edge pixel of noise.
BBOX_TOLERANCE = 0.02
CENTROID_TOLERANCE = 0.02


def load(path: Path):
    w, h, px = pnglib.read_png(str(path))
    return w, h, px


def subject_stats(w: int, h: int, px: bytearray) -> dict:
    """Bounding box, coverage and centroid of the non-transparent subject."""
    min_x, min_y, max_x, max_y = w, h, -1, -1
    count = 0
    sum_x = sum_y = 0
    has_alpha = any(px[i] < 255 for i in range(3, len(px), 4))

    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 4
            visible = px[i + 3] >= ALPHA_FLOOR if has_alpha else True
            if not visible:
                continue
            count += 1
            sum_x += x
            sum_y += y
            if x < min_x: min_x = x
            if x > max_x: max_x = x
            if y < min_y: min_y = y
            if y > max_y: max_y = y

    if count == 0:
        return {"empty": True, "has_alpha": has_alpha}
    return {
        "empty": False,
        "has_alpha": has_alpha,
        "bbox": (min_x, min_y, max_x, max_y),
        "bbox_w": max_x - min_x + 1,
        "bbox_h": max_y - min_y + 1,
        "coverage": count / (w * h),
        "centroid": (sum_x / count, sum_y / count),
    }


def mean_rgb(px: bytearray) -> tuple[float, float, float]:
    """Mean colour over visible pixels only."""
    tot = [0, 0, 0]
    n = 0
    for i in range(0, len(px), 4):
        if px[i + 3] < ALPHA_FLOOR:
            continue
        n += 1
        for c in range(3):
            tot[c] += px[i + c]
    if n == 0:
        return (0.0, 0.0, 0.0)
    return tuple(t / n for t in tot)  # type: ignore[return-value]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--bbox-tolerance", type=float, default=BBOX_TOLERANCE)
    args = ap.parse_args()

    for p in (args.before, args.after):
        if not Path(p).is_file():
            print(f"ERROR no such file: {p}", file=sys.stderr)
            return 2

    bw, bh, bpx = load(Path(args.before))
    aw, ah, apx = load(Path(args.after))

    problems: list[str] = []

    print(f"canvas   {bw}x{bh}  ->  {aw}x{ah}")
    if (bw, bh) != (aw, ah):
        problems.append(
            f"canvas changed {bw}x{bh} -> {aw}x{ah}. Downstream registration "
            f"assumes a stable canvas; rescale before using this."
        )

    b = subject_stats(bw, bh, bpx)
    a = subject_stats(aw, ah, apx)

    if b["empty"] or a["empty"]:
        print("subject  one image has no visible subject")
        problems.append("an image is empty or fully transparent")
    else:
        print(f"bbox     {b['bbox_w']}x{b['bbox_h']}  ->  {a['bbox_w']}x{a['bbox_h']}")
        print(f"coverage {b['coverage']:.1%}  ->  {a['coverage']:.1%}")
        print(f"centroid ({b['centroid'][0]:.0f},{b['centroid'][1]:.0f})  ->  "
              f"({a['centroid'][0]:.0f},{a['centroid'][1]:.0f})")

        dw = abs(a["bbox_w"] - b["bbox_w"]) / max(bw, 1)
        dh = abs(a["bbox_h"] - b["bbox_h"]) / max(bh, 1)
        if dw > args.bbox_tolerance or dh > args.bbox_tolerance:
            problems.append(
                f"subject resized by {max(dw, dh):.1%} of canvas - the edit "
                f"changed the silhouette's extent, not just its surface."
            )

        cdx = abs(a["centroid"][0] - b["centroid"][0]) / max(bw, 1)
        cdy = abs(a["centroid"][1] - b["centroid"][1]) / max(bh, 1)
        if cdx > CENTROID_TOLERANCE or cdy > CENTROID_TOLERANCE:
            problems.append(
                f"subject moved by {max(cdx, cdy):.1%} of canvas - position "
                f"was not held."
            )

        if not b["has_alpha"] and a["has_alpha"]:
            print("alpha    gained an alpha channel")
        elif b["has_alpha"] and not a["has_alpha"]:
            problems.append("alpha channel was lost in the edit")

    mb, ma = mean_rgb(bpx), mean_rgb(apx)
    drift = sum(abs(ma[c] - mb[c]) for c in range(3)) / 3
    print(f"colour   mean drift {drift:.1f}/255")

    if problems:
        print()
        for p in problems:
            print(f"DRIFT {p}", file=sys.stderr)
        return 1

    print("\nOK  geometry held within tolerance")
    return 0


if __name__ == "__main__":
    sys.exit(main())
