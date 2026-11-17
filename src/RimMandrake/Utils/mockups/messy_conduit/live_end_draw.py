#!/usr/bin/env python3
"""Pictures of live cut ends for the invention sheet and the sweep (RIMMANDRAKE_INVENT_SLACK_LIVE_END_GREEN_BY_THIN_MARGIN)."""
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

import live_end_lib as L


def panel(ax, P, pos, out, title, blocked=(), cnt=0, frames=None, ties=(), worst=None, note="", view=None, far=None):
    """One cord: floor grid, blocked cells, the cord (static part dark, whipping tail orange), the whip's frames (thin), the conduit end, tie bands."""
    P = np.asarray(P, float)
    for b in blocked:
        ax.add_patch(Rectangle((b[0], b[1]), 1, 1, color="#9aa7b0" if b[2] else "#5b6168", zorder=0))
    n = len(P)
    if frames is not None:
        for fr in frames:
            ax.plot(fr[:, 0], fr[:, 1], color="#f0a030", lw=0.6, alpha=0.35, zorder=2)
    ax.plot(P[:n - cnt + 1, 0], P[:n - cnt + 1, 1], color="#202020", lw=2.2, zorder=3, solid_capstyle="round")
    if cnt > 0:
        ax.plot(P[n - cnt:, 0], P[n - cnt:, 1], color="#d06000", lw=2.2, zorder=4, solid_capstyle="round")
        ax.plot([P[n - cnt, 0]], [P[n - cnt, 1]], "o", color="#d06000", ms=4, zorder=5)
    if worst is not None:
        ax.plot(worst[:, 0], worst[:, 1], color="#c00000", lw=1.3, zorder=5)
    cl = L.cumlen(P)
    for (s0, s1) in ties:
        i = int(np.searchsorted(cl, s0))
        i = min(max(i, 0), n - 1)
        ax.plot([P[i, 0]], [P[i, 1]], "s", color="#1060c0", ms=7, zorder=6)
    o = np.array(out, float)
    p = np.array(pos, float)
    ax.annotate("", xy=p + o * 0.35, xytext=p, arrowprops=dict(arrowstyle="->", color="#0a8a2a", lw=1.5), zorder=6)
    ax.plot([p[0]], [p[1]], "*", color="#e8c000", ms=11, zorder=7, markeredgecolor="#806000")
    if far is not None:
        ax.plot([far[0]], [far[1]], "D", color="#3070b0", ms=6, zorder=6)
    ax.set_aspect("equal")
    if view is None:
        c = P[-min(n, 60):]
        x0, x1, z0, z1 = c[:, 0].min(), c[:, 0].max(), c[:, 1].min(), c[:, 1].max()
        m = 0.6
        view = (x0 - m, x1 + m, z0 - m, z1 + m)
    ax.set_xlim(view[0], view[1])
    ax.set_ylim(view[2], view[3])
    ax.set_xticks(np.arange(math.floor(view[0]), math.ceil(view[1]) + 1))
    ax.set_yticks(np.arange(math.floor(view[2]), math.ceil(view[3]) + 1))
    ax.grid(True, color="#d8d8d8", lw=0.6)
    ax.tick_params(labelsize=6)
    ax.set_facecolor("#f4f1ea")
    ax.set_title(title, fontsize=8)
    if note:
        ax.text(0.02, 0.02, note, transform=ax.transAxes, fontsize=7, va="bottom", bbox=dict(boxstyle="round", fc="white", ec="#888", alpha=0.85))


def save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
