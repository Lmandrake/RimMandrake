# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
WANT = {"jawa/list_pawns", "jawa/drain_log", "rimworld/step_game_ticks", "jawa/destroy_batch",
        "rimworld/list_things", "jawa/list_things"}
with RimBridge(host, port, token) as rb:
    for t in rb.list_tools():
        n = t.get("name")
        if n in WANT or ("step" in n) or ("destroy" in n) or ("list_things" in n):
            print("###", n)
            print(json.dumps(t.get("inputSchema") or t.get("input_schema") or t, default=str)[:1500])
