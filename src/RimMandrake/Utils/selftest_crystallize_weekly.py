#!/usr/bin/env python3
"""selftest for crystallize_weekly.py (RIMMANDRAKE_REVIVE_WEEKLY_CRYSTALLIZE_RAN_31_DAYS_APART). One test per promise of
design/specs/2026-11-25-weekly-crystallize-run/boundary.md. Fixtures only: no ledger write, no launch, no live timer.

    python3 src/RimMandrake/Utils/selftest_crystallize_weekly.py
"""
import datetime as DT
import io
import json
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TMP = tempfile.mkdtemp(prefix="selftest_crystallize_weekly_")
CON = os.path.join(TMP, "rimmandrake", "conductor")
os.environ["RM_CRYSTALLIZE_DIR"] = CON
import crystallize_weekly as CW  # noqa: E402

FAILS = []
ON = lambda: (True, "rm-crystallize.timer is enabled/active")            # noqa: E731
OFF = lambda: (False, "rm-crystallize.timer is disabled/inactive")       # noqa: E731
BLIND = lambda: (None, "systemctl gave nothing")                         # noqa: E731


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def fresh_dir():
    shutil.rmtree(os.path.join(TMP, "rimmandrake"), ignore_errors=True)
    os.makedirs(CON)


def put(week, text):
    d = os.path.join(CON, "crystallize_" + week)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "CYCLE_REPORT.md"), "w") as f:
        f.write(text)


def quiet(fn, *a, **k):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = fn(*a, **k)
    return rc, buf.getvalue()


def plan(day):
    rc, out = quiet(CW.tick, False, day)
    return rc, json.loads(out.strip().splitlines()[-1])


def t_weeks_are_iso_weeks():
    check(CW.week_of(DT.date(2026, 11, 25)) == "2026W48", "2026-11-25 is 2026W48")
    check(CW.week_of(DT.date(2027, 1, 1)) == "2026W53", "ISO year: 2027-01-01 is 2026W53")
    check(CW.monday("2026W47") == DT.date(2026, 11, 16), "monday of 2026W47")


def t_a_final_report_is_the_stand_alone_status_line():
    fresh_dir()
    put("2026W43", "# Crystallize 2026-W43\n\nStatus: FINAL\n")
    put("2026W47", "# Crystallize 2026-W47\n\nStatus: FINAL\n")
    put("2026W48", "# Crystallize 2026-W48\n\nStatus: DRAFT (write `Status: FINAL` last)\n")
    put("notaweek", "Status: FINAL\n")
    rs = CW.reports(CON)
    check([r[0] for r in rs] == ["2026W43", "2026W47", "2026W48"], "reports sorted by week, a bad folder name skipped")
    check([r[2] for r in rs] == [True, True, False], "a DRAFT that quotes the FINAL line is not FINAL")
    check(CW.newest_final(CON)[0] == "2026W47", "newest FINAL")
    check(CW.newest_final(CON, before="2026W47")[0] == "2026W43", "newest FINAL before a week")
    check(quiet(CW.main, ["report", "2026W47"])[0] == 0, "report 2026W47 holds")
    check(quiet(CW.main, ["report", "2026W48"])[0] == 1, "report 2026W48 (DRAFT) fails")


def t_a_week_with_a_final_report_launches_nothing():
    check(CW.decide("2026W48", True, None, False)[0] == "none", "decide: a FINAL report this week: nothing")
    check(CW.decide("2026W48", False, "done", False)[0] == "none", "decide: the week's item closed: nothing")
    fresh_dir()
    put("2026W50", "# x\nStatus: FINAL\n")
    CW.item_state = lambda iid: None
    check(plan(DT.datetime(2026, 12, 9, 6))[1]["act"] == "none", "tick: the week's FINAL report stops the launch")


