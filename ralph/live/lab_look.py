#!/usr/bin/env python3
"""The blind judge's look faults, counted on a lab lay (no game): what the bends count does not see.
    python3 ralph/live/lab_look.py LAB_DIR [LAB_DIR ...] [--looks Modern,Scrapper,...] [--list]

Per look and lay folder:
  selfX    a cord crossing itself (a figure-8, a pretzel); a cut end's own curl is left out
  pairX    two cords off one box or strip crossing within 1.2 cells of it (the X under a strip)
  overBox  a cord passing within 0.4 cell of another box's, strip's or plate's middle (its own two ends left out)
  circle   a stretch that turns a whole round (>= 1.75 pi) within 7 cells of cord: a tight perfect ring
  lampTop  a cord through the cell above a standing lamp, where the lamp's art stands (in at its foot, out at its top)
"""
import argparse, json, math, os, re

ap = argparse.ArgumentParser()
ap.add_argument("dirs", nargs="+")
ap.add_argument("--looks", default="Modern,Scrapper,Industrial,Futuristic")
ap.add_argument("--list", action="store_true")
ap.add_argument("--worlds", default="Transient/lab/ba/worlds")
a = ap.parse_args()


def seg_x(p1, p2, p3, p4):
    d = (p2[0] - p1[0]) * (p4[1] - p3[1]) - (p2[1] - p1[1]) * (p4[0] - p3[0])
    if abs(d) < 1e-12:
        return None
    t = ((p3[0] - p1[0]) * (p4[1] - p3[1]) - (p3[1] - p1[1]) * (p4[0] - p3[0])) / d
    u = ((p3[0] - p1[0]) * (p2[1] - p1[1]) - (p3[1] - p1[1]) * (p2[0] - p1[0])) / d
    if 0 <= t < 1 and 0 <= u < 1:
        return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))
    return None


def cum(P):
    c = [0.0]
    for i in range(1, len(P)):
        c.append(c[-1] + math.dist(P[i - 1], P[i]))
    return c


def self_crossings(P):
    """Crossings of a strand with itself, as points, ignoring neighbouring segments."""
    out = []
    n = len(P)
    # bucket segments on a 0.5 grid
    grid = {}
    for i in range(n - 1):
        x0, x1 = sorted((P[i][0], P[i + 1][0])); z0, z1 = sorted((P[i][1], P[i + 1][1]))
        for gx in range(int(math.floor(x0 * 2)), int(math.floor(x1 * 2)) + 1):
            for gz in range(int(math.floor(z0 * 2)), int(math.floor(z1 * 2)) + 1):
                grid.setdefault((gx, gz), []).append(i)
    seen = set()
    for lst in grid.values():
        for ii in range(len(lst)):
            for jj in range(ii + 1, len(lst)):
                i, j = lst[ii], lst[jj]
                if abs(i - j) < 3 or (i, j) in seen:
                    continue
                seen.add((i, j))
                x = seg_x(P[i], P[i + 1], P[j], P[j + 1])
                if x:
                    out.append((x, i, j))
    return out


