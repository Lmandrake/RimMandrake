import sys, json, collections
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
plan=json.load(open(r"D:\Luke\dev\Rimworld\world\crag_meander_plan.json"))
by_to=collections.defaultdict(list)
for p in plan: by_to[p['to']].append(p['tile'])
want={p['tile']:p['to'] for p in plan}
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    # links baseline (roads reband must not touch rivers) - none here, biome only
    for to,tiles in by_to.items():
        # chunk tiles into <=1500 per call
        for i in range(0,len(tiles),1500):
            chunk=tiles[i:i+1500]
            r=rb.call("jawa/world_tile_set", {"tiles": ",".join(map(str,chunk)), "biome": to, "readBack": 1})
            print(f"{to}: chunk {len(chunk)} -> written={r.get('written')} success={r.get('success')}")
    c=rb.call("jawa/world_commit", {})
    print("commit:", c.get("success"), c.get("failedSteps"))
    # read back the moved tiles and diff
    ok=0; bad=[]
    allids=list(want.keys())
    got={}
    for i in range(0,len(allids),2000):
        chunk=allids[i:i+2000]
        rr=rb.call("jawa/world_tile_get", {"tiles": ",".join(map(str,chunk)), "limit": 2500})
        for t in rr.get("tiles",[]): got[t["tile"]]=t["biome"]
    for tid,exp in want.items():
        if got.get(tid)==exp: ok+=1
        else: bad.append((tid,exp,got.get(tid)))
    print(f"READ BACK: {ok}/{len(want)} correct | wrong: {len(bad)}")
    if bad: print("  sample wrong:", bad[:5])
