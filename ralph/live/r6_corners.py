"""Round 6: sharp local corners at strand ends. python3 ralph/live/r6_corners.py OUT.json [deg=45] [reach=0.5]: per strand end, the largest heading change across any 0.15-cell window within `reach` of the end."""
import json, math, sys
d = json.load(open(sys.argv[1])); lim = float(sys.argv[2]) if len(sys.argv) > 2 else 45; reach = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
def ang(a, b):
    return abs((math.degrees(math.atan2(a[0]*b[1]-a[1]*b[0], a[0]*b[0]+a[1]*b[1])) + 180) % 360 - 180)
def worst(s):
    pts = [tuple(p) for p in s]; arc = 0.0; best = (0, 0)
    for i in range(1, len(pts) - 1):
        a = (pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1]); arc += math.hypot(*a)
        if arc > reach: break
        w = 0.0
        for j in range(i + 1, len(pts)):
            b = (pts[j][0]-pts[j-1][0], pts[j][1]-pts[j-1][1]); w += math.hypot(*b)
            if w > 0.15: break
        else:
            continue
        t = ang(a, b) if math.hypot(*a) > 1e-9 and math.hypot(*b) > 1e-9 else 0
        if t > best[0]: best = (t, arc)
    return best
n = 0
for p in d["pieces"]:
    for s in p["strands"]:
        for end, pts in (("A", s), ("B", s[::-1])):
            t, arc = worst(pts)
            if t >= lim:
                n += 1; print("%-34s end %s turn %5.1f at %.2f  start %s" % (p["a"] + "|" + p["b"], end, t, arc, [round(x, 2) for x in pts[0]]))
print("corners>=%g within %g of an end: %d" % (lim, reach, n))
