import sys, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
F = ["Jawa_HuttCartel","Jawa_FreeDroidEnclaves","Jawa_WildsteamClan","Jawa_DeepwaterCompact",
     "Jawa_GeonosianFoundryHive","Jawa_AscendantHelix","Jawa_Junkers"]
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/get_defs", {"defs":";".join("FactionDef/"+f for f in F),"fields":""})
    defs = r.get("defs") or []
    rows = {d["defName"]: d.get("fields",{}) for d in defs if d.get("found")}
    print("FOUND:", list(rows))
    keys = set()
    for v in rows.values(): keys |= set(v)
    hutt = rows.get("Jawa_HuttCartel",{})
    print("\n=== fields where Hutt DIFFERS from at least one other ===")
    for k in sorted(keys):
        vals = {n: json.dumps(v.get(k))[:80] for n,v in rows.items()}
        if len(set(vals.values())) > 1:
            print("*", k)
            for n in F:
                if n in vals: print("     ", n.ljust(28), vals[n])
