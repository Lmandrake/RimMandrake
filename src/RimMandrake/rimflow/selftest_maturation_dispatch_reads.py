#!/usr/bin/env python3
"""Offline selftest of maturation_dispatch.py's reads: one test per promise on
design/specs/2026-11-19-maturation-dispatch-reads/boundary.md, each named after it (boundary_check.py reads that).

    python3 src/RimMandrake/rimflow/selftest_maturation_dispatch_reads.py                 every test; exit 0 PASS, 1 FAILED
    python3 src/RimMandrake/rimflow/selftest_maturation_dispatch_reads.py --only t_x ...  those alone
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation_dispatch as MD  # noqa: E402

TMP = tempfile.mkdtemp(prefix="selftest_maturation_dispatch_reads_")
FAILS = []


def check(ok, what, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, "" if ok or got is None else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def write(rel, text):
    p = os.path.join(TMP, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def raises(fn, *a):
    try:
        fn(*a)
    except RuntimeError:
        return True
    return False


def t_dispatch_state_absent_is_empty_unreadable_raises():
    """read_state: {} for an absent file; RuntimeError for one that does not parse or is not an object."""
    check(MD.read_state(os.path.join(TMP, "gone.json")) == {}, "an absent state.json reads {}")
    check(raises(MD.read_state, write("bad.json", "{nope")), "a state.json that does not parse raises")
    check(raises(MD.read_state, write("list.json", "[1]")), "a state.json that is not an object raises")
    check(MD.read_state(write("good.json", '{"mods": {}}')) == {"mods": {}}, "a good state.json reads as written")


def t_unparseable_time_is_no_time():
    """_ts: None for a time that does not parse, the epoch for an ISO one; arrivals records no arrival from it."""
    check(MD._ts("UNMEASURED") is None, "UNMEASURED is no time", MD._ts("UNMEASURED"))
    check(MD._ts("2026-11-16T13:37:29-08:00") == 1794865049.0, "an ISO time is its epoch",
          MD._ts("2026-11-16T13:37:29-08:00"))
    got = MD.arrivals({"stage": "designer", "since": "UNMEASURED", "moves": [{"from": "intake", "to": "designer",
                                                                              "at": "UNMEASURED"}]})
    check(got == {}, "an unparseable since and move time give no arrival", got)


def t_unreadable_run_record_ends_nothing():
    """end_ledger_runs: a run record that cannot be read, for a unit the facts do not list as ended, ends nothing."""
    st = {"mods": {"PlantedMod": {"ledger_runs": [{"unit": "rm-planted-1", "run": "r1"}]}}}
    got = MD.end_ledger_runs(TMP, st, {"PlantedMod": {"ended_runs": []}}, 1.0, fx={"record": lambda u: None})
    run = st["mods"]["PlantedMod"]["ledger_runs"][0]
    check(got == {} and not run.get("ended"), "no run.end, the run stays open", (got, run))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    for t in (t_dispatch_state_absent_is_empty_unreadable_raises, t_unparseable_time_is_no_time,
              t_unreadable_run_record_ends_nothing):
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
    print("PASS selftest_maturation_dispatch_reads")
    return 0


if __name__ == "__main__":
    sys.exit(main())
