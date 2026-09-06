"""HASH-ONLY topology statistics over the hand-authored map corpus.

Spec: infrastructure/state/items/CORPUS_MAP_STATISTICS_1.md. Computes the
feature families from design/RimMandrake/beautiful_tilemap.md §6 over every
`.rws` under research/RimMandrake/hand_authored_maps/, WITHOUT resolving any
shortHash to a defName -- the corpus spans mod sets our dump cannot resolve
(§6a), and this item's "not chasing" bans semantics (water/buildable) and any
nearest-neighbour scorer entirely. A "region" below always means a maximal
4-connected run of cells sharing the exact same 2-byte terrain shortHash --
never a named terrain.

Decoding: reuses SaveMap._decode (savemap.py, same directory) for the
base64+raw-DEFLATE codec only -- called as a static method, so no dump_dir /
hash table is ever loaded. mapSizeX/mapSizeZ and gameVersion are read by the
same regex approach savemap.py uses. Grids in this corpus are NOT always
square (e.g. 325x225); every function here takes (w, h) separately.

numpy: this machine has numpy 2.5.2, used throughout for the per-cell
vectorised ops (perimeter, adjacency, windows, erosion). Region LABELLING
uses a plain-Python union-find scanline (not a numpy trick) -- across the
whole 44-map corpus (~3.8M cells total) that is the fast path, and it is
plain Python only because there is no vectorised way to do scanline
union-find; everything downstream of a label array is numpy.

FEATURES computed per map:
  - connected-region size distribution: count, mean, p50, p90, max-fraction
  - perimeter/area per region: overall mean (unweighted over regions), and
    the perimeter, area and ratio of the 5 largest regions. Perimeter of a
    region = count of its cell-edges whose other side is a different region
    OR the map edge (a 1x1 island has perimeter 4).
  - openness: a def-name-free proxy. Without names we cannot know which
    hash is "passable" terrain, so openness is approximated as the fraction
    of cells whose hash is among the TOP_K (see TOP_K below) most frequent
    hashes on that map -- the working assumption (documented, not verified)
    that hand-built maps spend most of their non-feature area on a small
    number of common ground terrains. TOP_K = 3, chosen because a single
    top hash is sometimes a minor variant (e.g. rough vs flat sand) that
    undercounts open ground, while the top 3 usually covers the natural
    "ground family" without pulling in built floors or water. Same
    definition is reused, unchanged, for the windowed and chokepoint
    features below, so all three describe the same open set.
  - openness in 25x25 windows: the grid is tiled into complete WINDOW x
    WINDOW blocks (remainder cells at the far edges are dropped, not
    padded); mean and std of the per-window open fraction are reported.
    Falls back to a single whole-grid "window" if either dimension is
    smaller than WINDOW (never true of the real corpus; keeps --selftest's
    40x40 synthetic grid from crashing).
  - adjacency structure: over the raw hash grid (not regions), every
    4-neighbour edge whose two cells differ contributes one occurrence of
    the unordered pair {hash_a, hash_b}. Reported: how many DISTINCT pairs
    occur, and the Shannon entropy (base 2, bits) of the occurrence
    distribution over those pairs -- structure only, no pair is ever named.
  - chokepoints (documented proxy, no def names, no nearest-neighbour
    scorer): take the same TOP_K "open" boolean mask used above. Find its
    largest 4-connected component (the map's main open area) and repeatedly
    erode it with a 4-neighbour (plus-shaped) structuring element -- one
    ring of cells removed per step. A corridor of width W survives erosion
    up to step floor((W-1)/2) and disappears or SPLITS into >=2 components
    at step floor((W-1)/2)+1. So: erode until the component first splits
    (or vanishes), record that erosion radius r*, and estimate the
    narrowest-neck width as 2*r*-1. This finds a chokepoint WITHIN the
    single largest open region, which is exactly "the minimum cut that
    would produce two large open regions" -- the CORPUS_MAP_STATISTICS_1
    item's own suggested proxy ("min cut width between the two largest
    regions via erosion"). Capped at EROSION_CAP steps; a map with no
    chokepoint that narrow reports radius=-1, width_est=-1 (i.e. "no
    chokepoint found within the cap", never a fabricated number).
  - distinct-hash count, map width/height/cell-count, gameVersion (raw
    string from the save) and its major "X.Y", and the source file path.

NOT computed, on purpose (spec's "not chasing"): anything requiring a
defName (is-it-water, is-it-buildable), the things layer, any learned
model, any single composite "score", and no nearest-neighbour-to-corpus
distance of any kind.

Usage:
    python3 corpus_stats.py --selftest
    python3 corpus_stats.py --run
"""
import argparse
import base64
import glob
import io
import math
import os
import re
import struct
import sys
import time
import zlib
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from savemap import SaveMap  # noqa: E402  (reuse the codec only, never dump_dir)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
CORPUS_DIR = os.path.join(REPO_ROOT, "research", "RimMandrake", "hand_authored_maps")
OUT_DIR = os.path.join(REPO_ROOT, "research", "RimMandrake", "reference")
OUT_CSV = os.path.join(OUT_DIR, "corpus_map_stats.csv")
OUT_MD = os.path.join(OUT_DIR, "corpus_map_stats.md")

