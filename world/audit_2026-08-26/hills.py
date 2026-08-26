# -*- coding: utf-8 -*-
"""Derive hilliness from local relief + elevation. Preview only unless --write."""
import csv, json, collections, sys
A='world/_audit/'
T={int(r['tile']):r for r in csv.DictReader(open(A+'final_tiles.csv',encoding='utf-8'))}
NB={int(r['tile']):[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0]
    for r in csv.DictReader(open(A+'neighbors.csv',encoding='utf-8'))}
REG={int(r['tile']):r['region'] for r in csv.DictReader(open(A+'LIVE_tiles.csv',encoding='utf-8'))}
caps=json.load(open(A+'caps.json',encoding='utf-8'))
capF=set(caps['capF']); capM={t:m for t,m in caps['capM']}
SETT={o['tile'] for o in json.load(open(A+'objects.json',encoding='utf-8'))['objects'] if o['def']=='Settlement'}
HIL={'Flat':1,'SmallHills':2,'LargeHills':3,'Mountainous':4,'Impassable':5,'Undefined':0}
NAME={1:'Flat',2:'SmallHills',3:'LargeHills',4:'Mountainous',5:'Impassable'}
WATER={'Ocean','Lake','SeaIce'}
el={t:float(T[t]['elevation']) for t in T}
cur={t:HIL.get(T[t]['hilliness'],1) for t in T}
roads={t for t in T if int(T[t]['roadCount'] or 0)>0}

land=[t for t in T if el[t]>0 and T[t]['biome'] not in WATER]
relief={t: max((abs(el[t]-el[n]) for n in NB[t]), default=0.0) for t in T}
# second-order roughness: mean absolute deviation across the neighbourhood
rough={t: (sum(abs(el[n]-el[t]) for n in NB[t])/len(NB[t])) if NB[t] else 0.0 for t in T}
def pct(vals):
    s=sorted(vals); n=len(s)
    return lambda x: (sum(1 for v in s if v<x)/n)
pr=pct([relief[t] for t in land]); pe=pct([el[t] for t in land]); pg=pct([rough[t] for t in land])
# Authored intent: a region NAMED for mountains is one, whatever the noise says.
RANGES={'Ashfall Range','Scald Spine','Gray Crags','South Crags','Twilight Crags',
        'Fall Line','Fall Line Barrens','Dew Horn','Rimewall','Frostcaps','Knuckles'}
CORE  ={'Ashfall Range','Scald Spine','Dew Horn','Gray Crags','Twilight Crags','South Crags'}
score={t: 0.50*pr(relief[t]) + 0.30*pg(rough[t]) + 0.20*pe(el[t])
          + (0.35 if REG.get(t) in CORE else 0.22 if REG.get(t) in RANGES else 0.0)
       for t in land}
order=sorted(land, key=lambda t:-score[t])
# target shares of LAND
TARGET=[(5,0.020),(4,0.115),(3,0.190),(2,0.300),(1,None)]
want={}
i=0
for cls,share in TARGET:
    if share is None:
        for t in order[i:]: want[t]=1
        break
    k=int(len(order)*share)
    for t in order[i:i+k]: want[t]=cls
    i+=k
# constraints
new={}
for t in T:
    if t not in want: new[t]=1; continue          # water -> Flat
    v=want[t]
    if t in capF: v=1
    elif t in capM: v=min(v,capM[t])
    if t in SETT: v=min(v,4)
    if t in roads: v=min(v,4)
    # a named range never drops below rolling hills, and never loses a summit it had
    if REG.get(t) in RANGES and t not in capF and t not in capM:
        v=max(v, 3 if REG.get(t) in CORE else 2)
    if REG.get(t) in RANGES: v=max(v, min(cur[t],4) if t in SETT or t in roads else cur[t])
    new[t]=v
changed={t:(cur[t],new[t]) for t in T if new[t]!=cur[t]}
print("PREVIEW  (%d tiles change of %d)"%(len(changed),len(T)))
print("  before:", {NAME[k]:v for k,v in sorted(collections.Counter(cur.values()).items())})
print("  after :", {NAME[k]:v for k,v in sorted(collections.Counter(new.values()).items())})
def corr(xs,ys):
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    num=sum((a-mx)*(b-my) for a,b in zip(xs,ys))
    den=(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))**.5
    return num/den if den else 0
print("  corr(hilliness, relief): %.3f -> %.3f"%(corr([cur[t] for t in land],[relief[t] for t in land]),
                                                 corr([new[t] for t in land],[relief[t] for t in land])))
print("\n  named ranges after:")
for rn in ('Ashfall Range','Scald Spine','Dew Horn','Gray Crags','South Crags','Twilight Crags','Rimewall','Frostcaps','Fall Line'):
    ts=[t for t in T if REG.get(t)==rn]
    a=collections.Counter(new[t] for t in ts); bfr=collections.Counter(cur[t] for t in ts)
    print("    %-16s Mountainous %3d->%3d  Impassable %2d->%2d"%(rn,bfr[4],a[4],bfr[5],a[5]))
print("\n  the sand stays flat:")
for rn in ('Dune Sea','Glare','Long Sand','Kiln'):
    ts=[t for t in T if REG.get(t)==rn]
    a=collections.Counter(new[t] for t in ts)
    print("    %-12s Flat %4d  SmallHills %3d  LargeHills %3d  Mountainous %3d"%(rn,a[1],a[2],a[3],a[4]))
# landform unlock
mtn=sum(1 for t in T if new[t]>=4); mtn0=sum(1 for t in T if cur[t]>=4)
print("\n  landform eligibility (hilliness term only):")
print("    Crater / Rift  (need 3.4-5.0): %d -> %d tiles"%(mtn0,mtn))
print("    Valley         (need 3.7-4.8): %d -> %d tiles"%(sum(1 for t in T if cur[t]==4),sum(1 for t in T if new[t]==4)))
json.dump({str(t):new[t] for t in changed}, open(A+'hills_plan.json','w'))
print("\n  plan written: world/_audit/hills_plan.json")