def t_a_good_launch_is_not_repeated_in_its_week():
    check(CW.decide("2026W48", False, "doing", True)[0] == "none", "decide: a good launch: the run owns the week")
    fresh_dir()
    CW.item_state = lambda iid: "doing"
    CW.record(CW.reading_dir(CON), {"week": "2026W50", "act": "launch", "ok": True})
    check(plan(DT.datetime(2026, 12, 10, 6))[1]["act"] == "none", "tick: no second launch in the week")


def t_a_refused_launch_is_tried_again_next_tick():
    fresh_dir()
    CW.item_state = lambda iid: None
    CW.record(CW.reading_dir(CON), {"week": "2026W51", "act": "file+launch", "ok": False})
    rc, rec = plan(DT.datetime(2026, 12, 15, 6))
    check(rec["act"] == "file+launch" and rec["item"] == "RIMMANDRAKE_RUN_WEEKLY_CRYSTALLIZE_2026W51",
          "tick: a refused launch is planned again, the week's item named")
    CW.item_state = lambda iid: "proposed"
    check(plan(DT.datetime(2026, 12, 15, 6))[1]["act"] == "launch", "tick: a filed item is launched, not filed again")


def t_a_plan_writes_nothing():
    fresh_dir()
    CW.item_state = lambda iid: None
    plan(DT.datetime(2026, 12, 9, 6))
    check(not os.path.exists(os.path.join(CW.reading_dir(CON), "last.json")), "a plan writes no reading")
    check(not os.path.exists(os.path.join(CW.reading_dir(CON), "briefs")), "a plan writes no brief")


def t_fresh_needs_the_timer_and_a_report_of_this_or_last_week():
    fresh_dir()
    put("2026W47", "# x\nStatus: FINAL\n")
    nov25, dec2 = DT.datetime(2026, 11, 25, 12), DT.datetime(2026, 12, 2, 12)
    check(quiet(CW.fresh, nov25, ON)[0] == 0, "W48, FINAL W47, timer on: holds")
    check(quiet(CW.fresh, nov25, OFF)[0] == 1, "timer off: fails though the report is fresh")
    check(quiet(CW.fresh, dec2, ON)[0] == 1, "W49 with only W47 FINAL: a skipped week fails")
    put("2026W48", "# x\nStatus: FINAL\n")
    check(quiet(CW.fresh, dec2, ON)[0] == 0, "W49 with W48 FINAL: holds")
    fresh_dir()
    check(quiet(CW.fresh, nov25, ON)[0] == 1, "no report at all: fails")


def t_an_unreadable_timer_is_could_not_look():
    check(quiet(CW.fresh, DT.datetime(2026, 11, 25, 12), BLIND)[0] == 2, "systemctl unreadable: exit 2, never a pass")


def t_the_brief_names_the_week_item_and_last_pass():
    fresh_dir()
    put("2026W48", "# x\nStatus: FINAL\n")
    b = CW.brief("2026W50", CON, CW.newest_final(CON))
    check("RIMMANDRAKE_RUN_WEEKLY_CRYSTALLIZE_2026W50" in b and "crystallize_2026W48" in b
          and "crystallize_2026W50" in b and "{" not in b, "brief: every slot filled, the last pass named")
    check("none: no earlier FINAL report" in CW.brief("2026W50", CON, None), "brief: no last pass is said")
    check(CW.opus_cap() > 0, "the cap is read from list_dispatch.json")


def main():
    t_weeks_are_iso_weeks()
    t_a_final_report_is_the_stand_alone_status_line()
    t_a_week_with_a_final_report_launches_nothing()
    t_a_good_launch_is_not_repeated_in_its_week()
    t_a_refused_launch_is_tried_again_next_tick()
    t_a_plan_writes_nothing()
    t_fresh_needs_the_timer_and_a_report_of_this_or_last_week()
    t_an_unreadable_timer_is_could_not_look()
    t_the_brief_names_the_week_item_and_last_pass()
    shutil.rmtree(TMP, ignore_errors=True)
    print("FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
