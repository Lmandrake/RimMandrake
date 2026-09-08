#!/usr/bin/env python3
"""
ashkarr_rebase_from_save.py — rebuild the canonical tiles CSV from the SAVEGAME.

🔴 WHY THIS EXISTS (owner, 2026-09-07).

Ash'karr had TWO divergent lineages and nobody noticed for two weeks:

  A. THE WORLD ITSELF — a savegame, built over many sessions by scripts AND by
     hand: bridge edits, debug-menu edits, and the owner's own decisions made
     while looking at the globe. `WORLDMAP_V1_original_e.rws` is the last state
     the owner inspected and approved.

  B. `world/ASHKARR_WORLDMAP_*.csv` — seeded by `ashkarr_paint.py` and then
     surgically edited for weeks. It was treated as the authoring source and
     imported into the game repeatedly.

They were never the same planet. Measured 2026-09-07 against V1_original_e:

    biome      differs on 5,411 tiles
    hilliness  differs on 7,275 tiles   <- a THIRD of the planet, both directions
    elevation  differs on   787 tiles
    ROADS      the links CSV shares only 77 of the save's 1,399 road edges

The hilliness divergence was never anyone's decision. The CSV's hilliness has
been frozen at its current values since 2026-08-23 (609d2ea5) and the world's was
different; the 2026-09-07 worldmap redo imported the CSV wholesale and flattened
the planet — `Impassable` 355 -> 56, `Mountainous` 2,428 -> 1,495 — then verified
itself with `world_tile_validate` and reported "21,872/21,872, 0 mismatches".

⛔ THAT VERIFICATION WAS TRUE AND MEANINGLESS. A 100% match against the artifact
you just imported only proves the import worked. It cannot tell you the import was
WANTED. Any future validate of live-against-CSV must say which direction it is
evidence for.

✅ THE RULING (owner, 2026-09-07): lineage B is deprecated. The SAVEGAME is the
world. This script exports it back into the canonical CSV so that, from now on,
the CSV is a RECORD of the planet rather than a rival to it.

WHAT IT DOES

  engine truth   biome · elev_m · temp_c · rain_mm · hilliness · swampiness
                 taken from a `jawa/world_tile_export` of the save. These are the
                 only fields RimWorld actually has.
  geometry       lat · lon copied from the export; arc recomputed from them about
                 the substellar point (0,0) — verified to 0.005 deg against the
                 old column; bearing carried across, being pure geometry on an
                 identical grid (max lat/lon delta measured 0.000000).
  derived        water = (elev_m <= 0), which is the engine's own water test. The
                 old hand-maintained `water` column disagreed with elevation on
                 153 tiles and is not reproduced.
  inherited      river_flow · region are NOT in the engine export and are carried
                 from the previous CSV. region was calibrated against the save's
                 own live WorldFeatures: 69 of 71 names match tile-for-tile
                 (Ashfall Range 324 live vs 346, Notch 56 vs 68).

USAGE
    python3 src/RimMandrake/Utils/ashkarr_rebase_from_save.py            # plan
    python3 src/RimMandrake/Utils/ashkarr_rebase_from_save.py --apply    # write

The export is produced live: load the save, then
`jawa/world_tile_export --path <EXPORT>`. This script does not drive the bridge.
"""
import argparse
import csv
import io
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

CANON = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
EXPORT = os.path.join(REPO, "Transient", "base_e", "tiles.csv")

COLS = ["tile", "lat", "lon", "arc", "bearing", "elev_m", "temp_c", "rain_mm",
        "biome", "water", "river_flow", "region", "hilliness", "swampiness"]

HILL = {"Undefined": "0", "Flat": "1", "SmallHills": "2", "LargeHills": "3",
        "Mountainous": "4", "Impassable": "5"}


def arc_of(lat_deg, lon_deg):
    """Angular distance from the substellar point at (0, 0), in degrees."""
    la, lo = math.radians(lat_deg), math.radians(lon_deg)
    return math.degrees(math.acos(max(-1.0, min(1.0, math.cos(la) * math.cos(lo)))))


