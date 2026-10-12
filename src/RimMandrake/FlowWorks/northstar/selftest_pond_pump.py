"""Offline selftest of pond_pump.py's verdicts (WSL python3; no bridge). Each bar must be able to go red."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pond_pump as PP  # noqa: E402

cases = [
    (PP.draw_verdict(0, 40, 30.0, 22.0)[0], "PASS", "8 levels: stock -8, tank +40"),
    (PP.draw_verdict(0, 40, 30.0, 23.0)[0], "FAIL", "a unit created from nothing"),
    (PP.draw_verdict(0, 35, 30.0, 22.0)[0], "FAIL", "a level lost on the way"),
    (PP.draw_verdict(0, 0, 30.0, 30.0)[0], "FAIL", "the pump moved nothing"),
    (PP.draw_verdict(None, 40, 30.0, 22.0)[0], "UNMEASURED", "no tank read"),
    (PP.draw_verdict(0, 8, 30.0, 22.0)[0], "FAIL", "raw 1:1 (stock units == tank units) is not the bridged bar"),
    (PP.refill_verdict([{"stock": 23.0, "receded": 2}, {"stock": 25.1, "receded": 1}], 22.0, 2)[0], "PASS", "rise + re-wet"),
    (PP.refill_verdict([{"stock": 25.1, "receded": 2}], 22.0, 2)[0], "FAIL", "stock rose, nothing re-wet"),
    (PP.refill_verdict([{"stock": 22.0, "receded": 2}], 22.0, 2)[0], "FAIL", "no refill"),
    (PP.refill_verdict([{"stock": 25.0, "receded": 0}], 24.0, 0)[0], "UNMEASURED", "draw receded nothing"),
    (PP.refill_verdict([], 22.0, 2)[0], "UNMEASURED", "no reads"),
]
bad = [(got, want, why) for got, want, why in cases if got != want]
for got, want, why in bad:
    print("FAIL", why, "got", got, "want", want)
print("selftest_pond_pump: %d/%d" % (len(cases) - len(bad), len(cases)))
sys.exit(1 if bad else 0)
