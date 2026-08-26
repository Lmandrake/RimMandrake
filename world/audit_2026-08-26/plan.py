# -*- coding: utf-8 -*-
"""Build the six-pass edit plan for Ash'karr. Pure offline; writes ops.json.

Guards enforced here, because the setter enforces none of them:
  * biome whitelist / blacklist, hilliness, coast, canSpawnOnRiver   (the def's own gates)
  * CATEGORY COLLISION - AddMutator silently removes a same-category
    mutator already on the tile, so a tile already carrying one is skipped
    unless the op says displacement is intended.
Landmarks are emitted as ORDERED CANDIDATE LISTS with a target count; the
executor places them one at a time with checkValid and falls through.
"""
import csv, json, collections, random
A='world/_audit/'
T={int(r['tile']):r for r in csv.DictReader(open(A+'LIVE_tiles.csv',encoding='utf-8'))}
NB={int(r['tile']):[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0]
    for r in csv.DictReader(open(A+'neighbors.csv',encoding='utf-8'))}
MUT={t['tile']:{m['def'] for m in t['mutators']} for t in json.load(open(A+'mutators.json',encoding='utf-8'))}
LMK={x['tile']:x['def'] for x in json.load(open(A+'landmarks.json',encoding='utf-8'))['landmarks']}
LINKS={t['tile']:t for t in json.load(open(A+'links.json',encoding='utf-8'))}
SETT={o['tile'] for o in json.load(open(A+'objects.json',encoding='utf-8'))['objects']}
COAST=set(json.load(open(A+'coastal.json')))
CAT=json.load(open(A+'mut_categories.json'))
random.seed(7)

WATER={'Ocean','Lake','SeaIce'}
NOROAD={'AB_MechanoidIntrusion','Lake','Ocean','AB_PropaneLakes','AB_TarPits','IceSheet','SeaIce'}
DRY_WL={'Desert','ExtremeDesert','AridShrubland','Grasslands','TemperateForest','BiomeCypreJungle'}
SALT_WL={'Desert','ExtremeDesert','AridShrubland','Grasslands','BiomeCypreJungle'}
TAT_WL={'AridShrubland','Desert','ExtremeDesert'}
b=lambda t:T[t]['biome']; arc=lambda t:float(T[t]['arc']); hil=lambda t:int(T[t]['hilliness'])
elev=lambda t:float(T[t]['elev_m']); reg=lambda t:T[t]['region']
hasriver=lambda t:int(T[t]['river_count'] or 0)>0
hasroad=lambda t:int(T[t]['road_count'] or 0)>0
has=lambda t,d: d in MUT.get(t,())
free=lambda t: t not in LMK and t not in SETT

def collides(t,d):
    """True if the tile already holds a DIFFERENT mutator sharing a category."""
    cs=set(CAT.get(d) or ())
    if not cs: return False
    for m in MUT.get(t,()):
        if m!=d and cs & set(CAT.get(m) or ()): return True
    return False

ops=[]
def mut(tag, d, tiles, gate=None, displace=False, cap=None, note=''):
    out=[]
    for t in tiles:
        if has(t,d): continue
        if gate and not gate(t): continue
        if not displace and collides(t,d): continue
        out.append(t)
        if cap and len(out)>=cap: break
    if out:
        ops.append(dict(p=tag,kind='mutator',action='add',mutators=d,tiles=sorted(set(out)),note=note))
        for t in out: MUT.setdefault(t,set()).add(d)
    return out
def lmk(tag, d, candidates, want, note=''):
    cand=[t for t in candidates if free(t)]
    if cand:
        ops.append(dict(p=tag,kind='landmark',action='add',d=d,candidates=cand[:want*6],want=want,note=note))

def spread(cand,k,ring=2):
    out=[]
    for t in cand:
        if len(out)>=k: break
        if all(o!=t and t not in NB[o] and not (set(NB[t])&set(NB[o])) for o in out): out.append(t)
    return out

