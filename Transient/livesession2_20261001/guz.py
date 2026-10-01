import json
from bx import call
r = call("jawa/world_tile_map_generate", {"tile": 56098}, 400); print({k: r.get(k) for k in ("success", "mapId", "mapIndex")})
print(call("jawa/set_current_map", {"mapId": r.get("mapId")}, 60).get("success"))
ps = call("jawa/list_pawns", {"limit": 800}).get("pawns") or []
print("guzzka", [(p["id"], p.get("x"), p.get("z"), p.get("factionName")) for p in ps if "uzzka" in str(p.get("kindDef"))])
th = call("jawa/list_things", {"limit": 5000, "defName": "RM_GuzzkaEggFertilized"}); print("clutch?", [(t.get("def"), t.get("x"), t.get("z")) for t in (th.get("things") or [])][:10], th.get("message"))
home = call("jawa/set_current_map", {"mapId": 0}, 60); print("home", home.get("success"))
print(call("jawa/settlement_remove", {"mode": "map", "tile": 56098}, 120).get("success"))