TOP_K = 3            # see module docstring: openness/window/chokepoint proxy
WINDOW = 25           # openness window side, cells
EROSION_CAP = 25      # max erosion radius tried before giving up on a chokepoint

CSV_FIELDS = [
    "file", "name", "width", "height", "cells", "game_version", "version_major",
    "size_bucket", "distinct_hash_count",
    "region_count", "region_size_mean", "region_size_p50", "region_size_p90",
    "region_size_max_frac",
    "perim_area_mean_overall",
    "top5_sizes", "top5_perimeters", "top5_perim_area_ratios",
    "openness_topk_k", "openness_frac",
    "openness_window_mean", "openness_window_std",
    "adjacency_distinct_pairs", "adjacency_entropy_bits",
    "chokepoint_erosion_radius", "chokepoint_width_est", "chokepoint_split_count",
]


# --------------------------------------------------------------- decoding
def decode_save(path):
    """(w, h, values: list[int], game_version: str) from one .rws, hash-only."""
    text = io.open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r"<mapSizeX>(\d+)</mapSizeX>.*?<mapSizeZ>(\d+)</mapSizeZ>",
                  text, re.S)
    if not m:
        raise ValueError("no <mapSizeX>/<mapSizeZ> found")
    w, h = int(m.group(1)), int(m.group(2))
    gm = re.search(r"<topGridDeflate>(.*?)</topGridDeflate>", text, re.S)
    if not gm:
        raise ValueError("no <topGridDeflate> found")
    raw = SaveMap._decode(gm.group(1))
    n = len(raw) // 2
    values = struct.unpack("<%dH" % n, raw[:n * 2])
    if len(values) != w * h:
        raise ValueError("grid has %d cells, expected %d x %d = %d"
                          % (len(values), w, h, w * h))
    gv = re.search(r"<gameVersion>([^<]*)</gameVersion>", text)
    version = gv.group(1).strip() if gv else "UNKNOWN"
    return w, h, values, version


# ---------------------------------------------------------- region labels
def label_regions(values, w, h):
    """4-connected components of equal-value cells. values: flat, row-major.

    Plain-Python union-find scanline -- see module docstring for why this
    one step is not vectorised. Returns (labels: list[int] in 0..k-1, k).
    """
    n = w * h
    parent = list(range(n))

    def find(a):
        root = a
        while parent[root] != root:
            root = parent[root]
        while parent[a] != root:
            parent[a], a = root, parent[a]
        return root

    for z in range(h):
        base = z * w
        for x in range(w):
            i = base + x
            v = values[i]
            if x > 0 and values[i - 1] == v:
                ra, rb = find(i), find(i - 1)
                if ra != rb:
                    parent[rb] = ra
            if z > 0 and values[i - w] == v:
                ra, rb = find(i), find(i - w)
                if ra != rb:
                    parent[rb] = ra

    roots = [find(i) for i in range(n)]
    remap = {}
    labels = [0] * n
    for i, r in enumerate(roots):
        lab = remap.get(r)
        if lab is None:
            lab = len(remap)
            remap[r] = lab
        labels[i] = lab
    return labels, len(remap)


