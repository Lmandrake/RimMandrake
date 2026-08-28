# -*- coding: utf-8 -*-
"""JAWA leg redone. The last run aborted on a FALSE POSITIVE: wild Plant_YellowTallGrass
grew in the target cell and my 'if things' break fired on it. Check for Plant_Rice by name."""
import sys, json, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
LOG=r"D:\Luke\dev\Rimworld\world\_lf\j4sow4.log"
def P(*a):
    with io.open(LOG,"a",encoding="utf-8") as f: f.write(" ".join(str(x) for x in a)+"\n")
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=600); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
made=json.load(io.open(r"D:\Luke\dev\Rimworld\world\_lf\j45_pawns.json",encoding='utf-8'))
pid=made['JAWA']; X,Z=119,192
c('jawa/destroy_batch',{'rects':'%d,%d,3,3'%(X-1,Z-1)})
ci=c('rimworld/get_cell_info',{'x':X,'z':Z}).get('cell') or {}
P("JAWA target %d,%d terrain=%s things=%s"%(X,Z,ci.get('terrainDefName'),
   [q.get('defName') for q in (ci.get('things') or [])]))
r=c('jawa/ordered_job',{'pawnId':pid,'jobDef':'Sow','targetAX':X,'targetAZ':Z,'waitTicks':0})
P("order -> accepted=%s after=%s"%(r.get('accepted'), r.get('afterJobDef')))
sowJobSeen=False
for k in range(12):
    c('rimworld/step_game_ticks',{'ticks':700,'timeoutMs':300000})
    cols=c('rimworld/list_colonists',{}).get('colonists') or []
    hit=next((q for q in cols if q.get('pawnId')=='Thing_'+pid), None)
    job=(hit or {}).get('job')
    if job=='Sow': sowJobSeen=True
    ci=c('rimworld/get_cell_info',{'x':X,'z':Z}).get('cell') or {}
    things=[q.get('defName') for q in (ci.get('things') or [])]
    P("  +%5d  job=%-22s cell=%s"%((k+1)*700, job, things))
    if 'Plant_Rice' in things:
        P("  >>> Plant_Rice PRESENT - the Jawa sowed it (Sow job seen: %s)"%sowJobSeen); break
else:
    P("  >>> NO Plant_Rice after 8400 ticks. Sow job ever seen: %s"%sowJobSeen)
