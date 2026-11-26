"""Owed RIMMANDRAKE_PROVE_ANCHORLESS_HERD_AVOIDS_FRESH_ASH_SECOND_DOOR + RIMMANDRAKE_FIX_HERD_ANCHOR_FALLS_BACK_TO_FRESH_ASH,
on a freshly reloaded site (no lag-old burn): anchor must read invalid; off-ash ullai beside the opening front go to ash; where?"""
import sys, json, math
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h,p,tk = resolve_endpoint()
FB="RimMandrake.Pyrelands.RM_JobGiver_FollowBurn"; BL="RimMandrake.Pyrelands.MapComponent_BurnLine"
out={}
with RimBridge(h,p,tk) as rb:
    sc=lambda t,m,a=None: rb.call("jawa/static_call", dict({"type":t,"method":m}, **({"args":a} if a is not None else {}))).get("result")
    out["front"]=sc(BL,"ProbeOpeningFront"); print("front", out["front"])
    out["hist"]=sc(BL,"ProbeBurnHistory","120000"); print("hist", out["hist"])
    fr=rb.call("jawa/list_things",{"defName":"Fire","limit":2000}).get("things") or []
    fires=[(f["x"],f["z"]) for f in fr if not f.get("parent")]
    print("fires", len(fires), fires[:5])
    if not fires: print("NO FIRE: cannot place beside the front"); 
    cx=sum(x for x,z in fires)/max(1,len(fires)); cz=sum(z for x,z in fires)/max(1,len(fires))
    # a soil pocket 12 cells east of the burning front's centroid: off-ash ullai whose nearest ash (25 cells) includes the front's
    sx,sz=int(cx)+12,int(cz)-3
    rb.call("jawa/set_terrain",{"x":sx,"z":sz,"terrainDef":"RM_FE_Ground_Soil","width":6,"height":6,"layer":"top"})
    ids=[]
    for i in range(8):
        r=rb.call("jawa/spawn_pawn",{"kindDef":"RM_Ullai","x":sx+1+(i%4),"z":sz+1+(i//4)*2,"faction":"none","count":1})
        ids.append(((r.get("pawns") or [{}])[0]).get("id"))
    out["pocket"]=[sx,sz]; out["frontCentroid"]=[round(cx,1),round(cz,1)]
    out["issue"]=sc(FB,"ProbeHerd","RM_Ullai|true"); print("issue", out["issue"])
    def where():
        r=rb.call("jawa/site_state",{}); return [(q["x"],q["z"],q.get("job")) for q in r.get("pawns") or [] if q["id"] in ids]
    trace=[]
    for i in range(4):
        rb.call("jawa/safe_advance",{"ticks":250,"timeException":False})
        fr=rb.call("jawa/list_things",{"defName":"Fire","limit":3000}).get("things") or []
        fset={(f["x"],f["z"]) for f in fr if not f.get("parent")}
        w=where(); near=[(x,z) for x,z,_ in w if any(abs(x-a)<=1 and abs(z-b)<=1 for a,b in fset)]
        trace.append({"tick":(i+1)*250,"pos":w,"onOrBesideFire":len(near),"fires":len(fset)}); print(trace[-1])
    hs=[]
    for pid in ids:
        g=rb.call("jawa/pawn_get",{"pawn":pid}); q=(g.get("pawns") or [{}])[0]
        hs.append([hh.get("def") or hh.get("defName") for hh in q.get("hediffs") or []])
    out["trace"]=trace; out["hediffs"]=hs; print("hediffs", hs)
json.dump(out, open(r"Transient\pv1\anchorless.json","w"), indent=1)
