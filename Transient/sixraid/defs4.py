# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
NAMES = ["Jawa_HuttCartel", "Jawa_Junkers", "Jawa_FreeDroidEnclaves",
         "OutlanderCivil", "TribeCivil", "Empire", "Pirate"]
with RimBridge(host, port, token, timeout=300) as rb:
    r = rb.call("jawa/get_defs", {"defs": ";".join("FactionDef/" + n for n in NAMES), "limit": 50})
rows = {d["defName"]: d.get("fields", {}) for d in r.get("defs", []) if d.get("found")}
keys = sorted(set().union(*[set(v) for v in rows.values()]))
diff = []
for k in keys:
    vals = {n: json.dumps(rows.get(n, {}).get(k), default=str, sort_keys=True) for n in NAMES}
    jawa = {vals[n] for n in NAMES if n.startswith("Jawa_")}
    van = {vals[n] for n in NAMES if not n.startswith("Jawa_")}
    if len(jawa) == 1 and jawa.isdisjoint(van):
        diff.append((k, list(jawa)[0], {n: vals[n] for n in NAMES if not n.startswith("Jawa_")}))
print("FIELDS WHERE ALL JAWA AGREE AND NO VANILLA MATCHES:")
for k, j, v in diff:
    print("  %-40s jawa=%s   vanilla=%s" % (k, json.dumps(j, default=str)[:60], json.dumps(v, default=str)[:200]))
print()
print("ALL FIELDS:", len(keys))
with open(r"D:\Luke\dev\Rimworld\Transient\sixraid\defs4.json", "w", encoding="utf-8") as fh:
    json.dump(rows, fh, indent=1, default=str, ensure_ascii=False)
