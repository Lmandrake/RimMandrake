import sys, csv
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
live = {int(r['tile']): r['biome'] for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\Transient\v26_tiles_live.csv'))}
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/world_landmarks_get", {"def": "RUT_ComplexStructures", "limit": 500})
lms = r.get("landmarks", [])
print("ComplexStructures on planet:", len(lms))
cnt = Counter(live.get(l["tile"]) for l in lms)
for b, n in cnt.most_common(): print(f"  {n:4d}  {b}")
import json; json.dump([l["tile"] for l in lms], open(r'D:\Luke\dev\Rimworld\Transient\cs_tiles.json','w'))
