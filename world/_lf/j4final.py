# -*- coding: utf-8 -*-
"""CLEAN ATTRIBUTION. Every other colonist DRAFTED (a drafted pawn takes no work), so the
only pair of hands that can sow is the Jawa. Then order it and watch one named cell."""
import sys, json, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
LOG=r"D:\Luke\dev\Rimworld\world\_lf\j4final.log"
def P(*a):
    with io.open(LOG,"a",encoding="utf-8") as f: f.write(" ".join(str(x) for x in a)+"\n")
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=600); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
made=json.load(io.open(r"D:\Luke\dev\Rimworld\world\_lf\j45_pawns.json",encoding='utf-8'))
JAWA=made['JAWA']
cols=c('rimworld/list_colonists',{}).get('colonists') or []
others=[q for q in cols if q.get('pawnId')!='Thing_'+JAWA]
P("drafting %d other colonists so only the Jawa can work:"%len(others))
for q in others:
    r=c('jawa/set_draft',{'pawnId':q['pawnId'].replace('Thing_',''),'drafted':True})
    P("   %-14s draft -> %s %s"%(q.get('name'), r.get('success'), (r.get('message') or '')[:60]))
X,Z=124,192
c('jawa/set_terrain_batch',{'ops':'Soil:%d,%d,3,3'%(X-1,Z-1)})
c('jawa/destroy_batch',{'rects':'%d,%d,3,3'%(X-1,Z-1)})
ci=c('rimworld/get_cell_info',{'x':X,'z':Z}).get('cell') or {}
P("\nvirgin target %d,%d terrain=%s things=%s"%(X,Z,ci.get('terrainDefName'),
   [q.get('defName') for q in (ci.get('things') or [])]))
r=c('jawa/ordered_job',{'pawnId':JAWA,'jobDef':'Sow','targetAX':X,'targetAZ':Z,'waitTicks':0})
P("order -> accepted=%s after=%s"%(r.get('accepted'), r.get('afterJobDef')))
for k in range(14):
    c('rimworld/step_game_ticks',{'ticks':500,'timeoutMs':300000})
    cols=c('rimworld/list_colonists',{}).get('colonists') or []
    hit=next((q for q in cols if q.get('pawnId')=='Thing_'+JAWA), None)
    ci=c('rimworld/get_cell_info',{'x':X,'z':Z}).get('cell') or {}
    things=[q.get('defName') for q in (ci.get('things') or [])]
    P("  +%5d job=%-20s cell=%s"%((k+1)*500, (hit or {}).get('job'), things))
    if 'Plant_Rice' in things:
        P("  >>> THE JAWA SOWED IT. Every other colonist was drafted and could not."); break
else:
    P("  >>> no rice after 7000 ticks with only the Jawa able to work.")
P("\nundrafting:")
for q in others:
    c('jawa/set_draft',{'pawnId':q['pawnId'].replace('Thing_',''),'drafted':False})
P("   done")
