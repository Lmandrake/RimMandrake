#!/usr/bin/env python3
"""Poison Forest = a TERMINATOR biome fed by the terminator wall (owner, 2026-09-07).
No business well below freezing (floor -10 C); evicted cold strays re-band by the
backside temperature ladder. Then PF regains significance by consuming ~1/3 of the
prolific wall drylands (Desert/Wasteland/Badlands/AridShrubland) at arc 86-96, taken
as interleaved GROVES via a deterministic longitude field -- NOT a solid ring (that
would be a new bullseye) and NOT RNG (a seed could roll a second planet)."""
import csv, math, json, collections

def amp(lat):
    d=abs(math.sin(math.radians(lat)))
    return 3+10*d if d<=0.1 else 4+(d-0.1)*24/0.9
def band_target(mean,tmax,lon,elev):   # same ladder as backside_reband
    if mean>=-20: return 'AB_RockyCrags'
    lr=math.radians(lon)
    w=max(-16,min(16,8.5*math.sin(2*lr+0.5)+6.0*math.sin(3*lr+2.0)+3.0*math.sin(6*lr+1.1)+0.025*(elev-500)))
    a=mean+w
    if mean<-42 and a<-42: return 'AB_PropaneLakes'
    if tmax>=0: return None
    return 'RUT_NightsideIce' if a>=-33 else 'BiomeGRimond'
def grove(lon,lat):   # deterministic grove field, ~3 lobes along the wall
    return math.sin(math.radians(3*lon+2*lat+20))+0.6*math.sin(math.radians(7*lon+50))

DONORS={'Desert','Wasteland','ZBiome_Badlands','AridShrubland'}
TARGET_PF=500

def main():
    rows=list(csv.DictReader(open('world/ASHKARR_WORLDMAP_tiles.csv')))
    for r in rows:
        r['mean']=float(r['temp_c']); r['tmax']=r['mean']+amp(float(r['lat'])); r['arc']=float(r['arc'])
    moves={}   # tile -> new biome
    # A. evict cold PF (mean < -10)
    evict=0; corner=0
    for r in rows:
        if r['biome']=='PoisonForest' and r['mean']<-10:
            t=band_target(r['mean'],r['tmax'],float(r['lon']),float(r['elev_m']))
            if t is None: corner+=1; continue
            moves[int(r['tile'])]=t; evict+=1
    surv=sum(1 for r in rows if r['biome']=='PoisonForest' and r['mean']>=-10)
    # B. grow PF: consume donors at the wall, groves, up to TARGET
    need=TARGET_PF-surv
    cand=[r for r in rows if 86<=r['arc']<=96 and r['mean']>=-10 and r['biome'] in DONORS]
    cand.sort(key=lambda r:-grove(float(r['lon']),float(r['lat'])))  # highest grove-field first
    grown=collections.Counter()
    for r in cand[:need]:
        moves[int(r['tile'])]='PoisonForest'; grown[r['biome']]+=1
    # constraints on writes
    fin={int(r['tile']):r for r in rows}
    errs=[]
    for t,b in moves.items():
        r=fin[t]
        if b=='AB_PropaneLakes' and r['mean']>=-42: errs.append(('prop',t))
        if b in ('RUT_NightsideIce','BiomeGRimond') and r['tmax']>=0: errs.append(('melt',t))
        if b=='AB_RockyCrags' and r['mean']<-20: errs.append(('crags',t))
        if b=='PoisonForest' and r['mean']<-10: errs.append(('pfcold',t))
    census=collections.Counter(moves.get(int(r['tile']),r['biome']) for r in rows)
    print(f"PF evict cold {evict} (corner left {corner}) | PF survive {surv} | grow {sum(grown.values())} from {dict(grown)}")
    print(f"CONSTRAINT ERRORS {len(errs)} {errs[:4]}")
    for b in ['PoisonForest','Desert','Wasteland','ZBiome_Badlands','AridShrubland','AB_RockyCrags','RUT_NightsideIce','BiomeGRimond','AB_PropaneLakes']:
        print(f"  {b:20s} {sum(1 for r in rows if r['biome']==b):5d} -> {census[b]:5d}")
    json.dump([{'tile':t,'to':b} for t,b in moves.items()], open('world/pf_terminator_plan.json','w'))
    print("plan ->", len(moves), "tiles")

if __name__=='__main__': main()
