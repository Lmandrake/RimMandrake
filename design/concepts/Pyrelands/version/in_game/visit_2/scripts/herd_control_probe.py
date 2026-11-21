"""Visit 2: does herd_thirst's control herd (4 wild Muffalo) live and keep a readable RM_Thirst on the Pyrelands site?
python.exe, bridge held, the visit-2 site reloaded. Spawns 2 Muffalo and 2 RM_Ullai in open ash, sets RM_Thirst 0.8, then
reads each pawn's RM_Thirst, dead/downed and hediffs every game hour for 24 h. -> evidence/herd_control_probe.json"""
import sys, json
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
h, p, tk = resolve_endpoint()
out = {"hours": []}
with RimBridge(h, p, tk) as rb:
    call = lambda tool, **kw: rb.call(tool, kw)  # noqa: E731
    ids = {}
    for i, kind in enumerate(("Muffalo", "Muffalo", "RM_Ullai", "RM_Ullai")):
        r = call("jawa/spawn_pawn", kindDef=kind, x=125 + i * 3, z=125, faction="none", count=1)
        pid = ((r.get("pawns") or [{}])[0]).get("id"); ids[pid] = kind
        call("jawa/pawn_need", pawn=pid, action="need", need="RM_Thirst", level=0.8)
    out["ids"] = ids
    out["temp"] = {k: v for k, v in call("jawa/map_info").items() if "emp" in k}
    for hour in range(1, 25):
        call("jawa/safe_advance", ticks=2500, timeException=False)
        rows = dict((q.get("id"), q) for q in (call("jawa/list_pawns", limit=1000, includeHealth=True).get("pawns") or []))
        line = {"hour": hour}
        for pid in ids:
            q = rows.get(pid) or {}
            lv = next((n.get("level") for n in (call("jawa/pawn_need", pawn=pid, action="list").get("needs") or [])
                       if n.get("need") == "RM_Thirst"), None)
            line[pid] = {"thirst": lv, "dead": q.get("dead"), "downed": q.get("downed"), "listed": bool(q),
                         "hediffs": [str(x.get("def") or x.get("label") or x)[:30] for x in (q.get("hediffs") or [])][:6]}
        out["hours"].append(line)
print(json.dumps(out["temp"]))
for l in out["hours"][::4] + out["hours"][-1:]:
    print(json.dumps(l)[:600])
json.dump(out, open(r"design\concepts\Pyrelands\version\in_game\visit_2\evidence\herd_control_probe.json", "w"), indent=1)
