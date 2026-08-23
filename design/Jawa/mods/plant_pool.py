#!/usr/bin/env python3
"""Every plant installed, with the fields that decide whether it can live on a given tile.

⚠️ **This is the POOL, not the roster.** `plant_cherrypick_candidates.csv` answers "what can
already appear on Ash'karr" — the intersection of the shipped biome `wildPlants` with the
biomes we placed. That is 192. This file answers "what could we PUT anywhere", which is all
669 plant ThingDefs, and it is the input to authoring a biome's flora rather than inheriting it.

🔑 **`minGrowthTemperature` / `maxGrowthTemperature` are per-plant and they are MECHANICAL.**
A plant below its min simply does not grow, so a roster that ignores them produces bare ground
with no error. They are the hard filter; everything else is taste.

⭐ **`sowTags` tells you what a player normally GROWS.** Owner's ruling 2026-08-23: drawing on
`Plant_Healroot`, `Plant_Tinctoria` and friends to decorate a biome is allowed and wanted.
"""
import csv, json, os, sqlite3, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/"
      "RimWorld by Ludeon Studios/DefDump/defs.sqlite")
OUT = os.path.join(HERE, 'plant_pool.csv')
COLS = ['defName', 'label', 'mod', 'isTree', 'treeCategory', 'purpose', 'growDays',
        'harvestedThingDef', 'minGrowthTemp', 'maxGrowthTemp', 'minOptTemp', 'maxOptTemp',
        'fertilityMin', 'ignoresFertility', 'cavePlant', 'pollution', 'wildOrder',
        'wildClusterRadius', 'sowTags', 'texPath']


def num(v, d=''):
    return v if isinstance(v, (int, float)) else d


def main() -> int:
    if not os.path.exists(DB):
        print(f'UNMEASURED no defs.sqlite at {DB} — run `measure build`')
        return 2
    con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    rows = []
    for (j,) in con.execute("SELECT json FROM defs WHERE def_type='ThingDef'"):
        d = json.loads(j)
        f = d['fields']
        pl = f.get('plant')
        if not pl:
            continue
        g = f.get('graphicData') or {}
        rows.append({
            'defName': d['defName'], 'label': d.get('label') or '',
            'mod': d.get('modName') or '',
            'isTree': str(bool(pl.get('treeCategory') and pl.get('treeCategory') != 'None')),
            'treeCategory': pl.get('treeCategory') or 'None',
            'purpose': pl.get('purpose') or '',
            'growDays': num(pl.get('growDays')),
            'harvestedThingDef': pl.get('harvestedThingDef') or '',
            'minGrowthTemp': num(pl.get('minGrowthTemperature')),
            'maxGrowthTemp': num(pl.get('maxGrowthTemperature')),
            'minOptTemp': num(pl.get('minOptimalGrowthTemperature')),
            'maxOptTemp': num(pl.get('maxOptimalGrowthTemperature')),
            'fertilityMin': num(pl.get('fertilityMin')),
            'ignoresFertility': str(bool(pl.get('completelyIgnoreFertility'))),
            'cavePlant': str(bool(pl.get('cavePlant'))),
            'pollution': pl.get('pollution') or '',
            'wildOrder': num(pl.get('wildOrder')),
            'wildClusterRadius': num(pl.get('wildClusterRadius')),
            'sowTags': '|'.join(pl.get('sowTags') or []) if isinstance(pl.get('sowTags'), list) else '',
            'texPath': (g.get('texPath') or '') if isinstance(g, dict) else '',
        })
    rows.sort(key=lambda r: (r['mod'], r['defName']))
    with open(OUT, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    trees = sum(1 for r in rows if r['isTree'] == 'True')
    cave = sum(1 for r in rows if r['cavePlant'] == 'True')
    sowable = sum(1 for r in rows if r['sowTags'])
    print(f"MEASURED {len(rows)} plant ThingDefs -> {OUT}")
    print(f"  trees {trees} · cave {cave} · player-sowable {sowable}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
