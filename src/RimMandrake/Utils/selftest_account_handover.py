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
    ("system", M(1), 1, "idle", "not live: nothing to do, and no marker, so a later link stays armed"),
]
bad = 0
for live, row, good, want, name in CASES:
    got = H.decide(live, row, good, "lukas", 1)[0]
    if got != want:
        bad += 1
    print("%s %s" % ("ok  " if got == want else "FAIL", name))
for row, good, want, name in [(M(21), 21, "switch", "steven at his authorized floor switches"),
                              (M(22), 22, "wait", "steven above his floor waits"),
                              (None, 22, "switch", "steven blind within a point of his floor counts as past it")]:
    got = H.decide("steven", row, good, "steven", 21)[0]
    if got != want:
        bad += 1
    print("%s %s" % ("ok  " if got == want else "FAIL", name))
import datetime
Z = datetime.timezone(datetime.timedelta(hours=-8))
NOW = datetime.datetime(2026, 11, 4, 14, 0, tzinfo=Z)
for until, want, name in [(None, False, "no --until never expires"),
                          ("2026-11-04T13:59:00-08:00", True, "a link past its reset has expired"),
                          ("2026-11-04T14:00:00-08:00", True, "expiry is inclusive"),
                          ("2026-11-04T23:00:00+00:00", False, "an offset is honoured (15:00 PST, still open)"),
                          ("2026-11-11T13:59:00-08:00", False, "a link before its end stays armed")]:
    got = H.expired(until, NOW)
    if got != want:
        bad += 1
    print("%s %s" % ("ok  " if got == want else "FAIL", name))
try:
    H.expired("2026-11-04T13:59:00", NOW)
    bad += 1
    print("FAIL an offset-less --until is refused")
except SystemExit:
    print("ok   an offset-less --until is refused")
print("selftest_account_handover: %s" % ("PASS" if not bad else "RED: %d failed" % bad))
raise SystemExit(1 if bad else 0)
