import json
from bx import call
from st_sandswim_lib import step, paint
print(paint(200, 150, 6, 6, "Sand"))
r = call("rimworld/spawn_thing", {"defName": "SolarGenerator", "x": 202, "z": 152}, 60); tid = r.get("thingId", "").replace("Thing_", ""); print(r.get("success"), tid)
rows = []
for i in range(9):
    p = call("jawa/power_net", {"thing": tid}, 60); g = call("rimworld/get_game_info", {}, 30).get("ticksGame")
    rows.append((g, json.dumps(p, default=str)[:300])); print(rows[-1], flush=True)
    step(7500)
json.dump(rows, open("sol.json", "w"), indent=1)
