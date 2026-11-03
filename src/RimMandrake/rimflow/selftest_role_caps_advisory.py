#!/usr/bin/env python3
"""Operations' token caps are ADVISORY (owner 2026-11-02, ledger e7069d65ba: "a token limit for operations must be
advisory only. We can't have the system crash because we couldn't afford to watch. At the same time if it becomes
expensive it requires immediate action for sure. But not starving it or failing to do maintenance.")

A role with `caps_advisory: true`, against the same state that holds or refuses a role without it:
  A1 a scheduled slot past daily_token_cap LAUNCHES, with ONE immediate overspend_day alarm (Conductor log, RAISE
     FIRST); unflagged it is REFUSED.
  A2 a throttle band that skips slots (FLOOR, slots "none") or shrinks budgets (quick_cap_x) neither skips nor
     shrinks it; unflagged it is skipped.
  A3 the daily alarm-run count (alarm_runs_per_day) does not hold its alarm run; unflagged it waits.
  A4 a DISPATCHER incident run-now past the cap launches (it used to be refused, and the refusal sent its incidents
     to the owner rung); unflagged it is refused.
  A5 a finished run over its budget alarms at once with a RAISE FIRST line, and a day past the cap raises
     overspend_day once; unflagged the overrun alarm stays note-only.
  A6 the schedule validates the flag and the real Operations entry carries it.
  A7 since owner 2026-11-02 (TOKEN_LIMITS_TAME_BARK_NO_BITE) every role is advisory by DEFAULT: "unflagged" above
     means `caps_advisory: false` set explicitly (the strict gates, kept for when he lifts the ruling).
Pure: fake observers (selftest_dispatcher helpers)."""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
os.environ["TZ"] = "UTC"
time.tzset()
import role_launch as RL  # noqa: E402
import selftest_dispatcher as SD  # noqa: E402

FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def drive(role, now, rs=None, status=None, ro=None):
    st = {"roles": {"Operations": rs}} if rs is not None else {"roles": {}}
    acts = []
    o = ro or SD.robs(status or SD.ops_status(now))
    RL.decide_roles({"roles": [role]}, st, o, now, lambda **kw: acts.append(kw), set(), None)
    return acts, st


def launched(acts):
    return [a for a in acts if a.get("do") == "role_launch"]


def spent_rs(now, tokens):
    return {"done": {}, "runs": [{"state": "done", "unit": "rm-role-operations-1", "at": now - 7200, "day": RL.day_of(now),
                                  "tokens": tokens, "budget": 60000, "mode": "run"}]}


