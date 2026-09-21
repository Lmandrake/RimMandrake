import sys, json, time; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,T=resolve_endpoint()
b=RimBridge(token=T,timeout=60); b.connect()
r=b.call("rimworld/load_game_ready",{"saveName":"CANONICAL_ASHKARR_START_2026-09-12","timeoutMs":240000,"ignoreModCompatibility":True},check=False)
print("load:", str(r.get("message"))[:200], r.get("status"))
for i in range(50):
    time.sleep(10)
    try:
        b2=RimBridge(token=T,timeout=20); b2.connect()
        g=b2.call("rimworld/get_game_info",{},check=False)
        if g.get("programState")=="Playing" or g.get("status")=="game_loaded":
            print("loaded ~%ds:"%((i+1)*10), json.dumps(g)[:300]); break
    except Exception as e: print("poll",i,str(e)[:60])
