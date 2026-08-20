"""P3 proof: faction, ideo, relations (incl. the implied refusal), genes, age."""
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
lst = call("jawa/pawn_get", limit=8)
ps = [p for p in lst["pawns"] if p.get("faction") == "PlayerColony"]
PID = str(ps[0]["thingIdNumber"]); OTHER = str(ps[1]["thingIdNumber"])
print("pawns:", ps[0]["name"], "/", ps[1]["name"])

print("\n== 1. RELATIONS - direct works, IMPLIED must refuse ==")
r1 = call("jawa/pawn_relations", pawn=PID, action="add", relation="Sibling", otherPawn=OTHER)
print("   add Sibling -> added:", r1.get("added"), "notes:", r1.get("notes"))
print("   opinion both ways:", r1.get("opinionOfOther"), "/", r1.get("opinionOfMe"))
r2 = call("jawa/pawn_relations", pawn=PID, action="add", relation="Cousin", otherPawn=OTHER)
print("   add Cousin (implied) -> success:", r2.get("success"))
print("     message:", (r2.get("message") or "")[:150])
r3 = call("jawa/pawn_relations", pawn=PID, action="list")
print("   relations now:", [(x["def"], x["otherPawn"]) for x in r3.get("relations", [])])

print("\n== 2. IDEOLIGION ==")
i0 = call("jawa/set_pawn_ideo", pawn=PID, action="list")
print("   ideologyActive:", i0.get("success"), (i0.get("message") or "")[:70])
if i0.get("success"):
    avail = i0.get("availableIdeos") or []
    print("   available:", [a["name"] for a in avail])
    print("   current:", i0.get("after"))
    if avail:
        i1 = call("jawa/set_pawn_ideo", pawn=PID, action="certainty", certaintyOffset=-0.25)
        print("   certainty:", i1.get("before"), "->", i1.get("after"), i1.get("notes"))

print("\n== 3. GENES ==")
g0 = call("jawa/pawn_genes", pawn=PID, action="list")
print("   biotech:", g0.get("success"), (g0.get("message") or "")[:60])
if g0.get("success"):
    print("   xenotype:", g0.get("xenotype"), " endo:", g0.get("endogeneCount"), " xeno:", g0.get("xenogeneCount"))
    g1 = call("jawa/pawn_genes", pawn=PID, action="add", gene="Skin_Green")
    if not g1.get("success"): g1 = call("jawa/pawn_genes", pawn=PID, action="add", gene="Furskin")
    print("   add gene -> success:", g1.get("success"), (g1.get("message") or "")[:70])
    if g1.get("success"):
        print("   notes:", g1.get("notes"), " xenogenes:", g1.get("xenogenes")[-3:])

print("\n== 4. AGE - and the body-type mismatch warning ==")
a1 = call("jawa/set_pawn_age", pawn=PID, biologicalYears=9)
print("   success:", a1.get("success"))
print("   before:", a1.get("before"))
print("   after :", a1.get("after"))
print("   bodyTypeMismatch:", a1.get("bodyTypeMismatch"))
print("   warning:", (a1.get("warning") or "none"))
a2 = call("jawa/set_pawn_age", pawn=PID, biologicalYears=34)
print("   back to 34 -> lifeStage:", (a2.get("after") or {}).get("lifeStage"), " mismatch:", a2.get("bodyTypeMismatch"))

print("\n== 5. FACTION - move a colonist out and back ==")
f1 = call("jawa/set_pawn_faction", pawn=OTHER, faction="none")
print("   -> none: success:", f1.get("success"), " after:", f1.get("after"), " isColonist:", f1.get("isColonist"))
f2 = call("jawa/set_pawn_faction", pawn=OTHER, faction="player")
print("   -> player: success:", f2.get("success"), " after:", f2.get("after"), " isColonist:", f2.get("isColonist"))
f3 = call("jawa/set_pawn_faction", pawn=OTHER, faction="player")
print("   same-faction no-op refused:", not f3.get("success"), (f3.get("message") or "")[:90])
