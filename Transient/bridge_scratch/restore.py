import sys, json, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
rb = RimBridge(host, port, token, timeout=900.0); rb.connect()
def call(t, **p):
    r = rb.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
print("reload:", json.dumps({k: call("rimworld/load_game_ready", saveName="WORLDMAP_V1_original",
      readiness="gameData", timeoutMs=900000, pauseIfNeeded=True).get(k)
      for k in ("success","message")})[:300])
time.sleep(30)
print("ui:", json.dumps({k: call("rimworld/get_ui_state").get(k) for k in ("programState","currentMapId")}))
call("jawa/world_view", show=True, centerTile=8858, altitude=470, northUp=True)
time.sleep(3)
s = call("jawa/world_map_mode", mapModeDefName="FactionTerritories")
print("switch:", json.dumps({k: s.get(k) for k in ("success","switched","modeBefore","modeAfter","regenerateNow","message")}))
time.sleep(8)
f = call("jawa/world_map_mode")
print("final:", json.dumps({k: f.get(k) for k in ("modeAfter","regenBusy","regenerateNow","worldRendered")}))
print("screenshot_mode off:", json.dumps(call("jawa/screenshot_mode", enabled=False))[:140])
