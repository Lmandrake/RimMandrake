import sys, json
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
tgt = next((p for p in lst["pawns"] if p.get("faction") == "PlayerColony"), lst["pawns"][0])
PID = str(tgt["thingIdNumber"])
before = call("jawa/pawn_get", pawn=PID)["pawns"][0]
print("pawn:", before["name"])
print("BEFORE childhood:", before["childhood"], " adulthood:", before["adulthood"])
dis0 = [s["skill"] for s in before["skills"] if s["disabled"]]
print("BEFORE disabled skills:", dis0)

b = call("jawa/set_pawn_backstory", pawn=PID, childhood="MedievalSlave49", adulthood="Novelist7")
print("\nsuccess:", b.get("success"), (b.get("message") or "")[:100])
print("before:", b.get("before"))
print("after :", b.get("after"))
print("refreshed:")
for r in (b.get("refreshed") or []): print("   ", r)
print("disabledWorkTypes:", b.get("disabledWorkTypes"))

after = call("jawa/pawn_get", pawn=PID)["pawns"][0]
dis1 = [s["skill"] for s in after["skills"] if s["disabled"]]
print("\nAFTER childhood:", after["childhood"], " adulthood:", after["adulthood"])
print("AFTER disabled skills:", dis1)
print("=> disabled-skill set changed:", dis0 != dis1, "(this is what the four refreshes buy)")
