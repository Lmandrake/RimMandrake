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
    for f in fails:
        print("FAIL:", f)
    print("suspension bridge reach row: %d verdict cases + 3 mock runs (1 healthy, 2 planted lying reach), worst=%s limit=0 "
          "fails, %s" % (len(cases), len(fails), "ok" if not fails else "FAIL"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
