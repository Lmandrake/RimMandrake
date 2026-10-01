"""Zuurrik: unwounded-pawn rule, then settings toggle off (no wake) and back on (wake)."""
from bx import call
from st_sandswim_lib import step, pawns, spawn
import json
T = "RimMandrake.Stillsand.RM_StillsandSettings"
def zs(): return [(p["id"], p["x"], p["z"]) for p in pawns() if p.get("kindDef") == "RM_Zuurrik" and not p.get("dead")]
def inj(pid):
    for p in pawns():
        if p["id"] == pid:
            return [h["def"] for h in (p.get("health") or {}).get("hediffs", [])], p.get("dead")
    return "absent"
sw = [z for z in zs() if z[0] != "RM_Zuurrik111924"]
print("swarm", sw)
x, z = sw[0][1], sw[0][2]
hares, _ = spawn("Hare", x + 1, z + 1, "none", 3)
print("hares", hares, [inj(h) for h in hares])
for i in range(3):
    step(600); print("t", i, [inj(h) for h in hares], zs(), flush=True)
print("get", call("jawa/mod_settings_field", {"typeName": T, "action": "get", "field": "zuurrikEnabled"}).get("value"))
print("set off", json.dumps(call("jawa/mod_settings_field", {"typeName": T, "action": "set", "field": "zuurrikEnabled", "value": "false"}))[:300])
for pid, x, z in zs():
    if pid != "RM_Zuurrik111924":
        call("rimworld/execute_debug_action", {"path": "Actions\\T: Kill", "x": x, "z": z})
print("after kill", zs())
for i in range(3):
    step(600); print("off t", i, zs(), flush=True)
print("set on", json.dumps(call("jawa/mod_settings_field", {"typeName": T, "action": "set", "field": "zuurrikEnabled", "value": "true"}))[:300])
for i in range(3):
    step(600); print("on t", i, zs(), flush=True)
