# -*- coding: utf-8 -*-
"""Fire at EVERY faction in the world; tabulate who actually spawns pawns."""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    facs = [f for f in rb.call("jawa/list_factions", {}).get("factions", []) if not f.get("isPlayer")]
    print("%-26s %-6s %-8s %s" % ("faction", "arriv", "lords+", "kinds"))
    for f in facs:
        F = f["defName"]
        rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Hostile"})
        l0 = rb.call("jawa/lord_pawn_move", {"action": "list"}).get("count")
        r = rb.call("jawa/fire_raid", {"points": 3000, "faction": F, "dryRun": False,
                                       "strategy": "ImmediateAttack", "arrivalMode": "EdgeWalkIn"})
        l1 = rb.call("jawa/lord_pawn_move", {"action": "list"}).get("count")
        arr = r.get("arrived") or []
        n = sum(a["pawnsArrived"] for a in arr)
        who = ",".join(a["faction"] for a in arr)
        print("%-26s %-6s %-8s exec=%s sub=%s who=%s" % (
            F, n, "%s->%s" % (l0, l1), r.get("executed"),
            r.get("actual", {}).get("substituted"), who))
        rb.call("jawa/destroy_bulk", {"filter": "nonColonists", "dryRun": False})
        rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Neutral", "goodwill": 0})
