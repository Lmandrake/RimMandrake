"""river_lay.py - lay world river links so the engine's riverDist comes out canonical.

No numpy, no bridge: w9_run.py (Windows python.exe) imports it at stamp time, and
parity_fix_plans.py builds the U4 plan with it.

THE ENGINE RULE (1.6, WorldGrid.OverlayRiver(from, to)): `to.riverDist =
max(to.riverDist, from.riverDist + 1)`, and only when the link is NEW - a repeat link
returns early. So riverDist depends on the ORDER and the ORIENTATION links are laid in.
`jawa/world_links_import` lays rows in file order as OverlayRiver(a, b). A CSV exported
from a save is not mouth-first (93 of 326 Ash'karr rows name the upstream end first),
and laying it flattened every head to <= 5 (canonical heads 50, 37, 37, ...). Proof and
numbers: design/Jawa/worldbuilding/parity_causes_2026-10-20.md (U4).

The canonical riverDist cannot be inferred from geometry: 3 of 11 Ash'karr mouths are
neither the lowest tile nor the biggest-river leaf of their system (7 do not border a
sea), and two links are level. So the target is DATA - a (tile, river_dist) table -
and river_lay_order() finds a lay order that reproduces it exactly.
"""
import csv
import io
from collections import defaultdict


def simulate_overlay(order):
    """riverDist after laying `order` [(from, to), ...] with OverlayRiver's rule.
    A repeated edge is a no-op (OverlayRiver returns early on an existing link)."""
    d = defaultdict(int)
    seen = set()
    for a, b in order:
        k = (a, b) if a < b else (b, a)
        if k in seen:
            continue
        seen.add(k)
        d[b] = max(d[b], d[a] + 1)
    return d


def river_lay_order(edges, target):
    """Order and orient every edge once so simulate_overlay reproduces `target`
    on every endpoint. Greedy: always raise a tile by one link without
    overshooting its target, preferring lays that finish a tile from a finished
    neighbour; never finish a tile while it still owes an equal-valued
    neighbour its link (that neighbour must take it at target-1). Returns
    (order, mismatches) where mismatches lists (tile, got, want)."""
    edges = [tuple(e) for e in edges]
    if not hasattr(target, "items"):          # a per-tile list/array (worldview.read_river_distances)
        target = enumerate(target)
    target = defaultdict(int, target)
    adj = defaultdict(set)
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    left = set((a, b) if a < b else (b, a) for a, b in edges)
    d = defaultdict(int)
    order = []

    def unlaid(x, y):
        return ((x, y) if x < y else (y, x)) in left

    while True:
        best = None
        for e in left:
            for a, b in (e, e[::-1]):
                if not (d[a] + 1 <= target[b] and d[a] + 1 > d[b]):
                    continue
                exact = d[a] + 1 == target[b]
                if exact and any(unlaid(b, c) and c != a and target[c] == target[b]
                                 and d[c] < target[c] for c in adj[b]):
                    continue
                key = (not exact, d[a] != target[a], target[b], a, b)
                if best is None or key < best[0]:
                    best = (key, a, b, e)
        if best is None:
            break
        _, a, b, e = best
        d[b] = d[a] + 1
        order.append((a, b))
        left.discard(e)
    for e in sorted(left):                      # links that carry no distance
        for a, b in (e, e[::-1]):
            if d[a] + 1 <= d[b]:
                order.append((a, b))
                break
        else:
            order.append(e)                     # will overshoot; reported below
    got = simulate_overlay(order)
    tiles = set(t for e in edges for t in e)
    mism = sorted((t, got[t], target[t]) for t in tiles if got[t] != target[t])
    return order, mism


def read_river_dist(path):
    """{tile: river_dist} from a `tile,river_dist` CSV, or None if the file is absent."""
    import os
    if not os.path.isfile(path):
        return None
    with io.open(path, encoding="utf-8-sig", newline="") as fh:
        return {int(r["tile"]): int(r["river_dist"]) for r in csv.DictReader(fh)}


def order_links_mouth_first(rows, target):
    """rows: links CSV dicts (kind,a,b,def[,...]). Returns (rows_out, mismatches).

    River rows are re-ordered and re-oriented by river_lay_order(target); every river
    row keeps its own def and extra columns, each edge appears once, and road rows
    follow unchanged in their file order. Raises ValueError on a repeated river edge
    with two different defs (the lay would pick one silently)."""
    rivers, roads = [], []
    for r in rows:
        (rivers if (r.get("kind") or "").strip() == "river" else roads).append(r)
    by_edge = {}
    for r in rivers:
        a, b = int(r["a"]), int(r["b"])
        k = (a, b) if a < b else (b, a)
        if k in by_edge and by_edge[k]["def"] != r["def"]:
            raise ValueError("river edge %s listed twice with defs %s and %s"
                             % (k, by_edge[k]["def"], r["def"]))
        by_edge.setdefault(k, r)
    order, mism = river_lay_order(list(by_edge), target)
    out = []
    for a, b in order:
        r = dict(by_edge[(a, b) if a < b else (b, a)])
        r["a"], r["b"] = str(a), str(b)
        out.append(r)
    return out + list(roads), mism
