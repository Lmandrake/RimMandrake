import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
SPINE=[12253,15934,107,7924,1445,15951,9023]
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rr=rb.call("jawa/world_tile_get", {"tiles":",".join(map(str,SPINE)), "limit":10})
    info={t['tile']:t for t in rr.get("tiles",[])}
    for t in SPINE:
        i=info.get(t,{})
        print(f"  {t}: biome={i.get('biome')} temp={i.get('temperature')} hill={i.get('hilliness')} water={i.get('waterCovered')}")
    land=[t for t in SPINE if not info.get(t,{}).get('waterCovered')]
    rb.call("jawa/world_landmarks_set", {"tiles":",".join(map(str,land)), "def":"Chasm"})
    rb.call("jawa/world_commit", {})
    lm=rb.call("jawa/world_landmarks_get", {"limit":4000})
    got={l['tile']:l['def'] for l in lm.get("landmarks",[])}
    print("LIGHTFALL chasm tiles now:", [t for t in SPINE if got.get(t)=='Chasm'])
