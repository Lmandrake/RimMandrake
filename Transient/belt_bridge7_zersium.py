import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
def j(x, n=400): return json.dumps(x, default=str)[:n]
# ZERSIUM_FORGE_BIOME_1 L4/L5: defs load; new Forge map carries zersium, a non-Forge map 0, toggle-off Forge map 0.
for d in ("ThingDef/RSW_Zersium", "ThingDef/RSW_MineableZersium", "GenStepDef/RUT_ZersiumForgeLumps"):
    r = S.call("jawa/get_defs", defs=d)
    print("DEF", d, r.get("success"), r.get("foundCount"), r.get("notFound"))
def probe(tag):
    r = S.call("jawa/static_call", type="RimMandrake.Utinni.UtinniPatches.RUT_ZersiumForgeProof", method="Probe", args="x")
    print("PROBE", tag, r.get("result") if r.get("success") else j(r))
tiles = [int(t) for t in sys.argv[1].split(",")]   # three free tiles
back = int(sys.argv[2]) if len(sys.argv) > 2 else 0
m = S.biome_map(tiles[0], "RM_TheForge", size=150, keeper=(75, 140)); probe("forge_new mapId=%s" % m); S.drop_map(m, tiles[0], back)
m = S.biome_map(tiles[1], "AridShrubland", size=150, keeper=(75, 140)); probe("arid_new mapId=%s" % m); S.drop_map(m, tiles[1], back)
T = "RimMandrake.Utinni.UtinniPatches.UtinniPatchesSettings"
print("GET", j(S.call("jawa/mod_settings_field", typeName=T, action="get", field="zersiumForgeEnabled")))
with S.setting(T, zersiumForgeEnabled=False):
    m = S.biome_map(tiles[2], "RM_TheForge", size=150, keeper=(75, 140)); probe("forge_toggle_off mapId=%s" % m); S.drop_map(m, tiles[2], back)
print("GET after", j(S.call("jawa/mod_settings_field", typeName=T, action="get", field="zersiumForgeEnabled")))
