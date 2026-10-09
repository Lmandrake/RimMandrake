import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
mid=S.biome_map(114504,"RM_SeabedFloor_TheChill",layer="RM_SeabedLayer",surface_biome="RM_TheChill",parent="RM_SeabedSite")
try:
    print("biome",S.call("jawa/map_info").get("mapBiome"))
    t=S.call("jawa/list_things",defName="RM_Tarnn",limit=50); print("tarnn on floor",t.get("countMatched"))
    with S.Scene("garden",20,20,10,10) as sc:
        sc.room()
        pid=sc.colonist(2,2)
        S.call("jawa/pawn_health",pawn=pid,action="add",hediff="Heatstroke",severity=0.0) if False else None
        def tarnnstate():
            r=S.call("jawa/list_things",defName="RM_Tarnn",limit=50,includePawns=True)
            return [ (x.get("id"),x.get("x"),x.get("z")) for x in r.get("things",[])][:6]
        S.call("jawa/spawn_pawn",kindDef="RM_Tarnn",x=70,z=70,faction="none",count=3)
        for tid in [x[0] for x in tarnnstate()]: S.call("jawa/comp_read",thing=tid,comp="CanBeDormant",members="Awake")
        print("tarnn",tarnnstate(), [S.call("jawa/comp_read",thing=x[0],comp="CanBeDormant",members="Awake").get("values") for x in tarnnstate()])
        for i in range(4):
            sc.heat(5,5,21)
            sc.pawn("RM_Fessu",4,3,faction="none")
            f=sc.find("RM_Fessu")
            r=sc.order(pid,"AttackMelee",a=f.get("id"),wait=300)
            S.run(400)
            hed=len(sc.hediffs(pid) or [])
            S.call('jawa/pawn_health',pawn=pid,action='heal') if False else None
            lt=S.call("jawa/list_things",defName="RM_Fessu",rect=sc.rect,includePawns=True).get("countMatched")
            print("kill",i,"t",S.ticks(),"fessu left",lt,"hediffs",hed, str(r)[:120])
            S.run(2200)
        print("tarnn after",[S.call("jawa/comp_read",thing=x[0],comp="CanBeDormant",members="Awake").get("values") for x in tarnnstate()]); print([ (h) for h in (json.dumps(S.call("jawa/pawn_get",pawn=tarnnstate()[0][0]))[:600],)])
finally:
    S.drop_map(mid,114504,back=0)
