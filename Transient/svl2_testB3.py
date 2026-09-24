import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/set_current_map", {"mapId": 4})
    print("SET_MAP", json.dumps(r)[:600])

    lt = rb.call("jawa/list_things", {"rect": "0,0,100,100", "limit": 1500})
    things = lt.get("things", [])
    print("N_THINGS_RETURNED", len(things), "countMatched=", lt.get("countMatched"))
    from collections import Counter
    c = Counter(t.get("def") for t in things)
    for name, cnt in c.most_common(60):
        print("THING", name, cnt)

    lp = rb.call("jawa/list_pawns", {})
    allp = [p for p in lp.get("pawns", []) if p.get("faction") not in (None,)]
    print("N_PAWNS_ALL", len(lp.get("pawns", [])))
    for p in lp.get("pawns", []):
        print("PAWN", p.get("id"), p.get("defName"), p.get("kind"), p.get("faction"), p.get("x"), p.get("z"))
