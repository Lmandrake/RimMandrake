from bx import call
print(call("jawa/world_tile_get", {"tiles": "56099"}, 30).get("tiles"))
r = call("jawa/world_tile_map_generate", {"tile": 56099}, 400); print({k: r.get(k) for k in ("success", "mapId")})
print(call("jawa/set_current_map", {"mapId": r.get("mapId")}, 60).get("success"))
print(call("jawa/map_info", {}, 30).get("mapBiome"))
for inc in ("RM_MuurrokEmergence", "RUT_KraytAttack"):
    f = call("jawa/fire_incident", {"incidentDef": inc}, 120)
    print(inc, f.get("fired"), f.get("message"))
print(call("jawa/set_current_map", {"mapId": 1}, 60).get("success"), call("jawa/map_info", {}, 30).get("mapBiome"))
print(call("jawa/settlement_remove", {"mode": "map", "tile": 56099}, 120).get("success"))
