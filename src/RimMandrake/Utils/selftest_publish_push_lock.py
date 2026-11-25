#!/usr/bin/env python3
"""Selftest for publish.py's machine-wide push lock and its race limit (RM_ROOT/.publish-push.lock).

2026-11-24: ./publish lost the push race 8 times in a row and refused ("origin kept moving") twice for the Conductor
and once for a helper, with ~13 runs landing at once on this machine. The fix: the publishers of one machine take one
exclusive flock across one attempt's fetch, replay and push only (never the ~5 min of checks), and the race limit is
10x the measured need. Each check prints what it read; the lock lives under a temp PUBLISH_RM_ROOT, never the real one.

    python3 src/RimMandrake/Utils/selftest_publish_push_lock.py
"""
import contextlib
import fcntl
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.expanduser("~/.cache/publish-selftest")
ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null"}
os.environ.update(ENV)
import publish as P  # noqa: E402

LOCK_NAME = ".publish-push.lock"      # the spec: one lock file directly under RM_ROOT
MEASURED_NEED = 8                     # lost races in a row, 2026-11-24 (the Conductor twice, a helper once)
BARRIER_S = 5.0                       # how long a publisher at the push waits for its twin (parallel start, ~1 s apart)
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def sh(cwd, *a):
    r = subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr))
    return r.stdout.strip()


