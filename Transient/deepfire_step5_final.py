import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb

host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=600.0)
S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try:
            r = json.loads(r["content"][0]["text"])
        except Exception:
            pass
    return r

def log(*a):
    print(*a)
    sys.stdout.flush()

def section(s):
    log("\n===", s, "===")

section("start_debug_game_ready")
r = call("rimworld/start_debug_game_ready", timeoutMs=280000, readiness="mapData", pauseIfNeeded=True)
log(json.dumps(r)[:200])
for i in range(120):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing":
        break
    time.sleep(1)
log("programState:", st.get("programState"))
for i in range(60):
    lp = call("jawa/list_pawns")
    if lp.get("success") is not False and "No current map" not in json.dumps(lp):
        break
    time.sleep(1)

colonists = call("rimworld/list_colonists")
cpos = colonists["colonists"][0]["position"]
bx, bz = cpos["x"], cpos["z"]
log("colonist0 pos:", cpos)

wx, wz = bx + 4, bz
cx, cz = bx + 6, bz
sx, sz = bx + 8, bz
dx, dz = bx + 2, bz

section("spawn")
df = call("rimworld/spawn_thing", defName="RM_Deepfire", x=dx, z=dz, stackCount=50)
deepfire_id = df.get("thingId")
wall = call("rimworld/spawn_thing", defName="Wall", x=wx, z=wz)
wall_id = wall.get("thingId")
call("rimworld/execute_debug_action", path="Actions\\T: Set Stuff...\\Steel", thingId=wall_id)
chair = call("rimworld/spawn_thing", defName="DiningChair", x=cx, z=cz)
chair_id = chair.get("thingId")
call("rimworld/execute_debug_action", path="Actions\\T: Set Stuff...\\WoodLog", thingId=chair_id)
sculpture = call("rimworld/spawn_thing", defName="SculptureSmall", x=sx, z=sz)
sculpture_id = sculpture.get("thingId")
log("wall", wall_id, "chair", chair_id, "sculpture", sculpture_id, "deepfire", deepfire_id)

for name, tid in [("wall", wall_id), ("chair", chair_id), ("sculpture", sculpture_id)]:
    c = call("deepfire/comp_coats", thing=tid)
    log("comp_coats", name, c.get("present"), c.get("coats"))

section("real job: designate + unpause + poll (wall)")
log("designate:", call("deepfire/designate", thing=wall_id))
call("rimworld/set_time_speed", speed="Superfast")
coats = 0
for i in range(90):
    c = call("deepfire/comp_coats", thing=wall_id)
    coats = c.get("coats", 0)
    if coats >= 1:
        log("wall coat1 reached at poll", i, "ticksGame", call("rimworld/get_game_info").get("ticksGame"))
        break
    time.sleep(2)
call("rimworld/set_time_speed", speed="Paused")
log("wall coats after real job:", coats)

g1 = call("deepfire/glow_at", x=wx, z=wz)
log("wall glow after coat1:", g1.get("groundGlow"), g1.get("visual"))

section("paint wall blue -> glow follows colour")
p = call("deepfire/paint_building", thing=wall_id, colorDef="Structure_Blue")
log("paint result:", p)
g2 = call("deepfire/glow_at", x=wx, z=wz)
log("wall glow after paint blue:", g2.get("groundGlow"), g2.get("visual"))

section("coats 2 and 3 (direct AddCoat, same method the job calls)")
for n in (2, 3):
    r = call("deepfire/add_coat", thing=wall_id)
    log("add_coat ->", n, r.get("coatsBefore"), "->", r.get("coatsAfter"))
g3 = call("deepfire/glow_at", x=wx, z=wz)
log("wall glow at 3 coats:", g3.get("groundGlow"), g3.get("visual"))

section("4th coat refused")
r = call("deepfire/add_coat", thing=wall_id)
log("attempt coat 4 ->", r.get("coatsBefore"), "->", r.get("coatsAfter"), "(should be unchanged, capped at 3)")

section("remove -> 0")
r = call("deepfire/remove_coats", thing=wall_id)
log("remove_coats ->", r.get("coatsBefore"), "->", r.get("coatsAfter"))
g4 = call("deepfire/glow_at", x=wx, z=wz)
log("wall glow after removal:", g4.get("groundGlow"), g4.get("visual"))

section("minify chair, reinstall -> still glowing")
call("deepfire/add_coat", thing=chair_id)
call("deepfire/add_coat", thing=chair_id)
before = call("deepfire/comp_coats", thing=chair_id)
log("chair coats before minify:", before.get("coats"))
gbefore = call("deepfire/glow_at", x=cx, z=cz)
log("chair glow before minify:", gbefore.get("groundGlow"))

ch = call("rimworld/list_debug_action_children", path="Actions")
minify_matches = [c for c in ch.get("children", []) if "inify" in c.get("path", "")]
log("minify action candidates:", [m.get("path") for m in minify_matches])
minify_path = minify_matches[0]["path"] if minify_matches else None

if minify_path:
    mini = call("rimworld/execute_debug_action", path=minify_path, thingId=chair_id)
    log("minify action:", mini.get("success"), mini.get("message"))
else:
    log("NO minify debug action found -- skipping minify/reinstall sub-proof")

# find the minified thing at the same cell
info = call("rimworld/get_cell_info", x=cx, z=cz)
log("cell after minify:", json.dumps(info.get("things"))[:400])

with open(r"D:\Luke\dev\Rimworld\Transient\deepfire_step5_final_ids.json", "w") as f:
    json.dump({"deepfire_id": deepfire_id, "wall_id": wall_id, "chair_id": chair_id,
               "sculpture_id": sculpture_id, "wx": wx, "wz": wz, "cx": cx, "cz": cz,
               "sx": sx, "sz": sz}, f)

section("re-coat wall (fresh, since it was removed above) for the save/load check")
call("deepfire/add_coat", thing=wall_id)
call("deepfire/add_coat", thing=wall_id)
before_save = call("deepfire/comp_coats", thing=wall_id)
log("wall coats before save:", before_save.get("coats"))
g_before_save = call("deepfire/glow_at", x=wx, z=wz)
log("wall glow before save:", g_before_save.get("groundGlow"), g_before_save.get("visual"))

section("save + load -> still glowing")
sv = call("rimworld/save_game", saveName="deepfire_step5_proof")
log("save_game:", sv.get("success"), sv.get("message"))
ld = call("rimworld/load_game", saveName="deepfire_step5_proof")
log("load_game:", ld.get("success"), ld.get("message"))

for i in range(60):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing" and st.get("currentMapReady"):
        break
    time.sleep(1)
log("post-load programState:", st.get("programState"))

info2 = call("rimworld/get_cell_info", x=wx, z=wz)
log("wall cell after load:", json.dumps(info2.get("cell", {}).get("things"))[:400])
g_after_load = call("deepfire/glow_at", x=wx, z=wz)
log("wall glow after save/load:", g_after_load.get("groundGlow"), g_after_load.get("visual"))

