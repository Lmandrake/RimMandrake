#!/usr/bin/env python3
"""fixture_guard_gate.py -- release fixtures for the close gate's guard check (GUARD_GATE_FIX_CURE_IN_THE_TEST).

The instance: NIGHTLY_COP_FIX_RED_ENZRXF_ZBBM's guard was a census selftest (selftest_conductor_authority.py) whose cure IS a
row added to the test's own OWNER_ONLY allowlist, so its committed hash at the fix (7493667ebf) can never equal its hash when
shown red, and `_guard_refusals` refused a green, honest guard.

Each case builds a throwaway git repo with a census guard, shown red, then a second commit, and asks cli._guard_refusals:
  --case cure-in-test  the fix adds the missing allowlist row to the test itself; the gate must accept it
                       -> FIXTURE_VERDICT: PASS, exit 0 (FAIL, exit 1 when the gate refuses it)
  --case still-red     the test grows by a comment but the instance is not cured; the gate must still refuse
                       -> FIXTURE_VERDICT: FAIL, exit 1 (the gate holds) (PASS, exit 0 would mean it let a red guard close)
A setup that cannot build its repo prints no verdict and exits 2.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

TEST = "src/selftest_census_x.py"
RED = ('import os, sys\n'
       'ALLOW = {\n'
       '    "a.py": "reads only",\n'
       '}\n'
       'bad = [f for f in sorted(os.listdir("tools")) if f not in ALLOW]\n'
       'print("FAIL unlisted: %s" % bad if bad else "ok")\n'
       'sys.exit(1 if bad else 0)\n')
CURES = {"cure-in-test": ('    "a.py": "reads only",\n', '    "a.py": "reads only",\n    "b.py": "reads only, authorizes nothing",\n'),
         "still-red": ('ALLOW = {\n', '# b.py still unlisted: this comment cures nothing\nALLOW = {\n')}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True, choices=sorted(CURES))
    case = ap.parse_args().case
    tmp = tempfile.mkdtemp(prefix="fixture_guard_gate_")
    try:
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")

        def git(*a):
            r = subprocess.run(["git", *a], cwd=tmp, env=env, capture_output=True, text=True, stdin=subprocess.DEVNULL)
            if r.returncode:
                print("setup: git %s: %s" % (" ".join(a), r.stderr))
                sys.exit(2)
            return r.stdout.strip()

        def write(path, body):
            full = os.path.join(tmp, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w") as f:
                f.write(body)

        git("init", "-q", "-b", "main")
        write("tools/a.py", "x = 1\n")
        write("tools/b.py", "y = 2\n")      # the instance: a new tool the census has no row for
        write(TEST, RED)
        git("add", "-f", "tools", TEST)
        git("commit", "-q", "-m", "the guard, red on the instance")

        import cli
        import repeat_guard as RG
        rc, out = RG.run(tmp, TEST)
        if RG.red_problem(rc, out):
            print("setup: the guard is not red on the instance: %s" % RG.red_problem(rc, out))
            return 2
        old, new = CURES[case]
        write(TEST, RED.replace(old, new, 1))
        git("add", "-f", TEST)
        git("commit", "-q", "-m", "the fix (%s)" % case)
        sha = git("rev-parse", "HEAD")
        it = types.SimpleNamespace(id="FIXTURE_ITEM", runs=[], guard={"test": TEST, "testHash": RG.digest(RED.encode()), "ts": ""})
        cli.model.ROOT = tmp
        found = cli._guard_refusals(it, sha)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for _, why in found:
        print("gate refused: %s" % why)
    if not found:
        print("gate accepted the guard at %s" % sha[:12])
    print("FIXTURE_VERDICT: %s" % ("FAIL" if found else "PASS"))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
