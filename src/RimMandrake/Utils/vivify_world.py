#!/usr/bin/env python3
r"""vivify_world.py — read the world out of a LIVE RimWorld and write it back in our
own CSV bundle format, with the numbers the game actually computed.

🔴 Owner, 2026-08-23: *"the utility that sucks a map out of a live game and dumps it as
precisely the same style of CSV that you currently use to store our map... but with all
the numbers populated (such as max/min instead of just mean temperature). That would make
a 'vivified' version of our initial CSV with perfectly game-consistent numbers."*

WHAT "VIVIFIED" MEANS HERE
==========================
`world/ASHKARR_WORLDMAP_tiles.csv` is AUTHORED — it is what we asked the planet to be.
The running game is what the engine MADE of that request, after biome resolution, after
Cherry Picker, after every mod's patches. Those are two different objects and the
authored one has always been the only one on disk.

This writes the second one, in the first one's format, so every tool we already have
reads it with no change.

⭐ THE COLUMN ORDER IS THE CONTRACT. The first fourteen columns are byte-for-byte the
existing header, in the existing order:

    tile,lat,lon,arc,bearing,elev_m,temp_c,rain_mm,biome,water,river_flow,region,
    hilliness,swampiness

Everything new is APPENDED after them. `csv.DictReader` keys by name and ignores extras,
so `worldview.py`, `ashkarr_*.py` and every other consumer take a vivified bundle as a
drop-in. ⛔ Do not reorder or rename the first fourteen to make room for a new field;
append, or you break every reader at once.

PROVENANCE, PER COLUMN, ALWAYS
==============================
🔑 Not every column can be measured from every source, and a column quietly carried over
from the authored bundle while wearing the word "vivified" would be the worst possible
outcome of this tool. So each column is written with one of three origins and the run
prints and records them:

    MEASURED   the live game answered for this column, this run
    CARRIED    copied from the reference bundle - the live source did not offer it
    DERIVED    computed here from measured values (arc and bearing, from lat/lon)

The sidecar `<stem>_provenance.json` carries the same table, so a bundle can always be
asked where it came from rather than assumed to be whole.

SOURCES
=======
`--from-export FILE`   OFFLINE. Reads a CSV already written by `jawa/world_tile_export`.
                       Handles BOTH forms and tells them apart from the HEADER, never
                       from a flag: the nine-column original, and the twenty-column
                       `extended=true` form that adds tempMin, tempMax, seasonalShift,
                       pollution, riverDist, feature, featureId, waterCovered and the
                       three counts. No bridge, no game needed — this is the mode to use
                       when someone else holds the bridge.
`--live`               Calls the bridge for the export plus the per-tile scalars and the
                       feature table, so `region`, `water`, `river_flow` and the extra
                       columns are MEASURED too.

⛔ THE BRIDGE BELONGS TO CHECK. `--live` is not the default and never will be. Run the
offline mode against an export file unless the bridge is yours.

🔴 THE DERIVED TEMPERATURES ARE NOT AVAILABLE YET, AND THIS TOOL SAYS SO RATHER THAN
GUESSING. The owner asked specifically for min/max instead of just mean. Measured against
the live 121-tool companion on 2026-08-23: **no `jawa/` tool returns them.**
`jawa/world_tile_get`'s own description names `MinTemperature` and `MaxTemperature`, but
its payload carries only `temperature`, the mean. They need one new `[Tool]` method in
JawaBench, which needs a DLL build and a game-down window.
⛔ Do NOT "fix" this by recomputing them here from the mean and the latitude. The whole
value of a vivified bundle is that its numbers came from the engine; a plausible number
computed in Python is exactly the thing this tool exists to replace. Until the tool
exists, `temp_min_c` and `temp_max_c` write empty and read UNMEASURED.

USAGE
=====
    # offline, against an export already on disk
    # <DefDump> is whatever `python3 src/RimMandrake/Utils/game_paths.py` prints
    # for "DefDump root" — spelling it out here is how this example goes stale.
    python3 src/RimMandrake/Utils/vivify_world.py \
        --from-export "<DefDump>/world_tiles_raven.csv" \
        --reference world/ASHKARR_WORLDMAP --out world/ASHKARR_VIVIFIED

    # what changed between what we asked for and what the game made
    python3 src/RimMandrake/Utils/vivify_world.py --from-export <file> \
        --reference world/ASHKARR_WORLDMAP --diff-only
"""

