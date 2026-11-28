#!/usr/bin/env python3
"""selftest_check_tree_owner.py — a check tree goes when its owner ends, on every way the owner can end
(RIMMANDRAKE_SPEED_SCRATCH_REAP_SEAT_TMP_PUBLISH_CHECK_RESIDUE_2M).

The failure: ~/.seat-tmp/BENCH held about 2.0 M entries on 2026-11-27, 1.13 M of them in 279 folders named
publish_check_* (98) and wrong_check_* (181). ./publish makes a publish_check_ tree for each check and removed it in a
`finally`, which a SIGKILL or a SIGHUP skips. selftest_wrong_check_fixed_in_sitting.py makes its wrong_check_ tree at
import and removed it only at the end of its own main(), so each of the four selftests that import it left one on every
run. The scratch reap's fixture sweep knew neither name. Its borrower `find` walked them all: 129 s of 327 s.

Each test has the name of its promise on design/specs/2026-11-27-check-tree-owner/boundary.md. Pure: temp dirs, child
processes of its own, a fake reaper context; it never reads the real ~/.seat-tmp or the real owner registry."""
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RIMFLOW = HERE.parent / "rimflow"
sys.path[:0] = [str(HERE)]
F = []
# budget: danger=a child that never starts or never ends holds the selftest with no end; evidence=none measured;
# budget: longest=a few seconds (python start and the publish import at load 27, 2026-11-27); 600 s is over 10 times it
WAIT_S = 600


def ck(c, w):
    print(("PASS " if c else "FAIL ") + w)
    if not c:
        F.append(w)


OUTER = Path(tempfile.mkdtemp(prefix="selftest_check_tree_owner_"))
PUB_TMP = OUTER / "pubtmp"          # the publisher's TMPDIR: its check trees are made here
SEEN = OUTER / "seen"
TOP = OUTER / "top"                 # the fake landing tree that holds the fake checks
SEAT_ROOT = OUTER / ".seat-tmp"     # the reaper's fake reap root
SEAT = SEAT_ROOT / "BENCH"
for d in (PUB_TMP, SEEN, TOP, SEAT):
    d.mkdir(parents=True)
ENV = dict(os.environ, TMPDIR=str(PUB_TMP), SELFTEST_OWN_DIRS_REG=str(OUTER / "registry"),
           SCRATCH_REAP_ROOTS=str(SEAT_ROOT), SCRATCH_REAP_STATE=str(OUTER / "reapstate"))
os.environ.update({k: ENV[k] for k in ("TMPDIR", "SELFTEST_OWN_DIRS_REG", "SCRATCH_REAP_ROOTS", "SCRATCH_REAP_STATE")})
tempfile.tempdir = str(PUB_TMP)

# A check that says where its TMPDIR is, then sleeps until it is killed.
(TOP / "sleep_check.py").write_text("""import os, sys, tempfile, time
open(os.path.join(os.environ["SEEN_DIR"], "started.%d" % os.getpid()), "w").write(tempfile.gettempdir())
time.sleep(600)
""")
(TOP / "ok_check.py").write_text("import sys\nsys.exit(0)\n")
# A publisher in a process of its own: the signal handlers main() installs, then one sleeping check.
PUBLISHER = """import signal, sys
sys.path.insert(0, %r)
import publish as P
inst = getattr(P, "install_term_handlers", None)
if inst:
    inst()
else:
    signal.signal(signal.SIGTERM, P._on_term)       # what main() installed before this page
P._run_tree_checks(%r, {"timeout_s": 600, "checks": [{"test": "sleep_check.py"}]})
""" % (str(HERE), str(TOP))


def trees(prefix="publish_check_", root=PUB_TMP):
    return sorted(p for p in root.iterdir() if p.name.startswith(prefix))


def wait_for(pred, what):
    end = time.time() + WAIT_S
    while time.time() < end:
        got = pred()
        if got:
            return got
        time.sleep(0.2)
    raise RuntimeError("never happened in %d s: %s" % (WAIT_S, what))


