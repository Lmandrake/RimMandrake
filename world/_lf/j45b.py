# -*- coding: utf-8 -*-
"""J4 behaviourally: put a rice zone in front of a Jawa and a Baseliner and see who sows."""
import sys, json, io, collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=600); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
made=json.load(io.open(r"D:\Luke\dev\Rimworld\world\_lf\j45_pawns.json",encoding='utf-8'))
import io as _io
LOG=r"D:\Luke\dev\Rimworld\world\_lf\j45b.log"
def P(*a):
    s=" ".join(str(x) for x in a)
    with _io.open(LOG,"a",encoding="utf-8") as f: f.write(s+"\n")
P("pawns:", made)
P("clear the ground ->", (c('jawa/destroy_batch',{'rects':'118,186,10,8'}).get('message') or '')[:80])
z=c('jawa/map_zones',{'action':'createZone','zoneType':'growing','rect':'118,186,10,8'})
P("createZone ->", z.get('success'), (z.get('message') or json.dumps(z))[:150])
zid = z.get('zone') or z.get('zoneId') or (z.get('zones') or [{}])[0].get('id') if isinstance(z.get('zones'),list) else z.get('zone')
sc=c('jawa/set_crop',{'plantDef':'Plant_Rice','x':120,'z':188})
P("set_crop  ->", sc.get('success'), (sc.get('message') or json.dumps(sc))[:150])
for tag,pid in made.items():
    for wt in ('Growing','PlantCutting'):
        r=c('jawa/set_work_priority',{'pawnId':pid,'workType':wt,'priority':1})
        P("  %-10s %-13s -> %s %s"%(tag,wt,r.get('success'),(r.get('message') or '')[:70]))
P()
seen=collections.defaultdict(collections.Counter)
for i in range(8):
    c('rimworld/step_game_ticks',{'ticks':900,'timeoutMs':300000})
    ps={x['id']:x for x in (c('jawa/list_pawns',{'limit':400}).get('pawns') or [])}
    line=[]
    for tag,pid in made.items():
        j=(ps.get(pid) or {}).get('job')
        seen[tag][str(j)]+=1
        line.append("%s=%s"%(tag,j))
    P("  step %d  %s"%(i+1, "  ".join(line)))
P()
for tag in made: print("  %-10s jobs seen: %s"%(tag, dict(seen[tag])))
