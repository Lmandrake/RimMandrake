#!/usr/bin/env python3
"""Widen the Contagion (AB_OcularForest) onto every rain-receiving non-green
high on the dayside, per the_contagion.md's Owed-section ruling (owner,
2026-09-06, Badlands sitting) and CONTAGION_BIOME_PLACEMENT_1.

⛔ NOT a generator. One deterministic pass over the fixed tile list already
computed and reviewed in design/Jawa/worldbuilding/contagion_placement_candidates.md
and contagion_tile_candidates.csv (173 tiles: Scald Spine's 38-tile core,
unconditional, plus 135 tiles elsewhere on the dayside at elev>=1200m,
non-green, rain_mm>0). This script reads that CSV's tile column as its input
list; it does not re-derive it.

    python3 src/RimMandrake/Utils/ashkarr_contagion_summits.py
    python3 src/RimMandrake/Utils/ashkarr_contagion_summits.py --apply
"""
from __future__ import annotations
import argparse, collections, csv, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
TILES = os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_tiles.csv')
CANDIDATES = os.path.join(ROOT, 'design', 'Jawa', 'worldbuilding', 'contagion_tile_candidates.csv')

TO = 'AB_OcularForest'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()

    with open(CANDIDATES, encoding='utf-8') as fh:
        cand_ids = {row['tile'] for row in csv.DictReader(fh)}
    print(f"{len(cand_ids)} candidate tiles read from {CANDIDATES}")

    with open(TILES, encoding='utf-8') as fh:
        rd = csv.DictReader(fh)
        rows = list(rd)
        cols = rd.fieldnames

    by_id = {r['tile']: r for r in rows}
    missing = cand_ids - set(by_id)
    if missing:
        print(f"REFUSING: {len(missing)} candidate tile id(s) not found in {TILES}: "
              f"{sorted(missing)[:10]}")
        return 1

    moved = [by_id[t] for t in cand_ids]
    already = [r for r in moved if r['biome'] == TO]
    to_move = [r for r in moved if r['biome'] != TO]
    before = collections.Counter(r['biome'] for r in moved)
    for r in to_move:
        r['biome'] = TO

    print(f"{len(to_move)} tiles repainted -> {TO}  ({len(already)} already were {TO})")
    print("  from biomes: " + ", ".join(f"{b} ({n})" for b, n in before.most_common()))
    print("  regions: " + ", ".join(
        f"{n} ({c})" for n, c in collections.Counter(r['region'] for r in moved).most_common(10)))

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
