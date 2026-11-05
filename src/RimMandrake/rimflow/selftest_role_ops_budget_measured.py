#!/usr/bin/env python3
"""Operations' advisory budget matches its measured runs, and overbudget_repeat is a rate
(OPERATIONS_RUN_FIX_HALF_A_MILLION_HABIT).

The Dispatcher raised role:Operations:overbudget_repeat on 2026-11-05T03:34Z (rm-role-operations-1793849419: 505k
weighted against 450k). Measured 57 done Operations runs 2026-11-03..05 (D:\\ClaudeWork\\rimmandrake\\dispatcher\\
state.json roles.Operations.runs, weighted; the sample is frozen below): at the old caps 16 ran over, 7 of the 8
incident runs against a 200k cap, so "3 overruns in 7 days" fired every day on a role that runs ~25 times a day.

  B1 the live schedule's Operations caps sit at or above each kind's measured p90 (incident: its max), economy >=
     run, and the daily cap keeps _daily_cap_why's formula (economy + run + 2 alarm runs + 6 incident runs).
  B2 the measured sample replayed at the OLD caps passes OVER_RATE (the alarm was right about the budget), and at
     the LIVE caps stays under it (a run over budget now means a heavy run).
  B3 supervise_roles: 3 overruns among 30 measured runs in the window raise overbudget but NOT overbudget_repeat;
     3 among 10 raise both.
  B4 state written before fin_at existed: the done runs kept on record count as the denominator.
Pure: fake observers."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import role_launch as RL  # noqa: E402

FAILS = []


def check(ok, what):
    print(("ok    " if ok else "FAIL  ") + what)
    if not ok:
        FAILS.append(what)


# weighted tokens of the 57 done Operations runs on record 2026-11-05 (role_launch.run_tokens units)
RUN = [188717, 363452, 309862, 575285, 192389, 323128, 407056, 326966, 153909, 378855, 175539, 277964, 496553,
       660220, 349775, 191851, 505293]
ALARM = [325121, 486138, 229030, 604858, 298941, 246540, 31221, 449043, 422968, 224586, 612643, 236616, 518599,
         355119, 539533, 188409, 175847, 237426, 259425, 226796, 163952, 185977, 303491, 214524, 9847, 222404,
         187152, 159955, 222441, 202763, 151169, 234683]
INCIDENT = [218618, 284858, 250463, 327745, 183568, 300582, 353644, 372145]


def p90(v):
    v = sorted(v)
    return v[min(len(v) - 1, int(0.9 * len(v)))]


def over_rate(run_cap, incident_cap):
    over = sum(t > run_cap for t in RUN + ALARM) + sum(t > incident_cap for t in INCIDENT)
    return over, over / float(len(RUN) + len(ALARM) + len(INCIDENT))


sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
o = {r["name"]: r for r in sch["roles"]}["Operations"]
check(len(RUN) + len(ALARM) + len(INCIDENT) == 57, "sample: 57 measured runs")
check(o["run_token_cap"] >= max(p90(RUN), p90(ALARM)),
      "B1 run_token_cap %d >= run p90 %d and alarm p90 %d" % (o["run_token_cap"], p90(RUN), p90(ALARM)))
check(o["incident_token_cap"] >= max(INCIDENT), "B1 incident_token_cap %d >= incident max %d" % (
    o["incident_token_cap"], max(INCIDENT)))
check(o["economy_token_cap"] >= o["run_token_cap"], "B1 economy cap >= run cap (it carries the running check)")
check(o["daily_token_cap"] >= o["economy_token_cap"] + 3 * o["run_token_cap"] + 6 * o["incident_token_cap"],
      "B1 daily %d fits economy + evening + 2 alarm runs + 6 incident runs" % o["daily_token_cap"])
check(o.get("caps_advisory") is True, "B1 Operations caps stay advisory (owner 2026-11-02)")

n_old, r_old = over_rate(450000, 200000)
n_new, r_new = over_rate(o["run_token_cap"], o["incident_token_cap"])
check(n_old == 16 and r_old >= RL.OVER_RATE, "B2 old caps: %d of 57 over (%.0f%%) >= OVER_RATE %.0f%%" % (
    n_old, 100 * r_old, 100 * RL.OVER_RATE))
check(r_new < RL.OVER_RATE, "B2 live caps: %d of 57 over (%.0f%%) < OVER_RATE" % (n_new, 100 * r_new))

NOW = 1793900000.0


def supervise(fin_n, kept_runs=0):
    st = {"roles": {"Operations": {"done": {}, "over_at": [NOW - 86400, NOW - 3600],
                                   "fin_at": [NOW - 60 * (i + 2) for i in range(fin_n - 1)] if fin_n else None}}}
    if fin_n == 0:
        del st["roles"]["Operations"]["fin_at"]
    runs = [{"state": "done", "unit": "k%d" % i, "at": NOW - 600 * (i + 2), "tokens": 1000, "budget": 450000,
             "mode": "alarm", "item": "I", "seat": "BENCH", "run_max_s": 1800, "day": RL.day_of(NOW)}
            for i in range(kept_runs)]
    runs.append({"state": "running", "unit": "u0", "at": NOW - 60, "mode": "alarm", "budget": 1000, "item": "I",
                 "seat": "BENCH", "run_max_s": 1800, "day": RL.day_of(NOW), "scope": "sc"})
    st["roles"]["Operations"]["runs"] = runs
    acts = []
    ob = {"unit_state": lambda u: "inactive",
          "result": lambda r: {"usage": {"input_tokens": 5000, "cache_creation_input_tokens": 0,
                                         "cache_read_input_tokens": 0, "output_tokens": 0}, "subtype": "success"}}
    cfg = {"name": "Operations", "enabled": True, "caps_advisory": True, "ledger_item": "I"}
    RL.supervise_roles({"roles": [cfg]}, st, ob, NOW, lambda **a: acts.append(a))
    return [a.get("kind") for a in acts if a.get("do") == "alarm"], st


k, st = supervise(30)
check("role:Operations:overbudget" in k and "role:Operations:overbudget_repeat" not in k,
      "B3 3 overruns of 30 measured runs: overbudget only %s" % k)
check(len(st["roles"]["Operations"]["fin_at"]) == 30, "B3 the finished run is stamped in fin_at")
k, _ = supervise(10)
check("role:Operations:overbudget_repeat" in k, "B3 3 overruns of 10 measured runs: overbudget_repeat %s" % k)
k, _ = supervise(0, kept_runs=29)
check("role:Operations:overbudget_repeat" not in k, "B4 no fin_at, 30 done runs on record: no repeat %s" % k)
k, _ = supervise(0)
check("role:Operations:overbudget_repeat" in k, "B4 no fin_at, nothing on record: the count rule stands %s" % k)

print("%d failure(s)" % len(FAILS) if FAILS else "all ok")
sys.exit(1 if FAILS else 0)
