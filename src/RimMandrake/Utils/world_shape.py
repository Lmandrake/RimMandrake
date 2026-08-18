#!/usr/bin/env python3
"""Organic shaping over the tile adjacency graph.

Everything here exists because a per-tile paint looks like confetti: single hexes of
one biome dropped inside another, geometric rings, coastlines with straight edges.
These operate on the GRAPH, so they produce filaments, lobes and irregular masses.

    despeckle()   dissolve patches smaller than n tiles into their surroundings
    components()  connected runs of one label
    coastal()     tiles with a water neighbour - the honest definition
    grow()        region-grow irregular blobs from seeds
    roughen()     push a boundary in and out along a noise field
"""
import collections
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from world_graph import load


def graph():
    nb, lat, lon, vec = load()
    return nb, lat, lon, vec


def components(labels, nb, wanted=None):
    """[(label, [tiles...]), ...] for every connected run of one label."""
    seen = [False] * len(labels)
    out = []
    for s in range(len(labels)):
        if seen[s] or (wanted is not None and labels[s] not in wanted):
            continue
        lab = labels[s]
        stack, comp = [s], []
        seen[s] = True
        while stack:
            t = stack.pop()
            comp.append(t)
            for u in nb[t]:
                if not seen[u] and labels[u] == lab:
                    seen[u] = True
                    stack.append(u)
        out.append((lab, comp))
    return out


def despeckle(labels, nb, min_size=4, protect=(), passes=3):
    """Dissolve any patch below min_size into the commonest label around it.

    ⭐ This is the single biggest visual fix available: it is what turns a field of
    one-hex specks into a tapestry. Run it AFTER every biome assignment.
    `protect` holds labels that are allowed to be tiny (a crater sea, a cathedral).
    """
    labels = list(labels)
    moved = 0
    for _ in range(passes):
        changed = 0
        for lab, comp in components(labels, nb):
            if lab in protect or len(comp) >= min_size:
                continue
            ring = collections.Counter()
            for t in comp:
                for u in nb[t]:
                    if labels[u] != lab:
                        ring[labels[u]] += 1
            if not ring:
                continue
            win = ring.most_common(1)[0][0]
            for t in comp:
                labels[t] = win
            changed += len(comp)
        moved += changed
        if not changed:
            break
    return labels, moved


def coastal(is_water, nb):
    """Land tiles touching water, and water tiles touching land."""
    shore_land = [t for t in range(len(is_water))
                  if not is_water[t] and any(is_water[u] for u in nb[t])]
    shore_sea = [t for t in range(len(is_water))
                 if is_water[t] and any(not is_water[u] for u in nb[t])]
    return shore_land, shore_sea


def grow(nb, seeds, target, allowed, rng=None, wobble=0.55):
    """Grow one irregular blob per seed until `target` tiles, over `allowed` tiles.

    The front is popped at random rather than in order, which is what makes the
    outline lobed and filamentary instead of a disc.
    """
    rng = rng or random
    claimed = {}
    fronts = {s: [s] for s in seeds if allowed(s)}
    for s in fronts:
        claimed[s] = s
    live = list(fronts)
    while live:
        for s in list(live):
            f = fronts[s]
            if not f or sum(1 for v in claimed.values() if v == s) >= target:
                live.remove(s)
                continue
            i = rng.randrange(len(f)) if rng.random() < wobble else 0
            t = f.pop(i)
            for u in nb[t]:
                if u not in claimed and allowed(u):
                    claimed[u] = s
                    f.append(u)
    return claimed


def roughen(inside, nb, rng=None, bite=0.35, rounds=2):
    """Chew a boundary in and out so it stops looking like a compass circle."""
    rng = rng or random
    inside = set(inside)
    for _ in range(rounds):
        edge_in = [t for t in inside if any(u not in inside for u in nb[t])]
        edge_out = {u for t in inside for u in nb[t] if u not in inside}
        for t in edge_in:
            if rng.random() < bite:
                inside.discard(t)
        for u in edge_out:
            if rng.random() < bite:
                inside.add(u)
    return inside


def report(labels, nb, name="labels"):
    comps = components(labels, nb)
    sizes = collections.Counter()
    for lab, c in comps:
        sizes[len(c)] += 1
    singles = sizes.get(1, 0)
    tiny = sum(v for k, v in sizes.items() if k <= 3)
    print("  %s: %d patches | single-tile %d | <=3 tiles %d | largest %d"
          % (name, len(comps), singles, tiny, max(len(c) for _, c in comps)))
    return singles, tiny
