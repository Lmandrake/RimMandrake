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
ps = [p for p in lst["pawns"] if p.get("faction") == "PlayerColony"]
PID = str(ps[0]["thingIdNumber"]); OTHER = str(ps[1]["thingIdNumber"]) if len(ps) > 1 else None
# find a real social ThoughtDef by asking the game
for cand in ("HadAngeringChat", "Insulted", "KindWords", "RebuffedMyInsult", "HarmedMe", "SocialFightMemory"):
    r = call("jawa/pawn_need", pawn=PID, action="thought", thought=cand)
    msg = (r.get("message") or "")
    if "No ThoughtDef" not in msg:
        print("social def found:", cand, "| success:", r.get("success"), "|", msg[:110])
        if not r.get("success") and OTHER:
            r2 = call("jawa/pawn_need", pawn=PID, action="thought", thought=cand, otherPawn=OTHER)
            print("   with otherPawn -> success:", r2.get("success"), r2.get("notes"))
        break
else:
    print("none of the candidate names exist")
