#!/usr/bin/env python3
"""selftest_steve_worker_outer_copy.py - spawn's outer copy is the PULLED main's worker, even when the job pins the
very clone it runs from (STEVE_SPAWN_FIX_COPIES_THE_PAST).

On SteveDesktop CLONE == RUNNER: `start` pulls main, then `checkout --detach source_sha` rewrites worker.py, schema.py
and companion_identity.py on disk. spawn used to copy them AFTER that, so a job pinned to an older sha ran the OLD
outer worker. This builds a throwaway repo that is its own runner (an origin to pull from, no TESTQ_CLONE), commits an
"old" tree then the real one, starts a job pinned to the old sha with the launch stubbed out, and checks:

  O1  the pin really happened (the clone is detached at the old sha): the test reached the dangerous path
  O2  outer/worker.py, outer/schema.py, outer/companion_identity.py are the HEAD (main) bytes, not the pinned ones

Usage: selftest_steve_worker_outer_copy.py [WORKER]   (WORKER: a worker.py to test instead of this tree's)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
FILES = {   # repo path -> the worker's outer-copy name
    "infrastructure/stevedesktop/worker.py": "worker.py",
    "src/RimMandrake/Utils/testq/schema.py": "schema.py",
    "src/RimMandrake/bridgetools/companion_identity.py": "companion_identity.py",
    "src/RimMandrake/contracts/models.py": None,
}
OLD = b"\n# STALE_OUTER_MARKER: the pinned sha's copy\n"
FAILS = []

DRIVER = r'''
import io, json, os, sys
sys.path.insert(0, sys.argv[1])
import worker as W
W.shutil.which = lambda name: None              # no systemd-run: take the Popen route ...
_real = W.subprocess.Popen                       # ... and launch no attempt (git still runs)
W.subprocess.Popen = lambda argv, *a, **k: None if "_run" in argv else _real(argv, *a, **k)
sys.stdin = io.StringIO(sys.argv[2])
sys.exit(W.main(["start"]))
'''


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        FAILS.append(msg)


def main():
    worker_src = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(HERE, "worker.py")
    tmp = tempfile.mkdtemp(prefix="rf_steve_outer_")
    try:
        bare, clone, home = (os.path.join(tmp, d) for d in ("origin.git", "runner", "home"))
        env = {k: v for k, v in os.environ.items() if not k.startswith(("TESTQ_", "RM_HOST_GUARD"))}
        env.update(TESTQ_HOME=home, TESTQ_NO_SYSTEMD="1", GIT_CONFIG_NOSYSTEM="1",
                   GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")

        def g(*a, cwd=clone):
            r = subprocess.run(["git"] + list(a), cwd=cwd, env=env, capture_output=True, text=True, timeout=60)
            if r.returncode:
                raise RuntimeError("git %s: %s" % (" ".join(a), r.stderr))
            return r.stdout.strip()

        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True, capture_output=True)
        os.makedirs(clone)
        g("init", "-q", "-b", "main")
        want = {}
        for rel in FILES:
            src = worker_src if rel.endswith("stevedesktop/worker.py") else os.path.join(REPO, rel)
            data = open(src, "rb").read()
            want[rel] = data
            os.makedirs(os.path.dirname(os.path.join(clone, rel)), exist_ok=True)
            open(os.path.join(clone, rel), "wb").write(data + (OLD if FILES[rel] else b""))
        g("add", "-A")
        g("commit", "-q", "-m", "old")
        old = g("rev-parse", "HEAD")
        for rel, data in want.items():
            open(os.path.join(clone, rel), "wb").write(data)
        g("commit", "-q", "-am", "new")
        g("remote", "add", "origin", bare)
        g("push", "-q", "origin", "main")
        g("branch", "-q", "--set-upstream-to=origin/main", "main")

        sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "testq"))
        import schema as S
        job = S.make_job("Mock", {"rows": ["r1"]}, "commission", "BENCH", old)
        drv = os.path.join(tmp, "driver.py")
        open(drv, "w").write(DRIVER)
        r = subprocess.run([sys.executable, drv, os.path.join(clone, "infrastructure", "stevedesktop"), json.dumps(job)],
                           cwd=clone, env=env, capture_output=True, text=True, timeout=120)
        last = (r.stdout.strip().splitlines() or ["{}"])[-1]
        try:
            o = json.loads(last)
        except ValueError:
            o = {"raw": (r.stdout + r.stderr)[-600:]}
        check(r.returncode == 0 and o.get("state") == "started", "start reached spawn: rc=%s %s %s" % (r.returncode, o, r.stderr[-600:] if r.returncode else ""))
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=clone, env=env, capture_output=True, text=True).stdout
        check(head.strip() == old and o.get("runner_sha") == old, "O1 the clone that is its own runner was pinned to the old sha")
        for rel, name in FILES.items():
            if not name:
                continue
            path = os.path.join(home, "outer", name)
            got = open(path, "rb").read() if os.path.exists(path) else b""
            check(got == want[rel], "O2 outer/%s is main's bytes, not the pinned sha's (%s)"
                  % (name, "stale" if OLD in got else "missing" if not got else "ok" if got == want[rel] else "differs"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d failure(s)" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
