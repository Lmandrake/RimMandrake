#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_flora_distribution_portfolio.py — figs F1–F3: the LANDED flora assignment.

The fauna portfolios (figs 4–8, 9–11) never look at plants. This one does, and it
asks the three questions that decide whether the flora assignment is buildable:

  figF1  landed vs purged   per-BiomeDef count of landed flora rows and per-sheet
                            count of purge rulings. The shape of the flora work.
  figF2  temperature fit    each landed plant's [minGrowthTemp, maxGrowthTemp]
                            window against its biome's own MEASURED climate
                            envelope. A plant whose window does not contain the
                            biome's median temperature will not grow there —
                            the known case is the Rot (median −18.8 °C) vs the
                            fungal suite (minGrowthTemp 0 °C).
  figF3  flammability       per-biome Flammability of the landed flora, against
                            arid shrubland's ban 9 ("No flammable living flora").
                            Plants with no Flammability statBase, and the 35
                            authored-later new_defs that have no def at all, are
                            drawn on an explicit UNMEASURED rail — never as 0.

DATA HONESTY
  flora residency + commonality : biomes/rosters/*.json via rosters_residency.py.
                                  Commonality is a DESIGN CHOICE.
  growth temperatures           : design/Jawa/mods/plant_pool.csv — MEASURED.
  biome climate envelopes       : review/biome_climate.json — transcribed VERBATIM
                                  from each sheet's "## 0. The measurements
                                  everything rests on" block, with the sheet's own
                                  wording carried beside every number. Sheets that
                                  state no temperature are UNMEASURED and their
                                  rows say so; nothing is interpolated.
                                  (_freeze_matrix.csv was NOT used: it condenses
                                  the same §0 blocks and loses the p10/p90 spread.)
  flammability                  : review/plant_flammability.json — MEASURED from
                                  the inheritance-resolved def dump (plants inherit
                                  Flammability from abstract PlantBase parents, so
                                  raw mod XML cannot be grepped for it). Refresh:
                                    python3 <this file> --refresh-flammability
  ⛔ nothing here reads the creature register's residency fields.

Run from repo root:
  python3 design/Jawa/worldbuilding/review/gen_flora_distribution_portfolio.py
"""
from __future__ import annotations

import collections
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rosters_residency as RR

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VIZ = os.path.join(HERE, "viz")
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
POOL = os.path.join(ROOT, "design", "Jawa", "mods", "plant_pool.csv")
CLIMATE = os.path.join(HERE, "biome_climate.json")
FLAM = os.path.join(HERE, "plant_flammability.json")
DEFDB = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
         "RimWorld by Ludeon Studios/DefDump/defs.sqlite")
os.makedirs(VIZ, exist_ok=True)

C_GRAY = "#9aa0a6"; C_BLUE = "#3b6fb5"; C_ORANGE = "#d97706"; C_RED = "#c0392b"
C_GREEN = "#2e7d4f"; C_DARK = "#333333"; C_PURPLE = "#6b4fa0"
FOOT = dict(fontsize=7.0, color="#666666")

ROST = RR.load()


def num(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f


with open(POOL, encoding="utf-8") as f:
    POOLROWS = {r["defName"]: r for r in csv.DictReader(f)}
with open(CLIMATE, encoding="utf-8") as f:
    CLIM = json.load(f)
with open(FLAM, encoding="utf-8") as f:
    FLAMDOC = json.load(f)
FLAMMABILITY = FLAMDOC["flammability"]
FLAM_UNMEASURED = set(FLAMDOC["unmeasured"])

def is_directive(d):
    """A purge row whose `def` is a RULING over an unknown set rather than one
    defName — "ALL", "donor vanilla wildPlants, wholesale". A defName that is
    simply absent from plant_pool.csv (PlantTreeOak, grimpepper) is still ONE
    named plant and must not be miscounted as a wholesale ruling."""
    return d.startswith("ALL") or " " in d or "(" in d


WILDCARD_PURGES = {d for sh in ROST.flora_purged
                   for d in [x["def"] for x in ROST.flora_purged[sh]]
                   if is_directive(d)}
PURGES_OFF_POOL = {d for sh in ROST.flora_purged
                   for d in [x["def"] for x in ROST.flora_purged[sh]]
                   if not is_directive(d) and d not in POOLROWS}


def src_line():
    return ("Flora residency + commonality: design/Jawa/worldbuilding/biomes/rosters/*.json (authored 2026-09-09) via rosters_residency.py — commonality is a\n"
            "DESIGN CHOICE. Growth temperatures: design/Jawa/mods/plant_pool.csv (MEASURED, %d plant defs). Climate: review/biome_climate.json, transcribed verbatim\n"
            "from each biome sheet's §0 MEASURED block. Flammability: review/plant_flammability.json, from the def dump %s (%d mods, %d of %d pool defs carry the stat)."
            % (len(POOLROWS), FLAMDOC["_dump_provenance"]["captured_utc"][:10],
               int(FLAMDOC["_dump_provenance"]["mod_count"]),
               FLAMDOC["_measured"]["with_flammability"], FLAMDOC["_measured"]["pool_defs"]))


# ------------------------------------------------------------- figF1
def figF1():
    rows = []
    for b in ROST.biome_defs:
        landed = ROST.flora_residents(b)
        purged, wild = 0, 0
        for sheet in ROST.sheets_of_biome[b]:
            for x in ROST.flora_purged.get(sheet, []):
                if is_directive(x["def"]):
                    wild += 1
                else:
                    purged += 1
        newp = sum(1 for sheet in ROST.sheets_of_biome[b]
                   for x in ROST.new_defs.get(sheet, []) if x.get("kind") == "plant")
        rows.append(dict(biome=b, landed=len(landed), purged=purged, wild=wild, new=newp,
                         mass=sum(r.commonality for r in landed)))
    rows.sort(key=lambda r: (r["landed"] + r["purged"], r["landed"]))

    fig, ax = plt.subplots(figsize=(13.0, 10.4), dpi=150)
    y = np.arange(len(rows))
    ax.barh(y + 0.20, [r["landed"] for r in rows], height=0.34, color=C_GREEN, zorder=3,
            label="flora LANDED (roster rows)")
    ax.barh(y - 0.20, [-r["purged"] for r in rows], height=0.34, color=C_RED, zorder=3,
            label="donor flora PURGED (named defs)")
    ax.barh(y - 0.20, [-r["wild"] for r in rows], left=[-r["purged"] for r in rows],
            height=0.34, color="#e8b4ad", zorder=3,
            label="wholesale / wildcard purge rulings (\"ALL\", \"donor vanilla wildPlants\")")
    ax.barh(y + 0.20, [r["new"] for r in rows], left=[r["landed"] for r in rows],
            height=0.34, color=C_PURPLE, alpha=0.55, zorder=3,
            label="authored-later new plant defs (no def yet — UNMEASURABLE)")
    ax.axvline(0, color=C_DARK, lw=0.9, zorder=4)
    for i, r in enumerate(rows):
        if r["landed"] + r["new"]:
            ax.text(r["landed"] + r["new"] + 0.6, i + 0.20, "%d%s" % (r["landed"], (" +%d new" % r["new"]) if r["new"] else ""),
                    va="center", fontsize=6.9, color=C_DARK)
        if r["purged"] + r["wild"]:
            ax.text(-(r["purged"] + r["wild"]) - 0.6, i - 0.20,
                    "%d%s" % (r["purged"], (" +%d wholesale" % r["wild"]) if r["wild"] else ""),
                    va="center", ha="right", fontsize=6.9, color=C_RED)
    ax.set_yticks(y); ax.set_yticklabels([r["biome"] for r in rows], fontsize=7.8)
    ax.set_ylim(-0.8, len(rows) - 0.2)
    lo = min(-(r["purged"] + r["wild"]) for r in rows)
    hi = max(r["landed"] + r["new"] for r in rows)
    ax.set_xlim(lo * 1.35, hi * 1.35)
    ax.set_xlabel("← donor flora purged        |        flora landed →   (roster rows, not species: one def in two biomes counts twice)")
    ax.grid(True, axis="x", lw=0.4, alpha=0.3, zorder=0)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.legend(loc="lower left", fontsize=7.4, framealpha=0.96)
    tl = sum(r["landed"] for r in rows); tp = sum(r["purged"] for r in rows)
    ax.set_title("The flora assignment is mostly SUBTRACTION: %d landed rows against %d named purges (+%d wholesale rulings) across %d BiomeDefs.\n"
                 "%d distinct plant defs landed; %d authored-later plant defs are owed as NEW art/defs and cannot be measured against anything yet."
                 % (tl, tp, sum(r["wild"] for r in rows), len(rows), len(ROST.flora_residency),
                    sum(1 for s in ROST.new_defs for x in ROST.new_defs[s] if x.get("kind") == "plant")),
                 fontsize=10.6, loc="left")
    fig.text(0.008, 0.014,
             "Purges are recorded per SHEET, so a sheet binding several BiomeDefs shows the same purge count on each of its bars (the Forge's three defs, the two\n"
             "propane defs, the blue desert's two) — that is the ruling's real scope, not double counting. A purge row whose `def` is a directive rather than a\n"
             "defName (\"ALL\", \"donor vanilla wildPlants, wholesale\") is counted separately because it is one ruling over an unknown number of plants; %d named\n"
             "purge targets sit outside plant_pool.csv (%s) and are counted as named purges, not wholesale.\n%s"
             % (len(PURGES_OFF_POOL), ", ".join(sorted(PURGES_OFF_POOL)[:5]), src_line()), **FOOT)
    fig.subplots_adjust(left=0.185, right=0.985, top=0.925, bottom=0.155)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(VIZ, "figF1_flora_landed_purged.%s" % ext))
    plt.close(fig)
    return dict(landed_rows=tl, landed_defs=len(ROST.flora_residency), purged=tp,
                wildcard=sorted(WILDCARD_PURGES),
                top=[(r["biome"], r["landed"], r["purged"]) for r in rows[::-1][:6]])


# ------------------------------------------------------------- figF2
def figF2():
    rows, unmeasured = [], []
    for b in ROST.biome_defs:
        fl = ROST.flora_residents(b)
        if not fl:
            continue
        c = CLIM["biomes"].get(b)
        med = c and c.get("median")
        if med is None:
            unmeasured.append((b, len(fl), (c or {}).get("form", "no entry")))
            continue
        rows.append((b, c, fl))
    rows.sort(key=lambda t: t[1]["median"])

    fig, ax = plt.subplots(figsize=(13.8, 9.6), dpi=150)
    rng = np.random.default_rng(31)
    XLO, XHI = -95.0, 82.0          # one plant (BMT_Blastpod) declares maxGrowthTemp
    bad, clipped = [], []           # 352 °C, which would flatten every other segment

    for i, (b, c, fl) in enumerate(rows):
        lo = c.get("p10") if c.get("p10") is not None else c.get("floor")
        hi = c.get("p90") if c.get("p90") is not None else c.get("max")
        if lo is not None and hi is not None:
            ax.barh(i, hi - lo, left=lo, height=0.74, color="#dbe4f0", zorder=1)
        ax.plot([c["median"]] * 2, [i - 0.40, i + 0.40], color=C_BLUE, lw=2.0, zorder=5)
        ys = i + rng.uniform(-0.30, 0.30, len(fl))
        for q, yy in zip(fl, ys):
            r = POOLROWS.get(q.defName)
            if not r:
                continue
            a, z = num(r["minGrowthTemp"]), num(r["maxGrowthTemp"])
            if a is None or z is None:
                continue
            fits = a <= c["median"] <= z
            za = min(z, XHI - 1.0)
            if z > XHI - 1.0:
                clipped.append((q.defName, z))
                ax.scatter(XHI - 1.0, yy, s=13, marker=">",
                           c=C_GRAY if fits else C_RED, zorder=7)
            ax.plot([max(a, XLO + 1.0), za], [yy, yy], lw=1.5 if fits else 2.4,
                    color=C_GRAY if fits else C_RED, alpha=0.75, zorder=3 if fits else 6,
                    solid_capstyle="butt")
            if not fits:
                gap = (a - c["median"]) if c["median"] < a else (c["median"] - z)
                bad.append((b, q.defName, round(c["median"], 1), a, z, round(gap, 1), q.commonality))
    worst = sorted(bad, key=lambda t: -t[5])[:7]
    # Leader lines were tried and every one crossed another (the misfits stack on
    # three rows); the ranked list carries the same information without the noise.
    if worst:
        box = ["WORST MISFITS — biome median outside the plant's growth window"]
        for b, d, m, a, z, gap, comm in worst:
            box.append("  %-18s in %-26s  biome %6.4g °C, grows %g…%g   %.4g °C short"
                       % (d[:18], b[:26], m, a, z, gap))
        ax.text(XLO + 2.0, len(rows) + 3.15, "\n".join(box), fontsize=6.6, color=C_RED,
                ha="left", va="top", family="DejaVu Sans Mono", zorder=9,
                bbox=dict(boxstyle="round,pad=0.45", fc="white", ec="#e0b6ae", lw=0.7))
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(["%s  (%d flora, median %.4g °C)" % (b, len(fl), c["median"]) for b, c, fl in rows],
                       fontsize=7.8)
    ax.set_ylim(-0.8, len(rows) + 3.3)
    ax.set_xlim(XLO, XHI)
    ax.set_xlabel("temperature °C — plant segments are [minGrowthTemp … maxGrowthTemp] (MEASURED); biome bar is the sheet's own p10–p90 (or floor–max)")
    ax.axvline(0, color="#bbbbbb", lw=0.8, ls=":")
    ax.grid(True, axis="x", lw=0.4, alpha=0.3)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.legend(handles=[Line2D([], [], c=C_GRAY, lw=1.5, label="plant grows at the biome median"),
                       Line2D([], [], c=C_RED, lw=2.4, label="plant CANNOT grow at the biome median (%d of %d rows)" % (len(bad), sum(len(f) for _, _, f in rows))),
                       Line2D([], [], c=C_BLUE, lw=2.0, label="biome median temperature (sheet §0)"),
                       Line2D([], [], c="#dbe4f0", lw=8, label="biome p10–p90 (or floor–max where the sheet gives no percentiles)")],
              loc="lower right", fontsize=7.4, framealpha=0.96)
    ax.set_title("Does the landed flora survive its own biome?  %d of %d landed flora rows sit in a biome whose MEDIAN temperature\n"
                 "is outside the plant's own growth window — the Rot alone contributes %d of them."
                 % (len(bad), sum(len(f) for _, _, f in rows),
                    sum(1 for t in bad if t[0] == "AB_MycoticJungle")),
                 fontsize=10.6, loc="left")
    import textwrap
    note = textwrap.fill(
        "EXCLUDED, not guessed — biomes with landed flora whose sheet states no temperature: "
        + ("; ".join("%s (%d flora, %s)" % (b, n, f.split("—")[0].strip()[:38]) for b, n, f in unmeasured)
           if unmeasured else "none"), 172)
    fig.text(0.008, 0.012,
             "%s\n"
             "minGrowthTemp/maxGrowthTemp are the plant's hard grow limits; the OPTIMAL window (minOptTemp/maxOptTemp) is narrower still and is not drawn — a plant drawn grey\n"
             "may still grow badly. A biome's median is one number over its whole tile set: a plant failing the median may survive its warm tail, so a red row is a design\n"
             "question, not proof of a dead plant. %s\n%s"
             % (note,
                ("→ clipped at %g °C: %s" % (XHI - 1.0, ", ".join("%s max %g" % c for c in sorted(set(clipped), key=lambda t: -t[1])[:3]))) if clipped else "",
                src_line()), **FOOT)
    fig.subplots_adjust(left=0.235, right=0.985, top=0.925, bottom=0.185)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(VIZ, "figF2_flora_temperature_fit.%s" % ext))
    plt.close(fig)
    return dict(mismatches=len(bad), worst=worst, unmeasured_biomes=unmeasured,
                rows=sum(len(f) for _, _, f in rows))


# ------------------------------------------------------------- figF3
def figF3():
    rows = []
    for b in ROST.biome_defs:
        fl = ROST.flora_residents(b)
        if fl:
            rows.append((b, fl))
    rows.sort(key=lambda t: (max((FLAMMABILITY.get(q.defName, -1) for q in t[1]), default=-1),
                             len(t[1])))

    fig, ax = plt.subplots(figsize=(13.4, 9.6), dpi=150)
    rng = np.random.default_rng(37)
    RAIL = -0.14
    XHI = 1.9                       # one plant (BMT_GreyLady) declares Flammability 40
    unm = collections.defaultdict(list)
    hot, clipped = [], []
    for i, (b, fl) in enumerate(rows):
        ys = i + rng.uniform(-0.28, 0.28, len(fl))
        for q, yy in zip(fl, ys):
            v = FLAMMABILITY.get(q.defName)
            if v is None:
                unm[b].append(q.defName)
                ax.scatter(RAIL, yy, s=22, c=C_PURPLE, marker="x", zorder=5)
                continue
            if v > XHI - 0.06:
                clipped.append((q.defName, v))
                ax.scatter(XHI - 0.06, yy, s=26, c=C_RED, marker=">", zorder=6)
                ax.text(XHI - 0.10, yy, "%s %g " % (q.defName, v), fontsize=6.4,
                        color=C_RED, ha="right", va="center", zorder=7)
            else:
                ax.scatter(v, yy, s=10 + 44 * np.sqrt(min(q.commonality, 1.5)),
                           c=C_RED if v > 0 else C_GREEN, alpha=0.72, lw=0, zorder=4)
            if v > 0:
                hot.append((b, q.defName, v, q.commonality))
    ax.axvline(0, color=C_GREEN, lw=1.0, ls="--", zorder=2)
    n_unm = sum(len(v) for v in unm.values())
    if n_unm:
        ax.axvline(RAIL / 2, color="#bbbbbb", lw=0.7, ls=":")
        ax.text(RAIL, -0.55, "UNMEASURED rail\n(no Flammability statBase)", fontsize=6.8,
                color=C_PURPLE, ha="center", va="bottom")

    # arid shrubland ban 9 verdict
    ash = [t for t in hot if t[0] == "AridShrubland"]
    ashi = next((i for i, (b, _) in enumerate(rows) if b == "AridShrubland"), None)
    if ashi is not None:
        n_ash = len(ROST.flora_residents("AridShrubland"))
        ax.text(1.36, ashi, "ban 9: 'No flammable living flora'\n→ %d of %d landed flora burn"
                % (len(ash), n_ash), fontsize=7.4, color=C_RED if ash else C_GREEN,
                va="center", ha="left", weight="bold")

    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(["%s  (%d flora)" % (b, len(fl)) for b, fl in rows], fontsize=7.8)
    ax.set_ylim(-0.8, len(rows) - 0.15)
    ax.set_xlim(RAIL - 0.06, XHI)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel("Flammability (resolved statBase; 0 = will not burn, 1.0 = vanilla plant default) — MEASURED from the def dump")
    ax.grid(True, axis="x", lw=0.4, alpha=0.3)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    nunm = n_unm
    newp = sum(1 for s in ROST.new_defs for x in ROST.new_defs[s] if x.get("kind") == "plant")
    handles = [Line2D([], [], marker="o", ls="", c=C_GREEN, label="Flammability 0 — fireproof"),
               Line2D([], [], marker="o", ls="", c=C_RED, label="Flammability > 0 — will burn")]
    if nunm:
        handles.append(Line2D([], [], marker="x", ls="", c=C_PURPLE,
                              label="UNMEASURED: no Flammability statBase, n=%d rows" % nunm))
    ax.legend(handles=handles, loc="lower right", fontsize=7.4, framealpha=0.96)
    ax.set_title("Flammability of the landed flora — %d of %d landed rows burn.  %s\n"
                 "Marker area ∝ √commonality; the %d authored-later plant defs are absent from this figure entirely (no def exists to measure)."
                 % (len(hot), sum(len(f) for _, f in rows),
                    ("AridShrubland's ban 9 is currently VIOLATED by %d landed flora." % len(ash)) if ash
                    else "AridShrubland's ban 9 (no flammable living flora) holds on the landed roster.",
                    newp),
                 fontsize=10.4, loc="left")
    fig.text(0.008, 0.014,
             "Flammability is inheritance-resolved: most plants take it from an abstract PlantBase parent and declare nothing themselves, so a raw mod-XML grep\n"
             "returns confident wrong numbers. %d of the %d plant_pool defs carry the stat in the dump; the %d that do not are stump/filler defs, not plants.\n"
             "%s\n%s"
             % (FLAMDOC["_measured"]["with_flammability"], FLAMDOC["_measured"]["pool_defs"],
                FLAMDOC["_measured"]["without"],
                ("Rows with an × carry a pool def the dump has no Flammability for — an honest gap on its own rail, never plotted as 0."
                 if nunm else
                 "MEASURED COVERAGE IS COMPLETE: every one of the %d landed flora rows has a resolved Flammability, so there is no UNMEASURED rail on this figure."
                 % sum(len(f) for _, f in rows)),
                src_line()), **FOOT)
    fig.subplots_adjust(left=0.205, right=0.985, top=0.915, bottom=0.165)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(VIZ, "figF3_flora_flammability.%s" % ext))
    plt.close(fig)
    return dict(burning=len(hot), rows=sum(len(f) for _, f in rows),
                arid_shrubland_ban9=[(d, v, c) for b, d, v, c in ash],
                unmeasured={k: v for k, v in unm.items()},
                hottest=sorted(hot, key=lambda t: -t[2])[:10])


# ------------------------------------------------------------- flammability refresh
def refresh_flammability():
    """Re-read Flammability for the whole plant pool from the live def dump.
    Kept as a committed cache so the figure is reproducible without the dump."""
    import sqlite3
    c = sqlite3.connect("file:%s?mode=ro" % DEFDB, uri=True)
    prov = {k: v for k, v in c.execute("select key,value from provenance")}
    out, miss = {}, []
    for d in POOLROWS:
        row = c.execute("select json from defs where def_name=? and def_type='ThingDef'", (d,)).fetchone()
        vals = []
        if row:
            vals = [s["value"] for s in (json.loads(row[0]).get("fields", {}).get("statBases") or [])
                    if s.get("stat") == "Flammability"]
        (out.update({d: vals[0]}) if vals else miss.append(d))
    doc = dict(FLAMDOC)
    doc["_dump_provenance"] = prov
    doc["_measured"] = dict(pool_defs=len(POOLROWS), with_flammability=len(out), without=len(miss))
    doc["unmeasured"] = sorted(miss)
    doc["flammability"] = {k: out[k] for k in sorted(out)}
    with open(FLAM, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
    print("refreshed %s: %d/%d with Flammability, dump %s"
          % (FLAM, len(out), len(POOLROWS), prov["captured_utc"]))


if __name__ == "__main__":
    if "--refresh-flammability" in sys.argv:
        refresh_flammability()
        sys.exit(0)
    res = dict(figF1=figF1(), figF2=figF2(), figF3=figF3())
    print(json.dumps(res, indent=1, default=str)[:6000])
    print("\nwrote figs F1-F3 (png+svg) to", VIZ)
