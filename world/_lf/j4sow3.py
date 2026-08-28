# -*- coding: utf-8 -*-
"""Third attempt, and the two confounds are now named:
  1. Sand has fertility 0 - the first target could never grow rice.
  2. ordered_job's waitTicks is meaningless on a PAUSED game: ticksElapsed came back 0.
     The job is enqueued and simply never runs, because no ticks pass.
So: fertile Soil, order the job, then STEP THE CLOCK ourselves, then read the cell."""
import sys, json, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
LOG=r"D:\Luke\dev\Rimworld\world\_lf\j4sow3.log"
def P(*a):
    with io.open(LOG,"a",encoding="utf-8") as f: f.write(" ".join(str(x) for x in a)+"\n")
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=600); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
made=json.load(io.open(r"D:\Luke\dev\Rimworld\world\_lf\j45_pawns.json",encoding='utf-8'))
CELLS={'JAWA':(119,192),'BASELINER':(121,192)}
for tag,pid in made.items():
    X,Z=CELLS[tag]
    c('jawa/destroy_batch',{'rects':'%d,%d,1,1'%(X,Z)})
    ci=c('rimworld/get_cell_info',{'x':X,'z':Z}).get('cell') or {}
    P("\n--- %s at %d,%d terrain=%s empty=%s"%(tag,X,Z,ci.get('terrainDefName'),
      not (ci.get('things') or [])))
    r=c('jawa/ordered_job',{'pawnId':pid,'jobDef':'Sow','targetAX':X,'targetAZ':Z,'waitTicks':0})
    P("   order -> accepted=%s after=%s"%(r.get('accepted'), r.get('afterJobDef')))
    for k in range(6):
        c('rimworld/step_game_ticks',{'ticks':700,'timeoutMs':300000})
        cols=c('rimworld/list_colonists',{}).get('colonists') or []
        hit=next((q for q in cols if q.get('pawnId')=='Thing_'+pid), None)
        ci=c('rimworld/get_cell_info',{'x':X,'z':Z}).get('cell') or {}
        things=[q.get('defName') for q in (ci.get('things') or [])]
        P("   +%4d ticks  job=%-20s cell=%s"%((k+1)*700, (hit or {}).get('job'), things))
        if things: P("   SOWN by %s"%tag); break
