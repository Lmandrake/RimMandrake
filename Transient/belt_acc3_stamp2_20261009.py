import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
sc=S.Scene("stamp",30,30,7,7)
hot=S.Scene("hot",50,50,11,11); hot.__enter__(); hot.room(roof=True)
S.call("jawa/map_commit",full=True)
for p in S.call("jawa/list_pawns",rect="55,55,10,10",limit=30).get("pawns",[]):
    pass
r=S.call("jawa/spawn_pawn",kindDef="RM_Chorn",x=55,z=55,faction="none",count=8); print("spawn",r.get("spawnedCount"))
print(json.dumps(hot.heat(5,5,70))[:200])
def dry(tag):
    r=S.call("jawa/fire_incident",incidentDef="RM_ShadeStampede",dryRun=True); print(tag,json.dumps({k:r.get(k) for k in ("canFireNow","message")})[:200])
dry("hot herd+home roof")
with S.setting("RimMandrake.LongShade.RM_LongShadeSettings",stampedeEnabled=False):
    dry("setting off")
dry("on again")
