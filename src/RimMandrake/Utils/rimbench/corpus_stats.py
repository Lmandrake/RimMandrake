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
    scorer; fixed under CORPUS_STATS_VANILLA_CONTROLS_1 -- see below): take
    the same TOP_K "open" boolean mask used above. Find its largest
    4-connected component (the map's main open area) and repeatedly erode
    it with a 4-neighbour (plus-shaped) structuring element -- one ring of
    cells removed per step. A corridor of width W survives erosion up to
    step floor((W-1)/2) and disappears or SPLITS at step floor((W-1)/2)+1.
    Erode until the component first splits into >=2 components that are
    each at least MIN_SPLIT_FRAC of the ORIGINAL main-region size (not
    just >=2 components of ANY size), record that erosion radius r*, and
    estimate the narrowest-neck width as 2*r*-1. This finds a chokepoint
    WITHIN the single largest open region, which is exactly "the minimum
    cut that would produce two large open regions" -- the
    CORPUS_MAP_STATISTICS_1 item's own suggested proxy ("min cut width
    between the two largest regions via erosion"). Capped at EROSION_CAP
    steps; a map with no chokepoint that narrow, or whose main region
    vanishes before two large pieces separate, reports radius=-1,
    width_est=-1 (i.e. "no chokepoint found within the cap", never a
    fabricated number).
    PRIOR BUG (found by CORPUS_STATS_VANILLA_CONTROLS_1, fixed here): the
    original version treated ANY split -- including a single stray cell
    breaking off the main blob's jagged boundary -- as "the" split, so
    n_components > 1 fired at erosion step 1 on essentially every real
    terrain grid regardless of true bottleneck width. Measured: all 44
    corpus maps reported chokepoint_width_est == 1. The size-threshold
    fix above, re-run over the same 44 maps, produces radii from -1 to 14
    and widths from -1 to 27 -- a non-degenerate distribution -- because
    it now waits for the SECOND-largest resulting piece to itself be
    substantial before calling it a split, rather than firing on debris.
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
MIN_SPLIT_FRAC = 0.05  # a split piece must be >= this fraction of the ORIGINAL
                        # main-region size to count as a real second region
                        # (see module docstring's chokepoint PRIOR BUG note)

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


def _component_sizes(mask):
    """Sizes of every True-valued 4-connected component in mask, largest first."""
    if not mask.any():
        return np.array([], dtype=np.int64)
    h, w = mask.shape
    values = mask.astype(np.int8).ravel().tolist()
    labels, k = label_regions(values, w, h)
    lab_arr = np.array(labels, dtype=np.int64).reshape(h, w)
    sizes = np.bincount(lab_arr.ravel()[mask.ravel()], minlength=k)
    return np.sort(sizes)[::-1]


def chokepoint_estimate(open_mask, cap=EROSION_CAP, min_split_frac=MIN_SPLIT_FRAC):
    """(erosion_radius r*, width_est=2r*-1, n_big_pieces) or (-1, -1, 0).

    r* is the first erosion step at which the eroded main region has split
    into >=2 pieces each >= min_split_frac of the ORIGINAL main-region size
    (see module docstring's chokepoint PRIOR BUG note) -- not merely >=2
    pieces of any size, which fires on boundary debris at step 1 almost
    universally. -1,-1,0 if the region vanishes, or the cap is reached,
    before a genuine two-large-piece split occurs.
    """
    main = _largest_true_component(open_mask)
    if main is None:
        return -1, -1, 0
    main_size = int(main.sum())
    thresh = max(1, main_size * min_split_frac)
    cur = main
    for r in range(1, cap + 1):
        eroded = _erode(cur)
        if not eroded.any():
            return -1, -1, 0
        sizes = _component_sizes(eroded)
        n_big = int((sizes >= thresh).sum())
        if n_big >= 2:
            return r, max(2 * r - 1, 0), n_big
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


CONTROLS_DIR_DEFAULT = os.path.join(OUT_DIR, "controls")
OUT_CONTROLS_CSV = os.path.join(OUT_DIR, "controls_map_stats.csv")


def find_control_files(controls_dir):
    return sorted(glob.glob(os.path.join(controls_dir, "**", "*.txt"), recursive=True))


def decode_control_grid(path):
    """Text defName grid (render_terrain.py's INPUT B) -> (w, h, values, "control").

    No shortHash exists for a text grid, so the spec's "hash the defName
    string for the category id" is done as a per-file index into the
    file's own sorted distinct defNames -- deterministic across runs
    (unlike Python's str hash under randomised PYTHONHASHSEED) and free of
    accidental collisions a numeric hash could introduce. The category
    space is per-file, which is correct here: every downstream feature
    (region size, perimeter, openness, chokepoint) only ever compares
    cells for equality/inequality within one grid, never across grids.
    """
    rows = []
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if not line.strip():
                continue
            rows.append([c.strip() for c in line.split(",")])
    if not rows:
        raise ValueError("empty control grid: %s" % path)
    w = len(rows[0])
    for i, r in enumerate(rows):
        if len(r) != w:
            raise ValueError("ragged control grid in %s: row %d has %d cells, row 0 has %d"
                              % (path, i, len(r), w))
    h = len(rows)
    names = [name for row in rows for name in row]
    id_of = {name: i for i, name in enumerate(sorted(set(names)))}
    values = [id_of[name] for name in names]
    return w, h, values, "control"


def run(controls_dir=None):
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

    control_rows = []
    if controls_dir:
        control_files = find_control_files(controls_dir)
        if not control_files:
            print("FAILED no *.txt control grids found under %s" % controls_dir)
            return 1
        for path in control_files:
            try:
                w, h, values, version = decode_control_grid(path)
                row = analyze_map(w, h, values, version, path)
            except Exception as e:
                print("FAILED %s %s" % (path, e))
                return 1
            control_rows.append(row)
            print("[control] %s %dx%d" % (row["name"], w, h))

    os.makedirs(OUT_DIR, exist_ok=True)
    write_csv(rows, OUT_CSV)
    if control_rows:
        write_csv(control_rows, OUT_CONTROLS_CSV)
    write_summary(rows, control_rows)

    total = time.time() - t_all
    print("rows=%d controls=%d" % (len(rows), len(control_rows)))
    print("total_seconds=%.1f slowest=%s (%.1fs)" % (total, slowest[0], slowest[1]))
    if len(rows) != len(files):
        print("FAILED rows=%d != files=%d" % (len(rows), len(files)))
        return 1
    if controls_dir and len(control_rows) < 10:
        print("FAILED controls=%d < 10 required" % len(control_rows))
        return 1
    return 0


def write_csv(rows, path):
    import csv
    with io.open(path, "w", encoding="utf-8", newline="") as f:
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


def _ranges_overlap(a, b):
    """True if the [min, max] spans of two non-empty value lists intersect."""
    if not a or not b:
        return None
    return not (max(a) < min(b) or max(b) < min(a))


def write_summary(rows, control_rows=None):
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
    lines.append("%d hand-authored `.rws` maps, hash-only topology (no def-name"
                  % len(rows))
    lines.append("resolution). Source: `corpus_stats.py --run --controls <dir>`.")
    if control_rows:
        lines.append("Compared below against %d vanilla-generated control maps "
                      "(CORPUS_STATS_VANILLA_CONTROLS_1)." % len(control_rows))
    else:
        lines.append("NO CONTROLS THIS RUN -- pass `--controls <dir>` to compare")
        lines.append("against vanilla-generated maps (CORPUS_STATS_VANILLA_CONTROLS_1);")
        lines.append("nothing below has been compared to vanilla in this run.")
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

    if control_rows:
        lines.append("")
        lines.append("## Corpus vs controls, by size bucket (CORPUS_STATS_VANILLA_CONTROLS_1)")
        lines.append("")
        lines.append("%d vanilla-generated control maps, matched size buckets only "
                      "(a feature compared across mismatched sizes would read a size"
                      % len(control_rows))
        lines.append("effect as a corpus/vanilla difference -- see this item's LIES line).")
        lines.append("")
        for field, label in features:
            corpus_buckets = _stratify(rows, "size_bucket", field)
            control_buckets = _stratify(control_rows, "size_bucket", field)
            shared = [b for b in ["250", "275", "300", "325+", "400+"]
                      if b in corpus_buckets and b in control_buckets]
            lines.append("- **%s**" % label)
            if not shared:
                lines.append("  - no size bucket present in both corpus and controls")
                continue
            for b in shared:
                cvals, tvals = corpus_buckets[b], control_buckets[b]
                overlap = _ranges_overlap(cvals, tvals)
                verdict = "OVERLAP" if overlap else "NO OVERLAP (candidate distinguishing feature)"
                lines.append("  - %s: corpus %s | controls %s -> %s"
                              % (b, _range_str(cvals), _range_str(tvals), verdict))

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
    ap.add_argument("--controls", metavar="DIR", default=None,
                     help="dir of vanilla-control text grids (render_terrain.py "
                          "INPUT B format); adds the corpus-vs-controls section")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.run:
        return run(controls_dir=args.controls)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
