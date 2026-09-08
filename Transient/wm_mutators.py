import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    tl = {t["name"]: t for t in rb.list_tools()}
    print("== world_mutators_audit schema ==")
    print(json.dumps(tl["jawa/world_mutators_audit"].get("inputSchema"))[:700])
    print()
    a = rb.call("jawa/world_mutators_audit", {})
    d = {k: v for k, v in a.items() if k != "operation"}
    roster = None
    for k in ("roster", "mutators", "defs", "all"):
        if k in d:
            roster = d.pop(k)
            break
    print("== audit summary ==")
    print(json.dumps(d)[:1200])
    if roster:
        print("\n== water/lake-ish mutators in the live roster ==")
        for m in roster:
            name = m.get("defName") if isinstance(m, dict) else str(m)
            blob = json.dumps(m).lower() if isinstance(m, dict) else name.lower()
            if any(w in blob for w in ("lake", "water", "pond", "oasis", "marsh", "spring", "coast", "river", "ice")):
                print(json.dumps(m)[:400])
