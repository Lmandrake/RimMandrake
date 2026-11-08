#!/usr/bin/env python3
"""Draw the heap-walk trace the self-test's --shape-diag writes (heapwalk_trace.json): ground, stops, each attempt (green came round, red left the ground).
python3 ralph/live/heapwalk_plot.py TRACE.json OUT.png"""
import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
T = json.load(open(sys.argv[1]))
W = T["walks"]
n = len(W)
cols = 6
rows = (n + cols - 1) // cols
fig, axs = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3))
g = T["ground"]
for i, ax in enumerate(axs.flat):
    ax.set_axis_off()
    if i >= n: continue
    w = W[i]
    ax.scatter([p[0] for p in g], [p[1] for p in g], s=1, c="#d8c8a8")
    for d in T["decals"]:
        ax.plot(d[1], d[2], "s", c="#555", ms=5)
    xs = [p[0] for p in w["pts"]]; zs = [p[1] for p in w["pts"]]
    ax.plot(xs, zs, c="g" if w["done"] else "r", lw=1)
    ax.plot(xs[0], zs[0], "o", c="b", ms=3)
    for k, s in enumerate(w["stops"]):
        ax.plot(s[0], s[1], "x", c="k")
        ax.text(s[0], s[1], str(k), fontsize=6)
    ax.set_xlim(5, 12); ax.set_ylim(5, 12); ax.set_aspect("equal")
plt.tight_layout()
plt.savefig(sys.argv[2], dpi=70)
