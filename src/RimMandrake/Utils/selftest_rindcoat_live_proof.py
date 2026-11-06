#!/usr/bin/env python3
"""RINDCOAT_TUNE_NEAR_IMMUNE_AFTER_ALL live clause A1, offline: the proof line is one the live round will run, and the
verdict it reaches (prove_rindcoat_scald_live.decide) goes red on every way the clause can break.

The line: infrastructure/state/live_proofs/RINDCOAT_TUNE_NEAR_IMMUNE_AFTER_ALL.txt must hold exactly one `live-proof A1:`
that relentless_live.refused_proof accepts (no `$`, no shell loop, no game mutation) and that runs this proof. The
previous line (a `for i in $(seq ...)` poll loop) is planted and must be refused.

The verdict: synthetic two-day sample logs under held steam, at the clock's real rates (read from RM_ScaldExposure.xml),
the coat at the 8% floor -> PASS; and each planted defect -> red: the reversed 0.4x rung, an unprotected coat, a zeroed
clock, the wearer dead, the run short of two days (UNMEASURED), steam not held, and a clock def whose floor moved.

    python3 src/RimMandrake/Utils/selftest_rindcoat_live_proof.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "TerminalBiomes"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
import prove_rindcoat_scald_live as P  # noqa: E402
import relentless_live as RL  # noqa: E402
import json  # noqa: E402

ITEM = "RINDCOAT_TUNE_NEAR_IMMUNE_AFTER_ALL"
LINES = os.path.join(REPO, "infrastructure", "state", "live_proofs", ITEM + ".txt")
OLD = ("mkdir -p /tmp/x && python.exe src/RimMandrake/TerminalBiomes/proof_scald_steam.py setup; for i in $(seq 1 20); "
       "do python.exe src/RimMandrake/TerminalBiomes/proof_scald_steam.py run D:/x/run.json; done")
FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def run_log(factor, up, down, days=2.0, steam=True, rind_dies_at=None, step=3000):
    """A sampled run: the rind wearer's exposure integrates the clock at `factor`, as the hediff comp does."""
    log, died, sev, t = [], {}, 0.0, 0
    end = int(days * P.DAY) + 500
    while t <= end:
        w = "RM_ScaldSteam" if steam else "Clear"
        dead = rind_dies_at is not None and t >= rind_dies_at
        if dead:
            died.setdefault("rind", t)
        log.append({"tick": t, "weather": w,
                    "rind": {"dead": True, "hediffs": []} if dead else
                    {"hediffs": [["RM_ScaldExposure", round(sev, 4)]] if sev > 0 else []}})
        sev = max(0.0, sev + step / P.DAY * (up * factor if steam else down))
        t += step
    return {"log": log, "died": died, "verdict": {}}


def main():
    up, down, floor = P.clock()
    ok(abs(floor - 0.08) < 1e-9, "clock def floor is 0.08 (read %s)" % floor)
    ok(up > 0 and down < 0, "clock rates read: +%s/day exposed, %s/day unexposed" % (up, down))

    code, line = P.decide(run_log(floor, up, down), up, down, floor)
    ok(code == 0, "coat at the 8%% floor, two steam days -> PASS (%s)" % line)
    for name, d, want in (
            ("reversed 0.4x rung", run_log(0.4, up, down), 1),
            ("unprotected coat (1.0x)", run_log(1.0, up, down), 1),
            ("coat at 0.15x (floor missed)", run_log(0.15, up, down), 1),
            ("clock zeroed (Ban 3)", run_log(0.0, up, down), 1),
            ("rind wearer dies at 1.5 days", run_log(floor, up, down, rind_dies_at=90000), 1),
            ("run stopped at 1 day", run_log(floor, up, down, days=1.0), 2),
            ("steam never held", run_log(floor, up, down, steam=False), 1)):
        code, line = P.decide(d, up, down, floor)
        ok(code == want, "planted %s -> exit %d (got %d: %s)" % (name, want, code, line))
    code, line = P.decide(run_log(0.4, up, down), up, down, 0.4)
    ok(code == 1, "planted clock floor moved to 0.4 (replay moves with it) -> FAIL (got %d: %s)" % (code, line))

    lr = RL.live_rules(json.load(open(RL.RULES)))
    proofs = [m.group(1).strip() for m in re.finditer(r"^live-proof A1:(.*)$", open(LINES).read(), re.M)]
    ok(len(proofs) == 1, "exactly one live-proof A1 line (found %d)" % len(proofs))
    if proofs:
        why = RL.refused_proof(lr, ITEM, "rind coat exposure under held steam", proofs[0])
        ok(why is None, "the A1 line passes the live round's refusal gate (%s)" % why)
        ok("prove_rindcoat_scald_live.py" in proofs[0], "the A1 line runs prove_rindcoat_scald_live.py")
        ok(RL.proof_budget(proofs[0], lr["proof_max_s"]) >= 2400, "the A1 line asks the round for its 2400 s budget")
    ok(RL.refused_proof(lr, ITEM, "rind coat", OLD) is not None, "planted the old $(seq) poll-loop line -> refused")

    print("PASS" if not FAILS else "FAIL: %d" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
