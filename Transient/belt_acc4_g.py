import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
def raised():
    r=S.call("jawa/mod_settings_field",typeName="RimMandrake.MovingDunes.RM_DuneEvents",action="get",field="Raised"); return r.get("value"),r.get("success"),str(r.get("message"))[:100]
print("pre",raised(),flush=True)
mid=S.biome_map(114480,"RM_Stillsand",size=100,keeper=(50,50)); print("map",mid,flush=True)
try:
    print("t0",raised())
    for i in range(4):
        S.run(2500); print(S.ticks(),raised(),flush=True)
    print("announce",S.call("jawa/mod_settings_field",typeName="RimMandrake.MovingDunes.MovingDunesSettings",action="get",field="announceSandMoved").get("value"))
finally:
    S.drop_map(mid,114480,0)
