#!/usr/bin/env python3
"""The longest straight run in each laid world: a rod is what the owner ruled out. python3 ralph/live/lab_straight.py OUTDIR [--worst N] or a single LAID.json"""
import glob, json, math, os, sys


def straight(s, tol=0.15):
    q = []
    for i in range(1, len(s)):
        a, b = s[i - 1], s[i]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(L / 0.1))
        for j in range(k):
            q.append((a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k))
    q.append(tuple(s[-1]))
    best, at, n = 0, None, len(q)
    for i in range(0, n, 3):
        j = i + 10
        while j < n:
            ax, az = q[i]
            bx, bz = q[j]
            L = math.hypot(bx - ax, bz - az)
            if L < 0.01:
                break
            if not all(abs((q[k][0] - ax) * (bz - az) - (q[k][1] - az) * (bx - ax)) / L <= tol for k in range(i, j, 2)):
                break
            if L > best:
                best, at = L, ((ax + bx) / 2, (az + bz) / 2)
            j += 3
    return best, at


def main():
    p = sys.argv[1]
    if os.path.isfile(p):
        L = json.load(open(p))
        rows = sorted(((straight(s), x["a"], x["b"]) for x in L["pieces"] for s in x["strands"] if len(s) > 6), key=lambda r: -r[0][0])
        vals = [r[0][0] for r in rows]
        print("strands", len(vals), "over 3 cells", sum(v > 3 for v in vals), "over 4", sum(v > 4 for v in vals), "over 5", sum(v > 5 for v in vals))
        for r in rows[:6]:
            print("  %.1f at %s  %s | %s" % (r[0][0], [round(v, 1) for v in r[0][1]], r[1], r[2]))
        return
    rows = {}
    for f in sorted(glob.glob(os.path.join(p, "*.out.json"))):
        n = os.path.basename(f)[:-9].rsplit("_s", 1)[0]
        L = json.load(open(f))
        rows.setdefault(n, []).append(round(max([straight(s)[0] for x in L["pieces"] for s in x["strands"] if len(s) > 6] or [0]), 1))
    allv = [v for r in rows.values() for v in r]
    print("worlds", len(allv), "worst over 3:", sum(v > 3 for v in allv), "over 4:", sum(v > 4 for v in allv), "over 5:", sum(v > 5 for v in allv), "max", max(allv))
    for k in sorted(rows):
        print("  %-20s %s" % (k, rows[k]))


if __name__ == "__main__":
    main()
