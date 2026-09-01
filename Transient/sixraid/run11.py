# -*- coding: utf-8 -*-
"""Repeat-firing: is the empty result per-faction or intermittent?"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
N = 8
with RimBridge(host, port, token) as rb:
    for F in ("Pirate", "Empire", "Insect", "TradersGuild", "CASacrilegHunters", "Jawa_AscendantHelix", "Jawa_FreeDroidEnclaves"):
        rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Hostile"})
        got = []
        for i in range(N):
            r = rb.call("jawa/fire_raid", {"points": 3000, "faction": F, "dryRun": False,
                                           "strategy": "ImmediateAttack", "arrivalMode": "EdgeWalkIn"})
            arr = r.get("arrived") or []
            got.append(sum(a["pawnsArrived"] for a in arr if a["faction"] == F))
            rb.call("jawa/destroy_bulk", {"filter": "nonColonists", "dryRun": False})
        print("%-26s %s   hits=%d/%d" % (F, got, sum(1 for g in got if g), N))
        rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Neutral", "goodwill": 0})
