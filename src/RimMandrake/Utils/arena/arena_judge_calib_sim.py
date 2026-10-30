#!/usr/bin/env python3
"""arena_judge_calib_sim.py — re-run testpilot_sim with the critic AND judge rates measured on the frozen mutant set.

Item ARENA_JUDGE_RATES_MEASURE_PLANTED (the owed "simulator re-run with the measured rates" of
ARENA_CRITIC_MEASURE_PLANTED_DEFECTS_FIRST). The sim is not edited: scenarios are injected at runtime, as the
critic's own re-run did (D:\\ClaudeWork\\rimmandrake\\arena_critic\\sim\\run_sim.py).

    python3 src/RimMandrake/Utils/arena/arena_judge_calib_sim.py ensemble --scenario S --out DIR [--budget-s 480]
    python3 src/RimMandrake/Utils/arena/arena_judge_calib_sim.py report --scenario S --out DIR

The sim has ONE blind-review gate (crit_s = sensitivity per round, crit_fr = false reject on a small item); a member
draws each uniformly from its range. Ranges here are EXACT Clopper-Pearson 95% intervals (never bootstrap):
  critic_tierA   BEFORE: the critic's earlier re-run, l4-main Wilson ranges copied verbatim (old real-defect set)
  critic_mut     the L4 critic (baseline run mut2-l4) on the mutant set b54d2e85     } read from the judge score.json,
  judge_gate     the arena judge (run judge-1) as that SAME single gate, same set    } refused unless MEASURED
crit_fr_big (large items) keeps its assumed prior: neither reviewer was measured on large items.
STATED LIMITS of the mapping: each scenario REPLACES the one gate (critic then judge in series is not modelled);
crit_s is the reason-matched catch, which counts a wrong-reason reject as a miss although a real gate still blocks
it (conservative), and pools test- and read-detectable mutants (upstream tests might remove the test class);
tier-A FR is transferred to the sim's small-item population; drawing uniformly between CP bounds is a modelling
choice, not a posterior.
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "sim"))
sys.path.insert(0, str(HERE))
import testpilot_sim as T  # noqa: E402

SCORE = Path(os.environ.get("RM_JUDGE_CALIB_SCORE",
                            "/mnt/d/ClaudeWork/rimmandrake/arena/calibration/judge/judge-1/score.json"))
SET_SHA = "b54d2e850bf6"


def measured(sc: dict, block: str, key: str) -> tuple:
    """(k, n) of a MEASURED rate; refuses (never a number) when the score says UNMEASURED."""
    r = sc[block][key]
    if r.get("status") != "MEASURED" or not r.get("n"):
        raise SystemExit("%s.%s is %s (%s): no simulator input" % (block, key, r.get("status"), r.get("why")))
    return r["k"], r["n"]


def from_score(path: Path = SCORE) -> dict:
    """Scenario priors derived from the validated score artifact: exact CP 95% bounds recomputed from its counts."""
    import arena_critic_mutants as M
    sc = json.loads(path.read_text())
    if not str(sc.get("set_sha256", "")).startswith(SET_SHA):
        raise SystemExit("score %s is on set %s, not %s" % (path, sc.get("set_sha256"), SET_SHA))

    def gate(block):
        fk, fn = measured(sc, block, "false_reject_tierA")
        mk, mn = measured(sc, block, "miss_reason")
        lo, hi = M.cp(mk, mn)
        return {"priors": {"crit_fr": M.cp(fk, fn), "crit_s": (1 - hi, 1 - lo)},
                "source": "%s run %s: FR %d/%d, reason miss %d/%d" % (block, sc[block]["run"], fk, fn, mk, mn)}
    return {"critic_mut": gate("baseline_rates"), "judge_gate": gate("judge")}


SCEN = {"critic_tierA": {"priors": {"crit_fr": (0.0632, 0.5474), "crit_s": (1 - 0.9801, 1 - 0.565)}}}

if __name__ == "__main__":
    SCEN.update(from_score())
    for k, v in SCEN.items():
        print("scenario %s: %s %s" % (k, {p: tuple(round(x, 4) for x in r) for p, r in v["priors"].items()},
                                      v.get("source", "l4-main Wilson (before)")), file=sys.stderr)
    T.SCENARIOS.update({k: {"priors": v["priors"]} for k, v in SCEN.items()})
    sys.exit(T.main(sys.argv[1:]))
