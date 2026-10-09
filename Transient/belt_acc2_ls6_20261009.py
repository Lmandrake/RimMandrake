import sys, json, collections, time
sys.path.insert(0, "src/RimMandrake/Utils")
from scenes import scenelib as S
SET = "RimMandrake.LongShade.RM_LongShadeSettings"
out = {}
mid = int(open("Transient/belt_acc2_ls_map_id.txt").read())
S.call("jawa/set_current_map", mapId=mid)
S.quiet()

def shade_at(x, z):
    c = (S.call("jawa/shadegrid_read", cells="%d,%d" % (x, z)).get("cells") or [{}])[0]
    return c.get("shade")

def roofed(x, z):
    r = S.call("jawa/get_roof_batch", rects="%d,%d,1,1" % (x, z))
    return r

def pg(pid):
    return (S.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0]

def hed(pid):
    return [(h.get("def"), h.get("severity")) for h in pg(pid).get("hediffs", [])]

def feed(ids):
    for pid in ids:
        for n in ("Food", "Rest"):
            S.call("jawa/pawn_need", pawn=pid, action="need", need=n, level=1.0)

def place_colonist(x, z):
    r = S.call("jawa/spawn_pawn", kindDef="Colonist", x=x, z=z, faction="player", count=1)
    ps = r.get("pawns") or []
    return ps[0]["id"] if ps else None

try:
    # candidate deep-shade cells: shade 1.0 near x 67..79 z 25..43
    cands = [(67, 31), (67, 34), (70, 37), (70, 40), (73, 40), (73, 43), (76, 43), (79, 31), (67, 25)]
    good = []
    for (x, z) in cands:
        s = shade_at(x, z)
        if s is not None and s >= 0.7:
            good.append((x, z, s))
    out["shade_cands"] = good
    r0 = roofed(good[0][0], good[0][1]) if good else None
    out["roof_probe_keys"] = list(r0.keys()) if isinstance(r0, dict) else str(r0)[:100]
    out["roof_probe"] = json.dumps(r0, default=str)[:400]
    bx, bz, _ = good[0]; cx, cz, _ = good[2]
    # ---- Tollok on
    A = place_colonist(bx, bz); S.call("jawa/set_draft", pawnId=A, drafted=True)
    # awning control
    aw = S.call("jawa/spawn_batch", ops="RM_LureAwning:%d,%d" % (cx, cz))
    out["awning_spawn"] = json.dumps(aw, default=str)[:200]
    B = place_colonist(cx, cz); S.call("jawa/set_draft", pawnId=B, drafted=True)
    out["pos"] = {"A": (pg(A).get("x"), pg(A).get("z")), "B": (pg(B).get("x"), pg(B).get("z"))}
    out["shade_at_A"] = shade_at(*S.call("jawa/pawn_get", pawn=A)["pawns"][0].get("position", {"x": bx, "z": bz}).values()) if False else shade_at(bx, bz)
    with S.setting(SET, tollokTicksEnabled=True, lureAwningEnabled=True):
        for k in range(7):
            feed([A, B]); S.run(500)
        out["tollok_on"] = {"A_shade_unroofed": hed(A), "B_under_awning": hed(B)}
    print(json.dumps(out, default=str), flush=True)
    # awning inspect
    aid = (S.call("jawa/list_things", defName="RM_LureAwning", rect="%d,%d,3,3" % (cx - 1, cz - 1)).get("things") or [{}])[0].get("id")
    out["awning_inspect_on"] = S.call("jawa/inspect_string", thingIds=aid) if aid else None
    with S.setting(SET, lureAwningEnabled=False):
        out["awning_inspect_off"] = S.call("jawa/inspect_string", thingIds=aid) if aid else None
    for k in ("awning_inspect_on", "awning_inspect_off"):
        out[k] = json.dumps(out[k], default=str)[:400]
    print(json.dumps({k: out[k] for k in ("awning_inspect_on", "awning_inspect_off")}), flush=True)
    # ---- toggle off arm: fresh colonist standing still in shade with tollokTicksEnabled=false
    S.call("jawa/damage", damageDef="Bomb", amount=1, thingId=A, allowColonists=True) if False else None
    C = place_colonist(good[3][0], good[3][1]); S.call("jawa/set_draft", pawnId=C, drafted=True)
    with S.setting(SET, tollokTicksEnabled=False):
        for k in range(7):
            feed([C]); S.run(500)
        out["tollok_off_C"] = hed(C)
    print(json.dumps({"tollok_off_C": out["tollok_off_C"]}), flush=True)
    # ---- Harrok: wild harrok in open at (30,60); downed colonists 2..4 cells around in 8 directions
    hk = S.call("jawa/spawn_pawn", kindDef="RM_Harrok", x=30, z=60, faction="none", count=1)
    hid = (hk.get("pawns") or [{}])[0].get("id")
    out["harrok_spawn"] = (hk.get("success"), hid, str(hk.get("message"))[:100], shade_at(30, 60))
    prey = []
    for dx, dz in [(3,0),(-3,0),(0,3),(0,-3),(2,2),(-2,2),(2,-2),(-2,-2)]:
        pid = place_colonist(30 + dx, 60 + dz)
        if pid:
            S.call("jawa/pawn_force_incapacitate", pawn=pid); prey.append((pid, dx, dz))
    out["prey_n"] = len(prey)
    with S.setting(SET, harrokEnabled=True):
        for k in range(2):
            feed([p[0] for p in prey]); S.run(450)
        hits = [(dx, dz, [h for h in hed(pid) if h[0] in ("Stab",)]) for pid, dx, dz in prey]
        out["harrok_on_hits"] = [h for h in hits if h[2]]
    print(json.dumps({"harrok_on_hits": out["harrok_on_hits"], "harrok_spawn": out["harrok_spawn"]}, default=str), flush=True)
    msgs = S.call("jawa/drain_log", limit=100, contains="harrok")
    out["harrok_msgs"] = json.dumps(msgs, default=str)[:400]
    print(out["harrok_msgs"], flush=True)
finally:
    pass
