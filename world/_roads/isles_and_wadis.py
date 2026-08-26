"""Plan three things the owner asked for on 2026-08-25/26.

1. `CoastalIsland` + `Archipelago` scattered on the BARREN shores of the Twilight and Grey
   Seas — "caused when the ocean withdrew".
   ⚠️ Both defs carry a HARD coast-side gate (`CoastalIsland` 3-5 water neighbours,
   `Archipelago` 2-5) and both need NO river, so they cannot go out on the dry ground itself.
   The barren SHORELINE is where they are legal, and there is plenty of it.
   ⚠️ Both are `category=coastal`, so adding one DISPLACES another coastal landmark on the
   same tile (Peninsula, Bay, GravelBeach). Only tiles with no landmark at all are used.

2. `VEE_DryRiver` continuing from every river that DIES — owner: *"Add a few tiles with dry
   riverbed in them when a river dies."* The bed walks on downhill from the terminus.
   ⚠️ `VEE_DryRiver` requires **0 coast sides** (landlocked), so the bed stops if it
   reaches the shore — which is correct: a wadi that reaches the sea is a river.

⛔ No RNG. Scatter and length come from a hash of the tile id, so the result is
deterministic and no knob here could roll a second planet.
"""
import sys, json, collections
sys.path.insert(0, '/mnt/d/Luke/dev/Rimworld/world/_roads')
from rcommon import *
from field import build

F = build(); tiles, nb, lm = F['tiles'], F['nb'], F['lm']
riv = collections.defaultdict(dict)
for ch in json.load(open(R + '_final_links.json')):
    for l in ch['tiles']:
        for pr in l['potentialRivers']: riv[l['tile']][pr['neighbor']] = pr['def']
water = {t for t in tiles if tiles[t]['water']}
BARREN = {'AridShrubland','Wasteland','Desert','ExtremeDesert','ZBiome_Badlands',
          'AB_RockyCrags','AB_TarPits','Scarlands','ZBiome_Grasslands','HorrorWastes'}
h = lambda t: (t * 2654435761) % 1000
sides = lambda t: sum(1 for n in nb[t] if n in water)

plan = []          # (tile, def, why)
taken = set()

def spaced(t, chosen, gap):
    return all(gcdeg(tiles, t, c) > gap for c in chosen)

for sea, n_isle, n_arch in (('Twilight Sea', 8, 7), ('Grey Sea', 8, 7)):
    S = {t for t in tiles if tiles[t]['region'] == sea and tiles[t]['water']}
    pool = [t for t in tiles
            if not tiles[t]['water'] and 2 <= sides(t) <= 5
            and any(n in S for n in nb[t]) and not riv.get(t)
            and tiles[t]['biome'] in BARREN and t not in lm and t not in taken]
    chosen = []
    # CoastalIsland wants a deeply embayed tile: 3-5 coast sides, most water first
    for t in sorted([x for x in pool if 3 <= sides(x) <= 5], key=lambda x: (-sides(x), h(x))):
        if len(chosen) >= n_isle: break
        if not spaced(t, chosen, 2.6): continue
        chosen.append(t); taken.add(t)
        plan.append((t, 'CoastalIsland', '%s: a hill left standing when the water drew back' % sea))
    arch = []
    for t in sorted([x for x in pool if x not in taken], key=lambda x: h(x)):
        if len(arch) >= n_arch: break
        if not spaced(t, chosen + arch, 2.6): continue
        arch.append(t); taken.add(t)
        plan.append((t, 'Archipelago', '%s: a drowned ridge broken into a chain' % sea))
    print("%-13s CoastalIsland %d, Archipelago %d  (pool %d)" % (sea, len(chosen), len(arch), len(pool)))

# ---- dry riverbeds where a river dies -----------------------------------
dying = []
for t in riv:
    if len(riv[t]) != 1: continue
    if any(n in water for n in nb[t]): continue
    n = list(riv[t])[0]
    if tiles[t]['elev'] > tiles[n]['elev']: continue
    dying.append(t)
wadis = 0
for t in sorted(dying):
    cur, bed = t, []
    want = 2 + h(t) % 3                      # 2, 3 or 4 tiles
    while len(bed) < want:
        cands = [n for n in nb[cur]
                 if n not in water and n not in riv and n not in bed and n not in taken
                 and n not in lm and sides(n) == 0]     # ⚠️ landlocked is a hard gate
        if not cands: break
        nxt = min(cands, key=lambda x: (tiles[x]['elev'], h(x)))
        if tiles[nxt]['elev'] > tiles[cur]['elev'] + 60: break   # a bed does not climb
        bed.append(nxt); taken.add(nxt); cur = nxt
    for b in bed:
        plan.append((b, 'VEE_DryRiver', 'the bed the %s creek left when it gave out'
                     % tiles[t]['region']))
    if bed: wadis += 1
    print("   wadi from %-6d %-18s %4dm -> %d tiles %s" % (t, tiles[t]['region'], tiles[t]['elev'], len(bed), bed))
print("\n%d dying rivers, %d given a bed; %d placements total" % (len(dying), wadis, len(plan)))
json.dump(plan, open(R + 'isles_plan.json', 'w'))
