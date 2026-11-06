#!/usr/bin/env python3
"""archmagi_switch_reading.py - is the Archmagi backfill's trial switch alive? (ARCHMAGI_BACKFILL_WIRE_UNIT_RUNNER_WANTED)

testq.py's tick writes archmagi_state.json key "switch" (with read_at, UTC) only when TESTQ_ARCHMAGI=1 reaches
switch_step, and last_gate holds the first closed gate. A gate reading "no runner clone ..." means the runner clone is
missing; "off (...)" means the unit lacks TESTQ_ARCHMAGI=1. Any other gate (or none) proves both pieces are in place.

  archmagi_switch_reading.py [STATE_JSON] [--max-age-s N]     exit 0 alive, 1 not; one line either way
"""
import argparse
import calendar
import json
import sys
import time

DEFAULT = "/mnt/d/ClaudeWork/rimmandrake/testq/archmagi_state.json"
DEAD_GATES = ("no runner clone", "off")


def verdict(state, now, max_age_s):
    """-> (ok, line) for one archmagi_state.json dict."""
    sw = state.get("switch") or {}
    read_at = sw.get("read_at")
    if not read_at:
        return False, "FAIL no switch.read_at: switch_step never ran (TESTQ_ARCHMAGI=1 not in the tick's environment?)"
    t = calendar.timegm(time.strptime(read_at[:19], "%Y-%m-%dT%H:%M:%S"))
    gate = str(state.get("last_gate", ""))
    if now - t >= max_age_s:
        return False, "FAIL switch.read_at %s is %d s old (max %d)" % (read_at, now - t, max_age_s)
    if gate.startswith(DEAD_GATES):
        return False, "FAIL gate %r" % gate
    return True, "OK read_at %s gate %s" % (read_at, gate)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("state", nargs="?", default=DEFAULT)
    ap.add_argument("--max-age-s", type=int, default=7200)
    a = ap.parse_args(argv)
    try:
        state = json.load(open(a.state))
    except (OSError, ValueError) as e:
        print("FAIL cannot read %s: %s" % (a.state, e))
        return 1
    ok, line = verdict(state, time.time(), a.max_age_s)
    print(line)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
