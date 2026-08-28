# -*- coding: utf-8 -*-
"""Same test, terrain confound removed: lay fertile Soil first, THEN order the Sow.
The first attempt targeted Sand (fertility 0) and ordered_job correctly reported
accepted:true / nowRunningRequested:false - the job was taken and could never run."""
import sys, json, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
LOG=r"D:\Luke\dev\Rimworld\world\_lf\j4sow2.log"
def P(*a):
    with io.open(LOG,"a",encoding="utf-8") as f: f.write(" ".join(str(x) for x in a)+"\n")
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=600); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
made=json.load(io.open(r"D:\Luke\dev\Rimworld\world\_lf\j45_pawns.json",encoding='utf-8'))
CELLS={'JAWA':(119,192),'BASELINER':(121,192)}
P("lay fertile soil ->", (c('jawa/set_terrain_batch',{'ops':'Soil:118,191,8,3'}).get('message') or '')[:90])
P("clear   ->", (c('jawa/destroy_batch',{'rects':'118,191,8,3'}).get('message') or '')[:90])
P("crop    ->", json.dumps(c('jawa/set_crop',{'plantDef':'Plant_Rice','x':119,'z':192}))[:150])
for tag,pid in made.items():
    X,Z=CELLS[tag]
    ci=c('rimworld/get_cell_info',{'x':X,'z':Z}).get('cell') or {}
    P("\n--- %s at %d,%d terrain=%s"%(tag,X,Z,ci.get('terrainDefName')))
    r=c('jawa/ordered_job',{'pawnId':pid,'jobDef':'Sow','targetAX':X,'targetAZ':Z,
                            'waitTicks':4000,'timeoutSeconds':180})
    P("   %s"%json.dumps({k:v for k,v in r.items() if k!='note'})[:260])
    P("   note: %s"%str(r.get('note'))[:200])
    ci=c('rimworld/get_cell_info',{'x':X,'z':Z}).get('cell') or {}
    P("   CELL AFTER: %s"%json.dumps([q.get('defName') for q in (ci.get('things') or [])]))
