import sys, time, json
sys.path.insert(0, "src/RimMandrake/Utils")
from rimbridge_client import RimBridge, resolve_endpoint
ep = resolve_endpoint()
rb = RimBridge(host=ep[0], port=ep[1], token=ep[2], timeout=90)
rb.connect()

out = {}

# 1. Scorch-fruit yield item: live def — does it carry CompRottable and what lifespan?
d = rb.call("jawa/get_def", {"defType": "ThingDef", "defName": "RM_FE_ScorchFruitYield"})
txt = json.dumps(d)
out["scorchfruit_def_has_rottable"] = "Rottable" in txt
out["scorchfruit_rot_days"] = [s for s in txt.replace('"',' ').split() if "daysToRot" in s][:1] or "see_raw"
for k in ("comps","statBases"):
    if isinstance(d.get("def"),dict) and k in d["def"]: out[f"def_{k}"] = d["def"][k]

# 2. EmberGrass regrowth: sample growth of up to 30 plants now
def grass_sample():
    r = rb.call("jawa/list_things", {"defName": "RM_FE_Plant_EmberGrass"})
    return r.get("countMatched")
def quick_sample():
    r = rb.call("jawa/list_things", {"defName": "RM_FE_Plant_Quickgrass"})
    return r.get("countMatched")
out["embergrass_count_t0"] = grass_sample()
out["quickgrass_count_t0"] = quick_sample()
t0 = rb.call("jawa/time_clock", {})["ticksGame"]

# 3. run real time at speed 3 for 45s wall
rb.call("rimworld/set_time_speed", {"speed": 3})
time.sleep(45)
rb.call("rimworld/set_time_speed", {"speed": 0})
t1 = rb.call("jawa/time_clock", {})["ticksGame"]
out["ticks_advanced"] = t1 - t0

out["embergrass_count_t1"] = grass_sample()
out["quickgrass_count_t1"] = quick_sample()
r = rb.call("jawa/list_things", {"defName": "RM_FE_Filth_LooseAsh"})
out["looseash_now"] = r.get("countMatched")

print(json.dumps(out, indent=1, default=str)[:2200])
