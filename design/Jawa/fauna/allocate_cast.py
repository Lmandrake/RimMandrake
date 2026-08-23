#!/usr/bin/env python3
"""Cast all 25 biomes: who lives where, how common, and who needs to be made bigger.

Owner's brief, 2026-08-22:
  "there should be many small, some medium, a few large, and one super-huge rare entity in
   each biome, their appearance should match the biome when possible, ignore existing stats
   like combat heat and diet as we can change that, try to make creatures unique to a biome
   as much as possible and not have ubiquitous creatures"
  "We may need to re-size some of them ... to fill in gaps (need more giant things)"
  "finding things that are WILDLY differently colored is also biologically plausible if they
   can defend themselves with poison or hostility ... So that's just one criteria."

⛔ Deterministic. No RNG. Same inputs -> same cast, so a re-run after a tweak is a diff.
"""
import csv, json, math, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dumppath import animals as animals_path

FA = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(FA)))

# The pyramid, per biome. Sums to 29 - big enough to feel populated, small enough that a
# player learns the cast of a place.
SLOTS = [('tiny', 4), ('small', 8), ('med', 8), ('large', 5), ('huge', 3), ('SUPER', 1)]
# Commonality per band: the pyramid is about VARIETY; this is about how often you meet them.
COMMONALITY = {'tiny': 1.00, 'small': 0.70, 'med': 0.40, 'large': 0.18, 'huge': 0.07,
               'SUPER': 0.012}          # the set piece is genuinely rare
REUSE_PENALTY = 0.75                    # per biome already using this creature
# 🔴 The rare bands are scaled INVERSELY with the biome's animalDensity, against a reference.
# Commonality is RELATIVE, and total spawns scale with density - so a flat 0.012 makes the
# set piece 65x rarer in ExtremeDesert (density 0.1) than in AB_MiasmicMangrove (6.5). It
# would essentially never appear in a sparse biome, which defeats the point of having one.
DENSITY_REF = 1.8                       # AB_RockyCrags: a middling biome
RARE_SCALED = {'SUPER': (0.008, 0.20), 'huge': (0.05, 0.35)}   # (floor, ceiling) after scaling
# 🔴 DIET. A cast that cannot eat is not a cast.
#   - A strict vegetarian in a biome with no plants starves. SeaIce (plantDensity 0) was
#     given 14 herbivores and IceSheet 12.
#   - A cast that is more predator than prey eats itself. ZBiome_DesertOasis reached 1.07
#     carnivores per prey animal.
NO_PLANT_DENSITY = 0.02          # at or below this, treat the biome as having no forage
MAX_CARNIVORE_SHARE = 0.40       # of the whole cast
ANOMALY_BIOMES = {'HorrorWastes', 'AB_GelatinousSuperorganism', 'AB_OcularForest', 'Scarlands'}

def band(b):
    b = float(b or 0)
    return ('tiny' if b < 0.3 else 'small' if b < 0.8 else 'med' if b < 1.6
            else 'large' if b < 3.0 else 'huge' if b < 6.0 else 'SUPER')

def biome_plant_density():
    import json as _j
    from dumppath import defs_dir
    bl = _j.load(open(defs_dir() + '/BiomeDef.json', encoding='utf-8'))
    bl = bl if isinstance(bl, list) else bl.get('defs')
    return {x['defName']: ((x.get('fields') or {}).get('plantDensity'))
            for x in bl if isinstance(x, dict)}

def biome_density():
    import json as _j
    from dumppath import defs_dir
    bl = _j.load(open(defs_dir() + '/BiomeDef.json', encoding='utf-8'))
    bl = bl if isinstance(bl, list) else bl.get('defs')
    return {x['defName']: ((x.get('fields') or {}).get('animalDensity') or 1.0)
            for x in bl if isinstance(x, dict)}

def load():
    A = {x['defName']: x for x in json.load(open(animals_path(), encoding='utf-8'))['animals']}
    W = {r['defName']: r for r in csv.DictReader(open(f'{FA}/wildlife.csv', encoding='utf-8'))}
    fit = collections.defaultdict(dict)
    for r in csv.DictReader(open(f'{FA}/biome_fit.csv', encoding='utf-8')):
        fit[r['biome']][r['defName']] = (float(r['belong']), float(r['standout']))
    tiles = collections.defaultdict(list)
    for r in csv.DictReader(open(f'{ROOT}/world/ASHKARR_WORLDMAP_tiles.csv', encoding='utf-8')):
        if r['biome'] not in ('Ocean', 'Lake'):
            tiles[r['biome']].append(float(r['temp_c']))
    return A, W, fit, tiles

