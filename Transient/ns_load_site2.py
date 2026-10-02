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
def state(): return call("rimworld/get_ui_state").get("programState")
name, tile = sys.argv[1], int(sys.argv[2])
if state() == "Playing":
    try: call("rimworld/go_to_main_menu")
    except Exception as ex: print("menu raised", type(ex).__name__)
    t0=time.time()
    while state() != "Entry" and time.time()-t0 < 180: time.sleep(2)
print("state", state())
try: print(json.dumps(call("rimworld/load_game", saveName=name))[:120])
except Exception as ex: print("load raised", type(ex).__name__)
t0=time.time(); mi=None
while time.time()-t0 < 240:
    time.sleep(3)
    try:
        mi = call("jawa/map_info")
        if mi.get("success"): break
    except Exception: pass
print("map", {k: (mi or {}).get(k) for k in ("mapId","tile","mapBiome","outdoorTempNow")}, round(time.time()-t0), "s")
print("ui", [w.get("type") for w in call("rimworld/get_ui_state").get("windows", [])])
