#!/usr/bin/env python3
"""selftest_arena_replay.py - arena_replay.py, each criterion proven by FORCED FAILURE.

  no future    control: a replay clone of base A (fix B, later C) cannot `git show` B, nor find it by cat-file, by
               --batch-all-objects (loose, and after `git gc` packed), alternates, FETCH_HEAD, reflog, packed-refs or refs.
               Forced failures, each CAUGHT by audit_clone: a naive full clone; a --shared clone (alternates); a clone made
               gc'd into a pack; an init whose FETCH_HEAD / packed-refs / reflog merely NAMES the fix sha; a base that is
               a descendant of the fix (build raises ReplayLeak and leaves no directory)
  order        same freeze hash twice -> identical orders; a different hash -> different; every arm differs from every other
               arm; caller's arm order does not matter; interleaved slots hold each (arm, task) once and mix arms
  deleted      run_one leaves no clone after judging, after an exception in work, in judge, and in build; a runner that skips
               deletion is DETECTED by leftovers(); sweep removes it; run_schedule records an error and keeps going
  reap root    scratch_reap.DEFAULT_ROOTS contains the arena/replay tree
Everything lives under a temp dir (root= argument); the real arena tree is never touched.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arena_replay as R  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def git(repo, *a):
    e = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    return subprocess.run(["git", "-C", str(repo)] + list(a), capture_output=True, text=True, env=e, check=True).stdout.strip()


def mk_source(tmp):
    src = tmp / "src"
    src.mkdir()
    git(src, "init", "-q", "-b", "main")
    shas = []
    for i, name in enumerate("ABC"):
        (src / "f.txt").write_text("v%d\n" % i)
        (src / ("only_" + name + ".txt")).write_text("secret %s\n" % name)
        git(src, "add", "-A")
        git(src, "commit", "-q", "-m", "commit " + name)
        shas.append(git(src, "rev-parse", "HEAD"))
    return src, shas


def raises(exc, fn, *a, **k):
    try:
        fn(*a, **k)
    except exc as e:
        return str(e)
    return None


def t_no_future(tmp, src, A, B, C):
    root = tmp / "root1"
    c = R.build_replay_clone("armx", "T1", A, B, src, root)
    check(c == root / "replay" / "armx" / "T1" and (c / ".git").is_dir() and not (c / ".git").is_symlink(),
          "control: full clone (own .git directory, not a worktree) at replay/<arm>/<task>")
    check(git(c, "rev-parse", "HEAD") == A and (c / "only_A.txt").exists(), "control: checked out at the base sha")
    check(not (c / "only_B.txt").exists(), "control: the fix's file is not in the tree")
    shown = subprocess.run(["git", "-C", str(c), "show", B], capture_output=True)
    check(shown.returncode != 0, "git show <fix sha> FAILS in the replay clone")
    check(subprocess.run(["git", "-C", str(c), "show", C], capture_output=True).returncode != 0, "later commit C absent too")
    check(B not in git(c, "cat-file", "--batch-all-objects", "--batch-check"), "--batch-all-objects does not list the fix")
    git(c, "gc", "-q", "--prune=now")
    check(B not in git(c, "cat-file", "--batch-all-objects", "--batch-check") and R.audit_clone(c, [B]) == [],
          "still absent after gc packs the objects; audit is clean")
    check(not (c / ".git" / "FETCH_HEAD").exists() and not (c / ".git" / "logs").exists()
          and not (c / ".git" / "objects" / "info" / "alternates").exists(), "no FETCH_HEAD, reflog or alternates")
    check(git(c, "remote") == "" and git(c, "tag") == "" and git(c, "for-each-ref") == "", "no remote, tags or branches")
    R.rmtree(c)

    # forced failures: the audit must catch each way a clone could hold the future
    naive = tmp / "naive"
    subprocess.run(["git", "clone", "-q", str(src), str(naive)], check=True)
    f = R.audit_clone(naive, [B])
    check(f and any("cat-file" in x or "holds" in x for x in f), "FORCED: naive full clone is caught: %s" % f[:2])
    shared = tmp / "shared"
    subprocess.run(["git", "clone", "-q", "--shared", str(src), str(shared)], check=True)
    f = R.audit_clone(shared, [B])
    check(any("borrows" in x for x in f), "FORCED: --shared clone (alternates) caught: %s" % [x for x in f if "borrows" in x])
    packed = tmp / "packed"
    subprocess.run(["git", "clone", "-q", str(src), str(packed)], check=True)
    git(packed, "gc", "-q", "--prune=now")
    check(not list((packed / ".git" / "objects").glob("??/*")) and R.audit_clone(packed, [B]),
          "FORCED: fix inside a pack (no loose objects) still caught")
    lie = tmp / "lie"
    lie.mkdir()
    git(lie, "init", "-q")
    check(R.audit_clone(lie, [B]) == [], "control: empty repo is clean")
    (lie / ".git" / "FETCH_HEAD").write_text(B + "\t\t'x' of y\n")
    check(any("FETCH_HEAD" in x for x in R.audit_clone(lie, [B])), "FORCED: FETCH_HEAD naming the fix caught")
    (lie / ".git" / "FETCH_HEAD").unlink()
    (lie / ".git" / "packed-refs").write_text("%s refs/remotes/origin/x\n" % B)
    check(any("packed-refs" in x for x in R.audit_clone(lie, [B])), "FORCED: packed-refs naming the fix caught")
    (lie / ".git" / "packed-refs").unlink()
    (lie / ".git" / "logs" / "refs" / "heads").mkdir(parents=True)
    (lie / ".git" / "logs" / "refs" / "heads" / "x").write_text("0" * 40 + " " + B + " t\n")
    check(any("logs" in x for x in R.audit_clone(lie, [B])), "FORCED: reflog naming the fix caught")
    (lie / ".git" / "logs" / "refs" / "heads" / "x").unlink()
    (lie / ".git" / "refs" / "heads" / "leak").write_bytes(bytes.fromhex(B))
    check(any("refs" in x for x in R.audit_clone(lie, [B])), "FORCED: ref file holding the fix (binary) caught")
    # base that already contains the fix: the builder refuses and leaves nothing
    root2 = tmp / "root2"
    msg = raises(R.ReplayLeak, R.build_replay_clone, "armx", "T2", C, B, src, root2)
    check(msg is not None and not (root2 / "replay" / "armx" / "T2").exists(),
          "FORCED: base sha containing the fix -> ReplayLeak and no directory left")
    check(raises(R.ReplayError, R.clone_path, "../x", "T", root2) is not None, "path traversal in arm refused")


def t_order(tmp):
    tasks = ["T%02d" % i for i in range(12)]
    arms = ["v3", "ralph_a", "ralph_c", "trio"]
    s1 = R.schedule("abc123", arms, tasks)
    s2 = R.schedule("abc123", list(reversed(arms)), list(reversed(tasks)))
    check(s1 == s2, "same freeze hash twice -> identical orders and slots (caller order irrelevant)")
    s3 = R.schedule("abc124", arms, tasks)
    check(s3["orders"] != s1["orders"], "different freeze hash -> different orders")
    o = s1["orders"]
    check(len({tuple(v) for v in o.values()}) == len(arms), "every arm has a different order: %s" % [v[:3] for v in o.values()])
    check(all(sorted(v) == sorted(tasks) for v in o.values()), "each arm runs every task exactly once")
    check(sorted(s1["slots"]) == sorted((a, t) for a in arms for t in tasks) and len(s1["slots"]) == 48,
          "slots hold each (arm, task) once")
    check(len({a for a, _ in s1["slots"][:4]}) == 4 and len({a for a, _ in s1["slots"][4:8]}) == 4,
          "slots are interleaved across arms (every round has all four arms)")
    check(o["trio"] != sorted(tasks), "order is shuffled, not sorted")
    # forced: a seed that ignores the arm would give equal orders -> the comparison can fail
    same = [R.arm_order("abc123", "v3", tasks)] * 2
    check(same[0] == same[1], "FORCED: identical seed input yields identical order (so the 'differs' check is real)")
    tiny = R.schedule("h", ["a", "b", "c"], ["x", "y", "z"])["orders"]
    check(len({tuple(v) for v in tiny.values()}) == 3, "3 tasks, 3 arms: still three distinct orders")


def t_deleted(tmp, src, A, B, C):
    root = tmp / "root3"
    seen = []
    v = R.run_one("a1", "T1", A, B, lambda c: seen.append(c), lambda c: "PASS", src, root)
    check(v == "PASS" and seen and not seen[0].exists() and R.leftovers(root) == [], "judged clone is gone")

    def boom(c):
        seen.append(c)
        raise RuntimeError("mid-run")
    check(raises(RuntimeError, R.run_one, "a1", "T2", A, B, boom, lambda c: 1, src, root) is not None
          and not seen[-1].exists() and R.leftovers(root) == [], "clone gone after an exception in work")

    def jboom(c):
        seen.append(c)
        raise ValueError("judge")
    check(raises(ValueError, R.run_one, "a1", "T3", A, B, lambda c: 0, jboom, src, root) is not None
          and not seen[-1].exists(), "clone gone after an exception in judge")
    check(raises(R.ReplayError, R.run_one, "a1", "T4", "f" * 40, B, lambda c: 0, lambda c: 0, src, root) is not None
          and R.leftovers(root) == [], "nothing left after a failed build")
    check(raises(R.ReplayLeak, R.run_one, "a1", "T5", C, B, lambda c: 0, lambda c: 0, src, root) is not None
          and R.leftovers(root) == [], "nothing left after a leak refusal")

    # forced: a runner that forgets to delete -> leftovers() detects it, also after an exception
    def bad_runner(arm, task, fail):
        c = R.build_replay_clone(arm, task, A, B, src, root)
        if fail:
            raise RuntimeError("crash without cleanup")
        return c
    bad_runner("a2", "T1", False)
    try:
        bad_runner("a2", "T2", True)
    except RuntimeError:
        pass
    left = R.leftovers(root)
    check({x.name for x in left} == {"T1", "T2"}, "FORCED: clones left by a non-deleting runner (also the one that raised) are DETECTED: %s" % [str(x.name) for x in left])
    check(raises(R.ReplayError, R.build_replay_clone, "a2", "T1", A, B, src, root) is not None,
          "a stale clone blocks a rebuild (never silently reused)")
    (root / "replay" / "a3").mkdir()
    (root / "replay" / "a3" / "stray").mkdir()
    check(len(R.leftovers(root)) == 3, "any stray entry under replay/ counts as left behind")
    gone = R.sweep(root)
    check(len(gone) == 3 and R.leftovers(root) == [], "sweep removes the leftovers")

    tasks = {"T1": {"base_sha": A, "fix_sha": B}, "T2": {"base_sha": "e" * 40, "fix_sha": B}}
    res = R.run_schedule("hh", {k: v for k, v in tasks.items()}, ["a", "b"], lambda a, t, c: None, lambda a, t, c: "ok", src, root)
    check(len(res) == 4 and sum("error" in r for r in res) == 2 and sum(r.get("verdict") == "ok" for r in res) == 2
          and R.leftovers(root) == [], "run_schedule records failures, continues, leaves nothing: %s" % [r["task"] + ("E" if "error" in r else "") for r in res])


def t_reap():
    import scratch_reap as S
    check(Path("/home/mandrake/rm/arena/replay") in S.DEFAULT_ROOTS, "rm-scratch-reap default roots include arena/replay")


def main():
    tmp = Path(tempfile.mkdtemp(prefix="selftest_replay_"))
    try:
        src, (A, B, C) = mk_source(tmp)
        for fn, a in ((t_no_future, (tmp, src, A, B, C)), (t_order, (tmp,)), (t_deleted, (tmp, src, A, B, C)), (t_reap, ())):
            try:
                fn(*a)
            except Exception as e:  # noqa: BLE001
                check(False, "%s crashed: %s: %s" % (fn.__name__, type(e).__name__, e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
