import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with open(r"D:\Luke\dev\Rimworld\Transient\droidworks_detonation_review\spawn_log.json") as f:
    grid = json.load(f)

with RimBridge(host, port, token) as rb:
    lp = rb.call("jawa/list_pawns", {})
    pawns = lp["pawns"]
    # match new droids by kindDef + position, closest to expected cell coords,
    # picking the ones not already accounted for (droids of same kind can repeat).
    used_ids = set()
    for cell in grid:
        candidates = [p for p in pawns if p.get("kindDef") == cell["kind"] and p["id"] not in used_ids]
        # pick nearest by position
        def dist(p):
            pos = p.get("position") or {}
            return abs(pos.get("x", 9999) - cell["x"]) + abs(pos.get("z", 9999) - cell["z"])
        candidates.sort(key=dist)
        if not candidates:
            print("NO CANDIDATE for", cell["cell"], cell["kind"])
            continue
        chosen = candidates[0]
        used_ids.add(chosen["id"])
        cell["pawnId"] = chosen["id"]
        cell["spawned_position"] = chosen.get("position")
        print(cell["cell"], "-> pawnId", chosen["id"], "pos", chosen.get("position"))

    for cell in grid:
        if "pawnId" not in cell:
            continue
        r = rb.call("jawa/pawn_need", {
            "pawn": cell["pawnId"], "action": "need",
            "need": "RSW_DW_Power", "level": cell["charge"]})
        print(cell["cell"], "set need ->", json.dumps(r)[:200])
        cell["need_result"] = r

    with open(r"D:\Luke\dev\Rimworld\Transient\droidworks_detonation_review\grid_with_ids.json", "w") as f:
        json.dump(grid, f, indent=2)
