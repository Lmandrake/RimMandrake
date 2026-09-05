#!/usr/bin/env python3
"""Selftest for queue_staleness_review.py — a synthetic ledger, never the real one.

⚠️ EVERY TEMPORARY FILE IS UNDER THE REPO, NEVER `/tmp`. `/mnt/d` (9p/DrvFs) and
`/tmp` (tmpfs) are different filesystems with different atomicity — see
`rimflow/model.py`'s own docstring and `rimflow/selftest_render.py`, which this
fixture pattern is copied from (rebind `model.EVENTS`/`model.ITEMS`, never touch the
real ledger).

    python3 src/RimMandrake/Utils/selftest_queue_staleness_review.py
"""
import os
import shutil
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake"))
sys.path.insert(0, HERE)
from rimflow import model                                            # noqa: E402
import queue_staleness_review as qsr                                  # noqa: E402

PASS, FAIL = [], []
TMP = None
NOW = datetime(2026, 9, 5, tzinfo=timezone.utc)


def case(name, fn):
    try:
        fresh()
        fn()
        PASS.append(name)
        print("ok    %s" % name)
    except AssertionError as e:
        FAIL.append(name)
        print("FAIL  %s\n        %s" % (name, e))
    except Exception as e:
        FAIL.append(name)
        print("FAIL  %s\n        unexpected %s: %s" % (name, type(e).__name__, e))


def fresh():
    for d in ("ledger", "items"):
        shutil.rmtree(os.path.join(TMP, d), ignore_errors=True)
        os.makedirs(os.path.join(TMP, d), exist_ok=True)
    model.EVENTS = os.path.join(TMP, "ledger", "events.jsonl")
    model.ITEMS = os.path.join(TMP, "items")


_seq = [0]


def emit(ts, **kw):
    kw["ts"] = ts
    return model.append(kw)


def file_and_start(iid, ts_filed, ts_started, for_="FOUNDRY", needs=None):
    d = {"seat": "BENCH", "event": "file", "id": iid, "title": "t", "kind": "task",
         "for": for_}
    if needs:
        d["needs"] = needs
    emit(ts_filed, **d)
    emit(ts_filed, seat=for_, event="claim", id=iid)
    emit(ts_started, seat=for_, event="start", id=iid)


def world_and_events():
    events = model.read()
    return model.replay(events), events


# ---------------------------------------------------------------------------
def t_doing_item_idle_past_threshold_is_flagged_stale():
    file_and_start("A_ITEM_1", "2026-08-01T00:00:00Z", "2026-08-01T00:00:01Z")
    world, events = world_and_events()
    rows = qsr.collect(world, events, qsr.DEFAULT_BLOCKED_DAYS, qsr.DEFAULT_DOING_DAYS,
                       qsr.DEFAULT_MISTAG_MIN, now=NOW)
    row = next(r for r in rows if r["id"] == "A_ITEM_1")
    assert row["bucket"] == "doing", row
    assert row["stale"] is True, row
    assert row["days_idle"] > 30, row


def t_doing_item_recently_touched_is_not_stale():
    file_and_start("B_ITEM_1", "2026-08-01T00:00:00Z", "2026-09-04T23:00:00Z")
    world, events = world_and_events()
    rows = qsr.collect(world, events, qsr.DEFAULT_BLOCKED_DAYS, qsr.DEFAULT_DOING_DAYS,
                       qsr.DEFAULT_MISTAG_MIN, now=NOW)
    row = next(r for r in rows if r["id"] == "B_ITEM_1")
    assert row["stale"] is False, row


def t_blocked_item_uses_the_shorter_threshold():
    file_and_start("C_ITEM_1", "2026-09-01T00:00:00Z", "2026-09-01T00:00:01Z")
    emit("2026-09-01T00:00:02Z", seat="FOUNDRY", event="block", id="C_ITEM_1",
        reason="stuck on a decision")
    world, events = world_and_events()
    rows = qsr.collect(world, events, qsr.DEFAULT_BLOCKED_DAYS, qsr.DEFAULT_DOING_DAYS,
                       qsr.DEFAULT_MISTAG_MIN, now=NOW)
    row = next(r for r in rows if r["id"] == "C_ITEM_1")
    # 4 days idle: past the 3-day blocked threshold, well under the 7-day doing one.
    assert row["bucket"] == "blocked", row
    assert row["stale"] is True, row
    assert row["blocked_reason"] == "stuck on a decision", row


def t_owner_named_by_a_retired_seat_is_mistagged():
    # DECIDE is in model.SEATS (so old ledger lines still replay) but is a retired
    # seat per model.py's own comment — nobody occupies it. A legacy item claimed
    # and started by DECIDE back when that seat operated is exactly this shape:
    # still `doing`, owner never reassigned since the seat retired, orphaned today
    # regardless of how idle it is.
    file_and_start("D_ITEM_1", "2026-09-04T00:00:00Z", "2026-09-04T00:00:01Z",
                   for_="DECIDE")
    world, events = world_and_events()
    rows = qsr.collect(world, events, qsr.DEFAULT_BLOCKED_DAYS, qsr.DEFAULT_DOING_DAYS,
                       qsr.DEFAULT_MISTAG_MIN, now=NOW)
    row = next(r for r in rows if r["id"] == "D_ITEM_1")
    assert any("RETIRED seat" in m for m in row["mistags"]), row


