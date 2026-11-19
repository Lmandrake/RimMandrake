#!/usr/bin/env python3
"""Offline selftest of the reads in maturation_autonomy, maturation_hands, coverage_judge and run_void: one test per
promise on design/specs/2026-11-19-failed-before-reads/boundary.md, each named after it (boundary_check.py reads that).

    python3 src/RimMandrake/rimflow/selftest_failed_before_reads.py                 every test; exit 0 PASS, 1 FAILED
    python3 src/RimMandrake/rimflow/selftest_failed_before_reads.py --only t_x ...  those alone
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import coverage_judge as CJ  # noqa: E402
import maturation_autonomy as AUT  # noqa: E402
import maturation_hands as MH  # noqa: E402
import run_void as RV  # noqa: E402

FAILS = []


def check(ok, what, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", what, "" if ok or got is None else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(what)


def t_unreadable_concept_stage_holds_the_designer_lane():
    """_designer_lane(dst=None): decision designer_unreadable, why names stage.json."""
    row = {"mod": "Abyss"}
    AUT._designer_lane(row, "Abyss", "0.1.0", None, None)
    check(row.get("decision") == "designer_unreadable", "no stage reads designer_unreadable", row)
    check("stage.json" in str(row.get("why")), "the why names stage.json", row.get("why"))
    check(set(row) == {"mod", "decision", "why"}, "nothing else is set on the row", sorted(row))


def t_unparseable_stage_time_is_no_time():
    """_iso_ts and parse_time: the epoch for an ISO time, None for one that does not parse; never 0."""
    for f in (AUT._iso_ts, RV.parse_time):
        check(f("2026-11-19T10:00:00Z") == 1795082400, "%s: an ISO time is its epoch" % f.__name__,
              f("2026-11-19T10:00:00Z"))
        for bad in ("UNMEASURED", "", None):
            check(f(bad) is None, "%s: %r is no time" % (f.__name__, bad), f(bad))


def t_blind_ledger_on_road_back_is_named():
    """_road_back_items with a ledger read that raises: None, and the cause kept in h."""
    def blind(ids):
        raise OSError("the ledger is blind")
    h = {}
    got = MH._road_back_items("/nonexistent", {"road_back": {"caused_by": "RIMMANDRAKE_X"}}, {"caused_by": blind}, h)
    check(got is None, "a blind ledger is None, not an empty set", got)
    check("the ledger is blind" in str(h.get("road_back_error")), "the cause is kept", h)
    got = MH._road_back_items("/nonexistent", {"road_back": {"caused_by": "RIMMANDRAKE_X"}},
                              {"caused_by": lambda ids: []}, {})
    check(got == set(), "a ledger that answers none is the empty set", got)


def t_unreadable_prior_verdict_is_no_baseline():
    """prior_verdict on a verdict file that does not parse: None, no raise."""
    d = tempfile.mkdtemp()
    try:
        with open(os.path.join(d, CJ.VERDICT_FILE), "w", encoding="utf-8") as f:
            f.write("{broken")
        try:
            got = CJ.prior_verdict(d)
        except Exception as e:      # noqa: BLE001
            got = "raised %s" % type(e).__name__
        check(got is None, "an unparseable verdict is no baseline", got)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_unreadable_run_record_spend_is_unmeasured():
    """void_spend: a record that reads None counts no dollars and lists the unit UNMEASURED; a readable one counts."""
    s = {"voided": [{"unit": "u-blind", "book": "steward"}, {"unit": "u-read", "book": "steward"}]}
    got = RV.void_spend(s, lambda u: None if u == "u-blind" else {"cost_usd": 1.5})
    check(got == (1.5, ["u-blind"]), "the unreadable unit is UNMEASURED, the readable one counts", got)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    del FAILS[:]
    for t in (t_unreadable_concept_stage_holds_the_designer_lane, t_unparseable_stage_time_is_no_time,
              t_blind_ledger_on_road_back_is_named, t_unreadable_prior_verdict_is_no_baseline,
              t_unreadable_run_record_spend_is_unmeasured):
        if only is not None and t.__name__ not in only:
            continue
        print("== %s" % t.__name__)
        try:
            t()
        except Exception as e:      # noqa: BLE001
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS[:8])))
        return 1
    print("PASS selftest_failed_before_reads")
    return 0


if __name__ == "__main__":
    sys.exit(main())
