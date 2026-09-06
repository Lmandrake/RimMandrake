"""ashkarr_fix_impassable.py - three tiles say Impassable and their own lore says otherwise.

    python3 src/RimMandrake/Utils/ashkarr_fix_impassable.py            # report only
    python3 src/RimMandrake/Utils/ashkarr_fix_impassable.py --apply    # rewrite hilliness

⛔ NOT A GENERATOR. Three named tiles, one column, no seed and no knobs.

THE DEFECT. `jawa/world_lint` reports `settlementsOnImpassable: 3`. All three are holdings we
authored, and in every case the settlement's own `why` text describes passable ground:

    Oxalate Watch      "the Scald Gate - THE ONE BREACH IN THE SPINE"
    The Trade Socket   "LOW MOUNTAINS with poisonous volcanic spring"
    Vent Nine          "LOW MOUNTAINS with poisonous volcanic spring"

A breach that is impassable is not a breach, and "low mountains" is `Mountainous`, not
`Impassable`. So the terrain disagrees with the lore, and the lore is the authored thing.

⭐ WHY THIS RATHER THAN MOVING THE SETTLEMENTS. `SETTLEMENTS_OFF_IMPASSABLE_1` proposed
moving the three holdings to the nearest valid tile. That would work and it would be wrong:
these are NAMED PLACES sited for a reason - the Scald Gate is the only way into the crater,
and moving it puts the Empire's chokepoint somewhere that chokes nothing. Fixing the terrain
keeps every name where the design put it.

WHAT IT COSTS. `Impassable` on the planet goes 42 -> 39. `TileFinder.IsValidTileForNewSettlement`
refuses `Hilliness.Impassable` outright, so this also makes three tiles legally settleable
that were not - which is the point, since two of them already hold a settlement.
"""
import argparse
import csv
import io
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TILES = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
SETTS = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_settlements.csv")

IMPASSABLE, MOUNTAINOUS = "5", "4"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    with io.open(TILES, encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        cols = list(rd.fieldnames)
        rows = list(rd)
    before = [dict(r) for r in rows]
    by_tile = {int(r["tile"]): r for r in rows}

    with io.open(SETTS, encoding="utf-8") as fh:
        setts = list(csv.DictReader(fh))

    targets = [s for s in setts if by_tile[int(s["tile"])]["hilliness"] == IMPASSABLE]
    print("settlements standing on Impassable: %d" % len(targets))
    for s in targets:
        t = by_tile[int(s["tile"])]
        print("   %-20s tile %-6s %-26s elev %6s   %s"
              % (s["name"], s["tile"], t["biome"], t["elev_m"], s["why"][:52]))
        t["hilliness"] = MOUNTAINOUS

    n_before = sum(1 for r in before if r["hilliness"] == IMPASSABLE)
    n_after = sum(1 for r in rows if r["hilliness"] == IMPASSABLE)
    print("\nImpassable tiles on the planet: %d -> %d" % (n_before, n_after))

    # 🔴 Only `hilliness`, and only on those tiles.
    moved = {int(s["tile"]) for s in targets}
    for i, r in enumerate(rows):
        for c in cols:
            if c == "hilliness" and int(r["tile"]) in moved:
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
    print("⚠️ Now restamp the freeze:  python3 src/RimMandrake/Utils/verify_frozen.py "
          "--restamp world/ASHKARR_WORLDMAP_tiles.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
