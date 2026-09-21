import sys, json, os
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()

PAIRS = [
 "GameConditionDef/RUT_SheenExposureLock",
 "GameConditionDef/RUT_SporeCloud",
 "ThingDef/RUT_PaleTree",
 "ThingDef/RUT_PaleMoss",
 "ThingDef/RUT_AgelessCap",
 "ThingDef/RUT_RegenerantVeil",
 "ThingDef/RUT_EuphoricCrown",
 "ThingDef/RUT_FalseFruit",
 "ThingDef/RUT_BrewingVessel",
 "ThingDef/RUT_GrownFurnace",
 "ThingDef/RUT_Tea_AgeReversal",
 "ThingDef/RUT_Tea_Bioregeneration",
 "ThingDef/RUT_Tea_Pleasure",
 "ThingDef/RUT_Symbiont_Quickflesh",
 "ThingDef/RUT_Symbiont_Nightwake",
 "ThingDef/RUT_Symbiont_Sheenblood",
 "ThingDef/RUT_Symbiont_Mycoid",
 "ThingDef/RUT_Apparel_ChitinSpiderHelmet",
 "ThingDef/RUT_Glimmerslime",
 "ThingDef/RUT_RawDulcis",
 "HediffDef/RUT_SheenCoating",
 "HediffDef/RUT_SheenSymbiosis",
 "HediffDef/RUT_SporesBuildup",
 "HediffDef/RUT_SporeFlesh",
 "HediffDef/RUT_MatGrip",
 "TerrainDef/RUT_MycelialMatting",
 "TerrainDef/RUT_MushroomFloor",
 "WeatherDef/RUT_SheenFall",
 "WeatherDef/RUT_SheenMist",
 "WeatherDef/RUT_SheenStorm",
 "BiomeDef/RUT_TheRot",
 "ThoughtDef/RUT_SoldRotTreasureMemory",
 "HediffDef/RUT_AgeReversalSated",
 "HediffDef/RUT_Bioregenerating",
]
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/get_defs", {"defs": ";".join(PAIRS), "fields": "defName,label,conditionClass,modName"})
    rows = r.get("defs") or r.get("rows") or []
    print("foundCount", r.get("foundCount"), "notFound", r.get("notFound"))
    for row in rows:
        print(row.get("found"), row.get("defType"), row.get("defName"), "|", row.get("modName"), "|", (row.get("fields") or {}).get("conditionClass"))
