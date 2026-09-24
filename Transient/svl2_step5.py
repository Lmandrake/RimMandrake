import sys, json
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    info = rb.call("rimworld/get_game_info", {})
    print("GAME_INFO", json.dumps(info)[:1500])

    cols = rb.call("rimworld/list_colonists", {"currentMapOnly": True})
    colonists = cols.get("colonists", [])
    print("N_COLONISTS", len(colonists))
    for c in colonists:
        print("COL", c.get("name"), "job=", c.get("job"), "drafted=", c.get("drafted"),
              "downed=", c.get("downed"), "x=", c.get("x"), "z=", c.get("z"))

    pawns = rb.call("jawa/list_pawns", {})
    allp = pawns.get("pawns", [])
    print("N_ALL_PAWNS", len(allp))
    c = Counter()
    for p in allp:
        c[p.get("faction")] += 1
    print("FACTION_COUNTS", dict(c))
    for p in allp:
        fac = p.get("faction") or ""
        if fac and "player" not in fac.lower() and "jawa_free" not in fac.lower():
            print("HOSTILE_OR_OTHER", p.get("defName"), fac, p.get("x"), p.get("z"), p.get("downed"))
