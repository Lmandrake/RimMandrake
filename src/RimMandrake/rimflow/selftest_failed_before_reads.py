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


def _hands_site(prefix, moves, since):
    """A temp state dir and a root with one mod K whose stage_record holds `moves`. -> (root, saved env, st)."""
    import json
    root = tempfile.mkdtemp(prefix=prefix)
    saved = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(root, "state")
    import maturation_dispatch as MD
    MD.sdir()
    os.makedirs(os.path.join(root, "design", "concepts", "K", "version"))
    with open(os.path.join(root, "design", "concepts", "K", "version", "stage_record.json"), "w") as f:
        json.dump({"moves": moves}, f)
    return root, saved, {"hands": {"since": since, "last_tick": since + 10, "fold_at": since + 10}, "mods": {"K": {}}}


def _hands_done(root, saved):
    if saved is None:
        os.environ.pop("RM_MATURATION_DISPATCH_DIR", None)
    else:
        os.environ["RM_MATURATION_DISPATCH_DIR"] = saved
    shutil.rmtree(root, ignore_errors=True)


def t_stage_move_time_reads_its_offset():
    """A stage move's `at` is local time with its offset (maturation.py writes 2026-11-26T09:35:38-08:00): the act's
    time is that instant in UTC (17:35:38Z), so `list` prints 17:35:38Z and the 24 h overdue alarm counts from the move,
    not 8 h before it. The act id keeps the reading it had before the fix (move-K-1795685738), so an act recorded and
    folded then is not recorded a second time. RIMMANDRAKE_FIX_HAND_ACT_CLOCK_LOCAL_TIME_READ_AS_UTC."""
    import contextlib
    import io
    true = 1795714538.0         # 2026-11-26T17:35:38Z = 09:35:38 PST
    old_id = "move-K-1795685738"
    root, saved, st = _hands_site("fbr_clock_", [
        {"from": "his_walk", "to": "in_game", "at": "2026-11-26T09:35:38-08:00", "by": "CONDUCTOR", "why": "tick stuck"},
        {"from": "in_game", "to": "pre_human", "at": "2026-11-26T05:00:00-08:00", "by": "CONDUCTOR", "why": "by hand"}],
        true - 86400)
    try:
        # the 05:00 PST move was recorded before the fix, read as 05:00Z, and folded then
        MH._append(MH.ACTS, MH._act("move-K-1795669200", 1795669200.0, "hand_move", "K", "moved in_game -> pre_human")
                   | {"recorded": true})
        MH._append(MH.FOLDS, {"id": "move-K-1795669200", "at": true, "item": "RIMMANDRAKE_X_Y_Z", "by": "hand"})
        rd = {"needs_conductor": []}
        now = true + 20 * 3600      # 20 h after the move: not overdue; read 8 h early it would be 28 h, overdue
        MH.observe(root, {"advancing": ["K"]}, st, {"K": {"runs_seen": []}}, now, rd,
                   {"events": lambda: [], "known": lambda: set(), "record": lambda u: None, "quiet_gap": True})
        acts = {a["id"]: a for a in MH.read_acts()}
        check(old_id in acts, "the act id keeps the reading it had before the fix", sorted(acts))
        check(old_id in acts and acts[old_id]["at"] == true and MH.iso(acts[old_id]["at"]) == "2026-11-26T17:35:38Z",
              "the act's time is the move's instant in UTC (17:35:38Z)", acts.get(old_id))
        check(rd["hand_acts"]["open"] == 1 and rd["hand_acts"]["overdue"] == 0,
              "20 h after the move the open act is not overdue", rd["hand_acts"])
        check(sorted(acts) == sorted([old_id, "move-K-1795669200"]),
              "the move recorded before the fix is not recorded a second time", sorted(acts))
        check("move-K-1795669200" in MH.read_folds(), "the move recorded before the fix stays folded", MH.read_folds())
        check(acts.get("move-K-1795669200", {}).get("at") == 1795669200.0 + 8 * 3600,
              "the move recorded before the fix lists at its UTC instant (13:00:00Z)", acts.get("move-K-1795669200"))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            MH.main(["list", "--all"])
        check("2026-11-26T17:35:38Z" in out.getvalue() and "2026-11-26T09:35:38Z" not in out.getvalue(),
              "`list` prints 17:35:38Z, never 09:35:38Z", out.getvalue()[-400:])
        check(MH.ts("2026-11-26T09:35:38Z") == 1795685738.0 and MH.ts("2026-11-26T09:35:38") == 1795685738.0
              and MH.ts("2026-11-26T09:35:38.250000+00:00") == 1795685738.25 and MH.ts("2026-11-26T09:35:38 PST") is None,
              "ts: Z and no offset are UTC, a fraction is kept, an unknown tail is no time",
              [MH.ts(x) for x in ("2026-11-26T09:35:38Z", "2026-11-26T09:35:38", "2026-11-26T09:35:38.250000+00:00",
                                   "2026-11-26T09:35:38 PST")])
    finally:
        _hands_done(root, saved)


def t_pass_on_his_recorded_words_folds():
    """A move to passed, or off his_walk, that carries his words (`confirmed.owner_said`, the `--owner-said` event that
    maturation.py checks) is his act, recorded by the Conductor: it folds as a move by OWNER does, whatever the why
    says. The same move with no owner_said stays an open hand act."""
    t = MH.BASELINE_TS + 1e6
    root, saved, st = _hands_site("fbr_words_", [
        {"from": "his_walk", "to": "passed", "at": MH.iso(t + 100), "by": "CONDUCTOR", "why": "the walk is recorded",
         "confirmed": {"owner_said": "OWNER:1795714498917797906"}},
        {"from": "his_walk", "to": "passed", "at": MH.iso(t + 200), "by": "CONDUCTOR", "why": "the walk is recorded",
         "confirmed": {}}], t)
    try:
        MH.observe(root, {"advancing": ["K"]}, st, {"K": {"runs_seen": []}}, t + 3600, {"needs_conductor": []},
                   {"events": lambda: [], "known": lambda: set(), "record": lambda u: None, "quiet_gap": True})
        folds = MH.read_folds()
        a1, a2 = "move-K-%d" % (t + 100), "move-K-%d" % (t + 200)
        ids = {a["id"] for a in MH.read_acts()}
        check({a1, a2} <= ids, "both moves are recorded as hand moves", sorted(ids))
        check(a1 in folds and "five acts" in folds[a1].get("why", ""), "the pass that carries his words folds, naming why",
              folds.get(a1))
        check(a2 not in folds, "the pass with no words of his stays open", sorted(folds))
    finally:
        _hands_done(root, saved)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    del FAILS[:]
    for t in (t_unreadable_concept_stage_holds_the_designer_lane, t_unparseable_stage_time_is_no_time,
              t_blind_ledger_on_road_back_is_named, t_unreadable_prior_verdict_is_no_baseline,
              t_unreadable_run_record_spend_is_unmeasured, t_hand_run_the_books_now_own_is_folded,
              t_lane_launched_run_is_no_hand_run, t_stage_move_time_reads_its_offset,
              t_pass_on_his_recorded_words_folds):
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
