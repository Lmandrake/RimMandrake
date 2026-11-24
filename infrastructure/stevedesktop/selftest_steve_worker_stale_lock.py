#!/usr/bin/env python3
"""selftest_steve_worker_stale_lock.py - a reboot's leftover .git/index.lock does not refuse the next job SYNC
(RIMMANDRAKE_FIX_STEVE_WORKER_STALE_INDEX_LOCK_BEFORE_PULL).

The incident: SteveDesktop rebooted mid-git (2026-11-20 ~21:30Z); the next job J20261120T213808Z-8aa00b was
REFUSED/SYNC ('runner pull failed: index.lock: File exists') and the lane paused for an hour.
On a scratch runner clone (TESTQ_CLONE) with a real origin, through the worker's own pre-pull step (ready_for_pull):
  a lock older than this boot (no process that held it survives a reboot) is removed and the pull succeeds;
  a lock newer than this boot (a live git may hold it) is left alone, and the pull still refuses.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


PROBE = r"""
import os, sys, json
sys.path.insert(0, %r)
import worker
d = sys.argv[1]
os.makedirs(d, exist_ok=True)
worker.ready_for_pull(d)
rc, msg = worker.git("pull", "-q", "--ff-only", "origin", "main")
print(json.dumps({"rc": rc, "msg": msg}))
""" % HERE


def main():
    import json
    with tempfile.TemporaryDirectory() as tmp:
        origin, clone, home = (os.path.join(tmp, n) for n in ("origin.git", "runner", "home"))
        os.makedirs(home)

        def g(repo, *a):
            return subprocess.run(["git", "-C", repo] + list(a), capture_output=True, text=True).stdout.strip()
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", origin], check=True)
        subprocess.run(["git", "clone", "-q", origin, clone], check=True, capture_output=True)
        ident = ["-c", "user.name=t", "-c", "user.email=t@t"]

        def advance(name):      # origin moves on, so the pull has work to do (an empty pull may skip the index)
            open(os.path.join(clone, name), "w").write(name)
            g(clone, "add", name)
            g(clone, *ident, "commit", "-q", "-m", name)
            g(clone, "push", "-q", "origin", "main")
            g(clone, "reset", "-q", "--hard", "HEAD~1") if g(clone, "rev-list", "--count", "HEAD") != "1" else None
        open(os.path.join(clone, "base"), "w").write("base")
        g(clone, "add", "base")
        g(clone, *ident, "commit", "-q", "-m", "base")
        g(clone, "push", "-q", "-u", "origin", "main")
        lock = os.path.join(clone, ".git", "index.lock")
        env = dict(os.environ, TESTQ_CLONE=clone, TESTQ_HOME=home)

        def start(tag):
            r = subprocess.run([sys.executable, "-I", "-c", PROBE, os.path.join(home, "attempts", tag)], env=env,
                               capture_output=True, text=True, timeout=120)
            try:
                return json.loads(r.stdout.strip().splitlines()[-1])
            except (ValueError, IndexError):
                return {"rc": None, "msg": "probe failed: %s %s" % (r.stdout[-300:], r.stderr[-600:])}

        # 1. a lock left from before this boot: removed, the pull succeeds
        advance("one")
        open(lock, "w").close()
        os.utime(lock, (1000, 1000))        # 1970: older than any boot
        r = start("a1")
        check(r["rc"] == 0, "a pre-boot index.lock does not refuse the pull: %s" % r)
        check(not os.path.exists(lock), "the pre-boot index.lock is gone")
        note = os.path.join(home, "attempts", "a1", "index_lock_cleared.txt")
        check(os.path.exists(note), "the attempt dir records the removed lock")

        # 2. a lock from this boot (a live git may hold it): left alone, the pull still refuses
        advance("two")
        open(lock, "w").close()
        r = start("a2")
        check(r["rc"] != 0 and "index.lock" in (r["msg"] or ""), "a lock from this boot still refuses: %s" % r)
        check(os.path.exists(lock), "a lock from this boot is never deleted")
        os.remove(lock)

        # 3. the reboot hit an ATTEMPT: the clone is still on its detached pin, with the old lock (the usual case)
        advance("three")
        g(clone, "checkout", "-q", "--detach", "HEAD")
        open(lock, "w").close()
        os.utime(lock, (1000, 1000))
        r = start("a3")
        check(r["rc"] == 0 and g(clone, "symbolic-ref", "-q", "--short", "HEAD") == "main" and not os.path.exists(lock),
              "a pre-boot lock on a clone left on its pin: unpinned and pulled (%s)" % r)

        # 4. and with a dirty tracked file beside it
        advance("four")
        open(os.path.join(clone, "base"), "w").write("dirt")
        open(lock, "w").close()
        os.utime(lock, (1000, 1000))
        r = start("a4")
        check(r["rc"] == 0 and open(os.path.join(clone, "base")).read() == "base", "a pre-boot lock and dirt: healed and pulled (%s)" % r)
        # 5. the runner clone refuses a commit (STEVE_RUNNER_CLONE_ENFORCE_NO_LLM_WRITES): a commit there makes the next
        #    pull refuse SYNC; the runner's own update still lands
        open(os.path.join(clone, "llm"), "w").write("x")
        g(clone, "add", "llm")
        c = subprocess.run(["git", "-C", clone] + ident + ["commit", "-m", "an AI session"], capture_output=True, text=True)
        check(c.returncode != 0 and "own clone" in c.stderr, "a commit in the runner clone is refused, naming the cure: %s" % c.stderr[-200:])
        g(clone, "rm", "-q", "-f", "--cached", "llm")
        os.remove(os.path.join(clone, "llm"))
        other = os.path.join(tmp, "other")
        subprocess.run(["git", "clone", "-q", origin, other], check=True, capture_output=True)
        open(os.path.join(other, "five"), "w").write("5")
        g(other, "add", "five")
        g(other, *ident, "commit", "-q", "-m", "five")
        g(other, "push", "-q", "origin", "main")
        r = start("a5")
        check(r["rc"] == 0 and os.path.exists(os.path.join(clone, "five")), "the runner's own pull still lands: %s" % r)
        code = ("import sys; sys.path.insert(0, %r); import worker as w\n"
                "print([(w.setattr_clone(n), w.runner_clone_only())[1] for n in ('/x/runner', '/x/runner_b', '/x/bench')])" % HERE)
        code = code.replace("w.setattr_clone(n)", "setattr(w, 'CLONE', n)")
        out = subprocess.run([sys.executable, "-I", "-c", code], env={k: v for k, v in env.items() if k != "TESTQ_CLONE"},
                             capture_output=True, text=True, timeout=60).stdout.strip()
        check(out == "[True, True, False]", "both runner clones heal and refuse commits, a seat clone does neither: %s" % out)
    print("FAIL %d" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
