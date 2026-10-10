import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
def j(x, n=300): return json.dumps(x, default=str)[:n]
# ZERSIUM_FORGE_BIOME_1 L5 as a PLAYER HOME map (the GenStep is on Base_Player; scenelib.biome_map's faction-less
# settlement generates with Base_Faction, so it can never carry zersium - bridge7 first pass read 0 for that reason).
def probe(tag):
    r = S.call("jawa/static_call", type="RimMandrake.Utinni.UtinniPatches.RUT_ZersiumForgeProof", method="Probe", args="x")
    print("PROBE", tag, r.get("result") if r.get("success") else j(r))
def home(tile, biome):
    print("set", j(S.call("jawa/world_tile_set", tiles=str(tile), biome=biome, hilliness="LargeHills"), 150)); S.call("jawa/world_commit")
    print("found", j(S.call("jawa/colony_found", tile=tile, faction="Player"), 200))
    r = S.need(S.call("jawa/world_tile_map_generate", tile=tile, sizeX=250, sizeZ=250), "gen")
    mid = r["mapId"]; S.need(S.call("jawa/set_current_map", mapId=mid), "cur")
    S.call("jawa/spawn_pawn", kindDef="Colonist", x=75, z=140, faction="player", count=1)
    return mid
T = "RimMandrake.Utinni.UtinniPatches.UtinniPatchesSettings"
tiles = [int(t) for t in sys.argv[1].split(",")]
m = home(tiles[0], "RM_TheForge"); probe("forge_home mapId=%s" % m); S.drop_map(m, tiles[0], 0)
m = home(tiles[1], "AridShrubland"); probe("arid_home mapId=%s" % m); S.drop_map(m, tiles[1], 0)
with S.setting(T, zersiumForgeEnabled=False):
    m = home(tiles[2], "RM_TheForge"); probe("forge_home_toggle_off mapId=%s" % m); S.drop_map(m, tiles[2], 0)
print("GET after", S.call("jawa/mod_settings_field", typeName=T, action="get", field="zersiumForgeEnabled").get("value"))
