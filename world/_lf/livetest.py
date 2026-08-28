# -*- coding: utf-8 -*-
"""The 2026-08-26 live test: NEXT_RELOAD 24 (the Jawa hood) and 23 (the temperature table)."""
import sys, json, io, collections, time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}

gi=c('rimworld/get_game_info')
print("before: status=%s maps=%s"%(gi.get('status'), gi.get('mapCount')))
if (gi.get('mapCount') or 0)==0:
    print("starting quicktest ...")
    print("  start ->", json.dumps(c('rimworld/start_debug_game'))[:140])
    r=c('rimworld/start_debug_game_ready')
    print("  ready ->", json.dumps(r)[:200])
gi=c('rimworld/get_game_info')
print("after : status=%s maps=%s ticks=%s"%(gi.get('status'), gi.get('mapCount'), gi.get('ticksGame')))
if (gi.get('mapCount') or 0)==0:
    print("NO MAP - stopping."); raise SystemExit(1)
json.dump(gi, open(r"D:\Luke\dev\Rimworld\world\_lf\lt_state.json","w"))
