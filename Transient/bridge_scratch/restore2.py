import sys, json, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
rb = RimBridge(host, port, token, timeout=1200.0); rb.connect()
def call(t, **p):
    r = rb.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
r = call("rimworld/load_game", saveName="WORLDMAP_V1_original")
print("load_game:", json.dumps({k: r.get(k) for k in ("success","message")})[:300])
for i in range(150):
    time.sleep(4)
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing":
        print("PLAYING at t=%ds" % (i*4)); break
    if i % 10 == 0: print("  t=%ds %s" % (i*4, st.get("programState"))); sys.stdout.flush()
time.sleep(20)
print("ui:", json.dumps({k: call("rimworld/get_ui_state").get(k) for k in ("programState","currentMapId")}))
call("jawa/world_view", show=True, centerTile=8858, altitude=470, northUp=True)
time.sleep(4)
s = call("jawa/world_map_mode", mapModeDefName="FactionTerritories")
print("switch:", json.dumps({k: s.get(k) for k in ("success","switched","modeBefore","modeAfter","message")}))
time.sleep(8)
print("final:", json.dumps({k: call("jawa/world_map_mode").get(k) for k in
      ("modeAfter","regenBusy","regenerateNow","worldRendered")}))
