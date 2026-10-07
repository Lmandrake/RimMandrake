"""Diagnose KA scenes: stage each named scene, step N ticks, print verdict + the EK journal lines since staging.
python.exe ka_diag.py scene1,scene2 [ticks]  (run from repo root)"""
import json, os, sys
REPO = os.getcwd()
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
KA = "RimMandrake.KineticArms.RM_KineticArmsProof"
EK = "RimMandrake.ExplosiveKnockback.RM_KnockbackProof"

def call(b, typ, method, arg):
    r = b.call("jawa/static_call", {"type": typ, "method": method, "args": arg}, check=False)
    if isinstance(r, dict):
        if r.get("success") is False:
            return "ERROR %s" % json.dumps(r)[:300]
        return str(r.get("result", r.get("value", r)))
    return str(r)

names = sys.argv[1].split(",")
ticks = int(sys.argv[2]) if len(sys.argv) > 2 else 90
host, port, token = resolve_endpoint()
with RimBridge(host=host, port=port, token=token, timeout=600.0) as b:
    org = call(b, KA, "Origins", str(len(names))).split(";")
    call(b, KA, "Settings", "reset")
    for n, o in zip(names, org):
        call(b, EK, "Clear", "x")
        print(call(b, KA, "Stage", "%s,%s" % (n, o)))
        b.call("rimworld/step_game_ticks", {"ticks": ticks}, check=False)
        print(call(b, KA, "Verdict", n))
        print(call(b, EK, "Journal", "40"))
        print("-" * 40)
    call(b, KA, "Settings", "reset")
