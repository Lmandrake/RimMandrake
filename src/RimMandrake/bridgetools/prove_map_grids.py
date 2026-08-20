"""M1 visual + M4 grids."""
import sys, json, time
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
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

print("== unfog the whole map ==")
f = call("jawa/set_fog", action="unfogAll")
print("   foggedCellsNow:", f.get("foggedCellsNow"), "of", f.get("mapArea"))

print("\n== substructure slab + under-terrain + snow + sand + deep resource ==")
print("  substructure:", call("jawa/set_substructure_batch", action="set", rect="100,100,22,22").get("changed"))
print("  under sand  :", call("jawa/set_terrain_layer", layer="under", rect="130,100,12,12", **{"def":"Sand"}).get("changed"))
sn = call("jawa/set_weather_buildup", kind="snow", mode="set", rect="100,130,20,20", depth=0.9)
print("  snow        :", sn.get("cellsChanged"), " sample:", (sn.get("cells") or [{}])[0])
sd = call("jawa/set_weather_buildup", kind="sand", mode="set", rect="130,130,20,20", depth=0.9)
print("  sand        :", sd.get("cellsChanged"), " success:", sd.get("success"), (sd.get("message") or "")[:80])
dr = call("jawa/set_deep_resource", rect="160,100,6,6", **{"def":"MineableGold"})
print("  deep gold   :", dr.get("cellsChanged"), " sample:", (dr.get("cells") or [{}])[0])

print("\n== map_commit ==")
mc = call("jawa/map_commit"); print("   ok:", mc.get("success"), "failed:", mc.get("failedSteps"))

print("\n== camera to the slab, then shoot ==")
call("rimworld/jump_camera_to_cell", x=120, z=120)
call("rimworld/set_camera_zoom", zoom="Far") if False else call("rimworld/zoom_camera", **{"zoom": -3})
D = ("LudeonTK.EditWindow_Log","LudeonTK.Dialog_DevPalette","LudeonTK.Dialog_Debug")
for _ in range(4):
    for wt in D: call("rimworld/close_window", windowType=wt)
    if (call("rimworld/get_ui_state").get("windowCount", 9) or 9) <= 1: break
    time.sleep(0.5)
sh = call("rimworld/take_screenshot", fileName="m1_m4_grids", suppressMessage=True)
print("   saved:", sh.get("path"))
