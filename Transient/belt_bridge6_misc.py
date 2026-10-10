import sys, json
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
S.quiet()
def j(x,n=500): return json.dumps(x,default=str)[:n]
def sc(t,m,a):
    r=S.call("jawa/static_call", type=t, method=m, args=a)
    return r.get("result") if r.get("success") else "CALLFAIL "+j(r,300)
what=sys.argv[1]
if what=="shokk":
    for i in range(2): print("SHOKK A1", sc("RimMandrake.Webwork.RM_WebworkProof","ProofHarvest","true;RM_Webwork_Anchor;34"))
if what=="lasso":
    L=["AM_LassoCloth","AM_LassoHyperweave","AM_LassoDevilstrand"]
    r=S.call("jawa/get_defs", defs=";".join("RecipeDef/Make_"+x for x in L)+";ThingDef/AM_LassoCloth;RecipeDef/Make_Apparel_Duster", fields="recipeUsers,recipeMaker", deep="true")
    print("success", r.get("success"), "found", r.get("foundCount"), "notFound", r.get("notFound"))
    for d in r.get("defs") or []: print("DEF", d.get("requested"), d.get("found"), j(d.get("fields"),300))
if what=="droid":
    X,Z=int(sys.argv[2]),int(sys.argv[3])
    r=S.call("jawa/spawn_pawn", kindDef="RSW_DW_OuterRim_GNKDroid", x=X, z=Z, faction="player", count=3)
    ids=[p["id"] for p in r.get("pawns") or []]; print("spawn", ids)
    def info(pid):
        p=(S.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]
        return {"needs":[n.get("need") for n in p.get("needs") or []], "pos":p.get("position"), "job":p.get("job") or p.get("curJob")}
    for pid,t in zip(ids,["mindless","blank","sapient"]):
        print("SET", t, j(S.call("jawa/droid_format_tier", pawn=pid, action="set", tier=t),200))
    S.run(60)
    pos0={pid:info(pid)["pos"] for pid in ids}
    S.run(600)
    for pid,t in zip(ids,["mindless","blank","sapient"]):
        q=S.call("jawa/inspect_string", thingIds=pid); ins=((q.get("things") or [{}])[0].get("inspect") or [])[:3]
        job=sc("RimMandrake.CreatureBehaviors.RM_PawnJobProof","ProofJob",pid)
        print("AFTER", t, pid, info(pid), "pos0", pos0[pid], job, "insp", ins)