def main():
    # A1
    t = SD.at_local("07:30")
    for flag in (True, False):
        acts, st = drive(SD.operations(caps_advisory=flag), t, spent_rs(t, 290000))
        la = launched(acts)
        od = [a for a in acts if a.get("kind") == "role:Operations:overspend_day"]
        if flag:
            check(len(la) == 1 and la[0]["budget"] == 150000 if la else False,
                  "A1 advisory: the 07:30 slot past the cap launches at its full budget")
            check(len(od) == 1 and od[0].get("conductor_log") and "RAISE" not in od[0].get("why", "")
                  and "never starve" in od[0].get("raise_first", "") and "LAUNCHED anyway" in od[0]["why"],
                  "A1 advisory: one overspend_day alarm, Conductor log, RAISE FIRST line (%r)" % od)
            acts2, _ = drive(SD.operations(caps_advisory=True), t + 60, st["roles"]["Operations"])
            check(not [a for a in acts2 if a.get("kind") == "role:Operations:overspend_day"],
                  "A1 advisory: overspend_day is raised once a day, not every tick")
        else:
            check(not la and any("REFUSED: daily_token_cap" in a.get("why", "") for a in acts),
                  "A1 unflagged: the same slot is REFUSED on the daily cap")
    # A2
    bands = {"GREEN": {"runway_ge": 1.5, "quick_cap_x": 1.0, "slots": "all"},
             "AMBER": {"runway_ge": 0.0, "quick_cap_x": 0.5, "slots": "first"},
             "FLOOR": {"week_left_pct_lt": 10, "quick_cap_x": 0.4, "slots": "none"}}
    t = SD.at_local("19:30")
    floor = SD.ops_status(t, week_left=5.0)
    acts, _ = drive(SD.operations(caps_advisory=True, throttle_bands=bands), t, status=floor)
    la = launched(acts)
    check(len(la) == 1 and la[0]["budget"] == 60000, "A2 advisory: FLOOR (slots none) neither skips nor shrinks it (%r)"
          % [(a.get("do"), a.get("budget"), a.get("why")) for a in acts])
    acts, _ = drive(SD.operations(caps_advisory=False, throttle_bands=bands), t, status=floor)
    check(not launched(acts), "A2 strict (caps_advisory false): FLOOR skips the slot")
    acts, _ = drive(SD.operations(throttle_bands=bands), t, status=floor)
    check(len(launched(acts)) == 1, "A2 unflagged is advisory by default (owner 2026-11-02, token limits advisory "
          "everywhere): FLOOR does not skip it")
    # A3
    t = SD.at_local("12:00")
    al = {"a1": {"state": "OPEN", "item": "ITEM_ONE"}}
    used = {"done": {}, "runs": [], "alarm_day": {"day": RL.day_of(t), "n": 2, "keys": {}}}
    for flag in (True, False):
        op = SD.operations(runs_local=["07:30"], economy_pass_local=None, alarm_runs_per_day=2, caps_advisory=flag)
        acts, _ = drive(op, t, json.loads(json.dumps(used)), SD.ops_status(t, alarms=al))
        la = [a for a in launched(acts) if a.get("mode") == "alarm"]
        if flag:
            check(len(la) == 1, "A3 advisory: the alarm run launches past alarm_runs_per_day (%r)" % [
                (a.get("do"), a.get("why")) for a in acts])
        else:
            check(not la, "A3 unflagged: the alarm run waits on alarm_runs_per_day")
    # A4
    t = SD.at_local("12:00")
    for flag in (True, False):
        op = SD.operations(caps_advisory=flag)
        rs = spent_rs(t, 290000)
        rs["run_now"] = RL.run_now_request({"roles": [op]}, {"role": "Operations", "by": "DISPATCHER",
                                                             "why": "INCIDENT disk-1", "mode": "run"}, t - 30)
        rs["run_now"]["covers_slot"] = True
        acts, st = drive(op, t, rs)
        last = st["roles"]["Operations"].get("run_now_last") or {}
        if flag:
            check(len(launched(acts)) == 1 and not str(last.get("outcome", "")).startswith("refused"),
                  "A4 advisory: an incident run-now past the cap launches (%r)" % [(a.get("do"), a.get("why")) for a in acts])
        else:
            check(not launched(acts) and str(last.get("outcome", "")).startswith("refused"),
                  "A4 unflagged: it is refused (the path that sent incidents to his rung)")
    # A5
    t = SD.at_local("12:00")
    for flag in (True, False):
        cfg = dict(RL.ROLE_DEFAULTS, **SD.operations(caps_advisory=flag))
        rs = spent_rs(t, 250000)
        rs["runs"].append({"state": "running", "unit": "rm-role-operations-2", "at": t - 600, "day": RL.day_of(t),
                           "budget": 60000, "mode": "run", "item": "ROLES_ITEM_X", "scope": "S.scope", "marker": "M"})
        res = {"subtype": "success", "usage": SD.usage(input_tokens=90000)}
        obs = {"unit_state": lambda u: "inactive", "result": lambda r: res, "procs": lambda *a, **k: []}
        acts = []
        RL._supervise_one("Operations", rs, cfg, obs, t, lambda **kw: acts.append(kw), set())
        ob = [a for a in acts if a.get("kind") == "role:Operations:overbudget"]
        od = [a for a in acts if a.get("kind") == "role:Operations:overspend_day"]
        if flag:
            check(len(ob) == 1 and ob[0].get("conductor_log") and "cut its cost" in ob[0].get("raise_first", ""),
                  "A5 advisory: a run over budget alarms at once in the Conductor log (%r)" % ob)
            check(len(od) == 1 and "just finished" in od[0]["why"],
                  "A5 advisory: the day past its cap raises overspend_day at the run's end (%r)" % od)
        else:
            check(len(ob) == 1 and not ob[0].get("conductor_log") and not od,
                  "A5 unflagged: the overrun stays a note-only alarm")
    # A6
    try:
        RL.validate_role(dict(RL.ROLE_DEFAULTS, **SD.operations(caps_advisory="yes")))
        bad = False
    except ValueError as e:
        bad = "caps_advisory" in str(e)
    sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
    ops = [r for r in sch["roles"] if isinstance(r, dict) and r.get("name") == "Operations"]
    check(bad, "A6 caps_advisory must be true or false")
    check(ops and ops[0].get("caps_advisory") is True and "e7069d65ba" in ops[0].get("_caps_advisory_why", ""),
          "A6 the real Operations entry is advisory and cites the ruling")
    # A7 (owner 2026-11-02, TOKEN_LIMITS_TAME_BARK_NO_BITE: "Please make token limits advisory at this time
    # everywhere. Nothing gets killed or stopped for that, but it might call attention"): a role with NO flag, past its
    # daily cap, launches and raises the attention line (overspend_day, Conductor log); the defaults say so
    check(RL.ROLE_DEFAULTS.get("caps_advisory") is True and RL.ROLE_DEFAULTS.get("degraded_reading_ok") is True,
          "A7 every role is advisory by default")
    t = SD.at_local("07:30")
    plain = {k: v for k, v in SD.operations().items() if k not in ("caps_advisory", "degraded_reading_ok")}
    acts, _ = drive(plain, t, spent_rs(t, 290000))
    od = [a for a in acts if a.get("do") == "alarm" and str(a.get("kind", "")).endswith(":overspend_day")]
    check(len(launched(acts)) == 1 and len(od) == 1 and od[0].get("conductor_log") and "LAUNCHED anyway" in od[0]["why"],
          "A7 unflagged past its daily cap: launched, one attention alarm to the Conductor log (%r)"
          % [(a.get("do"), a.get("kind")) for a in acts])
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
