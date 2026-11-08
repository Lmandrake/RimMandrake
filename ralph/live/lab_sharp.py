#!/usr/bin/env python3
"""Sharp bends on every laid strand, ends included (prototype of CordShapeAudit.SharpBends, the never_taut_straight_cord count).

    python3 ralph/live/lab_sharp.py WORLD.json LAID.json [--crops OUTDIR] [--turn 90] [--arc 1.0]

A bend is a stretch where the cord's heading turns past --turn degrees within --arc cells of cord (signed turning summed, so an S
wiggle does not count). Forced: the apex is within 0.3 cell of a wall, rock or a machine that is not the strand's own end, or the
bend sits within 0.6 cell of a door. Prints one line per bend and a count per class.
"""
import argparse, json, math, os, sys


def resample(pts, step=0.05):
    out = [tuple(pts[0])]
    carry = 0.0
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        seg = math.hypot(bx - ax, bz - az)
        if seg < 1e-9:
            continue
        d = step - carry
        while d <= seg:
            t = d / seg
            out.append((ax + (bx - ax) * t, az + (bz - az) * t))
            d += step
        carry = seg - (d - step)
    if math.hypot(out[-1][0] - pts[-1][0], out[-1][1] - pts[-1][1]) > 1e-6:
        out.append(tuple(pts[-1]))
    return out


def bends(pts, turn_deg=90.0, arc=1.0, step=0.05):
    q = resample(pts, step)
    n = len(q)
    if n < 4:
        return []
    hd = [math.atan2(q[k + 1][1] - q[k][1], q[k + 1][0] - q[k][0]) for k in range(n - 1)]
    t = [0.0] * n   # signed turn at sample k (between segment k-1 and k)
    for k in range(1, n - 1):
        d = hd[k] - hd[k - 1]
        while d > math.pi: d -= 2 * math.pi
        while d < -math.pi: d += 2 * math.pi
        t[k] = d
    win = max(2, int(round(arc / step)))
    thr = math.radians(turn_deg)
    mark = [False] * n
    for i in range(1, n - 1):
        s = 0.0
        for j in range(i, min(n - 1, i + win)):
            s += t[j]
            if abs(s) > thr:
                for k in range(i, j + 1):
                    mark[k] = True
                break
    out = []
    k = 0
    cum = [0.0]
    for a, b in zip(q, q[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    L = cum[-1]
    while k < n:
        if not mark[k]:
            k += 1
            continue
        j = k
        while j + 1 < n and mark[j + 1]:
            j += 1
        tot = sum(t[k:j + 1])
        # apex: the sharpest point (largest turn over +-0.1 cell)
        w2 = max(1, int(0.1 / step))
        best, apex = -1, k
        for m in range(k, j + 1):
            v = abs(sum(t[max(1, m - w2):min(n - 1, m + w2 + 1)]))
            if v > best:
                best, apex = v, m
        # how far the turning keeps going one way around the bend: a coil goes round, a hairpin stops
        lo, hi = k, j
        sg = 1 if tot >= 0 else -1
        while lo > 1 and t[lo - 1] * sg > -0.02:
            lo -= 1
        while hi < n - 2 and t[hi + 1] * sg > -0.02:
            hi += 1
        oneway = abs(sum(t[lo:hi + 1]))
        out.append(dict(apex=q[apex], s=cum[apex], fromEnd=min(cum[apex], L - cum[apex]), turn=math.degrees(abs(tot)),
                        arc=cum[j] - cum[k], sharp=math.degrees(best), roundDeg=math.degrees(oneway), L=L))
        k = j + 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("world"); ap.add_argument("laid")
    ap.add_argument("--turn", type=float, default=90); ap.add_argument("--arc", type=float, default=1.0)
    ap.add_argument("--json", default="")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    W = json.load(open(a.world)); Lj = json.load(open(a.laid))
    blocked = {(x, z) for x, z, k in W["blocked"]}
    doors = {tuple(c) for c in W["doors"]}
    mach = W["machines"]

    def near_cell(p, cells, r):
        x, z = p
        for cx in range(int(math.floor(x - r)) - 1, int(math.floor(x + r)) + 2):
            for cz in range(int(math.floor(z - r)) - 1, int(math.floor(z + r)) + 2):
                if (cx, cz) in cells:
                    dx = max(cx - x, 0, x - (cx + 1)); dz = max(cz - z, 0, z - (cz + 1))
                    if math.hypot(dx, dz) <= r:
                        return (cx, cz)
        return None

    def mach_at(p, r, own):
        x, z = p
        for m in mach:
            if m["id"] in own:
                continue
            dx = max(m["x"] - x, 0, x - (m["x"] + m["w"])); dz = max(m["z"] - z, 0, z - (m["z"] + m["h"]))
            if math.hypot(dx, dz) <= r:
                return m
        return None

    def own_machines(piece):
        o = set()
        for e in (piece["a"], piece["b"]):
            if ":" not in e:
                continue
            kind, xy = e.split(":", 1)
            try:
                cx, cz = [int(v) for v in xy.split(",")[:2]]
            except ValueError:
                continue
            for m in mach:
                if m["x"] <= cx < m["x"] + m["w"] and m["z"] <= cz < m["z"] + m["h"]:
                    o.add(m["id"])
                for h in m["hookups"]:
                    if tuple(h) == (cx, cz):
                        o.add(m["id"])
        return o

    rows = []
    for p in Lj["pieces"]:
        own = own_machines(p)
        name = p["a"] + ("|" + p["b"] if p["b"] else "")
        for s in p["strands"]:
            for b in bends(s, a.turn, a.arc):
                why = None
                c = near_cell(b["apex"], blocked, 0.3)
                if c:
                    why = "wall%s" % (c,)
                m = mach_at(b["apex"], 0.3, own)
                if not why and m:
                    why = "machine:" + m["id"]
                d = near_cell(b["apex"], doors, 0.6)
                if not why and d:
                    why = "door%s" % (d,)
                cls = "loop" if b["roundDeg"] >= 300 else ("end" if b["fromEnd"] < 0.6 else "mid")
                b.update(piece=name, forced=why, cls=cls)
                rows.append(b)
    unf = [r for r in rows if not r["forced"]]
    from collections import Counter
    if not a.quiet:
        for r in sorted(rows, key=lambda r: (r["forced"] is not None, r["cls"], r["piece"])):
            print("%-6s %-24s apex=(%.2f,%.2f) turn=%3.0f arc=%.2f sharp=%3.0f round=%3.0f fromEnd=%.2f L=%.1f %s" % (
                r["cls"], (r["forced"] or "UNFORCED")[:24], r["apex"][0], r["apex"][1], r["turn"], r["arc"], r["sharp"], r["roundDeg"], r["fromEnd"], r["L"], r["piece"]))
    print("bends", len(rows), "unforced", len(unf), "by class", dict(Counter(r["cls"] for r in unf)), "forced", dict(Counter((r["forced"] or "").split("(")[0].split(":")[0] for r in rows if r["forced"])))
    if a.json:
        json.dump(rows, open(a.json, "w"))


if __name__ == "__main__":
    main()
