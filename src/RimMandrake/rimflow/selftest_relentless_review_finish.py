#!/usr/bin/env python3
"""selftest_relentless_review_finish.py — relentless.py defects from its full-file review
(RELENTLESS_REVIEW_FINISH_TOO_BIG_TO_SKIM). Each check fails on the code before the fix.

1. lease(): a full pool that has no room for the top item's NEW clone does not stop an item further down that already
   has its own clone: that one starts (its kept commits are what would free room), and the pool wait is said once.
2. staffing(): content stopped by the owner's token pause (only_system_and_live) is not ready work, so the pause reads
   as no under-staffing and raises no staffing or jam alarm.

Runs on selftest_relentless's FakeWorld; no ledger, clone or unit is touched.

    python3 src/RimMandrake/rimflow/selftest_relentless_review_finish.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import selftest_relentless as SR    # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def t_pool_full_lets_a_cloned_item_run():
    x = SR.staffed(n=2)
    x.w.pool = {"/c/L%d" % i: {"busy": True} for i in range(10)}
    x.tick()
    ok(not x.w.launches and {x.st("I0")["status"], x.st("I1")["status"]} == {"queued"},
       "fixture: both items queued, nothing starts in a full pool of live clones")
    # the lower item gets its own clone back (kept commits), in place of a live one: the pool stays at its cap
    del x.w.pool["/c/L0"]
    mine = x.w.clone_path("I1", len(x.st("I1")["quarantined"]))
    x.w.pool[mine] = {"kept": True}
    st = x.st("I1")
    st["clone"] = mine          # a put-down run's clone, kept for its commits
    x.s.save(st)
    acts = x.tick()
    started = [l[0] for l in x.w.launches]
    ok(started == ["I1"], "the item that has its clone starts though the top one has no room: %s" % started)
    waits = [a for a in acts or [] if isinstance(a, dict) and a.get("do") == "wait"
             and str(a.get("why", "")).startswith(("pool full", "pool at"))]
    ok(len(waits) <= 1, "the pool wait is said at most once a tick: %s" % waits)
    ok(x.st("I0")["status"] == "queued", "the top item keeps its place in line")
    x.done()


def t_owner_pause_is_not_under_staffing():
    x = SR.staffed(n=3)
    x.r["only_system_and_live"] = True      # the owner's token pause; FakeWorld has no system items
    x.tick()
    r = SR.reading(x)
    ok(not x.w.launches, "fixture: the pause starts no content")
    ok(r["ready"] == 0 and not r["under"], "content stopped by the pause is not ready, so not under-staffed: ready %s "
       "under %s why %s" % (r["ready"], r["under"], r.get("why")))
    x.tick(), x.tick()
    ok(not x.w.alarms and not x.w.jams, "no staffing or jam alarm for a pause he chose: %s %s" % (x.w.alarms, x.w.jams))
    x.done()


if __name__ == "__main__":
    try:
        t_pool_full_lets_a_cloned_item_run()
        t_owner_pause_is_not_under_staffing()
    except Exception as e:      # noqa: BLE001  a crash is a FAIL with its reason
        import traceback
        traceback.print_exc()
        FAILS.append("crashed: %s" % e)
    print("RESULT: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    sys.exit(1 if FAILS else 0)
