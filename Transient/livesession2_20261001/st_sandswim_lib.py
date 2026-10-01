from bx import call

def hediffs(pid):
    ps = call("jawa/pawn_get", {"pawn": pid}).get("pawns") or []
    if not ps:
        return None
    p = ps[0]
    return {"hediffs": [h.get("def") for h in (p.get("hediffs") or [])], "pos": p.get("position")}

def pawns():
    return call("jawa/list_pawns", {"limit": 400, "includeHealth": True, "includeCorpses": True}).get("pawns") or []

def step(n):
    return call("rimworld/step_game_ticks", {"ticks": n}, 300).get("ticksGame")

def spawn(kind, x, z, faction, count=1):
    r = call("jawa/spawn_pawn", {"kindDef": kind, "x": x, "z": z, "faction": faction, "count": count})
    return [p.get("id") for p in (r.get("pawns") or []) if p.get("ok")], r.get("message")

def paint(x, z, w, h, t):
    call("jawa/destroy_batch", {"rects": f"{x},{z},{w},{h}", "categories": "Plant,Item,Building,Filth"})
    return call("jawa/set_terrain", {"x": x, "z": z, "terrainDef": t, "width": w, "height": h}).get("success")
