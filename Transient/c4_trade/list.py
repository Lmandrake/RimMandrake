import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
names=[]
with RimBridge(host, port, token) as rb:
    for cand in ("rimbridge/list_tools","tools/list","rimbridge/get_tools"):
        try:
            r = rb.call(cand, {})
        except Exception as e:
            print("ERR", cand, e); continue
        s=json.dumps(r)
        import re
        names = sorted(set(re.findall(r'"(?:jawa|rimworld|rimbridge)/[a-z_0-9]+', s)))
        names = [n.strip('"') for n in names]
        if names:
            print("VIA", cand, "count", len(names)); break
open("Transient/c4_trade/tools.txt","w").write("\n".join(names))
print("TRADE-ish:", [n for n in names if any(k in n for k in ("trade","trad","caravan","incident","quest","dialog","window","ui_"))])
