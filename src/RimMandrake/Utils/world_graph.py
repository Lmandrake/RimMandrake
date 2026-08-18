#!/usr/bin/env python3
"""The tile adjacency graph — the thing every organic-looking edit needs.

The save stores per-tile arrays and nothing about which tile touches which, so a
painter without this can only make per-tile decisions, which is exactly why an
unclustered paint looks like confetti. Rivers, coasts, blobs, roads and any
"remove single-tile islands" pass all need neighbours.

Built from world/world_tiles_lada.csv with numpy only — scipy is blocked by PEP 668
on this machine and is not needed: a chunked brute-force over 21,872 unit vectors
takes seconds.

⭐ SELF-VERIFYING: a geodesic sphere has EXACTLY 12 pentagonal tiles, every other
tile hexagonal. If the neighbour count histogram is not {5: 12, 6: rest}, the graph
is wrong and everything built on it would be wrong too.

    python3 src/RimMandrake/Utils/world_graph.py        # build + verify + cache
"""
import csv
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TILES = os.path.join(REPO, "world", "world_tiles_lada.csv")
CACHE = os.path.join(REPO, "world", "world_graph.npz")


def unit_vectors(path=TILES):
    lat, lon = [], []
    for r in csv.DictReader(open(path)):
        lat.append(float(r["lat"]))
        lon.append(float(r["long"]))
    lat = np.radians(np.array(lat, dtype=np.float64))
    lon = np.radians(np.array(lon, dtype=np.float64))
    return np.stack([np.cos(lat) * np.cos(lon),
                     np.cos(lat) * np.sin(lon),
                     np.sin(lat)], axis=1), np.degrees(lat), np.degrees(lon)


def build(k=7, chunk=512):
    V, lat, lon = unit_vectors()
    n = len(V)
    idx = np.zeros((n, k - 1), dtype=np.int32)
    dist = np.zeros((n, k - 1), dtype=np.float32)
    for a in range(0, n, chunk):
        b = min(n, a + chunk)
        d = V[a:b] @ V.T                      # cosine similarity; 1.0 == itself
        part = np.argpartition(-d, k, axis=1)[:, :k]
        rows = np.arange(b - a)[:, None]
        dd = d[rows, part]
        order = np.argsort(-dd, axis=1)
        part = part[rows, order]
        dd = dd[rows, order]
        idx[a:b] = part[:, 1:k]               # drop self
        dist[a:b] = np.degrees(np.arccos(np.clip(dd[:, 1:k], -1, 1)))
    # 🔑 NO DISTANCE THRESHOLD. Two attempts at one failed: a fixed cut keeps a
    # phantom 6th neighbour on the pentagons (12 -> 4), and a per-tile relative cut
    # prunes true edges (12 -> 20, with degree-2 tiles).
    # The geometry gives the answer for free: take the 6 nearest for every tile and
    # keep only RECIPROCATED edges. A hexagon's six all list it back. A pentagon's
    # phantom sixth is a second-ring tile whose own six nearest do not include the
    # pentagon, so that edge dies on its own.
    step = float(np.median(dist[:, 0]))
    cand = [set(idx[i, :6].tolist()) for i in range(len(V))]
    keep = np.zeros((len(V), idx.shape[1]), dtype=bool)
    for i in range(len(V)):
        for c in range(6):
            j = int(idx[i, c])
            if i in cand[j]:
                keep[i, c] = True
    return V, lat, lon, idx, keep, step


def main():
    V, lat, lon, idx, keep, step = build()
    deg = keep.sum(axis=1)
    hist = {int(v): int(c) for v, c in zip(*np.unique(deg, return_counts=True))}
    print("tiles %d | median neighbour spacing %.3f deg" % (len(V), step))
    print("neighbour-count histogram:", hist)
    pent = hist.get(5, 0)
    ok = pent == 12 and set(hist) <= {5, 6}
    print("pentagons: %d (a geodesic sphere has exactly 12) -> %s"
          % (pent, "✅ GRAPH VERIFIED" if ok else "🔴 GRAPH IS WRONG"))
    if not ok:
        print("   refusing to cache a graph that fails the pentagon test")
        sys.exit(1)
    np.savez_compressed(CACHE, idx=idx, keep=keep, lat=lat, lon=lon, vec=V)
    print("cached ->", CACHE)


def load():
    """(neighbours: list[list[int]], lat, lon, vec) — builds and caches on demand."""
    if not os.path.exists(CACHE):
        main()
    z = np.load(CACHE)
    idx, keep = z["idx"], z["keep"]
    nb = [idx[i][keep[i]].tolist() for i in range(len(idx))]
    return nb, z["lat"], z["lon"], z["vec"]


if __name__ == "__main__":
    main()
