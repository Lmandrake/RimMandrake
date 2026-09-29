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
log("colonist0 pos:", cpos)
bx, bz = cpos["x"], cpos["z"]

# spawn everything near the existing colony instead of a fixed distant spot
wx, wz = bx + 4, bz
cx, cz = bx + 6, bz
sx, sz = bx + 8, bz
dx, dz = bx + 2, bz

df = call("rimworld/spawn_thing", defName="RM_Deepfire", x=dx, z=dz, stackCount=50)
log("spawn deepfire:", df.get("success"), df.get("thingId"))
deepfire_id = df.get("thingId")

wall = call("rimworld/spawn_thing", defName="Wall", x=wx, z=wz)
log("spawn wall:", wall.get("success"), wall.get("thingId"))
wall_id = wall.get("thingId")
call("rimworld/execute_debug_action", path="Actions\\T: Set Stuff...\\Steel", thingId=wall_id)

chair = call("rimworld/spawn_thing", defName="DiningChair", x=cx, z=cz)
log("spawn chair:", chair.get("success"), chair.get("thingId"))
chair_id = chair.get("thingId")
call("rimworld/execute_debug_action", path="Actions\\T: Set Stuff...\\WoodLog", thingId=chair_id)

sculpture = call("rimworld/spawn_thing", defName="SculptureSmall", x=sx, z=sz)
log("spawn sculpture:", sculpture.get("success"), sculpture.get("thingId"))
sculpture_id = sculpture.get("thingId")

targets = {"wall": wall_id, "chair": chair_id, "sculpture": sculpture_id}
cells = {"wall": (wx, wz), "chair": (cx, cz), "sculpture": (sx, sz)}

for name, tid in targets.items():
    c = call("deepfire/comp_coats", thing=tid)
    log("comp_coats", name, c.get("present"), c.get("coats"))

for name, (x, z) in cells.items():
    g = call("deepfire/glow_at", x=x, z=z)
    log("baseline glow", name, g.get("groundGlow"), g.get("visual"))

with open(r"D:\Luke\dev\Rimworld\Transient\deepfire_step5_ids.json", "w") as f:
    json.dump({"deepfire_id": deepfire_id, "targets": targets, "cells": cells}, f)

# --- real job: designate the wall, unpause, wait ---
log("designate wall:", call("deepfire/designate", thing=wall_id))
call("rimworld/set_time_speed", speed="Superfast")
coats = 0
for i in range(60):
    c = call("deepfire/comp_coats", thing=wall_id)
    coats = c.get("coats", 0)
    if coats >= 1:
        log("wall coat reached at poll", i)
        break
    time.sleep(2)
call("rimworld/set_time_speed", speed="Paused")
log("final wall comp_coats:", call("deepfire/comp_coats", thing=wall_id))
log("ticksGame:", call("rimworld/get_game_info").get("ticksGame"))
g = call("deepfire/glow_at", x=wx, z=wz)
log("wall glow after coat1 (real job):", g.get("groundGlow"), g.get("visual"))
