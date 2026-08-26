"""
Build the deterministic tile-list plan for the Scald's three mutator passes
(THE BOIL, THE NINE MOUTHS, THE BRINE LADDER) from the pre-computed geometry
in scald_geom.json, then write world/_scald/scald_plan.json for
apply_scald_mutators.py to consume.

Analysis-only: reads local files, never touches the bridge. Run under python3
with /mnt/d/... paths (the WSL side) - this is the read-repo-files case, the
opposite of apply_scald_mutators.py which must run under python.exe.

⛔ NO RNG. Every subset choice is a hash of the tile id -
`h(t) = (t * 2654435761) % 100` - so the exact same plan comes out every time
this script runs, and nothing here could ever roll a different Scald. That is
the owner's standing ruling on worldgen-shaped tools: a knob that could
produce a second planet is out of scope even turned once.

Traps hit while building this:
  - The 9 river "mouth" tiles are NOT lake tiles. `scald_geom.json`'s `scald`
    set is the 312 Lake tiles; the mouths sit just outside it on land
    (AB_OcularForest / BiomeCypreJungle). Checking `mouth in scald` for all 9
    returns an empty list - that is correct, not a bug, and it is why RiverDelta
    /Fish_Increased/AnimalLife_Increased are written to land tiles in section (3).
  - VEE_AlluvialFan's gate (max hilliness Flat + coastline) has ZERO eligible
    tiles here: every mouth measures hilliness 4-5 live, and no ring tile
    bordering a mouth measures Flat either. Computed explicitly below so this
    is a measured "there are none", not an assumption.
  - The "fan" lake tiles (adjacent to a mouth) turned out to be a subset of the
    shallow zone (dist 1-2) - confirmed by an overlap check below - which is
    why deep-heart's excluded-tile list comes back empty: nothing that got a
    mouth-fan write was ever going to land in dist 5+ anyway. The exclusion
    logic is still here because it was a hard requirement in the brief, not
    because it changed anything.
"""
import json, csv, collections

ROOT = '/mnt/d/Luke/dev/Rimworld/world/'
OUT_PATH = ROOT + '_scald/scald_plan.json'

geom = json.load(open(ROOT + '_roads/scald_geom.json'))
scald = set(geom['scald'])
dist = {int(k): v for k, v in geom['dist'].items()}
ring = set(geom['ring'])
volc = geom['volc']
nearvolc = set(geom['nearvolc'])
mouths = geom['mouths']

tiles = {}
for r in csv.DictReader(open(ROOT + '_roads/now_tiles.csv')):
    t = int(r['tile'])
    tiles[t] = dict(biome=r['biome'], hill=int(r['hilliness']), river_count=int(r['river_count']))

nb = {}
for r in csv.DictReader(open(ROOT + 'world_neighbors_sub7b.csv')):
    t = int(r['tile'])
    nb[t] = [int(r['n%d' % i]) for i in range(6) if int(r['n%d' % i]) >= 0]

muts_now = {}
for chunk in json.load(open(ROOT + '_roads/_muts_now.json')):
    for row in chunk['tiles']:
        muts_now[row['tile']] = set(m['def'] for m in row['mutators'] if m['def'])


def has_river_mut(t):
    ms = muts_now.get(t, set())
    return 'River' in ms or 'RiverDelta' in ms


h = lambda t: (t * 2654435761) % 100

# ---- (2) THE BOIL ----
volc_biome = {t: tiles[t]['biome'] for t in volc}
pyro = sorted(t for t in volc if volc_biome[t] == 'AB_PyroclasticConflagration')
assert len(pyro) == 3, 'AB_GeothermalHotspots gate: expected exactly the 3 measured pyroclastic rim tiles, got %r' % pyro

steam_tiles = sorted(nearvolc)
sulfuric_boil_candidates = [t for t in steam_tiles if not has_river_mut(t)]
sulfuric_boil = sorted(t for t in sulfuric_boil_candidates if h(t) < 50)

toxicvents = sorted(t for t in volc if h(t) < 50)
smokevents = sorted(t for t in volc if h(t) >= 50)

# ---- (3) THE NINE MOUTHS ----
mouth_set = set(mouths)
fan_tiles = set()
for m in mouths:
    for n in nb.get(m, []):
        if n in scald:
            fan_tiles.add(n)
fan_tiles -= mouth_set
mouths_in_scald = [m for m in mouths if m in scald]  # measured empty - mouths are land

# VEE_AlluvialFan: ring tile adjacent to a mouth, hilliness Flat (1). Measured empty.
alluvial_candidates = set()
for m in mouths:
    for n in nb.get(m, []):
        if n in ring and tiles.get(n, {}).get('hill') == 1:
            alluvial_candidates.add(n)

# ---- (4) THE BRINE LADDER ----
shallow = sorted(t for t in scald if dist.get(t, 0) in (1, 2))
mid = sorted(t for t in scald if dist.get(t, 0) in (3, 4))
deep = sorted(t for t in scald if dist.get(t, 0) >= 5)

mouth_fan_all = set(mouths_in_scald) | fan_tiles
deep_excluded = sorted(t for t in deep if t in mouth_fan_all)
deep_final = sorted(t for t in deep if t not in mouth_fan_all)

deep_no_river = [t for t in deep_final if not has_river_mut(t)]
deep_brine_subset = sorted(t for t in deep_no_river if h(t) < 33)
deep_sulfuric = sorted(t for t in deep_brine_subset if h(t) % 2 == 0)
deep_toxiclake = sorted(t for t in deep_brine_subset if h(t) % 2 == 1)

groups = dict(
    AB_GeothermalHotspots=pyro,
    SteamGeysers_Increased=steam_tiles,
    VEE_SulfuricLake=sorted(set(sulfuric_boil) | set(deep_sulfuric)),
    ToxicLake=deep_toxiclake,
    VEE_ToxicVents=toxicvents,
    VEE_SmokeVents=smokevents,
    RiverDelta=mouths,
    Fish_Increased=sorted(set(mouths) | fan_tiles | set(shallow)),
    AnimalLife_Increased=sorted(set(mouths) | fan_tiles),
    Fish_Decreased=deep_final,
)

if __name__ == '__main__':
    for k, v in groups.items():
        print(k, len(v))
    print('VEE_AlluvialFan candidates (expect 0):', sorted(alluvial_candidates))
    print('deep tiles excluded as mouth-fan (expect 0):', deep_excluded)
    json.dump(dict(groups=groups, meta=dict(
        mid_bare=mid, alluvial_candidates=sorted(alluvial_candidates),
        steam_tiles=steam_tiles, mouths=mouths, fan_tiles=sorted(fan_tiles),
        shallow=shallow, deep_final=deep_final, deep_excluded=deep_excluded,
    )), open(OUT_PATH, 'w'), indent=1)
    print('wrote', OUT_PATH)
