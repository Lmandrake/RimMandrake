"""think.py [save] -- (load save) then ProofThink for every hostile pawn."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fwb, story1  # noqa: E402
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
B = fwb.FW()
if len(sys.argv) > 1:
    B.call("rimworld/load_game", saveName=sys.argv[1]); print(fwb.V._wait_playing(B))
for p in story1.pawns(B, "hostile"):
    pid = int(re.sub(r"\D", "", str(p.get("id"))) or 0)
    r = B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_Patch_AttackTargetFinder_MeleeReach", method="ProofThink", args=str(pid)) or {}
    print(p.get("x"), p.get("z"), r.get("result") or r)
