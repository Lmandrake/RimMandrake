import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    info = rb.call("rimworld/get_game_info", {})
    print("GAME_INFO", json.dumps(info)[:2000])

    cols = rb.call("rimworld/list_colonists", {"currentMapOnly": True})
    print("COLONISTS_COUNT", len(cols.get("colonists", cols.get("pawns", []))))
    print("COLONISTS", json.dumps(cols)[:4000])

    pawns = rb.call("jawa/list_pawns", {})
    print("JAWA_PAWNS_COUNT", len(pawns.get("pawns", [])))
    # print factions summary
    from collections import Counter
    c = Counter()
    for p in pawns.get("pawns", []):
        c[p.get("faction")] += 1
    print("FACTION_COUNTS", dict(c))
    print("JAWA_PAWNS_SAMPLE", json.dumps(pawns.get("pawns", [])[:3])[:2000])
