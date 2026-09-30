"""SEA_DIVE_FLOOR_TERRAIN_1 live proof: generate each sea's DIVE floor the way the game does
and census its terrain + plants. Windows python.exe, repo root, on a throwaway debug map
(quicktest; this script re-biomes the current tile and leaves pocket maps behind):

    python.exe src/RimMandrake/bridgetools/prove_sea_dive_floor.py [TheScald GreySea TwilightSea TheChill]

The real route, not a shortcut: RM_SeaDiveHatch.GeneratePocketMapInt picks the generator from
the PARENT map's biome and runs PocketMapUtility.GeneratePocketMap; it fires when a pawn
completes the vanilla EnterPortal job (JobDriver_EnterPortal -> MapPortal.OnEntered ->
GetOtherMap -> GeneratePocketMap). Per sea:
  1. set the current map's world tile to the sea biome (Map.Biome reads TileInfo live),
  2. RM_DivingSettings.requireGravEngine=false for the run (no gravship on a quicktest),
  3. spawn a fresh RM_SeaDiveHatch beside a colonist (a hatch caches its pocket map, so one
     hatch per sea), order EnterPortal, tick until a new map appears,
  4. census every cell's terrain (jawa/get_terrain_batch, mapId) + every plant (list_things
     group=Plant on that map) and check the expected habitat terrains exist and carry plants.
Settings are restored at the end. Nothing here is a success claim until it prints PASS.
"""
import sys, json, time, collections
sys.path.insert(0, r"src\RimMandrake\Utils")
import rimbridge_client as rb

SEAS = {
    # biome: (expected band terrains, tag-gated plants that should appear on them)
    "TheScald":    ("RM_TheScald",    ["RM_SeaFloorGround", "RUT_ScaldMargin", "RUT_ScaldWaterOceanShallow"], ["RM_Crowncarpet"]),
    "GreySea":     ("RM_GreySea",     ["RM_SeaFloorGround"], []),
    "TwilightSea": ("RM_TwilightSea", ["RM_SeaFloorGround"], []),
    "TheChill":    ("RM_TheChill",    ["RM_ChillIceBedrock", "RM_SolidPropane", "RM_TheChillDeep"],
                    ["RM_Slackwax", "RM_Ghostpane", "RM_Keelgrass", "RM_Skyharp", "RM_Pitchpearl",
                     "RM_Eldspar", "RM_Tarspool", "RM_Stonewater", "RM_Fuselight", "RM_ChillStillbloom"]),
}
SETTINGS = "RimMandrake.DivingInteraction.RM_DivingSettings"

h, p, t = rb.resolve_endpoint(); S = rb.RimBridge(host=h, port=p, token=t, timeout=300.0); S.connect()
def call(n, **a):
    r = S.call(n, a) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r if isinstance(r, dict) else {"raw": r}

def xz(pos):
    # list_pawns/list_things report {x, z}; some tools report IntVec3.ToString() "(x, y, z)".
    if isinstance(pos, dict): return int(pos.get("x", 0)), int(pos.get("z", 0))
    q = [int(v) for v in str(pos).strip("() ").split(",")]
    return q[0], q[-1]

def loaded_maps():
    # set_current_map refuses an unknown id and lists every loaded map.
    r = call("jawa/set_current_map", mapId=-987654)
    return {m["mapId"]: m for m in (r.get("loadedMaps") or [])}

def terrain_census(map_id, sx, sz):
    c = collections.Counter(); read = 0
    for z0 in range(0, sz, 25):
        hh = min(25, sz - z0)
        r = call("jawa/get_terrain_batch", rects="0,%d,%d,%d" % (z0, sx, hh), mapId=map_id)
        read += r.get("cellsRead", 0) or 0
        for op in (r.get("ops") or "").split(";"):
            if ":" not in op: continue
            d, rect = op.rsplit(":", 1); q = rect.split(",")
            c[d] += int(q[2]) * int(q[3]) if len(q) == 4 else 1
    return c, read

home = call("jawa/map_info")
home_id, home_tile, home_biome = home.get("mapId") or home.get("uniqueID"), home.get("tile"), home.get("mapBiome")
print("home map", home_id, "tile", home_tile, "biome", home_biome)
old_req = call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="requireGravEngine").get("value")
old_bands = call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="seaFloorBandsEnabled").get("value")
print("settings before: requireGravEngine=%s seaFloorBandsEnabled=%s" % (old_req, old_bands))
if old_bands is None:
    sys.exit("FAIL: seaFloorBandsEnabled not readable - is the SEA_DIVE_FLOOR_TERRAIN_1 DLL deployed?")
