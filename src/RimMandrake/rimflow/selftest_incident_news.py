#!/usr/bin/env python3
"""selftest_incident_news: the promises of design/specs/2026-11-19-incident-news-and-program-routes/boundary.md.

RIMMANDRAKE_QUIET_OPS_REPEATS_AGING_COUNTS_AS_NEWS (owner's card 2026-11-19, "Fix the news bug" and "Program answers 5
repeat alarms"): a reading that only aged is not revisit news, a banded count is news only when it leaves its band, and
five repeat no-fix alarms are answered by a program note while their reading stays in band. Pure: incident.step and
role_launch.decide_roles on fake observers; nothing is written outside a temp dir.
"""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_incident_news_")
os.environ["RM_OPS_WATCH_DIR"] = os.path.join(TMP, "ops")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["TZ"] = "UTC"
time.tzset()
sys.path[:0] = [HERE, os.path.dirname(HERE)]
import incident as IN  # noqa: E402
import role_launch as RL  # noqa: E402
import selftest_dispatcher as SD  # noqa: E402

FAILS = []
SHIPPED = IN.load_table(IN.ROUTES)
FIVE = ("steve.incident_unclaimed_min", "accounts.lukas.runway", "wrapup.debris_standing",
        "maturation.idle_owed_max_min", "disk.scratch_dirty_end")
T0 = 1800000000.0


def check(ok, what, detail=""):
    print(("PASS " if ok else "FAIL ") + what + ("" if ok else "  %r" % (detail,)))
    if not ok:
        FAILS.append(what)


def row(v, standing=False, cls="warn", measured=True, fired=0):
    return [standing, cls, v, measured, fired]


def t_a_clock_that_only_aged_is_not_news():
    r1 = IN.reading_moved("plan.days_since_advance", row(2.0), row(2.0 + 1 / 24.0), 3600, 0)
    r2 = IN.reading_moved("plan.list_age_h", row(5.0), row(6.0), 3600, 0)
    check(r1 is False and r2 is False, "a-clock-that-only-aged-is-not-news: days_since_advance and list_age_h aged 1 h",
          (r1, r2))
    # the same, inside the slack, and the other day spellings
    check(IN.reading_moved("plan.days_since_advance", row(2.0), row(2.0 + 1.01 / 24.0), 3600, 120) is False,
          "a-clock-that-only-aged-is-not-news: inside the slack")
    # as ops_watch writes it, rounded to 0.01 d: an hour reads 0.04 or 0.05 (17.96 -> 18.0 -> 18.05)
    check(IN.reading_moved("plan.days_since_advance", row(17.96), row(18.0), 3600, 120) is False
          and IN.reading_moved("plan.days_since_advance", row(18.0), row(18.05), 3600, 120) is False,
          "a-clock-that-only-aged-is-not-news: a day clock rounded to 0.01 d aged an hour")
    # graded over the points' own observation times: the live 2026-11-17 revisit read 63.77 -> 67.66 h across a
    # 241.6 min status gap, the collector's two readings 233.4 min apart
    o, n = row(63.77) + [T0], row(67.66) + [T0 + 233.4 * 60]
    check(IN.reading_moved("plan.list_age_h", o, n, 241.6 * 60, 120) is False
          and IN.reading_moved("plan.list_age_h", row(63.77), row(67.66), 241.6 * 60, 120) is True,
          "a-clock-that-only-aged-is-not-news: graded over its own observed_at, not the status gap")
    pt = {"m": "MEASURED", "v": 1.5, "x": {"observed_at": "2027-01-15T08:00:00Z"}}
    rd = IN.revisit_reads({"metrics": {"plan.list_age_h": {}}}, {"points": {"plan.list_age_h": pt}}, {}, [])
    check(rd["plan.list_age_h"][5] == IN._epoch("2027-01-15T08:00:00Z"),
          "a-clock-that-only-aged-is-not-news: revisit_reads keeps the point's observed_at", rd)
    check(IN.clock_unit_s("x.wait_d") == 86400 and IN.clock_unit_s("x.wait_days") == 86400
          and IN.clock_unit_s("plan.days_since_advance") == 86400 and IN.clock_unit_s("plan.closes_24h") is None,
          "a-clock-that-only-aged-is-not-news: _d, _days and days_since_ names read in days, a plain count does not")


def t_a_clock_reset_is_news():
    check(IN.reading_moved("plan.days_since_advance", row(2.0), row(0.0), 3600, 120) is True,
          "a-clock-reset-is-news: days_since_advance reset to 0")
    check(IN.reading_moved("plan.days_since_advance", row(2.0), row(2.001), 3600, 60) is True,
          "a-clock-reset-is-news: a clock that crept while an hour passed moved")
    check(IN.reading_moved("plan.days_since_advance", row(17.96), row(17.98), 3600, 120) is True
          and IN.reading_moved("plan.list_age_h", row(5), row(5.4), 3600, 120) is True,
          "a-clock-reset-is-news: a rounded clock that rose well under the hour that passed moved")


def band_of(metric):
    return (IN.route_of(SHIPPED, metric) or {}).get("band")


