# -*- coding: utf-8 -*-
"""T3, done as a MECHANISM test rather than a biome tour.

The item wants an unclothed pawn to take hypothermia on a -59.8 C biome and NOT overheat on a
+48.2 C one. There is no bridge route to a map on a chosen tile, so instead: strip a Jawa and a
Baseliner, drive the ambient down with a ColdSnap, and watch which one breaks first. Their
measured comfyMin differ by exactly 10 C (-50 vs -40), so the Baseliner must go first or the
whole tolerance system is not doing what the stats say."""
import sys, json, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
LOG=r"D:\Luke\dev\Rimworld\world\_lf\cold.log"
def P(*a):
    with io.open(LOG,"a",encoding="utf-8") as f: f.write(" ".join(str(x) for x in a)+"\n")
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=600); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
subj={}
for i,(xeno,tag) in enumerate((('MandrakeJawa','JAWA'),('Baseliner','BASELINER'))):
    r=c('jawa/spawn_pawn',{'kindDef':'Colonist','x':150+i*2,'z':150,'faction':'none',
                           'count':1,'xenotype':xeno})
    pid=(r.get('pawns') or [{}])[0].get('id')
    if not pid: P(tag,"spawn failed"); continue
    c('jawa/pawn_gear',{'pawn':pid,'action':'clear','clearWhat':'apparel'})
    s=c('jawa/pawn_stats',{'pawn':pid,'stats':'ComfyTemperatureMin,ComfyTemperatureMax'})
    v={q['defName']:q['value'] for q in (s.get('stats') or [])}
    subj[tag]=pid
    P("%-10s %s stripped, comfy %.1f .. %.1f"%(tag,pid,v.get('ComfyTemperatureMin') or 0,
                                               v.get('ComfyTemperatureMax') or 0))
P("\ncold snap ->", json.dumps(c('jawa/game_condition',{'action':'start','condition':'ColdSnap',
                                                        'durationTicks':15000}))[:130])
def hed(pid):
    d=c('jawa/pawn_get',{'pawn':pid})
    pw=d.get('pawns')[0] if isinstance(d.get('pawns'),list) and d.get('pawns') else d
    return [(q.get('def'), round(q.get('severity') or 0,3)) for q in (pw.get('hediffs') or [])
            if 'ypotherm' in str(q.get('def')) or 'eatstroke' in str(q.get('def'))]
for k in range(14):
    c('rimworld/step_game_ticks',{'ticks':1000,'timeoutMs':300000})
    ct=c('jawa/cell_temperature',{'cell':'150,150'})
    line=["outdoor=%.1f"%(ct.get('outdoorTemp') or 0)]
    for tag,pid in subj.items(): line.append("%s=%s"%(tag, hed(pid) or "-"))
    P("  +%5d  %s"%((k+1)*1000, "   ".join(line)))
P("\nend condition ->", c('jawa/game_condition',{'action':'end','condition':'ColdSnap'}).get('success'))
