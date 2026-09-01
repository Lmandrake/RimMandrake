# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
F = "Jawa_HuttCartel"
with RimBridge(host, port, token) as rb:
    rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Hostile"})
    f = rb.call("jawa/fire_raid", {"points": 3000, "faction": F, "dryRun": False,
                                   "strategy": "ImmediateAttack", "arrivalMode": "EdgeWalkIn"})
    print("executed:", f.get("executed"), "arrived:", json.dumps(f.get("arrived")))
    for needle in ("Exception while generating pawn group",
                   "Got no pawns",
                   "Cannot generate pawns for",
                   "no usable PawnGroupMakers",
                   "Pawn generation error",
                   "Error while generating pawn",
                   "BetterRomance",
                   "NullReference"):
        r = rb.call("jawa/drain_log", {"limit": 8, "contains": needle})
        msgs = r.get("messages") or []
        print("### %-40s hits=%d" % (needle, len(msgs)))
        for m in msgs[-3:]:
            print("   [%s] %s" % (m.get("type"), (m.get("text") or "")[:1800]))
    rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Neutral", "goodwill": 0})
