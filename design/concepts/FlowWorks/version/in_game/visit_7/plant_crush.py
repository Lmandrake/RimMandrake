"""plant_crush.py <out.json> [crush|unarmed]: planted states for the underpass rows (visit 7 repairs).

crush (default): the crush fall is aimed at an off-map square ("-1,-1"): no deck falls, nobody under it is hurt, so
UND_crush_below_and_wreck must read FAIL.
unarmed: each gunner's revolver is taken away again right after the proof hands it over (pawn_gear clear equipment), so a
UND_shot_* row must be withheld (UNMEASURED, SITE), never PASS or FAIL. Runs suspension_bridge_proof.py --only underpass;
every other call goes through as written."""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 6))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "FlowWorks", "northstar"))
import validation_core as V  # noqa: E402

orig = V.Guarded.call
seen = {"fell": 0, "unarmed": 0}
MODE = sys.argv[2] if len(sys.argv) > 2 else "crush"


def call(self, tool, _answer=False, **kw):
    if MODE == "crush" and tool == "jawa/static_call" and kw.get("method") == "ProofFell" and kw.get("args") not in ("-1,-1", None):
        seen["fell"] += 1
        kw = dict(kw, args="-1,-1")          # the plant: the deck over the pawn never falls
    r = orig(self, tool, _answer, **kw)
    if MODE == "unarmed" and tool == "jawa/pawn_gear" and kw.get("action") == "equip":
        seen["unarmed"] += 1                 # the plant: the gun handed over is taken away again
        orig(self, "jawa/pawn_gear", True, pawn=kw.get("pawn"), action="clear", clearWhat="equipment")
    return r


V.Guarded.call = call
import suspension_bridge_proof as SBP  # noqa: E402
rc = SBP.main([sys.argv[1], "--only", "underpass"])
print("plant_crush %s: %d ProofFell call(s) redirected off-map, %d gun(s) taken away" % (MODE, seen["fell"], seen["unarmed"]))
sys.exit(rc)
