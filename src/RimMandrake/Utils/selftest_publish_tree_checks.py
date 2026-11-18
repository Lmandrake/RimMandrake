#!/usr/bin/env python3
"""selftest_publish_tree_checks.py - publish.tree_checks refuses on a red whole-tree check, naming it and its fix
(owner by card 2026-11-12 ~8:25 PM PST; validation_map_and_rules.md rule 10).

Offline: a temp dir stands in for the repo top, with its own publish_tree_checks.json and tiny check scripts.
Cases: all green passes; one red refuses naming that check, its FAIL line and its fix, and not the green one; a
ledger-only change runs nothing (a red check stays unrun); a timeout warns and refuses nothing; no config runs
nothing; the bypass variable skips, out loud. A sparse git fixture clone (a check joining an in-cone list with an
out-of-cone record) passes on a clean HEAD and refuses a violation committed in the cone, leaving no check tree. A pipeline
test red on origin/main the same way before the change is named PRE-EXISTING and not refused; one the change turned red,
made worse, or added, or one with no base to compare, is refused saying which. The real list: every listed test exists, and the listed seconds sum
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


# RIMMANDRAKE_REPAIR_TWO_GAMES_DOOR_TEST_BLOCKS_EVERY_PUBLISH (A3, A4): a pipeline test red on origin/main before the change
# refused every unrelated publish, and the refusal could not say "already red" from "your change broke it". The door
# re-runs a red test on the commit the change sits on (HEAD's merge base with origin/main): red there with the same FAIL
# lines is PRE-EXISTING (named, not refused); green there, red with new FAIL lines, or not readable there is refused,
# saying which. The FAIL line carries a pid so the comparison must ignore numbers that move between runs.
PIPE_TEST = r'''import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pipe
for f in pipe.FAULTS:
    if f not in ("crash", "silent"):
        print("FAIL %s fault (run %d)" % (f, 100000 + os.getpid()))
print("ok the rest")
if "crash" in pipe.FAULTS:
    raise RuntimeError("boom in run %d" % (100000 + os.getpid()))
sys.exit(1 if pipe.FAULTS else 0)
'''


def pipe_repo(tmp, name, base_faults, after_faults, remote=True, new_test=False):
    """-> a work clone whose origin/main holds pipe.py with base_faults and whose HEAD commit makes it after_faults."""
    up = os.path.join(tmp, name + "_up")
    os.makedirs(os.path.join(up, os.path.dirname(P.PIPELINE_TESTS)))
    json.dump({"timeout_s": 30, "pipeline_files": ["src/*.py"], "tests": [{"test": "src/selftest_pipe.py"}]},
              open(os.path.join(up, P.PIPELINE_TESTS), "w"))
    script(up, os.path.join("src", "pipe.py"), "FAULTS = %r\n" % (base_faults,))
    if not new_test:
        script(up, os.path.join("src", "selftest_pipe.py"), PIPE_TEST)
    g("init", "-q", cwd=up)
    g("add", "-A", cwd=up)
    g("commit", "-q", "-m", "base", cwd=up)
    work = os.path.join(tmp, name)
    if remote:
        g("clone", "-q", up, work, cwd=tmp)
    else:
        work = up
    script(work, os.path.join("src", "pipe.py"), "FAULTS = %r\n# the change\n" % (after_faults,))
    if new_test:
        script(work, os.path.join("src", "selftest_pipe.py"), PIPE_TEST)
        g("add", os.path.join("src", "selftest_pipe.py"), cwd=work)
    g("commit", "-q", "-am", "change", cwd=work)
    base = subprocess.run(["git", "-C", up, "rev-parse", "HEAD~1" if not remote else "HEAD"], capture_output=True,
                          text=True).stdout.strip()
    return work, base


def pcall(top, changed):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            P.pipeline_checks(top, changed)
            return None, buf.getvalue()
        except P.Refuse as e:
            return str(e), buf.getvalue()


def door_base_cases(tmp):
    ch = ["src/pipe.py"]
    work, base = pipe_repo(tmp, "pre", ["old"], ["old"])
    err, out = pcall(work, ch)
    check(err is None and "PRE-EXISTING" in out and "selftest_pipe.py" in out and base[:10] in out
          and "old fault" in out and "0 green, 1 PRE-EXISTING red" in out,
          "a test red the same way on origin/main before the change: named PRE-EXISTING with the base sha, not refused "
          "(%r)" % (err or out)[-240:])
    work, base = pipe_repo(tmp, "broke", [], ["old"])
    err, out = pcall(work, ch)
    check(bool(err) and "selftest_pipe.py" in err and "green on origin/main %s" % base[:10] in err,
          "a test green on origin/main that the change turns red: refused, saying the change broke it (%r)" % err)
    work, base = pipe_repo(tmp, "worse", ["old"], ["old", "new"])
    err, out = pcall(work, ch)
    check(bool(err) and "new fault" in err and "red on origin/main %s too" % base[:10] in err
          and "old fault" not in err.split("new in this change:")[-1],
          "red on origin/main and the change adds a FAIL line: refused naming only the new line (%r)" % err)
    work, base = pipe_repo(tmp, "noremote", ["old"], ["old"], remote=False)
    err, out = pcall(work, ch)
    check(bool(err) and "UNMEASURED" in err and "not proved pre-existing" in err,
          "no origin/main to compare with: refused, the base reading UNMEASURED by name (%r)" % err)
    work, base = pipe_repo(tmp, "newtest", ["old"], ["old"], new_test=True)
    err, out = pcall(work, ch + ["src/selftest_pipe.py"])
    check(bool(err) and "absent on origin/main" in err,
          "a red test the change itself adds is refused, never excused as pre-existing (%r)" % err)
    # Codex review 2026-11-18: ways a worse red could read as the old one
    work, base = pipe_repo(tmp, "crashafter", ["old"], ["old", "crash"])
    err, out = pcall(work, ch)
    check(bool(err) and "new in this change" in err and "crash" in err,
          "the same FAIL lines and then a crash: refused, the crash named as new (%r)" % err)
    work, base = pipe_repo(tmp, "twice", ["old"], ["old", "old"])
    err, out = pcall(work, ch)
    check(bool(err) and "new in this change" in err, "a FAIL line that now appears twice is new, not the old one (%r)" % err)
    work, base = pipe_repo(tmp, "silent", ["silent"], ["silent"])
    err, out = pcall(work, ch)
    check(bool(err) and "no FAIL line and no traceback" in err,
          "a red with nothing to compare by is refused, never excused as pre-existing (%r)" % err)
    work, base = pipe_repo(tmp, "dirty", ["old"], ["old", "new"])
    script(work, os.path.join("src", "pipe.py"), "FAULTS = ['old']\n# an uncommitted edit hides the committed new fault\n")
    err, out = pcall(work, ch)
    check(bool(err) and "new fault" in err and "new in this change" in err,
          "the working tree reads the old red but HEAD's commit adds a fault: compared commit to commit, refused (%r)" % err)
    work, base = pipe_repo(tmp, "dirtyred", ["old"], [])
    script(work, os.path.join("src", "pipe.py"), "FAULTS = ['old']\n# an uncommitted edit makes it red\n")
    err, out = pcall(work, ch)
    check(bool(err) and "green at HEAD's commit" in err,
          "red only through uncommitted edits (HEAD's commit is green): refused, not excused (%r)" % err)
    work, base = pipe_repo(tmp, "unknown", ["old"], ["old"], remote=False)
    check(P._changed_since_origin(work) is None, "no origin/main: the change set reads unknown (None), not empty")
    err, out = pcall(work, None)
    check(bool(err) and "every pipeline test runs" in out and "selftest_pipe.py" in err,
          "an unknown change set runs every pipeline test (it used to run none) (%r)" % (err or out))
    left = [n for w in ("pre", "broke", "worse", "newtest", "crashafter", "twice", "silent") for n in os.listdir(os.path.join(tmp, w, ".git"))
            if n.startswith(P.CHECKTREE_PREFIX)]
    check(not left, "no base tree left in any git dir: %s" % left)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        sparse_cases(tmp)
    with tempfile.TemporaryDirectory() as tmp:
        door_base_cases(tmp)
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
        # RIMMANDRAKE_STRIP_HOLDER_WRITER_FROM_DOOR_TESTS: a holder run's unit carries RM_MODLEDGER_WRITER=HOLDER.<lease>;
        # a door test that writes a DISPATCH or BACKFILL shard was refused under it, so no holder could publish.
        script(tmp, "holder.py", "import os, sys\nw = os.environ.get('RM_MODLEDGER_WRITER')\n"
               "print('FAIL the publisher\\'s ledger identity leaked: %s' % w) if w else print('ok')\nsys.exit(1 if w else 0)\n")
        fixture(tmp, ["holder.py"])
        was = {k: os.environ.get(k) for k in ("RM_MODLEDGER_WRITER", "RM_MODLEDGER_TOKEN")}
        os.environ.update(RM_MODLEDGER_WRITER="HOLDER.run-1", RM_MODLEDGER_TOKEN="1")
        err, out = call(tmp, ["src/a.py"])
        for k, v in was.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        check(err is None and "1 green" in out, "a holder's RM_MODLEDGER_WRITER/TOKEN never reach a door test (%r)" % err)
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
