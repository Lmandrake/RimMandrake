import sys, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    c=collections.Counter()
    for i in range(0,21872,2000):
        rr=rb.call("jawa/world_tile_get", {"range": f"{i}-{min(i+1999,21871)}", "limit": 2500})
        for t in rr.get("tiles",[]): c[t["biome"]]+=1
    vanilla=[b for b in ('SeaIce','Lake','Ocean','IceSheet','BMT_FungalForest','BMT_CrystalCaverns','HorrorWastes') if c.get(b)]
    print("VANILLA STRAGGLERS remaining:", {b:c[b] for b in vanilla} or "NONE - clean")
    print("total biomes:", len(c), "| top:", c.most_common(6))
