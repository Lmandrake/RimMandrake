import sys, csv, json
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
tiles = "2796,9224,9241,12462,14343,17304,19390,19391"
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    w = rb.call("jawa/world_tile_set", {"tiles": tiles, "biome": "BiomeCypreJungle", "readBack": 1})
    print("written:", w.get("written"))
    c = rb.call("jawa/world_commit", {})
    print("commit:", c.get("success"))
    r = rb.call("jawa/world_tile_get", {"tiles": tiles, "limit": 10})
    print("readback:", dict(Counter(row['biome'] for row in r.get("tiles", []))))
    # verify counts + save
    e = rb.call("jawa/world_tile_export", {"path": r"D:\Luke\dev\Rimworld\Transient\v26_tiles_live.csv"})
    print("export:", e.get("tilesTotal"))
    s = rb.call("rimworld/save_game", {"saveName": "WORLDMAP_V26_webwork_rivers_2026-09-09"})
    print("save:", s.get("saveName"), s.get("sizeBytes"))
