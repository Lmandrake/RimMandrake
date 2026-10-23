"""Offline checks for deep_stone_live.job_gate (DEEP_STONE_FIX_NOBODY_PICKS_UP_SHOVEL). No bridge."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import deep_stone_live as D  # noqa: E402

fails = []


def check(name, cond):
    print("%-4s  %s" % ("ok" if cond else "FAIL", name))
    if not cond:
        fails.append(name)


P = {"success": True, "designationPresent": True,
     "workGiver": {"shouldSkip": False, "hasJobOnCell": True, "jobDef": "RM_DigCanalJob", "designationDeletedByWorkGiver": False},
     "pawn": {"workTypeDisabled": False}}
O = {"accepted": True}
check("probe ok + order accepted: go", D.job_gate(P, O)[0] is True)
check("can-fail: giver hands no job", D.job_gate(dict(P, workGiver=dict(P["workGiver"], hasJobOnCell=False)), O)[0] is False)
check("can-fail: wrong job def", D.job_gate(dict(P, workGiver=dict(P["workGiver"], jobDef="Mine")), O)[0] is False)
check("can-fail: mining disabled", D.job_gate(dict(P, pawn={"workTypeDisabled": True}), O)[0] is False)
check("can-fail: no designation", D.job_gate(dict(P, designationPresent=False), O)[0] is False)
check("can-fail: order refused", D.job_gate(P, {"accepted": False, "note": "x"})[0] is False)
check("can-fail: probe tool missing", D.job_gate({"success": False, "message": "no tool"}, O)[0] is False)
check("can-fail: empty", D.job_gate({}, {})[0] is False)
print("%d failed" % len(fails))
sys.exit(1 if fails else 0)
