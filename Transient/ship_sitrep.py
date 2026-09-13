import sys
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    p = rb.call("jawa/list_pawns", {"limit": 100})
    pawns = p.get("pawns", [])
    print("pawns:", len(pawns))
    print(Counter(x.get("faction") for x in pawns).most_common())
    for x in pawns:
        if x.get("faction") == "PlayerColony":
            print("  COLONIST:", x.get("id"), x.get("name") or x.get("label"), "at", x.get("x"), x.get("z"), "downed:", x.get("downed"), "dead:", x.get("dead"))
    hostiles = [x for x in pawns if x.get("hostile")]
    print("hostile-flagged:", len(hostiles), [(x.get("def"), x.get("x"), x.get("z")) for x in hostiles][:8])
    g = rb.call("rimworld/get_game_info", {})
    print("ticks:", g.get("ticksGame"))