def write(repo, path, text):
    full = os.path.join(repo, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(text)


def world(n=2):
    """-> (dir, lock root, [clones]) over one bare origin."""
    os.makedirs(ROOT, exist_ok=True)
    d = tempfile.mkdtemp(dir=ROOT)
    bare = os.path.join(d, "bare.git")
    root = os.path.join(d, "rm")
    os.makedirs(root)
    sh(d, "init", "-q", "--bare", "-b", "main", bare)
    clones = [os.path.join(d, "c%d" % i) for i in range(n)]
    sh(d, "clone", "-q", bare, clones[0])
    write(clones[0], "seed.txt", "seed\n")
    sh(clones[0], "add", "seed.txt")
    sh(clones[0], "commit", "-q", "-m", "seed")
    sh(clones[0], "push", "-q", "origin", "HEAD:main")
    for c in clones[1:]:
        sh(d, "clone", "-q", bare, c)
    return d, root, clones


def on_origin(repo):
    sh(repo, "fetch", "-q")
    return set(sh(repo, "ls-tree", "-r", "--name-only", "origin/main").splitlines())


def peer_push(b, path, text):
    sh(b, "pull", "-q", "--rebase")
    write(b, path, text)
    sh(b, "add", path)
    sh(b, "commit", "-q", "-m", "peer", "--", path)
    sh(b, "push", "-q", "origin", "HEAD:main")


# a real ./publish in its own process; before_push marks its arrival and waits (up to BARRIER_S) for its twin's mark,
# so two publishers started together push in the same instant unless something serializes them
DRIVER = r"""
import os, sys, time
sys.path.insert(0, %r)
import publish as P
bar, me, twin = sys.argv[1:4]
def hook(attempt):
    open(os.path.join(bar, me), "w").close()
    end = time.time() + %r
    while time.time() < end and not os.path.exists(os.path.join(bar, twin)):
        time.sleep(0.02)
P.before_push = hook if twin != "-" else None
sys.exit(P.main(sys.argv[4:]))
""" % (HERE, BARRIER_S)


def publisher(clone, root, path, bar="-", me="-", twin="-"):
    write(clone, path, path + "\n")
    env = dict(os.environ, PUBLISH_RM_ROOT=root)
    return subprocess.Popen([sys.executable, "-c", DRIVER, bar, me, twin, "-m", "add " + path, path], cwd=clone,
                            env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def finish(p, timeout=120):
    try:
        so, se = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        so, se = p.communicate()
        return -9, so, se + "\n[selftest: killed after %d s]" % timeout
    return p.returncode, so, se


def guarded(fn, timeout):
    """fn() in a daemon thread -> (finished, result or exception). A publisher that waits on itself never returns."""
    box = {}

    def go():
        try:
            box["r"] = fn()
        except BaseException as e:  # noqa: BLE001
            box["r"] = e
    t = threading.Thread(target=go, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        sys.stdout = sys.__stdout__        # the stuck thread's redirect_stdout never exits
    return (not t.is_alive()), box.get("r")


def held_by_other(path):
    """True when another open file description holds the flock on path (probed from a fresh descriptor)."""
    try:
        fd = os.open(path, os.O_RDWR)
    except OSError:
        return False
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        return False
    except BlockingIOError:
        return True
    finally:
        os.close(fd)


def t_two_publishers_started_together_both_land_without_a_lost_race():
    d, root, (a, b) = world()
    try:
        bar = os.path.join(d, "bar")
        os.makedirs(bar)
        pa = publisher(a, root, "from_a.txt", bar, "a", "b")
        pb = publisher(b, root, "from_b.txt", bar, "b", "a")
        ra, rb = finish(pa), finish(pb)
        files = on_origin(a)
        # a lost race prints "origin moved ... retrying", or (two pushes in one instant: "[remote rejected] ... cannot
        # lock ref", measured on the parent 2026-11-24) "push failed (...); retrying": any retry is a lost race here
        lost = sum(("retrying" in so) for _, so, _ in (ra, rb))
        check(ra[0] == 0 and rb[0] == 0 and {"from_a.txt", "from_b.txt"} <= files,
              "two publishers started together both land (rc %s, %s; on origin: %s)"
              % (ra[0], rb[0], sorted(files & {"from_a.txt", "from_b.txt"})))
        check(lost == 0, "neither publisher lost a race: %d of 2 retried (limit 0)%s"
              % (lost, "" if not lost else "\n  a: %s\n  b: %s" % (ra[1].strip()[-300:], rb[1].strip()[-300:])))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_killed_lock_holder_does_not_stop_the_publisher():
    d, root, (a, _b) = world()
    try:
        lock = os.path.join(root, LOCK_NAME)
        code = ("import fcntl,os,time;fd=os.open(%r,os.O_CREAT|os.O_RDWR,0o644);fcntl.flock(fd,fcntl.LOCK_EX);"
                "print('held',flush=True);time.sleep(120)") % lock
        h = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, text=True)
        check(h.stdout.readline().strip() == "held", "the planted holder took %s" % lock)
        p = publisher(a, root, "after_kill.txt")
        time.sleep(4.0)                    # a lock-free publisher lands in ~1 s in this world
        waited = p.poll() is None and "after_kill.txt" not in on_origin(a)
        check(waited, "while the holder lives the publisher waits before its push (still running: %s; landed: %s)"
              % (p.poll() is None, "after_kill.txt" in on_origin(a)))
        h.kill()
        h.wait()
        t0 = time.time()
        rc, so, se = finish(p, 60)
        check(rc == 0 and "after_kill.txt" in on_origin(a),
              "after the holder is killed the publisher lands (rc %s, %.1f s after the kill)%s"
              % (rc, time.time() - t0, "" if rc == 0 else "\n  %s %s" % (so[-300:], se[-300:])))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_lock_file_that_cannot_be_opened_is_said_and_the_publish_lands():
    for kind in ("missing root", "read-only root"):
        d, root, (a, _b) = world()
        try:
            if kind == "missing root":
                root = os.path.join(d, "no-such-root")
            else:
                os.chmod(root, 0o555)
            name = "ro_%s.txt" % kind.split()[0]
            rc, so, se = finish(publisher(a, root, name), 60)
            said = [ln for ln in se.splitlines() if LOCK_NAME in ln]
            check(rc == 0 and name in on_origin(a), "%s: the publish still lands (rc %s)%s"
                  % (kind, rc, "" if rc == 0 else "\n  " + se[-300:]))
            check(len(said) == 1 and "without" in said[0],
                  "%s: stderr says so in one line (%d line(s) name the lock: %r)" % (kind, len(said), said[:2]))
        finally:
            os.chmod(os.path.join(d, "rm"), 0o755)
            shutil.rmtree(d, ignore_errors=True)


def t_the_lock_is_held_across_the_push_and_free_after():
    d, root, (a, b) = world()
    old = P.RM_ROOT
    P.RM_ROOT = root
    try:
        lock = os.path.join(root, LOCK_NAME)
        seen = []

        def race(attempt):
            seen.append(held_by_other(lock))
            if attempt == 0:
                peer_push(b, "raced.txt", "raced\n")      # one lost race, so a second attempt must take it again
        P.before_push = race
        write(a, "held.txt", "held\n")
        buf = io.StringIO()

        def go():
            with contextlib.redirect_stdout(buf):
                return P.publish(a, ["held.txt"], "held")
        done, r = guarded(go, 60)
        check(done, "a publisher that lost one race finishes its second attempt (did not wait on its own lock)")
        check(done and isinstance(r, str) and "held.txt" in on_origin(a), "it landed (result %r)" % (r,))
        check(seen == [True, True], "the lock was held at each push: %s (want [True, True])" % seen)
        check(not held_by_other(lock), "the lock is free once the publish returns")
    finally:
        P.before_push, P.RM_ROOT = None, old
        shutil.rmtree(d, ignore_errors=True)


def t_the_race_limit_is_ten_times_the_need_and_its_refusal_says_could_not_land():
    d, root, (a, b) = world()
    old = P.RM_ROOT, getattr(P, "RACE_PAUSE_MAX_S", None)
    P.RM_ROOT = root
    if old[1] is not None:
        P.RACE_PAUSE_MAX_S = 0.0           # the pause between lost races is not what this reads
    calls = []
    try:
        def race(attempt):
            calls.append(attempt)
            peer_push(b, "mover.txt", "move %d\n" % attempt)     # origin moves before every push: every race is lost
        P.before_push = race
        write(a, "never.txt", "never\n")
        buf = io.StringIO()

        def go():
            with contextlib.redirect_stdout(buf):
                return P.publish(a, ["never.txt"], "never")
        done, r = guarded(go, 400)
        msg = str(r) if isinstance(r, P.Refuse) else ""
        print("  read: %d attempts, MAX_TRIES %s, refusal %r" % (len(calls), P.MAX_TRIES, msg[:240]))
        check(done and isinstance(r, P.Refuse), "a push that can never land is refused, not looped (%s)" % type(r).__name__)
        check(P.MAX_TRIES >= 10 * MEASURED_NEED, "MAX_TRIES %s >= 10 x the measured need %d"
              % (P.MAX_TRIES, MEASURED_NEED))
        check(len(calls) == P.MAX_TRIES, "the refusal comes only after the limit: %d attempts (limit %s)"
              % (len(calls), P.MAX_TRIES))
        check("could not land" in msg and str(P.MAX_TRIES) in msg, "the refusal says 'could not land' and names the limit")
        check(msg.startswith("origin kept moving"),
              "the refusal keeps the prefix push_refusal_census.py reads ('^REFUSED: origin kept moving')")
        check("never.txt" in sh(a, "show", "--name-only", "--format=", "HEAD").splitlines(),
              "the commit stays on HEAD")
    finally:
        P.before_push, P.RM_ROOT = None, old[0]
        if old[1] is not None:
            P.RACE_PAUSE_MAX_S = old[1]
        shutil.rmtree(d, ignore_errors=True)


# origin's own hook moves main and declines the push, the way a peer's push that wins the ref lock in the same instant
# reads to the loser ("[remote rejected] main -> main (...)", "failed to push some refs"); it does so MOVES times
MOVER = r"""#!/bin/sh
n=$(cat "$GIT_DIR/moves" 2>/dev/null || echo 0)
[ "$n" -ge %d ] && exit 0
echo $((n + 1)) > "$GIT_DIR/moves"
while read old new ref; do
  t=$(env -u GIT_QUARANTINE_PATH -u GIT_OBJECT_DIRECTORY -u GIT_ALTERNATE_OBJECT_DIRECTORIES \
      git commit-tree "$old^{tree}" -p "$old" -m "peer $n")
  env -u GIT_QUARANTINE_PATH -u GIT_OBJECT_DIRECTORY -u GIT_ALTERNATE_OBJECT_DIRECTORIES git update-ref "$ref" "$t" "$old"
done
echo "peer won the ref lock" >&2
exit 1
"""
MOVES = 2


def t_a_race_lost_in_other_words_is_read_as_a_race():
    d, root, (a,) = world(1)
    try:
        hook = os.path.join(d, "bare.git", "hooks", "pre-receive")
        with open(hook, "w") as f:
            f.write(MOVER % MOVES)
        os.chmod(hook, 0o755)
        rc, so, se = finish(publisher(a, root, "worded.txt"), timeout=200)
        moved, failed = so.count("origin moved"), so.count("push failed")
        print("  read: rc %s, %d 'origin moved', %d 'push failed' (want %d, 0)" % (rc, moved, failed, MOVES))
        check(rc == 0 and "worded.txt" in on_origin(a), "it lands once origin stops moving (rc %s)" % rc)
        check(moved == MOVES and failed == 0,
              "a push declined while origin moved is a lost race: %d of %d read as races, %d as failed pushes (want 0)"
              % (moved, MOVES, failed))
    finally:
        shutil.rmtree(d, ignore_errors=True)


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("t_")]


def main():
    for t in TESTS:
        print("--", t.__name__)
        try:
            t()
        except Exception as e:  # noqa: BLE001
            check(False, "%s crashed: %s: %s" % (t.__name__, type(e).__name__, e))
    print(json.dumps({"failed": len(FAILS), "tests": len(TESTS)}))
    print("%s: %d check(s) failed" % ("FAIL" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
