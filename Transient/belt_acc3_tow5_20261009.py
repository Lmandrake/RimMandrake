import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
SET = "RimMandrake.LongShade.RM_LongShadeSettings"
for f in ("modEnabled","jawaReturnEnabled"): print(f, S.call("jawa/mod_settings_field", typeName=SET, action="get", field=f).get("value"))
g = S.call("jawa/get_defs", defs="FactionDef/RUT_Jawa_HuttCartel", fields="pawnGroupMakers,hidden,humanlikeFaction"); print(json.dumps(g, default=str)[:1500])
