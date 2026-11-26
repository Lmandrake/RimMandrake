#!/usr/bin/env python3
"""selftest_stage_ceiling_tokens.py — the stage ceiling counts weighted_v2 tokens, never the CLI's list dollars
(RIMMANDRAKE_KEEP_STAGE_CEILING_IN_TOKENS_NOT_LIST_DOLLARS).

The defect: a Fable 5.2 run whose CLI cost_usd was priced at Opus 5.5 rates (costBasis "unknown") counted at half its
weight, because the ceiling summed cost_usd. Its run record's `tokens` (weighted_v2) is the true figure.

The path read here is the real one: run records -> maturation_now.run_view (the status page's run views) ->
maturation_dispatch.gather (box_runs, run spend) -> stage_spent -> ceiling_gate (stage_spend through the control
store). Only the page's own gather and the mod's build facts are stood in, each from the records below.

  python3 selftest_stage_ceiling_tokens.py      # prints ALL PASS and exits 0, else names each FAIL and exits 1
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
_T = tempfile.mkdtemp(prefix="stage_ceiling_tokens_")
os.environ["RM_PIPE_CONTROL_DIR"] = os.path.join(_T, "control")        # an empty control store of its own
os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(_T, "dispatch")
os.environ["RM_RUN_VOIDS_FILE"] = os.path.join(_T, "voids.jsonl")       # no live hand voids (run_void.active)
os.makedirs(os.environ["RM_PIPE_CONTROL_DIR"], exist_ok=True)
os.makedirs(os.environ["RM_MATURATION_DISPATCH_DIR"], exist_ok=True)

import maturation_dispatch as MD  # noqa: E402
import maturation as M  # noqa: E402
import maturation_now as MN  # noqa: E402
import role_launch as RL  # noqa: E402

FAILS = []
CASES = [0]


def check(ok, what, worst=None, limit=None):
    CASES[0] += 1
    tail = "" if worst is None else "  (read %r, bar %r)" % (worst, limit)
    print(("ok    " if ok else "FAIL  ") + what + tail)
    if not ok:
        FAILS.append(what)


def guarded(name, fn):
    try:
        fn()
    except Exception as e:  # noqa: BLE001  a missing name on the old code is a FAIL, never a crash of the test
        check(False, "%s raised %s: %s" % (name, type(e).__name__, e))


MOD = "TokenMod"
NOW = 1_800_000_000.0
# a Fable 5.2 run: its true weight is 10,000,000 weighted_v2 tokens (= 40 list dollars at Opus input rates, the
# reference model); the CLI priced it at Opus rates, 20.00, half of it (Fable 5.2 input is 8 $/MTok, Opus 5.5 is 4)
FABLE_TOKENS, FABLE_OPUS_RATE_USD = 10_000_000, 20.0
LEGACY_USD = 4.0            # an old run with measured list dollars and no weighted_v2 tokens -> 1,000,000
CAP_USD = 15.0              # a run with neither: counted at its launch cap (budget_usd, dollars) -> 3,750,000
RECORDS = [
    {"unit": "rm-fable", "item": "RIMMANDRAKE_X_FABLE", "model": "claude-fable-5-2", "at": NOW - 5000,
     "ended": NOW - 4000, "status": "finished", "result": "success", "tokens": FABLE_TOKENS,
     "token_unit": "weighted_v2", "cost_usd": FABLE_OPUS_RATE_USD, "costBasis": "unknown", "budget_usd": 150},
    {"unit": "rm-legacy", "item": "RIMMANDRAKE_X_LEGACY", "model": "claude-opus-5-5", "at": NOW - 3900,
     "ended": NOW - 3000, "status": "finished", "result": "success", "cost_usd": LEGACY_USD, "budget_usd": 150},
    {"unit": "rm-nothing", "item": "RIMMANDRAKE_X_NOTHING", "model": "claude-opus-5-5", "at": NOW - 2900,
     "ended": NOW - 2000, "status": "finished", "result": "success", "cost_usd": "UNMEASURED", "budget_usd": CAP_USD},
]
WANT = FABLE_TOKENS + 1_000_000 + 3_750_000


def stand_in():
    views = [MN.run_view(r, NOW) for r in RECORDS]
    MN.gather = lambda root, live=True: {"mods": [{"name": MOD, "runs": views, "boxes": {"3": {"runs": views}}}]}
    M.build_facts = lambda root, mod: {"mod": mod, "stage": "offline_build"}
    M.load = lambda root, mod: {"stage": "offline_build", "moves": []}
    MD.killed_runs = lambda runs, *a, **k: {}
    MD.lane_on_mod_files = lambda unit, mod, *a, **k: None


def t_run_records_to_stage_spend():
    stand_in()
    f = MD.gather("/nonexistent", {"advancing": [MOD]}, live=False)[MOD]
    got = MD.stage_spent(f, "offline_build", [])
    check(got == WANT and isinstance(got, int), "stage_spent counts the Fable run's weighted_v2 tokens, a legacy "
          "run's list dollars converted once, and a run with neither at its cap", got, WANT)
    fable = (f.get("box_runs") or {}).get("3", {}).get("rm-fable")
    check(fable == FABLE_TOKENS, "the Fable run counts its tokens, not its Opus-rate cost_usd", fable, FABLE_TOKENS)
    # the gate: 14.75M spent plus a 12.5M cap passes a 25M ceiling; a legacy dollar release of 10 (2.5M) lifts it
    cfg = {"stage_ceiling_tokens": 25_000_000}
    over, rid = MD.ceiling_gate(cfg, {}, MOD, "offline_build", got, 12_500_000, "Stage 3", ([], 0))
    check(bool(over) and rid is None and "weighted tokens" in over, "the ceiling stops 14.75M + a 12.5M cap at 25M",
          over, "a stop")
    check("--read-tokens 14750000 --tokens 2250000" in (over or ""), "the stop's release command reads tokens",
          over, "--read-tokens 14750000 --tokens 2250000")
    rel = {"id": "rel-legacy", "ts": "2026-11-20T00:00:00Z", "mod": MOD, "stage": "offline_build", "by": "BENCH",
           "why": "a legacy dollar release", "read_usd": 59.0, "release_usd": 10.0}
    path = os.path.join(_T, "releases.jsonl")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(rel) + "\n")
    recs, bad = MD.read_releases(path)
    check(bad == 0 and len(recs) == 1, "a legacy read_usd/release_usd release is read, not counted malformed",
          (len(recs), bad), (1, 0))
    r0 = recs[0] if recs else {}
    check(r0.get("read_tokens") == 14_750_000 and r0.get("release_tokens") == 2_500_000,
          "the legacy release converts through role_launch to tokens",
          (r0.get("read_tokens"), r0.get("release_tokens")), (14_750_000, 2_500_000))
    over, rid = MD.ceiling_gate(cfg, {}, MOD, "offline_build", got, 12_500_000, "Stage 3", (recs, bad))
    check(over is None and rid == "rel-legacy", "the legacy release lifts the ceiling once", (over, rid),
          (None, "rel-legacy"))


def t_one_rate():
    per = RL.list_usd_to_weighted(1)
    check(per == 250_000 and isinstance(per, int), "one list dollar is 250,000 weighted_v2 tokens", per, 250_000)
    check(per == 1_000_000 / RL.MODEL_PRICES[RL.REF_MODEL]["input_tokens"], "the rate is the reference model's input "
          "price", per, 1_000_000 / RL.MODEL_PRICES[RL.REF_MODEL]["input_tokens"])
    back = RL.weighted_to_list_usd(37_500_000)
    check(back == 150.0, "the launch boundary turns a 37.5M cap back into 150 list dollars", back, 150.0)


def t_settings_in_tokens():
    with open(os.path.join(HERE, "maturation_dispatch.json"), encoding="utf-8") as fh:
        c = json.load(fh)
    usd = [k for k in c if "usd" in k.lower() and not k.startswith("_")]
    check(not usd, "maturation_dispatch.json has no non-underscore usd key", usd, [])
    want = {"cap_tokens": 37_500_000, "stage_ceiling_tokens": 250_000_000, "blind_cap_tokens": 50_000_000,
            "ingame_cap_tokens": 75_000_000, "steward_cap_tokens": 20_000_000, "fix_cap_tokens": 25_000_000}
    got = {k: c.get(k) for k in want}
    check(got == want, "the six caps are weighted tokens", got, want)
    check(not any(hasattr(MD, n) for n in ("WT_PER_USD", "to_wt", "from_wt")),
          "maturation_dispatch keeps no dollar converter of its own",
          [n for n in ("WT_PER_USD", "to_wt", "from_wt") if hasattr(MD, n)], [])


for name, fn in (("t_run_records_to_stage_spend", t_run_records_to_stage_spend), ("t_one_rate", t_one_rate),
                 ("t_settings_in_tokens", t_settings_in_tokens)):
    guarded(name, fn)
print("%d case(s) read, %d failed" % (CASES[0], len(FAILS)))
if FAILS:
    print("FAILED: %d" % len(FAILS))
    sys.exit(1)
print("ALL PASS")
