# -*- coding: utf-8 -*-
"""HeatWave ramps over its own duration, so a 400k-tick one barely moves in 3k ticks.
Short duration = steep ramp. Restart it short and step into the peak."""
import sys, json, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
LOG=r"D:\Luke\dev\Rimworld\world\_lf\heat3.log"
def w(s):
    with io.open(LOG,"a",encoding="utf-8") as f: f.write(s+"\n")
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=600); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
c('jawa/game_condition',{'action':'end','condition':'HeatWave'})
w("restart short -> %s"%json.dumps(c('jawa/game_condition',{'action':'start','condition':'HeatWave',
                                                            'durationTicks':12000}))[:170])
for i in range(12):
    s=c('rimworld/step_game_ticks',{'ticks':1200,'timeoutMs':300000})
    ti=c('jawa/cell_temperature',{'cell':'103,205'})
    rg=c('jawa/room_get',{'rect':'100,200,18,10'})
    rooms=[(q.get('role'), round(q.get('temperature') or 0,1))
           for q in (rg.get('rooms') or []) if (q.get('cellCount') or 0)>1]
    w("t=%s outdoor=%.1f indoor=%.1f rooms=%s"%(
        c('rimworld/get_game_info').get('ticksGame'), ti.get('outdoorTemp') or 0,
        ti.get('temperature') or 0, rooms))
    if (ti.get('outdoorTemp') or 0) > 33: w("PEAK REACHED"); break
w("done")
