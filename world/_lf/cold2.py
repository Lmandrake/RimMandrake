# -*- coding: utf-8 -*-
"""T3 via the WORLD TILE. A ColdSnap on a temperate map bottoms out around -10 and can never
reach a Jawa's comfyMin of -50. The map's temperature comes from its world tile, so set the
tile instead. The map is on tile 18393 - found as the player Settlement in world_objects_get,
because NO tool reports the current map's tile directly."""
import sys, json, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
LOG=r"D:\Luke\dev\Rimworld\world\_lf\cold2.log"
def P(*a):
    with io.open(LOG,"a",encoding="utf-8") as f: f.write(" ".join(str(x) for x in a)+"\n")
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=600); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
TILE=18393
P("tile before ->", json.dumps(c('jawa/world_tile_get',{'tiles':str(TILE)}))[:260])
P("set -60     ->", json.dumps(c('jawa/world_tile_set',{'tiles':str(TILE),'temperature':-60,'readBack':1}))[:260])
P("commit      ->", c('jawa/world_commit',{}).get('success'))
subj={}
for i,(xeno,tag) in enumerate((('MandrakeJawa','JAWA'),('Baseliner','BASELINER'))):
    r=c('jawa/spawn_pawn',{'kindDef':'Colonist','x':160+i*2,'z':160,'faction':'none','count':1,'xenotype':xeno})
    pid=(r.get('pawns') or [{}])[0].get('id')
    if not pid: P(tag,"spawn failed"); continue
    c('jawa/pawn_gear',{'pawn':pid,'action':'clear','clearWhat':'apparel'})
    subj[tag]=pid
P("subjects:", subj)
def hed(pid):
    d=c('jawa/pawn_get',{'pawn':pid})
    pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
    return [(q.get('def'), round(q.get('severity') or 0,3)) for q in (pw.get('hediffs') or [])
            if re.search('ypotherm|eatstroke|rostbite', str(q.get('def')))] if False else \
           [(q.get('def'), round(q.get('severity') or 0,3)) for q in (pw.get('hediffs') or [])
            if any(s in str(q.get('def')) for s in ('ypotherm','eatstroke','rostbite'))]
import re
for k in range(16):
    c('rimworld/step_game_ticks',{'ticks':1000,'timeoutMs':300000})
    ct=c('jawa/cell_temperature',{'cell':'160,160'})
    line=["out=%.1f seasonal=%.1f"%(ct.get('outdoorTemp') or 0, ct.get('seasonalTemp') or 0)]
    for tag,pid in subj.items(): line.append("%s=%s"%(tag, hed(pid) or "-"))
    P("  +%5d  %s"%((k+1)*1000, "   ".join(line)))
