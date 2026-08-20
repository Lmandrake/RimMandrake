"""M3 proof: capture a hand-built region and replay it elsewhere, then diff."""
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

X0, Z0, W, H = 120, 120, 9, 7
print("== 1. BUILD a source scene by hand ==")
ops = []
for i in range(W):
    ops.append("Wall:%d,%d" % (X0+i, Z0)); ops.append("Wall:%d,%d" % (X0+i, Z0+H-1))
for j in range(1, H-1):
    ops.append("Wall:%d,%d" % (X0, Z0+j)); ops.append("Wall:%d,%d" % (X0+W-1, Z0+j))
ops = [o for o in ops if o != "Wall:%d,%d" % (X0+4, Z0)]
ops.append("Door:%d,%d" % (X0+4, Z0))
b = call("jawa/build_batch", ops=";".join(ops), stuff="Steel", faction="PlayerColony")
f = call("jawa/build_batch", ops="Bed:122,123;StandingLamp:126,123;Table2x2c:124,122",
         stuff="WoodLog", faction="PlayerColony")
call("jawa/set_terrain_batch", ops="Concrete:%d,%d,%d,%d" % (X0+1, Z0+1, W-2, H-2))
call("jawa/set_roof_batch", ops="RoofConstructed:%d,%d,%d,%d" % (X0+1, Z0+1, W-2, H-2))
print("   built:", b.get("placed"), "+", f.get("placed"))

print("\n== 2. CAPTURE it ==")
cap = call("jawa/prefab_capture", name="hut", rect="%d,%d,%d,%d" % (X0, Z0, W, H),
           copyAllThings=True, copyTerrain=True)
print("   success:", cap.get("success"), " size:", cap.get("size"), " thingCount:", cap.get("thingCount"))
print("   contents:", list((cap.get("contents") or {}).items())[:6])
if not cap.get("success"): print("   message:", cap.get("message"))

print("\n== 3. LIST ==")
l = call("jawa/prefab_list", limit=3)
print("   sessionCaptures:", l.get("sessionCaptures"), l.get("captures"))
print("   shippedTotal:", l.get("shippedTotal"))

print("\n== 4. CHECK then PLACE it 30 cells east ==")
chk = call("jawa/prefab_place", name="hut", pos="160,120", checkOnly=True)
print("   canSpawn:", chk.get("canSpawn"), chk.get("message") or "")
p1 = call("jawa/prefab_place", name="hut", pos="160,120", faction="PlayerColony")
print("   spawnedCount:", p1.get("spawnedCount"))
for t in (p1.get("things") or [])[:4]: print("   ", t)

print("\n== 5. PLACE ROTATED, 30 cells south ==")
p2 = call("jawa/prefab_place", name="hut", pos="120,90", rot="1", faction="PlayerColony")
print("   spawnedCount:", p2.get("spawnedCount"), " rot:", p2.get("rot"))

print("\n== 6. DIFF: compare the source rect against the copy cell by cell ==")
def contents(rect):
    r = call("jawa/get_terrain_layers", rect=rect, limit=400)
    return {(c["x"], c["z"]): c["top"] for c in (r.get("cells") or [])}
src = contents("%d,%d,%d,%d" % (X0, Z0, W, H))
dst = contents("160,120,%d,%d" % (W, H))
same = sum(1 for (x, z), v in src.items() if dst.get((x - X0 + 160, z)) == v)
print("   terrain cells identical: %d of %d" % (same, len(src)))

print("\n== 7. commit + shoot ==")
call("jawa/map_commit")
call("rimworld/jump_camera_to_cell", x=145, z=118)
for _ in range(4):
    for wt in ("LudeonTK.EditWindow_Log","LudeonTK.Dialog_DevPalette","LudeonTK.Dialog_Debug"):
        call("rimworld/close_window", windowType=wt)
    if (call("rimworld/get_ui_state").get("windowCount", 9) or 9) <= 1: break
    time.sleep(0.5)
sh = call("rimworld/take_screenshot", fileName="m3_prefab", suppressMessage=True)
print("   saved:", sh.get("path"))
