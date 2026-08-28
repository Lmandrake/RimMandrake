# -*- coding: utf-8 -*-
"""Does the bridge silently DROP a parameter that is not in the tool's schema?
Two of my shakedown calls were mis-named and nothing complained. Prove it deliberately."""
import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=200); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
print("1. correct param name  (label)")
print("   ->", json.dumps(c('jawa/new_allowed_area',{'label':'CHECK_correct'}))[:150])
print("2. WRONG param name    (name)  + a param that exists nowhere")
print("   ->", json.dumps(c('jawa/new_allowed_area',{'name':'CHECK_wrong','banana':42}))[:150])
print("3. a read-only tool with pure garbage")
print("   ->", json.dumps(c('jawa/time_clock',{'zzz':'nonsense','ticks':'not-a-number'}))[:200])
print("\n4. areas now on the map:")
r=c('jawa/map_zones',{'action':'listZones'})
print("   ", json.dumps(r.get('areas') or r.get('zones'))[:400])
