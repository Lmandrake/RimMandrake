#!/usr/bin/env python3
"""selftest_scratch_reap_apply_order.py — the hourly apply takes the small rows first unless the disk is short
(RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH). Measured 2026-11-18 15:03 PST: apply spent 1178 s on
two DELETE clones of 284 MB and 2.1 GB and deferred all 333 ARCHIVE clones (median 29 KB) behind them, run after run.

`act` is stubbed with a fixed cost per row, so the budget runs out on a known row. Proves: off pressure, small clones go
first and a big one is what waits; under disk or /tmp pressure, the biggest clone goes first, as before; sessions follow
clones either way, so a shell is judged with its clones gone. Pure: no filesystem, no clock beyond the stub's."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scratch_reap as s                                    # noqa: E402

FAILS = []


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def rows():
    return [{"path": "/x/big", "kind": "clone", "verdict": "DELETE", "bytes": 2_000_000_000},
            {"path": "/x/mid", "kind": "clone", "verdict": "DELETE", "bytes": 280_000_000},
            {"path": "/x/sess", "kind": "session", "verdict": "DELETE", "bytes": 10},
            {"path": "/x/t1", "kind": "clone", "verdict": "ARCHIVE", "bytes": 29_000},
            {"path": "/x/t2", "kind": "clone", "verdict": "ARCHIVE", "bytes": 26_000},
            {"path": "/x/young", "kind": "clone", "verdict": "YOUNG", "bytes": 1}]


def run(pressed, budget_rows):
    """apply_rows with a clock that advances 1 s per acted row and a budget of `budget_rows` seconds."""
    clock, order = [0.0], []
    real = s.act, s.time.time, s.apply_pressed

    def fake_act(r, ctx, failures):
        order.append(r["path"])
        clock[0] += 1.0
        return r["bytes"]
    s.act, s.time.time, s.apply_pressed = fake_act, (lambda: clock[0]), (lambda: pressed)
    try:
        rs = rows()
        freed, deferred = s.apply_rows(rs, None, budget_rows - 0.5, [], 0.0)
    finally:
        s.act, s.time.time, s.apply_pressed = real
    return order, deferred, [r["path"] for r in rs if r.get("deferred")]


order, deferred, waits = run(False, 2)
ok(order == ["/x/t2", "/x/t1"], "off pressure the two small clones go first (%s)" % order)
ok(deferred == 3 and waits == ["/x/big", "/x/mid", "/x/sess"], "and the big clones and the session wait (%s)" % waits)
order, _, _ = run(False, 10)
ok(order == ["/x/t2", "/x/t1", "/x/mid", "/x/big", "/x/sess"], "with time for all, sessions still come last (%s)" % order)
order, deferred, waits = run(True, 1)
ok(order == ["/x/big"] and "/x/t1" in waits, "under pressure the biggest clone goes first, as before (%s)" % order)
order, _, _ = run(True, 10)
ok(order[-1] == "/x/sess", "under pressure sessions are still last (%s)" % order)

real_free, real_tmp = s.free_gb, s.tmp_reading
try:
    s.free_gb, s.tmp_reading = (lambda path="/": s.PRESSURE_GB - 1), (lambda: None)
    ok(s.apply_pressed() is True, "free space under the pressure line reads as pressure")
    s.free_gb = lambda path="/": s.PRESSURE_GB + 50
    ok(s.apply_pressed() is False, "free space over the line with /tmp unread reads as no pressure")
    s.tmp_reading = lambda: {"free_gb": 0.1, "used_pct": 99.9}
    ok(s.apply_pressed() is True, "a /tmp past its lines reads as pressure")
finally:
    s.free_gb, s.tmp_reading = real_free, real_tmp

print("%d failed" % len(FAILS))
sys.exit(1 if FAILS else 0)
