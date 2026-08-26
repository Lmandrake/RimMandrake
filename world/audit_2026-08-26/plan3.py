# -*- coding: utf-8 -*-
"""Scars, cenote relocation, Wither canyons, Rust Cathedral interior, buried things."""
import csv, json, collections, random
A='world/_audit/'
T={int(r['tile']):r for r in csv.DictReader(open(A+'now_tiles.csv',encoding='utf-8'))}
REG={int(r['tile']):r['region'] for r in csv.DictReader(open(A+'LIVE_tiles.csv',encoding='utf-8'))}
NB={int(r['tile']):[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0]
    for r in csv.DictReader(open(A+'neighbors.csv',encoding='utf-8'))}
MUT={t['tile']:{m['def'] for m in t['mutators']} for t in json.load(open(A+'now_mutators.json',encoding='utf-8'))}
LMK={x['tile']:x['def'] for x in json.load(open(A+'now_landmarks.json',encoding='utf-8'))}
SETT={o['tile'] for o in json.load(open(A+'objects.json',encoding='utf-8'))['objects']}
R=json.load(open(A+'roster.json',encoding='utf-8'))
M={x['defName']:x['fields'] for x in R if x['defType']=='TileMutatorDef'}
LDEF={x['defName'] for x in R if x['defType']=='LandmarkDef'}
CAT=json.load(open(A+'mut_categories.json',encoding='utf-8'))
HIL={'Flat':1,'SmallHills':2,'LargeHills':3,'Mountainous':4,'Impassable':5}
bi=lambda t:T[t]['biome']; hv=lambda t:HIL.get(T[t]['hilliness'],0)
random.seed(11)
ops=[]
def legal(d,t):
    f=M.get(d) or {}
    w=set(f.get('biomeWhitelistSet') or []); bl=set(f.get('biomeBlacklistSet') or [])
    if w and bi(t) not in w: return False
    if bi(t) in bl: return False
    mn=HIL.get(f.get('minHilliness','Undefined'),0); mx=HIL.get(f.get('maxHilliness','Undefined'),0)
    if mn and hv(t)<mn: return False
    if mx and hv(t)>mx: return False
    return True
def collides(t,d):
    cs=set(CAT.get(d) or ())
    if not cs: return False
    return any(m!=d and cs & set(CAT.get(m) or ()) for m in MUT.get(t,()))
def add(p,d,tiles,note=''):
    out=[t for t in tiles if d not in MUT.get(t,()) and legal(d,t) and not collides(t,d)]
    if out:
        ops.append(dict(p=p,kind='mut',action='add',d=d,tiles=sorted(set(out)),note=note))
        for t in out: MUT.setdefault(t,set()).add(d)
    return out
def rm(p,d,tiles,note=''):
    out=[t for t in tiles if d in MUT.get(t,())]
    if out:
        ops.append(dict(p=p,kind='mut',action='remove',d=d,tiles=sorted(set(out)),note=note))
        for t in out: MUT[t].discard(d)
    return out
def lmk(p,d,cands,want,note=''):
    if d not in LDEF: return
    c=[t for t in cands if t not in LMK and t not in SETT]
    if c: ops.append(dict(p=p,kind='lmk',d=d,candidates=c[:want*6],want=want,note=note))
def rmlmk(p,tiles,note=''):
    t2=[t for t in tiles if t in LMK]
    if t2: ops.append(dict(p=p,kind='lmk_remove',tiles=sorted(t2),note=note))
def chain(start, ok, n):
    """walk a wandering line of adjacent tiles that satisfy ok()"""
    path=[start]; seen={start}; cur=start
    while len(path)<n:
        nxt=[x for x in NB[cur] if x not in seen and ok(x)]
        if not nxt: break
        cur=random.choice(nxt); path.append(cur); seen.add(cur)
    return path

