#!/usr/bin/env python3
"""biome_sheet_stats.py — per-biome stats for the biome sheets, from the
CURRENT world state (GOLDEN_SHEET_REFRESH_1).

🔴 The canon CSV's `biome` column is the PRE-REBAND world. The current biome of
any tile is the CSV OVERLAID, in order, with the eight plan JSONs below
(BENCH_REBOOT_HANDOFF_202609081448, "the one thing to carry forward"). A reader
who measures from the CSV alone gets a world two dozen repaints out of date.
Every other column (arc, temp, elevation, region, bearing…) is CSV-authoritative.

    python3 src/RimMandrake/Utils/biome_sheet_stats.py            # table to stdout
    python3 src/RimMandrake/Utils/biome_sheet_stats.py --json PATH  # machine form

Read-only. The save is the world; this reconstructs it offline — when the
bridge is available, a live jawa/world_tiles_get read of a few spot tiles is
the cheap cross-check.
"""
import argparse
import collections
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CSV = os.path.join(ROOT, "world", "ASHKARR_WORLDMAP_tiles.csv")

# In application order — later plans overwrite earlier ones.
OVERLAYS = [
    "backside_reband_full.json",
    "pf_terminator_plan.json",
    "wasteland_reclaim_plan.json",
    "crag_meander_plan.json",
    "pf_meander_plan.json",
    "graycrags_coldonly_plan.json",
    "fungalforest_dissolve_plan.json",
    "straggler_cleanup_plan.json",
]


def current_tiles():
    """-> list of CSV row dicts with `biome` replaced by the overlaid value."""
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    by_tile = {int(r["tile"]): r for r in rows}
    applied = 0
    for name in OVERLAYS:
        plan = json.load(open(os.path.join(ROOT, "world", name), encoding="utf-8"))
        for step in plan:
            t = by_tile.get(int(step["tile"]))
            if t is not None:
                t["biome"] = step["to"]
                applied += 1
    return rows, applied


def pctl(sorted_vals, p):
    if not sorted_vals:
        return None
    i = min(len(sorted_vals) - 1, max(0, round(p / 100 * (len(sorted_vals) - 1))))
    return sorted_vals[i]


def biome_stats(rows):
    by_biome = collections.defaultdict(list)
    for r in rows:
        by_biome[r["biome"]].append(r)
    out = {}
    for biome, tiles in sorted(by_biome.items()):
        arc = sorted(float(t["arc"]) for t in tiles)
        lat = sorted(abs(float(t["lat"])) for t in tiles)
        tmp = sorted(float(t["temp_c"]) for t in tiles)
        elev = sorted(int(t["elev_m"]) for t in tiles)
        rain = sorted(float(t["rain_mm"]) for t in tiles)
        water = sum(1 for t in tiles if t["water"] not in ("0", "", "0.0"))
        rivers = sum(1 for t in tiles if float(t["river_flow"] or 0) > 0)
        regions = collections.Counter(t["region"] for t in tiles)
        sectors = collections.Counter(int(float(t["bearing"]) // 30) % 12 for t in tiles)
        # RimWorld Hilliness enum: 1 Flat, 2 SmallHills, 3 LargeHills,
        # 4 Mountainous, 5 Impassable
        hill = collections.Counter(int(t["hilliness"] or 0) for t in tiles)
        # per-region climate mini-stats inside this biome (SHEET_SUBMEASURE_REFRESH_1)
        reg_rows = collections.defaultdict(list)
        for t in tiles:
            reg_rows[t["region"]].append(t)
        reg_stats = {}
        for reg, rts in reg_rows.items():
            ra = sorted(float(t["arc"]) for t in rts)
            rt = sorted(float(t["temp_c"]) for t in rts)
            re_ = sorted(int(t["elev_m"]) for t in rts)
            reg_stats[reg] = {"n": len(rts), "arc_med": pctl(ra, 50),
                              "temp_med": pctl(rt, 50), "elev_med": pctl(re_, 50)}
        out[biome] = {
            "tiles": len(tiles),
            "arc_min": arc[0], "arc_max": arc[-1],
            "arc_p10": pctl(arc, 10), "arc_med": pctl(arc, 50), "arc_p90": pctl(arc, 90),
            "abslat_med": pctl(lat, 50),
            "temp_p10": pctl(tmp, 10), "temp_med": pctl(tmp, 50), "temp_p90": pctl(tmp, 90),
            "temp_max": tmp[-1],
            "elev_med": pctl(elev, 50), "elev_max": elev[-1],
            "rain_med": pctl(rain, 50), "rain_max": rain[-1],
            "water_tiles": water, "river_tiles": rivers,
            "rain_zero_tiles": sum(1 for t in tiles if float(t["rain_mm"] or 0) == 0),
            "hilliness": {"flat": hill.get(1, 0), "small": hill.get(2, 0),
                          "large": hill.get(3, 0), "mountainous": hill.get(4, 0),
                          "impassable": hill.get(5, 0)},
            "region_stats": reg_stats,
            "regions": regions.most_common(),
            "sectors_present": len(sectors),
            "sector_min": min(sectors.values()) if sectors else 0,
            "sector_max": max(sectors.values()) if sectors else 0,
            "sector_counts": [sectors.get(i, 0) for i in range(12)],
        }
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", help="also write full stats as JSON here")
    ap.add_argument("--biome", help="print only this biome def")
    args = ap.parse_args(argv)
    rows, applied = current_tiles()
    stats = biome_stats(rows)
    print("MEASURED %d tiles; %d overlay repaints applied (%d plans)"
          % (len(rows), applied, len(OVERLAYS)))
    for biome, s in stats.items():
        if args.biome and biome != args.biome:
            continue
        print("%-28s %5d tiles  arc %.0f→%.0f (p10/med/p90 %.0f/%.0f/%.0f)  "
              "temp %.0f/%.0f/%.0f°C  elev med %dm (max %d)  water %d  "
              "sectors %d/12 (%d–%d)"
              % (biome, s["tiles"], s["arc_min"], s["arc_max"], s["arc_p10"],
                 s["arc_med"], s["arc_p90"], s["temp_p10"], s["temp_med"],
                 s["temp_p90"], s["elev_med"], s["elev_max"], s["water_tiles"],
                 s["sectors_present"], s["sector_min"], s["sector_max"]))
        if args.biome:
            print("  regions:", ", ".join("%s %d" % rc for rc in s["regions"]))
            print("  sector counts (0–11):", s["sector_counts"])
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=1)
        print("json ->", args.json)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