def t_needs_bridge_flagged_stale_when_bridge_freed_repeatedly_since():
    file_and_start("E_ITEM_1", "2026-08-01T00:00:00Z", "2026-08-01T00:00:01Z",
                   needs="bridge")
    for i in range(3):
        emit("2026-08-1%dT00:00:00Z" % (i + 1), seat="FOUNDRY", event="bridge",
            state="taken")
        emit("2026-08-1%dT01:00:00Z" % (i + 1), seat="FOUNDRY", event="bridge",
            state="released")
    world, events = world_and_events()
    rows = qsr.collect(world, events, qsr.DEFAULT_BLOCKED_DAYS, qsr.DEFAULT_DOING_DAYS,
                       qsr.DEFAULT_MISTAG_MIN, now=NOW)
    row = next(r for r in rows if r["id"] == "E_ITEM_1")
    assert any("bridge went free" in m for m in row["mistags"]), row


def t_needs_bridge_not_flagged_when_bridge_never_freed_since():
    file_and_start("F_ITEM_1", "2026-08-01T00:00:00Z", "2026-08-01T00:00:01Z",
                   needs="bridge")
    world, events = world_and_events()
    rows = qsr.collect(world, events, qsr.DEFAULT_BLOCKED_DAYS, qsr.DEFAULT_DOING_DAYS,
                       qsr.DEFAULT_MISTAG_MIN, now=NOW)
    row = next(r for r in rows if r["id"] == "F_ITEM_1")
    assert row["mistags"] == [], row


def t_dropped_item_that_was_once_blocked_is_excluded():
    # Regression, found live 2026-09-05: item.blocked is a persistent flag a
    # later drop does not clear. Three real ledger items (REFMATCH_THRESHOLDS_
    # CALIBRATE_1, B55, FINAL_WORLD_PREP_1) were dropped MONTHS ago but still
    # read item.blocked==True, and an earlier version of collect() flagged all
    # three as needing attention today. item.open (state in proposed/ready/doing)
    # is what actually distinguishes "still blocked" from "was blocked, then closed".
    file_and_start("I_ITEM_1", "2026-08-01T00:00:00Z", "2026-08-01T00:00:01Z")
    emit("2026-08-01T00:00:02Z", seat="FOUNDRY", event="block", id="I_ITEM_1",
        reason="stuck")
    emit("2026-08-02T00:00:00Z", seat="FOUNDRY", event="drop", id="I_ITEM_1",
        reason="premise no longer applies")
    world, events = world_and_events()
    rows = qsr.collect(world, events, qsr.DEFAULT_BLOCKED_DAYS, qsr.DEFAULT_DOING_DAYS,
                       qsr.DEFAULT_MISTAG_MIN, now=NOW)
    assert not any(r["id"] == "I_ITEM_1" for r in rows), rows


def t_proposed_and_ready_items_are_excluded():
    emit("2026-08-01T00:00:00Z", seat="BENCH", event="file", id="G_ITEM_1", title="t",
        kind="task", **{"for": "FOUNDRY"})
    world, events = world_and_events()
    rows = qsr.collect(world, events, qsr.DEFAULT_BLOCKED_DAYS, qsr.DEFAULT_DOING_DAYS,
                       qsr.DEFAULT_MISTAG_MIN, now=NOW)
    assert not any(r["id"] == "G_ITEM_1" for r in rows), rows


def t_render_report_is_terse_and_has_no_traceback():
    file_and_start("H_ITEM_1", "2026-08-01T00:00:00Z", "2026-08-01T00:00:01Z")
    world, events = world_and_events()
    rows = qsr.collect(world, events, qsr.DEFAULT_BLOCKED_DAYS, qsr.DEFAULT_DOING_DAYS,
                       qsr.DEFAULT_MISTAG_MIN, now=NOW)
    text = qsr.render_report(rows, qsr.DEFAULT_BLOCKED_DAYS, qsr.DEFAULT_DOING_DAYS,
                             qsr.DEFAULT_MISTAG_MIN, "2026-09-05T00:00:00Z")
    assert "H_ITEM_1" in text
    assert "Traceback" not in text


CASES = [(k[2:], v) for k, v in sorted(globals().items()) if k.startswith("t_")]

if __name__ == "__main__":
    TMP = os.path.join(model.STATE, "derived", ".selftest_qsr")
    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP, exist_ok=True)
    real = (model.EVENTS, model.ITEMS)
    try:
        for name, fn in CASES:
            case(name, fn)
    finally:
        model.EVENTS, model.ITEMS = real
        shutil.rmtree(TMP, ignore_errors=True)
    print("\n%d/%d passed" % (len(PASS), len(PASS) + len(FAIL)))
    sys.exit(1 if FAIL else 0)
