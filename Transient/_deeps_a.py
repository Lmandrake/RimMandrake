import sys, json; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge
b=RimBridge(token="4f3c0a7aa74e4446ac19465c14fd54a9",timeout=120); b.connect()
names=["BiomeDef:RUT_LanternDeeps","WeatherDef:RUT_DeepCalm","ThingDef:RUT_DeepNuitae","ThingDef:RUT_DeepArpeau","ThingDef:RUT_DeepGreyLady","ThingDef:RUT_DeepDulcisPlant","ThingDef:RUT_DeepRawDulcis","ThingDef:RUT_LanternstoneSmall","ThingDef:RUT_LanternstoneHuge","TerrainDef:RUT_Lanternstone","GenStepDef:RUT_LanternstoneFormations","MapGeneratorDef:RUT_LanternDeepGenerator","ThingDef:RUT_Nuitae"]
r=b.call("jawa/get_defs", {"defs":";".join(n.replace(":","/") for n in names),"fields":"defName;label;isCavern","deep":False})
print(json.dumps(r,indent=0)[:2500])
