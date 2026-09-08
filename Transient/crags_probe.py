import sys, json, collections, csv
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
crags=set(); 
for r in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv")):
    if r['biome']=='AB_RockyCrags': crags.add(int(r['tile']))
with RimBridge(host, port, token) as rb:
    muts=[]
    for lo in range(0,21872,5500):
        r=rb.call("jawa/world_mutators_get", {"range": f"{lo}-{min(lo+5499,21871)}", "limit": 6000})
        muts.extend(r.get("tiles", r.get("mutators", [])))
    per={}
    for m in muts:
        t=m.get("tile"); ds=m.get("mutators") or m.get("defs") or []
        if t in crags: per[t]=len(ds) if isinstance(ds,list) else 0
    covered=sum(1 for v in per.values() if v>0)
    hist=collections.Counter(per.values())
    print("crags tiles with mutator rows:", len(per), "| >=1 mutator:", covered, f"({round(100*covered/1984,1)}%)")
    print("mutator-count hist:", dict(sorted(hist.items())))
    rb.call("jawa/clear_ui", {})
    rb.call("jawa/world_view", {"centerTile": 3450 if 3450 in crags else next(iter(crags)), "altitude": 300})
    s=rb.call("rimworld/take_screenshot", {})
    print("shot:", s.get("path"))
