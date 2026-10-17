import sys, json, time
sys.path.insert(0, "src/RimMandrake/Utils"); sys.path.insert(0, "src/RimMandrake/FlowWorks/northstar"); sys.path.insert(0,"src/RimMandrake/FlowWorks")
import proof_hose as PH
B = PH.PB()
BMC = "RimMandrake.FloodedCanyon.MapControls.RM_BiomeMapControls"
def tick():
    g = B.call("rimworld/get_game_info"); return g.get("ticksGame") or (g.get("state") or {}).get("tick")
def sc(typ, method, args=""):
    r = B.call("jawa/static_call", type=typ, method=method, args=args)
    return str(r.get("result") if r.get("result") is not None else (r.get("message") or r))
def rect(x, z, w, h, nz=True):
    ex = B.call("jawa/flowworks_excavation_rect", x=x, z=z, w=w, h=h, onlyNonZero=nz, includeTerrain=False)
    return ex.get("rows") or []
def wetn(rows): return sum(1 for r in rows if (r.get("f") or 0) > 0)
def vol(rows): return sum((r.get("f") or 0) for r in rows)
def pawns():
    return B.hp("colonists").get("pawns") or []
def safety():
    ps = pawns()
    bad = [(p["name"], p["pos"], p["drafted"], p["downed"]) for p in ps if p["downed"] or not p["drafted"]]
    return len(ps), bad
def draft_all():
    for p in pawns():
        B.hp("pawn:%d=draft" % p["id"])
def step(n):
    left = n
    while left > 0:
        k = min(500, left); B.ticks(k); left -= k
    return tick()
def feed():
    n=0
    for p in B.call("jawa/list_pawns").get("pawns") or []:
        if p.get("isPlayer"):
            for need in ("Food","Rest"):
                B.call("jawa/pawn_need", pawn=p["id"], action="need", need=need, level=1.0); 
            n+=1
    return n
