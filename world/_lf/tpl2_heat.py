# -*- coding: utf-8 -*-
"""CRITERION 2 - does the shell hold temperature? Force the outside hot with a HeatWave
GameCondition, step ticks so the sim actually runs, and read indoor vs outdoor back."""
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=600); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
IN=(103,205)      # inside the barracks
OUT=(140,200)     # open ground well clear of the hut
def temps(tag):
    ti=c('jawa/cell_temperature',{'cell':'%d,%d'%IN})
    to=c('jawa/cell_temperature',{'cell':'%d,%d'%OUT})
    rg=c('jawa/room_get',{'rect':'100,200,18,10'})
    rooms=[q for q in (rg.get('rooms') or []) if (q.get('cellCount') or 0)>1]
    print("  %-14s indoor cell %s | outdoor cell %s | rooms %s"%(
        tag,
        json.dumps(ti.get('temperature') if 'temperature' in ti else ti.get('celsius'))[:8],
        json.dumps(to.get('temperature') if 'temperature' in to else to.get('celsius'))[:8],
        [(q.get('role'), round(q.get('temperature') or 0,1)) for q in rooms]))
    return ti, to, rooms
print("BEFORE")
temps("baseline")
print("\nstart HeatWave")
r=c('jawa/game_condition',{'action':'start','condition':'HeatWave','durationTicks':200000})
print("  ->", r.get('success'), (r.get('message') or json.dumps(r))[:140])
for n in (2000, 6000, 12000):
    s=c('rimworld/step_game_ticks',{'ticks':n,'timeoutMs':240000})
    gi=c('rimworld/get_game_info')
    print("\nafter +%d ticks (game tick %s) step=%s"%(n, gi.get('ticksGame'), s.get('success')))
    temps("t+%d"%n)
