#!/usr/bin/env python3
"""Full metric audit for a creature FACING SET at wiring time.

Owner ruling 2026-09-16: "wire in the full metric check not just the size."
The sprite validator's structural gates run per file; this instrument runs
the CROSS-FACING checks nothing else owns, plus the per-file gates, so one
command answers "is this set wireable" with measurements instead of memory:

  per file    : canvas, real alpha, corners clear, faint-fringe %, mid-alpha
                band %, opaque coverage sanity
  across set  : canvas uniformity; major-axis size spread (the
                anooba-looks-huge class, flag > 15%); mean-RGB palette
                distance between facings (the mantis-east-wrong-colour
                class, flag > 40); bottom-anchor drift (creatures must sit
                at comparable height in the tile, flag > 12% of canvas);
                sha256 pairwise duplicates (the anooba-female-was-the-male
                class)

Exit 0 = every gate green. Exit 1 = at least one FLAG (wiring should stop
and a human look). Numbers are printed either way — this reports, the
human rules.

Usage:
  python3 facing_set_audit.py <north.png> <south.png> <east.png> [west.png]
  python3 facing_set_audit.py --set <dir-or-glob-prefix>   # finds *_north/_south/_east
"""
import hashlib
import sys
from pathlib import Path

from PIL import Image

SIZE_SPREAD_FLAG = 15.0     # percent, major-axis across facings
PALETTE_DIST_FLAG = 40.0    # mean-RGB euclidean distance between facings
ANCHOR_DRIFT_FLAG = 12.0    # percent of canvas height, bbox bottom edge
FRINGE_FLAG = 2.0           # percent of pixels at alpha 1..31
MIDALPHA_FLAG = 10.0        # percent of pixels at alpha 32..223
COVERAGE_RANGE = (2.0, 85.0)


def measure(path):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.load()
    alpha = im.split()[3]
    hist = alpha.histogram()
    total = w * h
    opaque = sum(hist[224:])
    fringe = sum(hist[1:32]) / total * 100
    mid = sum(hist[32:224]) / total * 100
    coverage = opaque / total * 100
    bbox = alpha.point(lambda a: 255 if a > 127 else 0).getbbox()
    corners = all(px[x, y][3] == 0 for x in (0, w - 1) for y in (0, h - 1))
    r = g = b = n = 0
    if bbox:
        small = im.crop(bbox)
        small.thumbnail((96, 96))
        for pr, pg, pb, pa in small.getdata():
            if pa > 127:
                r += pr; g += pg; b += pb; n += 1
    mean_rgb = (r / n, g / n, b / n) if n else (0, 0, 0)
    return {
        "path": str(path), "size": (w, h),
        "sha": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        "corners_clear": corners, "fringe": fringe, "mid": mid,
        "coverage": coverage, "bbox": bbox,
        "major": max(bbox[2] - bbox[0], bbox[3] - bbox[1]) if bbox else 0,
        "bottom_pct": (bbox[3] / h * 100) if bbox else 0,
        "mean_rgb": mean_rgb,
    }


def main(argv):
    args = argv[1:]
    if args and args[0] == "--set":
        stem = args[1]
        paths = []
        for f in ("north", "south", "east", "west"):
            hits = sorted(Path(".").glob(f"{stem}*{f}*.png")) or \
                   sorted(Path(stem).glob(f"*{f}*.png") if Path(stem).is_dir() else [])
            if hits:
                paths.append(hits[-1])
    else:
        paths = [Path(p) for p in args]
    if len(paths) < 2:
        print("need at least two facings"); return 2

    ms = [measure(p) for p in paths]
    flags = []

    for m in ms:
        name = Path(m["path"]).name
        if not m["bbox"]:
            flags.append(f"{name}: EMPTY (no opaque pixels)")
        if not m["corners_clear"]:
            flags.append(f"{name}: corner not transparent")
        if m["fringe"] > FRINGE_FLAG:
            flags.append(f"{name}: faint-fringe {m['fringe']:.2f}% > {FRINGE_FLAG}%")
        if m["mid"] > MIDALPHA_FLAG:
            flags.append(f"{name}: mid-alpha wash {m['mid']:.1f}% > {MIDALPHA_FLAG}%")
        if not (COVERAGE_RANGE[0] <= m["coverage"] <= COVERAGE_RANGE[1]):
            flags.append(f"{name}: coverage {m['coverage']:.1f}% outside {COVERAGE_RANGE}")

    if len({m["size"] for m in ms}) > 1:
        flags.append("canvas sizes differ across facings: " +
                     ", ".join(f"{Path(m['path']).name}={m['size']}" for m in ms))

    majors = [m["major"] for m in ms if m["major"]]
    if majors:
        spread = (max(majors) - min(majors)) / (sum(majors) / len(majors)) * 100
        if spread > SIZE_SPREAD_FLAG:
            flags.append(f"size spread {spread:.1f}% > {SIZE_SPREAD_FLAG}%")
    else:
        spread = 0.0

    for i in range(len(ms)):
        for j in range(i + 1, len(ms)):
            a, b = ms[i], ms[j]
            if a["sha"] == b["sha"]:
                flags.append(f"BYTE-IDENTICAL: {Path(a['path']).name} == {Path(b['path']).name}")
            d = sum((x - y) ** 2 for x, y in zip(a["mean_rgb"], b["mean_rgb"])) ** 0.5
            if d > PALETTE_DIST_FLAG:
                flags.append(f"palette distance {d:.0f} > {PALETTE_DIST_FLAG}: "
                             f"{Path(a['path']).name} vs {Path(b['path']).name}")

    bottoms = [m["bottom_pct"] for m in ms if m["bbox"]]
    if bottoms and max(bottoms) - min(bottoms) > ANCHOR_DRIFT_FLAG:
        flags.append(f"bottom-anchor drift {max(bottoms)-min(bottoms):.1f}% > {ANCHOR_DRIFT_FLAG}%")

    print(f"{'file':44s} {'canvas':>9s} {'major':>6s} {'cov%':>6s} {'fringe%':>8s} {'meanRGB':>13s}")
    for m in ms:
        print(f"{Path(m['path']).name:44s} {str(m['size']):>9s} {m['major']:6d} "
              f"{m['coverage']:6.1f} {m['fringe']:8.2f} "
              f"{','.join(str(int(c)) for c in m['mean_rgb']):>13s}")
    print(f"size spread {spread:.1f}%  |  anchor drift "
          f"{(max(bottoms)-min(bottoms)) if bottoms else 0:.1f}%")

    if flags:
        print("\nFLAGS:")
        for f in flags:
            print("  FLAG", f)
        return 1
    print("\nPASS — full metric gate green.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
