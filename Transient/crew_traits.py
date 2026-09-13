import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    d = rb.call("jawa/get_defs", {"defs": "TraitDef/IronWilled;TraitDef/Industriousness;TraitDef/ShootingAccuracy;TraitDef/TriggerHappy;TraitDef/SteadfastMind"})
    for row in d.get("defs", []):
        print(row.get("defName") or row.get("request"), "found:", row.get("found"))
    fixes = [("Human470521", "IronWilled", 0), ("Human470527", "Industriousness", 1), ("Human470530", "ShootingAccuracy", -1)]
    for pid, tr, deg in fixes:
        r = rb.call("jawa/pawn_traits", {"pawn": pid, "action": "add", "trait": tr, "degree": deg, "force": True})
        print(pid, tr, deg, "->", r.get("success"), str(r.get("message",""))[:60])
    for pid in ("Human470521","Human470524","Human470527","Human470530","Human470533"):
        t = rb.call("jawa/pawn_traits", {"pawn": pid, "action": "list"})
        print(pid, "traits:", [x.get("defName", x.get("trait")) if isinstance(x, dict) else x for x in t.get("traits", [])])
