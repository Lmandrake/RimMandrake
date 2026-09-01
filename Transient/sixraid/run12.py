# -*- coding: utf-8 -*-
"""Points sweep: is the empty group a cost gate?"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
PTS = [70, 150, 400, 1000, 3000, 10000, 30000]
with RimBridge(host, port, token) as rb:
    for F in ("Jawa_HuttCartel", "Jawa_IndigenousTribes", "OutlanderCivil"):
        rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Hostile"})
        row = []
        for p in PTS:
            r = rb.call("jawa/fire_raid", {"points": p, "faction": F, "dryRun": False,
                                           "strategy": "ImmediateAttack", "arrivalMode": "EdgeWalkIn"})
            arr = r.get("arrived") or []
            row.append((p, sum(a["pawnsArrived"] for a in arr if a["faction"] == F)))
            rb.call("jawa/destroy_bulk", {"filter": "nonColonists", "dryRun": False})
        print("%-24s %s" % (F, row))
        rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Neutral", "goodwill": 0})