def region_perimeters(lab_arr, k):
    """Per-region perimeter (unit cell-edges to a different region or map edge)."""
    perim = np.zeros(k, dtype=np.int64)
    h, w = lab_arr.shape
    pads = [
        (np.full_like(lab_arr, -1), (slice(1, None), slice(None)), (slice(None, -1), slice(None))),  # up
        (np.full_like(lab_arr, -1), (slice(None, -1), slice(None)), (slice(1, None), slice(None))),   # down
        (np.full_like(lab_arr, -1), (slice(None), slice(1, None)), (slice(None), slice(None, -1))),   # left
        (np.full_like(lab_arr, -1), (slice(None), slice(None, -1)), (slice(None), slice(1, None))),   # right
    ]
    for neighbor, dst, src in pads:
        neighbor[dst] = lab_arr[src]
        mismatch = lab_arr != neighbor
        perim += np.bincount(lab_arr[mismatch], minlength=k).astype(np.int64)
    return perim


# ----------------------------------------------------------- adjacency
def adjacency_stats(val_arr):
    """(distinct unordered hash-pairs across 4-neighbour edges, entropy bits)."""
    pairs = []
    for a, b in ((val_arr[:, :-1], val_arr[:, 1:]),
                 (val_arr[:-1, :], val_arr[1:, :])):
        mask = a != b
        lo = np.minimum(a[mask], b[mask])
        hi = np.maximum(a[mask], b[mask])
        if lo.size:
            pairs.append(np.stack([lo, hi], axis=1))
    if not pairs:
        return 0, 0.0
    combined = np.concatenate(pairs, axis=0)
    _, counts = np.unique(combined, axis=0, return_counts=True)
    total = counts.sum()
    p = counts / total
    entropy = float(-(p * np.log2(p)).sum())
    return int(counts.size), entropy


# ------------------------------------------------------------- openness
def openness_mask(val_arr):
    counts = Counter(val_arr.ravel().tolist())
    top_hashes = {h for h, _ in counts.most_common(TOP_K)}
    mask = np.isin(val_arr, list(top_hashes))
    return mask, float(mask.mean())


def windowed_openness(mask, window=WINDOW):
    h, w = mask.shape
    nh, nw = h // window, w // window
    if nh == 0 or nw == 0:
        frac = float(mask.mean())
        return frac, 0.0
    trimmed = mask[:nh * window, :nw * window].astype(np.float64)
    reshaped = trimmed.reshape(nh, window, nw, window)
    window_frac = reshaped.mean(axis=(1, 3)).ravel()
    return float(window_frac.mean()), float(window_frac.std())


# ------------------------------------------------------------ chokepoint
def _erode(mask):
    h, w = mask.shape
    up = np.zeros_like(mask); up[1:, :] = mask[:-1, :]
    down = np.zeros_like(mask); down[:-1, :] = mask[1:, :]
    left = np.zeros_like(mask); left[:, 1:] = mask[:, :-1]
    right = np.zeros_like(mask); right[:, :-1] = mask[:, 1:]
    return mask & up & down & left & right


