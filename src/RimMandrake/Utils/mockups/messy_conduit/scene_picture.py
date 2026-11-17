#!/usr/bin/env python3
"""A picture of a built Gimme Some Slack scene (selftest_gimmesomeslack.py --scene-dump OUT.json fuzz:SEED[:STEP] | placed:N | family:N):

    python3 scene_picture.py SCENE.json OUT.png [--zoom X,Z,HALF ...]

The ground (walls dark, machines blue-grey, doors brown, conduit cells tinted), every cord, the fittings' art as outlines (a box's arms drawn
to their tips, plugs, plates, tie bands), and what the audits refuse, as red text. With --zoom, one panel per place besides the whole scene.
"""
import json
import math
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ARM = 55.5 / 128.0


def draw(ax, d, view, title):
    for b in d["blocked"]:
        ax.add_patch(Rectangle((b[0], b[1]), 1, 1, color={"Wall": "#5b6168", "Rock": "#6b5b4b", "Water": "#7fb0d8", "Device": "#b9c2cc"}.get(b[2], "#888"), zorder=0))
    for c in d["conduit"]:
        ax.add_patch(Rectangle((c[0] + 0.3, c[1] + 0.3), 0.4, 0.4, color="#ffe9a0" if c[2] else "#e2e2e2", zorder=1))
    for c in d["doors"]:
        ax.add_patch(Rectangle((c[0], c[1]), 1, 1, color="#b08050", alpha=0.6, zorder=1))
    for m in d["machines"]:
        ax.add_patch(Rectangle((m["x"], m["z"]), m["w"], m["h"], fill=False, edgecolor="#30507a", lw=1.5, zorder=2))
        ax.text(m["x"] + 0.05, m["z"] + 0.05, m["kind"][:4], fontsize=5, color="#30507a", zorder=2, clip_on=True)
    for p in d["pieces"]:
        for s in p["strands"]:
            xs, zs = [q[0] for q in s["pts"]], [q[1] for q in s["pts"]]
            ax.plot(xs, zs, color="#202020" if not s["over"] else "#a05050", lw=1.4, zorder=4, solid_capstyle="round")
        for c in p["decals"]:
            k, x, z, a, sc = c["kind"], c["x"], c["z"], c["a"], c["s"]
            if k in ("JunctionTin", "JunctionTape"):
                if k == "JunctionTin":
                    arms = [a + i * math.pi / 2 for i in range(4) if c["ports"] == 0 or c["ports"] & (1 << i)]
                    mx, mz = x, z
                else:
                    mx, mz = x - math.sin(a) * 0.152 * sc, z + math.cos(a) * 0.152 * sc
                    arms = [a, a + math.pi, a - math.pi / 2]
                for h in arms:
                    ax.plot([mx, mx + math.cos(h) * ARM * sc], [mz, mz + math.sin(h) * ARM * sc], color="#3a9a5a", lw=4.5, alpha=0.55, zorder=3, solid_capstyle="butt")
                ax.plot([mx], [mz], "s", color="#3a9a5a", ms=7, zorder=3)
            elif k == "CableTie":
                ax.plot([x], [z], "s", color="#1060c0", ms=5, zorder=6)
            elif k in ("FrayLive", "FrayDead"):
                ax.plot([x], [z], "*" if k == "FrayLive" else "X", color="#e8c000" if k == "FrayLive" else "#666", ms=9, zorder=6, markeredgecolor="k", markeredgewidth=0.3)
            else:
                ax.plot([x, x + math.cos(a) * 0.18], [z, z + math.sin(a) * 0.18], color="#c04080", lw=3, alpha=0.6, zorder=5)
                ax.text(x, z, k[:6], fontsize=4.5, color="#c04080", zorder=6, clip_on=True)
    ax.set_aspect("equal")
    ax.set_xlim(view[0], view[1])
    ax.set_ylim(view[2], view[3])
    ax.set_xticks(range(math.floor(view[0]), math.ceil(view[1]) + 1))
    ax.set_yticks(range(math.floor(view[2]), math.ceil(view[3]) + 1))
    ax.grid(True, color="#d8d8d8", lw=0.5)
    ax.tick_params(labelsize=5)
    ax.set_facecolor("#f4f1ea")
    ax.set_title(title, fontsize=7)


def main(argv):
    d = json.load(open(argv[0]))
    zooms = []
    for i, a in enumerate(argv):
        if a == "--zoom":
            x, z, h = [float(t) for t in argv[i + 1].split(",")]
            zooms.append((x - h, x + h, z - h, z + h))
    n = 1 + len(zooms)
    fig, axs = plt.subplots(1, n, figsize=(7.5 * n, 7.5))
    axs = [axs] if n == 1 else list(axs)
    draw(axs[0], d, (0, d["w"], 0, d["h"]), d["name"])
    for ax, v in zip(axs[1:], zooms):
        draw(ax, d, v, "zoom")
    axs[0].text(0.01, 0.99, "\n".join(x[:150] for x in d["bad"][:8]), transform=axs[0].transAxes, fontsize=5.5, color="#b00000", va="top")
    fig.tight_layout()
    fig.savefig(argv[1], dpi=120)
    print(len(d["bad"]), "refusals:", *[x[:160] for x in d["bad"][:6]], sep="\n  ")


if __name__ == "__main__":
    main(sys.argv[1:])
