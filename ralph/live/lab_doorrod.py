#!/usr/bin/env python3
"""How straight is a cord where it goes through a door? For every strand crossing a door cell, the straight run (within 0.15 cell of a chord)
that holds the crossing, in cells. A cord that bends right after the door reads about 1.2-1.6; a rod through the door reads 2.5 and up.

    python3 ralph/live/lab_doorrod.py IN_DIR OUT_DIR [--worst N]
"""
import glob, json, math, os, sys


def dense(s, step=0.1):
    q = []
    for i in range(1, len(s)):
        a, b = s[i - 1], s[i]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(L / step))
        for j in range(k):
            q.append((a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k))
    q.append(tuple(s[-1]))
    return q


def ok(q, i, j, tol):
    ax, az = q[i]
    bx, bz = q[j]
    L = math.hypot(bx - ax, bz - az)
    if L < 0.01:
        return False
    return all(abs((q[k][0] - ax) * (bz - az) - (q[k][1] - az) * (bx - ax)) / L <= tol for k in range(i, j + 1))


def run_at(q, m, tol=0.15):
    """Longest straight chord over q[i..j] with i <= m <= j, grown greedily both ways."""
    i, j = m, m
    while True:
        grew = False
        if i > 0 and ok(q, i - 1, j, tol):
            i -= 1; grew = True
        if j < len(q) - 1 and ok(q, i, j + 1, tol):
            j += 1; grew = True
        if not grew:
            break
    return math.hypot(q[j][0] - q[i][0], q[j][1] - q[i][1])


def main():
    ind, outd = sys.argv[1], sys.argv[2]
    worst = int(sys.argv[sys.argv.index("--worst") + 1]) if "--worst" in sys.argv else 8
    rows = []
    for f in sorted(glob.glob(os.path.join(outd, "*.out.json"))):
        name = os.path.basename(f)[:-9]
        W = json.load(open(os.path.join(ind, name + ".json")))
        doors = set(tuple(d) for d in W.get("doors") or [])
        L = json.load(open(f))
        for p in L["pieces"]:
            for s in p["strands"]:
                if len(s) < 6:
                    continue
                q = dense(s)
                seen = set()
                for m, (x, z) in enumerate(q):
                    c = (int(math.floor(x)), int(math.floor(z)))
                    if c in doors and c not in seen:
                        # the middle of this pass through the door
                        k = m
                        while k + 1 < len(q) and (int(math.floor(q[k + 1][0])), int(math.floor(q[k + 1][1]))) == c:
                            k += 1
                        seen.add(c)
                        rows.append((run_at(q, (m + k) // 2), name, c, p["a"], p["b"]))
    v = sorted(r[0] for r in rows)
    if not v:
        print("no door crossings"); return
    print("door crossings", len(v), "median %.2f" % v[len(v) // 2], "p90 %.2f" % v[int(len(v) * 0.9)], "max %.2f" % v[-1],
          "over 2.0:", sum(x > 2.0 for x in v), "over 2.5:", sum(x > 2.5 for x in v), "over 3:", sum(x > 3 for x in v))
    for r in sorted(rows, key=lambda r: -r[0])[:worst]:
        print("  %.2f %s door %s  %s | %s" % r)


if __name__ == "__main__":
    main()
