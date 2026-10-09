import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
r=S.call("jawa/animal_stats", defs="RSW_Runyip", extraStats="ComfyTemperatureMax,ComfyTemperatureMin")
print(json.dumps(r,default=str)[:900])
r=S.call("jawa/get_defs", defs="ThingDef/RSW_Runyip", fields="race.herdAnimal"); print(json.dumps(r,default=str)[:500])
print(S.call("jawa/map_zones"))
