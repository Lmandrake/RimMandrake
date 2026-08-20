import sys, json
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rb
host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=300.0); S.connect()
def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
lst = call("jawa/pawn_get", limit=8)
ps = [p for p in lst["pawns"] if p.get("faction") == "PlayerColony"]
PID = str(ps[0]["thingIdNumber"]); OTHER = str(ps[1]["thingIdNumber"])

print("== A. why did Sibling fail? ==")
for rel in ("Sibling", "Parent", "Child", "Spouse", "Lover", "Fiance"):
    r = call("jawa/pawn_relations", pawn=PID, action="add", relation=rel, otherPawn=OTHER)
    print("   %-8s success=%s added=%s %s" % (rel, r.get("success"), r.get("added"), (r.get("message") or "")[:80]))
    if r.get("success") and r.get("added"):
        print("      opinion:", r.get("opinionOfOther"), "/", r.get("opinionOfMe"))
        print("      relations:", [(x["def"], x["otherPawn"]) for x in r.get("relations", [])])
        break

print("\n== B. does DebugSetAge refuse to go BACKWARDS? ==")
cur = call("jawa/pawn_get", pawn=PID)["pawns"][0]["ageBiologicalYears"]
print("   current age:", cur)
up = call("jawa/set_pawn_age", pawn=PID, biologicalYears=cur + 20)
print("   +20 forward -> before %s after %s" % (up["before"]["biologicalYears"], up["after"]["biologicalYears"]))
down = call("jawa/set_pawn_age", pawn=PID, biologicalYears=8)
print("   ->8 backward-> before %s after %s  mismatch=%s" % (
    down["before"]["biologicalYears"], down["after"]["biologicalYears"], down.get("bodyTypeMismatch")))
print("   VERDICT: DebugSetAge is %s" % ("FORWARD-ONLY" if down["after"]["biologicalYears"] >= down["before"]["biologicalYears"] else "bidirectional"))
