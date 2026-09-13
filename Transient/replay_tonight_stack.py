"""Replay tonight's full world-edit stack onto the LOADED save (gravship_f), then verify.
Deterministic: every selection recomputed from the same criteria as the original edits."""
import sys, json, csv, time
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
GREEN = {'COMIGO_GreaterSwamp_Tropical','AB_MiasmicMangrove','BiomeCypreJungle','AB_OcularForest','AB_FeraliskInfestedJungle','ZBiome_Grasslands'}
ok = True
def chk(name, got, want):
    global ok
    good = got == want
    if not good: ok = False
    print(("  OK  " if good else "  FAIL") + f" {name}: {got} (want {want})", flush=True)

with RimBridge(host, port, token) as rb:
    # 1. Rot cold tail -> NightsideIce (criteria identical to the ruled edit)
    rb.call("jawa/world_tile_export", {"path": r"D:\Luke\dev\Rimworld\Transient\replay_base.csv"})
    base = {int(r['tile']): r for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\Transient\replay_base.csv'))}
    tail = sorted(t for t,r in base.items() if r['biome']=='AB_MycoticJungle' and float(r['temperature']) < -42)
    print("rot tail:", len(tail), flush=True)
    if tail:
        rb.call("jawa/world_tile_set", {"tiles": ",".join(map(str,tail)), "biome": "RUT_NightsideIce", "readBack": 1})
    # 2. Webwork 8 -> Greentide
    WW = "2796,9224,9241,12462,14343,17304,19390,19391"
    rb.call("jawa/world_tile_set", {"tiles": WW, "biome": "BiomeCypreJungle", "readBack": 1})
    # 3. CS landmarks out of green biomes (post-repaint biomes)
    rb.call("jawa/world_tile_export", {"path": r"D:\Luke\dev\Rimworld\Transient\replay_mid.csv"})
    mid = {int(r['tile']): r['biome'] for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\Transient\replay_mid.csv'))}
    cs = rb.call("jawa/world_landmarks_get", {"def": "RUT_ComplexStructures", "limit": 500}).get("landmarks", [])
    victims = [l['tile'] for l in cs if mid.get(l['tile']) in GREEN]
    print("cs victims:", len(victims), flush=True)
    if victims:
        rb.call("jawa/world_landmarks_set", {"action": "remove", "tiles": ",".join(map(str,victims))})
    # 4. coastal mutators
    for d, tiles in (("CoastalIsland","239,361,3507,4569"),("Archipelago","2249,13203"),("Peninsula","11851")):
        rb.call("jawa/world_mutators_set", {"action": "remove", "mutators": d, "tiles": tiles})
    # 5. Zeddo ruin field
    PLAN = {17007:"Junkyard,AB_DerelictClusters,VEE_MechanoidShipChunks",1621:"Junkyard,AncientWarehouse",
            17011:"Junkyard,VEE_MechanoidShipChunks",17008:"AncientRuins,VEE_MechanoidShipChunks",
            17009:"AB_DerelictClusters,AncientRuins",8100:"AncientWarehouse",8096:"VEE_MechanoidShipChunks",3241:"AncientRuins"}
    for tile, defs in PLAN.items():
        rb.call("jawa/world_mutators_set", {"action": "add", "mutators": defs, "tiles": str(tile)})
    for tile, lm in ((17007,"Ruins"),(17009,"Ruins"),(1621,"AncientGarrison")):
        rb.call("jawa/world_landmarks_set", {"action": "add", "def": lm, "tiles": str(tile)})
    # 6. links rebuild + cycle edges
    r = rb.call("jawa/world_links_import", {"path": r"D:\Luke\dev\Rimworld\Transient\final_review\links_rebuilt.csv",
                                            "apply": True, "clearFirst": True, "expectTiles": 21872})
    print("links import:", r.get("rivers"), r.get("roads"), r.get("nonAdjacentRefused"), flush=True)
    g = rb.call("jawa/world_links_get", {"tiles": "2793,7653,14319,14323", "limit": 10})
    dist = {t['tile']: t['riverDist'] for t in g.get('tiles', [])}
    for a,b in ((2793,7653),(14319,14323)):
        lo,hi = (a,b) if dist.get(a,0)<=dist.get(b,0) else (b,a)
        rb.call("jawa/world_links_set", {"kind":"river","path":f"{lo},{hi}","def":"Creek"})
    # 7. Spine label
    rb.call("jawa/world_features_set", {"action":"edit","featureId":67,"drawAngle":35})
    rb.call("jawa/world_commit", {})
    time.sleep(1)
    # VERIFY
    rb.call("jawa/world_tile_export", {"path": r"D:\Luke\dev\Rimworld\Transient\replay_after.csv"})
    after = Counter(r['biome'] for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\Transient\replay_after.csv')))
    chk("AB_MycoticJungle", after['AB_MycoticJungle'], 2258)
    chk("RUT_NightsideIce", after['RUT_NightsideIce'], 1506)
    chk("BiomeCypreJungle", after['BiomeCypreJungle'], 235)
    chk("AB_FeraliskInfestedJungle", after['AB_FeraliskInfestedJungle'], 161)
    cs2 = rb.call("jawa/world_landmarks_get", {"def": "RUT_ComplexStructures", "limit": 500}).get("landmarks", [])
    chk("CS landmarks", len(cs2), 77)
    m = rb.call("jawa/world_mutators_get", {"tiles": "17007", "limit": 2}).get("tiles", [])
    have = sorted(d['def'] for d in m[0]['mutators']) if m else []
    chk("zeddo 17007 has Junkyard", "Junkyard" in have, True)
    lk = rb.call("jawa/world_links_get", {"range": "0-21871", "onlyLinked": True, "limit": 25000}).get("tiles", [])
    redges = set()
    for t in lk:
        for l in t.get('potentialRivers', []): redges.add(frozenset((t['tile'], l['neighbor'])))
    chk("river edges", len(redges), 326)
    print("REPLAY " + ("VERIFIED" if ok else "HAS FAILURES"), flush=True)
