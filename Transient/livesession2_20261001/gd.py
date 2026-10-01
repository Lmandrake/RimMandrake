import json,sys
from bx import call
defs = ";".join([
 "ThingDef/RM_KneelOllim","ThingDef/RM_Oorrik","PawnKindDef/RM_Oorrik","ThingDef/RM_Soorrak",
 "ThingDef/RM_ChillCryoponicsVat","ThingDef/RM_ChillFloorBed",
 "HediffDef/RM_PillarArm","HediffDef/RM_Lash","HediffDef/RM_Eyeburst","HediffDef/RM_CaudalSpring","HediffDef/RM_Bellows",
 "ThingDef/RM_PillarArmItem","ThingDef/RM_LashItem","RecipeDef/RM_InstallGrownArm","RecipeDef/RM_InstallGrownLeg",
 "HediffDef/RM_IrqitFloodBorn","ThingDef/RM_IrqitTarruq","ThingDef/RM_RavenNettle",
 "BiomeDef/RM_Stillsand","IncidentDef/RM_DuneGale","GameConditionDef/RM_DuneGale","ThingDef/RM_DustDevil",
 "IncidentDef/RUT_KraytAttack","IncidentDef/RM_MuurrokEmergence","ThingDef/RM_Muurrok","PawnKindDef/RM_Muurrok",
 "ThingDef/RM_Filth_DisturbedSand","ThingDef/RM_Filth_DragMark","PawnKindDef/RM_Vekka",
 "ThingDef/RM_DuneCrawler","ThingDef/RM_RustPuff","ThingDef/RM_Qorrax","ThingDef/RM_Nogtyl","WeatherDef/RM_SheenStorm","WeatherDef/RM_SheenMist","WeatherDef/RM_SheenFall",
 "ThingDef/RM_Dewshrooms","ThingDef/RM_Wrinklecap","ThingDef/RM_Arpeau","TerrainDef/RM_MycelialSoil","TerrainDef/RM_MycelialMatting","GameConditionDef/RM_SheenExposureLock",
])
r = call("jawa/get_defs", {"defs": defs}, 60)
json.dump(r, open("getdefs_smoke.json","w"), indent=1, default=str)
print({k: r.get(k) for k in ("success","foundCount","requestedCount","notFound","message")})
