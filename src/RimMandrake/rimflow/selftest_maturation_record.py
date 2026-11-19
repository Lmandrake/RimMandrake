#!/usr/bin/env python3
"""Offline selftest of maturation.py's stage record (spend, version rollover, the offline build's facts): one test per
promise on design/specs/2026-11-19-maturation-record/boundary.md, each named after it (boundary_check.py reads that).
Item RIMMANDRAKE_FIX_MATURATION_REVIEW_FINDINGS_SIX_PREDATE_SCOPE; each test watched failing on the base 7df09c59a2.

    python3 src/RimMandrake/rimflow/selftest_maturation_record.py                 every test; exit 0 PASS, 1 FAILED
    python3 src/RimMandrake/rimflow/selftest_maturation_record.py --only t_x ...  those alone
"""
import json
import os
import shutil
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation as M  # noqa: E402

TMP = tempfile.mkdtemp(prefix="selftest_maturation_record_")
FAILS = []
MOD = "RecordTestMod"


def check(ok, what, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, "" if ok or got is None else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def fresh(name, **rec):
    """-> a new root holding MOD with a stage record (0.1.0 at offline build unless rec says otherwise)."""
    root = os.path.join(TMP, name)
    base = {"schema": 1, "mod": MOD, "version": "0.1.0", "stage": "offline_build", "since": "2026-11-19T09:00:00-08:00",
            "cycles": {"visit": 0, "total": 0}, "pre_human_arrivals": 0, "moves": [], "spend": []}
    base.update(rec)
    M.write_text(root, MOD, M.RECORD, M.dump(base))
    return root


def t_spend_write_holds_the_mod_lock():
    """An add_spend started while another process holds the mod's lock (a move between its read and its write) waits
    for it, then writes: the move is not erased."""
    root = fresh("lock")
    lk = M._mod_lock(root, MOD)
    th = threading.Thread(target=M.add_spend, args=(root, MOD, "blind_challenge", 7), kwargs={"source": "run-locked"},
                          daemon=True)
    try:
        th.start()
        th.join(1.5)
        waited = th.is_alive() and (M.load(root, MOD).get("spend") or []) == []
        if waited:      # the move that lands while add_spend waits
            rec = M.load(root, MOD)
            rec["moves"].append({"from": "offline_build", "to": "blind_challenge", "by": "selftest"})
            rec["stage"] = "blind_challenge"
            M.write_text(root, MOD, M.RECORD, M.dump(rec))
    finally:
        lk.close()
    th.join(30)
    rec = M.load(root, MOD)
    check(waited, "add_spend waits while the mod's lock is held", waited)
    check(not th.is_alive() and [x.get("source") for x in rec.get("spend") or []] == ["run-locked"],
          "then it writes its row", rec.get("spend"))
    check(rec.get("stage") == "blind_challenge" and len(rec.get("moves") or []) == 1,
          "the move made while it waited is kept", (rec.get("stage"), rec.get("moves")))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    for t in (t_spend_write_holds_the_mod_lock,):
        if only is not None and t.__name__ not in only:
            continue
        print("== %s" % t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS[:8])))
        return 1
    print("PASS selftest_maturation_record")
    return 0


if __name__ == "__main__":
    sys.exit(main())
