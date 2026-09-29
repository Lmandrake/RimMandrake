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

log("=== start_debug_game_ready ===")
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
bx, bz = c0["position"]["x"], c0["position"]["y"] if "y" in c0["position"] else c0["position"]["z"]
log("pawn:", pawn_id, "pos", c0["position"])

wx, wz = bx + 4, bz
dx, dz = bx + 2, bz

df = call("rimworld/spawn_thing", defName="RM_Deepfire", x=dx, z=dz, stackCount=50)
deepfire_id = df.get("thingId")
wall = call("rimworld/spawn_thing", defName="Wall", x=wx, z=wz)
wall_id = wall.get("thingId")
call("rimworld/execute_debug_action", path="Actions\\T: Set Stuff...\\Steel", thingId=wall_id)
log("wall:", wall_id, "deepfire:", deepfire_id)

log("designate:", call("deepfire/designate", thing=wall_id))

fj = call("deepfire/force_apply_job", pawn=pawn_id, thing=wall_id)
log("force_apply_job:", json.dumps(fj)[:400])

call("rimworld/set_time_speed", speed="Normal")
coats = 0
for i in range(60):
    c = call("deepfire/comp_coats", thing=wall_id)
    coats = c.get("coats", 0)
    curjob = call("rimworld/list_colonists")
    cj = next((x.get("job") for x in curjob.get("colonists", []) if x.get("pawnId") == pawn_id), None)
    log("poll", i, "coats", coats, "pawn job", cj)
    if coats >= 1:
        break
    time.sleep(2)
call("rimworld/set_time_speed", speed="Paused")
log("FINAL coats:", coats)
g = call("deepfire/glow_at", x=wx, z=wz)
log("wall glow:", g.get("groundGlow"), g.get("visual"))
