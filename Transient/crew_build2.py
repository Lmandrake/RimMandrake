import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
spec = json.load(open(r"D:\Luke\dev\Rimworld\infrastructure\state\items\PLAYER_START_SITE_1.crew.json"))
CELLS = [(183,150),(185,148),(189,151),(150,149),(151,150)]
AGES = {"Nekko Vok": 52, "Tobb Nkik": 38, "Griz Utinn": 34, "Yeku": 19, "Wim Ateeka": 41}
with RimBridge(host, port, token) as rb:
    # out with the old crew
    for pid in ("Human469918", "Human469907"):
        r = rb.call("rimworld/execute_debug_action", {"path": "Actions\\T: Destroy", "thingId": "Thing_" + pid})
        print("removed", pid, r.get("success"))
    made = []
    for f, (x, z) in zip(spec["founders"], CELLS):
        s = rb.call("jawa/spawn_pawn", {"kindDef": "RSW_Jawa", "faction": "player", "x": x, "z": z, "count": 1})
        pid = (s.get("pawns") or s.get("spawned") or [{}])[0].get("id") if isinstance(s.get("pawns") or s.get("spawned"), list) else s.get("pawnId") or s.get("id")
        print(f["name"], "spawned ->", s.get("success"), pid, str(s)[:120] if not pid else "")
        if not pid: continue
        parts = f["name"].split()
        first, last = (parts[0], parts[1]) if len(parts) > 1 else (parts[0], "")
        i = rb.call("jawa/set_pawn_identity", {"pawn": pid, "first": first, "last": last or first, "nick": f["nick"]})
        a = rb.call("jawa/set_pawn_age", {"pawn": pid, "biologicalYears": AGES[f["name"]], "allowBackwards": True})
        for sk, lvl in f["skills"].items():
            rb.call("jawa/set_pawn_skill", {"pawn": pid, "skill": sk, "level": lvl, "passion": "Minor" if lvl >= 8 else "None"})
        for tr in f["traits"]:
            t = rb.call("jawa/pawn_traits", {"pawn": pid, "action": "add", "trait": tr.replace(" ", ""), "force": True})
            if not t.get("success"): print("  trait fail:", tr, str(t.get("message",""))[:70])
        made.append((f["name"], pid))
    print("crew:", made)
    p = rb.call("rimworld/list_colonists", {})
    print("colonists now:", [(c.get("name"), c.get("pawnId")) for c in p.get("colonists", p.get("pawns", []))])
