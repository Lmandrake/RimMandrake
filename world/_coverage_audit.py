import sys, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    biome={}
    for i in range(0,21872,2000):
        rr=rb.call("jawa/world_tile_get", {"range": f"{i}-{min(i+1999,21871)}", "limit": 2500})
        for t in rr.get("tiles",[]): biome[t["tile"]]=t["biome"]
    lm=rb.call("jawa/world_landmarks_get", {"limit":6000})
    haslm={l['tile'] for l in lm.get("landmarks",[])}
    tot=collections.Counter(biome.values())
    cov=collections.Counter(biome[t] for t in haslm if t in biome)
    print("biome                    tiles  landmark%  (barren if <20% and >150 tiles)")
    for b,n in tot.most_common():
        if n<80: continue
        pc=round(100*cov.get(b,0)/n)
        flag=" <-- BARREN" if pc<20 and n>150 else ""
        print(f"  {b:24s} {n:5d}   {pc:3d}%{flag}")
