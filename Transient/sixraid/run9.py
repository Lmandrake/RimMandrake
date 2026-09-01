# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    for F in ("Jawa_HuttCartel", "Pirate", "Empire"):
        rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Hostile"})
        l0 = rb.call("jawa/lord_pawn_move", {"action": "list"})
        f = rb.call("jawa/fire_raid", {"points": 3000, "faction": F, "dryRun": False,
                                       "strategy": "ImmediateAttack", "arrivalMode": "EdgeWalkIn"})
        l1 = rb.call("jawa/lord_pawn_move", {"action": "list"})
        lg = rb.call("jawa/drain_log", {"limit": 6, "contains": "Isekai"})
        print("### %-20s executed=%s arrived=%s lords %s -> %s" % (
            F, f.get("executed"), json.dumps(f.get("arrived")), l0.get("count"), l1.get("count")))
        print("    lords_after:", json.dumps(l1.get("lords"))[:600])
        for m in (lg.get("messages") or [])[-4:]:
            print("    ISEKAI:", (m.get("text") or "")[:220])
        rb.call("jawa/destroy_bulk", {"filter": "nonColonists", "dryRun": False})
        rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Neutral", "goodwill": 0})
