# -*- coding: utf-8 -*-
import sys, json, os, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
P=json.load(open(os.path.join(A,'wither_plan.json'),encoding='utf-8'))
struct=P['struct']
got={}
for i in range(0,len(struct),60):
    r=b.call('jawa/world_mutators_get',{'tiles':','.join(map(str,struct[i:i+60])),'limit':200})
    for row in (r.get('tiles') or []): got[row['tile']]={'m':[x['def'] for x in row['mutators']],
                                                         'lm':row.get('landmark'),'b':row.get('biome')}
tg=b.call('jawa/world_tile_get',{'tiles':','.join(map(str,struct[:60])),'limit':80})
hil=collections.Counter(r.get('hilliness') for r in (tg.get('tiles') or []))
print("hilliness across the spine:", dict(hil))
allm=collections.Counter(d for v in got.values() for d in v['m'])
print("mutators now on the 48:", dict(allm.most_common(12)))
BAD={'TerraformingScar','Mountain','Cliffs','VEE_SaltPlains','DryGround','VEE_RotstinkVents','Stockpile'}
left={d:n for d,n in allm.items() if d in BAD}
print("anything that should have been stripped still present:", left or "NONE")
MOUNT={'VEE_SerpentineCanyons','Chasm','Cavern','Hollow'}
bad=[t_ for t_,v in got.items() if len(set(v['m'])&MOUNT)!=1]
print("tiles without exactly one canyon def: %d %s"%(len(bad),bad[:6]))
print("landmarks on the spine:", collections.Counter(v['lm'] for v in got.values() if v['lm']))
print("example tile 830:", got.get(830))
