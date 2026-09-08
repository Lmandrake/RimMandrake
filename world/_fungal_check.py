import sys, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    live=collections.Counter()
    for i in range(0,21872,2000):
        rr=rb.call("jawa/world_tile_get", {"range": f"{i}-{min(i+1999,21871)}", "limit": 2500})
        for t in rr.get("tiles",[]): live[t["biome"]]+=1
    print("LIVE BMT_FungalForest:", live.get('BMT_FungalForest',0))
    print("LIVE AB_MycoticJungle (the Rot):", live.get('AB_MycoticJungle',0))
    print("all BMT_ / other suspicious biomes:", {b:n for b,n in live.items() if b.startswith('BMT_') or b in ('HorrorWastes','Ocean','SeaIce','IceSheet','Lake','BMT_CrystalCaverns')})
