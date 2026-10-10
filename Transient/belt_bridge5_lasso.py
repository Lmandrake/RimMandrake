import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
L=["AM_LassoCloth","AM_LassoHyperweave","AM_LassoDevilstrand","AM_Lasso"]
r=S.call("jawa/get_defs", defs=";".join("ThingDef/"+x for x in L)+";"+";".join("RecipeDef/Make_"+x for x in L), fields="recipeMaker,products,recipeUsers,researchPrerequisite", deep="true")
for d in r["defs"]: print("DEF", d.get("requested"), d.get("found"), json.dumps(d.get("fields"),default=str)[:400])
print("notFound", r.get("notFound"))
# pawns carrying a lasso, on every loaded map
for mid in (0,1,2,3,4,5):
    p=S.call("jawa/list_things", defName="AM_LassoCloth", limit=50, includePawns=True)
    break
tot=0
for mapId in range(0,8):
    if not S.call("jawa/set_current_map", mapId=mapId).get("success"): continue
    ps=S.call("jawa/list_pawns", limit=600).get("pawns") or []
    hits=[]
    for p in ps:
        if p.get("intelligence")!="Humanlike": continue
        g=S.call("jawa/pawn_gear", pawn=p["id"], action="list")
        s=json.dumps(g)
        if "Lasso" in s: hits.append(p["id"])
    tot+=len(ps); print("MAP", mapId, "pawns", len(ps), "lassoCarriers", hits)
S.call("jawa/set_current_map", mapId=4)
