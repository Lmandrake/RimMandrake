# -*- coding: utf-8 -*-
"""J4 behaviourally, done right: needs topped up so they WILL work, and jobs read from
rimworld/list_colonists because jawa/list_pawns' job field is always null."""
import sys, json, io, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
LOG=r"D:\Luke\dev\Rimworld\world\_lf\j45c.log"
def P(*a):
    with io.open(LOG,"a",encoding="utf-8") as f: f.write(" ".join(str(x) for x in a)+"\n")
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=600); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
made=json.load(io.open(r"D:\Luke\dev\Rimworld\world\_lf\j45_pawns.json",encoding='utf-8'))
NAMES={}
for tag,pid in made.items():
    d=c('jawa/pawn_get',{'pawn':pid})
    pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
    NAMES[tag]=pw.get('name'); P(tag,"=",pw.get('name'),pid)
    for need,val in (('Rest',0.95),('Food',0.95),('Joy',0.9)):
        r=c('jawa/pawn_need',{'pawn':pid,'need':need,'level':val})
        P("   need %-5s -> %s %s"%(need, r.get('success'), (r.get('message') or '')[:60]))
    # everything except plant work OFF, so the only thing on offer is the rice
    for wt in ('Growing','PlantCutting'):
        c('jawa/set_work_priority',{'pawnId':pid,'workType':wt,'priority':1})
    for wt in ('Hauling','Cleaning','Construction','Mining','Cooking','Doctor','Warden','Research','Crafting','Smithing','Tailoring','Art','Hunting','Firefighter','Patient','BasicWorker','PlantCutting_'):
        c('jawa/set_work_priority',{'pawnId':pid,'workType':wt,'priority':0})
P("")
seen=collections.defaultdict(collections.Counter)
for i in range(10):
    c('rimworld/step_game_ticks',{'ticks':1200,'timeoutMs':300000})
    cols=c('rimworld/list_colonists',{}).get('colonists') or []
    line=[]
    for tag in made:
        want=str(NAMES[tag])
        hit=next((q for q in cols
                  if q.get('pawnId')=='Thing_'+made[tag]
                  or str(q.get('fullName') or '')==want
                  or (q.get('name') and q['name'] in want)), None)
        j=(hit or {}).get('job')
        seen[tag][str(j)]+=1; line.append("%s=%s"%(tag,j))
    P("  step %-2d %s"%(i+1, "   ".join(line)))
P("")
for tag in made: P("  %-10s jobs seen: %s"%(tag, dict(seen[tag])))
# and did any rice actually appear?
r=c('jawa/list_things',{'rect':'118,186,10,8','limit':400})
things=collections.Counter((x.get('def') or x.get('defName')) for x in (r.get('things') or []))
P("  things in the growing zone:", dict(things))
