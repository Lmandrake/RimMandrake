#!/usr/bin/env python3
# selftest-timeout: 60
"""selftest_scratch_tmp_pressure_margin.py — scratch_reap's /tmp pressure trigger fires BELOW the TMP_FULL alarm line.

Class guard for OPS_TMP_DRAIN_RESTORE_JVCO: the trigger sat ON the alarm's 80 % line, so the reaper started draining
only after the alarm had fired (outage 2026-11-05T02:23Z, 86.2 %, with the 1 h pressure idle line already live).
Proves, with synthetic readings (the real /tmp decides nothing): a reading between the trigger and the alarm line is
pressure; one well under the trigger is not; the triggers follow the alarm's two lines in ops_watch_rules.json.
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FAILS = []
MARGIN = 10.0      # points under the alarm line the drain starts at


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def alarm_lines():
    """-> (used-% line, GB-free line) of the TMP_FULL alarm, read from ops_watch_rules.json however it is nested."""
    found = {}

    def walk(o):
        if isinstance(o, dict):
            if o.get("tag") == "TMP_FULL" and o.get("key") in ("disk.tmp_used_pct", "disk.tmp_free_gb"):
                found[o["key"]] = float(o["value"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(json.loads((HERE / "ops_watch_rules.json").read_text()))
    if len(found) != 2:
        raise SystemExit("FAIL TMP_FULL rules not found in ops_watch_rules.json: %s" % found)
    return found["disk.tmp_used_pct"], found["disk.tmp_free_gb"]


def main():
    for k in ("SCRATCH_REAP_TMP_PRESSURE_PCT", "SCRATCH_REAP_TMP_PRESSURE_GB"):
        os.environ.pop(k, None)
    import scratch_reap as s
    line, gb_line = alarm_lines()
    if hasattr(s, "tmp_pressure_lines"):
        trig, trig_gb = s.tmp_pressure_lines()
    else:
        trig, trig_gb = float(s.TMP_PRESSURE_PCT), float(s.TMP_PRESSURE_GB)
    ok(trig <= line - MARGIN, "the trigger (%.1f %%) sits %.0f points under the alarm line (%.1f %%)"
       % (trig, MARGIN, line))
    ok(trig_gb > gb_line, "the GB-free trigger (%.1f GB) fires before the alarm's %.1f GB line" % (trig_gb, gb_line))
    ok(s.tmp_low({"free_gb": gb_line + 0.5, "used_pct": 1.0}), "%.1f GB free (over the alarm, under the trigger) is pressure"
       % (gb_line + 0.5))
    near = line - MARGIN / 2
    ok(s.tmp_low({"free_gb": 50.0, "used_pct": near}), "a %.1f %% reading (under the alarm, past the trigger) is pressure" % near)
    ok(not s.tmp_low({"free_gb": 50.0, "used_pct": line - 3 * MARGIN}), "a calm reading is not pressure")
    ok(not s.tmp_low(None), "no reading is not pressure")
    print("FAILURES: %d" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