def _largest_true_component(mask):
    """Label mask.astype(int) and return the boolean array of the largest True region."""
    h, w = mask.shape
    values = mask.astype(np.int8).ravel().tolist()
    labels, k = label_regions(values, w, h)
    lab_arr = np.array(labels, dtype=np.int64).reshape(h, w)
    flat_mask = mask.ravel()
    lab_flat = lab_arr.ravel()
    true_labels = lab_flat[flat_mask]
    if true_labels.size == 0:
        return None
    sizes = np.bincount(true_labels)
    biggest = int(np.argmax(sizes))
    return lab_arr == biggest


def _count_true_components(mask):
    if not mask.any():
        return 0
    h, w = mask.shape
    values = mask.astype(np.int8).ravel().tolist()
    labels, k = label_regions(values, w, h)
    lab_arr = np.array(labels, dtype=np.int64).reshape(h, w)
    true_labels = np.unique(lab_arr[mask])
    return int(true_labels.size)


def chokepoint_estimate(open_mask, cap=EROSION_CAP):
    """(erosion_radius r*, width_est=2r*-1, split_count) or (-1, -1, 0)."""
    main = _largest_true_component(open_mask)
    if main is None:
        return -1, -1, 0
    cur = main
    for r in range(1, cap + 1):
        eroded = _erode(cur)
        if not eroded.any():
            return r, max(2 * r - 1, 0), 0
        n_components = _count_true_components(eroded)
        if n_components > 1:
            return r, 2 * r - 1, n_components
        cur = eroded
    return -1, -1, 0


# --------------------------------------------------------------- per-map
def analyze_map(w, h, values, version, file_path):
    val_arr = np.array(values, dtype=np.int64).reshape(h, w)
    n_cells = w * h

    labels, k = label_regions(values, w, h)
    lab_arr = np.array(labels, dtype=np.int64).reshape(h, w)
    sizes = np.bincount(lab_arr.ravel(), minlength=k).astype(np.int64)
    perims = region_perimeters(lab_arr, k)

    order = np.argsort(sizes)[::-1]
    sorted_sizes = sizes[order]
    sorted_perims = perims[order]

    region_size_mean = float(sizes.mean())
    region_size_p50 = float(np.percentile(sizes, 50))
    region_size_p90 = float(np.percentile(sizes, 90))
    region_size_max_frac = float(sizes.max() / n_cells)

    with np.errstate(divide="ignore", invalid="ignore"):
        ratios = np.where(sizes > 0, perims / sizes, 0.0)
    perim_area_mean_overall = float(ratios.mean())

    top5 = min(5, k)
    top5_sizes = sorted_sizes[:top5].tolist()
    top5_perims = sorted_perims[:top5].tolist()
    top5_ratios = [p / s if s else 0.0 for p, s in zip(top5_perims, top5_sizes)]

    open_mask, openness_frac = openness_mask(val_arr)
    win_mean, win_std = windowed_openness(open_mask)
    adj_pairs, adj_entropy = adjacency_stats(val_arr)
    choke_r, choke_w, choke_split = chokepoint_estimate(open_mask)

    version_major = ".".join(version.split(".")[:2]) if version != "UNKNOWN" else "UNKNOWN"

    row = {
        "file": file_path,
        "name": os.path.basename(os.path.dirname(file_path)),
        "width": w, "height": h, "cells": n_cells,
        "game_version": version, "version_major": version_major,
        "size_bucket": size_bucket(w, h),
        "distinct_hash_count": len(set(values)),
        "region_count": k,
        "region_size_mean": round(region_size_mean, 3),
        "region_size_p50": round(region_size_p50, 3),
        "region_size_p90": round(region_size_p90, 3),
        "region_size_max_frac": round(region_size_max_frac, 5),
        "perim_area_mean_overall": round(perim_area_mean_overall, 5),
        "top5_sizes": ";".join(str(x) for x in top5_sizes),
        "top5_perimeters": ";".join(str(x) for x in top5_perims),
        "top5_perim_area_ratios": ";".join("%.5f" % x for x in top5_ratios),
        "openness_topk_k": TOP_K,
        "openness_frac": round(openness_frac, 5),
        "openness_window_mean": round(win_mean, 5),
        "openness_window_std": round(win_std, 5),
        "adjacency_distinct_pairs": adj_pairs,
        "adjacency_entropy_bits": round(adj_entropy, 5),
        "chokepoint_erosion_radius": choke_r,
        "chokepoint_width_est": choke_w,
        "chokepoint_split_count": choke_split,
    }
    return row


