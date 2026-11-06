#!/usr/bin/env python3
"""selftest_relentless_seed_compare.py - the relentless_seed_compare offbox adapter (CHECKER_REACH_FIX_SEEDS_STILL_DARK).

RA_S03_WALL_MEASURE_DID_IT_HELP's proof (prove_relentless_s03_compare.py) reads the evaluation seeds, which the Marker's wall
keeps dark on purpose (they hold the E1 answer key). The adapter runs that proof outside the wall at the candidate sha and
lets only check-row lines cross. Rows (each runs the adapter as the supervisor does: offbox_readings -> run_bounded):
  (1) the adapter exists, covers the seeds path, fills only {repo} and {sha};
  (2) on a fixture repo whose stub proof prints a planted key line, a stderr line and a reason line: only ok/FAIL/RESULT/
      UNMEASURED/E1 keys lines cross, exit 0, the trailer names the sha;
  (3) a doc mutant (a changed number in the step 3 section) reads exit 1 with its FAIL row;
  (4) a sha without the proof, or without the TRUST doc, reads exit 2 'NOT RUN'; a stale export is swept;
  (5) the real proof at this checkout's HEAD and a step-3 doc mutant of it: exit 0 'RESULT PASS: 0 failed', then exit 1
      (skip when the seeds are not readable here, as inside the wall)."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R              # noqa: E402
import relentless_trust as T        # noqa: E402
import relentless_wall as W         # noqa: E402

FAILS = []
NAME = "relentless_seed_compare"
PROVE = "src/RimMandrake/rimflow/prove_relentless_s03_compare.py"
DOC = "design/RimMandrake/relentless_TRUST_2026-11-01.md"
SEEDS = "/mnt/d/ClaudeWork/rimmandrake/relentless_agent/seeds"
# The stub reads the step 3 number from the doc and prints every kind of line; only check rows may cross.
STUB = r'''import os, sys
from pathlib import Path
doc = Path(__file__).resolve().parents[3] / "design" / "RimMandrake" / "relentless_TRUST_2026-11-01.md"
n = doc.read_text().split("## Step 3: the evaluation seeds behind the wall")[1].split("fails ")[1].split()[0]
print("E1 keys 22; step 0 runs 1, S03 runs 1, wall runs 1")
print("KEY {'item': 'SECRET_CASE', 'cls': 'hunk_red', 'answer': 'PLANTED_ANSWER'}")
print("reason: the Marker said PLANTED_REASON", file=sys.stderr)
print("ok   S03 holds 22 cases")
ok = n == "4"
print(("ok   " if ok else "FAIL ") + "step 3 says fails %s (recomputed 4)" % n)
print("RESULT %s: %d failed" % ("PASS" if ok else "FAIL", 0 if ok else 1))
sys.exit(0 if ok else 1)
'''
DOCTEXT = "# trust\n\n## Step 3: the evaluation seeds behind the wall\n\nfails 4 of 9.\n\n## Step 4\n"


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else "  %s" % str(detail)[:400]))
    if not cond:
        FAILS.append(name)


def git(d, *a):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
    return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, env=env, check=True).stdout.strip()


class Fx:
    def run_offbox(self, name, adapter, timeout):
        return R.run_bounded(name, adapter, timeout)


def reading(r, repo, sha):
    return R.offbox_readings(Fx(), {"offbox": [NAME]}, r, {"sha": sha, "repo": repo, "item": "X"})[0]


def write(repo, rel, text):
    p = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


def mutate(text, at=r"fails (\d+)"):
    """-> text with one number in the step 3 section changed (the doc mutant the item names): the first match of `at`,
    whose group 1 is a number the proof recomputes (the fixture's 'fails N'; the real doc's all_red catch count)."""
    i = text.index("## Step 3: the evaluation seeds behind the wall")
    m = re.compile(at).search(text, i)
    k = m.start(1)
    return text[:k] + str(int(m.group(1)) + 7) + text[m.end(1):]


def main():
    r = R.rules(os.path.join(HERE, "relentless_rules.json"))
    ad = W.adapters(r).get(NAME)
    check("(1) the adapter is defined", ad is not None)
    if ad is None:
        return 1
    raw = r["offbox_adapters"][NAME]
    check("(1) it covers the seeds path", raw.get("covers") == [SEEDS], raw.get("covers"))
    slots = set(s for tok in ad["argv"] for s in re.findall(r"\{([a-z_]+)\}", tok))
    check("(1) it fills {repo} and {sha} only", slots == {"repo", "sha"}
          and ad["argv"][-2:] == ["{repo}", "{sha}"], ad["argv"][-2:])

    root = tempfile.mkdtemp(prefix="seedcmp-")
    old = os.environ.get("HOME")
    try:
        home = os.path.join(root, "home")
        os.makedirs(home)
        os.environ["HOME"] = home                   # the adapter works under HOME
        repo = os.path.join(root, "repo")
        os.makedirs(repo)
        git(repo, "init", "-q", "-b", "main")
        write(repo, "src/RimMandrake/rimflow/keep.txt", "k\n")
        write(repo, DOC, DOCTEXT)
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "no proof yet")
        bare = git(repo, "rev-parse", "HEAD")
        write(repo, PROVE, STUB)
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "proof")
        good = git(repo, "rev-parse", "HEAD")
        write(repo, DOC, mutate(DOCTEXT))
        git(repo, "commit", "-qam", "mutant")
        mut = git(repo, "rev-parse", "HEAD")

        got = reading(r, repo, good)
        out = got["out"]
        check("(2) exit 0 at the good sha", got["exit"] == 0, got)
        check("(2) the check rows cross", "ok   S03 holds 22 cases" in out and "RESULT PASS: 0 failed" in out
              and "E1 keys 22" in out, out[-400:])
        check("(2) no planted key, answer or reason crosses",
              not any(s in out for s in ("SECRET_CASE", "PLANTED_ANSWER", "PLANTED_REASON", "KEY ")), out[-400:])
        check("(2) the trailer names the sha", ("seed compare exit=0 at %s" % good) in out, out[-200:])
        check("(2) nothing left under HOME", os.listdir(home) == [], os.listdir(home))

        got = reading(r, repo, mut)
        check("(3) the doc mutant reads exit 1", got["exit"] == 1, got)
        check("(3) with its FAIL row", "FAIL step 3 says fails 11" in got["out"], got["out"][-300:])

        got = reading(r, repo, bare)
        check("(4) the proof absent at the sha reads exit 2", got["exit"] == 2 and "NOT RUN" in got["out"], got)
        git(repo, "rm", "-q", DOC)
        git(repo, "commit", "-qm", "no doc")
        got = reading(r, repo, git(repo, "rev-parse", "HEAD"))
        check("(4) the TRUST doc absent at the sha reads exit 2", got["exit"] == 2 and "NOT RUN" in got["out"], got)
        stale = os.path.join(home, ".offbox-seedcmp-leftover")
        os.makedirs(stale)
        os.utime(stale, (1, 1))
        reading(r, repo, good)
        check("(4) a leftover export over an hour old is swept", not os.path.exists(stale), os.listdir(home))

        priv = os.environ.get("RM_SEEDS_PRIVATE") or str(T.PRIVATE)
        top = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        here = top.stdout.strip()
        if not os.path.isfile(os.path.join(priv, "keys", "E1.json")) or top.returncode:
            print("skip (5) the seeds are not readable here (inside the wall they never are)")
        elif subprocess.run(["git", "-C", here, "cat-file", "-e", "HEAD:" + PROVE], capture_output=True).returncode:
            print("skip (5) HEAD has no %s" % PROVE)
        else:
            head = git(here, "rev-parse", "HEAD")
            got = reading(r, here, head)
            check("(5) the real proof at HEAD: exit 0, RESULT PASS: 0 failed",
                  got["exit"] == 0 and "RESULT PASS: 0 failed" in got["out"], got["out"][-400:])
            clone = os.path.join(root, "real")
            subprocess.run(["git", "clone", "-q", "--shared", "--no-checkout", here, clone], check=True, capture_output=True)
            git(clone, "checkout", "-q", head)
            with open(os.path.join(clone, DOC), encoding="utf-8") as f:
                text = f.read()
            with open(os.path.join(clone, DOC), "w", encoding="utf-8") as f:
                f.write(mutate(text, r"\| all_red \| (\d+) of"))
            git(clone, "commit", "-qam", "step 3 doc mutant")
            got = reading(r, clone, git(clone, "rev-parse", "HEAD"))
            check("(5) the real step-3 doc mutant: exit 1 with a FAIL row",
                  got["exit"] == 1 and "\nFAIL " in "\n" + got["out"], got["out"][-400:])
    finally:
        if old is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = old
        shutil.rmtree(root, ignore_errors=True)
    print("RESULT %s: %d failed" % ("PASS" if not FAILS else "FAIL", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
