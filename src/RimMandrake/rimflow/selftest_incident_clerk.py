#!/usr/bin/env python3
"""selftest_incident_clerk: the promises of design/specs/2026-11-19-incident-clerk/boundary.md.

RIMMANDRAKE_CLERK_OPEN_INCIDENTS_FIFTY_SEVEN_RUNS_ONLY_NOTED (owner's card 2026-11-19, "Program follows open
incidents"): a program re-reads the line each open plan states (`rimflow ack --trigger`), writes a "still X, no change"
row and pushes the revisit; a run is rung only when the line is crossed or cannot be read, or the rung changes; a plan
with no line keeps its model revisits and is asked for one; one deep read a day goes out on Opus. Pure: incident.step,
dispatcher.incident_execute and role_launch.launch_role on fixtures; nothing is written outside a temp dir.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = tempfile.mkdtemp(prefix="selftest_incident_clerk_")
os.environ["RM_OPS_WATCH_DIR"] = os.path.join(TMP, "ops")
os.environ["RM_DISPATCHER_STATE"] = os.path.join(TMP, "state")
os.environ["TZ"] = "UTC"
time.tzset()
os.makedirs(os.environ["RM_OPS_WATCH_DIR"])
sys.path[:0] = [HERE, os.path.join(HERE, "..", "Utils"), os.path.join(HERE, "..", "Utils", "ops_core")]
import dispatcher as D  # noqa: E402
import incident as IN  # noqa: E402
import role_launch as RL  # noqa: E402

H, M = 3600, 60
T0 = 1800000000.0          # 2027-01-15T08:00:00Z: after a 07:00 deep-read time
SHIPPED = IN.load_table(IN.ROUTES)
# the shipped policy numbers are the owner's to tune: every case runs on these (RIMMANDRAKE_PIN_TUNABLES_OUT_OF_SELFTESTS)
PIN = dict(ack_within_min=30, recover_min=60, sustain_min=60, event_quiet_min=420, relapse_h=6, tame_relapses=2,
           tame_window_h=24, min_step_min=15, status_max_age_min=45, runs_per_hour=2, owner_revisit_min=240,
           revisit_batch_min=30, revisit_quiet_max_min=1440, revisit_clock_slack_min=2,
           ladder={"emergency": [45, 60], "distressed": [60, 240]})
FAILED = set()


def check(promise, ok, what, detail=""):
    print(("PASS " if ok else "FAIL ") + promise + ": " + what + ("" if ok else "  %r" % (detail,)))
    if not ok:
        FAILED.add(promise)


def table(deep=None):
    t = json.loads(json.dumps(SHIPPED))
    t["routes"] = [{"match": "m.*", "route": "program"}] + t["routes"]   # the planted metrics open no incident of their own
    t["policy"].update(PIN, deep_read_local=deep)
    return t


def inc_rows(iid="c-1", trigger=None, v=5, rung=IN.OWNER_RUNG, t=T0, **extra):
    """One incident last looked at `t` with its metric m.<iid> reading v, acked by a run whose plan carries `trigger`."""
    m = "m." + iid
    r = {"ev": "opened", "id": iid, "at": IN.iso(t), "t": t, "state": "open", "rung": rung, "rung_t": t,
         "told_t": t - 9 * H, "told_at": IN.iso(t - 9 * H), "cause": iid.split("-")[0], "class": "distressed",
         "metrics": {m: {"class": "distressed", "event": False}}, "items": [], "reader": "Operations", "ack_min": 30,
         "acked_t": t + M, "recover_by_t": t + H, "recover_by": IN.iso(t + H), "ack_by": "OPERATIONS",
         "plan": "waiting on the fix", "trigger": trigger, "revisit_t": t, "revisit_seen_t": t, "revisits": 1,
         "revisit_read": {m: [True, "distressed", v, True, 0]}}
    r.update(extra)
    return [r]


def status(now, m="MEASURED", age_s=60, **vals):
    """vals: {name: v} for points m.<name with _ for ->, standing distressed."""
    pts = {"m.%s" % k.replace("_", "-"): {"m": m, "v": v, "class": "distressed"} for k, v in vals.items()}
    return {"t": now - age_s, "points": pts, "alarms": {}}


def sane_s(st):
    """The recovering incident s-1's point reads sane: its sane_since holds (and it closes after sustain_min)."""
    st["points"]["m.s-1"]["class"] = "sane"
    return st