def median(v):
    v = sorted(v); n = len(v)
    return v[n//2] if n % 2 else (v[n//2-1] + v[n//2]) / 2

def pct(v, p):
    v = sorted(v)
    return v[max(0, min(len(v) - 1, int(round(p * (len(v) - 1)))))]

def commonality_for(biome, bnd, DENS):
    c = COMMONALITY[bnd]
    if bnd not in RARE_SCALED:
        return c
    d = float(DENS.get(biome) or DENSITY_REF) or DENSITY_REF
    lo, hi = RARE_SCALED[bnd]
    return round(max(lo, min(hi, c * (DENSITY_REF / d))), 4)

def main():
    A, W, fit, tiles = load()
    DENS = biome_density()
    PDENS = biome_plant_density()
    biomes = sorted(tiles, key=lambda b: -len(tiles[b]))
    used = collections.Counter()
    cast = {}
    promote = []                 # creatures we must enlarge to fill a SUPER slot

    for b in biomes:
        # 🔴 NOT the median. Filtering on the median put cows, geese and ostriches on SeaIce:
        # that biome inherited the -2 C LIQUID-WATER CLAMP, so its median reads -2 while the
        # biome actually spans -60..0. A creature must tolerate the biome's INTERQUARTILE
        # range, not its middle tile, or it dies on most of the ground it was cast onto.
        cold, hot = pct(tiles[b], 0.25), pct(tiles[b], 0.75)
        anomaly_ok = b in ANOMALY_BIOMES
        pool = []
        for dn, w in W.items():
            if w['reason'] == 'anomaly' and not anomaly_ok:  continue
            if w['reason'] not in ('wildlife', 'anomaly'):   continue
            st = (A.get(dn, {}).get('stats') or {})
            lo, hi = st.get('ComfyTemperatureMin'), st.get('ComfyTemperatureMax')
            if lo is None or hi is None or not (lo <= cold and hi >= hot): continue
            if dn not in fit[b]:                              continue
            pool.append(dn)

        pd = PDENS.get(b)
        barren = pd is not None and pd <= NO_PLANT_DENSITY
        def food(dn):
            return str(((A.get(dn, {}).get('race') or {}).get('foodType')))
        if barren:
            # nothing to graze: a strict vegetarian here is a starvation report waiting to
            # happen. Omnivores stay - they can eat the carnivores' leavings.
            pool = [d for d in pool if 'Vegetarian' not in food(d)]
        carn_cap = int(round(sum(n for _, n in SLOTS) * MAX_CARNIVORE_SHARE))
        carn_used = 0

        chosen = []
        for bnd, want in SLOTS:
            here = [d for d in pool if band((A[d].get('race') or {}).get('baseBodySize')) == bnd]
            scored = []
            for d in here:
                belong, standout = fit[b][d]
                defence = float(W[d]['defence'])
                # STANDOUT is licensed by defence (aposematism); otherwise BELONG carries it.
                fitscore = max(belong, standout * defence)
                # a creature nobody has cast yet is worth more than one already placed
                dormant_bonus = 0.10 if W[d]['status'] == 'dormant' else 0.0
                anomaly_bonus = 0.15 if W[d]['reason'] == 'anomaly' else 0.0
                s = fitscore + dormant_bonus + anomaly_bonus - REUSE_PENALTY * used[d]
                scored.append((s, d))
            scored.sort(key=lambda z: (-z[0], z[1]))
            take = [d for _, d in scored[:want]]
            # SUPER slot empty? promote the best 'huge' instead of leaving the biome headless.
            if bnd == 'SUPER' and not take:
                hp = [(max(fit[b][d][0], fit[b][d][1] * float(W[d]['defence'])) - REUSE_PENALTY*used[d], d)
                      for d in pool if band((A[d].get('race') or {}).get('baseBodySize')) == 'huge']
                hp.sort(key=lambda z: (-z[0], z[1]))
                if hp:
                    take = [hp[0][1]]
                    promote.append((b, hp[0][1], (A[hp[0][1]].get('race') or {}).get('baseBodySize')))
            for d in take:
                if 'Carnivore' in food(d):
                    if carn_used >= carn_cap:
                        continue          # cast is already predator-heavy; skip this one
                    carn_used += 1
                used[d] += 1
                chosen.append((d, bnd))
        cast[b] = chosen

    # ---- write the assignment ----
    out = f'{FA}/cast_assignment.csv'
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['biome', 'defName', 'label', 'mod', 'band', 'bodySize', 'commonality',
                    'belong', 'standout', 'defence', 'status', 'reason', 'promoted'])
        promo = {(b, d) for b, d, _ in promote}
        for b in biomes:
            for d, bnd in cast[b]:
                bel, sta = fit[b][d]
                w.writerow([b, d, A[d].get('label'), A[d].get('modName'), bnd,
                            (A[d].get('race') or {}).get('baseBodySize'),
                            commonality_for(b, bnd, DENS), bel, sta, W[d]['defence'],
                            W[d]['status'], W[d]['reason'], int((b, d) in promo)])
    tot = sum(len(v) for v in cast.values())
    print(f"wrote {out}: {tot} (biome, creature) assignments across {len(biomes)} biomes")
    print(f"distinct creatures used: {len(used)} of {sum(1 for r in W.values() if r['reason'] in ('wildlife','anomaly'))} eligible")
    print(f"appear in exactly one biome: {sum(1 for c in used.values() if c==1)}   "
          f"in 2-3: {sum(1 for c in used.values() if 2<=c<=3)}   in 4+: {sum(1 for c in used.values() if c>=4)}")
    print(f"\nbiomes short of a full pyramid:")
    for b in biomes:
        c = collections.Counter(bnd for _, bnd in cast[b])
        miss = [f"{bnd} {c[bnd]}/{want}" for bnd, want in SLOTS if c[bnd] < want]
        if miss: print(f"   {b:30} {', '.join(miss)}")
    print(f"\nSUPER slots filled by PROMOTION ({len(promote)} biomes need a creature enlarged):")
    for b, d, sz in promote:
        print(f"   {b:30} {A[d].get('label') or d:28} bodySize {sz} -> needs >= 6.0")

if __name__ == '__main__':
    main()
