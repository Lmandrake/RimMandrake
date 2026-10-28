#!/usr/bin/env python3
"""Role token caps measure real cost (ROLE_CAPS_REMEASURE_ON_REAL_RUNS).

The first real Operations run (D:\\ClaudeWork\\rimmandrake\\dispatcher\\roles\\rm-role-operations-1793226998.json:
15 turns, 105 s; input 30, cache_creation 70,789 all 1h, cache_read 1,042,699, output 7,932) was counted at full weight
per token, 1,121,450, against a cap of 80,000 -> a false role:Operations:overbudget. A cache read costs a tenth of an
input token, so the count must weight each usage field by its price class (role_launch.TOKEN_WEIGHTS):
  W1 the measured run weighs 285,538 input-equivalent tokens (30 + 70,789 x 2 + 1,042,699 x 0.1 + 7,932 x 5, rounded up).
  W2 cache writes split by TTL when the result says so (5m x1.25, 1h x2); no split, or a split that does not add up
     to cache_creation_input_tokens, is weighed at the dearer 1h rate (never a guess in the cheap direction).
  W3 a missing / malformed field is still UNMEASURED (None), as before (review Q 8).
  W4 the weights reproduce the price ratios in the two proof records whose cost is known (haiku 1-turn runs): the
     weighted count is proportional to total_cost_usd (one per-token price fits both to 1%).
  W5 every enabled role's per-run caps hold the measured run with headroom, and its daily cap holds its scheduled
     runs at those caps; every cap carries a measured basis next to it (_caps_why naming the record).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import role_launch as RL  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


OPS_RUN = {"input_tokens": 30, "cache_creation_input_tokens": 70789, "cache_read_input_tokens": 1042699,
           "output_tokens": 7932,
           "cache_creation": {"ephemeral_1h_input_tokens": 70789, "ephemeral_5m_input_tokens": 0}}
MEASURED = 285538

# W1
check(RL.run_tokens({"usage": OPS_RUN}) == MEASURED, "W1 the measured Operations run weighs %d (got %r)"
      % (MEASURED, RL.run_tokens({"usage": OPS_RUN})))
check(RL.raw_tokens({"usage": OPS_RUN}) == 1121450, "W1 raw_tokens keeps the unweighted sum (1,121,450) for the record")
# W2
five = dict(OPS_RUN, cache_creation={"ephemeral_1h_input_tokens": 0, "ephemeral_5m_input_tokens": 70789})
check(RL.run_tokens({"usage": five}) == 232447,  # 30 + 88,486.25 + 104,269.9 + 39,660, rounded up
      "W2 an all-5m write weighs x1.25 (got %r)" % RL.run_tokens({"usage": five}))
nosplit = {k: v for k, v in OPS_RUN.items() if k != "cache_creation"}
check(RL.run_tokens({"usage": nosplit}) == MEASURED, "W2 no TTL split -> the 1h rate")
for bad in ({"ephemeral_1h_input_tokens": 1, "ephemeral_5m_input_tokens": 70788 - 5},
            {"ephemeral_5m_input_tokens": -5, "ephemeral_1h_input_tokens": 70794},
            {"ephemeral_5m_input_tokens": "x"}, "junk"):
    check(RL.run_tokens({"usage": dict(OPS_RUN, cache_creation=bad)}) == MEASURED,
          "W2 a split that does not add up (%r) -> the 1h rate" % (bad,))
# W3
for bad in ({}, dict(OPS_RUN, output_tokens=True), dict(OPS_RUN, cache_read_input_tokens=-1),
            dict(OPS_RUN, input_tokens=float("nan")), dict(OPS_RUN, input_tokens=1.5)):
    check(RL.run_tokens({"usage": bad}) is None, "W3 malformed usage -> UNMEASURED")
check(RL.run_tokens(None) is None and RL.run_tokens({}) is None, "W3 no usage block -> UNMEASURED")
# W4: the proof records (haiku, cost known) -- weighted / cost is one price
proofs = [({"input_tokens": 2, "cache_creation_input_tokens": 24009, "cache_read_input_tokens": 11227,
            "output_tokens": 4, "cache_creation": {"ephemeral_1h_input_tokens": 24009, "ephemeral_5m_input_tokens": 0}},
           0.00491627),
          ({"input_tokens": 2, "cache_creation_input_tokens": 52882, "cache_read_input_tokens": 0,
            "output_tokens": 4, "cache_creation": {"ephemeral_1h_input_tokens": 52882, "ephemeral_5m_input_tokens": 0}},
           0.0105786)]
per = [cost / RL.run_tokens({"usage": u}) for u, cost in proofs]
check(abs(per[0] / per[1] - 1) < 0.01, "W4 one per-token price fits both priced proof runs (%r)" % (per,))
# W5: the schedule
sch = json.load(open(os.path.join(HERE, "dispatcher_schedule.json")))
for r in sch["roles"]:
    caps = [r[k] for k in ("run_token_cap", "quick_token_cap", "economy_token_cap") if r.get(k) is not None]
    why = r.get("_caps_why", "")
    check("rm-role-operations-1793226998" in why and "[A]" in why,
          "W5 %s: _caps_why names the measured record and carries [A]" % r["name"])
    check(caps and min(caps) >= int(MEASURED * 1.25), "W5 %s: every per-run cap >= measured x1.25 (%r)" % (r["name"], caps))
    shrunk = min(caps) * min([float(b.get("quick_cap_x", 1.0)) for b in (r.get("throttle_bands") or {}).values()] or [1])
    check(shrunk >= MEASURED * 1.15, "W5 %s: the band-shrunk cap %d holds the measured run with >= 15%% to spare"
          % (r["name"], shrunk))
    import time as _t
    days = [_t.mktime((2026, 10, 26 + d, 12, 0, 0, 0, 0, -1)) for d in range(7)]       # Mon..Sun
    need = max(sum(c for _, _, c in RL.slots(r, d) if c) for d in days)
    check(r.get("daily_token_cap", 0) >= need,
          "W5 %s: daily cap %r holds the busiest day's scheduled runs (%d)" % (r["name"], r.get("daily_token_cap"), need))

print("%d failure(s)" % len(FAILS))
sys.exit(1 if FAILS else 0)
