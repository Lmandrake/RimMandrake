#!/usr/bin/env python3
"""Break the rectangular Poison Forest block into a meandering, interlocking terminator
grove (owner, 2026-09-08, from screenshot). Adjacency-based border meander: PF and its
warm neighbours (Desert/Wasteland/Badlands/AridShrubland/RockyCrags) finger into each
other via a deterministic lon+lat field. 'Maybe some crag could help' -> crag is an
allowed interlock partner, so crag tongues into the PF interior along the border. PF
floor -10C respected (PF never below it); crag floor -20C respected. NO RNG."""
import csv, math, json, collections
def amp(lat):
    d=abs(math.sin(math.radians(lat)))
    return 3+10*d if d<=0.1 else 4+(d-0.1)*24/0.9
def finger(lon,lat):
    return math.sin(math.radians(6*lon+5*lat+15))+0.5*math.sin(math.radians(13*lon+60))
rows=list(csv.DictReader(open('world/ASHKARR_WORLDMAP_tiles.csv')))
R={int(r['tile']):r for r in rows}
cur={int(r['tile']):r['biome'] for r in rows}
for pf in ('world/backside_reband_full.json','world/pf_terminator_plan.json',
           'world/wasteland_reclaim_plan.json','world/crag_meander_plan.json'):
    for p in json.load(open(pf)): cur[p['tile']]=p['to']
nb={int(row['tile']):[int(row[f'n{i}']) for i in range(6) if int(row[f'n{i}'])>=0]
    for row in csv.DictReader(open('world/world_neighbors_sub7b.csv'))}
PARTNERS={'Desert','Wasteland','ZBiome_Badlands','AridShrubland','AB_RockyCrags'}
def mean(t): return float(R[t]['temp_c'])
def fld(t): return finger(float(R[t]['lon']),float(R[t]['lat']))
moves={}
for t,b in cur.items():
    ns=nb.get(t,[])
    if b=='PoisonForest':
        partn=[cur[n] for n in ns if cur.get(n) in PARTNERS]
        if partn and fld(t)<-0.15:                    # PF recedes into a neighbour (incl. crag)
            pick=collections.Counter(partn).most_common(1)[0][0]
            if pick=='AB_RockyCrags' and mean(t)<-20: continue   # crag floor
            moves[t]=pick
    elif b in PARTNERS:
        if any(cur.get(n)=='PoisonForest' for n in ns) and fld(t)>0.2 and mean(t)>=-10:
            moves[t]='PoisonForest'                   # PF fingers out into the dryland
# constraints
errs=[t for t,mb in moves.items() if (mb=='PoisonForest' and mean(t)<-10) or (mb=='AB_RockyCrags' and mean(t)<-20)]
print(f"PF meander: {len(moves)} tiles | errors {len(errs)}")
print("  swaps:", dict(collections.Counter((cur[t],mb) for t,mb in moves.items())))
pfb=sum(1 for v in cur.values() if v=='PoisonForest')
pfa=pfb - sum(1 for t,mb in moves.items() if cur[t]=='PoisonForest') + sum(1 for mb in moves.values() if mb=='PoisonForest')
print(f"  PF {pfb} -> {pfa}")
json.dump([{'tile':t,'to':mb} for t,mb in moves.items()], open('world/pf_meander_plan.json','w'))
