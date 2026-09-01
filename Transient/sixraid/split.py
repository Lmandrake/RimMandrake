# -*- coding: utf-8 -*-
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
FAIL = ["Pirate", "CASacrilegHunters", "Jawa_HuttCartel", "Jawa_Junkers",
        "Jawa_FreeDroidEnclaves", "Jawa_AscendantHelix", "Jawa_IndigenousTribes"]
WORK = ["Empire", "Insect", "OutlanderCivil", "TribeCivil"]
NAMES = FAIL + WORK
with RimBridge(host, port, token, timeout=300) as rb:
    r = rb.call("jawa/get_defs", {"defs": ";".join("FactionDef/" + n for n in NAMES), "limit": 50})
rows = {d["defName"]: d.get("fields", {}) for d in r.get("defs", []) if d.get("found")}
keys = sorted(set().union(*[set(v) for v in rows.values()]))
print("candidates (all FAIL agree, no WORK matches):")
for k in keys:
    v = {n: json.dumps(rows.get(n, {}).get(k), default=str, sort_keys=True) for n in NAMES}
    f = {v[n] for n in FAIL}
    w = {v[n] for n in WORK}
    if len(f) == 1 and f.isdisjoint(w):
        print("  %-38s FAIL=%s  WORK=%s" % (k, list(f)[0][:50], json.dumps({n: v[n] for n in WORK})[:200]))
print()
print("candidates (all WORK agree, no FAIL matches):")
for k in keys:
    v = {n: json.dumps(rows.get(n, {}).get(k), default=str, sort_keys=True) for n in NAMES}
    f = {v[n] for n in FAIL}
    w = {v[n] for n in WORK}
    if len(w) == 1 and w.isdisjoint(f):
        print("  %-38s WORK=%s  FAIL=%s" % (k, list(w)[0][:50], json.dumps({n: v[n] for n in FAIL})[:260]))
