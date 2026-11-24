#!/usr/bin/env python3
"""selftest_take_clone_half_made.py - a launch never fails because a pool clone's checkout is incomplete
(RIMMANDRAKE_REPLACE_HALF_MADE_POOL_CLONE_LAUNCH_FAILED_THRICE; design/specs/2026-11-23-half-made-pool-clone/boundary.md).

Real git in a temp dir: an origin with a ./sync at its root, pool clones of it damaged in each way, and take_clone run on
each. Only scratch_clone.py is faked (it refuses an existing path and else `git clone`s origin, as the real one does);
./sync and every git call run for real. Prints the cases it read."""
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import detached_helper as DH  # noqa: E402

FAILS = []
CASES = [0]


def check(ok, msg):
    CASES[0] += 1
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def git(cwd, *a):
    r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd, capture_output=True,
                       text=True)
    assert r.returncode == 0, (a, r.stderr)
    return r.stdout


class World:
    """origin + pool/clones; `runner` is what take_clone is given."""

    def __init__(self, tmp):
        self.origin = os.path.join(tmp, "origin")
        self.pool = os.path.join(tmp, "pool")
        self.retired = os.path.join(tmp, "retired-trees")
        os.makedirs(self.origin)
        os.makedirs(os.path.join(self.pool, "clones"))
        git(self.origin, "init", "-q", "-b", "main")
        with open(os.path.join(self.origin, "sync"), "w") as fh:
            fh.write("#!/bin/sh\nexit 0\n")
        os.chmod(os.path.join(self.origin, "sync"), 0o755)
        for i in range(12):
            with open(os.path.join(self.origin, "f%02d.txt" % i), "w") as fh:
                fh.write("file %d\n" % i)
        git(self.origin, "add", "-A")
        git(self.origin, "commit", "-q", "-m", "origin")
        self.scratch_calls = 0

    def dest(self, item):
        return os.path.join(self.pool, "clones", item + ".det")

    def runner(self, argv, **kw):
        if "scratch_clone.py" in " ".join(argv):
            self.scratch_calls += 1
            dest = os.path.join(self.pool, "clones", argv[argv.index("--name") + 1])
            if os.path.exists(dest):        # the real scratch_clone: RuntimeError(f"{dest} already exists")
                return subprocess.CompletedProcess(argv, 1, "", "%s already exists" % dest)
            git(self.pool, "clone", "-q", self.origin, dest)
            return subprocess.CompletedProcess(argv, 0, "made", "")
        return subprocess.run(argv, **kw)

    def whole_clone(self, item):
        d = self.dest(item)
        git(self.pool, "clone", "-q", self.origin, d)
        return d

    def take(self, item):
        os.environ["RM_DETACHED_POOL"] = self.pool
        os.environ["RM_RETIRED_TREES"] = self.retired
        try:
            return DH.take_clone(item, runner=self.runner)
        except Exception as e:  # noqa: BLE001
            return None, "RAISED %s: %s" % (type(e).__name__, e)
        finally:
            os.environ.pop("RM_DETACHED_POOL", None)
            os.environ.pop("RM_RETIRED_TREES", None)

    def usable(self, d):
        return bool(d) and os.path.isfile(os.path.join(d, "sync")) and os.path.isfile(os.path.join(d, "f05.txt"))

    def aside(self, root, item):
        if not os.path.isdir(root):
            return []
        return [n for n in os.listdir(root) if n.startswith(item)]


def t_a_complete_clone_is_reused_unchanged(w):
    d = w.whole_clone("A_COMPLETE")
    ino = os.stat(d).st_ino
    got, line = w.take("A_COMPLETE")
    check(got == d and w.usable(got) and os.stat(d).st_ino == ino and line.startswith("reused ") and
          w.scratch_calls == 0 and not w.aside(os.path.join(w.pool, "clones"), "A_COMPLETE.det.") and
          not w.aside(w.retired, "A_COMPLETE"),
          "complete clone: reused unchanged, nothing moved, no new clone (%s)" % line[:80])


def case_half_no_work(w):
    # the failure that happened: a checkout that died partway: HEAD set, no files, no index, no ./sync
    d = w.dest("B_HALF")
    git(w.pool, "clone", "-q", "--no-checkout", w.origin, d)
    check(not os.path.exists(os.path.join(d, "sync")), "half-made fixture has no ./sync")
    got, line = w.take("B_HALF")
    side = w.aside(os.path.join(w.pool, "clones"), "B_HALF.det.")
    check(got == d and w.usable(got) and not line.startswith("RAISED"),
          "half-made clone holding no work: the launch ends with a usable clone (%s)" % line[:160])
    check(len(side) == 1 and os.path.isdir(os.path.join(w.pool, "clones", side[0], ".git")),
          "half-made clone holding no work: moved aside beside the pool, not deleted (%s)" % side)
    check("half-made" in line and "\n" not in line.strip(), "half-made clone: said in one line (%s)" % line[:160])


