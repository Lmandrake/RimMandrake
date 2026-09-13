"""BIOME_WORLD_SWITCH_WAVE_1 -- repaint Ash'karr's donor/vanilla tiles onto the
owned RUT_ BiomeDefs authored by BIOME_OWNERSHIP_WAVE_1 (cc11aee6e).

Mapping resolved from that commit's message plus each RUT_*.xml's own header
comment (every one names its donor explicitly). ZBiome_Grasslands is NOT here --
it rides PYRELANDS_WORLD_SWITCH_1 to RM_FE_Pyrelands.
"""
import sys, csv, json
from collections import Counter

sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

BEFORE = r"D:\Luke\dev\Rimworld\world\_bws\live_before.csv  (derived, not committed)"
AFTER = r"D:\Luke\dev\Rimworld\world\_bws\live_after.csv"

# donor -> owned. Ordered largest batch last so an early failure is cheap.
MAP = [
    ("Volcano", "RUT_TheForge"),
    ("LavaField", "RUT_TheForge"),
    ("AB_PyroclasticConflagration", "RUT_TheForge"),
    ("AB_TarPits", "RUT_Sump"),
    ("COMIGO_GreaterSwamp_Tropical", "RUT_FeverWood"),
    ("Scarlands", "RUT_Scarlands"),
    ("AB_MiasmicMangrove", "RUT_Miasma"),
    ("AB_GelatinousSuperorganism", "RUT_Slime"),
    ("AB_FeraliskInfestedJungle", "RUT_Webwork"),
    ("AB_OcularForest", "RUT_Contagion"),
    ("ZBiome_DesertOasis", "RUT_WeepingStones"),
    ("BiomeCypreJungle", "RUT_Greentide"),
    ("AB_MechanoidIntrusion", "RUT_RustCathedral"),
    ("PoisonForest", "RUT_PoisonForest"),
    ("AridShrubland", "RUT_AridShrubland"),
    ("ZBiome_Badlands", "RUT_CrackedLands"),
    ("AB_RockyCrags", "RUT_ForsakenCrags"),
    ("Wasteland", "RUT_Wasteland"),
    ("AB_MycoticJungle", "RUT_TheRot"),
    ("Desert", "RUT_Desert"),
    ("AB_PropaneLakes", "RUT_Umbra"),
    ("ExtremeDesert", "RUT_ExtremeDesert"),
]
CHUNK = 800

rows = list(csv.DictReader(open(BEFORE)))
assert len(rows) == 21872, len(rows)
by_donor = {}
for r in rows:
    by_donor.setdefault(r["biome"], []).append(int(r["tile"]))

host, port, token = resolve_endpoint()
report = []
with RimBridge(host, port, token) as rb:
    for donor, owned in MAP:
        tiles = by_donor.get(donor, [])
        if not tiles:
            print(f"SKIP {donor}: 0 tiles live")
            continue
        written = 0
        for i in range(0, len(tiles), CHUNK):
            part = tiles[i:i + CHUNK]
            w = rb.call("jawa/world_tile_set",
                        {"tiles": ",".join(str(t) for t in part), "biome": owned})
            if not w.get("success"):
                print(f"FAIL {donor}->{owned} chunk {i}: {w.get('message')}")
                sys.exit(1)
            written += w.get("written", 0)
        print(f"{donor:30s} -> {owned:20s} {len(tiles):5d} tiles, written {written}")
        report.append({"donor": donor, "owned": owned,
                       "tiles": len(tiles), "written": written})

    c = rb.call("jawa/world_commit", {})
    print("world_commit:", c.get("success"), c.get("message"))

    e = rb.call("jawa/world_tile_export", {"path": AFTER})
    print("export:", e.get("tilesTotal"), e.get("path"))

json.dump(report, open(r"D:\Luke\dev\Rimworld\world\_bws\report.json", "w"), indent=1)