call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="requireGravEngine", value="false")
call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="seaFloorBandsEnabled", value="true")

colonists = [p for p in ((lambda r: r.get("pawns") or r.get("results") or [])(call("jawa/list_pawns", faction="player"))) if not p.get("dead") and not p.get("downed")]
wanted = sys.argv[1:] or list(SEAS)
verdicts = {}
try:
    for i, sea in enumerate(wanted):
        biome, expect_terr, expect_plants = SEAS[sea]
        print("\n=== %s (%s)" % (sea, biome))
        if i >= len(colonists):
            verdicts[sea] = "UNMEASURED (no free colonist)"; continue
        call("jawa/set_current_map", mapId=home_id)
        call("jawa/world_tile_set", tiles=str(home_tile), biome=biome); call("jawa/world_commit")
        if call("jawa/map_info").get("mapBiome") != biome:
            verdicts[sea] = "UNMEASURED (parent map biome did not change)"; continue
        pawn = colonists[i]; px, pz = xz(pawn.get("position"))
        sp = call("jawa/spawn_batch", ops="RM_SeaDiveHatch:%d,%d" % (px + 2, pz))
        print("hatch spawn:", {k: sp.get(k) for k in ("success", "thingsPlaced", "failed")})
        hatches = [th for th in (call("jawa/list_things", defName="RM_SeaDiveHatch").get("things") or [])]
        hatch = min(hatches, key=lambda th: abs(xz(th.get("position"))[0] - px - 2) + abs(xz(th.get("position"))[1] - pz)) if hatches else None
        if not hatch:
            verdicts[sea] = "UNMEASURED (hatch did not spawn)"; continue
        before = loaded_maps()
        oj = call("jawa/ordered_job", pawnId=pawn.get("id"), jobDef="EnterPortal", targetAId=hatch.get("id"))
        print("EnterPortal:", {k: oj.get(k) for k in ("success", "accepted", "reason", "error")})
        new = {}
        for _ in range(20):
            call("rimworld/step_game_ticks", ticks=250, timeoutMs=120000)
            new = {k: v for k, v in loaded_maps().items() if k not in before}
            if new: break
        if not new:
            verdicts[sea] = "FAIL (no pocket map generated)"; continue
        mid, m = next(iter(new.items()))
        print("pocket map", mid, m)
        call("jawa/set_current_map", mapId=mid)
        mi = call("jawa/map_info"); sx, sz = mi.get("sizeX"), mi.get("sizeZ")
        terr, read = terrain_census(mid, sx, sz)
        plants = collections.Counter(th.get("def") for th in (call("jawa/list_things", group="Plant", limit=100000).get("things") or []))
        print("map biome", mi.get("mapBiome"), "size", sx, sz, "cellsRead", read)
        print("terrain:", json.dumps(dict(terr.most_common(20))))
        print("plants:", json.dumps(dict(plants.most_common(30))))
        missing_t = [x for x in expect_terr if terr.get(x, 0) == 0]
        missing_p = [x for x in expect_plants if plants.get(x, 0) == 0]
        # Sanity: the census must see the base floor, or it cannot see anything.
        if terr.get(expect_terr[0], 0) == 0:
            verdicts[sea] = "UNMEASURED (base floor %s not seen - census broken?)" % expect_terr[0]
        elif missing_t:
            verdicts[sea] = "FAIL (band terrains absent: %s)" % missing_t
        elif expect_plants and sum(plants.get(x, 0) for x in expect_plants) == 0:
            verdicts[sea] = "FAIL (habitat present, no tag-gated plant grew)"
        else:
            verdicts[sea] = "PASS" + (" (not seen this roll: %s)" % missing_p if missing_p else "")
finally:
    call("jawa/set_current_map", mapId=home_id)
    if home_biome: call("jawa/world_tile_set", tiles=str(home_tile), biome=home_biome); call("jawa/world_commit")
    if old_req is not None:
        call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="requireGravEngine", value=str(old_req).lower())
    call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="seaFloorBandsEnabled", value=str(old_bands).lower())

print("\nVERDICTS:")
for k, v in verdicts.items():
    print("  %-12s %s" % (k, v))