def evs(res, iid=None, ev=("revisited", "revisit_quiet", "escalated")):
    return [x for x in res["rows"] if x["ev"] in ev and (iid is None or x["id"] == iid)]


def t_a_trigger_line_is_parsed_or_refused():
    p = "a-trigger-line-is-parsed-or-refused"
    cl = IN.parse_trigger("accounts.system.runway < 10; after 2027-01-15T19:30Z ; m.x >= 2.5")
    check(p, [c[0] for c in cl] == ["metric", "after", "metric"] and cl[0][1:] == ("accounts.system.runway", "<", 10.0)
          and cl[1][1] == IN._epoch("2027-01-15T19:30:00Z") and cl[2][1:] == ("m.x", ">=", 2.5),
          "two metric clauses and a UTC time parse", cl)
    for bad in ("", " ; ", "m.x ~ 3", "m.x > lots", "after tomorrow", "after 2027-01-15T19:30", "m.x > 3; nonsense"):
        try:
            IN.parse_trigger(bad)
            check(p, False, "refuses %r" % bad)
        except ValueError as e:
            check(p, bad.strip(" ;") == "" or any(part.strip() in str(e) for part in bad.split(";") if part.strip()),
                  "refuses %r, naming the part" % bad, str(e))
    path = os.path.join(TMP, "told_ack.jsonl")
    IN.append(inc_rows("a-1"), path)
    row = IN.ack("a-1", "OPERATIONS", "watch the runway", trigger="accounts.system.runway < 10", path=path, now=T0)
    check(p, row.get("trigger") == "accounts.system.runway < 10", "ack stores the line", row)
    n = len(IN.read_rows(path))
    try:
        IN.ack("a-1", "OPERATIONS", "watch", trigger="runway is low", path=path, now=T0)
        check(p, False, "ack refuses a line that does not parse")
    except ValueError as e:
        check(p, "runway is low" in str(e) and len(IN.read_rows(path)) == n, "ack refuses a bad line and writes nothing",
              str(e))
    row = IN.ack("a-1", "OPERATIONS", "a new plan", path=path, now=T0)
    check(p, row.get("trigger") is None and IN.fold(IN.read_rows(path))[0]["a-1"].get("trigger") is None,
          "an ack with no --trigger stores none: a new plan does not inherit the old line", row)
    out = subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), "ack", "--help"], capture_output=True, text=True)
    check(p, out.returncode == 0 and "--trigger" in out.stdout, "rimflow ack takes --trigger", out.stdout[-300:])


def t_a_held_trigger_writes_the_no_change_row_and_pushes_the_revisit():
    p = "a-held-trigger-writes-the-no-change-row-and-pushes-the-revisit"
    tb = table()
    now = T0 + 240 * M
    rows = inc_rows(trigger="m.c-1 > 10")
    res = IN.step(tb, rows, status(now, c_1=7), now)           # the reading moved (5 -> 7) but stays under its line
    e = evs(res, "c-1")
    check(p, [x["ev"] for x in e] == ["revisit_quiet"] and e[0].get("clerk") is True and not res["rings"],
          "a moved reading under its line: one quiet row, no ring", (e, res["rings"]))
    check(p, bool(e) and "m.c-1 7" in (e[0].get("still") or "") and "no change" in e[0]["still"],
          "the row says still X, no change", e)
    x = IN.fold(rows + res["rows"])[0]["c-1"]
    check(p, IN.next_due(tb, x) == now + 240 * M and x.get("trigger") == "m.c-1 > 10" and x.get("plan"),
          "the revisit is pushed a floor on; the plan and its line stay", x)
    r = rig()
    st = {"roles": {}}
    D.incident_execute(dict(res), r, st, "/nonexistent", now, lambda *a: None, lambda *a: None)
    check(p, not (st["roles"].get("Operations") or {}).get("run_now"), "no Operations run is asked", st)
    # a run going out for another incident pulls in revisits due within revisit_batch_min: a held line stays out of it
    both = inc_rows("a-1", t=T0 - 5 * M) + inc_rows("c-1", trigger="m.c-1 > 10", t=T0 + 10 * M)
    res = IN.step(tb, both, status(now, a_1=6, c_1=7), now)
    check(p, [x["id"] for x in evs(res, ev=("revisited",))] == ["a-1"] and [r["id"] for r in res["rings"]] == ["a-1"],
          "the batch pass leaves a held line out of another incident's run", res["rows"])


