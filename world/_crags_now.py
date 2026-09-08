import sys, json, collections, csv, statistics
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
geo={int(r['tile']):r for r in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"))}
with RimBridge(host, port, token) as rb:
    live={}
    for i in range(0,21872,2000):
        rr=rb.call("jawa/world_tile_get", {"range": f"{i}-{min(i+1999,21871)}", "limit": 2500})
        for t in rr.get("tiles",[]): live[t["tile"]]=t["biome"]
    crags=[t for t,b in live.items() if b=='AB_RockyCrags']
    A=lambda t:float(geo[t]['arc']); T=lambda t:float(geo[t]['temp_c'])
    print(f"CRAGS live: {len(crags)} tiles | temp med {statistics.median([T(t) for t in crags]):.1f} ({min(T(t) for t in crags):.0f}..{max(T(t) for t in crags):.0f}) | arc med {statistics.median([A(t) for t in crags]):.0f}")
    print("  regions:", collections.Counter(geo[t]['region'] for t in crags).most_common(10))
    # mutator density on crags
    muts={}
    for lo in range(0,21872,5500):
        r=rb.call("jawa/world_mutators_get", {"range": f"{lo}-{min(lo+5499,21871)}", "limit": 6000})
        for m in r.get("tiles", r.get("mutators", [])):
            t=m.get("tile"); ds=m.get("mutators") or m.get("defs") or []
            if t in set(crags): muts[t]=len(ds) if isinstance(ds,list) else 0
    cov=sum(1 for v in muts.values() if v>0)
    print(f"  mutator coverage: {cov}/{len(crags)} = {round(100*cov/len(crags))}% | hist {dict(sorted(collections.Counter(muts.values()).items()))}")
    # landmark coverage
    lm=rb.call("jawa/world_landmarks_get", {"limit":3000})
    lmt={l['tile'] for l in lm.get("landmarks",[])}
    cl=sum(1 for t in crags if t in lmt)
    print(f"  landmark coverage: {cl}/{len(crags)} = {round(100*cl/len(crags),1)}%")
    bydef=collections.Counter(l['def'] for l in lm.get("landmarks",[]) if l['tile'] in set(crags))
    print("  crag landmarks by def:", bydef.most_common(8))
