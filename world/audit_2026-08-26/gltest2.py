# -*- coding: utf-8 -*-
import sys, json, os, csv
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
A=r"D:\Luke\dev\Rimworld\world\_audit"
h,p,t=rc.resolve_endpoint(); b=rc.RimBridge(host=h,port=p,token=t); b.connect()
F={int(q['tile']):q for q in csv.DictReader(open(os.path.join(A,'final_tiles.csv'),encoding='utf-8'))}
MUT={q['tile']:[m['def'] for m in q['mutators']]
     for q in json.load(open(os.path.join(A,'final_mutators.json'),encoding='utf-8'))}
def read(tile):
    r=b.call('jawa/world_mutators_get',{'tiles':str(tile),'limit':5})
    rows=r.get('tiles') or []
    return [m['def'] for m in rows[0]['mutators']] if rows else None
# pick a tile that ALREADY has mutators, so an empty readback cannot be a reading artefact
tile=[t for t in MUT if len(MUT[t])>=2 and F[t]['hilliness']=='Mountainous'][0]
print("control tile %d  %s %s"%(tile,F[tile]['biome'],F[tile]['hilliness']))
print("  before:", read(tile))
for d in ('GL_Caldera','GL_Canyon','GL_Sinkhole','VEE_JaggedRocks'):
    w=b.call('jawa/world_mutators_set',{'action':'add','mutators':d,'tiles':str(tile),'readBack':0})
    after=read(tile)
    landed = after is not None and d in after
    print("  add %-16s success=%s added=%s  ->  present after: %s"%(d,w.get('success'),w.get('added'),landed))
    if landed:
        b.call('jawa/world_mutators_set',{'action':'remove','mutators':d,'tiles':str(tile),'readBack':0})
print("  final:", read(tile))