def rebase_links(links_json, canon_links, apply):
    """Rewrite the links CSV from a `jawa/world_links_get` dump of the save.

    Rivers are emitted MOUTH FIRST (a = the lower `riverDist` end), because
    `WorldGrid.OverlayRiver` maintains `riverDist = max(d, other.d + 1)` and a
    max() can never be corrected downward on re-import.
    """
    import json
    rows = json.load(open(links_json))
    dist = {r["tile"]: r.get("riverDist", 0) for r in rows}
    roads, rivers = {}, {}
    for r in rows:
        t = r["tile"]
        for pr in (r.get("potentialRoads") or []):
            n = pr.get("neighbor")
            if n is not None:
                roads[(min(t, n), max(t, n))] = pr.get("def")
        for pv in (r.get("potentialRivers") or []):
            n = pv.get("neighbor")
            if n is not None:
                rivers[(min(t, n), max(t, n))] = pv.get("def")

    out = [["kind", "a", "b", "def"]]
    for (x, y), d in sorted(rivers.items()):
        a_, b_ = (x, y) if dist.get(x, 0) <= dist.get(y, 0) else (y, x)
        out.append(["river", a_, b_, d])
    for (x, y), d in sorted(roads.items()):
        out.append(["road", x, y, d])

    old_counts = {"river": 0, "road": 0}
    if os.path.exists(canon_links):
        for r in csv.DictReader(open(canon_links)):
            if r.get("kind") in old_counts:
                old_counts[r["kind"]] += 1

    print("\nLINKS REBASE — canonical links CSV <- savegame")
    print("  rivers: %5d  (was %d)" % (len(rivers), old_counts["river"]))
    print("  roads:  %5d  (was %d)" % (len(roads), old_counts["road"]))
    byd = {}
    for d in roads.values():
        byd[d] = byd.get(d, 0) + 1
    print("  road classes: %s" % byd)
    if not apply:
        print("  PLAN ONLY.")
        return
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows(out)
    open(canon_links, "w", newline="").write(buf.getvalue())
    print("  wrote %s" % canon_links)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", default=EXPORT, help="jawa/world_tile_export CSV of the save")
    ap.add_argument("--canon", default=CANON, help="canonical CSV to rewrite")
    ap.add_argument("--links-json", default=os.path.join(REPO, "Transient", "base_e", "links.json"),
                    help="jawa/world_links_get dump of the save")
    ap.add_argument("--canon-links", default=os.path.join(REPO, "world", "ASHKARR_WORLDMAP_links.csv"))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    old = {r["tile"]: r for r in csv.DictReader(open(a.canon))}
    exp = {r["tile"]: r for r in csv.DictReader(open(a.export))}

    if set(old) != set(exp):
        print("REFUSED: tile id sets differ (%d vs %d). Wrong export or wrong planet."
              % (len(old), len(exp)))
        return 1

    dlat = max(abs(float(old[t]["lat"]) - float(exp[t]["lat"])) for t in old)
    dlon = max(abs(float(old[t]["lon"]) - float(exp[t]["long"])) for t in old)
    if dlat > 0.001 or dlon > 0.001:
        print("REFUSED: not the same grid (max lat delta %.6f, lon %.6f)." % (dlat, dlon))
        return 1

    rows, changed = [], {c: 0 for c in COLS}
    for t in sorted(old, key=int):
        o, e = old[t], exp[t]
        lat, lon = float(e["lat"]), float(e["long"])
        elev = int(round(float(e["elevation"])))
        hil = HILL.get(e["hilliness"].strip())
        if hil is None:
            print("REFUSED: unknown hilliness %r on tile %s" % (e["hilliness"], t))
            return 1
        new = {
            "tile": t,
            "lat": "%.4f" % lat,
            "lon": "%.4f" % lon,
            "arc": "%.2f" % arc_of(lat, lon),
            "bearing": o["bearing"],                       # geometry, identical grid
            "elev_m": str(elev),
            "temp_c": "%.1f" % float(e["temperature"]),
            "rain_mm": str(int(round(float(e["rainfall"])))),
            "biome": e["biome"],
            "water": "1" if elev <= 0 else "0",            # the engine's own test
            "river_flow": o["river_flow"],                 # inherited, not in engine
            "region": o["region"],                         # inherited, calibrated 69/71
            "hilliness": hil,
            "swampiness": "%.2f" % float(e["swampiness"]),
        }
        for c in COLS:
            a_, b_ = str(o.get(c, "")).strip(), str(new[c]).strip()
            try:
                same = abs(float(a_) - float(b_)) < 0.005
            except ValueError:
                same = a_ == b_
            if not same:
                changed[c] += 1
        rows.append(new)

    print("REBASE PLAN — canonical CSV <- savegame export")
    print("  tiles: %d" % len(rows))
    for c in COLS:
        if changed[c]:
            print("     %-11s %6d tiles change" % (c, changed[c]))
    print("  (unlisted columns are unchanged)")

    if a.apply:
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
        open(a.canon, "w", newline="").write(buf.getvalue())
        print("\nwrote %s" % a.canon)

    if os.path.exists(a.links_json):
        rebase_links(a.links_json, a.canon_links, a.apply)

    if not a.apply:
        print("\nPLAN ONLY. Re-run with --apply to write.")
        return 0
    print("\nNOW RUN: python3 src/RimMandrake/Utils/verify_frozen.py --restamp")
    return 0


if __name__ == "__main__":
    sys.exit(main())
