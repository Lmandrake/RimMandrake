"""BLUE_DESERT_WORLD_SWITCH_1 - repaint BiomeGRimond's 1029 tiles to RUT_BlueDesert.
Run with python.exe from the repo root: python.exe Transient/blue_desert_repaint.py
"""
import sys
import os

sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402

with open(os.path.join("world", "ASHKARR_WORLDMAP_tiles.csv"), encoding="utf-8") as f:
    import csv
    tiles = [row["tile"] for row in csv.DictReader(f) if row["biome"] == "BiomeGRimond"]
print("tiles to repaint:", len(tiles))

host, port, token = resolve_endpoint()
if not token:
    print("NO TOKEN - is the game running?")
    sys.exit(2)

with RimBridge(host, port, token) as rb:
    gi = rb.call("rimworld/get_game_info", {})
    print("status:", gi.get("status"), "ticks:", gi.get("ticksGame"))
    if gi.get("status") != "game_loaded":
        print("Game not loaded, aborting.")
        sys.exit(3)

    written_total = 0
    CHUNK = 400
    for i in range(0, len(tiles), CHUNK):
        chunk = tiles[i:i + CHUNK]
        r = rb.call("jawa/world_tile_set", {
            "tiles": ",".join(chunk),
            "biome": "RUT_BlueDesert",
            "readBack": 3,
        })
        print(f"chunk {i}-{i+len(chunk)}: success={r.get('success')} written={r.get('written')} errors={r.get('errors')}")
        for row in (r.get("tiles") or [])[:3]:
            print("   readback:", row)
        written_total += r.get("written") or 0

    print("TOTAL WRITTEN:", written_total)

    commit = rb.call("jawa/world_commit", {})
    print("world_commit:", commit.get("success"))

    # spot-check a handful of tiles read back fresh
    sample = ",".join(tiles[:5] + tiles[-5:])
    chk = rb.call("jawa/world_tile_get", {"tiles": sample})
    print("spot-check:", chk)
