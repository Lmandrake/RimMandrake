#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_creature_distribution_portfolio.py — the DISTRIBUTION portfolio over the
creature register (economy, lethality, biome-law gap, dominance, husbandry).

Companion to gen_creature_size_portfolio.py (the size-mismatch portfolio, figs 1-3);
this one owns figs 4-8 in design/Jawa/worldbuilding/review/viz/. Notes and captions:
viz/PORTFOLIO_creature_distribution.md. Built 2026-09-05 (FOUNDRY analyst,
MandrakeVisuals stack). Data honesty: every number is computed here from
creature_register_rows.json — see gen_creature_register.py's header for where the
register's own numbers come from (sqlite dump WITH statBases, calibrated on Muffalo).

LIVE means: not Cherry-Picker cut, not commonality-zeroed, not modDropped.
The worklist lesson from the size portfolio holds: rankings over the full register
(cut included) are a different and wrong worklist; everything here is live-only
unless a layer is explicitly labeled otherwise.

Reference laws drawn (never fitted to these points):
  meat  : vanilla MeatAmount 140*bodySize (StatPart_BodySize over base 140), and the
          campaign doctrine's 140*bodySize^2 for bodySize>1.0 — MegafaunaYield.xml
          (src/RimUtinni/Doctrine/Patches/) writes base=140*bs so the engine's *bs
          makes the final yield quadratic. The vanilla postProcessCurve kinks at
          bodySize 0.036/0.286 make the linear reference approximate below 0.286.
  danger: beast_normalization_spec.md Law 3 — best single hit = 12-15 * bodySize
          for bodySize>=1 (shipped at K=15 in mandrake.rsw.beastnorm).
  biome : the biome definition sheets' HARD BANS (design/Jawa/worldbuilding/biomes/).
          🔴 SINCE 2026-09-09 fig6 IS A REGRESSION INSTRUMENT, not a workload meter.
          The assignment pass landed (BIOME_FAUNA_ASSIGNMENT_SITTING_1) and residency
          now comes from biomes/rosters/*.json via rosters_residency.py — the sheets'
          own product. A base-roster violation bar SHOULD be zero; a nonzero one is a
          DEFECT in the roster, to be fixed in the roster, never explained away here.

RESIDENCY SOURCE (changed 2026-09-09): rosters/*.json through rosters_residency.py.
The register's own `biomes` / `group` / `topCommonality` are the MODS' default
residency on a vanilla planet and are STALE for placement — they are never read for
residency anywhere in this file. The register remains the STATS source.

Analytic thresholds chosen here (stated, not canonical):
  size bands   small<0.5 <= medium <1.5 <= large <=3.5 < huge   (human=1.0 medium,
               muffalo 2.4 large, thrumbo 4.0 huge)
  pursuit-capable predator: has the predator special AND moveSpeed >= 4.5
               (a wild human sprints ~4.6; slower cannot run prey down)
  dune-sea "medium" (banned): 0.3 <= bodySize <= 3.0

Run from repo root:
  python3 design/Jawa/worldbuilding/review/gen_creature_distribution_portfolio.py
"""
from __future__ import annotations

import json, math, os, statistics, collections, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rosters_residency as RR

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = os.path.join(HERE, "creature_register_rows.json")
VIZ = os.path.join(HERE, "viz")
os.makedirs(VIZ, exist_ok=True)

D = json.load(open(ROWS))
ALL = D["rows"]
META = D["meta"]

def is_live(r):
    return not r.get("cut") and not r.get("commonalityZeroed") and not r.get("modDropped")

LIVE = [r for r in ALL if is_live(r)]

def besthit(r):
    tp = [t.get("power") or 0 for t in (r.get("tools") or [])]
    return max(tp) if tp else 0.0

def is_pred(r):
    return any("predator" in (s.get("text") or "") for s in (r.get("specials") or []))

# --------------------------------------------------- residency: rosters, never the register
ROST = RR.load()
REG = {r["defName"]: r for r in ALL}

# The rosters carry DESIGNED stat corrections that are part of the assignment ruling
# ("adjust-keep": the creature stays because its stat moves). Judging a roster against
# a sheet ban on the creature's PRE-adjustment stat would report a violation the
# assignment already fixed, so the designed value wins here and every designed point
# is drawn with an open marker so it is never mistaken for a MEASURED one.
DESIGNED = collections.defaultdict(dict)
for _a in ROST.stat_adjustments:
    DESIGNED[_a["def"]][_a["field"]] = _a["to"]


def designed(defName, field):
    """(value, is_designed). MEASURED from the register unless the rosters adjust it."""
    if field in DESIGNED.get(defName, {}):
        return DESIGNED[defName][field], True
    return REG.get(defName, {}).get(field), False


def is_pred_designed(defName):
    v, d = designed(defName, "predator")
    if d:
        return bool(v)
    return is_pred(REG[defName]) if defName in REG else False


def residents(biomedef):
    """Fauna LANDED in this BiomeDef by the assignment pass.
    Returns (register row, commonality, Residency) — commonality is the roster's
    DESIGN CHOICE, the register row is stats only."""
    out = []
    for res in ROST.residents(biomedef):
        r = REG.get(res.defName)
        if r is not None:
            out.append((r, res.commonality, res))
    return out

FLESH_KINDS = ("animal", "insectoid", "leviathan", "entity", "dryad")

C_GRAY = "#9aa0a6"; C_BLUE = "#3b6fb5"; C_ORANGE = "#d97706"; C_RED = "#c0392b"
C_GREEN = "#2e7d4f"; C_DARK = "#333333"; C_BAND = "#dcefe2"; C_BAN = "#f6d5d0"
FOOT = dict(fontsize=7.2, color="#666666")

def halo(txts):
    import matplotlib.patheffects as pe
    for t in txts:
        t.set_path_effects([pe.withStroke(linewidth=2.2, foreground="white")])

def src_line(extra=""):
    return ("Source: creature_register_rows.json (%s, dump %s mods, captured %s); live = not cut / not zeroed / not modDropped. %s"
            % (META["generator"], META["dumpMods"], META["dumpCaptured"][:10], extra))

# ---------------------------------------------------------------- fig 4: yield law
def fig4():
    pop = [r for r in LIVE if isinstance(r.get("bodySize"), (int, float)) and r["bodySize"] > 0
           and isinstance(r.get("meatAmount"), (int, float))]
    def law(bs):
        return 140.0 * bs * bs if bs > 1.0 else 140.0 * bs
    # Provenance-based classes: meatStatBase None = the author left the engine
    # default, so the row follows the vanilla LINEAR curve by construction (its
    # small-bs inflation included); only explicit statBases are judged against
    # the doctrine's quadratic law. MEASURED surprise: every RSW Sea Beast is
    # engine-default — MegafaunaYield.xml never patched our own mod, so the
    # planet's biggest animals still yield linear.
    default, big_linear, conform, escape, zero_flesh, zero_mach, dryads = [], [], [], [], [], [], []
    for r in pop:
        bs, m = r["bodySize"], r["meatAmount"]
        if m == 0:
            (zero_flesh if r["kindOf"] in FLESH_KINDS else zero_mach).append(r)
        elif r["kindOf"] == "dryad":
            dryads.append(r)
        elif r.get("meatStatBase") is None:
            (big_linear if bs > 1.0 else default).append(r)
        elif abs(m - law(bs)) / law(bs) <= 0.05:
            conform.append(r)
        else:
            escape.append(r)
    fig, ax = plt.subplots(figsize=(10.6, 7.6), dpi=150)
    xs = np.logspace(math.log10(0.008), math.log10(45), 300)
    ax.plot(xs, [law(x) for x in xs], color=C_DARK, lw=1.6, zorder=3,
            label="doctrine law: 140·bs, then 140·bs² above bs 1.0 (MegafaunaYield.xml)")
    ax.plot(xs, 140 * xs, color=C_DARK, lw=1.0, ls="--", zorder=3,
            label="engine default: linear 140·bs at every size")
    ax.scatter([r["bodySize"] for r in default], [r["meatAmount"] for r in default],
               s=14, c="#c9cdd2", alpha=0.6, lw=0, zorder=2,
               label="engine default, bs ≤ 1 (both laws agree), n=%d" % len(default))
    ax.scatter([r["bodySize"] for r in conform], [r["meatAmount"] for r in conform],
               s=14, c=C_GRAY, alpha=0.6, lw=0, zorder=2,
               label="authored base = doctrine law (±5%%) — the patched megafauna, n=%d" % len(conform))
    ax.scatter([r["bodySize"] for r in dryads], [r["meatAmount"] for r in dryads],
               s=30, c=C_GREEN, marker="D", lw=0, zorder=4, label="dryads — wooden, meat≈3.7 flat, n=%d" % len(dryads))
    ax.scatter([r["bodySize"] for r in big_linear], [r["meatAmount"] for r in big_linear],
               s=44, c=C_BLUE, marker="s", lw=0, zorder=5,
               label="bs > 1 but UNPATCHED — still linear (all 12 RSW Sea Beasts + %d others), n=%d"
                     % (sum(1 for r in big_linear if r["mod"] != "RimMandrake - SW Sea Beasts"), len(big_linear)))
    ax.scatter([r["bodySize"] for r in escape], [r["meatAmount"] for r in escape],
               s=52, c=C_ORANGE, marker="^", lw=0, zorder=6, label="authored, matches NEITHER law, n=%d" % len(escape))
    # zero-meat rail (log axis cannot hold 0 — disclosed)
    rail = 1.1
    ax.scatter([r["bodySize"] for r in zero_mach], [rail] * len(zero_mach),
               s=20, c="#c4c8cc", marker="x", zorder=2, label="zero meat, machine (expected), n=%d" % len(zero_mach))
    ax.scatter([r["bodySize"] for r in zero_flesh], [rail * 1.35] * len(zero_flesh),
               s=34, c=C_RED, marker="x", zorder=5, label="zero meat, FLESH — unbutcherable animals, n=%d" % len(zero_flesh))
    ax.axhline(rail * 1.8, color="#bbbbbb", lw=0.7, ls=":")
    ax.text(0.009, rail * 2.1, "meat = 0 rail (log axis cannot show zero)", fontsize=7.2, color="#777777")
    # named annotations
    ann = []
    for nm, dx, dy in (("Zakkeg", 1.25, 0.55), ("AA_Behemoth", 0.35, 0.5), ("ThrumbaToad", 1.3, 0.45), ("DA_Taraal", 0.28, 1.6)):
        r = next((x for x in escape if x["defName"] == nm), None)
        if r:
            ann.append(ax.annotate(nm, (r["bodySize"], r["meatAmount"]),
                                   xytext=(r["bodySize"] * dx, r["meatAmount"] * dy), fontsize=7.6,
                                   arrowprops=dict(arrowstyle="-", lw=0.6, color="#888888")))
    # Guarded like every other named annotation: a patch or dump change can move
    # either creature out of its bucket, and an unguarded next() would then kill
    # all five figures with StopIteration.
    r = next((x for x in conform if x["defName"] == "GR_Paraceramuffalo"), None)
    if r:
        ann.append(ax.annotate("GR_Paraceramuffalo — the law's own extreme:\n35,840 meat from one carcass (≈17,900 meals)",
                               (r["bodySize"], r["meatAmount"]), xytext=(3.1, 44000), fontsize=7.8,
                               arrowprops=dict(arrowstyle="-", lw=0.6, color="#888888")))
    r = next((x for x in big_linear if x["defName"] == "RSW_Lanternwhale"), None)
    if r:
        ann.append(ax.annotate("RSW_Lanternwhale bs 40, unpatched: 5,600 —\nless than a bs-16 land beast (law: 224,000)",
                               (r["bodySize"], r["meatAmount"]), xytext=(3.6, 700), fontsize=7.8,
                               arrowprops=dict(arrowstyle="-", lw=0.6, color="#888888")))
    fl = sorted(zero_flesh, key=lambda x: -x["bodySize"])[:2]
    for r, ty in zip(fl, (4.6, 2.5)):
        ann.append(ax.annotate(r["defName"], (r["bodySize"], rail * 1.35), xytext=(r["bodySize"] * 0.42, ty),
                               fontsize=7.2, color=C_RED, arrowprops=dict(arrowstyle="-", lw=0.5, color=C_RED)))
    an = [r for r in escape if r["mod"] == "Anomaly"]
    if an:
        ann.append(ax.annotate("Anomaly entities: authored at HALF yield\n(Noctol, Sightstealer, spikes…), n=%d" % len(an),
                               (max(r["bodySize"] for r in an), 70), xytext=(0.075, 300), fontsize=7.6,
                               arrowprops=dict(arrowstyle="-", lw=0.6, color="#888888")))
    halo(ann)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(0.008, 50); ax.set_ylim(0.9, 90000)
    ax.set_xlabel("bodySize (log)"); ax.set_ylabel("resolved MeatAmount per butchered carcass (log)")
    ax.set_title("TWO yield laws coexist above bodySize 1: the doctrine's quadratic megafauna economy (n=%d) and the\n"
                 "engine's linear default it never patched (n=%d) — the planet's biggest animals are on the WRONG side"
                 % (sum(1 for r in conform if r["bodySize"] > 1), len(big_linear)), fontsize=11, loc="left")
    ax.legend(loc="upper left", fontsize=7.4, framealpha=0.95)
    ax.grid(True, which="major", lw=0.4, alpha=0.35)
    fig.text(0.012, 0.022,
             "Both axes log (disclosed). Live population with numeric bodySize+meat, n=%d of %d rows. The engine multiplies the authored base by bodySize\n"
             "once (StatPart_BodySize); MegafaunaYield.xml authors base=140·bs for bs>1.0, so the final yield is quadratic ON PURPOSE (megafauna economy).\n"
             "Vanilla's postProcessCurve inflates yields below bs 0.286 (measured: engine-default median q 1.11 at bs 0.18, 1.48 at 0.1).\n%s"
             % (len(pop), len(ALL), src_line()), **FOOT)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.905, bottom=0.155)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(VIZ, "fig4_yield_law.%s" % ext))
    plt.close(fig)
    return dict(pop=len(pop), default=len(default), conform=len(conform),
                big_linear=[(r["defName"], r["bodySize"], r["mod"]) for r in sorted(big_linear, key=lambda x: -x["bodySize"])],
                escape=[(r["defName"], r["mod"]) for r in escape],
                zero_flesh=[r["defName"] for r in zero_flesh], zero_mach=len(zero_mach), dryads=len(dryads))

# ------------------------------------------------------- fig 5: lethality by mod
def fig5():
    pop = [r for r in LIVE if r["kindOf"] in FLESH_KINDS and (r.get("bodySize") or 0) >= 1.0 and r.get("tools")]
    k = {r["defName"]: besthit(r) / r["bodySize"] for r in pop}
    bymod = collections.defaultdict(list)
    for r in pop:
        bymod[r["mod"]].append(r)
    mods = [m for m, v in bymod.items() if len(v) >= 8]
    mods.sort(key=lambda m: statistics.median(k[r["defName"]] for r in bymod[m]))
    rest = [r for m, v in bymod.items() if m not in mods for r in v]
    rows = [("all other mods pooled (n<8 each)", rest)] + [(m, bymod[m]) for m in mods]
    fig, (ax, axg) = plt.subplots(1, 2, figsize=(11.5, 7.2), dpi=150,
                                  gridspec_kw=dict(width_ratios=[4.1, 1.0], wspace=0.04))
    rng = np.random.default_rng(7)
    XMAX = 30.0
    ax.axvspan(12, 15.5, color=C_BAND, zorder=0)
    clipped = []
    for i, (m, v) in enumerate(rows):
        ys = i + rng.uniform(-0.26, 0.26, len(v))
        for r, y in zip(v, ys):
            kk = k[r["defName"]]
            x = min(kk, XMAX - 0.3)
            inb = 12 <= kk <= 15.5
            col = C_GREEN if inb else (C_ORANGE if kk > 15.5 else C_GRAY)
            mk = "o" if inb else ("^" if kk > 15.5 else "v")
            ax.scatter(x, y, s=13, c=col, marker=mk, alpha=0.75, lw=0, zorder=3)
            if kk > XMAX:
                clipped.append((r["defName"], kk))
        med = statistics.median(k[r["defName"]] for r in v)
        ax.plot([med, med], [i - 0.33, i + 0.33], color=C_DARK, lw=1.6, zorder=4)
        pct = 100 * sum(1 for r in v if 12 <= k[r["defName"]] <= 15.5) / len(v)
        axg.barh(i, pct, height=0.6, color=C_GREEN if pct >= 90 else "#b9cdbf", zorder=2)
        if pct >= 55:
            axg.text(pct - 3, i, "%d%% (n=%d)" % (round(pct), len(v)), va="center", ha="right",
                     fontsize=7.4, color="white", zorder=3)
        else:
            axg.text(pct + 2.5, i, "%d%% (n=%d)" % (round(pct), len(v)), va="center", fontsize=7.4)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([m for m, _ in rows], fontsize=8)
    ax.set_xlim(0, XMAX); ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_xlabel("best single hit ÷ bodySize  (K, damage per bodySize unit)")
    ax.text(13.75, -0.58, "Law 3 band: best hit 12–15 × bodySize", ha="center", fontsize=7.6, color=C_GREEN)
    if clipped:
        cl = ", ".join("%s K=%.0f" % c for c in sorted(clipped, key=lambda t: -t[1])[:3])
        ax.text(0.3, len(rows) - 0.42, "→ %d clipped beyond K=30: %s" % (len(clipped), cl),
                ha="left", fontsize=7.2, color="#777777")
    axg.set_xlim(0, 104); axg.set_yticks([]); axg.set_ylim(ax.get_ylim())
    axg.set_xlabel("share in Law-3 band", fontsize=8)
    axg.set_xticks([0, 50, 100]); axg.set_xticklabels(["0%", "50%", "100%"], fontsize=7)
    for s in ("top", "right"): ax.spines[s].set_visible(False); axg.spines[s].set_visible(False)
    n_in = sum(1 for r in pop if 12 <= k[r["defName"]] <= 15.5)
    n_below = sum(1 for r in pop if k[r["defName"]] < 12)
    ax.set_title("The K=15 casual-lethality pass landed on exactly the two mods it targeted —\n"
                 "%d of %d big flesh creatures elsewhere still hit vanilla-soft (below the band)" % (n_below, len(pop)),
                 fontsize=11, loc="left")
    leg = [Line2D([], [], marker="o", ls="", c=C_GREEN, label="in band (12–15.5), n=%d" % n_in),
           Line2D([], [], marker="v", ls="", c=C_GRAY, label="below band, n=%d" % n_below),
           Line2D([], [], marker="^", ls="", c=C_ORANGE, label="above band, n=%d" % (len(pop) - n_in - n_below)),
           Line2D([], [], c=C_DARK, lw=1.6, label="mod median")]
    ax.legend(handles=leg, loc="lower right", fontsize=7.4, framealpha=0.95)
    fig.text(0.012, 0.02,
             "Live flesh creatures (animal/insectoid/leviathan/entity/dryad) with bodySize ≥ 1 and at least one melee tool, n=%d; K = max tool power ÷ bodySize.\n"
             "Reference band: beast_normalization_spec.md Law 3 (best hit 12–15 × bodySize; mandrake.rsw.beastnorm shipped K=15 over the SW collection and\n"
             "RSW Sea Beasts). Mods with n<8 pooled in the top row. Every creature drawn; medians are ticks, never a substitute. %s" % (len(pop), src_line()), **FOOT)
    fig.subplots_adjust(left=0.27, right=0.985, top=0.9, bottom=0.14)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(VIZ, "fig5_lethality_by_mod.%s" % ext))
    plt.close(fig)
    stats = {m: dict(n=len(v), median=round(statistics.median(k[r["defName"]] for r in v), 1),
                     inband=sum(1 for r in v if 12 <= k[r["defName"]] <= 15.5)) for m, v in rows}
    return dict(pop=len(pop), n_in=n_in, n_below=n_below, mods=stats)

# ------------------------------------------------------ fig 6: biome-law regression
def fig6():
    """POST-ASSIGNMENT REGRESSION INSTRUMENT.

    Residency comes from the rosters — the sheets' own product — so a base-roster
    bar SHOULD be zero. Injection-layer additions (fall_line) are drawn as a
    SEPARATE, differently-marked series: they are transient vermin injected over
    the underlying BiomeDefs under fall_line.md's own law, not dune-sea/desert
    residents, and folding them into the base bar would manufacture a violation
    the sheets never made."""
    out = {}
    fig, axes = plt.subplots(3, 1, figsize=(10.6, 10.4), dpi=150)
    rng = np.random.default_rng(11)

    def split(res):
        return ([t for t in res if not t[2].injection], [t for t in res if t[2].injection])

    def verdict(ax, nbase, nviol, x, y):
        ok = nviol == 0
        ax.text(x, y, ("✓ 0 base-roster violations of %d residents" % nbase) if ok
                else ("✗ %d base-roster violation%s of %d residents — ROSTER DEFECT"
                      % (nviol, "" if nviol == 1 else "s", nbase)),
                fontsize=8.2, color=C_GREEN if ok else C_RED, weight="bold", ha="left")

    # Panel A — Desert: no pursuit predators
    ax = axes[0]
    base, inj = split(residents("Desert"))
    preds = [(r, c, q) for r, c, q in base if is_pred_designed(r["defName"])]
    nonp = [t for t in base if not is_pred_designed(t[0]["defName"])]
    viol = [(r, c, q) for r, c, q in preds if (designed(r["defName"], "moveSpeed")[0] or 0) >= 4.5]
    injv = [(r, c, q) for r, c, q in inj
            if is_pred_designed(r["defName"]) and (designed(r["defName"], "moveSpeed")[0] or 0) >= 4.5]
    ax.axvspan(4.5, 9.4, color=C_BAN, zorder=0)
    ax.text(4.62, 1.78, "pursuit-capable: banned for predators (moveSpeed ≥ 4.5; wild human ≈ 4.6)",
            fontsize=7.4, color=C_RED, ha="left")
    ax.scatter([designed(r["defName"], "moveSpeed")[0] or 0 for r, c, q in nonp],
               0.35 + rng.uniform(-0.16, 0.16, len(nonp)),
               s=10, c=C_GRAY, alpha=0.45, lw=0)
    for r, c, q in preds:
        sp = designed(r["defName"], "moveSpeed")[0] or 0
        d = designed(r["defName"], "moveSpeed")[1]
        bad = sp >= 4.5
        ax.scatter(sp, 1.0 + rng.uniform(-0.2, 0.2), s=12 + 46 * math.sqrt(min(c, 1.5)),
                   facecolors="none" if d else (C_RED if bad else C_GREEN),
                   edgecolors=C_RED if bad else C_GREEN, linewidths=1.1 if d else 0,
                   marker="^" if bad else "o", alpha=0.85)
    for r, c, q in inj:
        sp = designed(r["defName"], "moveSpeed")[0] or 0
        ax.scatter(sp, 1.55 + rng.uniform(-0.14, 0.14), s=10 + 40 * math.sqrt(min(c, 1.5)),
                   c=C_ORANGE, marker="D", alpha=0.75, lw=0)
    ann = []
    for r, c, q in sorted(viol + injv, key=lambda t: -t[1])[:3]:
        yy = 1.55 if q.injection else 1.0
        ann.append(ax.annotate("%s (comm %.2g, %s)" % (r["defName"], c, q.sheet),
                               (designed(r["defName"], "moveSpeed")[0], yy),
                               xytext=(5.6, yy - 0.55), fontsize=7.2,
                               arrowprops=dict(arrowstyle="-", lw=0.5, color="#888888")))
    # the two designed slow-downs are the assignment's own repair — name them
    adj = [(r, c) for r, c, q in preds if designed(r["defName"], "moveSpeed")[1]]
    if adj:
        ann.append(ax.annotate("adjust-keep: %s slowed below the ban by roster ruling"
                               % ", ".join("%s %.1f→%.1f" % (r["defName"], REG[r["defName"]]["moveSpeed"],
                                                             designed(r["defName"], "moveSpeed")[0])
                                           for r, c in adj),
                               (4.4, 1.0), xytext=(0.25, 0.03), fontsize=7.0, color=C_BLUE,
                               arrowprops=dict(arrowstyle="-", lw=0.5, color=C_BLUE)))
    halo(ann)
    ax.set_yticks([0.42, 1.0, 1.55]); ax.set_yticklabels(["other residents", "predators", "Fall Line (injected)"], fontsize=7.6)
    ax.set_xlim(0, 9.4); ax.set_ylim(-0.22, 2.0)
    ax.set_xlabel("moveSpeed (cells/s) — roster-adjusted where the assignment ruled one", fontsize=8)
    ax.set_title("Desert (law: NO pursuit predators) — base roster %d residents, %d predators, %d pursuit-capable"
                 % (len(base), len(preds), len(viol)), fontsize=9.6, loc="left")
    verdict(ax, len(base), len(viol), 0.12, 1.80)
    ax.legend(handles=[Line2D([], [], marker="o", ls="", c=C_GREEN, label="predator, ambush-slow (legal)"),
                       Line2D([], [], marker="o", ls="", mfc="none", mec=C_GREEN, label="…via a roster stat_adjustment (DESIGNED)"),
                       Line2D([], [], marker="^", ls="", c=C_RED, label="predator, pursuit-capable (VIOLATION)"),
                       Line2D([], [], marker="D", ls="", c=C_ORANGE, label="Fall Line injection (own law)"),
                       Line2D([], [], marker="o", ls="", c=C_GRAY, label="non-predator resident")],
              loc="lower right", fontsize=6.6, framealpha=0.95, ncol=2)
    out["Desert"] = dict(base=len(base), injected=len(inj), predators=len(preds), pursuit=len(viol),
                         injected_violations=[(r["defName"], c) for r, c, q in injv],
                         top=[(r["defName"], c) for r, c, q in sorted(viol, key=lambda t: -t[1])[:8]])

    # Panel B — AridShrubland: the size void
    ax = axes[1]
    base, inj = split(residents("AridShrubland"))
    def bs_of(r): return designed(r["defName"], "bodySize")[0] or 0
    viol = [t for t in base if 1.5 <= bs_of(t[0]) <= 3.5]
    injv = [t for t in inj if 1.5 <= bs_of(t[0]) <= 3.5]
    ax.axvspan(1.5, 3.5, color=C_BAN, zorder=0)
    for r, c, q in base:
        bad = 1.5 <= bs_of(r) <= 3.5
        ax.scatter(bs_of(r), 0.75 + rng.uniform(-0.45, 0.45), s=10 + 46 * math.sqrt(min(c, 1.5)),
                   c=C_RED if bad else C_GRAY, marker="^" if bad else "o", alpha=0.75 if bad else 0.5, lw=0)
    for r, c, q in inj:
        ax.scatter(bs_of(r), 1.55 + rng.uniform(-0.1, 0.1), s=10 + 40 * math.sqrt(min(c, 1.5)),
                   c=C_ORANGE, marker="D", alpha=0.75, lw=0)
    ax.text(2.28, 1.86, "LARGE band: banned resident (legal only as huge-young)", fontsize=7.4, color=C_RED, ha="center")
    ax.set_xscale("log"); ax.set_xlim(0.008, 45); ax.set_ylim(0, 2.0)
    ax.set_yticks([0.75, 1.55]); ax.set_yticklabels(["base roster", "Fall Line"], fontsize=7.6)
    ax.set_xlabel("bodySize (log)", fontsize=8)
    ax.set_title("Arid shrubland (law: small · medium · VOID · huge) — base roster %d residents, %d in the banned large band"
                 % (len(base), len(viol)), fontsize=9.6, loc="left")
    verdict(ax, len(base), len(viol), 0.0095, 1.86)
    ax.text(0.0095, 1.60, "size bands (stated thresholds):\nsmall <0.5 ≤ medium <1.5 ≤ large ≤3.5 < huge", fontsize=7.0, color="#777777")
    out["AridShrubland"] = dict(base=len(base), injected=len(inj), large=len(viol),
                                injected_violations=[(r["defName"], c) for r, c, q in injv],
                                top=[(r["defName"], c) for r, c, q in sorted(viol, key=lambda t: -t[1])[:8]])

    # Panel C — ExtremeDesert (dune sea)
    ax = axes[2]
    base, inj = split(residents("ExtremeDesert"))
    viol = [t for t in base if 0.3 <= bs_of(t[0]) <= 3.0]
    injv = [t for t in inj if 0.3 <= bs_of(t[0]) <= 3.0]
    ax.axvspan(0.3, 3.0, color=C_BAN, zorder=0)
    for r, c, q in base:
        bad = 0.3 <= bs_of(r) <= 3.0
        ax.scatter(bs_of(r), 0.75 + rng.uniform(-0.45, 0.45), s=10 + 46 * math.sqrt(min(c, 1.5)),
                   c=C_RED if bad else C_GRAY, marker="^" if bad else "o", alpha=0.75 if bad else 0.5, lw=0)
    for r, c, q in inj:
        ax.scatter(bs_of(r), 1.55 + rng.uniform(-0.1, 0.1), s=10 + 40 * math.sqrt(min(c, 1.5)),
                   c=C_ORANGE, marker="D", alpha=0.8, lw=0)
    ax.text(0.95, 1.86, "MEDIUM: banned — 'giant or grain-scale, nothing between'", fontsize=7.4, color=C_RED, ha="center")
    ann = []
    for r, c, q in sorted(viol, key=lambda t: -t[1])[:2]:
        ann.append(ax.annotate("%s (bs %.2g, comm %.2g)\nroster law: %s" % (r["defName"], bs_of(r), c, (q.band or "—")),
                               (bs_of(r), 0.75), xytext=(4.2, 0.18), fontsize=7.0,
                               arrowprops=dict(arrowstyle="-", lw=0.5, color="#888888")))
    if injv:
        ann.append(ax.annotate("Fall Line injects %d vermin/droid rows here under its OWN law\n"
                               "(fall_line.md: transient, over the underlying def — not dune-sea residents)" % len(injv),
                               (0.6, 1.55), xytext=(0.011, 1.18), fontsize=7.0, color=C_ORANGE,
                               arrowprops=dict(arrowstyle="-", lw=0.5, color=C_ORANGE)))
    halo(ann)
    ax.set_xscale("log"); ax.set_xlim(0.008, 45); ax.set_ylim(0, 2.0)
    ax.set_yticks([0.75, 1.55]); ax.set_yticklabels(["base roster", "Fall Line"], fontsize=7.6)
    ax.set_xlabel("bodySize (log)", fontsize=8)
    ax.set_title("Dune sea + deep desert (`ExtremeDesert`, law: giant or grain-scale ONLY) — base roster %d residents, %d medium"
                 % (len(base), len(viol)), fontsize=9.6, loc="left")
    verdict(ax, len(base), len(viol), 0.0095, 1.70)
    ax.text(0.0095, 1.44, "banned 'medium' stated as 0.3 ≤ bodySize ≤ 3.0\n(the sheet gives no number; this is the analytic choice)", fontsize=7.0, color="#777777")
    out["ExtremeDesert"] = dict(base=len(base), injected=len(inj), medium=len(viol),
                                injected_violations=[(r["defName"], c) for r, c, q in injv],
                                top=[(r["defName"], c) for r, c, q in sorted(viol, key=lambda t: -t[1])[:8]])

    fig.suptitle("REGRESSION INSTRUMENT — the biome sheets' hard bans vs the LANDED assignment: base-roster bars should read zero",
                 fontsize=11.5, x=0.012, ha="left")
    fig.text(0.012, 0.012,
             "Resident = a row in biomes/rosters/<sheet>.json landed on that BiomeDef (rosters_residency.py). ⚠️ NOT the register's `biomes` field — that\n"
             "is the MODS' default residency on a vanilla planet, stale for placement. Marker AREA ∝ √commonality (design choice, disclosed); open\n"
             "markers = a roster stat_adjustment (DESIGNED, not yet built); ◆ = injection-layer addition judged under fall_line.md, never the host\n"
             "biome's law. Huge-young exemption (shrubland) stays UNMEASURED — no life-stage data in the register.\n"
             "Stats: creature_register_rows.json (dump %s mods, %s). Residency: biomes/rosters/*.json, authored 2026-09-09."
             % (META["dumpMods"], META["dumpCaptured"][:10]), **FOOT)
    fig.subplots_adjust(left=0.115, right=0.985, top=0.93, bottom=0.115, hspace=0.55)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(VIZ, "fig6_biome_law_gap.%s" % ext))
    plt.close(fig)
    return out

# ------------------------------------------------------ fig 7: dominance after the pass
def fig7():
    """Roster spread × roster top-commonality. Both axes come from the rosters;
    the register's `topCommonality` / `biomes` are NOT read here."""
    pop = [(REG[d], ROST.top_commonality(d), ROST.spread(d)) for d in sorted(ROST.residency)
           if d in REG]
    pop = [(r, tc, sp) for r, tc, sp in pop if sp > 0 and tc > 0]
    fig, ax = plt.subplots(figsize=(10.2, 7.2), dpi=150)
    rng = np.random.default_rng(19)
    aa = [t for t in pop if t[0]["mod"] == "Alpha Animals"]
    core = [t for t in pop if t[0]["mod"] == "Core"]
    oth = [t for t in pop if t[0]["mod"] not in ("Alpha Animals", "Core")]
    for grp, col, mk, lab in ((oth, C_GRAY, "o", "all other mods"),
                              (core, C_BLUE, "s", "Core (vanilla)"),
                              (aa, C_ORANGE, "^", "Alpha Animals")):
        ax.scatter([sp + rng.uniform(-0.16, 0.16) for _, _, sp in grp], [tc for _, tc, _ in grp],
                   s=15 if col == C_GRAY else 26, c=col, marker=mk,
                   alpha=0.5 if col == C_GRAY else 0.85, lw=0,
                   label="%s, n=%d" % (lab, len(grp)))
    ax.axvline(3.5, color="#bbbbbb", lw=0.8, ls=":"); ax.axhline(0.3, color="#bbbbbb", lw=0.8, ls=":")
    ub = sorted([t for t in pop if t[1] >= 0.3 and t[2] >= 4], key=lambda t: (-t[2], -t[1]))
    # No leader lines: at spread ≤5 the points stack on five x values and every
    # leader crossed another. The list IS the annotation, parked in the empty
    # low-commonality quadrant where nothing is plotted.
    box = ["WIDESPREAD AND COMMON — %d creatures (spread ≥4, top commonality ≥0.3)" % len(ub)]
    for r, tc, sp in ub:
        sh = sorted({q.sheet for q in ROST.residency[r["defName"]]})
        txt = ", ".join(sh[:2]) + (" +%d more" % (len(sh) - 2) if len(sh) > 2 else "")
        box.append("   %-14s %d biomes, comm %-4.2g %s" % (r["defName"], sp, tc, txt))
    ax.text(1.55, 0.0075, "\n".join(box), fontsize=7.0, color=C_DARK, ha="left", va="top",
            family="DejaVu Sans Mono",
            bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="#cccccc", lw=0.6))
    ax.set_yscale("log"); ax.set_xlim(0.4, 5.9); ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_ylim(0.0006, 4.5)
    ax.set_xlabel("biome spread — number of Ash'karr BiomeDefs the ROSTERS land this creature in (x jittered ±0.16)")
    ax.set_ylabel("top roster commonality across its homes (log)")
    mx_sp = max(sp for _, _, sp in pop); mx_tc = max(tc for _, tc, _ in pop)
    ax.set_title("After the assignment pass, ubiquity is gone: max spread %d biomes (was 45 on the mods' default residency),\n"
                 "%d of %d rostered creatures live in exactly ONE biome" % (mx_sp, sum(1 for _, _, sp in pop if sp == 1), len(pop)),
                 fontsize=11, loc="left")
    ax.legend(loc="upper right", fontsize=7.6, framealpha=0.95)
    ax.grid(True, which="major", lw=0.4, alpha=0.3)
    fig.text(0.012, 0.018,
             "Rostered creatures with at least one landed home, n=%d of the register's %d live rows — spread AND commonality both from\n"
             "biomes/rosters/*.json via rosters_residency.py. ⚠️ The register's own `biomes`/`topCommonality` (the MODS' default residency,\n"
             "where spread ran to 45 BiomeDefs and commonality to 3.0) are NOT plotted and NOT mixed in; that scale is quoted in the title as\n"
             "the state this pass replaced, nothing more. Y log (disclosed). Quadrant thresholds (spread 4, comm 0.3) are stated choices.\n"
             "Stats: creature_register_rows.json (dump %s mods, %s). Commonality is a DESIGN CHOICE, never a measured stat."
             % (len(pop), len(LIVE), META["dumpMods"], META["dumpCaptured"][:10]), **FOOT)
    fig.subplots_adjust(left=0.08, right=0.985, top=0.9, bottom=0.185)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(VIZ, "fig7_dominance.%s" % ext))
    plt.close(fig)
    return dict(pop=len(pop), max_spread=mx_sp, max_comm=mx_tc,
                singles=sum(1 for _, _, sp in pop if sp == 1),
                ubiq=[(r["defName"], tc, sp, r["mod"]) for r, tc, sp in sorted(ub, key=lambda t: -t[2])])

# ------------------------------------------------------ fig 8: husbandry (supplementary)
def fig8():
    pop = [r for r in LIVE if r["kindOf"] in ("animal", "insectoid") and r.get("wildness") is not None]
    wl = ["tame (<0.35)", "middle (0.35–0.75)", "wild (≥0.75)"]
    tl = ["None", "Intermediate", "Advanced"]
    def wb(w): return 0 if w < 0.35 else (1 if w < 0.75 else 2)
    M = np.zeros((3, 3), int)
    cell = collections.defaultdict(list)
    # Rows whose trainability names a def outside the vanilla three (a modded
    # TrainabilityDef) cannot be binned; count them explicitly so the caption
    # can say so instead of letting them vanish from the total.
    nonstandard = []
    for r in pop:
        t = r.get("trainability") or "None"
        if t not in tl:
            nonstandard.append(r["defName"])
            continue
        i, j = wb(r["wildness"]), tl.index(t)
        M[i, j] += 1
        cell[(i, j)].append(r)
    fig, ax = plt.subplots(figsize=(9.2, 6.4), dpi=150)
    im = ax.imshow(M, cmap="Greys", vmin=0, vmax=M.max() * 1.15)
    for i in range(3):
        for j in range(3):
            ax.text(j, i - 0.08, str(M[i, j]), ha="center", fontsize=15,
                    color="white" if M[i, j] > M.max() * 0.55 else "#222222", weight="bold")
    ax.text(2, 2 + 0.3, "the exotic-war-beast corner:\nhard to tame, trainable once kept\n(WarWyrm, EnergySpider…)", ha="center", fontsize=6.8, color="white")
    ax.text(0, 0 + 0.33, "docile and untrainable —\nthe farm-animal block\n(Goat, Duck, Donkey, Gorg, Bantha-kin)", ha="center", fontsize=7.4, color="#333333")
    ax.set_xticks(range(3)); ax.set_xticklabels(tl); ax.set_yticks(range(3)); ax.set_yticklabels(wl)
    ax.set_xlabel("trainability"); ax.set_ylabel("wildness")
    cb = fig.colorbar(im, ax=ax, shrink=0.8); cb.set_label("live creatures in cell", fontsize=8)
    ax.set_title("Husbandry space: the biggest cohort (n=%d) is wild-but-Advanced —\n"
                 "taming difficulty, not trainability, gates war/work beasts" % M[2, 2],
                 fontsize=10.5, loc="left")
    fig.text(0.012, 0.022,
             "Live animals+insectoids with a wildness stat, n=%d binned (rows lacking trainability default to None — RimWorld's own default;\n"
             "%d rows carry a nonstandard TrainabilityDef and are EXCLUDED from the matrix%s).\n"
             "Wildness bins are stated analytic choices. Counts printed in every cell; the colormap is monotonic-lightness grayscale.\n%s"
             % (sum(M.flatten()), len(nonstandard),
                (": " + ", ".join(nonstandard[:6])) if nonstandard else "", src_line()), **FOOT)
    fig.subplots_adjust(left=0.16, right=0.99, top=0.87, bottom=0.15)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(VIZ, "fig8_husbandry.%s" % ext))
    plt.close(fig)
    return dict(matrix=M.tolist(), pop=len(pop))

if __name__ == "__main__":
    res = dict(fig4=fig4(), fig5=fig5(), fig6=fig6(), fig7=fig7(), fig8=fig8())
    print(json.dumps(res, indent=1, default=str)[:4000])
    print("\nwrote figs 4-8 (png+svg) to", VIZ)