def size_bucket(w, h):
    """One of the five buckets named in CORPUS_MAP_STATISTICS_1.md, by max(w,h)."""
    m = max(w, h)
    if m <= 260:
        return "250"      # also catches the one 200x200 outlier; no bucket names it
    if m <= 290:
        return "275"
    if m <= 310:
        return "300"
    if m < 400:
        return "325+"
    return "400+"


# ------------------------------------------------------------------- run
def find_corpus_files():
    return sorted(glob.glob(os.path.join(CORPUS_DIR, "**", "*.rws"), recursive=True))


def run():
    files = find_corpus_files()
    if not files:
        print("FAILED no .rws files found under %s" % CORPUS_DIR)
        return 1
    rows = []
    t_all = time.time()
    slowest = (None, 0.0)
    for path in files:
        t0 = time.time()
        try:
            w, h, values, version = decode_save(path)
            row = analyze_map(w, h, values, version, path)
        except Exception as e:
            print("FAILED %s %s" % (path, e))
            return 1
        dt = time.time() - t0
        if dt > slowest[1]:
            slowest = (path, dt)
        rows.append(row)
        print("%s %dx%d %.1fs" % (row["name"], w, h, dt))
        if dt > 90:
            print("SLOW >90s: %s took %.1fs" % (path, dt))

    os.makedirs(OUT_DIR, exist_ok=True)
    write_csv(rows)
    write_summary(rows)

    total = time.time() - t_all
    print("rows=%d" % len(rows))
    print("total_seconds=%.1f slowest=%s (%.1fs)" % (total, slowest[0], slowest[1]))
    if len(rows) != len(files):
        print("FAILED rows=%d != files=%d" % (len(rows), len(files)))
        return 1
    return 0


def write_csv(rows):
    import csv
    with io.open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def _stratify(rows, key_field, feature_field):
    buckets = {}
    for r in rows:
        buckets.setdefault(r[key_field], []).append(r[feature_field])
    return buckets


