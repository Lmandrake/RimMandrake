import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
out={}
d=S.call("jawa/get_defs",defs="ThingDef/RUT_VaultFleshSeal",fields="passability,thingClass,comps")
out["seal"]=json.dumps(d,default=str)[:900]
d=S.call("jawa/get_defs",defs="StructureLayoutDef/RUT_Vault_V5",fields="defName")
out["v5"]=json.dumps(d,default=str)[:300]
d=S.call("jawa/get_defs",defs="ThingDef/AA_GreenGoo",fields="race")
out["gooRace"]=json.dumps(d,default=str)[:1500]
print(json.dumps(out,default=str))
