import json, sys, math
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from kink import kinks
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
d = json.load(open(sys.argv[1])); out = sys.argv[2]
x0, z0, x1, z1 = [float(v) for v in sys.argv[3].split(",")]
title = sys.argv[4] if len(sys.argv) > 4 else ""
fig, ax = plt.subplots(figsize=((x1 - x0) * 0.9, (z1 - z0) * 0.9), dpi=110)
n = 0
cols = ["#1f5fbf", "#2a8adf", "#0d3d8a", "#4aa0ff", "#173f6f", "#5b7fd0", "#0a6fb0"]
ci = 0
for p in d["pieces"]:
    for s in p["strands"]:
        if len(s) < 2 or not any(x0 <= x <= x1 and z0 <= z <= z1 for x, z in s): continue
        xs, zs = zip(*s); ax.plot(xs, zs, "-", lw=2.2, color=cols[ci % len(cols)]); ci += 1
        for a, x, z, deg in kinks(s):
            n += 1; ax.add_patch(plt.Circle((x, z), 0.18, fill=False, color="red", lw=2)); ax.text(x + 0.2, z + 0.15, "%.0f°" % deg, color="red", fontsize=9)
    for dc in p.get("decals", []):
        k, x, z = dc[0], dc[1], dc[2]
        if x0 <= x <= x1 and z0 <= z <= z1:
            ax.plot([x], [z], "s" if "Strip" in k else "o", ms=9 if "Strip" in k else 5, color="#444", alpha=.6); ax.text(x, z - .3, k, fontsize=6, color="#555")
ax.set_xlim(x0, x1); ax.set_ylim(z0, z1); ax.set_aspect("equal"); ax.grid(True, lw=.3)
ax.set_title("%s   kinks (>=50° turn within 0.12 cell): %d" % (title, n))
fig.tight_layout(); fig.savefig(out); print(out, "kinks", n)