def t_a_banded_count_inside_its_band_is_not_news():
    b = band_of("wrapup.debris_standing")
    check(isinstance(b, dict), "a-banded-count-inside-its-band-is-not-news: debris carries a band", b)
    moved = [IN.reading_moved("wrapup.debris_standing", o, n, 3600, 0, band=b) for o, n in (
        (row(0, standing=False, cls="sane"), row(3, standing=True, cls=None)),
        (row(3, standing=True, cls=None), row(0, standing=False, cls="sane")),
        (row(2, standing=True), row(5, standing=True)))]
    check(moved == [False, False, False], "a-banded-count-inside-its-band-is-not-news: 0->3, 3->0, 2->5", moved)
    # through revisit_news with the shipped table: the reading flapped, nothing else moved
    inc = {"id": "wrapup-x", "metrics": {"wrapup.debris_standing": {}}, "plan": "p", "revisit_plan": "p",
           "revisit_seen_t": T0, "revisit_t": T0, "revisit_status_t": T0,
           "revisit_read": {"wrapup.debris_standing": row(0, cls="sane")}}
    news = IN.revisit_news(inc, {"wrapup.debris_standing": row(4, standing=True, cls=None)}, True, [], [], T0 + 3600,
                           SHIPPED["policy"], None, T0 + 3600, table=SHIPPED)
    check(news == [], "a-banded-count-inside-its-band-is-not-news: revisit_news finds no news", news)


def t_a_banded_count_leaving_its_band_is_news():
    b = band_of("wrapup.debris_standing")
    hi = (b or {}).get("max", 0)
    check(IN.reading_moved("wrapup.debris_standing", row(3), row(hi + 1), 3600, 0, band=b) is True,
          "a-banded-count-leaving-its-band-is-news: up out of the band")
    check(IN.reading_moved("wrapup.debris_standing", row(3), row(3, measured=False), 3600, 0, band=b) is True
          and IN.reading_moved("wrapup.debris_standing", row(3), None, 3600, 0, band=b) is True,
          "a-banded-count-leaving-its-band-is-news: unmeasured or gone is news")
    check(IN.reading_moved("wrapup.debris_standing", row(3), row(3, fired=1), 3600, 0, band=b) is True,
          "a-banded-count-leaving-its-band-is-news: a fired signal is still news")


def t_the_five_repeat_alarms_are_program_routes_with_a_runbook():
    ok = []
    for k in FIVE:
        r = IN.route_of(SHIPPED, k) or {}
        b = r.get("band") or {}
        ok.append(r.get("route") == "program" and bool(r.get("runbook")) and isinstance(b, dict)
                  and any(isinstance(b.get(x), (int, float)) for x in ("min", "max"))
                  and r.get("reader") == "Operations" and bool(r.get("cause")))
    check(all(ok), "the-five-repeat-alarms-are-program-routes-with-a-runbook: %d of 5" % sum(ok), dict(zip(FIVE, ok)))
    sib = [(k, (IN.route_of(SHIPPED, k) or {}).get("route")) for k in (
        "accounts.system.runway", "steve.invalid_streak", "disk.scratch_dirty_start", "wrapup.records_24h",
        "maturation.stalled")]
    check(all(r == "role" for _, r in sib), "the-five-repeat-alarms-are-program-routes-with-a-runbook: siblings stay role",
          sib)


def status(metric, v, m="MEASURED", alarm_open=True):
    tag = "TAG"
    return {"t": T0, "points": {metric: {"m": m, "v": v}},
            "alarms": {"%s:%s" % (tag, metric): {"state": "OPEN", "item": "OPS_ITEM_X"}} if alarm_open else {}}


def t_in_band_opens_no_incident():
    opened = {}
    for k in FIVE:
        b = band_of(k)
        v = b.get("max", b.get("min")) if b else None      # the band's own edge: inclusive
        res = IN.step(SHIPPED, [], status(k, v), T0)
        opened[k] = [r["ev"] for r in res["rows"]]
    check(all(not v for v in opened.values()), "in-band-opens-no-incident: none of the five at its band edge", opened)


def out_of_band(k):
    b = band_of(k)
    return b["max"] + 1 if "max" in b else b["min"] - 0.01


def t_out_of_band_opens_the_routes_incident():
    got = {}
    for k in FIVE:
        res = IN.step(SHIPPED, [], status(k, out_of_band(k)), T0)
        op = [r for r in res["rows"] if r["ev"] == "opened"]
        rt = IN.route_of(SHIPPED, k)
        got[k] = bool(op) and op[0]["cause"] == rt["cause"] and op[0]["reader"] == rt["reader"] and bool(res["keys"])
    check(all(got.values()), "out-of-band-opens-the-routes-incident: all five open their cause's incident", got)


