"""MIASMA_SCUTTLER_PREDATION_1 -- minimal+Miasma quicktest proof that
RM_CompPlantPredator actually kills a scuttler pawn within range."""
_RM_ROOT = __import__("pathlib").Path(__file__).resolve().parents[3]  # repo root, derived (not hardcoded)
import sys, json, time
sys.path.insert(0, str(_RM_ROOT / 'src' / 'RimMandrake' / 'Utils'))
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

# PLANTPREDATORPROOF_FIX_NO_SPAWN_NO_VERDICT: 'ops' is jawa/spawn_batch's format; rimworld/spawn_thing takes
# defName/x/z, so the plant was never placed. list_pawns has no animalsOnly filter and hides the dead unless
# includeCorpses, and the script printed rows with no verdict -- it now judges the one prey it spawned, by id.
plant_r = call("jawa/spawn_batch", ops="RM_Ullavess:20,20")
print("spawn plant:", json.dumps(plant_r, indent=2)[:400])
plants = call("jawa/list_things", defName="RM_Ullavess", rect="20,20,1,1", limit=5)
if not plants.get("countMatched"):
    print("UNMEASURED: no RM_Ullavess at (20,20) after spawning:", json.dumps(plants)[:300])
    sys.exit(2)

prey_r = call("jawa/spawn_pawn", kindDef="RM_Karravel", x=21, z=20, faction="none")
print("spawn prey:", json.dumps(prey_r, indent=2)[:600])
prey_ids = [p.get("id") for p in (prey_r.get("pawns") or []) if p.get("spawned")]
if not prey_r.get("success") or len(prey_ids) != 1:
    print("UNMEASURED: wild RM_Karravel did not spawn")
    sys.exit(2)
prey_id = prey_ids[0]


def prey_row():
    r = call("jawa/list_pawns", includeCorpses=True, limit=5000)
    return next((p for p in (r.get("pawns") or []) if p.get("id") == prey_id), None)


before = prey_row()
print("prey before:", json.dumps(before)[:400])

print("== stepping ticks (aiming past one TickLong interval) ==")
for _ in range(3):
    call("rimworld/step_game_ticks", ticks=2500)

after = prey_row()
print("prey after:", json.dumps(after)[:400])

logs = call("jawa/drain_log", errorsOnly=True)
print("== error logs ==")
print(json.dumps(logs, indent=2)[:3000])

ok = bool(before and not before.get("dead") and after and after.get("dead"))
print("VERDICT: prey %s alive before, %s after 7500 ticks beside the plant => %s"
      % (prey_id, "dead" if after and after.get("dead") else "NOT dead/unseen", "PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
