import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
mid=S.biome_map(114503,"RM_SeabedFloor_TheScald",layer="RM_SeabedLayer",surface_biome="RM_TheScald",parent="RM_SeabedSite")
try:
    print("biome",S.call("jawa/map_info").get("mapBiome"), "outdoor", S.call("jawa/map_info").get("outdoorTempNow"))
    single=S.Scene("single",10,10,11,6); pair=S.Scene("pair",10,30,11,6)
    single.__enter__(); pair.__enter__()
    single.room(roof=True); pair.room(roof=True)
    for dz in range(1,5): pair.put("Wall",5,dz,stuff="BlocksGranite")
    S.call("jawa/map_commit",full=True)
    print("intensity",S.call("jawa/mod_settings_field",typeName="RimMandrake.DivingInteraction.RM_DivingSettings",action="get",field="scaldBerthIntensity"))
    def snap():
        return {"single":single.temp(5,3),"pairL":pair.temp(2,3),"pairR":pair.temp(8,3)}
    print("t0",snap())
    for i in range(4):
        S.run(1500); print("t",S.ticks(),snap())
finally:
    for s in (single,pair):
        s.teardown()
    S.drop_map(mid,114503,back=0)
