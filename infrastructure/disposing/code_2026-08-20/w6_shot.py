import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
for _ in range(120):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing": break
    time.sleep(1)
f = call("jawa/world_features_get", limit=200, sampleTiles=1)
big = max((f.get("features") or []), key=lambda x: x["tileCount"])
print("renaming feature", big["uniqueID"], big["name"], "tiles", big["tileCount"])
call("jawa/world_features_set", action="update", featureId=big["uniqueID"],
     name="THE DUNE SEA", drawAngle=30.0, maxDrawSizeInTiles=120.0)
t = (big.get("sampleTiles") or [0])[0]
v = call("jawa/world_view", show=True, centerTile=t, altitude=420.0, northUp=True)
print("view:", {k: v.get(k) for k in ("worldSelectedAfter","centeredOn","altitude","altitudeRange")})
call("jawa/world_commit")
D = ("LudeonTK.EditWindow_Log","LudeonTK.Dialog_DevPalette","LudeonTK.Dialog_Debug")
for _ in range(4):
    for wt in D: call("rimworld/close_window", windowType=wt)
    if (call("rimworld/get_ui_state").get("windowCount", 9) or 9) <= 1: break
    time.sleep(0.6)
sh = call("rimworld/take_screenshot", fileName="w6_dune_sea", suppressMessage=True)
print("saved:", sh.get("path"))
