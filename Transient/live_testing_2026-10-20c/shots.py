"""Screenshots: a fresh RUT_Umbra map (Camp parent, -60 C) and an RM_Ummisk at a painted lava pool on a fresh RM_TheForge
map. PNGs go to D:\\ClaudeWork\\screenshots\\2026-10-20. Maps are left loaded until the end, then dropped."""
import time, json
from bc import call, j, out
OUT = r"D:\ClaudeWork\screenshots\2026-10-20"
home = call("jawa/map_info"); home_id, htile = home.get("mapId"), int(home.get("tile"))
r = call("jawa/tile_settleable", tiles=",".join(str(htile + d) for d in range(40, 2400, 37)))
tiles = [int(x["tile"]) for x in r.get("tiles") or [] if x.get("settleable") or "not implemented" in str(x.get("reason"))]
res = {}


def make(tile, biome, temp):
    orig = (call("jawa/world_tile_get", tiles=str(tile)).get("tiles") or [{}])[0]
    call("jawa/world_tile_set", tiles=str(tile), biome=biome, temperature=temp); call("jawa/world_commit")
    g = call("jawa/world_tile_map_generate", tile=tile, suggestedMapParent="Camp", sizeX=120, sizeZ=120)
    call("jawa/set_current_map", mapId=g.get("mapId"))
    call("jawa/kill_hostiles")
    return g, orig


def shot(name, x, z, size=None):
    call("jawa/clear_ui")
    call("rimworld/jump_camera_to_cell", x=x, z=z)
    if size: call("rimworld/set_camera_zoom", rootSize=size)
    time.sleep(1.5)
    s = call("rimworld/take_screenshot", fileName=name, outputDirectory=OUT, suppressMessage=True)
    print(name, j({k: s.get(k) for k in ("success", "path", "filePath", "message")}, 300))
    return s

# Umbra
g, ou = make(tiles[0], "RUT_Umbra", -60.0)
info = call("jawa/map_info"); w = call("jawa/weather_get")
res["umbra"] = {"gen": j(g, 200), "info": j(info, 300), "weather": j(w, 800),
                "glow": j(call("jawa/glow_at", x=60, z=60), 300)}
print("umbra", res["umbra"]["info"]); print("weather", res["umbra"]["weather"][:500])
shot("umbra_mid_20c", 60, 60, 24); shot("umbra_close2_20c", 60, 60, 12)
umbra_idx = g.get("mapIndex")
# Forge + ummisk at lava
g2, of = make(tiles[1], "RM_TheForge", 30.0)
x0, z0 = 55, 55
call("jawa/destroy_batch", rects="%d,%d,24,20" % (x0 - 12, z0 - 7), categories="All")
call("jawa/set_terrain_batch", ops="Soil:%d,%d,24,20" % (x0 - 12, z0 - 7))
call("jawa/set_terrain_batch", ops="LavaDeep:%d,%d,6,6" % (x0, z0))
sp = call("jawa/spawn_pawn", kindDef="RM_Ummisk", x=x0 - 1, z=z0 + 2, faction="none", count=2)
print("spawn", j(sp, 300))
pass  # no ticks: a Camp map with no colonists is culled on tick (memory: generated map culled unless home)
res["forge"] = {"gen": j(g2, 200), "spawn": j(sp, 300)}
shot("ummisk_lava_wide_20c", x0 + 2, z0 + 3, 20); shot("ummisk_lava_close_20c", x0, z0 + 3, 9)
json.dump(res, open(out("shots.json"), "w"), indent=1)
# cleanup: back home, drop both maps, remove camps, restore tiles
call("jawa/set_current_map", mapId=home_id)
for gg, t, o in ((g, tiles[0], ou), (g2, tiles[1], of)):
    if gg.get("mapIndex") is not None:
        pass
for mid_g, t, o in ((g2, tiles[1], of), (g, tiles[0], ou)):
    print("drop", j(call("jawa/map_drop", mapIndex=mid_g.get("mapIndex"), notifyPlayer=False), 120))
    wo = call("jawa/world_objects_get", tiles=str(t)).get("objects") or []
    for o2 in wo:
        if o2.get("def") == "Camp": call("jawa/world_objects_remove", ids=str(o2.get("id")))
    call("jawa/world_tile_set", tiles=str(t), biome=o.get("biome"), temperature=o.get("temperature")); call("jawa/world_commit")
