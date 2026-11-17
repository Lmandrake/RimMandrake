#!/usr/bin/env python3
"""Operations' advisory budget matches its measured runs, and overbudget_repeat is a rate
(OPERATIONS_RUN_FIX_HALF_A_MILLION_HABIT).

The Dispatcher raised role:Operations:overbudget_repeat on 2026-11-05T03:34Z (rm-role-operations-1793849419: 505k
weighted against 450k). Measured 57 done Operations runs 2026-11-03..05 (D:\\ClaudeWork\\rimmandrake\\dispatcher\\
state.json roles.Operations.runs, weighted; the sample is frozen below): at the old caps 16 ran over, 7 of the 8
incident runs against a 200k cap, so "3 overruns in 7 days" fired every day on a role that runs ~25 times a day.

  The sample was measured in weighted_v1 (each model's tokens relative to its own input token). The live caps are
  weighted_v2 (RIMMANDRAKE_WEIGH_TOKENS_BY_MODEL_OPUS_INPUT_UNIT: list price / the Opus 5.5 input price), so the same
  57 runs are re-measured in v2 from their own result files (D:\\ClaudeWork\\rimmandrake\\dispatcher\\roles\\
  rm-role-operations-*.json, matched on their v1 figure, 57 of 57; 40 Opus 5.5, 17 Sonnet 5.5; the script is
  D:\\ClaudeWork\\rimmandrake\\weighted_v2\\scripts\\ops_sample_v2.py). v2 reads modelUsage, the whole process with its
  subagents, so a run can weigh more in v2 than its main thread did in v1.
  B1 the live schedule's Operations caps (v2) sit at or above each kind's measured v2 p90 (incident: its max),
     economy >= run, and the daily cap keeps _daily_cap_why's formula (economy + run + 2 alarm runs + 6 incident runs).
  B2 the v1 sample replayed at the OLD v1 caps passes OVER_RATE (the alarm was right about the budget), and the v2
     sample at the LIVE caps stays under it (a run over budget now means a heavy run).
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


# weighted_v1 tokens of the 57 done Operations runs on record 2026-11-05 (role_launch.run_tokens as it was then)
RUN_V1 = [188717, 363452, 309862, 575285, 192389, 323128, 407056, 326966, 153909, 378855, 175539, 277964, 496553,
       660220, 349775, 191851, 505293]
ALARM_V1 = [325121, 486138, 229030, 604858, 298941, 246540, 31221, 449043, 422968, 224586, 612643, 236616, 518599,
         355119, 539533, 188409, 175847, 237426, 259425, 226796, 163952, 185977, 303491, 214524, 9847, 222404,
         187152, 159955, 222441, 202763, 151169, 234683]
INCIDENT_V1 = [218618, 284858, 250463, 327745, 183568, 300582, 353644, 372145]
# the same runs, same order, in weighted_v2 (role_launch.run_tokens on each result file's modelUsage, 2026-11-16)
RUN = [163759, 274961, 242255, 407577, 164195, 249665, 300997, 254626, 137311, 289424, 151663, 215640, 417889, 524582,
       299539, 169820, 386074]
ALARM = [249932, 347316, 194566, 451834, 236635, 205250, 289098, 341048, 318175, 187482, 427651, 624636, 428740,
         303239, 393737, 79489, 73827, 96012, 103365, 89402, 70702, 79258, 120807, 88551, 90824, 91838, 78963, 71572,
         91223, 85770, 66067, 97611]
INCIDENT = [180492, 218142, 209384, 256630, 157662, 233282, 308173, 279894]


def p90(v):
    v = sorted(v)
    return v[min(len(v) - 1, int(0.9 * len(v)))]


def over_rate(run_cap, incident_cap, run=None, alarm=None, incident=None):
    run, alarm, incident = run or RUN, alarm or ALARM, incident or INCIDENT
    over = sum(t > run_cap for t in run + alarm) + sum(t > incident_cap for t in incident)
    return over, over / float(len(run) + len(alarm) + len(incident))


sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
o = {r["name"]: r for r in sch["roles"]}["Operations"]
check(len(RUN) + len(ALARM) + len(INCIDENT) == 57 and [len(RUN), len(ALARM), len(INCIDENT)] == [
    len(RUN_V1), len(ALARM_V1), len(INCIDENT_V1)], "sample: 57 measured runs, in v1 and v2")
check(o["run_token_cap"] >= max(p90(RUN), p90(ALARM)),
      "B1 run_token_cap %d >= v2 run p90 %d and alarm p90 %d (n %d, %d; margin %.1f%%)" % (
          o["run_token_cap"], p90(RUN), p90(ALARM), len(RUN), len(ALARM),
          100.0 * (o["run_token_cap"] / max(p90(RUN), p90(ALARM)) - 1)))
check(o["incident_token_cap"] >= max(INCIDENT), "B1 incident_token_cap %d >= v2 incident max %d (n %d; margin %.1f%%)"
      % (o["incident_token_cap"], max(INCIDENT), len(INCIDENT), 100.0 * (o["incident_token_cap"] / max(INCIDENT) - 1)))
check(o["economy_token_cap"] >= o["run_token_cap"], "B1 economy cap >= run cap (it carries the running check)")
check(o["daily_token_cap"] >= o["economy_token_cap"] + 3 * o["run_token_cap"] + 6 * o["incident_token_cap"],
      "B1 daily %d fits economy + evening + 2 alarm runs + 6 incident runs" % o["daily_token_cap"])
check(o.get("caps_advisory") is True, "B1 Operations caps stay advisory (owner 2026-11-02)")

n_old, r_old = over_rate(450000, 200000, RUN_V1, ALARM_V1, INCIDENT_V1)   # the v1 caps of 2026-11-05
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
                                         "cache_read_input_tokens": 0, "output_tokens": 0}, "subtype": "success",
                               "modelUsage": {"claude-opus-5-5": {"inputTokens": 5000, "outputTokens": 0,
                                                                  "cacheReadInputTokens": 0,
                                                                  "cacheCreationInputTokens": 0}}}}
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
