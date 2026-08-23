#!/usr/bin/env python3
"""Build the plant cherrypick candidate list — from BOTH routes a plant reaches a map.

🔴 **THERE WAS NO BUILDER.** `PLANT_CHERRYPICK_PASS_1` says *"the BUILDER is still wrong;
only its output was patched"*, and `PLANT_LIST_MISSES_MUTATOR_ROUTE_1` describes what to fix
in it. Measured 2026-08-23: `plant_cherrypick_candidates.csv` was produced ad hoc when the
item was filed (`43e2913f`) and **no script that writes it exists anywhere in the repo.** The
CSV was an orphan, hand-patched twice. This is the builder.

TWO ROUTES, AND READING ONLY THE FIRST IS THE DEFECT
----------------------------------------------------
  1. `BiomeDef.wildPlants[].plant`          — what the biome grows
  2. `TileMutatorDef.additionalWildPlants[].plant` and `TileMutatorDef.plantKinds[]`
                                            — what a MUTATOR adds, irrespective of biome

⚠️ Route 2 is invisible to a biome-only scan and it is not hypothetical: `VEE_RedDesertPlants`
puts `VEE_Plant_ChollaCactus` and `VEE_Plant_HoodiaCactus` on 8 tiles and **neither appears in
any biome's `wildPlants`**. They had to be appended by hand. 🔑 The five plants `Oasis` adds
were already in the list **by coincidence** — they also grow in `ZBiome_DesertOasis` — and
that coincidence is why the gap went unnoticed.

ROUTES CHECKED AND CLEAR — do not re-investigate (from PLANT_LIST_MISSES_MUTATOR_ROUTE_1)
  * No `BiomeVariantDef` on this planet touches plants.
  * No `extraGenSteps` on any planet mutator places flora.
  * Landmarks resolve to the same mutator set.
  * `src/Jawa/` patches touch `terrainPatchMakers`, never `wildPlants`.
  * `wildTerrainTags`, `terrainBlacklist`, `wildPlantUseDistanceToShore` only RESTRICT
    placement of plants already listed — they never add one.
  * `plantDensityFactor` shifts AMOUNT, not roster.

⚠️ **The dump nests plant fields under `fields`, not at the top level.** Reading
`thingDef['plant']['growDays']` returns null for EVERY plant, vanilla Saguaro included, and
looks like missing data. It is `thingDef['fields']['plant']['growDays']`.

    python3 design/Jawa/mods/gen_plant_candidates.py
    python3 design/Jawa/mods/gen_plant_candidates.py --out <path> --compare <old.csv>
"""
from __future__ import annotations
import argparse, collections, csv, glob, json, os, sqlite3, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TILES = os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_tiles.csv')
MUTS = os.path.join(ROOT, 'world', 'ASHKARR_WORLDMAP_mutators.csv')
OUT = os.path.join(HERE, 'plant_cherrypick_candidates.csv')
DB = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
      "RimWorld by Ludeon Studios/DefDump/defs.sqlite")

COLS = ['defName', 'label', 'mod', 'packageId', 'isTree', 'treeCategory', 'growDays',
        'harvestedThingDef', 'tilesReachable', 'biomes', 'mutators', 'routes']


