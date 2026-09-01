# -*- coding: utf-8 -*-
"""Restore the relation state observed at the start of the session."""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=300) as rb:
    rb.call("jawa/destroy_bulk", {"filter": "nonColonists", "dryRun": False})
    for g in ("Pirate", "Empire"):
        print(rb.call("jawa/faction_relations_set",
                      {"faction": g, "other": "Player", "kind": "Hostile", "goodwill": -100}).get("message"))
    for f in rb.call("jawa/list_factions", {}).get("factions", []):
        print("  %-28s hostile=%s goodwill=%s" % (f["defName"], f["hostile"], f["goodwill"]))
    print("pawns on map:", rb.call("jawa/list_pawns", {"limit": 5}).get("totalOnMap"))
    print("paused:", rb.call("rimbridge/get_bridge_status", {}).get("state", {}).get("paused"))
