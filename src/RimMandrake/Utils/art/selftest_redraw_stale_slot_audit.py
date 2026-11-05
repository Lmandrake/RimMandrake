#!/usr/bin/env python3
"""selftest_redraw_stale_slot_audit.py — redraw_stale_slot_audit.py classifies redraw/accept slots keyed by a lane
today's sheet no longer has (REDRAW_STALE_SLOT_KEY_AUDIT_DUPES). Pure fixtures: no git, no artpipe, no disk.

  1 a redraw slot keyed by a renamed lane, jobs under the stale key AND under today's lane: DUPLICATE
  2 jobs only under the stale key: MISROUTED
  3 a stale redraw slot with no job: WOULD_FILE; an asks.more on a stale slot likewise
  4 an accept on a stale key while a job redraws today's lane: ACCEPT_OVERRIDDEN; with none: ACCEPT_STALE
  5 a key that IS a lane today, and a row with no lane data today: no finding
  6 the ask id matches enact's step 3b hashing (det_id("ask", sheet, row, json(ask)) of the same dict)
  7 an unprovable sheet (ruled row None): finding kept, resolved None with a reason
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import redraw_stale_slot_audit as A  # noqa: E402
import artledger as L  # noqa: E402

OLD, NEW = "Things/Pawn/Animal/RM_Old/RM_Old", "Things/Pawn/Animal/RM_New/RM_New"
SHEET, ROW = "testsheet", "RM_Beast"
COLS = {"A": {"south": "aa11"}, "B": {"south": "bb22"}}
RULED = {"res": OLD, "graphic_of": {"A": OLD, "B": OLD}, "columns": COLS}
CUR = {"res": NEW, "graphic_of": {"A": NEW, "B": NEW}, "columns": COLS}
FAILS = []


def check(name, cond, detail=""):
    if not cond:
        FAILS.append(f"{name}: {detail}")
    print(("ok   " if cond else "FAIL ") + name + (f" — {detail}" if detail and not cond else ""))


def row_v(slots=None, asks=None):
    v = {"at": "2026-10-20T00:00:00Z", "decidedAt": "2026-10-20T00:00:00Z", "decision": "", "slots": slots or {}}
    if asks:
        v["asks"] = asks
    return v


def job_for(v, kind="slot", state="pending", slot=OLD):
    w = [x for x in A.ask_entries(v, CUR["res"]) if x["kind"] == kind][0]
    return {"id": f"enact_{A.ask_id(SHEET, ROW, w)}_rm_beast_v1", "target_def": ROW, "slot": slot, "_state": state}


def classes(fs):
    return sorted(f["class"] for f in fs)


v = row_v({OLD: {"state": "redraw"}})
stale_job = job_for(v)
twin = {"id": "enact_deadbeef_rm_beast_v1", "target_def": ROW, "slot": NEW, "_state": "done"}
fs = A.audit_row(SHEET, ROW, v, CUR, RULED, [stale_job, twin])
check("1 DUPLICATE", classes(fs) == ["DUPLICATE"] and fs[0]["resolved"] == NEW and fs[0]["twin_jobs"], str(fs))

fs = A.audit_row(SHEET, ROW, v, CUR, RULED, [stale_job])
check("2 MISROUTED", classes(fs) == ["MISROUTED"] and fs[0]["stale_jobs"], str(fs))

fs = A.audit_row(SHEET, ROW, v, CUR, RULED, [])
check("3 WOULD_FILE slot", classes(fs) == ["WOULD_FILE"], str(fs))
vm = row_v(asks={"more": [{"slot": OLD, "n": 2, "how": "bigger"}]})
fs = A.audit_row(SHEET, ROW, vm, CUR, RULED, [])
check("3 WOULD_FILE more", classes(fs) == ["WOULD_FILE"] and fs[0]["kind"] == "more", str(fs))
fs = A.audit_row(SHEET, ROW, vm, CUR, RULED, [job_for(vm, "more")])
check("3 more filed -> MISROUTED", classes(fs) == ["MISROUTED"], str(fs))

va = row_v({OLD: {"state": "accept"}})
fs = A.audit_row(SHEET, ROW, va, CUR, RULED, [twin])
check("4 ACCEPT_OVERRIDDEN", classes(fs) == ["ACCEPT_OVERRIDDEN"], str(fs))
fs = A.audit_row(SHEET, ROW, va, CUR, RULED, [])
check("4 ACCEPT_STALE", classes(fs) == ["ACCEPT_STALE"], str(fs))

fs = A.audit_row(SHEET, ROW, row_v({NEW: {"state": "redraw"}, OLD + "x": {"state": "pick", "pick": "A"}}), CUR,
                 RULED, [twin])
check("5 current lane / pick slot: nothing", fs == [], str(fs))
fs = A.audit_row(SHEET, ROW, v, {"columns": COLS}, RULED, [stale_job])
check("5 no lane data today: nothing", fs == [], str(fs))

w = {"kind": "slot", "slot": OLD, "n": 1, "base": None, "how": ""}
check("6 ask id = enact hashing", A.ask_id(SHEET, ROW, w) == L.det_id("ask", SHEET, ROW, json.dumps(w, sort_keys=True))[:8]
      and A.ask_entries(v, CUR["res"]) == [w], str(A.ask_entries(v, CUR["res"])))

fs = A.audit_row(SHEET, ROW, v, CUR, None, [stale_job])
check("7 unprovable sheet", classes(fs) == ["MISROUTED"] and fs[0]["resolved"] is None and fs[0]["why"], str(fs))

# a primary-slot redraw on a `redo` row is the row's redo (enact step 3a), not a slot job
vr = row_v({NEW: {"state": "redraw"}})
vr["decision"] = "redo"
check("8 primary redo excluded", A.ask_entries(vr, NEW) == [], str(A.ask_entries(vr, NEW)))

print("PASS" if not FAILS else f"FAIL ({len(FAILS)})")
sys.exit(1 if FAILS else 0)