def turning_windows(P, c):
    """Stretches turning >= 1.75 pi within 7 cells of cord, as their mid points (non-overlapping)."""
    n = len(P)
    h = [math.atan2(P[i + 1][1] - P[i][1], P[i + 1][0] - P[i][0]) for i in range(n - 1)]
    dt = [0.0]
    for i in range(1, len(h)):
        d = h[i] - h[i - 1]
        while d > math.pi: d -= 2 * math.pi
        while d < -math.pi: d += 2 * math.pi
        dt.append(d)
    acc = [0.0]
    for d in dt[1:]:
        acc.append(acc[-1] + d)
    out = []
    j = 0
    i = 0
    while i < len(acc):
        j = i
        hit = None
        while j < len(acc) and c[j] - c[i] <= 7.0:
            if abs(acc[j] - acc[i]) >= 1.75 * math.pi:
                hit = j
                break
            j += 1
        if hit is not None:
            out.append(P[(i + hit) // 2])
            # skip to the end of this ring
            i = hit + 1
        else:
            i += 1
    return out


def node_of(name):
    m = re.match(r"^([a-z_]+):(\d+),(\d+)$", name)
    return (m.group(1), int(m.group(2)), int(m.group(3))) if m else None


looks = a.looks.split(",")
for look in looks:
    W = json.load(open(os.path.join(a.worlds, "ba_%s.json" % look)))
    lamps = [m for m in W["machines"] if m["kind"] == 3]
    lamp_tops = {(m["x"], m["z"] + 1) for m in lamps}
    for d in a.dirs:
        f = os.path.join(d, "ba_%s.out.json" % look)
        if not os.path.exists(f):
            continue
        L = json.load(open(f))
        pieces = L["pieces"]
        nodes = {}
        for p in pieces:
            for nm in (p["a"], p["b"]):
                if node_of(nm):
                    k, x, z = node_of(nm)
                    if k in ("junction", "strip", "stub_wall", "stub_rock", "terminal", "tangle", "spur"):
                        nodes[(x, z)] = k
        tally = {"selfX": [], "pairX": [], "overBox": [], "circle": [], "lampTop": []}
        by_node = {}
        for p in pieces:
            ends = set()
            for nm in (p["a"], p["b"]):
                if node_of(nm):
                    _, x, z = node_of(nm)
                    ends.add((x, z))
            if p["a"].startswith("tangle") or p["b"].startswith("tangle") or p["b"] == "":
                continue   # a heap's cables cross by design; a box's own decal piece has no cord
            cutEnd = "terminal" in p["a"] or "terminal" in p["b"] or p["a"].startswith("tangle") or p["b"] == ""
            for P in p["strands"]:
                if len(P) < 4:
                    continue
                c = cum(P)
                for (x, i, j) in self_crossings(P):
                    # a cut end's own curl (within 1.6 of either end) is its art
                    if cutEnd and (c[-1] - c[j] < 1.8 or c[i] < 1.8):
                        continue
                    tally["selfX"].append((p["a"] + "|" + p["b"], round(x[0], 2), round(x[1], 2)))
                for q in turning_windows(P, c):
                    tally["circle"].append((p["a"] + "|" + p["b"], round(q[0], 2), round(q[1], 2)))
                hitB = set()
                for q in P[3:-3]:
                    cell = (math.floor(q[0]), math.floor(q[1]))
                    for dx in (-1, 0, 1):
                        for dz in (-1, 0, 1):
                            nc = (cell[0] + dx, cell[1] + dz)
                            if nc in nodes and nc not in ends and nc not in hitB and nodes[nc] != "tangle":
                                if math.dist(q, (nc[0] + 0.5, nc[1] + 0.5)) < 0.4:
                                    hitB.add(nc)
                                    tally["overBox"].append((p["a"] + "|" + p["b"], nc[0], nc[1]))
                    if cell in lamp_tops and not any(math.dist(q, (lx + 0.5, lz + 0.5)) < 1.6 and (lx, lz) in ends for (lx, lz) in [(t[0], t[1] - 1) for t in lamp_tops]):
                        tally["lampTop"].append((p["a"] + "|" + p["b"], cell[0], cell[1]))
                for e in ends:
                    by_node.setdefault(e, []).append((p["a"] + "|" + p["b"], P))
        # pairs of cords off one node crossing near it
        for nd, lst in by_node.items():
            if nodes.get(nd) == "tangle":
                continue
            ctr = (nd[0] + 0.5, nd[1] + 0.5)
            for ii in range(len(lst)):
                for jj in range(ii + 1, len(lst)):
                    A = [q for q in lst[ii][1] if math.dist(q, ctr) < 1.2]
                    B = [q for q in lst[jj][1] if math.dist(q, ctr) < 1.2]
                    hit = False
                    for i in range(len(A) - 1):
                        if hit: break
                        if math.dist(A[i], A[i + 1]) > 0.2: continue
                        for j in range(len(B) - 1):
                            if math.dist(B[j], B[j + 1]) > 0.2: continue
                            if seg_x(A[i], A[i + 1], B[j], B[j + 1]):
                                hit = True
                                break
                    if hit:
                        tally["pairX"].append((lst[ii][0] + " x " + lst[jj][0], nd[0], nd[1]))
        # lampTop: dedupe per piece
        tally["lampTop"] = sorted(set(tally["lampTop"]))
        print("%-10s %-28s " % (look, d) + " ".join("%s=%d" % (k, len(v)) for k, v in tally.items()))
        if a.list:
            for k, v in tally.items():
                for row in v:
                    print("    ", k, row)
        prev = globals().get("_prev")
        if prev is not None and prev[0] == look:
            for k, v in tally.items():
                old = set((r[0],) for r in prev[1][k]); new = set((r[0],) for r in v)
                for r in sorted(new - old): print("     +", k, r[0], [x[1:] for x in v if x[0] == r[0]][:3])
                for r in sorted(old - new): print("     -", k, r[0])
        globals()["_prev"] = (look, tally)
