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
dx, dz = bx + 2, bz

df = call("rimworld/spawn_thing", defName="RM_Deepfire", x=dx, z=dz, stackCount=50)
deepfire_id = df.get("thingId")
log("deepfire:", deepfire_id)

wall = call("rimworld/spawn_thing", defName="Wall", x=wx, z=wz)
wall_id = wall.get("thingId")
log("wall:", wall_id)
call("rimworld/execute_debug_action", path="Actions\\T: Set Stuff...\\Steel", thingId=wall_id)

log("designate:", call("deepfire/designate", thing=wall_id))

dbg = call("deepfire/debug_workgiver", thing=wall_id)
log(json.dumps(dbg, indent=2))

with open(r"D:\Luke\dev\Rimworld\Transient\deepfire_step5_ids2.json", "w") as f:
    json.dump({"deepfire_id": deepfire_id, "wall_id": wall_id, "wx": wx, "wz": wz}, f)
