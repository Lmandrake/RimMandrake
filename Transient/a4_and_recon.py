import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # A4: delete the one dead spur 21281->10451 (3 DirtRoad edges along the chain)
    g = rb.call("jawa/world_links_get", {"tiles": "21281,10451", "limit": 5})
    for t in g.get("tiles", []): print(t['tile'], "roads:", [(l['neighbor'], l['def']) for l in t.get('potentialRoads',[])])
    # find the chain: walk from 21281
    chain = [21281]
    seen = {21281}
    cur = 21281
    for _ in range(6):
        gt = rb.call("jawa/world_links_get", {"tiles": str(cur), "limit": 2}).get("tiles", [])
        if not gt: break
        nxt = [l['neighbor'] for l in gt[0].get('potentialRoads', []) if l['neighbor'] not in seen]
        if not nxt: break
        cur = nxt[0]; seen.add(cur); chain.append(cur)
        if cur == 10451: break
    print("chain:", chain)
    r = rb.call("jawa/world_links_clear", {"kind": "road", "tiles": ",".join(map(str, chain))})
    print("clear:", r.get("success"), r.get("cleared", r.get("message","")))
    rb.call("jawa/world_commit", {})
    # recon: colony map + ship layout needs
    gi = rb.call("rimworld/get_game_info", {})
    print("colony:", {k: gi.get(k) for k in ("colonyName","ticksGame")})
    objs = rb.call("jawa/world_objects_get", {"limit": 300})
    home = [o for o in objs.get("objects", []) if o.get("factionName") == "New Arrivals"]
    print("home:", home[:2])
