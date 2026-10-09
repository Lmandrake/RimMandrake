import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
SET = "RimMandrake.LongShade.RM_LongShadeSettings"
for f in ("modEnabled", "cleanPatchTellEnabled", "crawlerRoadEnabled", "tollokTicksEnabled", "jawaReturnEnabled", "stampedeEnabled"):
    print(f, S.call("jawa/mod_settings_field", typeName=SET, action="get", field=f).get("value"))
r = S.call("jawa/mod_settings_field", typeName=SET, action="list")
print([ (x["name"], x["value"]) for x in r.get("fields", [])][:40])
