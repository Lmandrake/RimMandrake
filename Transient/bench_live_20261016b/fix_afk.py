import sys, json
sys.path.insert(0, "src/RimMandrake/Utils"); sys.path.insert(0, "src/RimMandrake/FlowWorks/northstar"); sys.path.insert(0,"src/RimMandrake/FlowWorks")
import proof_hose as PH
B = PH.PB()
def terr(x,z): return ((B.call("rimworld/get_cell_info",x=x,z=z).get("cell") or {}).get("terrainDefName","?"))
def wet(t): return any(k in t for k in ("Fill","Channel","Super","Deep","Water","Tar"))
cols = B.hp("colonists").get("pawns") or []
moved={}
for p in cols:
    pid=p["id"]; x,z=p["pos"]
    r=B.call("jawa/pawn_get",pawn="Human%d"%pid)
    hs=[h["def"] for h in (r.get("pawns") or [{}])[0].get("hediffs",[]) if h["def"] in ("RM_PitDrowning","RM_PitExposure")]
    for hd in hs:
        o=B.call("jawa/pawn_health",pawn="Human%d"%pid,action="remove",hediff=hd)
        if not o.get("success"): print("rm fail",pid,hd,o.get("message"))
    if "Superdeep" in terr(x,z):
        dest=None
        for dx,dz in ((0,-3),(0,3),(-3,0),(3,0),(0,-4),(0,4),(-4,0),(4,0),(0,-5)):
            if not wet(terr(x+dx,z+dz)): dest=(x+dx,z+dz);break
        print(pid,p["name"],(x,z),"->",dest)
        if dest:
            B.hp("pawn:%d=undraft"%pid) if False else None
            o=B.hp("pawn:%d=tp:%d,%d"%(pid,dest[0],dest[1])); print(o.get("success"))
            moved[pid]=[x,z]
json.dump(moved,open("Transient/bench_live_20261016b/moved_pawns_afk.json","w"))
for p in cols: B.hp("pawn:%d=draft"%p["id"])
r=B.hp("colonists")
print([ (p["name"],p["pos"],p["drafted"],p["downed"]) for p in r["pawns"] if p["id"] in (39867,39835)])
