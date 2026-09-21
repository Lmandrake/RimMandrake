import sys, json, time; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge
T="4f3c0a7aa74e4446ac19465c14fd54a9"
b=RimBridge(token=T,timeout=25); b.connect()
try:
    r=b.call("rimworld/start_debug_game_ready", {"timeoutMs":20000}, check=False); print("start:", json.dumps(r)[:200])
except Exception as e: print("start raised (expected late):", str(e)[:120])
for i in range(12):
    time.sleep(5)
    try:
        b2=RimBridge(token=T,timeout=25); b2.connect()
        r=b2.call("jawa/map_info", {}, check=False); 
        if r and r.get("success") is not False and "No current map" not in json.dumps(r):
            print("map ready after ~%ds:"%((i+1)*5), json.dumps(r)[:300]); break
        print("poll", i, json.dumps(r)[:100])
    except Exception as e: print("poll", i, "err", str(e)[:80])
