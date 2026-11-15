#!/usr/bin/env python3
"""selftest_publish_tree_checks.py - publish.tree_checks refuses on a red whole-tree check, naming it and its fix
(owner by card 2026-11-12 ~8:25 PM PST; validation_map_and_rules.md rule 10).

Offline: a temp dir stands in for the repo top, with its own publish_tree_checks.json and tiny check scripts.
Cases: all green passes; one red refuses naming that check, its FAIL line and its fix, and not the green one; a
ledger-only change runs nothing (a red check stays unrun); a timeout warns and refuses nothing; no config runs
nothing; the bypass variable skips, out loud. A sparse git fixture clone (a check joining an in-cone list with an
out-of-cone record) passes on a clean HEAD and refuses a violation committed in the cone, leaving no check tree. The real list: every listed test exists, and the listed seconds sum
under budget_s. Exit 0 = all pass, 1 = a case failed.
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import publish as P  # noqa: E402

FAILS = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def fixture(tmp, checks, **extra):
    os.makedirs(os.path.join(tmp, os.path.dirname(P.TREE_CHECKS)), exist_ok=True)
    cfg = {"budget_s": 30, "timeout_s": 2, "skip_when_only": ["infrastructure/state/ledger/events/*.jsonl"],
           "checks": [{"test": n, "fix": "fix-for-" + n} for n in checks]}
    cfg.update(extra)
    json.dump(cfg, open(os.path.join(tmp, P.TREE_CHECKS), "w"))


def script(tmp, name, body):
    open(os.path.join(tmp, name), "w").write(body)


def call(tmp, changed):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            P.tree_checks(tmp, changed)
            return None, buf.getvalue()
        except P.Refuse as e:
            return str(e), buf.getvalue()


GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "core.hooksPath=/dev/null",
       "-c", "init.defaultBranch=main"]

# A check that joins an in-cone list with an out-of-cone record, as the real ones do (src names vs design/ records):
# blind (record missing) is red, a listed name the record does not allow is red.
JOIN_CHECK = r'''import os, sys
top = os.path.dirname(os.path.abspath(__file__))
allowed = os.path.join(top, "data", "allowed.txt")
if not os.path.isfile(allowed):
    print("FAIL instrument blind: data/allowed.txt not here"); sys.exit(1)
ok = set(open(allowed).read().split())
bad = [n for n in open(os.path.join(top, "src", "list.txt")).read().split() if n not in ok]
if bad:
    print("FAIL planted name not allowed: %s" % bad); sys.exit(1)
print("ok %d names allowed" % len(ok))
'''


def g(*a, cwd):
    subprocess.run([*GIT, *a], cwd=cwd, check=True, capture_output=True, text=True)


def sparse_cases(tmp):
    """A sparse clone runs the checks on a full checkout of HEAD: green when HEAD is clean (it went red blind before),
    red on a violation committed in the cone, and no check tree is left behind."""
    up = os.path.join(tmp, "up")
    os.makedirs(os.path.join(up, os.path.dirname(P.TREE_CHECKS)))
    os.makedirs(os.path.join(up, "data"))
    json.dump({"timeout_s": 30, "skip_when_only": [], "checks": [{"test": "join.py", "fix": "fix-join"}]},
              open(os.path.join(up, P.TREE_CHECKS), "w"))
    script(up, "join.py", JOIN_CHECK)
    script(up, os.path.join("src", "list.txt"), "alpha\n")
    script(up, os.path.join("data", "allowed.txt"), "alpha beta\n")
    g("init", "-q", cwd=up)
    g("add", "-A", cwd=up)
    g("commit", "-q", "-m", "base", cwd=up)
    sp = os.path.join(tmp, "sp")
    g("clone", "-q", "--no-checkout", up, sp, cwd=tmp)
    g("sparse-checkout", "set", "--cone", "src", cwd=sp)
    g("checkout", "-q", "main", cwd=sp)
    check(not os.path.exists(os.path.join(sp, "data", "allowed.txt")) and P.is_sparse(sp),
          "sanity: the fixture clone is sparse and lacks the out-of-cone record")
    check(not P.is_sparse(up), "sanity: a full clone is not sparse")
    err, out = call(sp, ["src/list.txt"])
    check(err is None and "full checkout of HEAD" in out and "1 green" in out,
          "a sparse clone with a clean HEAD passes, the check run on a full checkout (%r)" % (err or out.strip())[-160:])
    script(sp, os.path.join("src", "list.txt"), "alpha\ngamma\n")
    g("commit", "-q", "-am", "plant", cwd=sp)
    err, out = call(sp, ["src/list.txt"])
    check(bool(err) and "planted name not allowed" in err and "gamma" in err and "fix-join" in err,
          "a sparse clone refuses a violation committed in the cone (%r)" % (err or out)[-200:])
    gitdir = os.path.join(sp, ".git")
    left = [n for n in os.listdir(gitdir) if n.startswith(P.CHECKTREE_PREFIX)]
    check(not left, "no check tree left in the git dir: %s" % left)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        sparse_cases(tmp)
    with tempfile.TemporaryDirectory() as tmp:
        script(tmp, "green.py", "print('ok all good')\n")
        script(tmp, "red.py", "print('FAIL the planted fault in x.py')\nraise SystemExit(1)\n")
        script(tmp, "slow.py", "import time\ntime.sleep(5)\n")
        err, out = call(tmp, ["src/a.py"])
        check(err is None and out == "", "no config: nothing runs, nothing refused")
        fixture(tmp, ["green.py"])
        err, out = call(tmp, ["src/a.py"])
        check(err is None and "1 green" in out, "all green: passes and says so (%r)" % out.strip())
        fixture(tmp, ["green.py", "red.py"])
        err, out = call(tmp, ["src/a.py"])
        check(bool(err) and "red.py" in err and "planted fault" in err and "fix-for-red.py" in err,
              "a red check refuses naming the check, its FAIL line and its fix")
        check(bool(err) and "green.py" not in err, "the refusal names only the red check")
        err, out = call(tmp, ["infrastructure/state/ledger/events/BENCH.jsonl"])
        check(err is None and out == "", "a ledger-only change runs nothing")
        err, out = call(tmp, [])
        check(bool(err), "no changed paths (an already-made commit) still runs the checks")
        os.environ["RM_PUBLISH_SKIP_TREE_CHECKS"] = "selftest bypass"
        err, out = call(tmp, ["src/a.py"])
        del os.environ["RM_PUBLISH_SKIP_TREE_CHECKS"]
        check(err is None and "SKIPPED" in out and "selftest bypass" in out, "the bypass skips out loud with its reason")
        fixture(tmp, ["green.py", "slow.py"])
        err, out = call(tmp, ["src/a.py"])
        check(err is None and "UNMEASURED" in out and "slow.py" in out, "a timeout warns and refuses nothing")
    cfg = json.load(open(os.path.join(HERE, "..", "..", "..", P.TREE_CHECKS)))
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    listed = [c["test"] for c in cfg["checks"] + cfg.get("nightly_only", [])]
    tracked = set(subprocess.run(["git", "-C", root, "ls-files", "--", *listed], capture_output=True, text=True,
                                 timeout=60).stdout.split())      # a sparse clone holds them in git, not on disk
    missing = [t for t in listed if not os.path.isfile(os.path.join(root, t)) and t not in tracked]
    check(not missing, "every listed test exists: %s" % missing)
    total = sum(c["seconds"] for c in cfg["checks"])
    check(total < cfg["budget_s"] * 1.5 and max(c["seconds"] for c in cfg["checks"]) < cfg["budget_s"],
          "listed seconds %.1f serial; run in parallel the wall stays under budget_s %d" % (total, cfg["budget_s"]))
    check(all(c.get("fix") for c in cfg["checks"]), "every listed check carries its fix")
    print("PASS" if not FAILS else "FAIL %d" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
