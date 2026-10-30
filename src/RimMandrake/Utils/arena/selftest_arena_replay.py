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
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import arena_replay as R  # noqa: E402

FAILS = []
H1, H2, H3 = "a" * 63 + "b", "a" * 63 + "c", "d" * 64


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
    s1 = R.schedule(H1, arms, tasks)
    s2 = R.schedule(H1, list(reversed(arms)), list(reversed(tasks)))
    check(s1 == s2, "same freeze hash twice -> identical orders and slots (caller order irrelevant)")
    s3 = R.schedule(H2, arms, tasks)
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
    same = [R.arm_order(H1, "v3", tasks)] * 2
    check(same[0] == same[1], "FORCED: identical seed input yields identical order (so the 'differs' check is real)")
    tiny = R.schedule(H3, ["a", "b", "c"], ["x", "y", "z"])["orders"]
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
    check(len(gone) == 2 and [x.name for x in R.leftovers(root)] == ["stray"], "sweep removes the marked leftovers and leaves the unmarked stray dir")
    R.rmtree(root / "replay" / "a3")

    tasks = {"T1": {"base_sha": A, "fix_sha": B}, "T2": {"base_sha": "e" * 40, "fix_sha": B}}
    res = R.run_schedule(H3, {k: v for k, v in tasks.items()}, ["a", "b"], lambda a, t, c: None, lambda a, t, c: "ok", src, root)
    check(len(res) == 4 and sum("error" in r for r in res) == 2 and sum(r.get("verdict") == "ok" for r in res) == 2
          and R.leftovers(root) == [], "run_schedule records failures, continues, leaves nothing: %s" % [r["task"] + ("E" if "error" in r else "") for r in res])


def t_reap():
    import scratch_reap as S
    check(Path("/home/mandrake/rm/arena/replay") in S.DEFAULT_ROOTS, "rm-scratch-reap default roots include arena/replay")


