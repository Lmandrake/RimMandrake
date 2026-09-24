import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    pawns = rb.call("jawa/list_pawns", {})
    rows = pawns.get("pawns") or pawns.get("result", {}).get("pawns") or []
    print("TOTAL PAWNS", len(rows))
    by_fac = {}
    for r in rows:
        f = r.get("faction")
        by_fac.setdefault(f, []).append(r.get("name") or r.get("defName"))
    for f, names in by_fac.items():
        print(f, len(names), names[:6])

    ci = rb.call("rimworld/get_cell_info", {"x": 174, "z": 132})
    print("CELL_INFO_SAMPLE", json.dumps(ci)[:800])
