# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/list_pawns", {"limit": 500})
    print("keys:", sorted(r.keys()))
    print(json.dumps({k: v for k, v in r.items() if k != "operation"}, default=str)[:2500])
    t = rb.call("jawa/list_things", {"defName": "DropPodIncoming", "limit": 20})
    print("things keys:", sorted(t.keys()))
    print(json.dumps({k: v for k, v in t.items() if k != "operation"}, default=str)[:1200])
