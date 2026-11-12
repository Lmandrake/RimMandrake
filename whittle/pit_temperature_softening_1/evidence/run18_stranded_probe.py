import sys, os, json
sys.path.insert(0, os.getcwd())
import proof_hose as PH
B = PH.PB()
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
print(str(B.call("rimworld/get_ui_state"))[:400])
B.call("jawa/clear_ui", all=True)
print(str(B.call("rimworld/get_ui_state"))[:300])
def pos():
    p = ((B.call("jawa/pawn_get", pawn="Human234") or {}).get("pawns") or [{}])[0]
    return p.get("position"), p.get("drafted")
print("before", pos())
r = B.call("jawa/order_pawn", pawnId="Human234", x=119, z=129, draft=True, unpause=True, waitTicks=900, timeoutSeconds=25) or {}
print("order", json.dumps(r, default=str)[:700])
print("after", pos(), str(B.call("jawa/static_call", type=NSP, method="ProofClimb", args="pawn:Human234", _answer=True))[:200])
