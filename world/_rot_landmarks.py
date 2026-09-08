import sys, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rot=set()
    for i in range(0,21872,2000):
        rr=rb.call("jawa/world_tile_get", {"range": f"{i}-{min(i+1999,21871)}", "limit": 2500})
        for t in rr.get("tiles",[]):
            if t["biome"]=="AB_MycoticJungle": rot.add(t["tile"])
    lm=rb.call("jawa/world_landmarks_get", {"limit":4000})
    haslm={l['tile']:l['def'] for l in lm.get("landmarks",[])}
    onrot=[haslm[t] for t in rot if t in haslm]
    print(f"Rot tiles: {len(rot)} | landmark coverage: {len(onrot)}/{len(rot)} = {round(100*len(onrot)/len(rot),1)}%")
    print("Rot landmarks by def:", collections.Counter(onrot).most_common(8))
    # available landmark defs (what's placed anywhere - shows valid defs)
    print("all landmark defs on the planet:", collections.Counter(haslm.values()).most_common(20))