# ================================================================= A. SOLAR
solarBL={'Glowforest','AB_RockyCrags'}
mut('A-solar','VEE_MoreSolarPower',[t for t in T if arc(t)<=55 and b(t) not in solarBL and b(t) not in WATER],
    note='dayside within 55 deg of the substellar point')
mut('A-solar','VEE_LessSolarPower',[t for t in T if arc(t)>=125 and b(t) not in solarBL and b(t) not in WATER],
    note='beyond 125 deg - effectively night. The terminator belt is left unmarked on purpose.')

# ================================================================= B. WATER MEMORY
dry_ok  = lambda t: b(t) in DRY_WL  and t not in COAST and not hasriver(t)
salt_ok = lambda t: b(t) in SALT_WL and t not in COAST and not hasriver(t)
sources=[]
for rname,n in (('Ashfall Range',7),('Dew Horn',6),('Fall Line',4),('Gray Crags',4),('Twilight Crags',3)):
    cand=sorted([t for t in T if reg(t)==rname and hil(t)>=3 and not hasriver(t)], key=elev, reverse=True)
    picked=[]
    for t in cand:
        if len(picked)>=n: break
        if all(p not in NB[t] for p in picked): picked.append(t)
    sources+=picked
channels=[]
for s in sources:
    path=[s]; cur=s; seen={s}
    for _ in range(30):
        nbrs=[x for x in NB[cur] if x not in seen and b(x) not in WATER]
        if not nbrs: break
        nxt=min(nbrs,key=lambda x:(elev(x),hil(x)))
        if elev(nxt)>elev(cur)+12: break
        path.append(nxt); seen.add(nxt); cur=nxt
    if len(path)>=5: channels.append(path)
