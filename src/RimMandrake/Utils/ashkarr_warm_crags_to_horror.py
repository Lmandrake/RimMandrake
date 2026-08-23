#!/usr/bin/env python3
"""The warm end of AB_RockyCrags becomes HorrorWastes.

🔴 **OWNER, 2026-08-23, verbatim:** *"we will use HorrorWastes instead of RockyCrags for
any tile above 0C"*.

⛔ NOT a generator. One deterministic pass over the one map. `--apply` writes; without it
nothing is touched. The rule is a single threshold and there is no parameter to sweep.

WHY IT IS THE RIGHT BIOME, measured off the live dump rather than assumed
------------------------------------------------------------------------
`HorrorWastes` (Horrors (Continued)) describes itself as *"A **dry region**, contorted by
alien fauna and flora to be unrecognizable."* Its `terrainsByFertility` is `Sand` / `Soil` /
`SoilRich`; its one `wildPlants` entry is `Plant_Agave`; `animalDensity` is 3.6.

⇒ **That is a hot dry biome.** It was placed on the deep nightside at a median −49 °C, where
every one of those fields reads wrong — warm sand between near-black `AB_RockyCrags` rock
([29,27,30]) and pale `SeaIce` ([155,164,172]), with a desert succulent on it. On the warm
band it fits without a single def change.

⚠️ **WHAT THIS DOES NOT FIX, and it must be said in the same breath.** The rule moves the
thermal problem, it does not remove it:

    AB_RockyCrags   4155 -> 3816 tiles,  span 101.8 -> 82.0 °C
    HorrorWastes     468 ->  807 tiles,  span  41.0 -> 94.7 °C

Both biomes still span more than 80 °C, because `HorrorWastes` now holds BOTH the warm band
(0.1 … 19.8 °C) and the 468 cold nightside pockets (−74.9 … −33.9 °C). 🔑 **The open question
is what happens to those 468 pockets**, and REP's incoming note on the horror wastes is
expected to answer it.

🔴 **ANSWERED 2026-08-23 by DECIDE, and this script's result is HALF SUPERSEDED.** The 468
pockets keep `HorrorWastes`; the 339 warm tiles this script moved were moved on again, to
`Desert`. The owner's threshold was right about `AB_RockyCrags` and `HorrorWastes` was the
wrong destination — it is bioweapon class (§6c), and its shipped def is warm-authored, so
sending it the warm band made the biome two places 20 °C apart with no tile in the gap.
⇒ **Do not re-run this script.** It would take the warm tiles back off `Desert`. The pass
that stands is `ashkarr_horror_is_one_place.py`. Until then this script deliberately leaves them alone: the owner ruled
on the warm tiles and only on the warm tiles.

    python3 src/RimMandrake/Utils/ashkarr_warm_crags_to_horror.py
    python3 src/RimMandrake/Utils/ashkarr_warm_crags_to_horror.py --apply
"""
from __future__ import annotations
import argparse, collections, csv, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TILES = os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_tiles.csv')

FROM = 'AB_RockyCrags'
TO = 'HorrorWastes'
ABOVE_C = 0.0          # the owner's threshold, verbatim: "any tile above 0C"


def span(vals):
    return (min(vals), max(vals), max(vals) - min(vals)) if vals else (0, 0, 0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()

    with open(TILES, encoding='utf-8') as fh:
        rd = csv.DictReader(fh)
        rows = list(rd)
        cols = rd.fieldnames

    moved = [r for r in rows if r['biome'] == FROM and float(r['temp_c']) > ABOVE_C]
    before = {b: [float(r['temp_c']) for r in rows if r['biome'] == b] for b in (FROM, TO)}
    for r in moved:
        r['biome'] = TO
    after = {b: [float(r['temp_c']) for r in rows if r['biome'] == b] for b in (FROM, TO)}

    print(f"{len(moved)} tiles: {FROM} -> {TO}  (temp > {ABOVE_C:g} °C)")
    print(f"  regions touched: " + ", ".join(
        f"{n} ({c})" for n, c in collections.Counter(r['region'] for r in moved).most_common(6)))
    for b in (FROM, TO):
        lo0, hi0, sp0 = span(before[b])
        lo1, hi1, sp1 = span(after[b])
        flag = "   ⚠️ WIDER" if sp1 > sp0 + 0.05 else ""
        print(f"  {b:16s} {len(before[b]):5d} -> {len(after[b]):5d} tiles · "
              f"span {sp0:.1f} -> {sp1:.1f} °C  ({lo1:.1f} … {hi1:.1f}){flag}")

    if not a.apply:
        print("\n(dry run — pass --apply to write)")
        return 0
    with open(TILES, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {TILES}")
    print("⚠️ Now restamp the freeze:  python3 src/RimMandrake/Utils/verify_frozen.py "
          "--restamp world/ASHKARR_WORLDMAP_tiles.csv")
    return 0


if __name__ == '__main__':
    sys.exit(main())
