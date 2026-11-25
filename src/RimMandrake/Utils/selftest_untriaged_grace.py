#!/usr/bin/env python3
"""Class guard for OPS_FINDINGS_DIAGNOSE_XZLM: flow.untriaged_findings rings only on a finding past one judge cycle.

A finding filed after the daily findings judge has no outcome until the next judge run, by design; the alarm rang on every
such finding, every day (alarms_log.jsonl 2026-11-22..24 on Archmagi). The fold is stubbed: only the age rule is tested
here (selftest_ops_watch drives the real fold). The clock is ops_watch's own time.time, so a reading without the age rule
fails these checks instead of crashing on a new parameter.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import findings_fold as FF  # noqa: E402
import ops_watch as OW  # noqa: E402

FAILS = []


def check(name, cond, got=None):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  got %r" % (got,)))
    if not cond:
        FAILS.append(name)


def main():
    ftype = sorted(FF.load_rules()["finding_types"])[0]
    f = {"seat": "RUNNER", "event": "finding", "id": "IT_R", "type": ftype, "name": "X_1", "ts": "2026-11-24T16:50:00Z"}
    born = OW.epoch(f["ts"])
    grace = getattr(OW, "UNTRIAGED_GRACE_S", 26 * 3600)
    real_no, real_time = FF.no_outcome, OW.time.time
    FF.no_outcome = lambda *a, **k: {"X_1"}
    try:
        OW.time.time = lambda: born + 3 * 3600          # 3 h after the filing: tomorrow's judge has not run yet
        r = OW.untriaged_reading([f])
        check("a finding inside one judge cycle waits: no ring", r.get("m") == "MEASURED" and r.get("v") == 0, r)
        OW.time.time = lambda: born + grace + 60         # past a whole cycle with no outcome: the judge missed it
        r = OW.untriaged_reading([f])
        check("a finding past one judge cycle rings", r.get("m") == "MEASURED" and r.get("v") == 1, r)
        OW.time.time = lambda: born + 60
        r = OW.untriaged_reading([dict(f, ts="garbled")])
        check("a finding with no readable time counts", r.get("v") == 1, r)
        r = OW.untriaged_reading([dict(f, type="NOT_A_FOLDED_TYPE"), dict(f, ts="garbled")])
        check("only the fold's own finding types date a finding", r.get("v") == 1, r)
    finally:
        FF.no_outcome, OW.time.time = real_no, real_time
    print("ALL PASS" if not FAILS else "%d FAIL" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
