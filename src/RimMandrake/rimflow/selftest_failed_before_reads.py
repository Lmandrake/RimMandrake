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
    """void_spend: a record that reads None counts no tokens and lists the unit UNMEASURED; a readable one counts its
    weighted_v2 tokens (a Fable 5.2 record whose CLI cost_usd is the Opus-rate half counts its tokens), a legacy
    record with only cost_usd counts it at 250,000 weighted tokens per list dollar."""
    s = {"voided": [{"unit": "u-blind", "book": "steward"}, {"unit": "u-read", "book": "steward"},
                    {"unit": "u-fable", "book": "steward"}]}
    recs = {"u-read": {"cost_usd": 1.5},
            "u-fable": {"cost_usd": 1.0, "tokens": 500000, "token_unit": "weighted_v2", "model": "fable"}}
    got = RV.void_spend(s, recs.get)
    check(got == (875000, ["u-blind"]), "the unreadable unit is UNMEASURED; v2 tokens count, never the CLI dollars",
          got)


def t_hand_run_the_books_now_own_is_folded():
    """_fold_tick_own: an open hand_run act whose unit the current books hold folds once; one no book holds stays."""
    root = tempfile.mkdtemp(prefix="fbr_reclass_")
    was = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    os.environ["RM_MATURATION_DISPATCH_DIR"] = root
    try:
        for u in ("own-1", "hand-2"):
            MH._append(MH.ACTS, MH._act("run-" + u, 1.0, "hand_run", "F", "launched by hand: " + u))
        st = {"mods": {"F": {"cleared": [{"at": 2, "released": {"fixers": {"X": {"unit": "own-1", "item": "X"}}}}]}}}
        MH._fold_tick_own(st, 10.0)
        MH._fold_tick_own(st, 20.0)
        folds = [r for r in MH._lines(MH.FOLDS)]
        check([r["id"] for r in folds] == ["run-own-1"], "only the run the books hold folds, once", folds)
    finally:
        if was is None:
            os.environ.pop("RM_MATURATION_DISPATCH_DIR", None)
        else:
            os.environ["RM_MATURATION_DISPATCH_DIR"] = was
        shutil.rmtree(root, ignore_errors=True)


def t_lane_launched_run_is_no_hand_run():
    """A run that the Workshop lane (list_dispatch) launched is a program's launch: collect records no hand run for it,
    and _fold_tick_own folds one already recorded, naming the lane. A run in no book stays an open hand act; a lane
    state that cannot be read is could-not-look: nothing folds."""
    import json
    T = MH.BASELINE_TS + 1e6      # after the census baseline, which folds every act before it
    root = tempfile.mkdtemp(prefix="fbr_lane_")
    saved = {k: os.environ.get(k) for k in ("RM_MATURATION_DISPATCH_DIR", "RM_LIST_DISPATCH_DIR")}
    os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(root, "state")
    os.environ["RM_LIST_DISPATCH_DIR"] = os.path.join(root, "lane")
    try:
        import maturation_dispatch as MD
        MD.sdir()
        os.makedirs(os.environ["RM_LIST_DISPATCH_DIR"])
        lane_path = os.path.join(os.environ["RM_LIST_DISPATCH_DIR"], "state.json")
        item = "RIMMANDRAKE_DRIVE_F_IN_GAME_VISIT_TWO"
        with open(lane_path, "w") as f:
            json.dump({"items": {item: {"attempts": [{"unit": "lane-live", "at": T + 1.0}],
                                        "cleared": [{"at": 2, "attempts": [{"unit": "lane-cleared"}]}]}}}, f)
        for u in ("lane-old", "lane-cleared", "nobody"):
            MH._append(MH.ACTS, MH._act("run-" + u, T + 1.0, "hand_run", "F", "launched by hand: " + u))
        with open(lane_path) as f:
            lane = json.load(f)
        lane["items"][item]["attempts"].append({"unit": "lane-old"})
        with open(lane_path, "w") as f:
            json.dump(lane, f)
        st = {"hands": {"since": T + 5.0, "last_tick": T + 1000.0, "fold_at": T + 1000.0}, "mods": {"F": {}}}
        facts = {"F": {"runs_seen": [{"unit": u, "item": item, "at": T + 100.0, "end": T + 200.0}
                                     for u in ("lane-live", "hand-new")]}}
        fx = {"events": lambda: [], "known": lambda: {item}, "record": lambda u: None}
        MH.observe(root, {"advancing": ["F"]}, st, facts, T + 1010.0, {"needs_conductor": []}, fx)
        ids = {a["id"] for a in MH.read_acts()}
        folds = MH.read_folds()
        check("run-lane-live" not in ids, "a lane attempt's run is recorded as no hand run", sorted(ids))
        check("run-hand-new" in ids and "run-hand-new" not in folds, "a run no book holds is recorded and stays open", sorted(folds))
        check({"run-lane-old", "run-lane-cleared"} <= set(folds)
              and all("list_dispatch" in folds[i]["why"] for i in ("run-lane-old", "run-lane-cleared")),
              "a recorded hand run the lane's books hold (live or cleared attempt) folds, naming the lane", folds)
        check("run-nobody" not in folds, "a recorded run no lane attempt and no tick book holds stays open", sorted(folds))
        # the lane state cannot be read: could not look, so nothing folds on its word
        with open(lane_path, "w") as f:
            f.write("{not json")
        MH._append(MH.ACTS, MH._act("run-lane-live", T + 1.0, "hand_run", "F", "launched by hand: lane-live"))
        MH._fold_tick_own(st, T + 1020.0, fx)
        check("run-lane-live" not in MH.read_folds(), "an unreadable lane state folds nothing", sorted(MH.read_folds()))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(root, ignore_errors=True)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    del FAILS[:]
    for t in (t_unreadable_concept_stage_holds_the_designer_lane, t_unparseable_stage_time_is_no_time,
              t_blind_ledger_on_road_back_is_named, t_unreadable_prior_verdict_is_no_baseline,
              t_unreadable_run_record_spend_is_unmeasured, t_hand_run_the_books_now_own_is_folded,
              t_lane_launched_run_is_no_hand_run):
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