def t_round1(tmp, src, A, B, C):
    import threading
    import time
    root = tmp / "r1"
    # D1a: two runs of the same (arm, task): the second refuses and the first's clone survives untouched
    started, release, box = threading.Event(), threading.Event(), {}

    def slow_work(c):
        (c / "mine.txt").write_text("first run's work")
        started.set()
        release.wait(20)

    def first():
        box["v"] = R.run_one("a1", "T1", A, B, slow_work, lambda c: "J1", src, root)
    th = threading.Thread(target=first)
    th.start()
    started.wait(20)
    err = raises(R.ReplayExists, R.run_one, "a1", "T1", A, B, lambda c: None, lambda c: "J2", src, root)
    live = root / "replay" / "a1" / "T1"
    check(err is not None and (live / "mine.txt").exists(), "D1 FORCED: second concurrent run refuses and the first clone is untouched")
    err2 = raises(R.ReplayExists, R.build_replay_clone, "a1", "T1", A, B, src, root)
    check(err2 is not None and (live / "mine.txt").exists(), "D1: a direct build onto a live clone refuses, deletes nothing")
    release.set()
    th.join(30)
    check(box.get("v") == "J1" and not live.exists(), "D1: the first run still judges and cleans up its own clone")
    # D1b: pre-existing directory at the clone path (e.g. a SIGKILLed run's leftover): refused, not deleted
    pre = root / "replay" / "a2" / "T1"
    pre.mkdir(parents=True)
    (pre / "keep.txt").write_text("x")
    ran = []
    err = raises(R.ReplayError, R.run_one, "a2", "T1", A, B, lambda c: ran.append(1), lambda c: 0, src, root)
    check(err is not None and (pre / "keep.txt").exists() and not ran, "D1 FORCED: pre-existing dir at the clone path refused and kept")
    # D1c: symlinked arm dir: refused; the link target survives
    victim = tmp / "victim"
    victim.mkdir()
    (victim / "T1").mkdir()
    (victim / "T1" / "precious").write_text("p")
    (root / "replay" / "a3").symlink_to(victim)
    err = raises(R.ReplayError, R.run_one, "a3", "T1", A, B, lambda c: 0, lambda c: 0, src, root)
    check(err is not None and "symlink" in err and (victim / "T1" / "precious").exists(), "D1/L5 FORCED: symlinked arm dir refused, target intact")
    # L1: whitespace / newline / NUL
    for bad in ("a1\n", "a 1", "a\x001", "a1\t"):
        check(raises(R.ReplayError, R.clone_path, bad, "T", root) is not None, "L1: arm %r refused" % bad)
    check(raises(R.ReplayError, R.clone_path, "a", "T\n", root) is not None, "L1: task with trailing newline refused")
    check(raises(R.ReplayError, R.build_replay_clone, "q", "T", A + "\n", B, src, root) is not None, "L1: sha with trailing newline refused")
    check(raises(R.ReplayError, R.build_replay_clone, "q", "T", A, " " + B, src, root) is not None, "L1: sha with leading space refused")
    check(raises(R.ReplayError, R.audit_clone, tmp, [B + "\n"]) is not None, "L1: forbidden sha with newline refused")
    # L2
    check(R.schedule(" " + H1.upper() + "\n", ["a"], ["x", "y"]) == R.schedule(H1, ["a"], ["x", "y"]), "L2: freeze hash stripped + lowercased")
    for bad in ("abc123", "", "g" * 64, "a" * 63, "a" * 65):
        check(raises(R.ReplayError, R.schedule, bad, ["a"], ["x"]) is not None, "L2: freeze hash %r refused" % bad[:8])
    # L3
    check(raises(R.ReplayError, R.arena_root, "/mnt") is not None and raises(R.ReplayError, R.arena_root, "/mnt/d/x") is not None,
          "L3: /mnt and /mnt/* refused")
    check(raises(R.ReplayError, R.arena_root, "rel/arena") is not None, "L3: relative root refused")
    os.environ["RM_ARENA_ROOT"] = "relative/arena"
    check(raises(R.ReplayError, R.arena_root) is not None, "L3: relative RM_ARENA_ROOT refused")
    del os.environ["RM_ARENA_ROOT"]
    # L4: GIT_* in the environment neither causes a false leak nor hides a real one
    c = R.build_replay_clone("e1", "T1", A, B, src, tmp / "r2")
    os.environ["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = str(src / ".git" / "objects")
    os.environ["GIT_DIR"] = str(src / ".git")
    try:
        check(R.audit_clone(c, [B]) == [], "L4: env alternates/GIT_DIR cannot make a clean clone look leaky")
        naive = tmp / "naive4"
        subprocess.run(["git", "clone", "-q", str(src), str(naive)], check=True, env={k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
        check(R.audit_clone(naive, [B]) != [], "L4: env cannot hide a real leak")
        clean_env_clone = R.audit_clone(c, [B])
    finally:
        del os.environ["GIT_ALTERNATE_OBJECT_DIRECTORIES"], os.environ["GIT_DIR"]
    # D4: no url/include in the clone config, nothing names the source or the mirror, fetch came from the private mirror
    cfg = (c / ".git" / "config").read_text()
    check("url" not in cfg and "include" not in cfg and str(src) not in cfg, "D4: clone config names no url/include/source")
    mir = list((tmp / "private").glob("mirror_*.git"))
    check(len(mir) == 1 and oct((tmp / "private").stat().st_mode & 0o777) == "0o700", "D4: harness-private mirror exists, dir mode 0700")
    f = R.audit_clone(c, [B], masked=[str(src)])
    check(f == [], "D4: audit with masked source path clean")
    (c / ".git" / "config").write_text(cfg + "[include]\n\tpath = %s/.git/config\n" % src)
    check(any("include" in x for x in R.audit_clone(c, [B])), "D4 FORCED: [include] in clone config caught")
    (c / ".git" / "config").write_text(cfg + '[remote "o"]\n\turl = %s\n' % src)
    check(any("url" in x or "remote" in x for x in R.audit_clone(c, [B])), "D4 FORCED: remote url naming the source caught")
    (c / ".git" / "config").write_text(cfg)
    (c / ".git" / "stray").write_text("fetched from %s\n" % src)
    check(any("names the source" in x for x in R.audit_clone(c, [B], masked=[str(src)])), "D4 FORCED: a .git file naming the source caught")
    m = R.sandbox_masks(src)
    check(str(src) in m and str(tmp / "private") in m and "/home/mandrake/rm/bench" in m, "D4: sandbox_masks lists source, private dir, bench")
    t_masks_cover_old_history(tmp)
    R.rmtree(c)


def covered(path, masks):
    p = str(path).rstrip("/")
    return any(p == x or p.startswith(x.rstrip("/") + "/") for x in masks)


def t_masks_cover_old_history(tmp):
    """ARENA_SANDBOX_HARDEN_RETIRED_TREES_VISIBLE: every old-history repo (the pinned replay fixes) is masked."""
    import arena_tasks as T
    m = R.sandbox_masks()
    for e in T.OLD_HISTORY_DEFAULT:
        check(covered(R.glob_dir(e), m), "D5: OLD_HISTORY_DEFAULT entry %s masked at %s" % (e, R.glob_dir(e)))
    repos = T.old_history_repos()
    check(len(repos) >= 1, "D5 sanity: old_history_repos() sees at least one repo (%d)" % len(repos))
    for p in repos:
        check(str(p) in m, "D5: old-history repo %s listed in sandbox_masks" % p)
    check(R.RETIRED_TREES in m and R.CLAUDEWORK_ROOT in m, "D5: retired-trees root and ClaudeWork notes root masked")
    check(not covered(str(R.arena_root() / "tasks"), m), "D5: the arena root itself is not masked (arms read tasks)")
    # FORCED: a NEW default entry (a glob and a plain dir) appears in the masks without touching sandbox_masks
    new_glob, new_dir = tmp / "oldh" / "*-git-*", tmp / "oldh2"
    (tmp / "oldh" / "x-git-1").mkdir(parents=True)
    new_dir.mkdir()
    saved = T.OLD_HISTORY_DEFAULT
    try:
        T.OLD_HISTORY_DEFAULT = saved + (str(new_glob), str(new_dir))
        m2 = R.sandbox_masks()
    finally:
        T.OLD_HISTORY_DEFAULT = saved
    check(covered(tmp / "oldh" / "x-git-1", m2) and str(tmp / "oldh") in m2 and str(new_dir) in m2,
          "D5 FORCED: a new OLD_HISTORY_DEFAULT glob + dir are masked with no edit to sandbox_masks")
    check(not covered(tmp / "oldh" / "x-git-1", m), "D5 FORCED sanity: the new entry was not masked before")


def t_reaper_marker(tmp, src, A, B):
    import json
    import scratch_reap as S
    root = tmp / "r3"
    # a run that is SIGKILLed mid-work leaves a marked clone
    code = ("import sys,os,time,signal\nsys.path.insert(0,%r)\nimport arena_replay as R\n"
            "def w(c):\n    print('READY',flush=True)\n    time.sleep(60)\n"
            "R.run_one('k1','T1',%r,%r,w,lambda c:0,%r,%r)\n") % (str(HERE), A, B, str(src), str(root))
    pr = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, text=True, env=dict(os.environ))
    pr.stdout.readline()
    pr.kill()
    pr.wait()
    left = root / "replay" / "k1" / "T1"
    marker = left / ".git" / "rm_arena_replay.json"
    check(left.is_dir() and marker.is_file(), "SIGKILLed run leaves a clone with the harness marker")
    d = json.loads(marker.read_text())
    check(len(d["nonce"]) == 32 and d["created"] > 0, "marker holds nonce + created time")
    os.environ["SCRATCH_REAP_ROOTS"] = str(root / "replay")
    os.environ["SCRATCH_REAP_REPLAY_ROOTS"] = str(root / "replay")
    try:
        now = time.time()
        (left / "work.txt").write_text("arm output")           # untracked work: normal rules would refuse
        j = S.judge("clone", left, [], now + 7 * 3600)
        check(j["verdict"] == "DELETE", "D2: marked replay clone > 6 h with no remote/untracked work is reapable: %s" % j["why"][:1])
        check(S.judge("clone", left, [], now + 3600)["verdict"] == "YOUNG", "D2: marked clone younger than 6 h is YOUNG")
        os.environ["SCRATCH_REAP_REPLAY_TTL_HOURS"] = "1"
        check(S.judge("clone", left, [], now + 7 * 3600)["verdict"] == "DELETE", "D2: TTL is configurable")
        del os.environ["SCRATCH_REAP_REPLAY_TTL_HOURS"]
        saved = marker.read_text()
        marker.unlink()
        j = S.judge("clone", left, [], now + 48 * 3600)
        check(j["verdict"] == "REFUSE" and any("no remote" in w for w in j["why"]), "D2 FORCED: clone WITHOUT marker still protected (no remote)")
        marker.write_text(saved)
        # non-replay root: same marked clone under an ordinary scratch root stays protected
        os.environ["SCRATCH_REAP_REPLAY_ROOTS"] = str(tmp / "elsewhere")
        j = S.judge("clone", left, [], now + 48 * 3600)
        check(j["verdict"] == "REFUSE", "D2 FORCED: marked clone under a non-replay root still REFUSED")
        os.environ["SCRATCH_REAP_REPLAY_ROOTS"] = str(root / "replay")
        marker.write_text('{"nonce": "xx", "created": 1}')
        check(S.judge("clone", left, [], now + 48 * 3600)["verdict"] == "REFUSE", "D2 FORCED: malformed marker (bad nonce) not trusted")
        marker.write_text(saved)
        # --apply actually deletes it, even with a chmod-000 dir left by a judge
        (left / "locked").mkdir()
        (left / "locked" / "f").write_text("x")
        os.chmod(left / "locked", 0)
        rc = None
        os.environ["SCRATCH_REAP_STATE"] = str(tmp / "reapstate")
        os.environ["SCRATCH_REAP_CORPUS"] = str(tmp / "nocorpus")
        old = time.time() - 8 * 3600
        d["created"] = old
        marker.write_text(json.dumps(d))
        for dp in (left, left / ".git"):
            os.utime(dp, (old, old))
        for f in list(left.rglob("*")):
            if f.name != "locked" and f.parent.name != "locked":
                try:
                    os.utime(f, (old, old), follow_symlinks=False)
                except OSError:
                    pass
        os.utime(left / "locked", (old, old))
        rc = S.main(["--apply"])
        check(not left.exists(), "D2: scratch_reap --apply deletes the SIGKILL leftover (rc=%s)" % rc)
    finally:
        for k in ("SCRATCH_REAP_ROOTS", "SCRATCH_REAP_REPLAY_ROOTS", "SCRATCH_REAP_STATE", "SCRATCH_REAP_CORPUS", "SCRATCH_REAP_REPLAY_TTL_HOURS"):
            os.environ.pop(k, None)


def t_rmtree(tmp):
    d = tmp / "rm1"
    (d / "locked" / "sub").mkdir(parents=True)
    (d / "locked" / "sub" / "f").write_text("x")
    os.chmod(d / "locked" / "sub", 0)
    os.chmod(d / "locked", 0)
    R.rmtree(d)
    check(not d.exists(), "D3 FORCED: tree with chmod-000 dirs is deleted (no TypeError on this Python %s)" % sys.version.split()[0])
    d = tmp / "rm2"
    (d / "ro").mkdir(parents=True)
    (d / "ro" / "f").write_text("x")
    os.chmod(d / "ro" / "f", 0o400)
    os.chmod(d / "ro", 0o500)
    os.chmod(d, 0o500)
    R.rmtree(d)
    check(not d.exists(), "D3 FORCED: read-only tree is deleted")
    # the handler itself accepts both signatures
    d = tmp / "rm3"
    d.mkdir()
    (d / "f").write_text("x")
    os.chmod(d, 0o500)
    R._on_rm_error(os.unlink, str(d / "f"), (OSError, OSError("x"), None))
    check(not (d / "f").exists(), "D3: handler works with the onerror (exc_info tuple) signature")
    os.chmod(d, 0o700)
    (d / "g").write_text("x")
    os.chmod(d, 0o500)
    R._on_rm_error(os.unlink, str(d / "g"), OSError("x"))
    check(not (d / "g").exists(), "D3: handler works with the onexc (exception) signature")
    R.rmtree(d)


def t_round2(tmp, src, A, B, C):
    import json
    import signal
    import hashlib
    import scratch_reap as S
    root = tmp / "r4"
    rep = root / "replay"

    # (2) sweep: symlinked replay / arm dirs, unmarked dirs, a live run's clone
    victim = tmp / "victim"
    (victim / "k" / "t").mkdir(parents=True)
    (victim / "k" / "t" / "keep.txt").write_text("x")
    root.mkdir()
    os.symlink(victim, rep)
    R.sweep(root)
    check((victim / "k" / "t" / "keep.txt").exists(), "R2-2 FORCED: symlinked replay dir: sweep deletes nothing behind it")
    os.unlink(rep)
    rep.mkdir()
    os.symlink(victim / "k", rep / "linkarm")
    R.sweep(root)
    check((victim / "k" / "t" / "keep.txt").exists(), "R2-2 FORCED: symlinked arm dir: sweep deletes nothing behind it")
    os.unlink(rep / "linkarm")
    seen = {}

    def w(c):
        seen["gone"] = R.sweep(root)
        seen["alive"] = c.is_dir() and (c / ".git" / "rm_arena_replay.json").is_file()
    R.run_one("live", "T1", A, B, w, lambda c: 0, src, root)
    check(seen.get("gone") == [] and seen.get("alive"), "R2-2 FORCED: sweep during a live run (lock held) leaves the active clone: %s" % seen)

    # (3) marker mutated / mistyped: the run still removes its own clone
    for label, payload in (("list", "[1,2]"), ("garbage", "\x00not json"), ("other nonce", '{"nonce":"%s","created":1}' % ("0" * 32))):
        def w3(c, payload=payload):
            (c / ".git" / "rm_arena_replay.json").write_text(payload)
        res = raises(Exception, R.run_one, "mk", "T1", A, B, w3, lambda c: 0, src, root)
        check(res is None and not (rep / "mk" / "T1").exists(), "R2-3 FORCED: marker %s: run removes its own clone, no crash (%s)" % (label, res))
    # reaper side: a list marker is just 'not a marker', not an AttributeError
    c = rep / "mk2" / "T1"
    (c / ".git").mkdir(parents=True)
    (c / ".git" / "rm_arena_replay.json").write_text("[1]")
    os.environ["SCRATCH_REAP_REPLAY_ROOTS"] = str(rep)
    try:
        check(S.replay_clone_marked(c, time.time() + 99 * 3600) is False, "R2-3 FORCED: scratch_reap on a list marker -> False, no AttributeError")
    finally:
        os.environ.pop("SCRATCH_REAP_REPLAY_ROOTS", None)
    shutil.rmtree(rep / "mk2")
    # a clone renamed away mid-run: nothing at the path -> run neither crashes nor deletes anything else; replaced dir refused
    def w3b(c):
        os.rename(c, c.parent / "moved")
        os.mkdir(c)
        (c / "other.txt").write_text("not ours")
    res = raises(R.ReplayError, R.run_one, "rn", "T1", A, B, w3b, lambda c: 0, src, root)
    check(res is not None and (rep / "rn" / "T1" / "other.txt").exists(), "R2-3 FORCED: dir swapped in at the clone path is NOT deleted (%s)" % res)
    R.rmtree(rep / "rn")

    # (4) SIGKILL during the build: the marker is already there ('building'), reaper takes it after the TTL
    code = ("import sys,os,signal\nsys.path.insert(0,%r)\nimport arena_replay as R\n"
            "orig=R._git\n"
            "def g(repo,*a,**k):\n    if 'fetch' in a and '--no-write-fetch-head' in a: os.kill(os.getpid(),signal.SIGKILL)\n    return orig(repo,*a,**k)\n"
            "R._git=g\nR.build_replay_clone('kb','T1',%r,%r,%r,%r)\n") % (str(HERE), A, B, str(src), str(root))
    pr = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=dict(os.environ))
    left = rep / "kb" / "T1"
    mk = left / ".git" / "rm_arena_replay.json"
    check(pr.returncode == -signal.SIGKILL and mk.is_file(), "R2-4 FORCED: SIGKILL mid-build (rc=%s) leaves a clone WITH a marker" % pr.returncode)
    d = json.loads(mk.read_text()) if mk.is_file() else {}
    check(d.get("state") == "building", "R2-4 marker state is 'building'")
    os.environ["SCRATCH_REAP_REPLAY_ROOTS"] = str(rep)
    try:
        now = time.time()
        check(S.replay_clone_marked(left, now + 7 * 3600) is True, "R2-4 reaper takes a 'building' clone older than the TTL")
        check(S.replay_clone_marked(left, now + 60) is False, "R2-4 reaper leaves a 'building' clone younger than the TTL")
    finally:
        os.environ.pop("SCRATCH_REAP_REPLAY_ROOTS", None)
    check(R.sweep(root) == [left], "R2-4 sweep (lock free, marker valid) removes the dead build")
    ok = R.build_replay_clone("kc", "T1", A, B, src, root)
    check(json.loads((ok / ".git" / "rm_arena_replay.json").read_text())["state"] == "ready", "R2-4 finished build is state 'ready'")
    R.rmtree(ok)

    # (6) work()/judge() get a scrubbed environment
    os.environ["GIT_DIR"] = "/nonexistent"
    os.environ["GIT_ALTERNATE_OBJECT_DIRECTORIES"] = str(src / ".git" / "objects")
    envs = []
    try:
        R.run_one("en", "T1", A, B, lambda c: envs.append(dict(os.environ)), lambda c: envs.append(dict(os.environ)), src, root)
    finally:
        os.environ.pop("GIT_DIR", None)
        os.environ.pop("GIT_ALTERNATE_OBJECT_DIRECTORIES", None)
    check(len(envs) == 2 and all(not any(k.startswith("GIT_") and k not in ("GIT_CONFIG_NOSYSTEM", "GIT_CONFIG_GLOBAL", "GIT_TERMINAL_PROMPT") for k in e)
                                 and e.get("GIT_CONFIG_NOSYSTEM") == "1" and e.get("GIT_CONFIG_GLOBAL") == "/dev/null"
                                 and e.get("HOME") != os.environ.get("HOME") for e in envs),
          "R2-6 FORCED: work/judge see no inherited GIT_*, nosystem/global config, private HOME")
    check("GIT_DIR" not in os.environ, "R2-6 environment restored afterwards")

    # (7) audit: git errors fail closed; hooksPath / filter / fsmonitor / includeIf refused
    c = R.build_replay_clone("au", "T1", A, B, src, root)
    check(R.audit_clone(c, [B]) == [], "R2-7 control: clean clone audits clean")
    (c / ".git" / "HEAD").write_text("garbage\n")
    f = R.audit_clone(c, [B])
    check(any("audit failure" in x or "no real" in x for x in f), "R2-7 FORCED: broken repo (git errors) -> audit failure, not 'absent': %s" % f[:1])
    R.rmtree(c)
    for label, extra in (("hooksPath", "[core]\n\thooksPath = /x\n"), ("filter", "[filter \"x\"]\n\tclean = cat\n"),
                         ("fsmonitor", "[core]\n\tfsmonitor = /x\n"), ("includeIf", "[includeIf \"gitdir:/\"]\n\tpath = /x\n"),
                         ("textconv", "[diff \"y\"]\n\ttextconv = cat\n")):
        c = R.build_replay_clone("au", "T1", A, B, src, root)
        with open(c / ".git" / "config", "a") as fh:
            fh.write(extra)
        f = R.audit_clone(c, [B])
        check(len(f) > 0, "R2-7 FORCED: config with %s refused: %s" % (label, f[:1]))
        R.rmtree(c)

    # (9) orders independent of the arm set; collision path via a fake hash
    tasks = ["T%02d" % i for i in range(8)]
    o_full = R.schedule(H1, ["a", "b", "c", "d"], tasks)["orders"]
    o_one = R.schedule(H1, ["c"], tasks)["orders"]
    check(o_full["c"] == o_one["c"] == R.arm_order(H1, "c", tasks), "R2-9 an arm's order does not depend on the other arms")
    check(R.arm_seed(H1, "c") == int.from_bytes(hashlib.sha256(("%s|c" % H1).encode()).digest()[:8], "big"), "R2-9 seed is sha256(freeze|arm)")
    real = R._HASH
    R._HASH = lambda b: real(b"same") if b.count(b"|") == 1 else real(b)     # every unsalted seed collides
    try:
        s1 = R.schedule(H1, ["a", "b", "c"], tasks)["orders"]
        s2 = R.schedule(H1, ["c", "b", "a"], tasks)["orders"]
        check(len({tuple(v) for v in s1.values()}) == 3 and s1 == s2, "R2-9 FORCED collision: deterministic salt increment makes the orders distinct and reproducible")
        check(s1["a"] == R.arm_order(H1, "a", tasks), "R2-9 first arm keeps its unsalted order")
        R._HASH = lambda b: real(b"always")                                      # even salted seeds collide: must raise, not duplicate
        m = raises(R.ReplayError, R.schedule, H1, ["a", "b"], tasks)
        check(m is not None, "R2-9 FORCED: a collision salting cannot resolve raises instead of duplicating an order")
    finally:
        R._HASH = real
    # (10) lock naming
    root5 = tmp / "r5"
    check(raises(R.ReplayError, R._lock(" bad", "t", root5).__enter__) is not None and not (root5 / "locks").exists(),
          "R2-10 FORCED: bad name refused before any lock path/dir is built")
    with R._lock("a__b", "c", root5):
        try:
            with R._lock("a", "b__c", root5):
                ok = True
        except R.ReplayExists:
            ok = False
    check(ok, "R2-10 FORCED: a__b+c and a+b__c use different locks")
    with R._lock("a", "b", root5):
        check(raises(R.ReplayExists, R._lock("a", "b", root5).__enter__) is not None, "R2-10 same pair still excluded")


def main():
    tmp = Path(tempfile.mkdtemp(prefix="selftest_replay_"))
    os.environ["RM_ARENA_PRIVATE"] = str(tmp / "private")
    try:
        src, (A, B, C) = mk_source(tmp)
        for fn, a in ((t_no_future, (tmp, src, A, B, C)), (t_order, (tmp,)), (t_deleted, (tmp, src, A, B, C)), (t_reap, ()),
                      (t_round1, (tmp, src, A, B, C)), (t_reaper_marker, (tmp, src, A, B)), (t_rmtree, (tmp,)),
                      (t_round2, (tmp, src, A, B, C))):
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
