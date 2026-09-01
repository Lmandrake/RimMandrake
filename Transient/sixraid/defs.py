# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
OUT = r"D:\Luke\dev\Rimworld\Transient\sixraid\defs.json"
out = {}
with RimBridge(host, port, token, timeout=300) as rb:
    print(json.dumps([t for t in rb.list_tools() if t.get("name") == "jawa/get_def"], default=str)[:1200])
    for d in ("Jawa_HuttCartel", "OutlanderCivil", "Empire", "Pirate", "Jawa_IndigenousTribes"):
        try:
            r = rb.call("jawa/get_def", {"defType": "FactionDef", "defName": d})
        except Exception as e:
            print("ERR", d, e); continue
        out[d] = r
        print("###", d, "keys:", sorted(k for k in r.keys() if k != "operation"))
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1, default=str, ensure_ascii=False)
print("->", OUT)
