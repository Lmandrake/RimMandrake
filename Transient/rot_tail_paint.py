import sys, csv, json
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
live = {int(r['tile']): r for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\Transient\v24_tiles_live.csv'))}
tail = sorted(t for t,r in live.items() if r['biome']=='AB_MycoticJungle' and float(r['temperature']) < -42)
assert len(tail) == 90, len(tail)
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    w = rb.call("jawa/world_tile_set", {"tiles": ",".join(map(str, tail)), "biome": "RUT_NightsideIce", "readBack": 3})
    print("written:", w.get("written"), "| sample:", json.dumps(w.get("tiles", [])[:2]))
    c = rb.call("jawa/world_commit", {})
    print("commit:", c.get("success"), c.get("message", "")[:120])
    # verify: read all 90 back raw
    r = rb.call("jawa/world_tile_get", {"tiles": ",".join(map(str, tail)), "limit": 100})
    got = Counter(row['biome'] for row in r.get("tiles", []))
    print("readback of tail tiles:", dict(got), f"({sum(got.values())} rows)")
