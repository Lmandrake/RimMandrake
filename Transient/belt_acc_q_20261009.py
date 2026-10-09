import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
for t in ("AM.AMSettings.Settings","AM.Settings","AM.AMSettings.AMSettings"):
    r=S.call("jawa/mod_settings_field",typeName=t,action="list")
    print(t,json.dumps(r,default=str)[:1500])
