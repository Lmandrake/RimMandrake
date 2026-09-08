#!/usr/bin/env python3
"""Backside temperature-band repaint, owner-ruled 2026-09-07 (in discussion, BENCH).

RULING. Warm->cold on the nightside: crags > white ice > blue desert > propane.
  crags        mean >= -20 C            (owner: "crags shouldn't go below -20")
  white ice    -33 <= mean < -20        (warmer half of the mid band)
  blue desert  colder half              (ice/blue split -33 C, ice warmer)
  propane      mean < -42 C             (propane's boiling point; the shadow cap
               across Umbra+Ammonia Flats+Deadstone, de-circled)
HARD PHYSICAL LINES (never crossed by the anti-bullseye wobble):
  * propane requires real mean < -42 C  (boils above it)
  * ice AND blue desert require real MAX temp < 0 C (else the ice melts) -- max =
    mean + SeasonalTempVariationCurve(|sin lat|), RimWorld's own curve (3..28 C).
ANTI-BULLSEYE (owner: "de-circle-fied, keep adding longitudinal structure"):
  a deterministic longitude field w(lon,elev) wobbles the two SOFT boundaries
  (ice/blue, and which sub-42 tiles propane claims) so the bands lobe by longitude
  instead of ringing the antipode. No RNG -- a seed could roll a second planet.
SCOPE: tiles already in the dark pool {crags, ice, blue desert, propane biome} plus
  the 37 mycotic-jungle tiles that strayed onto the cap regions. The propane LAKE
  (RUT_PropaneLake) and the Rot's cold HOME are excluded (owner: trim spread only).
"""
import csv, math, collections, json, sys

DARK={'AB_RockyCrags','RUT_NightsideIce','BiomeGRimond','AB_PropaneLakes'}
CAP={'Umbra','Ammonia Flats','Deadstone','Coldstone'}
SPLIT=-33.0

def amp(lat):
    d=abs(math.sin(math.radians(lat)))
    return 3+10*d if d<=0.1 else 4+(d-0.1)*24/0.9

def wobble(lon, elev):
    # Longitudinal anti-bullseye field (owner: "de-circle-fied, keep adding
    # longitudinal structure"). Deterministic in the tile's own lon+elevation --
    # NO RNG (a seed could roll a second planet). Big low-frequency lobes (freq 2,3)
    # break the propane disk into fingers; freq 6 adds edge detail; elevation ties
    # the lobes to real relief. Amplitude ~16 C so the swing actually crosses bands.
    lr=math.radians(lon)
    w=(8.5*math.sin(2*lr+0.5) + 6.0*math.sin(3*lr+2.0)
       + 3.0*math.sin(6*lr+1.1) + 0.025*(elev-500))
    return max(-16.0, min(16.0, w))

def target(mean, tmax, lon, elev):
    if mean>=-20: return 'AB_RockyCrags'
    a=mean+wobble(lon,elev)                     # soft-band coordinate
    if mean<-42 and a<-42: return 'AB_PropaneLakes'   # propane finger: real AND wobbled cold
    if tmax>=0: return None                     # impossible corner (cold mean, thaws in summer):
                                                 # can't be ice/blue (melts), can't be crags (<-20 floor),
                                                 # can't be propane (>-42). Leave the tile as it is.
    return 'RUT_NightsideIce' if a>=SPLIT else 'BiomeGRimond'

def main(path):
    rows=list(csv.DictReader(open(path)))
    for r in rows:
        r['mean']=float(r['temp_c']); r['tmax']=r['mean']+amp(float(r['lat']))
    fin_by={int(r['tile']):r for r in rows}
    scope=[r for r in rows if r['biome'] in DARK or
           (r['biome']=='AB_MycoticJungle' and r['region'] in CAP)]
    moves=[]; left=0
    for r in scope:
        t=target(r['mean'], r['tmax'], float(r['lon']), float(r['elev_m']))
        if t is None: left+=1; continue          # impossible corner, leave unchanged
        if t!=r['biome']: moves.append((int(r['tile']), r['biome'], t))
    # ---- constraint proofs on the TILES I WRITE (fail loud) ----
    mvto={t:to for t,_,to in moves}
    errs=[]
    for t,_,b in moves:
        r=fin_by[t]
        if b=='AB_PropaneLakes' and r['mean']>=-42: errs.append(('propane>=-42',t,r['mean']))
        if b in ('RUT_NightsideIce','BiomeGRimond') and r['tmax']>=0: errs.append(('melt',t,r['tmax']))
        if b=='AB_RockyCrags' and r['mean']<-20: errs.append(('crags<-20',t,r['mean']))
    # anti-bullseye check: biome diversity per latitude ring
    ring=collections.defaultdict(set)
    for r in rows:
        b=mvto.get(int(r['tile']), r['biome'])
        if b in DARK|{'AB_PropaneLakes'}:
            ring[round(float(r['arc'])/5)*5].add(b)
    multi=sum(1 for s in ring.values() if len(s)>1)
    census=collections.Counter(mvto.get(int(r['tile']), r['biome']) for r in rows)
    print(f"scope {len(scope)} | moves {len(moves)} | left-unchanged(corner) {left} | CONSTRAINT ERRORS {len(errs)}")
    if errs: print("  ERR sample:", errs[:5]); sys.exit(2)
    print("move matrix:", dict(collections.Counter((f,t) for _,f,t in moves)))
    print("resulting census:")
    for b in ['AB_RockyCrags','RUT_NightsideIce','BiomeGRimond','AB_PropaneLakes','RUT_PropaneLake','AB_MycoticJungle']:
        before=sum(1 for r in rows if r['biome']==b)
        print(f"  {b:20s} {before:5d} -> {census[b]:5d}")
    print(f"anti-bullseye: arc rings with >1 dark biome = {multi}/{len(ring)}")
    json.dump([{'tile':t,'from':f,'to':to} for t,f,to in moves],
              open('world/backside_reband_plan.json','w'))
    print("plan -> world/backside_reband_plan.json")

if __name__=='__main__':
    main('world/ASHKARR_WORLDMAP_tiles.csv')
