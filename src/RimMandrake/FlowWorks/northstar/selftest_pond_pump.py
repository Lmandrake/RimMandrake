"""Offline selftest of pond_pump.py's verdicts (WSL python3; no bridge). Each bar must be able to go red."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pond_pump as PP  # noqa: E402

cases = [
    (PP.draw_verdict(0, 80000, 30.0, 22.0)[0], "PASS", "8 levels: stock -8, tank +80000 dL (8 kL)"),
    (PP.draw_verdict(0, 80000, 30.0, 23.0)[0], "FAIL", "a unit created from nothing"),
    (PP.draw_verdict(0, 70000, 30.0, 22.0)[0], "FAIL", "a level lost on the way"),
    (PP.draw_verdict(0, 0, 30.0, 30.0)[0], "FAIL", "the pump moved nothing"),
    (PP.draw_verdict(None, 80000, 30.0, 22.0)[0], "UNMEASURED", "no tank read"),
    (PP.draw_verdict(0, 8, 30.0, 22.0)[0], "FAIL", "raw 1:1 (stock units == tank units) is not the bridged bar"),
    (PP.draw_verdict(0, 40, 30.0, 22.0)[0], "FAIL", "the old 5-per-level bridge is not the bar"),
    (PP.refill_verdict([{"stock": 23.0, "receded": 2}, {"stock": 25.1, "receded": 1}], 22.0, 2)[0], "PASS", "rise + re-wet"),
    (PP.refill_verdict([{"stock": 25.1, "receded": 2}], 22.0, 2)[0], "FAIL", "stock rose, nothing re-wet"),
    (PP.refill_verdict([{"stock": 22.0, "receded": 2}], 22.0, 2)[0], "FAIL", "no refill"),
    (PP.refill_verdict([{"stock": 25.0, "receded": 0}], 24.0, 0)[0], "UNMEASURED", "draw receded nothing"),
    (PP.refill_verdict([], 22.0, 2)[0], "UNMEASURED", "no reads"),
    (PP.engine_gate(False)[0], "UNMEASURED", "engine off -> refill row UNMEASURED"),
    (PP.engine_gate("false")[0], "UNMEASURED", "engine off as string"),
    (PP.engine_gate(None)[0], "UNMEASURED", "engine setting unread is not 'on'"),
    (PP.engine_gate(True)[0], None, "engine on -> refill runs"),
    # POND_PUMP_FIX_LAST_DROP_COUNTS phase C: (drain, stage)
    (PP.drain_verdict([{"units": 0, "stock": 2.35}, {"units": 23500, "stock": 0.0}], {"a": "Mud", "b": "RM_Lakebed"})[:2],
     ("PASS", "PASS"), "a 2.35-notch pond pumped to 0: tank +23,500 dL, squares staged"),
    (PP.drain_verdict([{"units": 0, "stock": 2.35}, {"units": 20000, "stock": 0.35}], {"a": "Mud"})[:2],
     ("FAIL", "UNMEASURED"), "the last 0.35 notch stranded (the old whole-notch rule)"),
    (PP.drain_verdict([{"units": 0, "stock": 2.35}, {"units": 20000, "stock": 0.35}], {"a": "Mud"}, tank_full=True)[:2],
     ("UNMEASURED", "UNMEASURED"), "a full tank stopped it, not the pump"),
    (PP.drain_verdict([{"units": 0, "stock": 2.35}, {"units": 23000, "stock": 0.0}], {"a": "Mud"})[0],
     "FAIL", "500 dL lost between the pond and the tank"),
    (PP.drain_verdict([{"units": 0, "stock": 2.35}, {"units": 23500, "stock": 0.0}], {"a": "WaterShallow", "b": "Mud"})[1],
     "FAIL", "a square still reads wet with 0 dL left"),
    (PP.drain_verdict([{"units": 0, "stock": 2.35}, {"units": 23500, "stock": 0.0}], {"a": None})[1],
     "UNMEASURED", "an unread terrain is not a pass"),
    (PP.drain_verdict([{"units": 0, "stock": 2.35}], {"a": "Mud"})[0], "UNMEASURED", "one read is no window"),
]
bad = [(got, want, why) for got, want, why in cases if got != want]
for got, want, why in bad:
    print("FAIL", why, "got", got, "want", want)
print("selftest_pond_pump: %d/%d" % (len(cases) - len(bad), len(cases)))
sys.exit(1 if bad else 0)