def t_a_crossed_trigger_launches_one_run():
    p = "a-crossed-trigger-launches-one-run"
    tb = table()
    now = T0 + 60 * M                     # not due until T0 + 240 min: a crossing does not wait for the revisit
    rows = inc_rows(trigger="m.c-1 > 10")
    res = IN.step(tb, rows, status(now, c_1=12), now)
    e = evs(res, "c-1")
    rings = [r for r in res["rings"] if r["id"] == "c-1"]
    check(p, [x["ev"] for x in e] == ["revisited"] and "trigger crossed" in " ".join(e[0]["news"])
          and "m.c-1 reads 12" in " ".join(e[0]["news"]) and len(rings) == 1 and rings[0]["how"] == "fresh_run",
          "a crossing between revisits: one revisit, one fresh run, the clause named", (e, res["rings"]))
    res2 = IN.step(tb, rows + res["rows"], status(now + 5 * M, c_1=12), now + 5 * M)
    check(p, not evs(res2, "c-1") and not res2["rings"], "the next tick launches nothing more (the line went with the plan)",
          (res2["rows"], res2["rings"]))
    timed = inc_rows(trigger="after %s" % time.strftime("%Y-%m-%dT%H:%MZ", time.gmtime(T0 + 30 * M)))
    res3 = IN.step(tb, timed, status(now, c_1=5), now)
    check(p, [x["ev"] for x in evs(res3, "c-1")] == ["revisited"] and len(res3["rings"]) == 1,
          "an after-time clause whose time came launches one run", res3["rows"])
    res4 = IN.step(tb, timed, status(T0 + 20 * M, c_1=5), T0 + 20 * M)
    check(p, not evs(res4, "c-1") and not res4["rings"], "and before its time, nothing", res4["rows"])


def t_a_rung_change_launches_one_run():
    p = "a-rung-change-launches-one-run"
    tb = table()
    now = T0 + 240 * M
    for name, extra in (("reopened", {"ev": "reopened", "id": "c-1", "t": T0 + 10 * M, "reopens": 1}),
                        ("escalated", {"ev": "escalated", "id": "c-1", "t": T0 + 10 * M})):
        res = IN.step(tb, inc_rows(trigger="m.c-1 > 10") + [extra], status(now, c_1=5), now)
        e = evs(res, "c-1")
        check(p, [x["ev"] for x in e] == ["revisited"] and "rung" in " ".join(e[0]["news"]) and len(res["rings"]) == 1,
              "an %s row since the last look, the line holding: one run" % name, (e, res["rings"]))
    joined = {"ev": "joined", "id": "c-1", "t": T0 + 10 * M, "metrics": {
        "m.c-1": {"class": "distressed", "event": False}, "m.new": {"class": "distressed", "event": False}}}
    res = IN.step(tb, inc_rows(trigger="m.c-1 > 10") + [joined], dict(status(now, c_1=5), points=dict(
        status(now, c_1=5)["points"], **{"m.new": {"m": "MEASURED", "v": 1, "class": "distressed"}})), now)
    check(p, [x["ev"] for x in evs(res, "c-1")] == ["revisited"] and "m.new" in " ".join(evs(res, "c-1")[0]["news"]),
          "a metric that joined since the last look: one run", res["rows"])
    low = inc_rows(trigger="m.c-1 > 10", rung=0, recover_by_t=T0 + H)     # acked below his rung, its recover_by gone
    res = IN.step(tb, low, status(T0 + 2 * H, c_1=5), T0 + 2 * H)
    e = evs(res, "c-1")
    check(p, [x["ev"] for x in e] == ["escalated"] and len([r for r in res["rings"] if r["id"] == "c-1"]) == 1,
          "below his rung the climb rings exactly one run, the line holding or not", (e, res["rings"]))