# ---------------- P1  CENOTES: get them off bare rock, put them in the wet dark
BAD_CENOTE={'AridShrubland','AB_RockyCrags','AB_TarPits','ZBiome_Badlands','Desert','ExtremeDesert'}
bad=[t for t,ds in MUT.items() if 'VEE_Cenotes' in ds and bi(t) in BAD_CENOTE]
badlm=[t for t,d in LMK.items() if d=='VEE_Cenotes' and bi(t) in BAD_CENOTE]
rmlmk('P1-cenotes',badlm,'cenotes on bare rock / tar / arid ground')
rm('P1-cenotes','VEE_Cenotes',bad,'a cenote is a flooded limestone sinkhole; it does not belong on crags or tar')
VEG={'AB_MycoticJungle','BMT_FungalForest','PoisonForest','BiomeCypreJungle','AB_OcularForest'}
for rn,k in (('Sweatwood',7),('Stepwood',7),('Hanging Wood',9),('Blindwood',8),
             ('Ashwood',6),('Capwood',6),('Slough',7),('Frostcaps',9),('Mould Marches',6)):
    pool=[t for t in T if REG.get(t)==rn and bi(t) in VEG and legal('VEE_Cenotes',t) and t not in SETT]
    if not pool: continue
    seed=max(pool,key=lambda t:sum(1 for n in NB[t] if REG.get(n)==rn))
    ch=chain(seed, lambda x: REG.get(x)==rn and bi(x) in VEG and legal('VEE_Cenotes',x) and x not in SETT, k)
    add('P1-cenotes','VEE_Cenotes',ch,'karst chain in '+rn)
    lmk('P1-cenotes','VEE_Cenotes',[ch[0]]+ch[3:],1,'cenote field in '+rn)

# ---------------- P2  NIGHTSIDE SCAR CHAINS
scar_ok=lambda x: legal('TerraformingScar',x) and x not in SETT and 'TerraformingScar' not in MUT.get(x,())
NIGHT=[('Umbra',4,9),('Ammonia Flats',4,9),('Deadstone',3,8),('Cinderdark',2,7),
       ('Ashen Wastes',2,8),('Scour',2,7),('Sunreach',3,9),('Nightspill',3,8)]
