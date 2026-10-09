import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
print(json.dumps(S.call("jawa/static_call",type="RimMandrake.FloodedCanyon.RM_PeakstormDustProof",method="ProofState",args=""),default=str)[:600])
print(json.dumps(S.call("jawa/get_defs",defs="WeatherDef/RM_PeakstormLight;ThingDef/RUT_DyingCreep",fields="defName"),default=str)[:500])
r=S.call("jawa/spawn_batch",ops="RUT_DyingCreep:40,300"); print(json.dumps(r,default=str)[:900])
print(json.dumps(S.call("jawa/weather_get") if False else S.call("jawa/map_info"),default=str)[400:900])
