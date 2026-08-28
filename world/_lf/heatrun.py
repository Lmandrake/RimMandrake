# -*- coding: utf-8 -*-
"""Let the heat wave develop, then RE-PAUSE. Writes progress to a log so nothing blocks."""
import sys, json, io, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
LOG=r"D:\Luke\dev\Rimworld\world\_lf\heatrun.log"
def w(s):
    with io.open(LOG,"a",encoding="utf-8") as f: f.write(s+"\n")
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=240); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
w("start ticks=%s"%c('rimworld/get_game_info').get('ticksGame'))
w("speed-> %s"%json.dumps(c('rimworld/set_time_speed',{'speed':3,'ultraSpeedBoost':True}))[:120])
try:
    for i in range(14):
        time.sleep(20)
        gi=c('rimworld/get_game_info')
        ti=c('jawa/cell_temperature',{'cell':'103,205'})
        rg=c('jawa/room_get',{'rect':'100,200,18,10'})
        rooms=[(q.get('role'), round(q.get('temperature') or 0,1))
               for q in (rg.get('rooms') or []) if (q.get('cellCount') or 0)>1]
        w("t=%s outdoor=%.1f indoor=%.1f rooms=%s"%(
            gi.get('ticksGame'), ti.get('outdoorTemp') or 0, ti.get('temperature') or 0, rooms))
        if (ti.get('outdoorTemp') or 0) > 34: w("OUTDOOR IS HOT ENOUGH"); break
finally:
    w("re-pause -> %s"%json.dumps(c('rimworld/set_time_speed',{'speed':0}))[:100])
    w("final ticks=%s"%c('rimworld/get_game_info').get('ticksGame'))
