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
def ui(): return [w["type"] for w in call("rimworld/get_ui_state").get("windows", [])]
def mp():
    m = call("jawa/map_info"); return {k: m.get(k) for k in ("mapId","tile","mapBiome","outdoorTempNow")}
print("before", mp(), ui())
if "RimWorld.Dialog_NamePlayerFactionAndSettlement" in ui():
    print("accept", str(call("rimworld/press_accept"))[:100])
print("after dismiss", mp(), ui())
r = call("rimworld/step_game_ticks", ticks=300, pauseFirst=True, timeoutMs=120000); print("step", r.get("status"), r.get("completedTicks"))
print("after step", mp(), ui())
print("close", str(call("jawa/window_list_close", action="close", typeName="RimWorld.Dialog_NamePlayerFactionAndSettlement"))[:200])
print("ui", ui(), mp())
