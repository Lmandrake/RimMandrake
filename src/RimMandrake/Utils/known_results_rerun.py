#!/usr/bin/env python3
"""Does the known-result ledger answer a real rerun of unchanged tests? Exit 0 yes, 1 no, 2 could not look.

The outcome check of RIMMANDRAKE_KEY_TESTQ_SKIP_CACHE_ON_INPUTS. It runs a fixed sample of real selftests twice, back to
back, on a fresh private ledger. Nothing changes between the two runs, so every test that the second run runs again had
only the instrument's reasons to run. The check holds when the second run answers at least BAR of the sample.

The sample is every STRIDE-th test of pipeline_tests.json (the tests ./publish runs, so the reruns that happen most).
It is a stride over the list, never a hand-picked set of tests known to cache.

Measured 2026-11-26 on SteveDesktop, 39 tests (stride 6): 5 of 39 answered before the fix (all 34 refusals carried the
wall-clock rule), 18 of 39 after it; at the default stride 12, 2 of 20 before and 7 of 20 after. The rest read live
state that really is not cacheable: the D: dispatcher folder, the game's folders, /proc, git, the network.

  python3 src/RimMandrake/Utils/known_results_rerun.py [--stride N] [--bar F] [--keep]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUNNER = HERE / "run_selftests.py"
PIPELINE_TESTS = HERE / "pipeline_tests.json"
STRIDE = 12             # about 20 tests: two runs fit well inside list_effect's 600 s cmd deadline
BAR = 1 / 4             # stride 12, 2026-11-26: 2 of 20 answered before the fix, 7 of 20 after it. A quarter (5) lies
                        # between the two with room on both sides for a test that a busy machine refuses once
RUN_DEADLINE_S = 270    # a hang guard per run (two runs < list_effect's 600 s), far above the 60 s a run takes
LINE = re.compile(r"known results: (\d+)/(\d+) answered")


def sample(stride: int) -> list:
    tests = [t.get("test") for t in json.loads(PIPELINE_TESTS.read_text())["tests"]]
    return [t for t in tests[::stride] if t and (REPO / t).is_file()]


def run(tests: list, state: Path):
    env = dict(os.environ, RM_SELFTEST_STATE_DIR=str(state))
    p = subprocess.run([sys.executable, str(RUNNER), "--only", *tests], cwd=REPO, env=env, capture_output=True,
                       text=True, errors="replace", timeout=RUN_DEADLINE_S, stdin=subprocess.DEVNULL)
    m = LINE.search(p.stdout)
    return (int(m.group(1)), int(m.group(2))) if m else None, p


def refusals(state: Path) -> dict:
    out = {}
    f = state / "known_results" / "refusals.jsonl"
    if f.is_file():
        for ln in f.read_text().splitlines():
            r = json.loads(ln)
            out[r["test"]] = r["why"][:3]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stride", type=int, default=STRIDE)
    ap.add_argument("--bar", type=float, default=BAR)
    ap.add_argument("--keep", action="store_true", help="keep the private ledger and print its path")
    a = ap.parse_args(argv)
    tests = sample(a.stride)
    if not tests:
        print("UNMEASURED: no sample (pipeline_tests.json names no test file that exists)")
        return 2
    # The ledger must live on a local disk: /mnt is outside what the tracer can follow, and the runner's own default
    # state stays untouched so this check never seeds or reads the ledger of real runs.
    base = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state")
    base.mkdir(parents=True, exist_ok=True)
    state = Path(tempfile.mkdtemp(prefix="known-results-rerun-", dir=base))
    try:
        try:
            first, p1 = run(tests, state)
            second, p2 = run(tests, state)
        except subprocess.TimeoutExpired:
            print(f"UNMEASURED: a run passed its {RUN_DEADLINE_S}s hang guard")
            return 2
        if first is None or second is None:
            print("UNMEASURED: the runner printed no 'known results' line (no shim, no ledger?)")
            print((p2 if first else p1).stdout[-1500:])   # cut-ok: the tail of the runner says why, on the console only
            return 2
        answered, total = second
        why = refusals(state)
        print(f"rerun of {total} unchanged tests (every {a.stride}th pipeline test): {answered} answered from the ledger;"
              f" bar {a.bar:.2f} of {total} = {a.bar * total:.1f}")
        for t, w in sorted(why.items()):
            print(f"  runs again: {t}: {'; '.join(w)[:160]}")   # cut-ok: a report line
        ok = answered >= a.bar * total and answered > 0
        print("HOLDS" if ok else "FAILS")
        return 0 if ok else 1
    finally:
        if a.keep:
            print(f"ledger kept: {state}")
        else:
            shutil.rmtree(state, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
