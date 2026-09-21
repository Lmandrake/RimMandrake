import sys, json; sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge
b=RimBridge(token="0370ddcc7f524e24a54e6cff36301136",timeout=120); b.connect()
new=["BiomeDef/RUT_LanternDeeps","WeatherDef/RUT_DeepCalm","SoundDef/RUT_DeepHum","SoundDef/RUT_DeepChorus","ThingDef/RUT_DeepMycelium","ThingDef/RUT_ZivvitTaper","ThingDef/RUT_QuorrFern","ThingDef/RUT_OsskBramble","ThingDef/RUT_BrellikBulb","ThingDef/RUT_TwitchingPuffer","ThingDef/RUT_ThrakkCap","ThingDef/RUT_PrennaLace","ThingDef/RUT_VellokReed","ThingDef/RUT_KuvraSpout","ThingDef/RUT_NurrikGill","ThingDef/RUT_PufferTendrils","ThingDef/RUT_Lanternstone_Huge","BiomeDef/BMT_CrystalCaverns"]
old=["ThingDef/RUT_Gleamtip","ThingDef/RUT_Fungusfern","ThingDef/RUT_CrystaltipBrambles","ThingDef/RUT_YumBulbs","ThingDef/RUT_DeepDulcisPlant","ThingDef/RUT_Crystalcap","ThingDef/RUT_DeepGreyLady","ThingDef/RUT_DeepArpeau","ThingDef/RUT_LuminousSpout","ThingDef/RUT_DeepNuitae","ThingDef/RUT_DeepRawDulcis"]
for label,names in (("NEW (expect present)",new),("OLD (expect absent)",old)):
    r=b.call("jawa/get_defs", {"defs":";".join(names),"fields":"defName;label","deep":False})
    print("==",label); print(json.dumps(r)[:1800])
