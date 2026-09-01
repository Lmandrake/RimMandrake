# -*- coding: utf-8 -*-
"""raid_preview with exactly ONE hostile faction, so its usableStrategies are about THAT faction."""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
ALL = None
with RimBridge(host, port, token, timeout=180) as rb:
    ALL = [f["defName"] for f in rb.call("jawa/list_factions", {}).get("factions", []) if not f.get("isPlayer")]
    for F in ("Jawa_HuttCartel", "Empire", "Pirate", "OutlanderCivil"):
        for g in ALL:
            rb.call("jawa/faction_relations_set", {"faction": g, "other": "Player",
                                                   "kind": "Hostile" if g == F else "Neutral",
                                                   "goodwill": -100 if g == F else 0})
        pv = rb.call("jawa/raid_preview", {"points": 3000})
        print("### sole hostile =", F)
        print("   defaultParms:", json.dumps(pv.get("defaultParms")))
        print("   hostiles:", json.dumps(pv.get("hostileFactions")))
        print("   usable:", [s["def"] for s in pv.get("usableStrategies", [])])
        print("   notes:", pv.get("resolvedNotes"))
    for g in ALL:
        rb.call("jawa/faction_relations_set", {"faction": g, "other": "Player", "kind": "Neutral", "goodwill": 0})