chan=[t for p in channels for t in p[1:-2]]
term=[t for p in channels for t in p[-3:]]
mut('B-water','VEE_DryRiver',chan,gate=dry_ok,note='dead channels descending out of the named ranges')
mut('B-water','VEE_SaltPlains',term,gate=salt_ok,note='where each dead channel gives up')
lmk('B-water','VEE_DryRiver',[p[len(p)//2] for p in channels if len(p)>=9],8)
lmk('B-water','DryLake',[t for t in term if salt_ok(t)],6)
grey=spread(sorted([t for t in COAST if reg(t)=='Grey Sea' and hil(t)<=1 and b(t) in DRY_WL and free(t)],
                   key=lambda t:-elev(t)),8)
twi =spread(sorted([t for t in COAST if reg(t)=='Twilight Sea' and hil(t)<=1 and free(t)],
                   key=lambda t:-elev(t)),5)
mut('B-water','VEE_RelictDelta',grey,note='the Grey Sea is documented as shrinking - this is the shoreline it left')
mut('B-water','VEE_AlluvialFan',twi)
lmk('B-water','VEE_RelictDelta',grey,6); lmk('B-water','VEE_AlluvialFan',twi,4)

# ================================================================= C. ROADS
road=collections.defaultdict(dict)
for t in LINKS.values():
    for x in t['potentialRoads']:
        road[t['tile']][x['neighbor']]=x['def']; road[x['neighbor']][t['tile']]=x['def']
idx={t:{v:i for i,v in enumerate(NB[t])} for t in NB}
ORGANIC={'StoneRoad','DirtRoad','DirtPath'}
ok=lambda t: t in T and b(t) not in NOROAD and hil(t)<5 and t not in road and t not in SETT
straight=[]
for t,ns in road.items():
    if len(ns)!=2: continue
    a,c=list(ns)
    if road[t][a] not in ORGANIC or road[t][c] not in ORGANIC: continue
    ia,ic=idx[t].get(a),idx[t].get(c)
    if ia is None or ic is None: continue
    d=abs(ia-ic); d=min(d,len(NB[t])-d)
    if d==3: straight.append((t,a,c,ia))
random.shuffle(straight)
locked=set(); detours=[]
for t,a,c,ia in straight:
    if {t,a,c} & locked: continue
    n=len(NB[t]); best=None
    for step in (1,-1):
        if NB[t][(ia+3*step)%n]!=c: continue
        x=NB[t][(ia+step)%n]; y=NB[t][(ia+2*step)%n]
        if not (ok(x) and ok(y)): continue
        cost=abs(elev(x)-elev(t))+abs(elev(y)-elev(t))+40*(hil(x)+hil(y))
        if best is None or cost<best[0]: best=(cost,x,y)
    if not best: continue
    _,x,y=best
    detours.append(dict(t=t,a=a,c=c,x=x,y=y,d=road[t][a]))
    locked |= {t,a,c,x,y}
ops.append(dict(p='C-roads',kind='road_detour',items=detours,
                note='straight A-t-B replaced by A-x-y-B: one hex of bulge, 60deg steps. The Imperial highway is untouched.'))

# ================================================================= D. CLUSTERS
G={'VEE_SerpentineCanyons':lambda t:hil(t)>=4,'Cavern':lambda t:hil(t)>=4,
   'VEE_MeteorCrater':lambda t:hil(t)<=1 and t not in COAST and b(t) not in ('SeaIce','IceSheet'),
   'VEE_RockRidge':lambda t:hil(t)<=1 and t not in COAST and b(t) not in ('SeaIce','IceSheet','LavaField'),
   'VEE_JaggedRocks':lambda t:hil(t)<=1 and t not in COAST and b(t) not in ('SeaIce','IceSheet','LavaField'),
   'VEE_DustBowl':lambda t:t not in COAST,'DryLake':salt_ok,'VEE_SaltPlains':salt_ok,
   'VEE_Cenotes':lambda t:b(t) not in ('Desert','ExtremeDesert','AridShrubland'),
   'Chasm':lambda t:True,'Hollow':lambda t:True,'Stockpile':lambda t:True,
   'AncientRuins':lambda t:True,'AncientWarehouse':lambda t:True,'VEE_StagnantRivulet':lambda t:True}
FAM={'VEE_SerpentineCanyons':['VEE_JaggedRocks','Chasm'],'VEE_MeteorCrater':['VEE_DustBowl','VEE_RockRidge'],
     'DryLake':['VEE_SaltPlains','VEE_DustBowl'],'AncientRuins':['AncientWarehouse','Stockpile'],
     'VEE_Cenotes':['Hollow','VEE_StagnantRivulet'],'Cavern':['Chasm','VEE_RockRidge']}
for anchor,regions in (('VEE_SerpentineCanyons',['Gray Crags','South Crags','Twilight Crags']),
                       ('VEE_MeteorCrater',['Glare','Long Sand','Kiln']),
                       ('DryLake',['Salt','Dry Marches','Sinkground']),
                       ('AncientRuins',['Deadstone','Ashen Wastes','Scour']),
                       ('VEE_Cenotes',['Nightspill','Damp','Mould Marches']),
                       ('Cavern',['Rimewall','Frostcaps','Ashfall Range'])):
    for rn in regions:
        pool=[t for t in T if reg(t)==rn and G[anchor](t)]
        if not pool: continue
        seed=max(pool,key=lambda t:sum(1 for n_ in NB[t] if reg(n_)==rn))
        core=[seed]+[n_ for n_ in NB[seed] if n_ in T and reg(n_)==rn]
        ring2=[n2 for n_ in core for n2 in NB[n_] if n2 in T and reg(n2)==rn and n2 not in core]
        ring2=list(dict.fromkeys(ring2))
        mut('D-cluster',anchor,core,gate=G[anchor],cap=3,note='cluster anchor in '+rn)
        for d in FAM[anchor]:
            mut('D-cluster',d,core+ring2,gate=G.get(d),cap=4,note='cluster family in '+rn)
        sat=[t for t in ring2 if G[anchor](t) and free(t)]
        lmk('D-cluster',anchor,[seed]+spread(sat,4),3,note='a FAMILY of landmarks in '+rn+', not a lone pin')

# ================================================================= E. FIVE REGIONS
R=lambda n:[t for t in T if reg(t)==n]
sink=R('Sinkground')
mut('E-regions','VEE_Sinkholes',sink,gate=lambda t:hil(t)<=3,cap=60,note='Sinkground finally sinks')
qp=lambda t:b(t)=='Desert' and t not in COAST and not hasriver(t)
mut('E-regions','VEE_QuicksandPits',sink,gate=qp,cap=22)
lmk('E-regions','VEE_QuicksandPits',spread([t for t in sink if qp(t) and free(t)],6),4)
fan=R('Fanground')
mut('E-regions','VEE_DryRiver',sorted(fan,key=lambda t:-elev(t)),gate=dry_ok,cap=26,
    note='Fanground gets its fan - told with dry channels and salt, because VEE_AlluvialFan needs a coast and this is inland')
mut('E-regions','VEE_SaltPlains',sorted(fan,key=elev),gate=salt_ok,cap=16)
lmk('E-regions','DryLake',spread([t for t in sorted(fan,key=elev) if salt_ok(t) and free(t)],5),3)
gate_=R('Salt Gate')
mut('E-regions','RiverDelta',[t for t in gate_ if not hasroad(t)],cap=6,note='the delta at Salt Gate')
mut('E-regions','Marshy',gate_,cap=10)
deeps=R('Lantern Deeps'); core=sorted(deeps,key=lambda t:(-hil(t),-elev(t)))[:7]
ops.append(dict(p='E-regions',kind='tile_hilliness',tiles=core,value=4,
                note='the Deeps are made mountainous so a Cavern can legally exist in them'))
for t in core: T[t]['hilliness']='4'
mut('E-regions','UndergroundCave',deeps,cap=24)
mut('E-regions','MineralRich',core,displace=True,note='intentionally displaces the devoid pass in the Deeps')
lmk('E-regions','Cavern',core,4)
spore=R('Sporefields')
mut('E-regions','VEE_Mycelium',spore,cap=70)
myc=[t for t in spore if b(t)=='AB_MycoticJungle']
mut('E-regions','AB_MoldyEnvironment',myc[:100],cap=40)
mut('E-regions','AB_EdibleAirborneMicrofungi',myc[100:],cap=30)

# ================================================================= F. SARLACC + FLORA
flora=sorted([t for t in T if b(t) in TAT_WL and arc(t)<=95],key=lambda t:(arc(t),t))
mut('F-tatooine','WildTattooinePlants',flora,cap=1400,note='the dayside ground cover it should always have had')
deep=[t for t in T if reg(t) in ('Dune Sea','Long Sand','Glare','Kiln') and b(t) in ('Desert','ExtremeDesert')
      and not hasroad(t) and free(t) and hil(t)<=2]
pits=spread(deep,8,3)
lmk('F-tatooine','sw_Sarlacc',pits,5,note='far from every road, which is the point')
near=[t for t in deep if t not in pits and any(set(NB[t])&set(NB[p]) for p in pits)]
lmk('F-tatooine','sw_DeadSarlacc',spread(near,6),3,note='a dead one on the approach, as a warning')

json.dump(ops,open(A+'ops.json','w'),indent=0)
agg=collections.defaultdict(int)
for o in ops:
    if o['kind']=='mutator': agg[(o['p'],'mut  '+o['mutators'])]+=len(o['tiles'])
    elif o['kind']=='landmark': agg[(o['p'],'LMK  '+o['d'])]+=o['want']
    elif o['kind']=='road_detour': agg[(o['p'],'road detours')]+=len(o['items'])
    elif o['kind']=='tile_hilliness': agg[(o['p'],'hilliness -> Mountainous')]+=len(o['tiles'])
tot_m=sum(len(o['tiles']) for o in ops if o['kind']=='mutator')
tot_l=sum(o['want'] for o in ops if o['kind']=='landmark')
for k in sorted(agg): print("  %-11s %-34s %5d"%(k[0],k[1],agg[k]))
print("\n  %d channels traced · %d mutator writes · %d landmarks wanted · %d road detours"%(
      len(channels),tot_m,tot_l,sum(len(o['items']) for o in ops if o['kind']=='road_detour')))
