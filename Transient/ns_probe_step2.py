import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb
h,p,t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=240.0); S.connect()
def call(tool, **kw):
    r = S.call(tool, kw) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
print(call("jawa/set_current_map", mapId=1).get("tile"))
r = call("rimworld/step_game_ticks", ticks=600, pauseFirst=True, timeoutMs=120000); print("step", r.get("status"), r.get("completedTicks"))
m = call("jawa/map_info"); print({k: m.get(k) for k in ("mapId","tile","mapBiome","outdoorTempNow")})
