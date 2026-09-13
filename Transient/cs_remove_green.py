import sys, csv, json
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
GREEN = {'COMIGO_GreaterSwamp_Tropical','AB_MiasmicMangrove','BiomeCypreJungle','AB_OcularForest','AB_FeraliskInfestedJungle','ZBiome_Grasslands'}
live = {int(r['tile']): r['biome'] for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\Transient\v26_tiles_live.csv'))}
cs = json.load(open(r'D:\Luke\dev\Rimworld\Transient\cs_tiles.json'))
victims = [t for t in cs if live.get(t) in GREEN]
print("removing:", len(victims))
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/world_landmarks_set", {"action": "remove", "tiles": ",".join(map(str, victims))})
    print("removed:", r.get("removed"), "| success:", r.get("success"))
    c = rb.call("jawa/world_commit", {})
    print("commit:", c.get("success"))
    # verify
    g = rb.call("jawa/world_landmarks_get", {"def": "RUT_ComplexStructures", "limit": 500})
    lms = g.get("landmarks", [])
    left = Counter(live.get(l["tile"]) for l in lms)
    print("remaining:", len(lms), "| in green biomes:", sum(n for b,n in left.items() if b in GREEN))
    print(dict(left.most_common()))
    s = rb.call("rimworld/save_game", {"saveName": "WORLDMAP_V27_cs_icons_scoped_2026-09-09"})
    print("save:", s.get("saveName"), s.get("sizeBytes"))
