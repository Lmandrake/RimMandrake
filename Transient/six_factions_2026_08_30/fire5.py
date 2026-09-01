import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
NEEDLES = ["Cannot generate pawns", "Defaulting to a single random cheap group",
           "Hostile group incoming", "Processed", "cooldown", "Cooldown",
           "MirrorImage", "Tabula", "CanGenerateFrom", "Exception", "NullReference"]
def txt(rb, sub, lim=25):
    r = rb.call("jawa/drain_log", {"limit":lim, "contains":sub})
    return [ (m.get("text") or "") for m in (r.get("messages") or []) ]
def lords(rb): return rb.call("jawa/lord_pawn_move", {"action":"list"}).get("count",0)
with RimBridge(host, port, token) as rb:
    rb.call("jawa/destroy_bulk", {"filter":"nonColonists","dryRun":False})
    base = {n: len(txt(rb,n,60)) for n in NEEDLES}
    print("BASELINE", base)
    lb=lords(rb)
    r = rb.call("jawa/fire_raid", {"faction":"Pirate","points":3000,"strategy":"ImmediateAttack",
                                   "arrivalMode":"EdgeWalkIn","dryRun":False})
    time.sleep(2.0)
    print("PIRATE lords %d->%d arrived=%s executed=%s" % (lb, lords(rb), json.dumps(r.get("arrived")), r.get("executed")))
    for n in NEEDLES:
        rows = txt(rb,n,60)
        if len(rows) != base[n] or n in ("Cannot generate pawns","Defaulting to a single random cheap group","Hostile group incoming"):
            print("  %-42s %d -> %d" % (n, base[n], len(rows)))
            for m in rows[-3:]: print("       |", m[:180])
    print("\nFULL RESP:", json.dumps(r, ensure_ascii=False)[:1400])
