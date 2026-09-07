#!/usr/bin/env python3
"""Dissolve HorrorWastes into a five-lobe mosaic, per the_blue_desert.md §0's
anti-bullseye ruling (owner, 2026-09-06) and HORRORWASTES_BIOME_DISSOLVE_1 /
NIGHTSIDE_ICE_DEF_1.

⛔ NOT a generator. One deterministic pass, reading the fixed assignment map
already computed in design/Jawa/worldbuilding/horrorwastes_dissolve_mosaic.json
(2,338 tiles: 1,711 former HorrorWastes ring + 578 BMT_CrystalCaverns + 49
vanilla IceSheet). It does not re-derive that map.

Rule (the_blue_desert.md §0's table, cross-validated against nightside_ice.md
§0's own tile counts before trusting it — ring sectors 1-3 = 337 matches
exactly, caverns elev>=900 = 416 matches exactly, total ice = 802 matches
exactly):
  - Ring (former HorrorWastes) tiles, by 30-degree bearing sector (bearing//30):
      sectors 0,7,9,10,11  -> BiomeGRimond (Blue Desert core)
      sectors 1,2,3        -> RUT_NightsideIce (the ring's own highland)
      sectors 4,5,8        -> BiomeGRimond (the elevation split in this band
                               is CrystalCaverns-only, see below -- ring tiles
                               here are NOT re-split by elevation; verified
                               against nightside_ice.md's own 802 total, which
                               has no room for a ring-4/5/8 contribution)
      sector 6              -> AB_PropaneLakes (the propane bulge)
  - BMT_CrystalCaverns tiles (no longer a worldmap biome, the_lantern_deeps.md):
      elev_m >= 900  -> RUT_NightsideIce
      elev_m < 900   -> BiomeGRimond
  - Vanilla IceSheet's 49 tiles repaint too -> RUT_NightsideIce (NIGHTSIDE_ICE_DEF_1)

NOT included here, flagged and deferred: the_blue_desert.md's "arc excursion"
refinement (Blue Desert lobes in sectors 0/11 push further into arc 143-155;
the propane bulge in sector 6 pushes toward lower arc) -- no measurable tile
population was pinned down for this pass; it pulls in tiles OUTSIDE the three
source populations above and needs its own derivation before painting.

    python3 src/RimMandrake/Utils/ashkarr_horrorwastes_dissolve.py
    python3 src/RimMandrake/Utils/ashkarr_horrorwastes_dissolve.py --apply
"""
from __future__ import annotations
import argparse, collections, csv, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TILES = os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_tiles.csv')
MOSAIC = os.path.join(ROOT, 'design', 'Jawa', 'worldbuilding', 'horrorwastes_dissolve_mosaic.json')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()

    with open(MOSAIC, encoding='utf-8') as fh:
        assign = json.load(fh)
    print(f"{len(assign)} tile assignments read from {MOSAIC}")

    with open(TILES, encoding='utf-8') as fh:
        rd = csv.DictReader(fh)
        rows = list(rd)
        cols = rd.fieldnames

    by_id = {r['tile']: r for r in rows}
    missing = set(assign) - set(by_id)
    if missing:
        print(f"REFUSING: {len(missing)} tile id(s) in the mosaic not found in {TILES}: "
              f"{sorted(missing)[:10]}")
        return 1

    before = collections.Counter(by_id[t]['biome'] for t in assign)
    moved = 0
    for tile, biome in assign.items():
        r = by_id[tile]
        if r['biome'] != biome:
            r['biome'] = biome
            moved += 1

    print(f"{moved} tiles repainted ({len(assign) - moved} already matched their target)")
    print("  before: " + ", ".join(f"{b} ({n})" for b, n in before.most_common()))
    after = collections.Counter(assign.values())
    print("  after:  " + ", ".join(f"{b} ({n})" for b, n in after.most_common()))

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
