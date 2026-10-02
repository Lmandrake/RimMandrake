import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
step = sys.argv[1]
h,p,t = resolve_endpoint()
def conn(): return RimBridge(h,p,t)
def info():
    with conn() as rb: return rb.call("rimworld/get_game_info", {})
if step == "info":
    print(json.dumps(info())[:1500])
elif step == "menu":
    with conn() as rb: print(json.dumps(rb.call("rimworld/go_to_main_menu", {}))[:800])
elif step == "load":
    with conn() as rb:
        r = rb.call("rimworld/load_game", {"saveName": "CANONICAL_ASHKARR_START_2026-09-12"})
    print("LOAD RESP:", json.dumps(r)[:1500])
    t0=time.time()
    while time.time()-t0 < 560:
        time.sleep(15)
        try:
            i = info()
        except Exception as e:
            print(int(time.time()-t0), "info err", e); continue
        s = {k:i.get(k) for k in ("programState","status","hasCurrentGame","mapCount","ticksGame")}
        print(int(time.time()-t0), s, flush=True)
        if i.get("programState")=="Playing" and (i.get("mapCount") or 0)>0:
            time.sleep(10); print("AFTER10", json.dumps(info())[:800]); break
