# -*- coding: utf-8 -*-
"""set_time_speed does not tick. step_game_ticks does. Drive the heat wave with the one that works."""
import sys, json, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
LOG=r"D:\Luke\dev\Rimworld\world\_lf\heatrun2.log"
def w(s):
    with io.open(LOG,"a",encoding="utf-8") as f: f.write(s+"\n")
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=600); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
w("cond -> %s"%json.dumps(c('jawa/game_condition',{'action':'start','condition':'HeatWave',
                                                  'durationTicks':400000}))[:150])
for i in range(20):
    s=c('rimworld/step_game_ticks',{'ticks':3000,'timeoutMs':300000})
    gi=c('rimworld/get_game_info')
    ti=c('jawa/cell_temperature',{'cell':'103,205'})
    rg=c('jawa/room_get',{'rect':'100,200,18,10'})
    rooms=[(q.get('role'), round(q.get('temperature') or 0,1))
           for q in (rg.get('rooms') or []) if (q.get('cellCount') or 0)>1]
    w("t=%s step=%s outdoor=%.1f indoor=%.1f rooms=%s"%(
        gi.get('ticksGame'), s.get('status'), ti.get('outdoorTemp') or 0,
        ti.get('temperature') or 0, rooms))
    if (ti.get('outdoorTemp') or 0) > 33:
        w("OUTDOOR PAST 33 - the criterion is now testable"); break
w("done")
