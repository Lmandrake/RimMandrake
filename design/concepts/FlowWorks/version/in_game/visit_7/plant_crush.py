"""plant_crush.py <out.json>: the planted state for UND_crush_below_and_wreck (visit 7 repair of its harm reading).

Runs suspension_bridge_proof.py --only underpass with the crush fall aimed at an off-map square ("-1,-1"): no deck falls,
nobody under it is hurt, so the crush row must read FAIL. Every other call goes through as written."""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "northstar"))
import validation_core as V  # noqa: E402

orig = V.Guarded.call
seen = {"fell": 0}


def call(self, tool, _answer=False, **kw):
    if tool == "jawa/static_call" and kw.get("method") == "ProofFell" and kw.get("args") not in ("-1,-1", None):
        seen["fell"] += 1
        kw = dict(kw, args="-1,-1")          # the plant: the deck over the pawn never falls
    return orig(self, tool, _answer, **kw)


V.Guarded.call = call
import suspension_bridge_proof as SBP  # noqa: E402
rc = SBP.main([sys.argv[1], "--only", "underpass"])
print("plant_crush: %d ProofFell call(s) redirected off-map" % seen["fell"])
sys.exit(rc)
