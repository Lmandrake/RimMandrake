"""MIDCHANNEL_ISLAND_FILL_REACH_UNMEASURED: SB_islands_restore_reach asserts the measured outcome. Offline: reach_verdict's
three outcomes, and the mock run of the `reach` section walks every staging path to a mock PASS. Can-fail: an unreachable
square, a square left part-filled, or one the restore still tracks must each read FAIL with its outcome. Proves the SCRIPT,
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


def main():
    fails = []
    cases = [
        ((8, True, [7, 6, 5, 4, 3, 2, 1, 0], False), ("PASS", "reached_and_grounded")),
        ((8, False, [], None), ("FAIL", "needs_bridge_first")),
        ((8, None, [], None), ("FAIL", "needs_bridge_first")),
        ((8, True, [7, 6, 6], None), ("FAIL", "reached_not_grounded")),
        ((8, True, [], None), ("FAIL", "reached_not_grounded")),
        ((8, True, [7, 0], True), ("FAIL", "reached_and_grounded")),
    ]
    for args, want in cases:
        got = SBP.reach_verdict(*args)[:2]
        if got != want:
            fails.append("reach_verdict%r -> %r, want %r" % (args, got, want))
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "reach.json")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = SBP.main(["--mock", "--only", "reach", out])
        rows = json.load(open(out, encoding="utf-8"))["rows"]
        ids = [r["id"] for r in rows]
        if rc != 0 or ids != ["SB_islands_restore_reach"]:
            fails.append("mock reach run rc=%s rows=%s" % (rc, ids))
        else:
            det = rows[0]["detail"]
            if det.get("mock") != "PASS" or det.get("outcome") != "reached_and_grounded" or det.get("depths", [None])[-1] != 0:
                fails.append("mock reach row %s" % json.dumps(det)[:200])
    for f in fails:
        print("FAIL:", f)
    print("suspension bridge reach row: %d verdict cases, %s" % (len(cases), "ok" if not fails else "FAIL"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