def world():
    """(tile -> biome, tile -> [mutator])"""
    biome, mut = {}, collections.defaultdict(list)
    for r in csv.DictReader(open(TILES, encoding='utf-8')):
        if r.get('biome'):
            biome[r['tile']] = r['biome']
    for r in csv.DictReader(open(MUTS, encoding='utf-8')):
        for m in (r['mutators'] or '').split(';'):
            if m:
                mut[r['tile']].append(m)
    return biome, mut


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--compare', help='an older CSV; report what this build adds or drops')
    a = ap.parse_args()
    if not os.path.exists(DB):
        print(f'UNMEASURED no defs.sqlite at {DB} — run `measure build`')
        return 2

    con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    biome_of, muts_of = world()
    live_biomes = set(biome_of.values())
    live_muts = {m for ms in muts_of.values() for m in ms}

    # ---- route 1: biome wildPlants, for the biomes that exist on THIS planet
    plants_of_biome = collections.defaultdict(set)
    for (j,) in con.execute("SELECT json FROM defs WHERE def_type='BiomeDef'"):
        d = json.loads(j)
        if d['defName'] not in live_biomes:
            continue
        for wp in (d['fields'].get('wildPlants') or []):
            if isinstance(wp, dict) and wp.get('plant'):
                plants_of_biome[d['defName']].add(wp['plant'])

    # ---- route 2: mutator additionalWildPlants + plantKinds, for the mutators in use
    plants_of_mut = collections.defaultdict(set)
    for (j,) in con.execute("SELECT json FROM defs WHERE def_type='TileMutatorDef'"):
        d = json.loads(j)
        if d['defName'] not in live_muts:
            continue
        f = d['fields']
        for wp in (f.get('additionalWildPlants') or []):
            if isinstance(wp, dict) and wp.get('plant'):
                plants_of_mut[d['defName']].add(wp['plant'])
        for p in (f.get('plantKinds') or []):
            if isinstance(p, str):
                plants_of_mut[d['defName']].add(p)

    # ---- attribute tiles. 🔑 A tile counts ONCE per plant however many routes reach it.
    reach = collections.defaultdict(set)          # plant -> {tile}
    by_biome = collections.defaultdict(set)       # plant -> {biome}
    by_mut = collections.defaultdict(set)         # plant -> {mutator}
    for tile, b in biome_of.items():
        for p in plants_of_biome.get(b, ()):
            reach[p].add(tile)
            by_biome[p].add(b)
        for m in muts_of.get(tile, ()):
            for p in plants_of_mut.get(m, ()):
                reach[p].add(tile)
                by_mut[p].add(m)

    # ---- the plant defs themselves
    rows = []
    for (j,) in con.execute("SELECT json FROM defs WHERE def_type='ThingDef'"):
        d = json.loads(j)
        n = d['defName']
        if n not in reach:
            continue
        f = d['fields']
        pl = f.get('plant') or {}            # ⚠️ nested under `fields`, never at the top
        rows.append({
            'defName': n, 'label': d.get('label') or '',
            'mod': d.get('modName') or '', 'packageId': d.get('packageId') or '',
            'isTree': str(bool(pl.get('treeCategory') and pl.get('treeCategory') != 'None')),
            'treeCategory': pl.get('treeCategory') or 'None',
            'growDays': pl.get('growDays') if pl.get('growDays') is not None else '',
            'harvestedThingDef': pl.get('harvestedThingDef') or '',
            'tilesReachable': len(reach[n]),
            'biomes': '|'.join(sorted(by_biome[n])),
            'mutators': '|'.join(sorted(by_mut[n])),
            'routes': '+'.join([r for r, ok in (('biome', by_biome[n]), ('mutator', by_mut[n])) if ok]),
        })
    rows.sort(key=lambda r: -r['tilesReachable'])

    missing = sorted(set(reach) - {r['defName'] for r in rows})
    with open(a.out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)

    only_mut = [r for r in rows if r['routes'] == 'mutator']
    print(f"MEASURED {len(rows)} reachable plants over {len(live_biomes)} biomes and "
          f"{len(live_muts)} mutators -> {a.out}")
    print(f"  by biome only: {sum(1 for r in rows if r['routes']=='biome')} · "
          f"both: {sum(1 for r in rows if r['routes']=='biome+mutator')} · "
          f"🔴 MUTATOR ONLY (invisible to the old builder): {len(only_mut)}")
    for r in only_mut:
        print(f"     {r['defName']:28s} {r['tilesReachable']:5d} tiles via {r['mutators']}")
    if missing:
        print(f"  ⚠️ {len(missing)} plant(s) named by a biome or mutator have NO ThingDef in "
              f"the dump — UNMEASURED, not absent: {missing[:6]}")

    if a.compare and os.path.exists(a.compare):
        old = {r['defName']: r for r in csv.DictReader(open(a.compare, encoding='utf-8'))}
        new = {r['defName']: r for r in rows}
        add, drop = sorted(set(new) - set(old)), sorted(set(old) - set(new))
        print(f"\n  vs {a.compare}: +{len(add)} / -{len(drop)}")
        for n in add:
            print(f"     + {n:28s} routes={new[n]['routes']} {new[n]['mutators'] or new[n]['biomes'][:40]}")
        for n in drop:
            print(f"     - {n:28s} was {old[n]['tilesReachable']} tiles")
        if drop:
            print("     🔴 A DROP IS NOT AUTOMATICALLY A BUG — the world changed on 2026-08-23 "
                  "and a biome that lost tiles takes its exclusive plants with it. Check each.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
