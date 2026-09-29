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
log(json.dumps(r)[:300])

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
log("list_pawns ok:", lp.get("success", True))

# --- spawn a colonist near origin ---
sp = call("jawa/spawn_pawn", kindDef="Colonist", x=50, z=50, count=1, faction="player")
log("spawn colonist:", json.dumps(sp)[:300])

# find the colonist id
colonists = call("rimworld/list_colonists")
log("colonists:", json.dumps(colonists)[:500])

# --- spawn RM_Deepfire nearby (plenty, single stack) ---
df = call("rimworld/spawn_thing", defName="RM_Deepfire", x=48, z=50, stackCount=50)
log("spawn deepfire stack:", json.dumps(df)[:300])
deepfire_id = df.get("thingId")

# --- spawn targets: wall, chair, sculpture ---
wall = call("rimworld/spawn_thing", defName="Wall", x=52, z=52)
log("spawn wall:", json.dumps(wall)[:300])
wall_id = wall.get("thingId")
call("rimworld/execute_debug_action", path="Actions\\T: Set Stuff...\\Steel", thingId=wall_id)

chair = call("rimworld/spawn_thing", defName="DiningChair", x=54, z=52)
log("spawn chair:", json.dumps(chair)[:300])
chair_id = chair.get("thingId")
call("rimworld/execute_debug_action", path="Actions\\T: Set Stuff...\\WoodLog", thingId=chair_id)

sculpture = call("rimworld/spawn_thing", defName="SculptureSmall", x=56, z=52)
log("spawn sculpture:", json.dumps(sculpture)[:300])
sculpture_id = sculpture.get("thingId")

targets = {"wall": wall_id, "chair": chair_id, "sculpture": sculpture_id}
log("targets:", targets)

# --- baseline glow at each cell before coating ---
cells = {"wall": (52, 52), "chair": (54, 52), "sculpture": (56, 52)}
for name, (x, z) in cells.items():
    g = call("deepfire/glow_at", x=x, z=z)
    log("baseline glow", name, g)

# --- comp presence check ---
for name, tid in targets.items():
    c = call("deepfire/comp_coats", thing=tid)
    log("comp_coats", name, c)

with open(r"D:\Luke\dev\Rimworld\Transient\deepfire_step5_ids.json", "w") as f:
    json.dump({"deepfire_id": deepfire_id, "targets": targets, "cells": cells}, f)

log("=== PHASE 1 DONE (setup) ===")
