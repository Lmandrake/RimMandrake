#!/usr/bin/env python3
"""selftest_publish_tree_checks.py - publish.tree_checks refuses on a red whole-tree check, naming it and its fix
(owner by card 2026-11-12 ~8:25 PM PST; validation_map_and_rules.md rule 10).

Offline: a temp dir stands in for the repo top, with its own publish_tree_checks.json and tiny check scripts.
Cases: all green passes; one red refuses naming that check, its FAIL line and its fix, and not the green one; a
ledger-only change runs nothing (a red check stays unrun); a timeout warns and refuses nothing; no config runs
nothing; the bypass variable skips, out loud. A sparse git fixture clone (a check joining an in-cone list with an
out-of-cone record) passes on a clean HEAD and refuses a violation committed in the cone, leaving no check tree. A pipeline
test red on origin/main the same way before the change is named PRE-EXISTING and not refused; one the change turned red,
made worse, or added, or one with no base to compare, is refused saying which. The real list: every listed test exists and carries
its fix. Exit 0 = all pass, 1 = a case failed.
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


def t_a_check_that_died_on_enomem_runs_again(tmp):
    # (RIMMANDRAKE_RERUN_DOOR_CHECK_DEAD_ON_ENOMEM_NOT_RED)
    def counted(name, body):
        script(tmp, name, "import os, sys\np = os.path.abspath(__file__) + '.n'\n"
               "n = int(open(p).read()) if os.path.exists(p) else 0\nopen(p, 'w').write(str(n + 1))\n" + body)

    def runs(name):
        return int(open(os.path.join(tmp, name + ".n")).read())

    boom = "raise OSError(12, 'Cannot allocate memory')\n"
    counted("mem_once.py", "if n == 0:\n    " + boom + "print('ok')\n")
    counted("mem_always.py", boom)
    counted("mem_then_red.py", "if n == 0:\n    " + boom + "print('FAIL real fault'); sys.exit(1)\n")
    counted("red_names_it.py", "print('FAIL the page says Cannot allocate memory'); sys.exit(1)\n")
    fixture(tmp, ["green.py", "mem_once.py"])
    err, out = call(tmp, ["src/a.py"])
    check(err is None and "2 green" in out and "mem_once.py" in out and "ran again" in out and runs("mem_once.py") == 2,
          "a-check-that-died-on-enomem-runs-again: it passes on its second run and the output says so (%r, %r)"
          % (err, out.strip()[-160:]))
    fixture(tmp, ["mem_always.py"])
    err, out = call(tmp, ["src/a.py"])
    check(bool(err) and "mem_always.py" in err and runs("mem_always.py") == 2,
          "a-check-that-died-on-enomem-runs-again: out of memory twice is still refused, after two runs")
    fixture(tmp, ["mem_then_red.py"])
    err, out = call(tmp, ["src/a.py"])
    check(bool(err) and "real fault" in err, "a-check-that-died-on-enomem-runs-again: a red second run is refused")
    fixture(tmp, ["red_names_it.py"])
    err, out = call(tmp, ["src/a.py"])
    check(bool(err) and runs("red_names_it.py") == 1,
          "a-check-that-died-on-enomem-runs-again: a FAIL whose text names the words is a red, never run again")


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
    # RIMMANDRAKE_CHECK_COMMITTED_TREE_NOT_DIRTY_WORKTREE_AT_DOOR: a FULL clone's door verdict is about the commit too.
    # `up` is full; publishing one of two edited files leaves the other dirty in the working tree, where the checks ran.
    script(up, os.path.join("src", "list.txt"), "alpha\ngamma\n")
    g("commit", "-q", "-am", "the commit: a name the committed record does not allow", cwd=up)
    script(up, os.path.join("data", "allowed.txt"), "alpha beta gamma\n")    # the fix, edited but not committed
    err, out = call(up, ["src/list.txt"])
    check(bool(err) and "planted name not allowed" in err,
          "a full clone refuses a commit that is red, whatever an uncommitted edit would make of it (%r)"
          % (err or out)[-200:])
    g("commit", "-q", "-am", "the fix, committed", cwd=up)
    script(up, os.path.join("data", "allowed.txt"), "alpha\n")               # a peer's half-done edit, not in the commit
    err, out = call(up, ["src/list.txt"])
    check(err is None and "1 green" in out,
          "a full clone passes a commit that is green, whatever an uncommitted edit would make of it (%r)"
          % (err or out)[-200:])
    check(not [n for n in os.listdir(os.path.join(up, ".git")) if n.startswith(P.CHECKTREE_PREFIX)],
          "no check tree left in the full clone's git dir")


# RIMMANDRAKE_REPAIR_TWO_GAMES_DOOR_TEST_BLOCKS_EVERY_PUBLISH (A3, A4): a pipeline test red on origin/main before the change
# refused every unrelated publish, and the refusal could not say "already red" from "your change broke it". The door
# re-runs a red test on the commit the change sits on (HEAD's merge base with origin/main): red there with the same FAIL
# lines is PRE-EXISTING (named, not refused); green there, red with new FAIL lines, or not readable there is refused,
# saying which. The FAIL line carries a pid so the comparison must ignore numbers that move between runs.
PIPE_TEST = r'''import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pipe
if "flake" in pipe.FAULTS:     # red on its first run only, green after (the file in $PIPE_FLAKE_FILE counts runs)
    first = not os.path.exists(os.environ["PIPE_FLAKE_FILE"])
    open(os.environ["PIPE_FLAKE_FILE"], "a").write("run\n")
    print("FAIL a timing row under load (run %d)" % (100000 + os.getpid()) if first else "ok the timing row")
    sys.exit(1 if first else 0)
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
    check(err is None, "red only through uncommitted edits (HEAD's commit is green): the door judges the commit, and "
          "passes it (%r)" % err)
    # RIMMANDRAKE_FIX_VISIT_WAIT_MISSES_FAILURE_CITED_ON_OLD_ITEM: a clone's door run is already on HEAD's commit, so red
    # there and green on the re-run of that same commit is a flaky reading; the door said "uncommitted edits make it
    # red" and refused three publishes of one change at load 14-18 on 14 cores (selftest_game_lock's timing rows)
    os.environ["PIPE_FLAKE_FILE"] = os.path.join(tmp, "flake_runs")
    work, base = pipe_repo(tmp, "flaky", [], ["flake"])
    err, out = pcall(work, ch)
    check(err is None and "FLAKY" in out and "selftest_pipe.py" in out and "uncommitted" not in out,
          "red at the door, green on a re-run of the same commit: named FLAKY, not refused, no uncommitted-edit story "
          "(%r)" % (err or out)[-300:])
    work, base = pipe_repo(tmp, "unknown", ["old"], ["old"], remote=False)
    check(P._changed_since_origin(work) is None, "no origin/main: the change set reads unknown (None), not empty")
    err, out = pcall(work, None)
    check(bool(err) and "every pipeline test runs" in out and "selftest_pipe.py" in err,
          "an unknown change set runs every pipeline test (it used to run none) (%r)" % (err or out))
    left = [n for w in ("pre", "broke", "worse", "newtest", "crashafter", "twice", "silent", "flaky") for n in os.listdir(os.path.join(tmp, w, ".git"))
            if n.startswith(P.CHECKTREE_PREFIX)]
    check(not left, "no base tree left in any git dir: %s" % left)


# RIMMANDRAKE_CHECK_PUBLISH_TREE_ON_REBASED_HEAD_NOT_STALE (design/specs/2026-11-22-publish-door-judges-landing-tree/
# boundary.md): a clone 19 behind origin was refused twice by selftest_modledger_tree.py for ledger lines origin had
# already restored (2026-11-22 ~00:55 PST). The whole-tree checks ran on HEAD before the rebase, and they take no
# pre-existing excuse (base=None in tree_checks), so origin's old red read as the commit's.
LEDGER_CHECK = r'''import os, sys
top = os.path.dirname(os.path.abspath(__file__))
lines = open(os.path.join(top, "data", "ledger.txt")).read().split()
if "line2" not in lines:
    print("FAIL STALE_TOKEN line2 deleted from data/ledger.txt"); sys.exit(1)
other = os.path.join(top, "src", "other.txt")
if os.path.isfile(other) and "BAD" in open(other).read():
    print("FAIL planted fault in src/other.txt"); sys.exit(1)
print("ok ledger whole")
'''


def landing_repo(tmp, name, origin_repairs=True, commit_body="ok\n"):
    """-> (work clone, origin sha after the last origin commit). Origin goes red (line2 deleted), the work clone branches
    there, then origin repairs it (or makes an unrelated commit), and the work clone writes src/other.txt (uncommitted:
    publish commits it)."""
    bare = os.path.join(tmp, name + ".git")
    g("init", "-q", "--bare", bare, cwd=tmp)
    seed = os.path.join(tmp, name + "_seed")
    g("clone", "-q", bare, seed, cwd=tmp)
    os.makedirs(os.path.join(seed, os.path.dirname(P.TREE_CHECKS)))
    os.makedirs(os.path.join(seed, "data"))
    json.dump({"timeout_s": 30, "skip_when_only": [], "checks": [{"test": "ledger_check.py", "fix": "fix-ledger"}]},
              open(os.path.join(seed, P.TREE_CHECKS), "w"))
    script(seed, "ledger_check.py", LEDGER_CHECK)
    script(seed, os.path.join("data", "ledger.txt"), "line1\nline2\n")
    script(seed, os.path.join("src", "keep.txt"), "a\n")
    g("add", "-A", cwd=seed)
    g("commit", "-q", "-m", "base", cwd=seed)
    g("push", "-q", "origin", "HEAD:main", cwd=seed)
    script(seed, os.path.join("data", "ledger.txt"), "line1\n")
    g("commit", "-q", "-am", "seat_dirt: line2 deleted", cwd=seed)
    g("push", "-q", "origin", "HEAD:main", cwd=seed)
    work = os.path.join(tmp, name)
    g("clone", "-q", bare, work, cwd=tmp)
    for k, v in (("user.name", "t"), ("user.email", "t@example.invalid"), ("core.hooksPath", "/dev/null")):
        g("config", k, v, cwd=work)
    if origin_repairs:
        script(seed, os.path.join("data", "ledger.txt"), "line1\nline2\n")
        g("commit", "-q", "-am", "restore line2", cwd=seed)
    else:
        script(seed, os.path.join("src", "keep.txt"), "a\nb\n")
        g("commit", "-q", "-am", "unrelated", cwd=seed)
    g("push", "-q", "origin", "HEAD:main", cwd=seed)
    script(work, os.path.join("src", "other.txt"), commit_body)
    up = subprocess.run(["git", "-C", seed, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    return work, up


def publish_call(work, paths):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            sha = P.publish(work, paths, "fixture change\n")
            return None, buf.getvalue() + ("PUBLISHED %s\n" % sha)
        except P.Refuse as e:
            return str(e), buf.getvalue()


def head_of(repo, ref="HEAD"):
    return subprocess.run(["git", "-C", repo, "rev-parse", ref], capture_output=True, text=True).stdout.strip()


def t_the_door_judges_the_tree_that_lands(tmp):
    work, up = landing_repo(tmp, "judge")
    g("add", "src/other.txt", cwd=work)
    g("commit", "-q", "-m", "the change", cwd=work)
    err, out = call(work, ["src/other.txt"])
    check(err is None and "replayed onto origin/main %s" % up[:12] in out and "1 green" in out,
          "the-door-judges-the-tree-that-lands: a clone behind origin is judged on HEAD replayed onto the fetched origin "
          "(%r)" % (err or out)[-300:])
    g("pull", "-q", "--rebase", cwd=work)
    err, out = call(work, ["src/other.txt"])
    check(err is None and "full checkout of HEAD" in out and "replayed" not in out,
          "the-door-judges-the-tree-that-lands: a clone on top of origin is judged on HEAD (%r)" % (err or out)[-300:])


def t_a_red_origin_already_repaired_does_not_refuse(tmp):
    work, up = landing_repo(tmp, "repaired")
    err, out = publish_call(work, ["src/other.txt"])
    landed = head_of(os.path.join(tmp, "repaired.git"), "main")
    check(err is None and "PUBLISHED" in out and landed != up,
          "a-red-origin-already-repaired-does-not-refuse: a clone that branched on origin's red lands after origin "
          "repaired it (%r)" % (err or out)[-400:])


def t_a_red_the_commit_makes_is_refused_on_the_landing_tree(tmp):
    for behind in (True, False):
        name = "plant_behind" if behind else "plant_level"
        work, up = landing_repo(tmp, name, commit_body="BAD\n")
        if not behind:
            g("pull", "-q", "--rebase", cwd=work)
        before = head_of(work)
        err, out = publish_call(work, ["src/other.txt"])
        check(bool(err) and "planted fault in src/other.txt" in err and "fix-ledger" in err
              and "line2 deleted" not in err and head_of(work) == before
              and head_of(os.path.join(tmp, name + ".git"), "main") == up,
              "a-red-the-commit-makes-is-refused-on-the-landing-tree (%s origin): refused naming the commit's fault only, "
              "commit undone, nothing pushed (%r)" % ("behind" if behind else "level with", (err or out)[-400:]))


def t_a_red_origin_has_not_repaired_is_still_refused(tmp):
    work, up = landing_repo(tmp, "unrepaired", origin_repairs=False)
    err, out = publish_call(work, ["src/other.txt"])
    check(bool(err) and "line2 deleted" in err and "fix-ledger" in err
          and head_of(os.path.join(tmp, "unrepaired.git"), "main") == up,
          "a-red-origin-has-not-repaired-is-still-refused: origin's own red refuses a clone behind it (%r)"
          % (err or out)[-400:])


CITE_CHECK = r'''import os, subprocess, sys
top = os.path.dirname(os.path.abspath(__file__))
for sha in open(os.path.join(top, "data", "cites.txt")).read().split():
    if subprocess.run(["git", "-C", top, "merge-base", "--is-ancestor", sha, "origin/main"]).returncode:
        print("FAIL SHA_NOT_ON_BASE %s does not resolve on origin/main" % sha[:12]); sys.exit(1)
print("ok every cited sha is on origin/main")
'''


def t_the_landing_tree_sees_origin_main_as_landed(tmp):
    """The first live run of the fix (2026-11-22 ~01:50 PST): selftest_modledger_tree.py read SHA_NOT_ON_BASE for a
    HOLDER shard line citing a sha on the real origin, because the throwaway checkout's origin/main was the clone's
    stale local main."""
    work, up = landing_repo(tmp, "cites")
    seed = os.path.join(tmp, "cites_seed")
    cfg_p = os.path.join(seed, P.TREE_CHECKS)
    cfg = json.load(open(cfg_p))
    cfg["checks"] = [{"test": "cite_check.py", "fix": "fix-cite"}]
    json.dump(cfg, open(cfg_p, "w"))
    script(seed, "cite_check.py", CITE_CHECK)
    script(seed, os.path.join("data", "cites.txt"), "")
    g("add", "-A", cwd=seed)
    g("commit", "-q", "-m", "a landed fix", cwd=seed)
    fixed = head_of(seed)
    script(seed, os.path.join("data", "cites.txt"), fixed + "\n")
    g("commit", "-q", "-am", "a ledger line cites the landed fix", cwd=seed)
    g("push", "-q", "origin", "HEAD:main", cwd=seed)
    err, out = publish_call(work, ["src/other.txt"])
    check(err is None and "PUBLISHED" in out,
          "the-landing-tree-sees-origin-main-as-landed: a sha on origin, cited in origin's tree, resolves on origin/main "
          "in the landing checkout of a clone behind it (%r)" % (err or out)[-400:])
    work2, _up = landing_repo(tmp, "cites_bad")
    seed2 = os.path.join(tmp, "cites_bad_seed")
    json.dump(cfg, open(os.path.join(seed2, P.TREE_CHECKS), "w"))
    script(seed2, "cite_check.py", CITE_CHECK)
    script(seed2, os.path.join("data", "cites.txt"), "0123456789abcdef0123456789abcdef01234567\n")
    g("add", "-A", cwd=seed2)
    g("commit", "-q", "-m", "a ledger line cites a sha nowhere", cwd=seed2)
    g("push", "-q", "origin", "HEAD:main", cwd=seed2)
    err, out = publish_call(work2, ["src/other.txt"])
    check(bool(err) and "SHA_NOT_ON_BASE" in err,
          "the-landing-tree-sees-origin-main-as-landed: a cited sha on no branch is still refused (%r)" % (err or out)[-300:])


def measured_readings_cases():
    """2026-11-23: selftest_game_lock's timing row, red on origin/main too, was refused as "new" because its 3-digit ms
    readings differed between the two runs (the blanking took only numbers of 4+ digits)."""
    a = ("FAIL a query answers in under 100 ms (median of 9, in one of up to three batches)  batch medians "
         "['581', '742', '629'] ms, CPU ['106', '111', '107'] ms")
    b = ("FAIL a query answers in under 100 ms (median of 9, in one of up to three batches)  batch medians "
         "['566', '560', '495'] ms, CPU ['102', '108', '108'] ms")
    ka, _ = P.red_signature(a + "\n", "/nowhere", 1)
    kb, _ = P.red_signature(b + "\n", "/nowhere", 1)
    check(ka == kb, "the same FAIL line with other timing readings is the same red (%s / %s)" % (list(ka), list(kb)))
    k1, _ = P.red_signature("FAIL unit 1 is wrong\n", "/nowhere", 1)
    k2, _ = P.red_signature("FAIL unit 2 is wrong\n", "/nowhere", 1)
    check(k1 != k2, "a short number that is not a reading still tells two FAIL lines apart")
    k3, _ = P.red_signature("FAIL took 3 of 9 rows\n", "/nowhere", 1)
    k4, _ = P.red_signature("FAIL took 4 of 9 rows\n", "/nowhere", 1)
    check(k3 != k4, "a count is kept")


def main():
    measured_readings_cases()
    for t in (t_the_door_judges_the_tree_that_lands, t_a_red_origin_already_repaired_does_not_refuse,
              t_the_landing_tree_sees_origin_main_as_landed,
              t_a_red_the_commit_makes_is_refused_on_the_landing_tree, t_a_red_origin_has_not_repaired_is_still_refused):
        with tempfile.TemporaryDirectory() as tmp:
            t(tmp)
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
        cfg_sh = {"budget_s": 30, "timeout_s": 2, "checks": [{"test": "green.py", "fix": "f"},
                  {"test": "red.py", "fix": "f", "shadow": True}]}
        json.dump(cfg_sh, open(os.path.join(tmp, P.TREE_CHECKS), "w"))
        err, out = call(tmp, ["src/a.py"])
        check(err is None and "shadow" in out and "planted fault" in out,
              "a shadow check prints its last line and refuses nothing (%r, %r)" % (err, out.strip()[-160:]))
        fixture(tmp, ["green.py", "red.py"])
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
        t_a_check_that_died_on_enomem_runs_again(tmp)
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
        # RIMMANDRAKE_MEASURE_FLOWWORKS_DIG_CALL_QUARTER_SECOND_ON_SITTING_MAP: a game-b run's unit carries
        # RM_GAME_INSTANCE=b and the rest of `game_instance.py env b`; selftest_game_lock, selftest_conductor_acts and
        # three more door tests read the caller's game from it and went red under it (measured 2026-11-21).
        game_vars = ("RM_GAME_INSTANCE", "RM_GAME_USERDATA", "RM_GAME_LOGDIR", "GABP_SERVER_PORT", "GABP_TOKEN",
                     "RIMFLOW_DRIVER_LOCK")
        script(tmp, "gamevars.py", "import os, sys\nw = [k for k in %r if k in os.environ]\n"
               "print('FAIL the publisher\\'s game choice leaked: %%s' %% w) if w else print('ok')\nsys.exit(1 if w else 0)\n"
               % (game_vars,))
        fixture(tmp, ["gamevars.py"])
        was = {k: os.environ.get(k) for k in game_vars}
        os.environ.update({k: "b" for k in game_vars})
        err, out = call(tmp, ["src/a.py"])
        for k, v in was.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        check(err is None and "1 green" in out, "a game-b publisher's game choice never reaches a door test (%r)" % err)
    cfg = json.load(open(os.path.join(HERE, "..", "..", "..", P.TREE_CHECKS)))
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    listed = [c["test"] for c in cfg["checks"] + cfg.get("nightly_only", [])]
    tracked = set(subprocess.run(["git", "-C", root, "ls-files", "--", *listed], capture_output=True, text=True,
                                 timeout=60).stdout.split())      # a sparse clone holds them in git, not on disk
    missing = [t for t in listed if not os.path.isfile(os.path.join(root, t)) and t not in tracked]
    check(not missing, "every listed test exists: %s" % missing)
    check(all(c.get("fix") for c in cfg["checks"]), "every listed check carries its fix")
    print("PASS" if not FAILS else "FAIL %d" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
