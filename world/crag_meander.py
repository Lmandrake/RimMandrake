#!/usr/bin/env python3
"""Break the linear crag stripe into an interlocking, meandering border (owner,
2026-09-07). Uses tile adjacency: along the crag band's edge, a deterministic
longitude+lat finger field decides which side each border tile falls on, so crags
and its warm neighbours (Wasteland/Desert/Badlands) interlock as fingers, and ice
tongues into the cold edge. Physical floors respected: NO crags below -20C (owner),
ice only where max temp < 0 (melt). PoisonForest and seas are never eaten. NO RNG."""
import csv, math, json, collections
def amp(lat):
    d=abs(math.sin(math.radians(lat)))
    return 3+10*d if d<=0.1 else 4+(d-0.1)*24/0.9
def finger(lon,lat):
    return math.sin(math.radians(5*lon+4*lat+10))+0.5*math.sin(math.radians(11*lon+40))
rows=list(csv.DictReader(open('world/ASHKARR_WORLDMAP_tiles.csv')))
R={int(r['tile']):r for r in rows}
cur={int(r['tile']):r['biome'] for r in rows}
for pf in ('world/backside_reband_full.json','world/pf_terminator_plan.json','world/wasteland_reclaim_plan.json'):
    for p in json.load(open(pf)): cur[p['tile']]=p['to']
nb={}
for row in csv.DictReader(open('world/world_neighbors_sub7b.csv')):
    nb[int(row['tile'])]=[int(row[f'n{i}']) for i in range(6) if int(row[f'n{i}'])>=0]
WARM={'Wasteland','Desert','ZBiome_Badlands'}   # generic drylands crags may interlock with
COLD={'RUT_NightsideIce','BiomeGRimond'}
def mean(t): return float(R[t]['temp_c'])
def tmax(t): return mean(t)+amp(float(R[t]['lat']))
def fld(t): return finger(float(R[t]['lon']),float(R[t]['lat']))
moves={}
for t,b in cur.items():
    ns=nb.get(t,[])
    if b=='AB_RockyCrags':
        warmn=[cur[n] for n in ns if cur.get(n) in WARM]
        coldn=[n for n in ns if cur.get(n) in COLD]
        if warmn and fld(t)<-0.2 and mean(t)>=-20:            # crag recedes into a warm neighbour
            moves[t]=collections.Counter(warmn).most_common(1)[0][0]
        elif coldn and fld(t)<-0.2 and tmax(t)<0 and mean(t)<=-15:  # ice tongue into cold edge
            moves[t]='RUT_NightsideIce'
    elif b in WARM:
        if any(cur.get(n)=='AB_RockyCrags' for n in ns) and fld(t)>0.25 and -20<=mean(t)<=5:
            moves[t]='AB_RockyCrags'                          # crag fingers out into the dryland
# constraint proof
errs=[(t,) for t,mb in moves.items() if mb=='AB_RockyCrags' and mean(t)<-20]
print(f"crag border meander: {len(moves)} tiles | crags<-20 errors {len(errs)}")
print("  swaps:", dict(collections.Counter((cur[t],mb) for t,mb in moves.items())))
cb=sum(1 for v in cur.values() if v=='AB_RockyCrags')
nb_c=cb - sum(1 for t,mb in moves.items() if cur[t]=='AB_RockyCrags') + sum(1 for mb in moves.values() if mb=='AB_RockyCrags')
print(f"  crags {cb} -> {nb_c}")
json.dump([{'tile':t,'to':mb} for t,mb in moves.items()], open('world/crag_meander_plan.json','w'))
