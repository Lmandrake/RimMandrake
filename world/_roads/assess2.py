import sys, json, collections
sys.path.insert(0,'/mnt/d/Luke/dev/Rimworld/world/_roads')
from rcommon import *
tiles,nb,roads,rivers,setts,objs=load()
lm=json.load(open(R+'_landmarks.json'))['landmarks']
by_tile=collections.defaultdict(list)
for l in lm: by_tile[l['tile']].append(l['def'])

RUIN={'Ruins','AncientGarrison','AncientWarehouse','AbandonedColonyTribal','AbandonedColonyOutlander',
      'AncientQuarry','AncientChemfuelRefinery','TerraformingScar','FrozenRuins','AncientLaunchSite',
      'AncientHeatVent','sw_DeadSarlacc'}
SHADE={'Cliffs','Valley','Cavern','Hollow','Chasm','VEE_SerpentineCanyons','VEE_RockRidge',
       'Plateau','Basin','VEE_StoneForest','VEE_MeteorCrater'}
WATER={'Oasis','VEE_Cenotes','HotSprings','DryLake','VEE_StagnantRivulet','VEE_AlluvialFan','Bay'}

rt=set(roads)
# BFS distance from the road network
dist={t:0 for t in rt}; frontier=list(rt)
d=0
while frontier and d<40:
    d+=1; nxt=[]
    for t in frontier:
        for n in nb[t]:
            if n not in dist: dist[n]=d; nxt.append(n)
    frontier=nxt

def report(name, S):
    hits=[(t,defs) for t,defs in by_tile.items() if set(defs)&S]
    ds=[dist.get(t,99) for t,_ in hits]
    on=sum(1 for x in ds if x==0); near=sum(1 for x in ds if 1<=x<=2); far=sum(1 for x in ds if x>=6)
    ds_s=sorted(ds)
    print("%-8s %3d tiles   on-road %2d   within 2 %2d   6+ away %2d   median dist %d"
          %(name,len(hits),on,near,far,ds_s[len(ds_s)//2]))
    return hits

print("LANDMARK CLASSES vs the road network (hex distance)")
ruins=report('RUIN',RUIN); shade=report('SHADE',SHADE); water=report('WATER',WATER)

print("\nSETTLEMENTS not on a road:")
for o in setts:
    if o['tile'] not in rt:
        t=tiles[o['tile']]
        print("  %-26s %-22s tile %-6d %-22s %4dm %5.1fC  d-to-road %s"
              %(o['name'] or o['label'], o['factionName'], o['tile'], t['biome'], t['elev'], t['temp'], dist.get(o['tile'],'>40')))

# how hot/shaded is the ground the roads cross, vs alternatives
print("\nSHADE PROXIES on road tiles vs land")
land=[t for t in tiles if not tiles[t]['water']]
def m(sel,f): 
    v=[f(tiles[t]) for t in sel]; return sum(v)/len(v)
print("  hilliness   road %.2f  land %.2f"%(m(rt,lambda x:x['hill']),m(land,lambda x:x['hill'])))
print("  tmax        road %.1f  land %.1f"%(m(rt,lambda x:x['tmax']),m(land,lambda x:x['tmax'])))
print("  riverDist   road %.2f  land %.2f"%(m(rt,lambda x:x['riverDist']),m(land,lambda x:x['riverDist'])))
# oasis/cenote proximity
wset={t for t,_ in water}
wd={t:0 for t in wset}; fr=list(wset); dd=0
while fr and dd<12:
    dd+=1; nx=[]
    for t in fr:
        for n in nb[t]:
            if n not in wd: wd[n]=dd; nx.append(n)
    fr=nx
print("  dist to nearest WATER landmark: road %.2f  land %.2f"
      %(m(rt,lambda x:wd.get(x['tile'],12)), m(land,lambda x:wd.get(x['tile'],12))))
