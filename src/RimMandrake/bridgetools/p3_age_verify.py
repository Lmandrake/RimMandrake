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
ps = [p for p in call("jawa/pawn_get", limit=8)["pawns"] if p.get("faction") == "PlayerColony"]
PID = str(ps[0]["thingIdNumber"])
cur = call("jawa/pawn_get", pawn=PID)["pawns"][0]["ageBiologicalYears"]
print("pawn:", ps[0]["name"], "age", cur)

print("\n1. FORWARD (should work, birthdays fire)")
u = call("jawa/set_pawn_age", pawn=PID, biologicalYears=cur + 15)
print("   ", u["before"]["biologicalYears"], "->", u["after"]["biologicalYears"], u.get("ageNotes"))

print("\n2. BACKWARD without the flag (must REFUSE, not silently no-op)")
d = call("jawa/set_pawn_age", pawn=PID, biologicalYears=9)
print("   success:", d.get("success"))
print("   message:", (d.get("message") or "")[:220])

print("\n3. BACKWARD with allowBackwards=true")
d2 = call("jawa/set_pawn_age", pawn=PID, biologicalYears=9, allowBackwards=True)
print("   ", d2["before"]["biologicalYears"], "->", d2["after"]["biologicalYears"])
print("   ageNotes:", d2.get("ageNotes"))
print("   lifeStage:", d2["after"]["lifeStage"], " bodyType:", d2["after"]["bodyType"])
print("   bodyTypeMismatch:", d2.get("bodyTypeMismatch"))
print("   warning:", (d2.get("warning") or "none")[:150])
