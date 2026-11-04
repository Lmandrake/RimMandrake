#!/usr/bin/env python3
"""account_handover.decide: the line, the blind meter, and an account that is not live. No network, no switch."""
import account_handover as H

M = lambda left, source="MEASURED", stale=False: {"week_pct_left": left, "source": source, "stale": stale}
CASES = [
    ("lukas", M(3), 3, "wait", "above the line waits"),
    ("lukas", M(1), 1, "switch", "at the line switches"),
    ("lukas", M(0), 0, "switch", "under the line switches"),
    ("lukas", M(1, stale=True), 3, "wait", "a stale figure far from the line never switches"),
    ("lukas", M(None, "ESTIMATE"), 2, "switch", "blind after near the line counts as past it"),
    ("lukas", None, 2, "switch", "no row after near the line counts as past it"),
    ("lukas", None, None, "wait", "never read waits"),
    ("system", M(1), 1, "done", "already moved: nothing to do"),
]
bad = 0
for live, row, good, want, name in CASES:
    got = H.decide(live, row, good, "lukas", 1)[0]
    if got != want:
        bad += 1
    print("%s %s" % ("ok  " if got == want else "FAIL", name))
print("selftest_account_handover: %s" % ("PASS" if not bad else "RED: %d failed" % bad))
raise SystemExit(1 if bad else 0)
