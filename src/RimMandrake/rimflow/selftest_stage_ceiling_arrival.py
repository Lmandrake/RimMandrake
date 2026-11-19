#!/usr/bin/env python3
"""selftest_stage_ceiling_arrival.py — a stage's ceiling counts only what the mod spent there since it last arrived
(RIMMANDRAKE_TRACE_SLACK_STAGE_SIX_SPEND_BEFORE_FIRST_VISIT). One test per promise on
design/specs/2026-11-19-stage-ceiling/boundary.md, each of the promise's name. The fixture
selftest_stage_ceiling_arrival.json is GimmeSomeSlack's real Stage 6 box as read 2026-11-19: 13 runs, USD 119.42 kept,
nine of them started before the mod arrived at Stage 6 (2026-11-16 11:25:09Z), so the ceiling stopped it falsely.

  python3 selftest_stage_ceiling_arrival.py [--only t_name ...]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation_dispatch as MD  # noqa: E402

FAILS = []
FX = os.path.join(HERE, "selftest_stage_ceiling_arrival.json")


def check(ok, what):
    print(("ok    " if ok else "FAIL  ") + what)
    if not ok:
        FAILS.append(what)


def facts():
    with open(FX, encoding="utf-8") as fh:
        fx = json.load(fh)
    f = {k: fx[k] for k in ("box_runs", "run_usd", "runs_seen")}
    f["arrived"] = MD.arrivals(fx["record"])
    return fx, f


def t_counts_only_since_arrival():
    fx, f = facts()
    got = MD.stage_spent(f, "in_game", [], {})
    # the four runs from visit 1's driver on: 30.0 + 1.07 + 3.16 + 1.24
    check(got == 35.47, "counts-only-since-arrival: GSS Stage 6 counts USD 35.47 of the box's 119.42 (got %s)" % got)
    check(MD.over_ceiling(got, fx["cap_usd"], fx["ceiling_usd"], "x") is None,
          "counts-only-since-arrival: GSS is under its ceiling with the next run's cap")
    f["box_runs"]["3"] = {"old": 50.0, "new": 4.0}
    f["stage_runs"], f["run_usd"]["old"], f["run_usd"]["new"] = f["box_runs"]["3"], 50.0, 4.0
    f["runs_seen"] += [{"unit": "old", "at": 1.0}, {"unit": "new", "at": 4e9}]
    f["arrived"]["offline_build"] = 2e9
    got = MD.offline_usd(f, {})
    check(got == 4.0, "counts-only-since-arrival: the offline build drops a run from before its arrival (got %s)" % got)


def t_a_move_within_the_stage_is_not_an_arrival():
    fx, _ = facts()
    got = MD.arrivals(fx["record"]).get("in_game")
    want = MD._ts("2026-11-16T03:25:09-08:00")
    check(got == want, "a-move-within-the-stage-is-not-an-arrival: Stage 6 arrival is the move from Stage 4+5, not "
                       "visit 2's road back of 2026-11-17 (got %s, want %s)" % (got, want))
    got = MD.arrivals({"stage": "in_game", "since": "2026-11-17T09:22:15-08:00", "moves": []}).get("in_game")
    check(got == MD._ts("2026-11-17T09:22:15-08:00"), "a-move-within-the-stage-is-not-an-arrival: a record with no "
                                                      "move into its stage reads its since (got %s)" % got)


def t_unknown_arrival_counts_every_run():
    _, f = facts()
    f["arrived"] = {}
    got = MD.stage_spent(f, "in_game", [], {})
    check(got == 119.42, "unknown-arrival-counts-every-run: no arrival read counts the whole box (got %s)" % got)


def t_void_runs_spend_nothing():
    _, f = facts()
    s = {"voided": [{"unit": "rm-detached-bench-rimmandrake-drive-gimmesomeslack-in-game-1794834319"}]}
    got = MD.stage_spent(f, "in_game", [], s, both=True)
    check(got == (5.47, 30.0), "void-runs-spend-nothing: a voided run after arrival is shown apart (got %s)" % (got,))


def t_this_steps_launches_count():
    _, f = facts()
    got = MD.stage_spent(f, "in_game", [{"unit": "u-new", "cap": 15.0}], {})
    check(got == 50.47, "this-steps-launches-count: a launch not yet placed counts at its cap (got %s)" % got)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    only = set(argv[argv.index("--only") + 1:]) if "--only" in argv else None
    for t in (t_counts_only_since_arrival, t_a_move_within_the_stage_is_not_an_arrival,
              t_unknown_arrival_counts_every_run, t_void_runs_spend_nothing, t_this_steps_launches_count):
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
    print("PASS selftest_stage_ceiling_arrival")
    return 0


if __name__ == "__main__":
    sys.exit(main())
