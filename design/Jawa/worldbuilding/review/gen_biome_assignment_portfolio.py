#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_biome_assignment_portfolio.py — figs 9–11: what the LANDED assignment
actually looks like, per biome.

Sibling of gen_creature_distribution_portfolio.py (figs 4–8, the register's own
economy/lethality questions). This file asks the three questions only the rosters
can answer, and it asks them of the rosters ONLY:

  fig9  commonality mass   Σ(commonality) and roster row count per BiomeDef, each
                           bar tagged with its sheet's stated population doctrine.
                           THE NORMALIZATION INSTRUMENT: commonality is a design
                           choice, so the doctrine is the only thing that can say
                           whether a biome's mass is right. Biomes whose sheet
                           states no population doctrine are marked "unstated" —
                           never given an invented one.
  fig10 size ladder        per-biome bodySize strip plot (every rostered creature
                           one point, bodySize MEASURED from the register), with
                           Large Pawns' live multi-cell thresholds (2.5 / 4.5 / 10)
                           and TITANIC_CREATURES_MOD_1's draft tier boundaries
                           (4 / 8 / 20) drawn as reference lines. Feeds that item:
                           its tier table says "tune at build against the actual
                           roster census; the assignment pass's size-ladder figure
                           is the instrument."
  fig11 biome matrix       rostered def × BiomeDef presence matrix, rows grouped by
                           primary sheet, injection-layer cells marked distinctly.
                           The zoo-effect picture: how block-diagonal did the
                           assignment actually get?