def case_half_files_deleted_no_work(w):
    # index populated, working tree emptied (23,639 files missing): deletions alone are not work
    d = w.whole_clone("C_DELETED")
    for n in os.listdir(d):
        if n != ".git":
            os.remove(os.path.join(d, n))
    got, line = w.take("C_DELETED")
    check(got == d and w.usable(got) and not w.aside(w.retired, "C_DELETED"),
          "half-made (every file deleted): usable clone, nothing sent to retired-trees (%s)" % line[:120])


def case_half_with_commit(w):
    d = w.whole_clone("D_COMMIT")
    with open(os.path.join(d, "mine.txt"), "w") as fh:
        fh.write("local work\n")
    git(d, "add", "mine.txt")
    git(d, "commit", "-q", "-m", "local commit origin lacks")
    sha = git(d, "rev-parse", "HEAD").strip()
    os.remove(os.path.join(d, "sync"))
    got, line = w.take("D_COMMIT")
    kept = w.aside(w.retired, "D_COMMIT")
    holds = bool(kept) and subprocess.run(["git", "cat-file", "-e", sha], cwd=os.path.join(w.retired, kept[0]),
                                          capture_output=True).returncode == 0
    check(got == d and w.usable(got) and "mine.txt" not in os.listdir(got),
          "half-made clone with a local commit: fresh clone used (%s)" % line[:120])
    check(holds, "half-made clone with a local commit: moved to retired-trees with the commit intact (%s)" % kept)


def case_half_with_changed_file(w):
    d = w.whole_clone("E_CHANGED")
    with open(os.path.join(d, "f03.txt"), "w") as fh:
        fh.write("edited by a run\n")
    os.remove(os.path.join(d, "sync"))
    got, line = w.take("E_CHANGED")
    kept = w.aside(w.retired, "E_CHANGED")
    edited = bool(kept) and open(os.path.join(w.retired, kept[0], "f03.txt")).read() == "edited by a run\n"
    check(got == d and w.usable(got) and edited,
          "half-made clone with a changed file: edit kept in retired-trees, fresh clone used (%s)" % line[:120])


def case_half_with_untracked_file(w):
    d = w.whole_clone("F_UNTRACKED")
    with open(os.path.join(d, "notes.md"), "w") as fh:
        fh.write("not committed\n")
    os.remove(os.path.join(d, "sync"))
    got, line = w.take("F_UNTRACKED")
    kept = w.aside(w.retired, "F_UNTRACKED")
    check(got == d and w.usable(got) and kept and os.path.isfile(os.path.join(w.retired, kept[0], "notes.md")),
          "half-made clone with an untracked file: kept in retired-trees (%s)" % line[:120])


def t_a_directory_with_no_git_is_moved_aside_and_replaced(w):
    d = w.dest("G_NOGIT")
    os.makedirs(os.path.join(d, "sub"))
    with open(os.path.join(d, "sub", "x.txt"), "w") as fh:
        fh.write("x\n")
    got, line = w.take("G_NOGIT")
    kept = w.aside(w.retired, "G_NOGIT")
    check(got == d and w.usable(got) and kept and os.path.isfile(os.path.join(w.retired, kept[0], "sub", "x.txt")),
          "directory with no .git: contents moved to retired-trees, fresh clone made (%s)" % line[:120])
    d = w.dest("H_EMPTYDIR")
    os.makedirs(d)
    got, line = w.take("H_EMPTYDIR")
    check(got == d and w.usable(got), "empty directory with no .git: fresh clone made (%s)" % line[:120])


def t_a_stale_lock_file_never_blocks_a_launch(w):
    d = w.whole_clone("I_LOCK")
    code = ("import sys; sys.path.insert(0, %r); import detached_helper as D\n"
            "with D.clone_lock(%r): pass\n") % (HERE, d)
    subprocess.run([sys.executable, "-c", code], check=True)       # the holder ran and died, the file stays
    check(os.path.exists(DH.clone_lock_path(d)), "stale lock fixture: the lock file is left behind")
    t0 = time.time()
    got = None
    with DH.clone_lock(d):      # the dead holder's file never blocks (flock dies with its holder)
        got, line = w.take("I_LOCK")
    check(got == d and w.usable(got) and time.time() - t0 < 30,
          "stale lock file, holder dead: the launch is not blocked (%.1f s)" % (time.time() - t0))


def t_a_half_made_clone_is_replaced_not_failed(w):
    case_half_no_work(w)
    case_half_files_deleted_no_work(w)


def t_a_half_made_clone_holding_work_is_never_destroyed(w):
    case_half_with_commit(w)
    case_half_with_changed_file(w)
    case_half_with_untracked_file(w)


def main():
    with tempfile.TemporaryDirectory(prefix="half_made_clone_") as tmp:
        w = World(tmp)
        t_a_complete_clone_is_reused_unchanged(w)
        t_a_half_made_clone_is_replaced_not_failed(w)
        t_a_half_made_clone_holding_work_is_never_destroyed(w)
        t_a_directory_with_no_git_is_moved_aside_and_replaced(w)
        t_a_stale_lock_file_never_blocks_a_launch(w)
    print("%s: %d failure(s) of %d checks read (cases: complete, half-made no work, all files deleted, local commit, "
          "changed file, untracked file, no .git (full and empty), stale lock)"
          % ("FAIL" if FAILS else "PASS", len(FAILS), CASES[0]))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
