"""MIASMA_SCUTTLER_PREDATION_1 -- minimal+Miasma quicktest proof that
RM_CompPlantPredator actually kills a scuttler pawn within range."""
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


print("== defs sanity ==")
d = call("jawa/get_defs", defs="ThingDef/RM_Ullavess")
print(json.dumps(d, indent=2)[:800])

print("== start_debug_game_ready ==")
r = call("rimworld/start_debug_game_ready", timeoutMs=120000, readiness="mapData", pauseIfNeeded=True)
print(json.dumps(r, indent=2)[:500])

st = {}
for _ in range(60):
    st = call("rimworld/get_ui_state")
    if st.get("programState") == "Playing":
        break
    time.sleep(1)
print("programState:", st.get("programState"))

info = call("rimworld/get_game_info")
print("map info:", json.dumps(info, indent=2)[:400])

plant_r = call("rimworld/spawn_thing", ops="RM_Ullavess:20,20")
print("spawn plant:", json.dumps(plant_r, indent=2)[:400])

prey_r = call("jawa/spawn_pawn", kindDef="RM_Karravel", x=21, z=20, faction="none")
print("spawn prey:", json.dumps(prey_r, indent=2)[:600])

before = call("jawa/list_pawns", animalsOnly=True)
print("pawns before:", json.dumps(before, indent=2)[:600])

print("== stepping ticks (aiming past one TickLong interval) ==")
call("rimworld/step_game_ticks", ticks=2500)
call("rimworld/step_game_ticks", ticks=2500)
call("rimworld/step_game_ticks", ticks=2500)

after = call("jawa/list_pawns", animalsOnly=True)
print("pawns after:", json.dumps(after, indent=2)[:600])

logs = call("jawa/drain_log", errorsOnly=False)
print("== recent logs ==")
print(json.dumps(logs, indent=2)[:3000])
