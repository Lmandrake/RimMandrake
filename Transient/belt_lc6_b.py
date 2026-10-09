import sys; sys.path.insert(0,"Transient")
from belt_lc6_lib import *
b="RM_RustCathedral RM_TheForge RM_Webwork RM_FloodedCanyon RM_TheSump RM_LongShade RM_WeepingStones RM_Pyrelands RM_FeverWood RM_Stillsand RM_Greentide".split()
r=call("jawa/get_defs", defs=";".join("BiomeDef/"+x for x in b), fields="modExtensions", deep=True)
print("biomes found", r["foundCount"], "notFound", r["notFound"])
for d in r["defs"]:
    if "fields" in d: print(" ", d["defName"], len(d["fields"].get("modExtensions",[])))
t="RUT_ScaldWaterDeep RUT_ScaldWaterOceanDeep RUT_ScaldWaterMovingChestDeep RUT_ScaldWaterShallow RUT_ScaldWaterOceanShallow RUT_ScaldWaterMovingShallow".split()
r=call("jawa/get_defs", defs=";".join("TerrainDef/"+x for x in t), fields="modExtensions", deep=True)
print("terrain found", r["foundCount"], r["notFound"], [ (d["defName"], json.dumps(d["fields"])[:120]) for d in r["defs"] if "fields" in d])