def start_publisher():
    for f in SEEN.iterdir():
        f.unlink()
    p = subprocess.Popen([sys.executable, "-c", PUBLISHER], env=dict(ENV, SEEN_DIR=str(SEEN)),
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    started = wait_for(lambda: list(SEEN.glob("started.*")), "the publisher's check started")
    check_pid = int(started[0].name.split(".")[1])
    tree = Path(started[0].read_text().strip())
    return p, check_pid, tree


def kill_quietly(pid):
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def end_by(sig):
    """-> (the tree the check ran in, whether it is still there once the publisher has exited)."""
    p, check_pid, tree = start_publisher()
    os.kill(p.pid, sig)
    p.wait(timeout=WAIT_S)
    kill_quietly(check_pid)                     # a SIGKILLed publisher leaves its check running in its own session
    return tree, tree.exists()


def t_a_terminated_publish_leaves_no_tree():
    tree, left = end_by(signal.SIGTERM)
    ck(not left, "a-terminated-publish-leaves-no-tree: SIGTERM ends publish through its clean-up (%s left: %s)"
       % (tree.name, left))


def t_a_hangup_publish_leaves_no_tree():
    tree, left = end_by(signal.SIGHUP)
    ck(not left, "a-hangup-publish-leaves-no-tree: SIGHUP (a closed terminal) ends publish through its clean-up "
       "(%s left: %s)" % (tree.name, left))


def t_a_killed_publish_tree_goes_at_the_next_run():
    import publish as P
    tree, left = end_by(signal.SIGKILL)
    ck(left, "a-killed-publish-tree-goes-at-the-next-run: the SIGKILLed publisher's tree is there before the next run")
    P._run_tree_checks(str(TOP), {"timeout_s": 600, "checks": [{"test": "ok_check.py"}]})
    ck(not tree.exists(), "a-killed-publish-tree-goes-at-the-next-run: the next run of publish removes it (%s left: %s)"
       % (tree.name, tree.exists()))
    ck(trees() == [], "a-killed-publish-tree-goes-at-the-next-run: no check tree is left at all (%s)"
       % [t.name for t in trees()])


IMPORTER = """import sys, time
sys.path.insert(0, %r)
import selftest_wrong_check_fixed_in_sitting as S
print(S.TMP, flush=True)
if sys.argv[1:] == ["sleep"]:
    time.sleep(600)
""" % str(RIMFLOW)


def importer(*args):
    return subprocess.Popen([sys.executable, "-c", IMPORTER, *args], env=ENV, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True)


def t_an_imported_wrong_check_tree_goes_at_exit():
    p = importer()
    out, _ = p.communicate(timeout=WAIT_S)
    tmp = Path(out.strip().splitlines()[-1]) if out.strip() else None
    ck(tmp is not None and not tmp.exists(), "an-imported-wrong-check-tree-goes-at-exit: a selftest that imports "
       "selftest_wrong_check_fixed_in_sitting leaves no tree when it exits (%s exists: %s)"
       % (tmp, tmp is not None and tmp.exists()))


def t_a_killed_wrong_check_tree_goes_at_the_next_run():
    p = importer("sleep")
    tmp = Path(p.stdout.readline().strip())
    p.kill()
    p.wait(timeout=WAIT_S)
    ck(tmp.is_dir(), "a-killed-wrong-check-tree-goes-at-the-next-run: the SIGKILLed run's tree is there (%s)" % tmp)
    q = importer()
    q.communicate(timeout=WAIT_S)
    ck(not tmp.exists(), "a-killed-wrong-check-tree-goes-at-the-next-run: the next import removes it (%s exists: %s)"
       % (tmp.name, tmp.exists()))


OWNER = """import sys, time
sys.path.insert(0, %r)
import selftest_own_dirs as O
try:
    cm = O.own_dir("publish_check", dir=%r, prefix="publish_check_", signals=False)
except TypeError:
    cm = O.own_dir("publish_check", dir=%r)
with cm as d:
    open(d + "/work.txt", "w").write("x")
    print(d, flush=True)
    time.sleep(600)
""" % (str(HERE), str(SEAT), str(SEAT))


def fake_ctx(now, users=()):
    import scratch_reap as R
    ctx = R.Ctx.__new__(R.Ctx)
    ctx.now = now
    ctx.live = type("L", (), {"blind": [], "taken": time.time(), "users": lambda self, p: [p] if p in users else []})()
    ctx.borrows = type("B", (), {"hold": [], "taken": time.time(), "of": lambda self, p: []})()
    return ctx


def t_a_tree_whose_owner_lives_is_kept():
    import publish as P
    import scratch_reap as R
    p = subprocess.Popen([sys.executable, "-c", OWNER], env=ENV, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                         text=True)
    try:
        tree = Path(p.stdout.readline().strip())
        ck(tree.is_dir(), "a-tree-whose-owner-lives-is-kept: the live owner's tree exists (%s)" % tree)
        P._run_tree_checks(str(TOP), {"timeout_s": 600, "checks": [{"test": "ok_check.py"}]})   # it reaps on entry
        ck(tree.is_dir(), "a-tree-whose-owner-lives-is-kept: the next run of publish keeps it")
        out = R.sweep_fixtures(fake_ctx(time.time() + 3 * 86400), True, 0)
        ck(tree.is_dir(), "a-tree-whose-owner-lives-is-kept: the scratch reap's sweep keeps it three days on, "
           "untouched and used by no file handle (%r)" % out)
    finally:
        p.kill()
        p.wait(timeout=WAIT_S)


def t_an_aged_unmarked_check_tree_is_swept():
    import scratch_reap as R
    names = {"pub": "publish_check_ab12cd34", "wrong": "wrong_check_ef56gh78", "used": "publish_check_inuse123"}
    made = {}
    for k, n in names.items():
        d = SEAT / n
        (d / "sub").mkdir(parents=True)
        (d / "sub" / "f.txt").write_text("x")
        made[k] = d
    subprocess.run(["git", "init", "-q", str(made["pub"] / "sub")], check=True)   # a check's git fixture inside
    young = R.sweep_fixtures(fake_ctx(time.time()), True, 0)
    ck(all(d.is_dir() for d in made.values()), "an-aged-unmarked-check-tree-is-swept: a young one is kept (%r)" % young)
    later = time.time() + 3 * 86400
    out = R.sweep_fixtures(fake_ctx(later, users=(made["used"],)), True, 0)
    ck(not made["pub"].exists(), "an-aged-unmarked-check-tree-is-swept: an aged publish_check_ tree goes, a git "
       "fixture inside it too (%r)" % out)
    ck(not made["wrong"].exists(), "an-aged-unmarked-check-tree-is-swept: an aged wrong_check_ tree goes")
    ck(made["used"].is_dir(), "an-aged-unmarked-check-tree-is-swept: an aged one that a process uses is kept")


def main() -> int:
    try:
        for t in (t_a_terminated_publish_leaves_no_tree, t_a_hangup_publish_leaves_no_tree,
                  t_a_killed_publish_tree_goes_at_the_next_run, t_an_imported_wrong_check_tree_goes_at_exit,
                  t_a_killed_wrong_check_tree_goes_at_the_next_run, t_a_tree_whose_owner_lives_is_kept,
                  t_an_aged_unmarked_check_tree_is_swept):
            try:
                t()
            except Exception as e:                        # one broken case is a red, never a crash of the rest
                ck(False, "%s raised %r" % (t.__name__, e))
    finally:
        subprocess.run(["chmod", "-R", "u+rwx", str(OUTER)], capture_output=True)
        import shutil
        shutil.rmtree(OUTER, ignore_errors=True)
    print("selftest_check_tree_owner:", "FAIL" if F else "PASS", len(F))
    return 1 if F else 0


if __name__ == "__main__":
    sys.exit(main())
