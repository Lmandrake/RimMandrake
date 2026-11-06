#!/usr/bin/env python3
"""selftest_relentless_reach_other_dark_third.py - the `other` repair's inherited adapters read at an older candidate.

CHECKER_REACH_FIX_OTHER_DARK_THIRD: NIGHTSIDE_TITAN_JUDGE_GIANTS_IN_THE_DARK inherited ROT_KEPT's passed `other` repair
(adapters git_stat_candidate, git_log_candidate, unit_probe_selftests_candidate). Probed at its candidate 7cc64bac, two of
them failed, so the probe failed and three waiters stayed blocked:
  - git_log_candidate printed 120 whole subjects, ran past OFFBOX_OUT_MAX (20000 bytes) and was killed;
  - unit_probe_selftests_candidate exited 2 because selftest_relentless_reach_item_prose postdates that sha.
Rows (each runs the adapter as the supervisor's probe does: Effects.reach_probe -> offbox_readings -> run_bounded):
  (1) git_log_candidate on 120 commits with 300-char subjects: exit 0, 120 lines, under the cap;
  (2) unit_probe_selftests_candidate with one fixed test present (green) and one absent: exit 0, the absent one named;
  (3) the probe itself passes with all three adapters on that fixture repo;
  (4) the real instance: git_log_candidate at 7cc64bac in this repo's history (skip when the history lacks it).
Rows 1-3 fail on the rules before the fix ('output over 20000 bytes, killed'; exit 2)."""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R              # noqa: E402
import relentless_wall as W         # noqa: E402

FAILS = []
ADAPTERS = ["git_stat_candidate", "git_log_candidate", "unit_probe_selftests_candidate"]
NIGHTSIDE_SHA = "7cc64bacb4c4ec12eaed14dca2ec17d0b9a972cd"
GREEN = "print('ok   a row')\nprint('RESULT: GREEN')\n"


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else "  %s" % str(detail)[:300]))
    if not cond:
        FAILS.append(name)


def rules():
    with open(os.path.join(HERE, "relentless_rules.json"), encoding="utf-8") as f:
        return json.load(f)


def git(d, *a):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
    return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, env=env, check=True).stdout.strip()


class Fx:
    """Only what reach_probe needs when it is handed adapters alone (no paths, no grants: no systemd unit)."""

    def run_offbox(self, name, adapter, timeout):
        return R.run_bounded(name, adapter, timeout)


def reading(r, name, repo, sha):
    return R.offbox_readings(Fx(), {"offbox": [name]}, r, {"sha": sha, "repo": repo, "item": "X"})[0]


def fixed_tests(r):
    src = next(a for a in W.adapters(r)["unit_probe_selftests_candidate"]["argv"] if "tests = [" in a)
    return ast.literal_eval(re.search(r"tests = (\[[^\]]*\])", src).group(1))


def make_repo(root, r):
    repo = os.path.join(root, "repo")
    rim = os.path.join(repo, "src", "RimMandrake", "rimflow")
    os.makedirs(rim)
    os.makedirs(os.path.join(repo, "src", "RimMandrake", "Utils"))
    with open(os.path.join(repo, "src", "RimMandrake", "Utils", "keep.txt"), "w") as f:
        f.write("u\n")
    git(repo, "init", "-q", "-b", "main")
    tests = fixed_tests(r)
    with open(os.path.join(rim, tests[0] + ".py"), "w") as f:      # the older test exists; the newer ones do not yet
        f.write(GREEN)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "base")
    long = "CHECKER_REACH_FIX_OTHER_DARK_THIRD: " + "a subject that runs on and on " * 10
    for i in range(130):
        git(repo, "commit", "-q", "--allow-empty", "-m", "%03d %s" % (i, long))
    return repo, git(repo, "rev-parse", "HEAD"), tests


def main():
    r = rules()
    root = tempfile.mkdtemp(prefix="reachdark3-")
    old = os.environ.get("HOME")
    try:
        home = os.path.join(root, "home")
        os.makedirs(home)
        os.environ["HOME"] = home                   # the unit-probe adapter works under HOME
        repo, sha, tests = make_repo(root, r)

        got = reading(r, "git_log_candidate", repo, sha)
        lines = got["out"].splitlines()
        check("(1) git_log_candidate on 120 long subjects: exit 0", got["exit"] == 0, got["exit"])
        check("(1) it reads 120 lines, the newest first", len(lines) == 120 and lines[0].startswith(sha), len(lines))
        check("(1) under the offbox cap", len(got["out"].encode()) <= W.OFFBOX_OUT_MAX, len(got["out"]))

        got = reading(r, "unit_probe_selftests_candidate", repo, sha)
        check("(2) one fixed test absent at an older sha: exit 0", got["exit"] == 0, got)
        check("(2) the present test ran", ("== %s exit=0" % tests[0]) in got["out"], got["out"][-300:])
        if len(tests) > 1:
            check("(2) the absent one is named", ("%s: absent at %s" % (tests[1], sha)) in got["out"], got["out"][-300:])

        good, why = R.Effects.reach_probe(Fx(), r, [], ADAPTERS, {"sha": sha, "repo": repo, "item": "X"}, root)
        check("(3) the probe passes with the three inherited adapters", good, why)

        top = subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        here = top.stdout.strip()
        if top.returncode or subprocess.run(["git", "-C", here, "cat-file", "-e", NIGHTSIDE_SHA + "^{commit}"],
                                            capture_output=True).returncode:
            print("skip (4) this history lacks %s" % NIGHTSIDE_SHA[:10])
        else:
            got = reading(r, "git_log_candidate", here, NIGHTSIDE_SHA)
            check("(4) git_log_candidate at NIGHTSIDE's 7cc64bac: exit 0 under the cap",
                  got["exit"] == 0 and len(got["out"].splitlines()) == 120, got["exit"])
    except Exception as e:      # a row that crashes is a red row, not a dead selftest
        check("ran", False, "%s: %s" % (type(e).__name__, e))
    finally:
        if old is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = old
        shutil.rmtree(root, ignore_errors=True)
    print("RESULT: %s" % ("GREEN" if not FAILS else "RED %d: %s" % (len(FAILS), ", ".join(FAILS))))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
