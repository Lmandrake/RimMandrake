#!/usr/bin/env python3
"""selftest_validation_core_yield.py - the row-boundary yield in validation_core.row (ARCHMAGI_BACKFILL_WIRE_TRIAL_SWITCH).

work_allocation_framework_2026-10-26.md section 2: an Archmagi backfill attempt aborts at its next ROW BOUNDARY when an
agent takes the bridge, and records how far it got. testq writes TESTQ_YIELD_FILE; row() checks it after each row.
Proves: no env / no file -> rows go on; file present -> the row is recorded first, then YieldAtRowBoundary is raised,
the rows so far land in <file>.rows.json, and a driver's `except Exception` does not swallow it.
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validation_core as V  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    tmp = tempfile.mkdtemp(prefix="vc_yield_")
    yf = os.path.join(tmp, "yield.json")
    os.environ.pop("TESTQ_YIELD_FILE", None)
    rows = []
    V.row(rows, "a1", "PASS", "MOD", "no env")
    check(len(rows) == 1, "TESTQ_YIELD_FILE unset: the row is recorded and the proof goes on")
    os.environ["TESTQ_YIELD_FILE"] = yf
    V.row(rows, "a2", "PASS", "MOD", "env, no file")
    check(len(rows) == 2 and not os.path.exists(yf + ".rows.json"), "file absent: the proof goes on, nothing written")
    with open(yf, "w") as f:
        json.dump({"holder": "CONDUCTOR"}, f)
    raised = swallowed = False
    try:
        try:
            V.row(rows, "a3", "FAIL", "MOD", "after the take")
        except Exception:       # noqa: BLE001 - what a driver does; it must not catch the yield
            swallowed = True
    except V.YieldAtRowBoundary:
        raised = True
    check(raised and not swallowed, "file present: YieldAtRowBoundary raised, not swallowed by `except Exception`")
    check([r["id"] for r in rows] == ["a1", "a2", "a3"], "the row in hand was recorded before the yield")
    kept = json.load(open(yf + ".rows.json")).get("rows") or []
    check([r["id"] for r in kept] == ["a1", "a2", "a3"] and kept[2]["status"] == "FAIL",
          "the rows measured so far are kept beside the yield file: %s" % [r["id"] for r in kept])
    os.environ.pop("TESTQ_YIELD_FILE", None)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
