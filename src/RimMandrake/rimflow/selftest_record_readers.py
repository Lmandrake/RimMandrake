#!/usr/bin/env python3
"""selftest_record_readers.py - each reader of the shared run-record folder names what a run record is.
Item RIMMANDRAKE_SCOPE_COULD_NOT_LOOK_ONE_STRAY_FILE_HELD_ELEVEN_TICKETS; page
design/specs/2026-11-24-record-readers/boundary.md (each t_ function is one promise of it, by name). Offline: a
throwaway dispatcher state dir holding one real record beside other writers' files. Red on f5ffa47176 (readers that
took every *.json but <unit>.out.json, or <unit>.alive.json too, for a record).
"""
import json
import os
import sys
import tempfile
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
STATE = tempfile.mkdtemp(prefix="record_readers_")
os.environ["RM_DISPATCHER_STATE"] = STATE
FAILS = []
NOW = 1_800_000_000.0
REAL = "rm-detached-bench-real-1799999000"
GHOST = "rm-detached-bench-ghost-1799999500"
SID = "sess-1"


def chk(cond_fn, what):
    try:
        cond = cond_fn()
    except Exception as e:  # noqa: BLE001
        cond, what = False, "%s (raised %s: %s)" % (what, type(e).__name__, str(e)[:300])
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def _put(name, obj):
    import detached_helper as DH
    with open(os.path.join(DH.runs_dir(), name), "w", encoding="utf-8") as f:
        f.write(obj if isinstance(obj, str) else json.dumps(obj))


def plant():
    """One real finished record, and other writers' files beside it: the run_alive look, an out file, a log, and a
    sign-of-life file of a new kind that copies a run's fields (unit, item, status, launch time, session, clone)."""
    import detached_helper as DH
    clone = tempfile.mkdtemp(prefix="rr_clone_")
    DH.write_record({"unit": REAL, "item": "ITEM_REAL", "status": "finished", "at": NOW - 600, "ended": NOW - 7200,
                     "next_act_owner": "list_dispatch", "clone": tempfile.mkdtemp(prefix="rr_real_"),
                     "env": {"RM_CONTROL_MOD": "M", "RM_CONTROL_STAGE": "S"}})
    _put(REAL + ".alive.json", {"act": "renewed", "line": "ALIVE: ok"})
    _put(REAL + ".out.json", {"type": "result", "session_id": SID})
    _put("left_open_continue.jsonl", '{"at": 1}\n')
    ghost = {"unit": GHOST, "item": "ITEM_GHOST", "status": "running", "at": NOW - 300, "ended": NOW - 7200,
             "session": SID, "session_tokens": 999, "next_act_owner": "list_dispatch", "clone": clone,
             "env": {"RM_CONTROL_MOD": "M", "RM_CONTROL_STAGE": "S"}}
    _put(GHOST + ".heartbeat.json", ghost)
    _put("notes.json", {"kind": "a note file of another tool"})
    return ghost


def t_a_record_is_named_by_its_unit():
    import detached_helper as DH
    chk(lambda: DH.record_unit(REAL + ".json") == REAL and DH.record_unit("/a/b/%s.json" % REAL) == REAL,
        "<unit>.json names the record of <unit>")
    chk(lambda: not any(DH.record_unit(REAL + x) for x in (".alive.json", ".out.json", ".heartbeat.json", ".err",
                                                           ".json.return", ".finish.log")),
        "a file with a dot in its stem is another writer's")
    chk(lambda: DH.is_record({"unit": REAL}, REAL) and not DH.is_record({"unit": GHOST}, REAL)
        and not DH.is_record({"kind": "x"}, "notes") and not DH.is_record(None, REAL),
        "a parsed file is a record only when it names its own unit")


def t_all_records_reads_only_records():
    import detached_helper as DH
    unread = []
    got = [r["unit"] for r in DH.all_records(unreadable=unread.append)]
    chk(lambda: got == [REAL] and unread == [],
        "all_records yields the one record and calls no other writer's file unreadable (got %s, unreadable %s)"
        % (got, unread))
    _put("rm-detached-bench-torn-1799999900.json", "{")
    unread = []
    got = [r["unit"] for r in DH.all_records(unreadable=unread.append)]
    chk(lambda: got == [REAL] and unread == ["rm-detached-bench-torn-1799999900.json"],
        "a record file that does not parse is unreadable, named (%s)" % unread)
    os.remove(os.path.join(DH.runs_dir(), "rm-detached-bench-torn-1799999900.json"))
    notdir = os.path.join(STATE, "not_a_folder")
    open(notdir, "w").close()
    with patch.object(DH, "runs_dir", lambda root=None: notdir):
        try:
            list(DH.all_records())
            raised = False
        except OSError:
            raised = True
    chk(lambda: raised, "a folder that cannot be listed raises: could not look is never no records")


def t_every_reader_of_the_folder_skips_other_writers_files():
    import detached_helper as DH
    import stop_resume as SR
    import maturation as M
    import fleet_mods as FM
    got = [r["unit"] for r in SR.recent_records(None, NOW)]
    chk(lambda: GHOST not in got, "stop_resume.recent_records takes no sign-of-life file for a run (%s)" % got)
    twins, why = M.live_twins("M", "S", "ITEM_GHOST", status=lambda r: r.get("status"))
    chk(lambda: twins == [], "maturation.live_twins sees no twin in a sign-of-life file (%s, %s)" % (twins, why))
    rows = FM.detached_done(24, now=NOW, root=DH.runs_dir(), unit_state=lambda u: "inactive",
                            item_state=lambda i: "open", commits=lambda i, s: 0)
    chk(lambda: [r["item"] for r in rows] == ["ITEM_REAL"], "fleet_mods.detached_done reads only records (%s)" % rows)
    with patch("role_launch.read_result", return_value=None):
        tot = DH.earlier_session_totals({"unit": "rm-detached-bench-new-1800000000", "at": NOW}, SID)
    chk(lambda: tot == (None, None), "earlier_session_totals counts no sign-of-life file's tokens (%s)" % (tot,))
    seen = []
    ghost_rec = json.load(open(os.path.join(DH.runs_dir(), GHOST + ".heartbeat.json")))
    ghost_rec["status"] = "finished"
    _put(GHOST + ".heartbeat.json", ghost_rec)
    with patch.object(DH, "owns_clone", lambda rec: True), \
            patch.object(DH, "return_clone", lambda u, **k: seen.append(u) or (0, "returned %s" % u)):
        DH.return_all(now=NOW, grace_s=0)
    chk(lambda: seen == [REAL], "return_all returns the record's clone and none named by a sign-of-life file (%s)" % seen)


def main():
    plant()
    for t in (t_a_record_is_named_by_its_unit, t_all_records_reads_only_records,
              t_every_reader_of_the_folder_skips_other_writers_files):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            chk(lambda: False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    print("selftest_record_readers: %s (%d fail)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