import argparse
import csv
import json
import math
import os
import re
import subprocess
import sys

# The authored bundle's header, in order. ⛔ This tuple IS the compatibility contract
# with every existing reader - see the module docstring before touching it.
BASE_COLUMNS = ("tile", "lat", "lon", "arc", "bearing", "elev_m", "temp_c", "rain_mm",
                "biome", "water", "river_flow", "region", "hilliness", "swampiness")

# Appended, never inserted. Empty string means UNMEASURED - see `temp_min_c` below.
EXTRA_COLUMNS = ("temp_min_c", "temp_max_c", "seasonal_shift_c", "pollution",
                 "river_dist", "road_count", "river_count", "mutator_count",
                 "feature_id")

# Our column name <- the column `jawa/world_tile_export extended=true` writes. The
# extended export appends these after the original nine and never reorders them, so a
# file written by the OLD companion simply lacks them and every lookup below misses,
# which is exactly the behaviour we want: absent means UNMEASURED, not zero.
EXTENDED_FROM_EXPORT = {
    "temp_min_c": "tempMin",
    "temp_max_c": "tempMax",
    "seasonal_shift_c": "seasonalShift",
    "pollution": "pollution",
    "river_dist": "riverDist",
    "road_count": "roadCount",
    "river_count": "riverCount",
    "mutator_count": "mutatorCount",
    "feature_id": "featureId",
}

# RimWorld's Hilliness enum, in declaration order. The authored bundle stores the int;
# `world_tile_export` writes the NAME, so one of the two has to be translated and it is
# cheaper to translate the live side than to migrate 21,872 authored rows.
HILLINESS = {"Undefined": 0, "Flat": 1, "SmallHills": 2, "LargeHills": 3,
             "Mountainous": 4, "Impassable": 5}

MEASURED, CARRIED, DERIVED, UNMEASURED = "MEASURED", "CARRIED", "DERIVED", "UNMEASURED"


def ab_of(lat_deg, lon_deg):
    """(arc, bearing) for a lat/lon, in the frame the authored bundle uses.

    🔑 Lifted verbatim from `ashkarr_paint.py:ab_of`, which is the definition of record.
    arc is the angular distance from the SUBSTELLAR POINT at (0, 0) - this planet is
    tidally locked and arc is its real coordinate, which is why every climate script
    keys on it. bearing is the angle around that point.

    ⚠️ Do not "simplify" to colatitude. arc is 90 on the terminator, not at the equator.
    """
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    arc = math.degrees(math.acos(max(-1.0, min(1.0, math.cos(lon) * math.cos(lat)))))
    bear = math.degrees(math.atan2(math.sin(lat),
                                   math.cos(lat) * math.sin(lon))) % 360.0
    return arc, bear


def read_reference(stem):
    """The authored bundle's tiles, keyed by tile id. None if there is no reference."""
    path = stem + "_tiles.csv"
    if not os.path.exists(path):
        return None, path
    with open(path, encoding="utf-8") as fh:
        return {r["tile"]: r for r in csv.DictReader(fh)}, path


