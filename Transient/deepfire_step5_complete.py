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
for i in range(120):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing":
        break
    time.sleep(1)
for i in range(60):
    lp = call("jawa/list_pawns")
    if lp.get("success") is not False and "No current map" not in json.dumps(lp):
        break
    time.sleep(1)

colonists = call("rimworld/list_colonists")
c0 = colonists["colonists"][0]
pawn_id = c0["pawnId"]
bx, bz = c0["position"]["x"], c0["position"]["z"]
log("pawn:", pawn_id, "pos", c0["position"])

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

section("REAL job: designate wall + let colonist do it (via WorkGiver/JobDriver, no forcing)")
log("designate:", call("deepfire/designate", thing=wall_id))
coats = 0
for i in range(30):
    call("rimworld/step_game_ticks", ticks=200)
    c = call("deepfire/comp_coats", thing=wall_id)
    coats = c.get("coats", 0)
    cur = call("rimworld/list_colonists")
    cj = next((x.get("job") for x in cur.get("colonists", []) if x.get("pawnId") == pawn_id), None)
    log("poll", i, "coats", coats, "pawn0 job", cj, "tick", call("rimworld/get_game_info").get("ticksGame"))
    if coats >= 1:
        break
log("WALL COAT1 via REAL job:", coats)

g1 = call("deepfire/glow_at", x=wx, z=wz)
log("wall glow after real coat1:", g1.get("groundGlow"), g1.get("visual"))

section("paint wall blue -> glow follows colour")
p = call("deepfire/paint_building", thing=wall_id, colorDef="Structure_Blue")
log("paint result colorDef/drawColor:", p.get("colorDef"), p.get("drawColor"))
g2 = call("deepfire/glow_at", x=wx, z=wz)
log("wall glow after paint blue:", g2.get("groundGlow"), g2.get("visual"))

section("coats 2 and 3 (direct AddCoat -- same method the job calls on completion)")
r2 = call("deepfire/add_coat", thing=wall_id)
log("-> coat2:", r2.get("coatsBefore"), "->", r2.get("coatsAfter"))
r3 = call("deepfire/add_coat", thing=wall_id)
log("-> coat3:", r3.get("coatsBefore"), "->", r3.get("coatsAfter"))
g3 = call("deepfire/glow_at", x=wx, z=wz)
log("wall glow at 3 coats:", g3.get("groundGlow"), g3.get("visual"))

section("4th coat refused (capped at 3)")
r4 = call("deepfire/add_coat", thing=wall_id)
log("attempt coat4:", r4.get("coatsBefore"), "->", r4.get("coatsAfter"))

section("remove -> 0, light off")
rr = call("deepfire/remove_coats", thing=wall_id)
log("remove_coats:", rr.get("coatsBefore"), "->", rr.get("coatsAfter"))
g4 = call("deepfire/glow_at", x=wx, z=wz)
log("wall glow after removal:", g4.get("groundGlow"), g4.get("visual"))

section("chair: 2 coats, then save/load persistence check")
call("deepfire/add_coat", thing=chair_id)
call("deepfire/add_coat", thing=chair_id)
cb = call("deepfire/comp_coats", thing=chair_id)
log("chair coats before save:", cb.get("coats"))
gcb = call("deepfire/glow_at", x=cx, z=cz)
log("chair glow before save:", gcb.get("groundGlow"), gcb.get("visual"))

sv = call("rimworld/save_game", saveName="deepfire_step5_proof_final")
log("save_game:", sv.get("success"))
ld = call("rimworld/load_game", saveName="deepfire_step5_proof_final")
log("load_game:", ld.get("success"))
for i in range(60):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing" and st.get("currentMapReady"):
        break
    time.sleep(1)
log("post-load programState:", st.get("programState"))

info = call("rimworld/get_cell_info", x=cx, z=cz)
things = info.get("cell", {}).get("things", [])
log("chair cell after load, things:", json.dumps(things)[:400])
chair_after = next((t for t in things if t.get("defName") == "DiningChair"), None)
log("chair still present after load:", chair_after is not None)
g_after = call("deepfire/glow_at", x=cx, z=cz)
log("chair-cell glow after save/load:", g_after.get("groundGlow"), g_after.get("visual"))

with open(r"D:\Luke\dev\Rimworld\Transient\deepfire_step5_complete_ids.json", "w") as f:
    json.dump({"deepfire_id": deepfire_id, "wall_id": wall_id, "chair_id": chair_id,
               "sculpture_id": sculpture_id, "pawn_id": pawn_id,
               "wx": wx, "wz": wz, "cx": cx, "cz": cz, "sx": sx, "sz": sz}, f)
log("\n=== ALL DONE ===")
