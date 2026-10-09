import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
for t,f in (("RimMandrake.Stillsand.RM_SandSwimRemainderStartup","songPatched"),("RimMandrake.Stillsand.RM_SandSwimRemainderStartup","driftPatched")):
    r=S.call("jawa/mod_settings_field",typeName=t,action="get",field=f); print(t,r.get("success"),r.get("value"),str(r.get("message"))[:150])
