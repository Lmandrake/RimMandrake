#!/usr/bin/env python3
"""selftest_relentless_reach_nested_unit.py - a Judge blind on a nested unit gets a reading (CHECKER_REACH_FIX_OTHER_STILL_DARK).

CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS's Judge ran selftest_relentless_reach_git_grant, whose live row starts its own
systemd-run --user unit; the Marker's box refuses a namespaced unit (exit 226). The text fell to the catch-all `other`
class, whose seed offered only /mnt (refused), so nothing was proposed and the item blocked on this ticket. Rows:
  (1) that blind text classes as nested_unit and its seed proposes the adapter unit_probe_selftests_candidate (no paths);
  (2) the owner's stored `other` seed proposal gains the adapter when its ticket closes and it re-probes (refreshed());
  (3) the adapter, run as the supervisor runs one (run_bounded) on a throwaway repo: exit 0 on a green test with only the
      check rows crossing back and a TMPDIR under HOME, the test's own exit on a red one, 128+N on a signal death, 2 when the test is absent.
Rows 1-3 fail on the rules before the class (classify() said `other`; the adapter did not exist)."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R              # noqa: E402
import relentless_reachfix as RF    # noqa: E402
import relentless_wall as W         # noqa: E402

FAILS = []
ADAPTER = "unit_probe_selftests_candidate"
TEXT = ("live wall probe of the git_history grant (selftest_relentless_reach_git_grant row 5): nested mount namespace "
        "refused, 'systemd-run --user -p TemporaryFileSystem=/mnt true' -> exit 226 in this box")
STORE = "/home/mandrake/rm/relentless/store"


def check(name, cond, detail=""):
    print(("ok   " if cond else "FAIL ") + name + ("" if cond else "  %s" % str(detail)[:300]))
    if not cond:
        FAILS.append(name)


def rules():
    with open(os.path.join(HERE, "relentless_rules.json"), encoding="utf-8") as f:
        return json.load(f)


def test_class(r):
    c = RF.classify(r, [TEXT])
    check("(1) the nested-unit text classes as nested_unit", c.get("class") == "nested_unit", c.get("class"))
    p = RF.propose(r, c, [], [], TEXT, STORE)
    check("(1) its seed proposes the adapter", p["adapters"] == [ADAPTER], p)
    check("(1) and no read path (a unit is not a path)", not p["paths"] and not p["refused"], p)
    check("(1) the adapter is a supervisor offbox adapter", ADAPTER in W.adapters(r))
    git = RF.classify(r, ["the tree is a git-less export, so 'git show <rev>:...' cannot run"])
    check("(1) a plain git text still classes as git", git.get("class") == "git", git.get("class"))


def test_refresh(r):
    st = {"reach": {"class": "other", "status": "ticket", "proposal": {"adapters": [], "by": "seed", "grants": [],
                                                                        "paths": [], "refused": {"/mnt": "x"}}},
          "blind": {"what": TEXT}}
    p = RF.refreshed(r, st)
    check("(2) the stored `other` seed gains the adapter on re-probe", ADAPTER in (p.get("adapters") or []), p)


def git(d, *a):
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
    return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, env=env, check=True).stdout.strip()


def commit(repo, body):
    d = os.path.join(repo, "src", "RimMandrake", "rimflow")
    os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(repo, "src", "RimMandrake", "Utils"), exist_ok=True)
    with open(os.path.join(repo, "src", "RimMandrake", "Utils", "keep.txt"), "w") as f:
        f.write("u\n")
    f = os.path.join(d, "selftest_relentless_reach_git_grant.py")
    if body is None:
        if os.path.exists(f):
            os.remove(f)
        with open(os.path.join(d, "other.py"), "w") as g:
            g.write("x = 1\n")
    else:
        with open(f, "w") as g:
            g.write(body)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "c")
    return git(repo, "rev-parse", "HEAD")


GREEN = ("import os, sys\nprint('ok   tmp=%s' % os.environ.get('TMPDIR'))\nprint('a worker note that must not cross')\n"
         "print('ok   root=%s' % os.environ.get('RELENTLESS_ROOT'))\nprint('ok   required=%s' % os.environ.get('RELENTLESS_UNIT_PROBE_REQUIRED'))\nprint('RESULT: GREEN')\n")
KILLED = "import os, signal\nprint('ok   before')\nos.kill(os.getpid(), signal.SIGKILL)\n"
RED = "print('FAIL (5) a row')\nprint('RESULT: RED 1: (5) a row')\nraise SystemExit(1)\n"


def run(r, repo, sha):
    argv, why = W.fill_argv(W.adapters(r)[ADAPTER]["argv"], {"sha": sha, "repo": repo, "item": "X"})
    assert not why, why
    return R.run_bounded(ADAPTER, dict(W.adapters(r)[ADAPTER], argv=argv), 60)


def test_adapter(r):
    root = tempfile.mkdtemp(prefix="nestunit-")
    old = {k: os.environ.get(k) for k in ("HOME", "RELENTLESS_ROOT")}
    try:
        home = os.path.join(root, "home")
        os.makedirs(home)
        os.environ["HOME"] = home                   # the adapter works under HOME; the box's own may be read-only
        os.environ["RELENTLESS_ROOT"] = "/secret/store"
        repo = os.path.join(root, "repo")
        os.makedirs(repo)
        git(repo, "init", "-q", "-b", "main")
        green = commit(repo, GREEN)
        got = run(r, repo, green)
        out = got["out"]
        check("(3) a green test: exit 0", got["exit"] == 0, got)
        check("(3) its check rows and RESULT cross back", "RESULT: GREEN" in out and "ok   tmp=" in out, out)
        check("(3) a non-row line does not", "worker note" not in out, out)
        check("(3) the store root does not reach the test", "root=None" in out, out)
        check("(3) the live row is required off the box", "required=1" in out, out)
        tmp = out.split("ok   tmp=", 1)[-1].split("\n", 1)[0]
        check("(3) TMPDIR is under HOME, never the caller's", tmp.startswith(home + "/"), tmp)
        check("(3) the work folder is removed", not [n for n in os.listdir(home) if n.startswith(".offbox-")],
              os.listdir(home))
        check("(3) the closing line names the sha", ("exit=0 at %s" % green) in out, out[-200:])
        got = run(r, repo, commit(repo, RED))
        check("(3) a red test: its exit", got["exit"] == 1 and "FAIL (5) a row" in got["out"], got)
        got = run(r, repo, commit(repo, KILLED))
        check("(3) a test killed by a signal: 128+N, never 0", got["exit"] == 137, got)
        got = run(r, repo, commit(repo, None))
        check("(3) the test absent at the sha: exit 2", got["exit"] == 2 and "absent" in got["out"], got)
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(root, ignore_errors=True)


def main():
    r = rules()
    for t in (test_class, test_refresh, test_adapter):
        try:
            t(r)
        except Exception as e:      # a row that crashes is a red row, not a dead selftest
            check("%s ran" % t.__name__, False, "%s: %s" % (type(e).__name__, e))
    print("RESULT: %s" % ("GREEN" if not FAILS else "RED %d: %s" % (len(FAILS), ", ".join(FAILS))))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
