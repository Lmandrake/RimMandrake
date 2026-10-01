"""Dune gale + dust devil."""
import json
from bx import call
OUT = {}
def log(k, v):
    OUT[k] = v; print(k, json.dumps(v, default=str)[:700], flush=True)
    json.dump(OUT, open("t4.json", "w"), indent=1, default=str)
def letters():
    return [(l.get("label") if not isinstance(l.get("label"), dict) else l["label"].get("RawText"), l.get("arrivalTick")) for l in call("jawa/letter_list", {}).get("letters", [])]
def tick(): return call("rimworld/get_game_info", {}, 30).get("ticksGame")
log("dry", call("jawa/fire_incident", {"incidentDef": "RM_DuneGale", "dryRun": True}, 60))
log("fire", call("jawa/fire_incident", {"incidentDef": "RM_DuneGale"}, 120))
log("weather", call("jawa/weather_get", {}, 30))
log("end_incident_gale", call("jawa/game_condition", {"action": "end", "condition": "RM_DuneGale"}, 60))
log("start_short", call("jawa/game_condition", {"action": "start", "condition": "RM_DuneGale", "durationTicks": 6000}, 60))
t0 = tick(); log("t0", t0)
for i in range(7):
    call("rimworld/step_game_ticks", {"ticks": 1000}, 300)
    w = call("jawa/weather_get", {}, 30)
    log(f"g{i}", {"tick": tick(), "weather": w.get("current") or w.get("weather") or str(w)[:200]})
log("letters", letters()[-12:])
th = call("jawa/list_things", {"group": "Filth", "limit": 5000})
cnt = {}
for t in th.get("things") or []:
    d = t.get("def"); 
    if str(d).startswith("RM_Filth"): cnt[d] = cnt.get(d, 0) + 1
log("rm_filth", cnt)
# dust devil
r = call("rimworld/spawn_thing", {"defName": "RM_DustDevil", "x": 100, "z": 100}, 60)
log("devil_spawn", r)
pos = []
for i in range(12):
    call("rimworld/step_game_ticks", {"ticks": 250}, 120)
    th = call("jawa/list_things", {"defName": "RM_DustDevil", "limit": 20})
    pos.append([(t.get("id"), t.get("x"), t.get("z")) for t in (th.get("things") or [])])
log("devil_track", pos)
