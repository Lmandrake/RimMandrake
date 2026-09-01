# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=180) as rb:
    print(json.dumps([t for t in rb.list_tools() if t.get("name") == "jawa/fire_incident"], default=str)[:1400])
    for F in ("Jawa_HuttCartel", "Empire"):
        rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Hostile"})
        for i in range(4):
            n0 = rb.call("jawa/list_pawns", {"limit": 5}).get("totalOnMap")
            r = rb.call("jawa/fire_incident", {"incidentDef": "RaidEnemy", "faction": F, "points": 3000, "dryRun": False})
            n1 = rb.call("jawa/list_pawns", {"limit": 5}).get("totalOnMap")
            print("%-18s fire_incident #%d  pawns %s->%s  keys=%s" % (F, i, n0, n1,
                  json.dumps({k: v for k, v in r.items() if k not in ("operation",)}, default=str)[:400]))
            rb.call("jawa/destroy_bulk", {"filter": "nonColonists", "dryRun": False})
        rb.call("jawa/faction_relations_set", {"faction": F, "other": "Player", "kind": "Neutral", "goodwill": 0})