def t_an_unmeasured_reading_calls_the_agent():
    k = "wrapup.debris_standing"
    rt = IN.route_of(SHIPPED, k)
    ans = [IN.program_answer(rt, p) for p in (None, {"m": "UNMEASURED", "v": 1}, {"m": "MEASURED", "v": None},
                                              {"m": "MEASURED", "v": "3"}, {"m": "MEASURED", "v": True})]
    check(all(a and a[0] == "agent" and a[1] for a in ans), "an-unmeasured-reading-calls-the-agent: every blind shape", ans)
    check(IN.program_answer(rt, {"m": "MEASURED", "v": 1})[0] == "program"
          and IN.program_answer(IN.route_of(SHIPPED, "cap:x"), {"m": "MEASURED", "v": 1}) is None,
          "an-unmeasured-reading-calls-the-agent: a measured in-band reading is the program's; an unbanded route is not this")
    res = IN.step(SHIPPED, [], status(k, 1, m="UNMEASURED"), T0)
    check(any(r["ev"] == "opened" for r in res["rows"]), "an-unmeasured-reading-calls-the-agent: step opens its incident")


def op():
    return SD.operations(runs_local=["07:30"], economy_pass_local=None, model="opus", model_by_mode={"alarm": "sonnet"})


def drive(rs, now, st_status):
    st = {"roles": {"Operations": rs}}
    acts = []
    RL.decide_roles({"roles": [op()]}, st, SD.robs(st_status), now, lambda **kw: acts.append(kw), set(), None)
    return acts, st["roles"]["Operations"]


def ops_with(now, metric, v, item="OPS_DEBRIS_ITEM"):
    s = SD.ops_status(now, alarms={"WRAPUP_DEBRIS:%s" % metric: {
        "state": "OPEN", "item": item, "clear_seen": 0, "title": "Ops alarm WRAPUP_DEBRIS", "since": "x",
        "told": {"v": v}}})
    s["points"][metric] = {"m": "MEASURED", "v": v}
    return s


def launched(acts):
    return [a for a in acts if a.get("do") == "role_launch" and a.get("mode") == "alarm"]


def program_notes(acts):
    return [a for a in acts if a.get("do") == "role_hold" and a.get("note") and "program answer" in a.get("why", "")]


def t_a_program_answered_alarm_buys_no_alarm_run_and_is_noted_once():
    t = SD.at_local("12:00")
    k = "wrapup.debris_standing"
    acts, rs = drive({"done": {}, "runs": []}, t, ops_with(t, k, 2))
    notes = program_notes(acts)
    runbook = IN.route_of(SHIPPED, k)["runbook"]
    check(not launched(acts) and len(notes) == 1 and notes[0].get("ticket") == "OPS_DEBRIS_ITEM"
          and runbook in notes[0]["why"],
          "a-program-answered-alarm-buys-no-alarm-run-and-is-noted-once: no run, one runbook note on the item",
          [(a.get("do"), a.get("ticket"), a.get("why")) for a in acts])
    check("OPS_DEBRIS_ITEM" not in (rs.get("alarms_seen") or []),
          "a-program-answered-alarm-buys-no-alarm-run-and-is-noted-once: the key is not marked seen")
    acts2, rs = drive(rs, t + 60, ops_with(t + 60, k, 3))
    check(not launched(acts2) and not program_notes(acts2),
          "a-program-answered-alarm-buys-no-alarm-run-and-is-noted-once: the next tick notes nothing again")
    # an alarm with no item (RUNWAY_LOW on accounts) notes on the role's own item
    s = SD.ops_status(t, alarms={"RUNWAY_LOW:accounts.lukas.runway": {
        "state": "OPEN", "for": "Operations", "clear_seen": 0, "title": "t", "since": "x", "told": {"v": 0.5}}})
    s["points"]["accounts.lukas.runway"] = {"m": "MEASURED", "v": 0.5}
    acts3, _ = drive({"done": {}, "runs": []}, t, s)
    n3 = program_notes(acts3)
    check(not launched(acts3) and len(n3) == 1 and n3[0].get("ticket") == op()["ledger_item"],
          "a-program-answered-alarm-buys-no-alarm-run-and-is-noted-once: an itemless alarm notes on the role's item",
          [(a.get("do"), a.get("ticket"), a.get("why")) for a in acts3])


def t_leaving_the_band_gets_its_run():
    t = SD.at_local("12:00")
    k = "wrapup.debris_standing"
    _, rs = drive({"done": {}, "runs": []}, t, ops_with(t, k, 2))
    acts, rs = drive(rs, t + 120, ops_with(t + 120, k, out_of_band(k)))
    la = launched(acts)
    check(len(la) == 1 and "alarm OPS_DEBRIS_ITEM" in la[0].get("why", ""),
          "leaving-the-band-gets-its-run: out of band, the alarm run launches at once",
          [(a.get("do"), a.get("why")) for a in acts])


def main():
    t_a_clock_that_only_aged_is_not_news()
    t_a_clock_reset_is_news()
    t_a_banded_count_inside_its_band_is_not_news()
    t_a_banded_count_leaving_its_band_is_news()
    t_the_five_repeat_alarms_are_program_routes_with_a_runbook()
    t_in_band_opens_no_incident()
    t_out_of_band_opens_the_routes_incident()
    t_an_unmeasured_reading_calls_the_agent()
    t_a_program_answered_alarm_buys_no_alarm_run_and_is_noted_once()
    t_leaving_the_band_gets_its_run()
    print("selftest_incident_news: %s (%d fails)" % ("OK" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
