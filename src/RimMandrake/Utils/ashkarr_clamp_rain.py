"""ashkarr_clamp_rain.py - dry the desert and the lava back down. Nothing else.

    python3 src/RimMandrake/Utils/ashkarr_clamp_rain.py            # report only
    python3 src/RimMandrake/Utils/ashkarr_clamp_rain.py --apply    # rewrite rain_mm

⛔ NOT A MODEL, AND IT MUST NEVER PRETEND TO BE ONE. The physically correct fix is to gate
the Scald plume inside `ashkarr_paint.py` and re-run it - but rainfall is not a leaf
column there: `rain_src` feeds `flow()` -> `acc` -> where the rivers ARE -> riparian ->
biome. Gating it re-rolls the hydrology, moves rivers and biomes, and makes the ortho
globes the owner accepted on 2026-08-20 describe a planet that no longer exists.
`ashkarr_regate_rain.py` tried the faithful reconstruction and REFUSED itself at 67.8%
exact, because `lift` is computed from PRE-erosion elevation and the bundle only stores
the post-erosion value. That input is gone.

So this is the owner's call of 2026-08-21, taken with the trade named out loud: clamp the
number where it reads absurd, leave every other column untouched, and accept that
rainfall now describes the GROUND rather than the hydrology that carved it.

THE DEFECT. `ashkarr_paint.py:481` adds `2.6 * scald_plume` UNGATED - it is the one term
not multiplied by `dayside` - and the plume peaks at 1.0, which is exactly the saturation
point of `:902`'s transform. So every tile within ~15 degrees of the Scald pins at 1668 mm
whatever it is made of. 596 tiles sit there: 271 are the jungle corridor the plume exists
to create and are LEFT ALONE, and the rest include the entire volcanic province.

WHAT IT TOUCHES: `rain_mm`, on ceiling tiles whose biome is arid or volcanic. Nothing else,
and it asserts that.
"""
import argparse
import collections
import csv
import io
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
TILES = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
CEILING = 1668

# ⚠️ The wet-by-design biomes are ABSENT on purpose. The jungle corridor, the oases, the
# grassland fringe and the mangrove are supposed to be the wet places on this planet -
# that is the whole point of the Scald pumping water - so clamping them would delete the
# design along with the defect.
ARID = {
    "ExtremeDesert", "Desert", "AridShrubland", "ZBiome_Badlands", "Wasteland",
    "AB_RockyCrags", "Scarlands", "AB_TarPits", "AB_PropaneLakes",
    "Volcano", "LavaField", "AB_PyroclasticConflagration",
}

PCT = 90   # cap at this percentile of the biome's OWN non-ceiling tiles


def pctile(vals, p):
    if not vals:
        return None
    v = sorted(vals)
    return v[min(len(v) - 1, int(round((p / 100.0) * (len(v) - 1))))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    with io.open(TILES, encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        cols = list(rd.fieldnames)
        rows = list(rd)
    before = [dict(r) for r in rows]

    # Each arid biome's own 90th percentile, computed from its tiles that are NOT pinned.
    pool = collections.defaultdict(list)
    for r in rows:
        v = int(r["rain_mm"])
        if r["biome"] in ARID and v < CEILING:
            pool[r["biome"]].append(v)
    caps = {b: pctile(v, PCT) for b, v in pool.items()}

    # ⚠️ The whole volcanic province is PINNED - every Volcano, LavaField and
    # Pyroclastic tile sits at the ceiling - so those biomes have no unpinned sample of
    # their own to derive a cap from. Falling back to the arid family's pooled figure is
    # what stops the three biomes that read most absurdly from being the three this pass
    # silently skips.
    pooled = pctile([v for b, vs in pool.items() for v in vs], PCT)
    for b in ARID:
        if caps.get(b) is None:
            caps[b] = pooled

    # 🔑 ONLY tiles AT the ceiling. The defect is the saturation, not the gradient, and a
    # percentile cap applied to every tile above it would move 1,506 tiles instead of the
    # 231 that are actually pinned - far wider than the targeted clamp that was agreed.
    moved = collections.Counter()
    for r in rows:
        b = r["biome"]
        if b not in ARID or int(r["rain_mm"]) != CEILING:
            continue
        r["rain_mm"] = str(int(caps[b]))
        moved[b] += 1

    print("cap = each arid biome's own %dth percentile among its UNPINNED tiles" % PCT)
    print("%-30s %6s %6s %6s" % ("biome", "cap", "moved", "of"))
    for b in sorted(ARID):
        n = sum(1 for r in before if r["biome"] == b)
        if n:
            print("%-30s %6s %6d %6d" % (b, caps.get(b), moved.get(b, 0), n))
    print("\ntiles changed: %d" % sum(moved.values()))
    ceil_before = sum(1 for r in before if int(r["rain_mm"]) == CEILING)
    ceil_after = sum(1 for r in rows if int(r["rain_mm"]) == CEILING)
    print("at the %d ceiling: %d -> %d" % (CEILING, ceil_before, ceil_after))
    still = collections.Counter(r["biome"] for r in rows if int(r["rain_mm"]) == CEILING)
    print("still pinned (by design): %s" % dict(still.most_common()))

    # 🔴 Every other column must be byte-identical. The accepted map is only still the
    # accepted map if this is true, so it is asserted rather than hoped for.
    other = [c for c in cols if c != "rain_mm"]
    for i, r in enumerate(rows):
        for c in other:
            if r[c] != before[i][c]:
                sys.exit("🔴 column %s changed on tile %s - refusing to write" % (c, r["tile"]))
    print("verified: all %d other columns byte-identical across all %d rows"
          % (len(other), len(rows)))

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
