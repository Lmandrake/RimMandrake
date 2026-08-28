# -*- coding: utf-8 -*-
"""ATTRIBUTED: order the JAWA specifically to sow one named cell, and watch that cell.
14 rice appeared in the zone but three other colonists share the Growing work type, so the
zone census cannot say who sowed them. A player-ordered job can."""
import sys, json, io, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
LOG=r"D:\Luke\dev\Rimworld\world\_lf\j4sow.log"
def P(*a):
    with io.open(LOG,"a",encoding="utf-8") as f: f.write(" ".join(str(x) for x in a)+"\n")
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=600); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
made=json.load(io.open(r"D:\Luke\dev\Rimworld\world\_lf\j45_pawns.json",encoding='utf-8'))
# find an EMPTY, fertile-looking cell inside the zone
target=None
for x in range(118,128):
    for z in range(186,194):
        ci=c('rimworld/get_cell_info',{'x':x,'z':z}).get('cell') or {}
        if not ci: continue
        if (ci.get('solidThingDefs') or []): continue
        if 'Basalt' in str(ci.get('terrainDefName')): continue
        target=(x,z,ci.get('terrainDefName')); break
    if target: break
P("target cell:", target)
if not target: P("no empty non-basalt cell in the zone"); raise SystemExit
X,Z,terr=target
for tag,pid in made.items():
    P("\n--- %s (%s)"%(tag,pid))
    r=c('jawa/ordered_job',{'pawnId':pid,'jobDef':'Sow','targetAX':X,'targetAZ':Z,
                            'waitTicks':2500,'timeoutSeconds':120})
    P("   ordered_job Sow at %d,%d -> %s"%(X,Z,json.dumps({k:v for k,v in r.items()})[:300]))
    ci=c('rimworld/get_cell_info',{'x':X,'z':Z}).get('cell') or {}
    P("   cell after: terrain=%s things=%s"%(ci.get('terrainDefName'),
        json.dumps([q.get('defName') for q in (ci.get('things') or [])])[:120]))
    # clear it again so the next subject starts from the same place
    c('jawa/destroy_batch',{'rects':'%d,%d,1,1'%(X,Z)})
