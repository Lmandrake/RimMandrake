import sys, json, math, csv, statistics
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
plan=json.load(open(r"D:\Luke\dev\Rimworld\world\_roads\ancient_straight_plan.json"))
geo={int(r['tile']):r for r in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"))}
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # 1. clear old ancient edges (precise, per-edge, kind=road)
    cok=0
    for a,b in plan['clear']:
        r=rb.call("jawa/world_links_clear", {"kind":"road","tiles":str(a),"to":b})
        cok+= 1 if r.get('success') else 0
    print(f"cleared {cok}/{len(plan['clear'])} old ancient edges")
    # 2. set new straight+dashed ancient edges
    sok=0
    for a,b in plan['set']:
        r=rb.call("jawa/world_links_set", {"kind":"road","path":f"{a},{b}","def":"AncientAsphaltHighway"})
        sok+= 1 if r.get('success') else 0
    print(f"set {sok}/{len(plan['set'])} new ancient edges")
    rb.call("jawa/world_commit", {})
    # verify: harvest ancient edges, measure sinuosity
    import collections
    anc=set()
    for lo in range(0,21872,3000):
        rr=rb.call("jawa/world_links_get", {"range":f"{lo}-{min(lo+2999,21871)}","limit":3500})
        for t in rr.get("tiles",[]):
            for e in (t.get("potentialRoads") or []):
                if 'AncientAsphalt' in e.get('def',''):
                    x,y=t['tile'],e['neighbor']; anc.add((min(x,y),max(x,y)))
    print(f"live ancient edges now: {len(anc)}")
