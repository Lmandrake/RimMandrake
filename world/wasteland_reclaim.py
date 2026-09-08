#!/usr/bin/env python3
"""Wasteland reaches too far into shadow (owner, 2026-09-07, from his screenshot).
Reclaim the cold wasteland into ice+blue desert (backside order: ice warmer, blue
colder), pushing wasteland back toward the sun. A wasteland tile is reclaimable only
where it is PERMANENTLY sub-zero (max temp < 0) -- a tile that thaws in summer cannot
be ice/blue and stays wasteland, which is exactly 'pushed toward the sun'. Same
de-circling longitude field as the backside; physical lines hard."""
import csv, math, json, collections
def amp(lat):
    d=abs(math.sin(math.radians(lat)))
    return 3+10*d if d<=0.1 else 4+(d-0.1)*24/0.9
def wob(lon,elev):
    lr=math.radians(lon)
    return max(-16,min(16,8.5*math.sin(2*lr+0.5)+6.0*math.sin(3*lr+2.0)+3.0*math.sin(6*lr+1.1)+0.025*(elev-500)))
rows=list(csv.DictReader(open('world/ASHKARR_WORLDMAP_tiles.csv')))
# current live biome = CSV overlaid with the two applied plans
cur={int(r['tile']):r['biome'] for r in rows}
for pf in ('world/backside_reband_full.json','world/pf_terminator_plan.json'):
    for p in json.load(open(pf)): cur[p['tile']]=p['to']
moves={}
for r in rows:
    t=int(r['tile'])
    if cur[t]!='Wasteland': continue
    mean=float(r['temp_c']); tmax=mean+amp(float(r['lat']))
    if tmax>=0: continue                       # thaws in summer -> stays wasteland (pushed sunward)
    a=mean+wob(float(r['lon']),float(r['elev_m']))
    if mean<-42 and a<-42: moves[t]='AB_PropaneLakes'
    elif a>=-33: moves[t]='RUT_NightsideIce'
    else: moves[t]='BiomeGRimond'
# constraint proof
errs=[]
byid={int(r['tile']):r for r in rows}
for t,b in moves.items():
    r=byid[t]; mean=float(r['temp_c']); tmax=mean+amp(float(r['lat']))
    if b in ('RUT_NightsideIce','BiomeGRimond') and tmax>=0: errs.append(('melt',t))
    if b=='AB_PropaneLakes' and mean>=-42: errs.append(('prop',t))
print(f"wasteland reclaim: {len(moves)} tiles | ERRORS {len(errs)}")
print("  ->", dict(collections.Counter(moves.values())))
wl_before=sum(1 for v in cur.values() if v=='Wasteland')
print(f"  Wasteland {wl_before} -> {wl_before-len(moves)}")
json.dump([{'tile':t,'to':b} for t,b in moves.items()], open('world/wasteland_reclaim_plan.json','w'))
