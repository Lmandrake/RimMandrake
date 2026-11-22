"""MIDCHANNEL_ISLAND_FILL_REACH_UNMEASURED: SB_islands_restore_reach asserts the measured outcome. Offline: reach_verdict's
outcomes, and the mock run of the `reach` section walks every staging path to a mock PASS. Can-fail: a lone mid square the
reach says yes to (the climb rule says no), an edge no bank colonist can touch, a square left part-filled, or one the restore
still tracks must each read FAIL with its outcome; a planted lying reach veto ("yes" / "no") must turn the mock run red. Proves the SCRIPT,
never the game (the live row is infrastructure/state/live_proofs/MIDCHANNEL_ISLAND_FILL_REACH_UNMEASURED.txt).

    python3 src/RimMandrake/FlowWorks/northstar/selftest_suspension_bridge_reach.py
"""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import suspension_bridge_proof as SBP  # noqa: E402


def _mock(fault):
    SBP.FakeBridge.reach_fault = fault
    try:
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "reach.json")
            with redirect_stdout(io.StringIO()):
                rc = SBP.main(["--mock", "--only", "reach", out])
            return rc, json.load(open(out, encoding="utf-8"))["rows"]
    finally:
        SBP.FakeBridge.reach_fault = None


def main():
    fails = []
    G = lambda n: {"can": True, "depths": list(range(n - 1, -1, -1)), "tracked": False}  # noqa: E731
    cases = [
        ((8, False, G(8), G(8)), ("PASS", "reached_and_grounded")),
        ((8, True, G(8), G(8)), ("FAIL", "lone_square_reach_says_yes")),
        ((8, None, G(8), G(8)), ("FAIL", "lone_square_unread")),
        ((8, False, {"can": False, "depths": []}, {"can": None, "depths": []}), ("FAIL", "needs_bridge_first")),
        ((8, False, G(8), {"can": False, "depths": []}), ("FAIL", "mid_unreachable_after_edge")),
        ((8, False, {"can": True, "depths": [7, 6, 6]}, {"can": None, "depths": []}), ("FAIL", "reached_not_grounded")),
        ((8, False, G(8), {"can": True, "depths": []}), ("FAIL", "reached_not_grounded")),
        ((8, False, G(8), dict(G(8), tracked=True)), ("FAIL", "reached_and_grounded")),
        ((8, False, dict(G(8), tracked=None), G(8)), ("FAIL", "reached_and_grounded")),
    ]
    for args, want in cases:
        got = SBP.reach_verdict(*args)[:2]
        if got != want:
            fails.append("reach_verdict%r -> %r, want %r" % (args, got, want))
    for fault, want in ((None, ("PASS", "reached_and_grounded")), ("yes", ("FAIL", "lone_square_reach_says_yes")),
                        ("no", ("FAIL", "needs_bridge_first"))):
        rc, rows = _mock(fault)
        ids = [r["id"] for r in rows]
        if rc != (0 if fault is None else 1) or ids != ["SB_islands_restore_reach"]:
            fails.append("mock reach run fault=%s rc=%s rows=%s" % (fault, rc, ids))
            continue
        det = rows[0]["detail"]
        got = (det.get("mock"), det.get("outcome"))
        if got != want:
            fails.append("mock reach fault=%s -> %r, want %r (%s)" % (fault, got, want, json.dumps(det)[:200]))
        elif fault is None and (det["mid"]["depths"][-1:] != [0] or det["edge"]["depths"][-1:] != [0]):
            fails.append("mock reach row grounded nothing: %s" % json.dumps(det)[:200])
    # RIMMANDRAKE_UNSTICK_FLOWWORKS_FILL_JOB_HOLDS_GRAVEL_BESIDE_THE_HOLE: the worker is staged at a known Mining and its
    # MiningSpeed read back. A planted slow worker (speed 0.1, Mining 0: the visit 6 "stall") must withhold the row, never PASS.
    SBP.FakeBridge.worker_speed = 0.1
    try:
        rc, rows = _mock(None)
    finally:
        SBP.FakeBridge.worker_speed = 1.0
    det = rows[0]["detail"] if rows else {}
    why = json.dumps(det.get("unmeasuredBecause") or [])
    if det.get("mock") == "PASS" or "MiningSpeed" not in why:
        fails.append("mock reach with a slow worker (MiningSpeed 0.1) -> %r, unmeasuredBecause %s; want withheld on the "
                     "worker's MiningSpeed" % (det.get("mock"), why[:200]))
    # a colonist whose Mining is disabled is drafted and another spawned (visit 7); every one disabled withholds the row
    for planted, want_pass in ((1, True), (99, False)):
        SBP.FakeBridge.skill_disabled = planted
        try:
            rc, rows = _mock(None)
        finally:
            SBP.FakeBridge.skill_disabled = 0
        det = rows[0]["detail"] if rows else {}
        if (det.get("mock") == "PASS") != want_pass:
            fails.append("mock reach with %d Mining-disabled colonist(s) first -> %r, want %s" % (
                planted, det.get("mock"), "PASS" if want_pass else "withheld"))
    for f in fails:
        print("FAIL:", f)
    print("suspension bridge reach row: %d verdict cases + 6 mock runs (1 healthy, 2 planted lying reach, 1 planted slow "
          "worker, 2 planted Mining-disabled), worst=%s limit=0 "
          "fails, %s" % (len(cases), len(fails), "ok" if not fails else "FAIL"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
