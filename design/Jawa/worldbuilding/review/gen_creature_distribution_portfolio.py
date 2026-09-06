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
  biome : the biome definition sheets' HARD BANS (design/Jawa/worldbuilding/biomes/),
          which are the TARGET state (authored 2026-09-05) — the fauna assignment
          predates them, so violations measure the curation workload, not bugs.

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

import json, math, os, statistics, collections

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

def residents(biomedef):
    out = []
    for r in LIVE:
        for b in r["biomes"]:
            if b["biomeDef"] == biomedef and (b.get("commonality") or 0) > 0:
                out.append((r, b["commonality"]))
                break
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

# ------------------------------------------------------ fig 6: biome-law gap
def fig6():
    out = {}
    fig, axes = plt.subplots(3, 1, figsize=(10.6, 10.4), dpi=150)
    rng = np.random.default_rng(11)

    # Panel A — Desert: no pursuit predators
    ax = axes[0]
    res = residents("Desert")
    preds = [(r, c) for r, c in res if is_pred(r)]
    nonp = [(r, c) for r, c in res if not is_pred(r)]
    viol = [(r, c) for r, c in preds if (r.get("moveSpeed") or 0) >= 4.5]
    ax.axvspan(4.5, 9.4, color=C_BAN, zorder=0)
    ax.text(4.62, 1.72, "pursuit-capable: banned for predators (moveSpeed ≥ 4.5; wild human ≈ 4.6)",
            fontsize=7.4, color=C_RED, ha="left")
    ax.scatter([r.get("moveSpeed") or 0 for r, c in nonp], 0.35 + rng.uniform(-0.16, 0.16, len(nonp)),
               s=10, c=C_GRAY, alpha=0.4, lw=0, label="non-predator residents, n=%d" % len(nonp))
    for r, c in preds:
        sp = r.get("moveSpeed") or 0
        bad = sp >= 4.5
        ax.scatter(sp, 1.0 + rng.uniform(-0.2, 0.2), s=12 + 46 * math.sqrt(min(c, 1.5)),
                   c=C_RED if bad else C_GREEN, marker="^" if bad else "o", alpha=0.8, lw=0)
    ann = []
    for nm, tx, ty in (("GR_Manwolf", 5.35, 0.05), ("Meganeura", 7.35, 1.45), ("JOE_Cephalope", 7.5, 0.42)):
        t = next(((r, c) for r, c in viol if r["defName"] == nm), None)
        if t:
            ann.append(ax.annotate(nm + " (comm %.2g)" % t[1], (t[0].get("moveSpeed"), 1.0),
                                   xytext=(tx, ty), fontsize=7.2,
                                   arrowprops=dict(arrowstyle="-", lw=0.5, color="#888888")))
    halo(ann)
    ax.set_yticks([0.35, 1.0]); ax.set_yticklabels(["other residents", "predators"], fontsize=8)
    ax.set_xlim(0, 9.4); ax.set_ylim(-0.1, 1.95)
    ax.set_xlabel("moveSpeed (cells/s)", fontsize=8)
    ax.set_title("Desert (sheet law: NO pursuit predators, steady populations) — %d of %d resident predators are pursuit-capable"
                 % (len(viol), len(preds)), fontsize=9.6, loc="left")
    leg = [Line2D([], [], marker="^", ls="", c=C_RED, label="predator, pursuit-capable (violates), n=%d" % len(viol)),
           Line2D([], [], marker="o", ls="", c=C_GREEN, label="predator, slow (ambush-compatible), n=%d" % (len(preds) - len(viol)))]
    ax.legend(handles=leg, loc="upper left", fontsize=7.2, framealpha=0.95)
    out["Desert"] = dict(residents=len(res), predators=len(preds), pursuit=len(viol),
                         top=[(r["defName"], c) for r, c in sorted(viol, key=lambda t: -t[1])[:8]])

    # Panel B — AridShrubland: the size void (nothing resident in LARGE)
    ax = axes[1]
    res = residents("AridShrubland")
    viol = [(r, c) for r, c in res if 1.5 <= (r.get("bodySize") or 0) <= 3.5]
    ax.axvspan(1.5, 3.5, color=C_BAN, zorder=0)
    for r, c in res:
        bs = r.get("bodySize") or 0
        bad = 1.5 <= bs <= 3.5
        ax.scatter(bs, 0.8 + rng.uniform(-0.55, 0.55), s=10 + 46 * math.sqrt(min(c, 1.5)),
                   c=C_RED if bad else C_GRAY, marker="^" if bad else "o", alpha=0.65 if bad else 0.4, lw=0)
    ax.text(2.28, 1.78, "LARGE band: banned resident (legal only as huge-young)", fontsize=7.4, color=C_RED, ha="center")
    ann = []
    for nm, tx, ty in (("Gutkurr", 0.62, 1.6), ("Dactillion", 4.6, 0.05), ("Varactyl", 5.2, 1.55)):
        t = next(((r, c) for r, c in viol if r["defName"] == nm), None)
        if t:
            ann.append(ax.annotate("%s (comm %.2g)" % (nm, t[1]), (t[0]["bodySize"], 0.8),
                                   xytext=(tx, ty), fontsize=7.2,
                                   arrowprops=dict(arrowstyle="-", lw=0.5, color="#888888")))
    halo(ann)
    ax.set_xscale("log"); ax.set_xlim(0.008, 45); ax.set_ylim(0, 2.0); ax.set_yticks([])
    ax.set_xlabel("bodySize (log)", fontsize=8)
    ax.set_title("Arid shrubland (sheet law: small · medium · VOID · huge) — %d of %d residents sit in the banned large band (%d%%)"
                 % (len(viol), len(res), round(100 * len(viol) / len(res)) if res else 0), fontsize=9.6, loc="left")
    ax.text(0.0095, 1.72, "size bands (stated thresholds):\nsmall <0.5 ≤ medium <1.5 ≤ large ≤3.5 < huge", fontsize=7.0, color="#777777")
    out["AridShrubland"] = dict(residents=len(res), large=len(viol),
                                top=[(r["defName"], c) for r, c in sorted(viol, key=lambda t: -t[1])[:8]])

    # Panel C — ExtremeDesert (dune sea): giant or grain-scale, nothing between
    ax = axes[2]
    res = residents("ExtremeDesert")
    viol = [(r, c) for r, c in res if 0.3 <= (r.get("bodySize") or 0) <= 3.0]
    ax.axvspan(0.3, 3.0, color=C_BAN, zorder=0)
    for r, c in res:
        bs = r.get("bodySize") or 0
        bad = 0.3 <= bs <= 3.0
        ax.scatter(bs, 0.8 + rng.uniform(-0.55, 0.55), s=10 + 46 * math.sqrt(min(c, 1.5)),
                   c=C_RED if bad else C_GRAY, marker="^" if bad else "o", alpha=0.65 if bad else 0.4, lw=0)
    ax.text(0.95, 1.78, "MEDIUM: banned — 'body sizes are giant or grain-scale, nothing between'",
            fontsize=7.4, color=C_RED, ha="center")
    ann = []
    for nm, tx, ty in (("Tooke", 0.045, 1.5), ("Wraid", 4.6, 0.05), ("Falumpaset", 5.2, 1.5)):
        t = next(((r, c) for r, c in viol if r["defName"] == nm), None)
        if t:
            ann.append(ax.annotate("%s (comm %.2g)" % (nm, t[1]), (t[0]["bodySize"], 0.8),
                                   xytext=(tx, ty), fontsize=7.2,
                                   arrowprops=dict(arrowstyle="-", lw=0.5, color="#888888")))
    halo(ann)
    ax.set_xscale("log"); ax.set_xlim(0.008, 45); ax.set_ylim(0, 2.0); ax.set_yticks([])
    ax.set_xlabel("bodySize (log)", fontsize=8)
    ax.set_title("Dune sea / ExtremeDesert (sheet law: giant or grain-scale ONLY) — %d of %d residents are medium-sized (%d%%)"
                 % (len(viol), len(res), round(100 * len(viol) / len(res)) if res else 0), fontsize=9.6, loc="left")
    ax.text(0.0095, 1.72, "banned 'medium' stated as 0.3 ≤ bodySize ≤ 3.0\n(the sheet gives no number; this is the analytic choice)", fontsize=7.0, color="#777777")
    out["ExtremeDesert"] = dict(residents=len(res), medium=len(viol),
                                top=[(r["defName"], c) for r, c in sorted(viol, key=lambda t: -t[1])[:8]])

    fig.suptitle("The biome sheets' hard bans vs the fauna the mods actually assign — the curation gap, measured",
                 fontsize=12, x=0.012, ha="left")
    fig.text(0.012, 0.012,
             "Resident = live creature with spawn commonality > 0 in that BiomeDef. Marker AREA ∝ √commonality (non-scale sizing, disclosed).\n"
             "The sheets (design/Jawa/worldbuilding/biomes/, authored 2026-09-05) are the TARGET; the fauna lists predate them — these are curation\n"
             "WORKLOADS, not code defects. Huge-young exemption (shrubland) is UNMEASURED: the register carries no life-stage data.\n%s" % src_line(), **FOOT)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.935, bottom=0.095, hspace=0.5)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(VIZ, "fig6_biome_law_gap.%s" % ext))
    plt.close(fig)
    return out

