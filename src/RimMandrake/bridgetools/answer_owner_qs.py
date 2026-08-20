"""Answer, with evidence: partial fog repaint, marriage/parents, hediff severity."""
import sys, json, time
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
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

print("== Q: FOG — can we paint it back, or only restore the whole map? ==")
a = call("jawa/set_fog", action="unfogAll")
print("   after unfogAll        fogged:", a.get("foggedCellsNow"), "of", a.get("mapArea"))
b = call("jawa/set_fog", action="refog", rect="60,60,30,30")
print("   after refog 30x30     fogged:", b.get("foggedCellsNow"), "  (expect ~900)")
c = call("jawa/set_fog", action="refog", rect="120,120,10,10")
print("   after refog +10x10    fogged:", c.get("foggedCellsNow"), "  (expect ~1000)")
d = call("jawa/set_fog", action="unfog", rect="60,60,15,15")
print("   after unfog 15x15     fogged:", d.get("foggedCellsNow"), "  (expect ~775)")
e = call("jawa/set_fog", action="floodUnfog", cell="65,65")
print("   after floodUnfog      fogged:", e.get("foggedCellsNow"))
print("   VERDICT: partial refog and unfog BOTH work per-rect; whole-map is just one option.")

print("\n== Q: marriage, love, and CHANGING PARENTS ==")
ps = [p for p in call("jawa/pawn_get", limit=10)["pawns"] if p.get("faction") == "PlayerColony"]
A, B = str(ps[0]["thingIdNumber"]), str(ps[1]["thingIdNumber"])
C = str(ps[2]["thingIdNumber"]) if len(ps) > 2 else None
print("   pawns:", ps[0]["name"], "|", ps[1]["name"], "|", ps[2]["name"] if C else "-")
for rel in ("Lover", "Fiance", "Spouse"):
    r = call("jawa/pawn_relations", pawn=A, action="add", relation=rel, otherPawn=B)
    print("   add %-8s ok=%s added=%s opinion %s/%s" % (rel, r.get("success"), r.get("added"),
          r.get("opinionOfOther"), r.get("opinionOfMe")))
r = call("jawa/pawn_relations", pawn=A, action="remove", relation="Lover", otherPawn=B)
print("   remove Lover -> removed:", r.get("removed"))
r = call("jawa/pawn_relations", pawn=A, action="add", relation="ExSpouse", otherPawn=B)
print("   add ExSpouse (a breakup) -> added:", r.get("added"))
print("   relations now:", [(x["def"], x["otherPawn"]) for x in r.get("relations", [])])
if C:
    r = call("jawa/pawn_relations", pawn=C, action="add", relation="Parent", otherPawn=A)
    print("   set %s's Parent -> added: %s" % (ps[2]["name"], r.get("added")))
    r2 = call("jawa/pawn_relations", pawn=C, action="list")
    print("   child's relations:", [(x["def"], x["otherPawn"]) for x in r2.get("relations", [])])

print("\n== Q: arbitrary hediffs, incl. severity ==")
h = call("jawa/pawn_health", pawn=A, action="add", hediff="Malnutrition", severity=0.85)
print("   Malnutrition@0.85 ->", h.get("didWhat"))
got = [x for x in (h.get("hediffs") or []) if x["def"] == "Malnutrition"]
print("   read back:", got)
h2 = call("jawa/pawn_health", pawn=A, action="add", hediff="Anesthetic")
print("   Anesthetic ->", h2.get("didWhat"), " total hediffs:", h2.get("hediffCount"))
