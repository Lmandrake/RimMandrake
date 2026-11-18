#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_RECHECK_ADVANCE_CALIBRATION_TEST_PASSES_WITHOUT_ROW.

13db68e8ed made maturation advance refusals count by adding families.maturation_advance to
infrastructure/state/judge_calibration.json; its own close says "what must stay true is the maturation_advance row
reading CALIBRATED". Nothing checks that: selftest_maturation.py --submit builds its own registry, and no timer runs
`refusal_contract.py calibrate`. Measured 2026-11-18 on c32e228e91: with the row deleted, --submit reads ALL PASS, and
the row's brief is maturation.py itself, so the next edit to maturation.py makes status() UNTESTED and every advance
refusal silently advisory again.

Passes when the pipeline door for a maturation.py change (publish.pipeline_selection) goes RED with
RM_JUDGE_CALIBRATION pointing at a copy of the registry WITHOUT the row, and stays GREEN with the real registry (so a
fix that turns the door red for everything does not pass).

    python3 src/RimMandrake/rimflow/acceptance/advance_calibration_bound_accept.py     exit 0 = pass, 1 = fail

Expected on a correct result: `PASS the door refuses a maturation.py change once maturation_advance is not CALIBRATED`.
~2 min (two door runs). The builder does not edit this file.
"""
import concurrent.futures
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
import publish as P  # noqa: E402

REG = os.path.join(ROOT, "infrastructure", "state", "judge_calibration.json")
cfg = json.load(open(os.path.join(ROOT, P.PIPELINE_TESTS), encoding="utf-8"))
sel = [c["test"] for c in P.pipeline_selection(ROOT, ["src/RimMandrake/rimflow/maturation.py"], cfg)]


def door(reg):
    env = {k: v for k, v in os.environ.items() if k not in P.LEDGER_IDENTITY}
    env["RM_JUDGE_CALIBRATION"] = reg

    def one(t):
        try:
            return t, subprocess.run([sys.executable, os.path.join(ROOT, t)], cwd=ROOT, capture_output=True, text=True,
                                     timeout=int(cfg.get("timeout_s", 180)), stdin=subprocess.DEVNULL, env=env).returncode
        except subprocess.TimeoutExpired:
            return t, None
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(one, sel))
    return [t for t, rc in res if rc not in (0, None)], [t for t, rc in res if rc is None]


with tempfile.TemporaryDirectory() as tmp:
    reg = json.load(open(REG, encoding="utf-8"))
    reg["families"].pop("maturation_advance", None)
    cut = os.path.join(tmp, "judge_calibration.json")
    json.dump(reg, open(cut, "w", encoding="utf-8"), indent=1)
    red_cut, slow_cut = door(cut)
    red_real, slow_real = door(REG)
print("%d door tests for a maturation.py change; without the row: %d red %s; real registry: %d red %s%s" % (
    len(sel), len(red_cut), red_cut[:3], len(red_real), red_real[:3],
    "; timed out: %s" % (slow_cut + slow_real) if slow_cut or slow_real else ""))
if red_real:
    print("UNMEASURED: the door is red with the real registry too, so this cannot tell the row's absence apart")
    sys.exit(2)
ok = bool(red_cut)
print("PASS the door refuses a maturation.py change once maturation_advance is not CALIBRATED" if ok else
      "FAIL the door stays green with maturation_advance gone from the registry")
sys.exit(0 if ok else 1)
