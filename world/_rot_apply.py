import sys, collections, hashlib
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
def h(t,s): return int(hashlib.md5(f"{t}:{s}".encode()).hexdigest(),16)
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rot=[]
    for i in range(0,21872,2000):
        rr=rb.call("jawa/world_tile_get", {"range": f"{i}-{min(i+1999,21871)}", "limit": 2500})
        for t in rr.get("tiles",[]):
            if t["biome"]=="AB_MycoticJungle": rot.append(t["tile"])
    lm=rb.call("jawa/world_landmarks_get", {"limit":4000})
    haslm={l['tile'] for l in lm.get("landmarks",[])}
    # fungal-jungle landmark density: Cavern (hollows), Cenotes (pools), Valley (jungle folds)
    plan={}
    for t in rot:
        if t in haslm: continue
        if h(t,'cover')%100 >= 38: continue          # ~38% coverage, hash-gapped
        r=h(t,'def')%100
        plan[t] = 'Cavern' if r<48 else 'VEE_Cenotes' if r<78 else 'Valley'
    print(f"Rot density plan: {len(plan)} landmarks | {dict(collections.Counter(plan.values()))}")
    for d in set(plan.values()):
        tiles=[t for t,dd in plan.items() if dd==d]
        for i in range(0,len(tiles),800):
            ch=tiles[i:i+800]
            rr=rb.call("jawa/world_landmarks_set", {"tiles":",".join(map(str,ch)),"def":d})
            print(f"  {d}: +{rr.get('added')}")
    rb.call("jawa/world_commit", {})
    lm2=rb.call("jawa/world_landmarks_get", {"limit":6000})
    got={l['tile']:l['def'] for l in lm2.get("landmarks",[])}
    ok=sum(1 for t,d in plan.items() if got.get(t)==d)
    print(f"READ BACK: {ok}/{len(plan)} | Rot coverage now ~{round(100*(84+ok)/2348)}%")