DATA HONESTY
  residency + commonality : biomes/rosters/*.json via rosters_residency.py.
                            Commonality is a DESIGN CHOICE, never a measured stat,
                            and every axis carrying it says so.
  bodySize                 : creature_register_rows.json — MEASURED (sqlite def
                            dump, calibrated on Muffalo). Rosters may carry a
                            DESIGNED stat_adjustment; those points are drawn open.
  population doctrine      : the `animals` column of
                            design/Jawa/worldbuilding/biomes/_freeze_matrix.csv —
                            the sheets' own condensation of their §5/§6 population
                            law, one row per sheet. A sheet with no row there is
                            "doctrine unstated", printed as such.
  ⛔ the register's `biomes` / `group` / `topCommonality` are NEVER read here.

Run from repo root:
  python3 design/Jawa/worldbuilding/review/gen_biome_assignment_portfolio.py
"""
from __future__ import annotations

import collections
import csv
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rosters_residency as RR

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VIZ = os.path.join(HERE, "viz")
BIOMES = os.path.abspath(os.path.join(HERE, "..", "biomes"))
FREEZE = os.path.join(BIOMES, "_freeze_matrix.csv")
TITAN = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..",
                                     "infrastructure", "state", "items",
                                     "TITANIC_CREATURES_MOD_1.md"))
os.makedirs(VIZ, exist_ok=True)

ROST = RR.load()
REG = RR.load_register_stats()
META = RR.register_meta()

C_GRAY = "#9aa0a6"; C_BLUE = "#3b6fb5"; C_ORANGE = "#d97706"; C_RED = "#c0392b"
C_GREEN = "#2e7d4f"; C_DARK = "#333333"; C_PURPLE = "#6b4fa0"
FOOT = dict(fontsize=7.0, color="#666666")

# Large Pawns (neku.largepawns, ACTIVE in the live list) — MEASURED from the item:
# bodySize ≥2.5 → 2x2, ≥4.5 → 3x3, ≥10 → 4x4.
LARGEPAWNS = [(2.5, "2×2"), (4.5, "3×3"), (10.0, "4×4")]
# TITANIC_CREATURES_MOD_1 draft tier table — BENCH DRAFT, explicitly not ruled.
TITAN_TIERS = [(4.0, 8.0, "T1 heavy"), (8.0, 20.0, "T2 colossal"), (20.0, 1e9, "T3 titanic")]


# ---------------------------------------------------------------- doctrine
def load_doctrine():
    """sheet -> stated population doctrine, from _freeze_matrix.csv's `animals`
    column (the sheets' own condensation). Missing = unstated, never invented."""
    rows = {}
    with open(FREEZE, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[r["sheet"].strip()] = (r.get("animals") or "").strip()
    out = {}
    for sheet in ROST.sheets:
        parts = [p.strip() for p in sheet.split("+")]
        got = [rows[p] for p in parts if rows.get(p)]
        out[sheet] = " · ".join(got) if got else None
    return out


DOCTRINE = load_doctrine()


def biome_doctrine(biome):
    """Doctrine for a BiomeDef = the doctrine of the sheet(s) that roster it,
    excluding injection layers (they add over a host, they do not set its law)."""
    txt, unstated = [], []
    for sheet in ROST.sheets_of_biome.get(biome, []):
        if ROST.is_injection(sheet):
            continue
        d = DOCTRINE.get(sheet)
        (txt if d else unstated).append(d or sheet)
    if txt:
        return " · ".join(dict.fromkeys(txt)), True
    return "doctrine unstated (%s)" % ", ".join(unstated or ["no sheet"]), False


DESIGNED = collections.defaultdict(dict)
for _a in ROST.stat_adjustments:
    DESIGNED[_a["def"]][_a["field"]] = _a["to"]


def bodysize(defName):
    """(bodySize, is_designed). MEASURED unless a roster adjusts it."""
    if "bodySize" in DESIGNED.get(defName, {}):
        return DESIGNED[defName]["bodySize"], True
    return REG.get(defName, {}).get("bodySize"), False


def src_line():
    return ("Residency + commonality: design/Jawa/worldbuilding/biomes/rosters/*.json (authored 2026-09-09) via rosters_residency.py — commonality is a DESIGN\n"
            "CHOICE, not a measured stat. Stats: creature_register_rows.json (%s, dump %s mods, captured %s) — MEASURED.\n"
            "NEVER READ HERE: the register's own biomes/group/topCommonality — that is the MODS' default residency on a vanilla planet, stale for placement."
            % (META["generator"], META["dumpMods"], META["dumpCaptured"][:10]))


# ------------------------------------------------------------ fig 9: commonality mass
def fig9():
    rows = []
    for b in ROST.biome_defs:
        res = ROST.residents(b)
        base = [r for r in res if not r.injection]
        inj = [r for r in res if r.injection]
        doc, stated = biome_doctrine(b)
        rows.append(dict(biome=b, n=len(base), n_inj=len(inj),
                         mass=sum(r.commonality for r in base),
                         mass_inj=sum(r.commonality for r in inj),
                         doc=doc, stated=stated,
                         tiles=max((ROST.tiles(s) for s in ROST.sheets_of_biome[b]
                                    if not ROST.is_injection(s)), default=0)))
    rows.sort(key=lambda r: (r["mass"] + r["mass_inj"]))

    fig, (ax, axn) = plt.subplots(1, 2, figsize=(15.2, 11.0), dpi=150,
                                  gridspec_kw=dict(width_ratios=[3.0, 1.0], wspace=0.02))
    y = np.arange(len(rows))
    ax.barh(y, [r["mass"] for r in rows], height=0.62, color=C_BLUE, zorder=3,
            label="base roster Σ commonality")
    ax.barh(y, [r["mass_inj"] for r in rows], left=[r["mass"] for r in rows],
            height=0.62, color=C_ORANGE, zorder=3, label="injection layer (Fall Line) Σ commonality")
    for i, r in enumerate(rows):
        tot = r["mass"] + r["mass_inj"]
        ax.text(tot + 0.22, i, "%.2f" % tot, va="center", fontsize=7.0, color=C_DARK, zorder=4)
        ax.text(0.22, i + 0.34, r["doc"][:96], va="bottom", fontsize=6.3,
                color=(C_DARK if r["stated"] else C_RED),
                style="normal" if r["stated"] else "italic", zorder=5)
    axn.barh(y, [r["n"] for r in rows], height=0.62, color="#b9c6da", zorder=3)
    axn.barh(y, [r["n_inj"] for r in rows], left=[r["n"] for r in rows],
             height=0.62, color="#f0d4a8", zorder=3)
    for i, r in enumerate(rows):
        t = r["n"] + r["n_inj"]
        axn.text(t + 0.7, i, "%d%s" % (t, (" (+%d inj)" % r["n_inj"]) if r["n_inj"] else ""),
                 va="center", fontsize=6.8, color=C_DARK)

    labs = ["%s   [%s]" % (r["biome"], ("%d tiles" % r["tiles"]) if r["tiles"] else "injected/untiled")
            for r in rows]
    ax.set_yticks(y); ax.set_yticklabels(labs, fontsize=7.6)
    ax.set_ylim(-0.7, len(rows) - 0.25)
    ax.set_xlim(0, max(r["mass"] + r["mass_inj"] for r in rows) * 1.16)
    ax.set_xlabel("Σ spawn commonality across the biome's roster  (a DESIGN CHOICE, not a measured stat)")
    ax.grid(True, axis="x", lw=0.4, alpha=0.3, zorder=0)
    ax.legend(loc="lower right", fontsize=7.4, framealpha=0.95)
    axn.set_yticks(y); axn.set_yticklabels([]); axn.set_ylim(ax.get_ylim())
    axn.set_xlim(0, max(r["n"] + r["n_inj"] for r in rows) * 1.3)
    axn.set_xlabel("roster rows (species)", fontsize=8.5)
    axn.grid(True, axis="x", lw=0.4, alpha=0.3, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False); axn.spines[s].set_visible(False)

    hi, lo = rows[-1], next(r for r in rows if r["mass"] + r["mass_inj"] > 0)
    nstated = sum(1 for r in rows if r["stated"])
    ax.set_title("Commonality mass per biome — the normalization instrument.  Heaviest %s (Σ %.2f over %d species); "
                 "lightest non-empty %s (Σ %.2f over %d).\nGrey italic = the sheet states NO population doctrine, so nothing here can say whether its mass is right (%d of %d biomes stated)"
                 % (hi["biome"], hi["mass"] + hi["mass_inj"], hi["n"] + hi["n_inj"],
                    lo["biome"], lo["mass"] + lo["mass_inj"], lo["n"] + lo["n_inj"],
                    nstated, len(rows)), fontsize=10.5, loc="left")
    fig.text(0.008, 0.014,
             "One bar per BiomeDef the rosters bind (%d). Doctrine text above each bar is the sheet's own population law, verbatim from the `animals` column of\n"
             "biomes/_freeze_matrix.csv (its condensation of the sheet's §5/§6); a sheet with no row there is printed in red italic as UNSTATED and is NOT given an\n"
             "invented one. Tiles are the roster's own MEASURED tile count. Σ commonality is comparable BETWEEN biomes only as an authored weight — RimWorld resolves\n"
             "actual spawn counts from commonality × the biome's animalDensity, which this figure does not carry.\n%s" % (len(rows), src_line()), **FOOT)
    fig.subplots_adjust(left=0.175, right=0.985, top=0.935, bottom=0.155)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(VIZ, "fig9_commonality_mass.%s" % ext))
    plt.close(fig)
    return dict(n_biomes=len(rows), stated=nstated,
                top=[(r["biome"], round(r["mass"] + r["mass_inj"], 2), r["n"] + r["n_inj"]) for r in rows[::-1][:6]],
                bottom=[(r["biome"], round(r["mass"] + r["mass_inj"], 3), r["n"] + r["n_inj"]) for r in rows[:6]],
                unstated=[r["biome"] for r in rows if not r["stated"]])


# ------------------------------------------------------------ fig 10: size ladder
def fig10():
    rows = []
    for b in ROST.biome_defs:
        pts = []
        for q in ROST.residents(b):
            bs, des = bodysize(q.defName)
            if isinstance(bs, (int, float)) and bs > 0:
                pts.append((q.defName, bs, q.commonality, q.injection, des))
        if pts:
            rows.append((b, pts))
    rows.sort(key=lambda t: max(p[1] for p in t[1]))

    fig, ax = plt.subplots(figsize=(14.6, 10.6), dpi=150)
    rng = np.random.default_rng(23)
    for lo, hi, name in TITAN_TIERS:
        ax.axvspan(lo, min(hi, 60), color="#f3eef8" if name != "T3 titanic" else "#e7dcf2", zorder=0)
    for x, fp in LARGEPAWNS:
        ax.axvline(x, color=C_GREEN, lw=1.1, ls="--", zorder=2)
    for lo, _, name in TITAN_TIERS:
        ax.axvline(lo, color=C_PURPLE, lw=1.0, ls=":", zorder=2)

    for i, (b, pts) in enumerate(rows):
        ys = i + rng.uniform(-0.28, 0.28, len(pts))
        for (d, bs, c, inj, des), yy in zip(pts, ys):
            ax.scatter(bs, yy, s=10 + 44 * math.sqrt(min(c, 1.5)),
                       facecolors="none" if des else (C_ORANGE if inj else C_BLUE),
                       edgecolors=C_ORANGE if inj else C_BLUE,
                       linewidths=1.1 if des else 0,
                       marker="D" if inj else "o", alpha=0.72, zorder=4)
        big = sorted(pts, key=lambda p: -p[1])[0]
        # Only the T2+ giants get a name: below 8 the labels repeat across the
        # rows that share a creature (the three Forge defs share one roster) and
        # the column turns into noise.
        if big[1] >= 8.0:
            right = big[1] > 22          # keep the bs-40 whale's label inside the axes
            ax.annotate("%s %.4g" % (big[0], big[1]), (big[1], i),
                        xytext=(big[1] * (0.88 if right else 1.15), i + 0.34),
                        ha="right" if right else "left", fontsize=6.8, color=C_DARK, zorder=6)

    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(["%s  (n=%d)" % (b, len(p)) for b, p in rows], fontsize=7.8)
    ax.set_xscale("log"); ax.set_xlim(0.007, 90); ax.set_ylim(-0.8, len(rows) - 0.2)
    ax.set_xlabel("bodySize (log) — MEASURED from the register; open markers carry a roster stat_adjustment (DESIGNED)")
    # Line labels ride INSIDE the axes on two alternating rows: a shared secondary
    # x-axis put "LP 3×3 4.5" on top of "T1 heavy 4" and both became unreadable.
    ytop = len(rows) - 0.35
    for x, fp in LARGEPAWNS:
        ax.text(x, ytop, " LP %s (%.4g)" % (fp, x), rotation=90, fontsize=6.6,
                color=C_GREEN, ha="left", va="top", zorder=7)
    for lo, _, name in TITAN_TIERS:
        ax.text(lo, ytop - 4.2, " %s (%.4g)" % (name, lo), rotation=90, fontsize=6.6,
                color=C_PURPLE, ha="left", va="top", zorder=7)
    ax.grid(True, axis="x", which="major", lw=0.4, alpha=0.3, zorder=1)
    for s in ("top", "right"): ax.spines[s].set_visible(False)

    census = collections.Counter()
    tiered = collections.defaultdict(set)
    for d in ROST.residency:
        bs, _ = bodysize(d)
        if not isinstance(bs, (int, float)):
            continue
        for lo, hi, name in TITAN_TIERS:
            if lo <= bs < hi:
                census[name] += 1
                tiered[name].add(d)
    lp = collections.Counter()
    for d in ROST.residency:
        bs, _ = bodysize(d)
        if isinstance(bs, (int, float)):
            for x, fp in LARGEPAWNS:
                if bs >= x:
                    lp[fp] += 1

    ax.legend(handles=[Line2D([], [], marker="o", ls="", c=C_BLUE, label="base-roster resident"),
                       Line2D([], [], marker="D", ls="", c=C_ORANGE, label="injection layer (Fall Line)"),
                       Line2D([], [], marker="o", ls="", mfc="none", mec=C_BLUE, label="roster stat_adjustment (DESIGNED)"),
                       Line2D([], [], c=C_GREEN, ls="--", lw=1.1, label="Large Pawns multi-cell threshold (LIVE mod: 2.5 / 4.5 / 10)"),
                       Line2D([], [], c=C_PURPLE, ls=":", lw=1.0, label="TITANIC_CREATURES_MOD_1 draft tier (4 / 8 / 20 — NOT ruled)")],
              loc="lower left", fontsize=7.2, framealpha=0.96)
    ax.set_title("The size ladder the rosters actually landed — and the two ladders that will act on it.  Titan-tier census (distinct rostered defs):\n"
                 "T1 heavy 4–8: %d   ·   T2 colossal 8–20: %d   ·   T3 titanic 20+: %d.   Large Pawns would make %d rostered defs 2×2 or bigger (%d at 3×3, %d at 4×4)."
                 % (census["T1 heavy"], census["T2 colossal"], census["T3 titanic"],
                    lp["2×2"], lp["3×3"], lp["4×4"]), fontsize=10.5, loc="left")
    fig.text(0.008, 0.015,
             "Every rostered creature is one point (marker AREA ∝ √commonality, disclosed); a def landed in k biomes appears k times, once per biome — this is a per-biome\n"
             "ladder, not a species census (the census is in the title, over distinct defs). Rows sorted by their largest resident. X log (disclosed). Large Pawns thresholds\n"
             "are MEASURED from the live mod (neku.largepawns, ACTIVE); the 4/8/20 tier boundaries are the TITANIC_CREATURES_MOD_1 DRAFT, which its own table says to tune\n"
             "against this figure — the two ladders currently disagree, which is the item's open decision, not a defect here.\n%s" % src_line(), **FOOT)
    fig.subplots_adjust(left=0.20, right=0.985, top=0.925, bottom=0.155)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(VIZ, "fig10_size_ladder.%s" % ext))
    plt.close(fig)
    return dict(census={k: sorted(v) for k, v in tiered.items()},
                largepawns={k: v for k, v in lp.items()},
                biomes=len(rows))


# ------------------------------------------------------------ fig 11: biome matrix
def fig11():
    defs = sorted(ROST.residency, key=lambda d: (ROST.primary_sheet(d) or "~", -ROST.top_commonality(d), d))
    biomes = ROST.biome_defs
    bi = {b: i for i, b in enumerate(biomes)}
    M = np.zeros((len(defs), len(biomes)), int)   # 0 absent, 1 base, 2 injection
    for i, d in enumerate(defs):
        for q in ROST.residency[d]:
            M[i, bi[q.biome]] = 2 if q.injection else 1

    fig, ax = plt.subplots(figsize=(12.4, 16.0), dpi=150)
    cmap = ListedColormap(["#f4f2ec", C_BLUE, C_ORANGE])
    ax.imshow(M, cmap=cmap, norm=BoundaryNorm([-0.5, 0.5, 1.5, 2.5], 3),
              aspect="auto", interpolation="nearest")

    # sheet blocks
    prim = [ROST.primary_sheet(d) for d in defs]
    bounds, cur = [], prim[0]
    for i, p in enumerate(prim):
        if p != cur:
            bounds.append(i); cur = p
    for y in bounds:
        ax.axhline(y - 0.5, color="#555555", lw=0.55)
    for x in range(1, len(biomes)):
        ax.axvline(x - 0.5, color="#dddddd", lw=0.35)
    starts = [0] + bounds
    ends = bounds + [len(defs)]
    # 242 rows in 16 inches is ~4.8 pt per row, so consecutive 1-2 row blocks
    # collide at any readable size: alternate the label into a second gutter
    # column whenever the previous label is closer than 4 rows.
    last_y, alt = -99.0, False
    for s0, e0 in zip(starts, ends):
        cy = (s0 + e0 - 1) / 2.0
        alt = (cy - last_y) < 4.0 and not alt
        nm = prim[s0].replace(" + ", "+")
        if len(nm) > 20:
            nm = nm[:19] + "…"
        ax.text(-4.4 if alt else -0.9, cy, "%s  (%d)" % (nm, e0 - s0),
                ha="right", va="center", fontsize=7.0, color=C_DARK)
        if alt:
            ax.plot([-4.1, -1.2], [cy, cy], color="#cccccc", lw=0.5, clip_on=False)
        last_y = cy

    ax.set_xticks(range(len(biomes)))
    ax.set_xticklabels(["%s (%d)" % (b, len(ROST.residents(b))) for b in biomes],
                       rotation=90, fontsize=7.2)
    ax.set_yticks([])
    ax.set_xlim(-0.5, len(biomes) - 0.5)
    ax.tick_params(axis="x", length=2)

    offdiag = sum(1 for i, d in enumerate(defs)
                  for q in ROST.residency[d] if not q.injection
                  and q.sheet != prim[i])
    singles = sum(1 for d in defs if ROST.spread(d) == 1)
    fill = 100.0 * (M > 0).sum() / M.size
    ax.set_title("The zoo effect, after the pass: %d defs × %d BiomeDefs, %.1f%% of cells filled — %d defs (%d%%) live in exactly one biome.\n"
                 "The block diagonal IS the assignment; %d of %d base rows visit a non-primary sheet."
                 % (len(defs), len(biomes), fill, singles, round(100 * singles / len(defs)), offdiag,
                    sum(1 for d in defs for q in ROST.residency[d] if not q.injection)),
                 fontsize=10.5, loc="left")
    ax.legend(handles=[Line2D([], [], marker="s", ls="", c=C_BLUE, label="landed in this BiomeDef (base roster)"),
                       Line2D([], [], marker="s", ls="", c=C_ORANGE, label="injection-layer addition (Fall Line — over the host def, under its own law)")],
              loc="upper center", bbox_to_anchor=(0.5, -0.205), ncol=2, fontsize=7.6, framealpha=0.95)
    fig.text(0.008, 0.012,
             "Rows = %d rostered creature defs, grouped by PRIMARY roster sheet (the def's highest-commonality home), then descending top commonality, then defName —\n"
             "a deterministic order, so two runs are diffable. Columns = the %d BiomeDefs the rosters bind, in sheet order, with each column's row count. One cell per\n"
             "(def, BiomeDef) pair; a filled cell is a roster row, never a mod default. A def landed by TWO sheets on the same BiomeDef shows one cell (the injection\n"
             "colour wins only where the base roster has none).\n%s" % (len(defs), len(biomes), src_line()), **FOOT)
    fig.subplots_adjust(left=0.235, right=0.99, top=0.945, bottom=0.245)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(VIZ, "fig11_biome_matrix.%s" % ext))
    plt.close(fig)
    return dict(defs=len(defs), biomes=len(biomes), fill_pct=round(fill, 2),
                singles=singles, cross_sheet_rows=offdiag)


if __name__ == "__main__":
    res = dict(fig9=fig9(), fig10=fig10(), fig11=fig11())
    print(json.dumps(res, indent=1, default=str)[:6000])
    print("\nwrote figs 9-11 (png+svg) to", VIZ)
