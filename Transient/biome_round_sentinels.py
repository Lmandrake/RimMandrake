import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

SENTINELS = (
    "BiomeDef/RM_TheRot;BiomeDef/RM_FeverWood;BiomeDef/RM_Greentide;"
    "BiomeDef/RM_NightsideIce;BiomeDef/RM_Stillsand;BiomeDef/RM_LongShade;"
    "BiomeDef/RM_Wasteland;BiomeDef/RM_TheScald;BiomeDef/RM_GreySea;"
    "BiomeDef/RM_TwilightSea;BiomeDef/RM_PropaneLake;"
    "ThingDef/RM_Vaunoom;ThingDef/RM_Fessk;ThingDef/RM_Eesh;"
    "ThingDef/RM_Vorrel;ThingDef/RM_GiantLeaf;"
    "TerrainDef/RM_TheRotGrass;TerrainDef/RM_SolidPropane"
)

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    resp = rb.call("jawa/get_defs", {"defs": SENTINELS, "fields": "label"})
    results = resp.get("results") or resp.get("defs") or resp
    print(type(results))
    if isinstance(results, list):
        for r in results:
            print(r)
    else:
        print(results)
