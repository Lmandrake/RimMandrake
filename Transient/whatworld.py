import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    gi = rb.call("rimworld/get_game_info", {})
    print("ticks:", gi.get("ticksGame"))
    p = rb.call("jawa/list_pawns", {"faction": "PlayerColony", "limit": 10})
    print("player pawns:", len(p.get("pawns", [])), [x.get("name") or x.get("label") for x in p.get("pawns", [])])
    eng = rb.call("jawa/list_things", {"defName": "GravEngine", "limit": 3}).get("things", [])
    print("gravship engine present:", len(eng))
    # is the punch-list world present? check the Zeddo ruin field (tile 17007 Junkyard) + Rot count
    m = rb.call("jawa/world_mutators_get", {"tiles": "17007", "limit": 2}).get("tiles", [])
    zeddo = [d['def'] for d in m[0]['mutators']] if m else []
    print("tile 17007 mutators (Zeddo ruin field):", zeddo)
    st = rb.call("jawa/world_stats", {})
    print("world tiles:", st.get("tilesTotal"))