def t_a_trigger_that_cannot_be_read_calls_the_agent():
    p = "a-trigger-that-cannot-be-read-calls-the-agent"
    tb = table()
    now = T0 + 240 * M
    for name, rows, st, says in (
            ("an UNMEASURED point", inc_rows(trigger="m.c-1 > 10"), status(now, m="UNMEASURED", c_1=5), "UNMEASURED"),
            ("an absent point", inc_rows(trigger="m.gone > 10"), status(now, c_1=5), "m.gone"),
            ("a text value", inc_rows(trigger="m.c-1 > 10"), status(now, c_1="high"), "not a number"),
            ("a stale status", inc_rows(trigger="m.c-1 > 10"), status(now, age_s=2 * H, c_1=5), "not fresh"),
            ("a stored line that does not parse", inc_rows(trigger="whenever it looks bad"), status(now, c_1=5),
             "does not parse")):
        res = IN.step(tb, rows, st, now)
        e = evs(res, "c-1")
        news = " ".join(e[0]["news"]) if e and e[0].get("news") else ""
        check(p, [x["ev"] for x in e] == ["revisited"] and "could not be read" in news and says in news
              and any(r["id"] == "c-1" for r in res["rings"]), "%s: revisited, the cause named" % name, e)


def t_a_plan_with_no_trigger_keeps_its_model_revisit_and_is_asked_for_one():
    p = "a-plan-with-no-trigger-keeps-its-model-revisit-and-is-asked-for-one"
    tb = table()
    now = T0 + 240 * M
    res = IN.step(tb, inc_rows(), status(now, c_1=7), now)
    e = evs(res, "c-1")
    ring = [r for r in res["rings"] if r["id"] == "c-1"]
    check(p, [x["ev"] for x in e] == ["revisited"] and "readings moved" in " ".join(e[0]["news"])
          and e[0].get("trigger_owed") is True, "a moved reading with no line: the model revisit stays", e)
    check(p, len(ring) == 1 and "--trigger" in ring[0]["text"], "its run is asked for a trigger line", ring)
    res = IN.step(tb, inc_rows(), status(now, c_1=5), now)
    e = evs(res, "c-1")
    check(p, [x["ev"] for x in e] == ["revisit_quiet"] and e[0].get("trigger_owed") is True and not e[0].get("clerk")
          and "no trigger line" in e[0]["why"], "unchanged with no line: quiet as before, and the row says it is owed", e)
    res = IN.step(tb, inc_rows(auto_ack=True, trigger=None, plan="close on X"), status(now, c_1=5), now)
    check(p, [x["ev"] for x in evs(res, "c-1")] == ["revisited"], "an auto-ack carries no line: graded as before",
          res["rows"])


def rig():
    real = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
    return dict(real, seats={}, ledger_notes=False, publish=False,
                roles=[dict(r, runs_local=[], quick_checks_local=[], economy_local=None) for r in real["roles"]
                       if r["name"] in ("Operations", "Conductor")])


