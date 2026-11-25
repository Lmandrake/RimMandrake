#!/usr/bin/env python3
"""selftest_dispatch_clone_behind_line.py [LINE] — the DISPATCH_CLONE_BEHIND alarm fires on a dispatch clone that stays
behind, never on one tick of ordinary lag.

Instance (OPS_DISPATCH_CLONE_BEHIND_UNSTICK_YUYW): with the line at 5 min, single readings of 5.4-7.0 min that level on
the next tick opened the alarm 22 times 2026-11-16..11-24 (ops_watch/series/maturation.jsonl on Archmagi: no reading over
5 min lasted past one tick after 2026-11-20). The danger is timers running old code for long: 40 min on 2026-11-15 and
86 min on 2026-11-19. `5` as an argument replays the instance's line and fails; with no argument the shipped rule is read
from ops_watch_rules.json."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ops_watch as OW  # noqa: E402

FAILS = []


def check(ok, what):
    print("%s %s" % ("ok  " if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


def main(argv):
    rules = json.loads((HERE / "ops_watch_rules.json").read_text())
    rows = rules if isinstance(rules, list) else next(v for v in rules.values()
                                                      if isinstance(v, list) and any(isinstance(r, dict) and r.get("key") == "maturation.clone_behind_min" for r in v))
    rule = next(r for r in rows if isinstance(r, dict) and r.get("key") == "maturation.clone_behind_min")
    line = float(argv[0]) if argv else rule["value"]
    for blip in (5.4, 6.0, 6.8, 7.0):
        check(not OW._cmp(blip, rule["op"], line), "a one-tick lag of %.1f min does not alarm (line %s %g)" % (blip, rule["op"], line))
    for stuck in (40.0, 86.1):
        check(OW._cmp(stuck, rule["op"], line), "a clone stuck %.1f min behind alarms (line %s %g)" % (stuck, rule["op"], line))
    print("FAIL %d" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
