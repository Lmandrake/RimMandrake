#!/usr/bin/env python3
"""Pictures of the oracle scenes as the C# builder lays them (selftest_gimmesomeslack.py --dump DIR), zoomed on every live end and tie band:
    python3 live_end_scenes.py DUMP_DIR OUT_DIR [scene ...]
(RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN: a cord that passes the bars and looks wrong is a finding.)"""
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

MK = {"CableTie": ("s", "#1060c0", 7), "FrayLive": ("*", "#e8c000", 12), "FrayDead": ("X", "#666", 8), "JunctionTin": ("s", "#8a8f98", 14),
      "JunctionTape": ("s", "#8a8f98", 14), "Plug": (">", "#333", 8), "PlugTop": ("o", "#333", 6), "PowerStrip": ("s", "#b0a080", 12),
      "PowerStripDark": ("s", "#806040", 12), "StubWall": ("D", "#555", 8), "StubRock": ("D", "#855", 8), "WallOutlet": ("D", "#335", 8)}


def draw(ax, d, view, title):
    for s in d["strands"]:
        p = np.array(s["pts"])
        ax.plot(p[:, 0], p[:, 1], color="#202020" if not s["over"] else "#a05050", lw=1.6, solid_capstyle="round")
    for c in d["decals"]:
        m = MK.get(c["kind"], (".", "r", 5))
        ax.plot([c["x"]], [c["z"]], m[0], color=m[1], ms=m[2], alpha=0.85, markeredgecolor="k", markeredgewidth=0.3)
    ax.set_aspect("equal")
    ax.set_xlim(view[0], view[1])
    ax.set_ylim(view[2], view[3])
    ax.set_facecolor("#f4f1ea")
    ax.grid(True, color="#d8d8d8", lw=0.5)
    ax.set_xticks(range(math.floor(view[0]), math.ceil(view[1]) + 1))
    ax.set_yticks(range(math.floor(view[2]), math.ceil(view[3]) + 1))
    ax.tick_params(labelsize=6)
    ax.set_title(title, fontsize=8)


def main(argv):
    src, out = argv[0], argv[1]
    names = argv[2:] or sorted(f[:-10] for f in os.listdir(src) if f.endswith(".laid.json"))
    for name in names:
        d = json.load(open(os.path.join(src, name + ".laid.json")))
        seen, sp = [], []
        for c in d["decals"]:
            if c["kind"] == "FrayLive" and all(math.hypot(c["x"] - a, c["z"] - b) > 0.5 for a, b in seen):
                seen.append((c["x"], c["z"]))
                sp.append(("live end", c["x"], c["z"]))
        sp = sp[:6] + [("tied loop", c["x"], c["z"]) for c in d["decals"] if c["kind"] == "CableTie"][:3]
        n = len(sp) + 1
        cols = min(4, n)
        rows = (n + cols - 1) // cols
        fig, axs = plt.subplots(rows, cols, figsize=(5.2 * cols, 5.2 * rows))
        axs = np.array(axs).reshape(-1)
        draw(axs[0], d, (0, d["w"], 0, d["h"]), name + ": whole scene (stars = live ends, blue squares = tie bands)")
        for k, (t, x, z) in enumerate(sp, 1):
            draw(axs[k], d, (x - 1.7, x + 1.7, z - 1.7, z + 1.7), "%s: %s at (%.1f, %.1f)" % (name, t, x, z))
        for k in range(len(sp) + 1, len(axs)):
            axs[k].axis("off")
        fig.tight_layout()
        fig.savefig(os.path.join(out, "after_%s.png" % name), dpi=110)
        plt.close(fig)
        print(name, len(sp), "spots")


if __name__ == "__main__":
    main(sys.argv[1:])