def t_the_daily_deep_read_launches_once_a_day_on_opus():
    p = "the-daily-deep-read-launches-once-a-day-on-opus"
    tb = table(deep="07:00")
    look = T0 - 3 * H            # last looked at 05:00: none is due before 09:00
    rows = (inc_rows("a-1", trigger="m.a-1 > 10", t=look) + inc_rows("b-1", trigger="m.b-1 > 10", t=look)
            + inc_rows("t-1", trigger="m.t-1 > 10", t=look, tamed=True)
            + inc_rows("s-1", trigger="m.s-1 > 10", t=look, sane_since=T0 - M))
    pre = IN.step(tb, rows, sane_s(status(T0 - 2 * H, a_1=5, b_1=5, t_1=5, s_1=5)), T0 - 2 * H)      # 06:00: before its time
    check(p, not [x for x in pre["rows"] if x.get("deep")], "before deep_read_local, no deep read", pre["rows"])
    now = T0 + 10 * M
    res = IN.step(tb, rows, sane_s(status(now, a_1=5, b_1=5, t_1=5, s_1=5)), now)
    deep = sorted(x["id"] for x in res["rows"] if x["ev"] == "revisited" and x.get("deep"))
    rings = [r for r in res["rings"] if r.get("deep")]
    check(p, deep == ["a-1", "b-1"] and sorted(r["id"] for r in rings) == ["a-1", "b-1"]
          and all(r["how"] == "fresh_run" for r in rings),
          "after its time: every open untamed incident at his rung, not recovering, read deep, triggers holding",
          (res["rows"], res["rings"]))
    rows2 = rows + res["rows"]
    res2 = IN.step(tb, rows2, sane_s(status(now + H, a_1=5, b_1=5, t_1=5, s_1=5)), now + H)
    check(p, not [x for x in res2["rows"] if x.get("deep")] and not [r for r in res2["rings"] if r.get("deep")],
          "a later tick that day adds none", res2["rows"])
    rows3 = rows2 + res2["rows"]
    day2 = T0 + 23 * H + 5 * M    # 07:05 the next day
    res3 = IN.step(tb, rows3, sane_s(status(day2, a_1=5, b_1=5, t_1=5, s_1=5)), day2)
    check(p, sorted(x["id"] for x in res3["rows"] if x.get("deep")) == ["a-1", "b-1"], "the next day it comes again",
          res3["rows"])
    st = {"roles": {}}
    D.incident_execute(dict(res), rig(), st, "/nonexistent", now, lambda *a: None, lambda *a: None)
    req = (st["roles"].get("Operations") or {}).get("run_now") or {}
    check(p, req.get("model") == "opus" and req.get("ids") == ["a-1", "b-1"] and "DAILY DEEP READ" in req.get("why", ""),
          "the dispatcher asks ONE Operations run for the batch, carrying model opus", req)
    op = next(r for r in rig()["roles"] if r["name"] == "Operations")
    sonnet_runs = dict(op, model_by_mode=dict(op.get("model_by_mode") or {}, run="sonnet"))
    check(p, RL.launch_role(sonnet_runs, {"mode": "run", "run_now": req})["model"] == "opus"
          and RL.launch_role(sonnet_runs, {"mode": "run", "run_now": {"by": "DISPATCHER"}})["model"] == "sonnet",
          "launch_role puts the deep run on Opus even where model_by_mode picks Sonnet; other runs keep theirs")
    check(p, RL.job_model(sonnet_runs, {"mode": "run", "manual": req}) == "opus",
          "the launcher's account reading and its log name the same model (job_model)")


def main():
    t_a_trigger_line_is_parsed_or_refused()
    t_a_held_trigger_writes_the_no_change_row_and_pushes_the_revisit()
    t_a_crossed_trigger_launches_one_run()
    t_a_rung_change_launches_one_run()
    t_a_trigger_that_cannot_be_read_calls_the_agent()
    t_a_plan_with_no_trigger_keeps_its_model_revisit_and_is_asked_for_one()
    t_the_daily_deep_read_launches_once_a_day_on_opus()
    n = 7
    print("selftest_incident_clerk: %d of %d promises pass%s" % (n - len(FAILED), n,
                                                                 "" if not FAILED else " (FAIL: %s)" % ", ".join(sorted(FAILED))))
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
