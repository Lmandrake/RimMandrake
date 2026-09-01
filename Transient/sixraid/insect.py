# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token, timeout=180) as rb:
    print(rb.call("jawa/faction_relations_set", {"faction": "Insect", "other": "Player",
                                                 "kind": "Hostile", "goodwill": -100}).get("message"))