for rn,count,ln in NIGHT:
    pool=[t for t in T if REG.get(t)==rn and scar_ok(t)]
    if not pool: continue
    seeds=[]
    for t in sorted(pool,key=lambda x:-sum(1 for n in NB[x] if REG.get(n)==rn)):
        if len(seeds)>=count: break
        if all(s not in NB[t] and not (set(NB[t])&set(NB[s])) for s in seeds): seeds.append(t)
    for s in seeds:
        ch=chain(s, lambda x: REG.get(x)==rn and scar_ok(x), ln)
        if len(ch)>=4:
            add('P2-nightscars','TerraformingScar',ch,'scar chain across '+rn)
            lmk('P2-nightscars','TerraformingScar',[ch[len(ch)//2]],1,'the chain head in '+rn)

# ---------------- P3  WITHER + THE FORSAKEN CRAGS: canyon shapes
for rn in ('Wither','The Verge','South Crags','Scour'):
    pool=[t for t in T if REG.get(t)==rn and scar_ok(t)]
    if pool:
        seed=max(pool,key=lambda t:hv(t))
        ch=chain(seed, lambda x: REG.get(x)==rn and scar_ok(x), 11)
        add('P3-wither','TerraformingScar',ch,'a torn canyon line through '+rn)
        lmk('P3-wither','TerraformingScar',[ch[0],ch[-1]],1,'canyon mouth in '+rn)
    high=[t for t in T if REG.get(t)==rn and hv(t)>=4 and t not in SETT]
    add('P3-wither','VEE_SerpentineCanyons',high[:6],'real canyons where the ground is high enough, '+rn)
    lmk('P3-wither','VEE_SerpentineCanyons',high,2,'canyon system in '+rn)
    add('P3-wither','Chasm',[t for t in high if 'VEE_SerpentineCanyons' not in MUT.get(t,())][:4],'chasms in '+rn)

# ---------------- P4  RUST CATHEDRAL: give the lozenge an interior
rc=[t for t in T if REG.get(t)=='Rust Cathedral']
cen=max(rc,key=lambda t:sum(1 for n in NB[t] if REG.get(n)=='Rust Cathedral'))
ring1=[n for n in NB[cen] if REG.get(n)=='Rust Cathedral']
ring2=list(dict.fromkeys([m for n in ring1 for m in NB[n] if REG.get(m)=='Rust Cathedral' and m!=cen and m not in ring1]))
outer=[t for t in rc if t not in ring1 and t not in ring2 and t!=cen]
add('P4-cathedral','AB_DerelictArchonexus',[cen],'the core')
add('P4-cathedral','AncientUplink',ring1[:3],'uplinks around the core')
add('P4-cathedral','VEE_MineableComponentSpacer',ring1[3:]+ring2[:12],'the works: advanced components in the ground')
add('P4-cathedral','AB_DerelictBioLab',(ring2[12:]+outer[28:36])[:6],'derelict bio labs')
add('P4-cathedral','VEE_MechanoidShipChunks',outer[:18],'wreckage trailing out')
add('P4-cathedral','VEE_DeadlifeVents',outer[18:24],'deadlife venting at the edge')
add('P4-cathedral','VEE_ContaminatedReservoir',outer[24:28],'poisoned water on the approach')
appro=[t for t in outer if any(REG.get(n)!='Rust Cathedral' for n in NB[t])]
add('P4-cathedral','TerraformingScar',appro[:14],'scarred approach to the Cathedral')
for d,w in (('AB_DerelictArchonexus',1),('AncientUplink',2),('VEE_ContaminatedReservoir',2),('TerraformingScar',3)):
    lmk('P4-cathedral',d,[cen]+ring1+ring2+outer[:40],w,'Cathedral: '+d)

# ---------------- P5  THE BURIED THINGS, where they are legal
for d,regs,k in (('AB_DerelictKemeticTemple',['Dry Marches','Long Sand','Combs'],5),
                 ('AB_GiantFossils',['Dune Sea','Long Sand','Kiln'],7),
                 ('AncientToxVent',['Scorch','Cinders','Ashfall Range'],4),
                 ('AncientSmokeVent',['Scorch','Cinders','Fall Line'],4),
                 ('VEE_MineableComponentSpacer',['The Abandoned Mines','Glass Reach'],6),
                 ('VEE_DeadlifeVents',['Ashen Wastes','Cinderdark'],4)):
    pool=[t for t in T if REG.get(t) in regs and legal(d,t) and t not in SETT]
    picked=[]
    for t in pool:
        if len(picked)>=k: break
        if all(t not in NB[o] for o in picked): picked.append(t)
    add('P5-buried',d,picked,'%s in %s'%(d,'/'.join(regs)))
    lmk('P5-buried',d,picked,max(1,k//2),d+' as a named place')

json.dump(ops,open(A+'ops3.json','w'),indent=0)
agg=collections.defaultdict(int)
for o in ops:
    if o['kind']=='mut': agg[(o['p'],('add  ' if o['action']=='add' else 'REMOVE ')+o['d'])]+=len(o['tiles'])
    elif o['kind']=='lmk': agg[(o['p'],'LMK  '+o['d'])]+=o['want']
    elif o['kind']=='lmk_remove': agg[(o['p'],'LMK REMOVE')]+=len(o['tiles'])
for k in sorted(agg): print("  %-14s %-38s %4d"%(k[0],k[1],agg[k]))
print("\n  mutator writes %d · landmarks wanted %d · ops %d"%(
    sum(len(o['tiles']) for o in ops if o['kind']=='mut'),
    sum(o['want'] for o in ops if o['kind']=='lmk'), len(ops)))
