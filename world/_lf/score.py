# -*- coding: utf-8 -*-
"""Score all 44 GL landform graphs against Ash'karr AS IT LIVES NOW.
Reads the requirement ranges straight from the mod's NodeCanvas XML - nothing hand-copied."""
import re, os, glob, csv, json, math, collections
W="/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100/2773943594/1.6/Landforms-v1"
R="/mnt/d/Luke/dev/Rimworld"

# ---- 1. requirements, parsed from the graphs
LF=[]
for f in sorted(glob.glob(os.path.join(W,"Landform*.xml"))):
    d=re.sub(r' xmlns:[^=]+="[^"]*"','',open(f,encoding='utf-8').read())
    m=re.search(r'<Node name="World Tile Requirements".*?</Node>', d, re.S)
    if not m: continue
    s=m.group(0)
    def fr(n,dv):
        mm=re.search(r'<FloatRange name="%s">\s*<min>([-\d.eE+]+)</min>\s*<max>([-\d.eE+]+)</max>'%n,s)
        return (float(mm.group(1)),float(mm.group(2))) if mm else dv
    LF.append(dict(
        id=re.search(r'<string name="Id">([^<]+)<',d).group(1),
        topo=re.search(r'<Topology name="Topology">([^<]+)<',s).group(1),
        com=float(re.search(r'<float name="Commonness">([\d.eE+-]+)<',s).group(1)),
        cave=float(re.search(r'<float name="CaveChance">([\d.eE+-]+)<',s).group(1)),
        hil=fr("HillinessRequirement",(1,6)), elev=fr("ElevationRequirement",(0,5000)),
        temp=fr("AvgTemperatureRequirement",(-100,100)), rain=fr("RainfallRequirement",(0,5000)),
        swamp=fr("SwampinessRequirement",(0,1)), river=fr("RiverRequirement",(0,1)),
        road=fr("RoadRequirement",(0,1)), depth=fr("DepthInCaveSystemRequirement",(0,10)),
        nodes=len(re.findall(r'<Node name=',d))))

# ---- 2. the live planet
T={}
for r in csv.DictReader(open(os.path.join(R,"world/_lf/live_tiles.csv"),encoding='utf-8')):
    T[int(r['tile'])]=r
NB={}
for r in csv.DictReader(open(os.path.join(R,"world/_audit/neighbors.csv"),encoding='utf-8')):
    NB[int(r['tile'])]=[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0]
HN={1:'Flat',2:'SmallHills',3:'LargeHills',4:'Mountainous',5:'Impassable'}
HV={v:k for k,v in HN.items()}
def water(t):
    r=T.get(t)
    return r is None or r['waterCovered'].lower() in ('true','1')

# topology approximation: water-neighbour count. GL's own Cliff*/Cave* classes are
# computed inside the mod and are NOT modelled here.
TOPO={}
for t,r in T.items():
    if water(t): TOPO[t]='Water'; continue
    w=sum(1 for n in NB.get(t,()) if water(n))
    TOPO[t]= 'Inland' if w==0 else ('CoastOneSide' if w==1 else 'CoastTwoSides' if w==2
             else 'CoastThreeSides' if w==3 else 'CoastAllSides')
UNMODELLED={'CliffOneSide','CliffTwoSides','CliffThreeSides','CliffAllSides','CliffValley',
            'CliffAndCoast','CoastLandbridge','CaveTunnel','CaveEntrance'}

def eligible(L):
    if L['topo'] in UNMODELLED: return None
    hlo,hhi=L['hil']
    n=0; ex=[]
    for t,r in T.items():
        if water(t): continue
        h=HV.get(r['hilliness'],0)
        if not (hlo-1e-9 <= h <= hhi+1e-9): continue
        if L['topo'] not in ('Any',) and TOPO[t]!=L['topo']: continue
        e=float(r['elevation']); tc=float(r['temperature']); ra=float(r['rainfall'])
        sw=float(r['swampiness']); rv=int(r['riverCount']); rd=int(r['roadCount'])
        if not (L['elev'][0]<=e<=L['elev'][1]): continue
        if not (L['temp'][0]<=tc<=L['temp'][1]): continue
        if not (L['rain'][0]<=ra<=L['rain'][1]): continue
        if not (L['swamp'][0]<=sw<=L['swamp'][1]): continue
        if L['river'][1]<=0 and rv>0: continue
        if L['river'][0]>0 and rv==0: continue
        if L['road'][1]<=0 and rd>0: continue
        if L['road'][0]>0 and rd==0: continue
        n+=1
        if len(ex)<3: ex.append(t)
    return n,ex

rows=[]
for L in LF:
    r=eligible(L)
    rows.append((L,r))
rows.sort(key=lambda x:(x[1] is None, -(x[1][0] if x[1] else 0)))
print("%-16s %-16s %5s %5s %-14s %8s  %s"%("landform","topology","com","cave","hilliness","TILES","sample"))
for L,r in rows:
    hl="%.2g-%.2g"%L['hil']
    if r is None:
        print("%-16s %-16s %5.3f %5.2f %-14s %8s"%(L['id'],L['topo'],L['com'],L['cave'],hl,"GL-COMPUTED"))
    else:
        print("%-16s %-16s %5.3f %5.2f %-14s %8d  %s"%(L['id'],L['topo'],L['com'],L['cave'],hl,r[0],
              ",".join(map(str,r[1]))))
h=collections.Counter(v['hilliness'] for v in T.values() if not water(int(v['tile'])))
print("\nlive land hilliness:", dict(h))
print("live topology:", dict(collections.Counter(TOPO.values())))
