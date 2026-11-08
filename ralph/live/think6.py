"""think6.py <pawnNum>...: what each pawn's think tree hands it now (ProofThink), its cell's depths, held/trapped."""
import json, sys
import fwb
B = fwb.FW()
for a in sys.argv[1:]:
    r = B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_Patch_AttackTargetFinder_MeleeReach", method="ProofThink", args=a) or {}
    print("THINK", a, str(r.get("result") or r.get("message"))[:600])
    p = B.call("jawa/pawn_get", pawnId="Human" + a) or {}
    x, z = p.get("x") or (p.get("pawn") or {}).get("x"), p.get("z") or (p.get("pawn") or {}).get("z")
    if x is not None:
        rep = B.call("jawa/flowworks_pit_report", x=x, z=z) or {}
        print("PIT", a, x, z, json.dumps({k: v for k, v in rep.items() if k not in ("operation", "state")}, default=str)[:900])
