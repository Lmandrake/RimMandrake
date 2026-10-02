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
try: call("rimworld/load_game", saveName=sys.argv[1])
except Exception as ex: print("load raised", type(ex).__name__)
time.sleep(25); t0=time.time()
while time.time()-t0<200:
    try:
        mi = call("jawa/map_info")
        if mi.get("success") and mi.get("tile")==57226: break
    except Exception: pass
    time.sleep(3)
print("current", call("jawa/map_info").get("tile"))
print("set", json.dumps(call("jawa/set_current_map", mapId=int(sys.argv[2])))[:160])
mi = call("jawa/map_info"); print({k: mi.get(k) for k in ("mapId","tile","mapBiome","outdoorTempNow","latitude","season")})
