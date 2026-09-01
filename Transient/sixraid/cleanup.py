# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=300) as rb:
    print(rb.call("jawa/destroy_bulk", {"filter": "nonColonists", "dryRun": False}).get("message"))
    for f in rb.call("jawa/list_factions", {}).get("factions", []):
        if f.get("isPlayer"):
            continue
        r = rb.call("jawa/faction_relations_set",
                    {"faction": f["defName"], "other": "Player", "kind": "Neutral", "goodwill": 0})
    fl = rb.call("jawa/list_factions", {})
    print([(x["defName"], x["hostile"], x["goodwill"]) for x in fl.get("factions", [])])
    print("pawns:", rb.call("jawa/list_pawns", {"limit": 10}).get("totalOnMap"))
    names = sorted(t.get("name") for t in rb.list_tools())
    print("DEF TOOLS:", [n for n in names if "def" in n.lower() or "xenotype" in n.lower()])
