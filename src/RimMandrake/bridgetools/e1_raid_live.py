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
before = call("jawa/pawn_get", limit=60)
fb = sorted(set(str(p.get("faction")) for p in before["pawns"]))
print("BEFORE pawns:", before.get("count"), " factions:", fb)

print("\nfiring RaidEnemy 1200 pts, ImmediateAttack, EdgeWalkIn ...")
live = call("jawa/fire_raid", points=1200, strategy="ImmediateAttack",
            arrivalMode="EdgeWalkIn", dryRun=False)
print("  success:", live.get("success"), " executed:", live.get("executed"))
print("  resolved:", live.get("resolved"))
print("  factionNotes:", live.get("factionNotes"))
print("  note:", live.get("note"))

call("rimworld/step_game_ticks", ticks=120)
after = call("jawa/pawn_get", limit=80)
fa = sorted(set(str(p.get("faction")) for p in after["pawns"]))
print("\nAFTER pawns:", after.get("count"), " factions:", fa)
new = after.get("count", 0) - before.get("count", 0)
print("DELTA pawns: %+d" % new)
raiders = [p for p in after["pawns"] if p.get("faction") not in ("PlayerColony", None)]
print("non-player pawns on map:", len(raiders))
for r in raiders[:5]: print("   ", r["name"], r["faction"], "at", r.get("x"), r.get("z"))