def read_export(path):
    """A `jawa/world_tile_export` CSV, keyed by tile id.

    ⚠️ `utf-8-sig`: the companion writes a BOM, and without this the first column name
    comes back as '﻿tile' and every lookup silently misses.
    """
    with open(path, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        sys.exit("export %s has no rows" % path)
    need = {"tile", "lat", "long", "biome", "elevation", "temperature",
            "rainfall", "hilliness", "swampiness"}
    missing = need - set(rows[0].keys())
    if missing:
        sys.exit("export %s is missing columns: %s\n"
                 "Is it really a jawa/world_tile_export file?"
                 % (path, ", ".join(sorted(missing))))
    return {r["tile"]: r for r in rows}


def build_rows(export, reference):
    """One vivified row per exported tile, plus the per-column provenance table."""
    prov = {c: UNMEASURED for c in BASE_COLUMNS + EXTRA_COLUMNS}
    for c in ("tile", "lat", "lon", "elev_m", "temp_c", "rain_mm", "biome",
              "hilliness", "swampiness"):
        prov[c] = MEASURED
    prov["arc"] = prov["bearing"] = DERIVED
    for c in ("water", "river_flow", "region"):
        prov[c] = CARRIED if reference else UNMEASURED

    # 🔑 Detected from the FILE, never from a flag. An export written before the
    # extended companion shipped is silently the nine-column form, and asking the
    # header is the only honest way to know which one is in front of us.
    sample = export[next(iter(export))]
    have = {k for k in EXTENDED_FROM_EXPORT if EXTENDED_FROM_EXPORT[k] in sample}
    for c in have:
        prov[c] = MEASURED
    if "feature" in sample:
        prov["region"] = MEASURED
    if "waterCovered" in sample:
        prov["water"] = MEASURED

    out = []
    for tid in sorted(export, key=lambda x: int(x)):
        e = export[tid]
        ref = reference.get(tid) if reference else None
        lat, lon = float(e["lat"]), float(e["long"])
        arc, bear = ab_of(lat, lon)

        row = {
            "tile": tid,
            "lat": "%.4f" % lat,
            "lon": "%.4f" % lon,
            "arc": "%.1f" % arc,
            "bearing": "%.2f" % bear,
            "elev_m": "%d" % round(float(e["elevation"])),
            "temp_c": "%.1f" % float(e["temperature"]),
            "rain_mm": "%g" % float(e["rainfall"]),
            "biome": e["biome"],
            # ⚠️ CARRIED, not measured. `world_tile_export` has no water, river or
            # feature column; the live values need `--live`, which uses the bridge.
            "water": (ref or {}).get("water", ""),
            "river_flow": (ref or {}).get("river_flow", ""),
            "region": (ref or {}).get("region", ""),
            "hilliness": "%d" % HILLINESS.get(e["hilliness"], 0),
            "swampiness": "%g" % float(e["swampiness"]),
        }
        for c in EXTRA_COLUMNS:
            src = EXTENDED_FROM_EXPORT[c]
            # ⛔ Empty, never 0, when the export does not carry it. A zero here would
            # read as "this tile has no rivers" rather than "nobody asked the game".
            row[c] = e.get(src, "") if src in e else ""
        # An extended export also names the tile's world region, which the base export
        # cannot, so `region` stops being CARRIED and becomes MEASURED for real.
        if "feature" in e:
            row["region"] = e["feature"]
        if "waterCovered" in e:
            row["water"] = e["waterCovered"]
        out.append(row)
    return out, prov


# ---------------------------------------------------------------------------
# LIVE HARVEST
# ---------------------------------------------------------------------------
# 🔑 WHY THIS SHELLS OUT INSTEAD OF IMPORTING THE CLIENT. RimBridge binds WINDOWS
# loopback and WSL2 is NAT-mode, so 127.0.0.1:5174 has no route from this side —
# `rimbridge_client.py` says exactly that and refuses. But every path this tool
# handles is a `/mnt/...` path, and Windows python cannot read the repo through one
# reliably. So the script stays WSL-side and spawns `python.exe` per call. It costs
# a process per bridge call; there are about a dozen of them for a whole planet.

CLIENT = "src/RimMandrake/Utils/rimbridge_client.py"


def win_to_wsl(path):
    r"""`C:/x/y` or `C:\x\y` -> `/mnt/c/x/y`. Returned paths mix both separators."""
    p = (path or "").replace("\\", "/")
    m = re.match(r"^([A-Za-z]):/(.*)$", p)
    return "/mnt/%s/%s" % (m.group(1).lower(), m.group(2)) if m else p


def call(tool, params=None, timeout=900):
    """One bridge call. Returns the parsed payload, or exits with the refusal.

    ⚠️ `--yes-i-know-this-is-live` is passed for every call here. That guard exists to
    stop an ACCIDENTAL write; everything this tool calls is a read, and the guard's
    heuristic cannot tell them apart. Nothing below writes to the game.
    """
    cmd = ["python.exe", CLIENT, "--call", tool, "--yes-i-know-this-is-live"]
    if params:
        cmd += ["--json", json.dumps(params)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    out = r.stdout or ""
    i = out.find("{")
    if i < 0:
        sys.exit("bridge call %s produced no JSON.\n%s\n%s"
                 % (tool, out.strip()[:400], (r.stderr or "").strip()[:400]))
    try:
        d = json.loads(out[i:])
    except ValueError as e:
        sys.exit("bridge call %s returned unparseable JSON: %s" % (tool, e))
    if d.get("success") is False:
        sys.exit("bridge refused %s: %s" % (tool, d.get("message")))
    return d


def harvest_live(batch=3000):
    """The whole planet, from the running game. Returns (export, extended_ok).

    ⭐ TWO CALLS' WORTH OF WORK, NOT 21,872. `world_tile_export` writes every tile to
    a file server-side in one call (86 ms measured for 21,872), and `world_tile_get`
    answers 3,000 tiles per call for the scalars the export does not carry. Eight
    batches covers this planet. ⛔ Do not "simplify" this to a per-tile loop.
    """
    # 1 — the base table, in one call. Ask for the extended form first; a companion
    #     that predates it refuses the unknown parameter and we fall back, rather than
    #     the caller having to know which DLL is deployed.
    res = call("jawa/world_tile_export", {"format": "csv", "extended": True})

    # 🔴 THE BRIDGE SILENTLY IGNORES A PARAMETER THE DEPLOYED TOOL DOES NOT DECLARE.
    # Measured 2026-08-23: asking a pre-extended companion for extended=true returns
    # success:true and writes the nine-column file. ⛔ So "the call worked" proves
    # NOTHING about whether the parameter was honoured, and an earlier version of this
    # function inferred it exactly that way and cheerfully printed "(EXTENDED)" over a
    # nine-column file. The tool's OWN `columns` list is the answer; it is built from
    # the same constant that writes the header, so it cannot disagree with the file.
    cols = res.get("columns") or []
    extended_ok = "tempMin" in cols
    path = win_to_wsl(res.get("path"))
    if not os.path.exists(path):
        sys.exit("the game reported writing %s but it is not readable from here.\n"
                 "Translated to: %s" % (res.get("path"), path))
    print("  world_tile_export -> %d tiles, %d columns%s"
          % (res.get("tilesTotal", -1), len(cols),
             "  EXTENDED" if extended_ok else ""))
    print("                       %s" % path)
    if not extended_ok:
        print("  ⚠️  asked for extended=true and the deployed companion IGNORED it — it "
              "predates the parameter.\n"
              "      The call still returned success:true. Deploy the new "
              "JawaBench.BridgeTools.dll to fill the derived columns.")
    export = read_export(path)

    # 2 — the scalars `world_tile_export` has never carried. Skipped entirely when the
    #     extended export already supplied them, because then it is pure duplication.
    if not extended_ok:
        ids = sorted(int(t) for t in export)
        got = 0
        for lo in range(ids[0], ids[-1] + 1, batch):
            hi = min(lo + batch - 1, ids[-1])
            d = call("jawa/world_tile_get",
                     {"range": "%d-%d" % (lo, hi), "limit": batch})
            for t in d.get("tiles", []):
                row = export.get(str(t["tile"]))
                if row is None:
                    continue
                # Named exactly as the extended export names them, so the single
                # EXTENDED_FROM_EXPORT mapping serves both sources and there is no
                # second translation table to drift.
                row["feature"] = t.get("feature") or ""
                row["featureId"] = t.get("featureId", -1)
                row["waterCovered"] = 1 if t.get("waterCovered") else 0
                row["pollution"] = t.get("pollution", "")
                row["riverDist"] = t.get("riverDist", "")
                row["roadCount"] = t.get("roadCount", "")
                row["riverCount"] = t.get("riverCount", "")
                row["mutatorCount"] = t.get("mutatorCount", "")
                got += 1
        print("  world_tile_get     -> %d tiles enriched in %d call(s)"
              % (got, (ids[-1] - ids[0]) // batch + 1))
    return export, extended_ok


def live_meta():
    """Provenance for the sidecar: which world this actually was."""
    info = call("jawa/world_info_get").get("info", {}) or {}
    return {k: info.get(k) for k in
            ("name", "seedString", "planetCoverage", "overallRainfall",
             "overallTemperature", "overallPopulation", "pollution", "factionCount")}


def diff(rows, reference, prov):
    """Where the live world disagrees with what we authored, column by column.

    🔑 This is the reason to run the tool even when nothing is written: an authored
    bundle and a running planet drifting apart is invisible otherwise, and neither side
    logs it.
    """
    NUMERIC = {"lat": 0.02, "lon": 0.02, "elev_m": 0.5, "temp_c": 0.05,
               "rain_mm": 0.5, "swampiness": 0.005}
    counts = {}
    examples = {}
    compared = 0
    for row in rows:
        ref = reference.get(row["tile"])
        if ref is None:
            counts["__missing_from_reference"] = counts.get("__missing_from_reference", 0) + 1
            continue
        compared += 1
        for col in BASE_COLUMNS:
            if col == "tile" or col in ("arc", "bearing"):
                continue
            if col in ("water", "river_flow", "region") and prov.get(col) != MEASURED:
                continue           # carried from the reference; comparing is circular
            a, b = ref.get(col, ""), row.get(col, "")
            if col in NUMERIC:
                try:
                    same = abs(float(a) - float(b)) <= NUMERIC[col]
                except (TypeError, ValueError):
                    same = (a == b)
            else:
                same = (a == b)
            if not same:
                counts[col] = counts.get(col, 0) + 1
                examples.setdefault(col, []).append((row["tile"], a, b))
    return compared, counts, examples


def write_bundle(rows, prov, out_stem, source_note, live_info=None):
    path = out_stem + "_tiles.csv"
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    cols = list(BASE_COLUMNS + EXTRA_COLUMNS)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    side = out_stem + "_provenance.json"
    with open(side, "w", encoding="utf-8") as fh:
        json.dump({
            "tool": "vivify_world.py",
            "source": source_note,
            "tiles": len(rows),
            "columns": cols,
            "provenance": prov,
            "world": live_info,
            "note": ("MEASURED = the live game answered this run. CARRIED = copied from "
                     "the reference bundle. DERIVED = computed from measured values. "
                     "UNMEASURED = nothing on the live side offers it yet - for "
                     "temp_min_c/temp_max_c that is the missing JawaBench tool, and the "
                     "column is EMPTY rather than guessed."),
        }, fh, indent=2)
    return path, side


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--from-export", metavar="FILE",
                     help="a CSV already written by jawa/world_tile_export. OFFLINE.")
    src.add_argument("--live", action="store_true",
                     help="harvest through the bridge. ⚠️ The bridge is shared - hold it "
                          "before using this.")
    ap.add_argument("--reference", default="world/ASHKARR_WORLDMAP",
                    help="authored bundle stem to carry columns from and diff against")
    ap.add_argument("--out", default="world/ASHKARR_VIVIFIED",
                    help="output bundle stem")
    ap.add_argument("--diff-only", action="store_true",
                    help="report the drift and write nothing")
    a = ap.parse_args()

    live_info = None
    if a.live:
        print("harvesting the live world through the bridge...")
        export, extended_ok = harvest_live()
        live_info = live_meta()
        print("  world_info_get     -> %s (seed %s, coverage %s)"
              % (live_info.get("name"), live_info.get("seedString"),
                 live_info.get("planetCoverage")))
        source_note = "live bridge harvest of %s (seed %s)" % (
            live_info.get("name"), live_info.get("seedString"))
    else:
        export = read_export(a.from_export)
        source_note = "jawa/world_tile_export file: " + a.from_export
    reference, ref_path = read_reference(a.reference)
    if reference is None:
        print("⚠️  no reference bundle at %s - water, river_flow and region will be "
              "EMPTY, not carried." % ref_path)

    rows, prov = build_rows(export, reference)
    print("MEASURED %d tiles from %s" % (len(rows), a.from_export or source_note))

    if reference:
        compared, counts, examples = diff(rows, reference, prov)
        print("\ncompared %d tiles against %s" % (compared, ref_path))
        if not counts:
            print("  ✅ the live world matches the authored bundle on every compared "
                  "column.")
        for col in sorted(counts, key=lambda c: -counts[col] if False else -counts[c]):
            print("  %-12s differs on %6d / %d tiles" % (col, counts[col], compared))
            for tid, was, now in examples.get(col, [])[:3]:
                print("        tile %-6s authored=%-24s live=%s" % (tid, was, now))

    print("\nprovenance:")
    for c in BASE_COLUMNS + EXTRA_COLUMNS:
        print("  %-14s %s" % (c, prov[c]))

    if a.diff_only:
        print("\n--diff-only: nothing written.")
        return 0

    path, side = write_bundle(rows, prov, a.out, source_note, live_info)
    print("\nwrote %s\n      %s" % (path, side))
    if prov["temp_min_c"] != MEASURED:
        print("⚠️  temp_min_c and temp_max_c are EMPTY. This export came from the "
              "NINE-COLUMN form of the exporter.\n"
              "    The extended companion is BUILT but not deployed - the OS holds the "
              "DLL while the game runs.\n"
              "    Once it deploys, re-export with extended=true and re-run: these "
              "columns fill themselves and the\n"
              "    provenance flips to MEASURED without touching this tool.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
