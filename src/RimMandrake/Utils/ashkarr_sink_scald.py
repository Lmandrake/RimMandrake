"""ashkarr_sink_scald.py - make the Scald actually be water to the engine.

    python3 src/RimMandrake/Utils/ashkarr_sink_scald.py            # report only
    python3 src/RimMandrake/Utils/ashkarr_sink_scald.py --apply    # rewrite elev_m

⛔ NOT A GENERATOR. 312 named tiles, one column, no seed and no knobs.

THE DEFECT. `RimWorld/Planet/SurfaceTile.cs:28`:

    public override bool WaterCovered => elevation <= 0f;

The Scald's 312 `Lake` tiles are authored at **+1411 m** — a crater lake inside a 2,050 m
rim — so the engine does not count them as water at all. `jawa/world_stats` reads 6.71%
water against the bundle's 8.14%, and the shortfall is exactly those 312 tiles.
`jawa/world_lint` has been saying so as `lakesAboveSeaLevel: 312`.

OWNER'S CALL, 2026-08-21: drop them below sea level. A caldera whose floor is below sea
level inside a high rim is physically ordinary — the Dead Sea is −430 m — and it makes the
Scald behave as the water the design says it is.

🔴 WHAT THIS BUYS, from the call sites of `WaterCovered`:
  * `GenStep_ElevationFertility`, `GenStep_RocksFromGrid`, `GenStep_RockChunks` — a map
    generated on a Scald tile builds as WATER instead of dry land with rock in it
  * `TileMutatorWorker_RiverDelta` / `RiverConfluence` — both pick the neighbour that is NOT
    water-covered, so a delta emptying into the Scald finally behaves as a mouth
  * `WorldDrawLayer_Roads` — roads stop drawing across it
  * `jawa/world_stats` water goes 6.71% → 8.14%, and lint's `lakesAboveSeaLevel` → 0

⚠️ WHAT IT COSTS, and it is why this is its own script and not a one-liner. `elev_m` is not
inert: the relief renderer shades from it, and the Scald sits inside the Spine, which is the
highest ground on the planet. Dropping the floor deepens the contrast at the rim.
🔑 **So this is judged by LOOKING, not by the statistic it fixes.** Re-render afterwards and
compare the Scald against `world/view/ASHKARR_WORLDMAP.biome.equirect.png`.

⛔ It does NOT touch the rim, the Spine, or any land tile — only tiles whose biome is `Lake`.
"""
import argparse
import csv
import io
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TILES = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")

# The Ocean floor is authored at -30. Matching it keeps one convention for "under water"
# rather than inventing a second depth nobody chose.
NEW_ELEV = "-30"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    with io.open(TILES, encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        cols = list(rd.fieldnames)
        rows = list(rd)
    before = [dict(r) for r in rows]

    lake = [r for r in rows if r["biome"] == "Lake"]
    ocean = [r for r in rows if r["biome"] == "Ocean"]
    print("Lake tiles:  %d, elevation %s" % (len(lake), sorted({r["elev_m"] for r in lake})))
    print("Ocean tiles: %d, elevation %s  <- the convention being matched"
          % (len(ocean), sorted({r["elev_m"] for r in ocean})))

    moved = 0
    for r in lake:
        if r["elev_m"] != NEW_ELEV:
            r["elev_m"] = NEW_ELEV
            moved += 1
    print("\nmoved %d Lake tile(s) to %s m" % (moved, NEW_ELEV))

    now_water = sum(1 for r in rows if float(r["elev_m"]) <= 0)
    print("tiles the engine will now call WaterCovered: %d of %d = %.2f%%"
          % (now_water, len(rows), 100.0 * now_water / len(rows)))

    # 🔴 Only `elev_m`, and only on Lake tiles.
    for i, r in enumerate(rows):
        for c in cols:
            if c == "elev_m" and r["biome"] == "Lake":
                continue
            if r[c] != before[i][c]:
                sys.exit("🔴 %s changed on tile %s - refusing to write" % (c, r["tile"]))
    print("verified: nothing else moved, across all %d rows" % len(rows))

    if not a.apply:
        print("\nreport only. Pass --apply to write.")
        return 0
    with io.open(TILES, "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        wr.writerows(rows)
    print("\nwrote %s" % TILES)
    print("⚠️ NOW LOOK AT IT. Re-render and judge the Scald's relief; the statistic is not "
          "the criterion.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
