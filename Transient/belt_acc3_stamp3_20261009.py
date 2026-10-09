import sys,json
sys.path.insert(0,"src/RimMandrake/Utils")
from scenes import scenelib as S
hot=S.Scene("hot",50,50,11,11)
S.call("jawa/room_heat",mode="set",value=70,x=55,z=55)
def dry(tag):
    S.run(5)
    r=S.call("jawa/fire_incident",incidentDef="RM_ShadeStampede",dryRun=True); print(tag,json.dumps({k:r.get(k) for k in ("canFireNow","message")})[:160],flush=True)
dry("hot herd+roof")
with S.setting("RimMandrake.LongShade.RM_LongShadeSettings",stampedeEnabled=False):
    dry("setting off")
dry("on again")
r=S.call("jawa/fire_incident",incidentDef="RM_ShadeStampede",forced=True); print("fire",json.dumps(r)[:300])
S.run(130)
print(json.dumps(S.call("jawa/letter_list"))[:500])
for p in S.call("jawa/list_pawns",rect=hot.rect,limit=10).get("pawns",[])[:3]:
    print(p.get("id"),p.get("curJob") or p.get("job"))
