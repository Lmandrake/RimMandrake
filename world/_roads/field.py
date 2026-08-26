"""The comfort field: what a road on Ash'karr wants to walk on.

Owner, 2026-08-25: roads should "follow easier terrain, especially seeking shade
opportunities or near water sources (but not directly on rivers as much as possible,
just crossing them when needed)". He chose all three readings of "shade" on a tidally
locked world: BROKEN GROUND, COOLER GROUND and VEGETATION.

Everything here is measured off the live harvest. No RNG anywhere - the modulation is
the terrain's, per the ruling in references/river-networks.md 5.
"""
import sys, json, csv, collections
sys.path.insert(0, '/mnt/d/Luke/dev/Rimworld/world/_roads')
from rcommon import *

SHADE_LM = {'Cliffs', 'Valley', 'Cavern', 'Hollow', 'Chasm', 'VEE_SerpentineCanyons',
            'VEE_RockRidge', 'Plateau', 'Basin', 'VEE_StoneForest', 'VEE_MeteorCrater'}
WATER_LM = {'Oasis', 'VEE_Cenotes', 'HotSprings', 'DryLake', 'VEE_StagnantRivulet',
            'VEE_AlluvialFan', 'Bay', 'VEE_DryRiver'}
RUIN_LM  = {'Ruins', 'AncientGarrison', 'AncientWarehouse', 'AbandonedColonyTribal',
            'AbandonedColonyOutlander', 'AncientQuarry', 'AncientChemfuelRefinery',
            'TerraformingScar', 'FrozenRuins', 'AncientLaunchSite', 'AncientHeatVent',
            'sw_DeadSarlacc'}
# biomes whose vegetation actually casts shade on this planet
CANOPY = {'BiomeCypreJungle': 1.0, 'AB_FeraliskInfestedJungle': 1.0, 'AB_MycoticJungle': 0.9,
          'BMT_FungalForest': 0.9, 'AB_OcularForest': 0.8, 'ZBiome_DesertOasis': 1.0,
          'AB_MiasmicMangrove': 0.9, 'BMT_CrystalCaverns': 0.6, 'AB_TarPits': 0.2,
          'AridShrubland': 0.45, 'ZBiome_Grasslands': 0.5, 'ZBiome_Badlands': 0.25,
          'AB_RockyCrags': 0.35, 'Desert': 0.05, 'ExtremeDesert': 0.0, 'Wasteland': 0.0,
          'Scarlands': 0.1, 'HorrorWastes': 0.0}

def build():
    tiles, nb, roads, rivers, setts, objs = load()
    arc = {}
    for r in csv.DictReader(open(R + 'base_tiles.csv')):
        arc[int(r['tile'])] = float(r['arc'])
    allow = {}
    for ch in json.load(open(R + '_links_raw.json')):
        for l in ch['tiles']:
            allow[l['tile']] = l['allowRoads']
    lm = collections.defaultdict(list)
    for l in json.load(open(R + '_landmarks.json'))['landmarks']:
        lm[l['tile']].append(l['def'])

    def spread(seed, maxd):
        d = {t: 0 for t in seed}; fr = list(seed)
        for k in range(1, maxd + 1):
            nx = []
            for t in fr:
                for n in nb[t]:
                    if n not in d: d[n] = k; nx.append(n)
            fr = nx
            if not fr: break
        return d

    shade_seed = {t for t, ds in lm.items() if set(ds) & SHADE_LM}
    water_seed = {t for t, ds in lm.items() if set(ds) & WATER_LM}
    water_seed |= {t for t in tiles if tiles[t]['water']}      # lakes, sea
    ruin_seed  = {t for t, ds in lm.items() if set(ds) & RUIN_LM}
    ds_, dw_ = spread(shade_seed, 4), spread(water_seed, 5)

    river_t = set(rivers)
    comfort, parts = {}, {}
    for t, tt in tiles.items():
        # 1. broken ground -- relief you can stand in the lee of
        relief = min(1.0, max(0.0, (tt['hill'] - 1) / 3.0))
        near_shade = max(0.0, 1.0 - ds_.get(t, 9) / 4.0)
        shade = min(1.0, 0.60 * relief + 0.55 * near_shade)
        # 2. cooler ground -- summer max is what kills a caravan
        cool = min(1.0, max(0.0, (48.0 - tt['tmax']) / 55.0))
        # 3. vegetation
        canopy = CANOPY.get(tt['biome'], 0.35)
        # 4. water within reach, but NOT the channel itself
        near_water = max(0.0, 1.0 - dw_.get(t, 9) / 5.0)
        rd = tt['riverDist']
        near_river = 1.0 if 1 <= rd <= 3 else (0.5 if rd == 4 else 0.0)
        water = min(1.0, 0.70 * near_water + 0.45 * near_river)
        c = 0.30 * shade + 0.25 * cool + 0.20 * canopy + 0.25 * water
        comfort[t] = c
        parts[t] = (shade, cool, canopy, water)
    return dict(tiles=tiles, nb=nb, roads=roads, rivers=rivers, setts=setts, objs=objs,
                arc=arc, allow=allow, lm=lm, comfort=comfort, parts=parts,
                river_t=river_t, ruin_seed=ruin_seed, shade_seed=shade_seed,
                water_seed=water_seed, ds=ds_, dw=dw_)

if __name__ == '__main__':
    F = build()
    c = F['comfort']; tiles = F['tiles']; roads = F['roads']
    land = [t for t in tiles if not tiles[t]['water'] and F['allow'][t]]
    v = sorted(c[t] for t in land)
    print("COMFORT over %d roadable land tiles: min %.3f p10 %.3f median %.3f p90 %.3f max %.3f"
          % (len(v), v[0], v[len(v)//10], v[len(v)//2], v[9*len(v)//10], v[-1]))
    print("  on today's roads: mean %.3f   all roadable land: mean %.3f"
          % (sum(c[t] for t in roads)/len(roads), sum(v)/len(v)))
    for nm, reg in [('Anvil','Anvil'),('Glare','Glare'),('Kiln','Kiln'),('Dew Horn','Dew Horn'),
                    ('Scald Spine','Scald Spine'),('Long Sand','Long Sand'),('Fever Wood','Fever Wood')]:
        s = [c[t] for t in land if tiles[t]['region'] == reg]
        if s: print("  %-12s n=%4d mean comfort %.3f" % (nm, len(s), sum(s)/len(s)))