# ------------------------------------------------------ fig 7: dominance (supplementary)
def fig7():
    pop = [(r, r.get("topCommonality") or 0, sum(1 for b in r["biomes"] if (b.get("commonality") or 0) > 0))
           for r in LIVE]
    pop = [(r, tc, sp) for r, tc, sp in pop if sp > 0 and tc > 0]
    fig, ax = plt.subplots(figsize=(10.2, 7.2), dpi=150)
    aa = [(r, tc, sp) for r, tc, sp in pop if r["mod"] == "Alpha Animals"]
    core = [(r, tc, sp) for r, tc, sp in pop if r["mod"] == "Core"]
    oth = [(r, tc, sp) for r, tc, sp in pop if r["mod"] not in ("Alpha Animals", "Core")]
    ax.scatter([sp for _, _, sp in oth], [tc for _, tc, _ in oth], s=13, c=C_GRAY, alpha=0.45, lw=0,
               label="all other mods, n=%d" % len(oth))
    ax.scatter([sp for _, _, sp in core], [tc for _, tc, _ in core], s=22, c=C_BLUE, marker="s", alpha=0.8, lw=0,
               label="Core (vanilla), n=%d" % len(core))
    ax.scatter([sp for _, _, sp in aa], [tc for _, tc, _ in aa], s=22, c=C_ORANGE, marker="^", alpha=0.85, lw=0,
               label="Alpha Animals, n=%d" % len(aa))
    ax.axvline(20, color="#bbbbbb", lw=0.8, ls=":"); ax.axhline(0.3, color="#bbbbbb", lw=0.8, ls=":")
    ub = [(r, tc, sp) for r, tc, sp in pop if tc >= 0.3 and sp >= 20]
    ann = []
    for nm, dx, dy in (("AA_PebbleMit", -6.2, 1.6), ("Rat", -3.5, 1.25), ("Hare", -3, 1.3), ("AA_Aerofleet", -8.5, 1.5),
                       ("Muffalo", 0.4, 1.4), ("GraniteSlug", 0.5, 1.55), ("Boomalope", 0.3, 0.52)):
        t = next(((r, tc, sp) for r, tc, sp in ub if r["defName"] == nm), None)
        if t:
            ann.append(ax.annotate(nm, (t[2], t[1]), xytext=(t[2] + dx, t[1] * dy), fontsize=7.4,
                                   arrowprops=dict(arrowstyle="-", lw=0.5, color="#888888")))
    halo(ann)
    ax.text(33, 1.9, "EVERYWHERE AND COMMON\n%d creatures — the homogenizers:\nthey will make every biome feel the same" % len(ub),
            fontsize=8.4, color=C_DARK, ha="center")
    ax.set_yscale("log"); ax.set_xlim(-0.5, 48); ax.set_ylim(0.0004, 4.5)
    ax.set_xlabel("biome spread — number of BiomeDefs where the creature spawns (commonality > 0)")
    ax.set_ylabel("top commonality across those biomes (log)")
    ax.set_title("Who will be everywhere: 25 creatures are both widespread (≥20 biomes) and common (top ≥ 0.3) —\n"
                 "11 of them Alpha Animals; biome identity dies by ubiquity, not by any single bad def", fontsize=11, loc="left")
    ax.legend(loc="lower left", fontsize=7.6, framealpha=0.95)
    ax.grid(True, which="major", lw=0.4, alpha=0.3)
    fig.text(0.012, 0.02,
             "Live creatures with at least one spawn biome, n=%d. Spread counts ALL registered BiomeDefs (52, modded included), not only those on\n"
             "Ash'karr — an upper bound on campaign ubiquity. Y log (disclosed). Quadrant thresholds (spread 20, commonality 0.3) are stated analytic\n"
             "choices. %s" % (len(pop), src_line()), **FOOT)
    fig.subplots_adjust(left=0.08, right=0.985, top=0.9, bottom=0.13)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(VIZ, "fig7_dominance.%s" % ext))
    plt.close(fig)
    return dict(pop=len(pop), ubiq=[(r["defName"], tc, sp, r["mod"]) for r, tc, sp in sorted(ub, key=lambda t: -t[2])])

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