def _range_str(vals):
    if not vals:
        return "n/a"
    vals = sorted(vals)
    n = len(vals)
    p50 = vals[n // 2]
    return "min=%.4g p50=%.4g max=%.4g (n=%d)" % (vals[0], p50, vals[-1], n)


def write_summary(rows):
    features = [
        ("region_count", "region count"),
        ("region_size_max_frac", "largest-region fraction of map"),
        ("perim_area_mean_overall", "perimeter/area, mean over regions"),
        ("openness_frac", "openness (top-%d hash fraction)" % TOP_K),
        ("openness_window_std", "openness std across 25x25 windows"),
        ("adjacency_distinct_pairs", "distinct adjacency pairs"),
        ("adjacency_entropy_bits", "adjacency entropy (bits)"),
        ("chokepoint_width_est", "chokepoint width estimate (-1=none found)"),
        ("distinct_hash_count", "distinct terrain hashes"),
    ]
    lines = []
    lines.append("# Corpus map topology statistics")
    lines.append("")
    lines.append("44 hand-authored `.rws` maps, hash-only topology (no def-name")
    lines.append("resolution). Source: `corpus_stats.py --run`. NO CONTROLS YET --")
    lines.append("vanilla-generated control maps are a follow-up captured through")
    lines.append("the bridge (CORPUS_MAP_STATISTICS_1.md); nothing below has been")
    lines.append("compared to vanilla, and no fabricated control numbers appear here.")
    lines.append("")
    lines.append("## By size bucket (250 / 275 / 300 / 325+ / 400+, by max(w,h))")
    lines.append("")
    for field, label in features:
        buckets = _stratify(rows, "size_bucket", field)
        lines.append("- **%s**" % label)
        for b in ["250", "275", "300", "325+", "400+"]:
            if b in buckets:
                lines.append("  - %s: %s" % (b, _range_str(buckets[b])))
    lines.append("")
    lines.append("## By game version (1.4 / 1.5 / 1.6)")
    lines.append("")
    for field, label in features:
        buckets = _stratify(rows, "version_major", field)
        lines.append("- **%s**" % label)
        for v in ["1.4", "1.5", "1.6"]:
            if v in buckets:
                lines.append("  - %s: %s" % (v, _range_str(buckets[v])))
    lines.append("")
    lines.append("## Confound check (§6b)")
    lines.append("")
    for field, label in features:
        by_size = _stratify(rows, "size_bucket", field)
        by_ver = _stratify(rows, "version_major", field)
        size_spread = _spread_ratio(by_size)
        ver_spread = _spread_ratio(by_ver)
        verdict = []
        verdict.append("size-driven" if size_spread > 2.0 else "not clearly size-driven")
        verdict.append("version-driven" if ver_spread > 2.0 else "not clearly version-driven")
        lines.append("- %s: %s (bucket-median spread ratio %.2fx size, %.2fx version)."
                      % (label, ", ".join(verdict), size_spread, ver_spread))
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def _spread_ratio(buckets):
    medians = []
    for vals in buckets.values():
        if vals:
            s = sorted(vals)
            medians.append(s[len(s) // 2])
    medians = [abs(m) for m in medians if m == m]  # drop NaN
    if len(medians) < 2 or min(medians) == 0:
        if len(medians) < 2:
            return 1.0
        return float("inf") if max(medians) > 0 else 1.0
    return max(medians) / min(medians)


# --------------------------------------------------------------- selftest
def selftest():
    n_pass = 0
    n_total = 0
    w, h = 40, 40

    # 3 regions of known size: 1000 (rows 0-24), 400 (rows 25-34), 200 (rows 35-39)
    values = [0] * (w * h)
    for z in range(h):
        for x in range(w):
            i = z * w + x
            if z < 25:
                values[i] = 1
            elif z < 35:
                values[i] = 2
            else:
                values[i] = 3
    labels, k = label_regions(values, w, h)
    lab_arr = np.array(labels).reshape(h, w)
    sizes = sorted(np.bincount(lab_arr.ravel()).tolist(), reverse=True)

    n_total += 1
    if k == 3:
        n_pass += 1
        print("PASS region_count == 3")
    else:
        print("FAIL region_count == 3, got %d" % k)

    n_total += 1
    if sizes == [1000, 400, 200]:
        n_pass += 1
        print("PASS region sizes == [1000, 400, 200]")
    else:
        print("FAIL region sizes == [1000, 400, 200], got %s" % sizes)

    # 2-hash checkerboard: every 4-neighbour edge differs -> exactly 1 distinct pair
    cw, ch = 20, 20
    board = np.zeros((ch, cw), dtype=np.int64)
    for z in range(ch):
        for x in range(cw):
            board[z, x] = (x + z) % 2
    distinct, entropy = adjacency_stats(board)

    n_total += 1
    if distinct == 1:
        n_pass += 1
        print("PASS checkerboard adjacency_distinct_pairs == 1")
    else:
        print("FAIL checkerboard adjacency_distinct_pairs == 1, got %d" % distinct)

    n_total += 1
    if abs(entropy - 0.0) < 1e-9:
        n_pass += 1
        print("PASS checkerboard adjacency entropy == 0 bits (one pair only)")
    else:
        print("FAIL checkerboard adjacency entropy == 0, got %.6f" % entropy)

    print("SELFTEST PASS %d/%d" % (n_pass, n_total))
    return 0 if n_pass == n_total else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.run:
        return run()
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
