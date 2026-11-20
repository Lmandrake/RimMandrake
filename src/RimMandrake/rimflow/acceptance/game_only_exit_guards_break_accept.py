#!/usr/bin/env python3
"""Planted faults for design/specs/2026-11-19-maturation-game-only-blind-exit/boundary.md: each fault breaks one promise
in a temp copy of src/RimMandrake/rimflow, and that promise's test in selftest_maturation_game_only_exit.py must go red
(item RIMMANDRAKE_UNBLOCK_GAME_ONLY_ADVANCE_AT_BLIND_EXIT). The live tree is never written. Run from the repo root.
Prints `PASS N/N` when every fault is caught and the unplanted copy stays green; exits 1 otherwise."""
import os
import shutil
import subprocess
import sys
import tempfile

SRC = "src/RimMandrake/rimflow"
TEST = "selftest_maturation_game_only_exit.py"
# (promise test, old text, planted text)
FAULTS = [
    ("t_unfixed_problem_still_refuses",
     "if fixed and game_only_bars is not None and all(w == JUDGE_SAYS_FALSE for w in why):",
     "if fixed and game_only_bars is not None and all(w == JUDGE_SAYS_FALSE or 'not FIXED' in w for w in why):"),
    ("t_offline_row_without_named_item_still_refuses",
     "(at[b] not in OFFLINE_PROVES or bool((named or {}).get(b)))",
     "(at[b] not in OFFLINE_PROVES or bool(named))"),
    ("t_not_game_only_move_unchanged",
     "if fixed and game_only_bars is not None and all(",
     "if fixed and all("),
    ("t_owed_judge_from_other_cause_still_refuses",
     "if fixed and game_only_bars is not None and all(",
     "if game_only_bars is not None and all("),
    ("t_evaluate_gives_bars_only_when_game_only_passes",
     "        if go_ok:\n            go_bars = bars_named_by(root, mod, ids)",
     "        if ids:\n            go_bars = bars_named_by(root, mod, ids)"),
    ("t_game_only_exit_skips_owed_judge_and_named_rows",
     "                ex = read_exit(root, mod, n, tt, game_only_bars=game_only_bars)",
     "                ex = read_exit(root, mod, n, tt)"),
]


def run(body, test=None):
    d = tempfile.mkdtemp(prefix="goexit_plant_")
    try:
        dst = os.path.join(d, SRC)      # the same depth: maturation.py finds Utils at ../Utils from its own folder
        shutil.copytree(SRC, dst, ignore=shutil.ignore_patterns("__pycache__", "acceptance"))
        os.symlink(os.path.abspath("src/RimMandrake/Utils"), os.path.join(os.path.dirname(dst), "Utils"))
        if body is not None:
            with open(os.path.join(dst, "maturation.py"), "w", encoding="utf-8") as f:
                f.write(body)
        argv = [sys.executable, os.path.join(dst, TEST)] + (["--only", test] if test else [])
        r = subprocess.run(argv, capture_output=True, text=True, timeout=300)
        return r.returncode
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    with open(os.path.join(SRC, "maturation.py"), encoding="utf-8") as f:
        good = f.read()
    ok, n = 0, len(FAULTS) + 1
    rc = run(None)
    print("%s  unplanted copy stays green (rc %s)" % ("PASS" if rc == 0 else "FAIL", rc))
    ok += rc == 0
    for test, old, new in FAULTS:
        if good.count(old) != 1:
            print("FAIL  %s: the planted text is not found once in maturation.py (%d)" % (test, good.count(old)))
            continue
        rc = run(good.replace(old, new), test)
        print("%s  %s goes red on its fault (rc %s)" % ("PASS" if rc != 0 else "FAIL", test, rc))
        ok += rc != 0
    print("PASS %d/%d" % (ok, n) if ok == n else "FAIL %d/%d" % (ok, n))
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
