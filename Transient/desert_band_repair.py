"""WORLDMAP_DESERT_BAND_REPAIR_1 - retype Desert climate-outlier bands A and D.
Band A (arc<60, Desert) -> ExtremeDesert. Band D (arc>95, Desert) -> Wasteland.
Band C left untouched (owner call, per item file). Settlements exempted.
Run with python.exe from the repo root: python.exe Transient/desert_band_repair.py
"""
import sys, os, csv, json

sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402

TILES_CSV = os.path.join("world", "ASHKARR_WORLDMAP_tiles.csv")
SETTLE_CSV = os.path.join("world", "ASHKARR_WORLDMAP_settlements.csv")

rows = list(csv.DictReader(open(TILES_CSV, encoding="utf-8")))
settle_tiles = {r["tile"] for r in csv.DictReader(open(SETTLE_CSV, encoding="utf-8"))}


def band(arc):
    if arc < 60:
        return "A"
    if arc < 88:
        return "B"
    if arc < 95:
        return "C"
    return "D"


bandA = sorted({r["tile"] for r in rows if r["biome"] == "Desert" and band(float(r["arc"])) == "A"} - settle_tiles)
bandD = sorted({r["tile"] for r in rows if r["biome"] == "Desert" and band(float(r["arc"])) == "D"} - settle_tiles)

print("bandA (Desert->ExtremeDesert) candidates:", len(bandA))
print("bandD (Desert->Wasteland) candidates:", len(bandD))

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

    CHUNK = 400
    results = {"A": [], "D": []}

    for label, tiles, biome in (("A", bandA, "ExtremeDesert"), ("D", bandD, "Wasteland")):
        written_total = 0
        for i in range(0, len(tiles), CHUNK):
            chunk = tiles[i:i + CHUNK]
            r = rb.call("jawa/world_tile_set", {
                "tiles": ",".join(chunk),
                "biome": biome,
                "readBack": 3,
            })
            print(f"[{label}] chunk {i}-{i+len(chunk)}: success={r.get('success')} written={r.get('written')} errors={r.get('errors')}")
            for row in (r.get("tiles") or [])[:3]:
                print("   readback:", row)
            written_total += r.get("written") or 0
            results[label].append(r)
        print(f"[{label}] TOTAL WRITTEN:", written_total)

    commit = rb.call("jawa/world_commit", {})
    print("world_commit:", commit.get("success"))

    # spot-check
    sampleA = ",".join(bandA[:5] + bandA[-5:]) if bandA else ""
    sampleD = ",".join(bandD[:5] + bandD[-5:]) if bandD else ""
    if sampleA:
        print("spot-check A:", rb.call("jawa/world_tile_get", {"tiles": sampleA}))
    if sampleD:
        print("spot-check D:", rb.call("jawa/world_tile_get", {"tiles": sampleD}))

    # settlement tiles must be untouched - spot check a few
    settle_sample = ",".join(sorted(settle_tiles)[:5])
    print("settlement spot-check (should be unaffected):", rb.call("jawa/world_tile_get", {"tiles": settle_sample}))

    json.dump({"bandA": bandA, "bandD": bandD}, open(os.path.join("Transient", "desert_band_repair_applied_tiles.json"), "w"))
    print("Wrote Transient/desert_band_repair_applied_tiles.json")
