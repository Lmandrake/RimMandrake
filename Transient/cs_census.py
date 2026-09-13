import sys, csv
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
live = {int(r['tile']): r['biome'] for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\Transient\v26_tiles_live.csv'))}
host, port, token = resolve_endpoint()
rows, seen = [], set()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/world_landmarks_get", {"limit": 500})
    lms = r.get("landmarks", [])
    print("returned:", len(lms), "| reported total:", r.get("total") or r.get("count"))
    cs = [l for l in lms if l.get("def")=="RUT_ComplexStructures"]
    print("ComplexStructures returned:", len(cs))
    print("by biome:", dict(Counter(live.get(l["tile"]) for l in cs).most_common()))
