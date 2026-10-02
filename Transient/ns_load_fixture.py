import sys, json, time
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=240.0); S.connect()
def call(tool, **kw):
    r = S.call(tool, kw) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
name = sys.argv[1]
try: print(json.dumps(call("rimworld/load_game", saveName=name))[:300])
except Exception as ex: print("load raised", type(ex).__name__)
t0 = time.time()
while time.time() - t0 < 300:
    time.sleep(3)
    try:
        mi = call("jawa/map_info")
        if mi.get("success"): print("MAP", mi.get("tile"), mi.get("mapBiome"), round(time.time()-t0)); break
    except Exception as ex: pass
