import json, sys, os
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
h, p, t = resolve_endpoint()
cells = [(110, 60), (114, 60)]
with RimBridge(h, p, t) as B:
    def rd():
        r = B.call("jawa/flowworks_excavation_rect", {"x": 110, "z": 60, "w": 5, "h": 1, "onlyNonZero": False})
        m = {(q["x"], q["z"]): (q.get("d"), q.get("terrain")) for q in r.get("rows") or []}
        return [m.get(c) for c in cells]
    print("before", rd())
    for i in range(int(sys.argv[1]) if len(sys.argv) > 1 else 6):
        s = B.call("rimworld/step_game_ticks", {"ticks": 500})
        pw = B.call("jawa/list_pawns", {}) or {}
        js = [(q.get("id") or q.get("pawnId"), q.get("job") or q.get("curJob"), q.get("position")) for q in (pw.get("pawns") or []) if str(q.get("id") or q.get("pawnId") or "").startswith(("Mech_Tunneler25068", "Human25065"))]
        print(i, s.get("advancedTicks"), rd(), js)
