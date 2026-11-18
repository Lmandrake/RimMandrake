#!/usr/bin/env python3
"""SCHEDULE_HARDEN_FAIL_CLOSED_NO_DEFAULTS: dispatcher.load_schedule refuses a schedule with a required key missing.
Planted fault on the real path: the shipped dispatcher_schedule.json with one key removed at a time."""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import dispatcher as D  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def load_with(mutate):
    with open(D.DEFAULT_SCHEDULE, encoding="utf-8") as f:
        sch = json.load(f)
    mutate(sch)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "s.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(sch, f)
        try:
            return D.load_schedule(p), None
        except Exception as e:  # noqa: BLE001
            return None, e


def main():
    check(load_with(lambda s: None)[1] is None, "the shipped schedule loads")
    keys = getattr(D, "REQUIRED_KEYS", None)
    check(bool(keys), "REQUIRED_KEYS is the one list of required keys")
    for k in keys or ():
        sch, err = load_with(lambda s, k=k: s.pop(k, None))
        check(sch is None and isinstance(err, D.ScheduleInvalid) and k in str(err), "missing %r refuses, naming it" % k)
    caps = getattr(D, "REQUIRED_CAPS", None)
    check(bool(caps), "REQUIRED_CAPS is the one list of required caps")
    for k in caps or ():
        sch, err = load_with(lambda s, k=k: s["caps"].pop(k, None))
        check(sch is None and isinstance(err, D.ScheduleInvalid) and k in str(err), "missing cap %r refuses, naming it" % k)
    sch, err = load_with(lambda s: s.pop("caps", None))
    check(sch is None and isinstance(err, D.ScheduleInvalid), "missing caps block refuses")
    check(not hasattr(D, "DEFAULTS") and not hasattr(D, "CAP_DEFAULTS"), "no default values remain in dispatcher")
    print("FAIL" if FAILS else "PASS", len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
