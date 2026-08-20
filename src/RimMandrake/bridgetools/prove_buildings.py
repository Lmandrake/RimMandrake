"""M2 proof: build_batch, build_check, designate_batch."""
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
call("jawa/set_fog", action="unfogAll")

print("== 1. BUILD_CHECK before building ==")
c = call("jawa/build_check", rect="120,120,3,3", stuff="Steel", **{"def": "Wall"})
print("   acceptable:", c.get("acceptableCells"), "of", c.get("tested"))
for x in (c.get("cells") or [])[:2]: print("   ", x)

print("\n== 2. BUILD a 9x7 room: walls, a door, a lamp, a bed ==")
ops = []
X0, Z0, W, H = 120, 120, 9, 7
for i in range(W):
    ops.append("Wall:%d,%d" % (X0+i, Z0))
    ops.append("Wall:%d,%d" % (X0+i, Z0+H-1))
for j in range(1, H-1):
    ops.append("Wall:%d,%d" % (X0, Z0+j))
    ops.append("Wall:%d,%d" % (X0+W-1, Z0+j))
ops = [o for o in ops if o != "Wall:%d,%d" % (X0+4, Z0)]
ops.append("Door:%d,%d" % (X0+4, Z0))
b = call("jawa/build_batch", ops=";".join(ops), stuff="Steel",
         quality="Excellent", hitPoints=175, faction="PlayerColony")
print("   placed:", b.get("placed"), " failed:", b.get("failedCount"))
for f in (b.get("failed") or [])[:3]: print("    fail:", f)
for t in (b.get("things") or [])[:3]: print("   ", t)

print("\n== 3. HITPOINTS: were they ours or the PostMake roll? ==")
for t in (b.get("things") or [])[:3]:
    print("   %-6s hp=%s / max=%s  quality=%s  faction=%s" % (
        t["def"], t["hitPoints"], t["maxHitPoints"], t["quality"], t["faction"]))

print("\n== 4. furniture inside + roof it (walls make NO roof) ==")
f2 = call("jawa/build_batch", ops="Bed:122,123;StandingLamp:126,123;Table2x2c:124,122",
          stuff="WoodLog", faction="PlayerColony")
print("   placed:", f2.get("placed"), "failed:", f2.get("failedCount"))
for x in (f2.get("failed") or [])[:3]: print("    fail:", x)
rf = call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,%d,%d" % (X0+1, Z0+1, W-2, H-2))
print("   roof cellsChanged:", rf.get("cellsChanged"), " failedVerify:", rf.get("cellsFailedVerify"))

print("\n== 5. DESIGNATIONS with no cursor ==")
d1 = call("jawa/designate_batch", action="add", designation="Mine", rect="135,120,4,4")
print("   Mine added:", d1.get("added"), " already:", d1.get("alreadyPresent"), " totalNow:", d1.get("totalNow"))
d2 = call("jawa/designate_batch", action="add", designation="Mine", rect="135,120,4,4")
print("   re-add (must be 0 added, N already):", d2.get("added"), d2.get("alreadyPresent"))
q = call("jawa/designate_batch", action="query", designation="Mine", limit=3)
print("   query:", q.get("total"), (q.get("designations") or [])[:2])
d3 = call("jawa/designate_batch", action="remove", designation="Mine", rect="135,120,4,4")
print("   removed:", d3.get("removed"), " totalNow:", d3.get("totalNow"))

print("\n== 6. map_commit + shoot ==")
mc = call("jawa/map_commit"); print("   ok:", mc.get("success"), "failed:", mc.get("failedSteps"))
call("rimworld/jump_camera_to_cell", x=124, z=123)
for _ in range(4):
    for wt in ("LudeonTK.EditWindow_Log","LudeonTK.Dialog_DevPalette","LudeonTK.Dialog_Debug"):
        call("rimworld/close_window", windowType=wt)
    if (call("rimworld/get_ui_state").get("windowCount", 9) or 9) <= 1: break
    time.sleep(0.5)
sh = call("rimworld/take_screenshot", fileName="m2_building", suppressMessage=True)
print("   saved:", sh.get("path"))
