#!/usr/bin/env python3
"""Give the boiling ocean and the two brine seas their own BiomeDefs, per
LIQUID_BIOMES_MAP_1_RECONCILIATION.md.

⛔ NOT a generator. Three deterministic region+biome selectors, each
region's own vanilla placeholder biome swapped for the def authored to
replace it:

    region "Scald"         , biome Lake  -> RUT_TheScald     (312 tiles)
    region "Twilight Sea"   , biome Ocean -> RUT_TwilightSea  (442 tiles)
    region "Grey Sea"       , biome Ocean -> RUT_GreySea      (381 tiles)

The propane lake (RUT_PropaneLake) is deliberately NOT painted here -- its
exact tile subset within Umbra's 802 land tiles is still owner-gated (no
water=1 tile exists there yet to select from), per the reconciliation
doc's own §4.

    python3 src/RimMandrake/Utils/ashkarr_three_seas.py
    python3 src/RimMandrake/Utils/ashkarr_three_seas.py --apply
"""
from __future__ import annotations
import argparse, csv, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TILES = os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_tiles.csv')

SELECTORS = [
    ('Scald', 'Lake', 'RUT_TheScald'),
    ('Twilight Sea', 'Ocean', 'RUT_TwilightSea'),
    ('Grey Sea', 'Ocean', 'RUT_GreySea'),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()

    with open(TILES, encoding='utf-8') as fh:
        rd = csv.DictReader(fh)
        rows = list(rd)
        cols = rd.fieldnames

    total = 0
    for region, from_biome, to_biome in SELECTORS:
        moved = [r for r in rows if r['region'] == region and r['biome'] == from_biome]
        print(f"{region!r}: {len(moved)} tiles {from_biome} -> {to_biome}")
        for r in moved:
            r['biome'] = to_biome
        total += len(moved)

    print(f"\n{total} tiles total repainted")

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
