"""Offline selftest of liquid_checks.py's timing and verdict logic (WSL python3; no bridge). Each bar must be able to go red.
THEFT_ROW_REPAIR_WITNESS_WALKS_OFF: a FAIL needs a LIVE witness present at the theft check; a witness that walked off is
UNMEASURED (HARNESS), never FAIL."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import liquid_checks as LC  # noqa: E402

W = [{"id": 1, "x": 81, "z": 185, "downed": False, "dead": False}]
cases = []


def case(got, want, why):
    cases.append((got, want, why))


case([LC.ticks_until(t, LC.WITNESS_PHASE) for t in (4, 5, 254, 1000, 1003)], [0, 249, 0, 4, 1], "ticks_until wraps at 250")
case((1000 + LC.ticks_until(1000, LC.WITNESS_PHASE)) % 250, LC.WITNESS_PHASE, "step lands on the witness phase")
case(LC.WITNESS_PHASE < LC.CHECK_PHASE <= LC.WITNESS_PHASE + 5, True, "witness spawns just BEFORE the theft check")
case(LC.theft_verdict(40, 0, 1, 0, 1, W)[0], "PASS", "caught + letter + live witness")
case(LC.theft_verdict(40, 0, 0, 0, 0, W)[0], "FAIL", "live witness present, mod caught nothing")
case(LC.theft_verdict(40, 0, 0, 0, 0, [])[0], "UNMEASURED", "witness walked off / absent: harness, not mod")
case(LC.theft_verdict(40, 0, 0, 0, 0, [dict(W[0], downed=True)])[0], "UNMEASURED", "downed witness is not a witness")
case(LC.theft_verdict(40, 0, 0, 0, 0, [dict(W[0], dead=True)])[2].get("why", "")[:7], "no live", "reason names the lost witness")
case(LC.theft_verdict(0, 0, 0, 0, 0, W)[0], "UNMEASURED", "nothing drawn: no theft to spot")
case(LC.theft_verdict(40, 0, 1, 0, 0, W)[0], "FAIL", "caught rose but no letter")
case(LC.theft_verdict(40, 0, 1, 0, 1, W, "site")[0], "UNMEASURED", "precondition failed")
case(LC.theft_verdict(40, None, 1, 0, 1, W)[0], "UNMEASURED", "caught unreadable")
case(LC.goodwill_verdict(10, 8, 0, -2, 2, True)[0], "PASS", "goodwill fell by perDay")
case(LC.goodwill_verdict(10, 10, 0, 0, 2, True)[0], "FAIL", "caught but no charge")
case(LC.goodwill_verdict(10, 8, 0, -2, 2, False)[0], "UNMEASURED", "never caught")
case(LC.dump_no_pump_verdict([100, 98, 96], 0, 2)[0], "PASS", "slow drain wets the canal")
case(LC.dump_no_pump_verdict([100, 100], 0, 0)[0], "FAIL", "no drain")
case(LC.dump_no_pump_verdict([0, 0], 0, 0)[0], "UNMEASURED", "tank never held liquid")
case(LC.dump_pump_verdict([100, 50], 0, 5, 4)[0], "PASS", "pump faster than no-pump")
case(LC.dump_pump_verdict([100, 97], 0, 5, 4)[0], "FAIL", "pump not faster")
case(LC.dump_pump_verdict([100, 50], 0, 5, None)[0], "UNMEASURED", "no slow rate to compare")
bad = [(g, w, y) for g, w, y in cases if g != w]
for g, w, y in bad:
    print("FAIL", y, "got", g, "want", w)
print("selftest_liquid_checks: %d/%d" % (len(cases) - len(bad), len(cases)))
sys.exit(1 if bad else 0)
