#!/usr/bin/env python3
"""CANDIDATE_SHA_REPAIR_LANDED_UNDER_NEW_HASH: a worker named its local sha, the landing rebased it onto origin/main
under another hash, the clone was reaped, and the supervisor asked `merge-base` about an object the books clone never
held: exit 128 -> None -> publish_unknown every tick for 10 hours (four built items, 2026-11-06).

Synthetic repos only (origin, books, worker, lander): no network, no real store."""
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless as R  # noqa: E402
import selftest_relentless as T  # noqa: E402

ITEM = "WIDGET_FIX_LANDED_ELSEWHERE"
FAILS = []


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def git(cwd, *args, env=None):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, **(env or {})))
    if r.returncode:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr))
    return r.stdout.strip()


def commit(cwd, msg, files, when):
    for p, text in files.items():
        os.makedirs(os.path.dirname(os.path.join(cwd, p)) or cwd, exist_ok=True)
        with open(os.path.join(cwd, p), "w") as f:
            f.write(text)
        git(cwd, "add", p)
    stamp = "@%d +0000" % when
    git(cwd, "commit", "-q", "-m", msg, env={"GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp})
    return git(cwd, "rev-parse", "HEAD")


def setup(d):
    origin, worker, lander = (os.path.join(d, x) for x in ("origin.git", "worker", "lander"))
    git(d, "init", "-q", "--bare", "-b", "main", origin)
    for c in (worker, lander):
        git(d, "clone", "-q", origin, c)
        git(c, "config", "user.name", "t")
        git(c, "config", "user.email", "t@x")
    base = commit(worker, "seed", {"a.txt": "a\n"}, 1000)
    git(worker, "push", "-q", "origin", "HEAD:main")
    git(lander, "pull", "-q", "origin", "main")
    a = commit(worker, "%s: the fix" % ITEM, {"src/fix.py": "x = 1\n"}, 2000)
    b = commit(worker, "%s: clean marks" % ITEM, {"code_review/fix.json": "{}\n"}, 2010)
    commit(lander, "OTHER_ITEM: moved on meanwhile", {"other.txt": "o\n"}, 2005)
    git(lander, "fetch", "-q", worker, "HEAD")
    git(lander, "cherry-pick", a, b)          # the landing: same work, new hashes
    git(lander, "push", "-q", "origin", "HEAD:main")
    return origin, worker, lander, base, a, b, git(lander, "rev-parse", "HEAD")


def main():
    d = tempfile.mkdtemp(prefix="rl-landed-")
    try:
        origin, worker, lander, base, a, b, landed = setup(d)
        ok(landed != b, "0. the landing rebased the worker's tip under a new hash")

        # 1. finish-time: the worker's clone still holds its sha; record what origin holds instead
        sha, note = R.landed_commit(b, cwd=worker)
        ok(sha == landed and note and "landed as" in note, "1. landed_commit maps the local sha to the landed one by patch-id")
        same, note2 = R.landed_commit(base, cwd=worker)
        ok(same == base and note2 is None, "1b. a sha origin/main already holds is recorded as is")
        key = R.landing_key(worker, b)
        ok(key and key["patch_id"] and key["subject"].startswith(ITEM), "1c. the landing key carries patch-id, subject, author")

        # 2. the supervisor: books never held the worker's object
        store = R.Store(os.path.join(d, "store"))
        git(d, "clone", "-q", origin, os.path.join(store.root, "books"))
        fx = R.Effects(dict(T.RULES), store)
        ok(fx.published(b) is False, "2. an object absent after a good fetch reads not-published, never unknown (None)")
        st = {"item": ITEM, "base": base, "clone": worker, "candidate": {"sha": b, "at": 2100.0, "gen": 1}}
        got = fx.relanded(st)
        ok(got and got[0] == landed and "patch-id" in got[1], "2b. relanded resolves through the live clone by patch-id: %s" % (got,))
        st = {"item": ITEM, "base": base, "clone": os.path.join(d, "reaped"),
              "candidate": {"sha": b, "at": 2100.0, "gen": 1, "key": key}}
        got = fx.relanded(st)
        ok(got and got[0] == landed, "2c. a reaped clone with the finish's recorded key still resolves: %s" % (got,))
        st["candidate"].pop("key")
        got = fx.relanded(st)
        ok(got and got[0] == landed and "naming" in got[1], "2d. the legacy case (no key, no clone): newest item-named commit: %s" % (got,))
        st["started_at"] = 2008.0           # a later run: the fix was an earlier run's landed half
        ok(fx.relanded(st)[0] == landed, "2d'. the finishing run's own window still holds the clean marks")
        st["started_at"] = 2012.0           # (one second of slack either side)
        ok(fx.relanded(st) is None, "2d''. nothing this run authored landed: no earlier run's commit is taken")
        st["started_at"] = 1500.0
        st["candidate"]["at"] = 2003.0      # finished after the fix but before the clean marks were authored
        got = fx.relanded(st)
        ok(got and got[0] != landed and git(lander, "log", "-1", "--format=%s", got[0]).endswith("the fix"),
           "2e. authored-by-the-finish bounds the legacy match: %s" % (got,))
        st = {"item": "NOBODY_NAMED_THIS_EVER", "base": base, "clone": None,
              "candidate": {"sha": "0123456789" * 4, "at": 9e9, "gen": 1}}
        ok(fx.relanded(st) is None, "2f. an absent sha that names nothing on origin resolves to nothing")
        ok(fx.relanded({"item": ITEM, "base": base, "candidate": {"sha": base, "at": 9e9}}) is None,
           "2g. a sha books holds is left to published()")

        # 3. the tick: a candidate the world relands moves to the landed sha and goes on to its check
        x = T.Rig(n=1, share=1.0)
        x.w.is_pub = None                   # as in the incident: the old sha cannot be asked about
        x.run_one("I0")
        s0 = x.st("I0")
        R.contract(x.s, "I0", s0["gen"], "p")
        R.finish(x.s, "I0", s0["gen"], "oldsha", "e")
        x.w.up[s0["run"]["unit"]] = False
        x.tick()
        x.tick()
        ok(x.st("I0")["status"] == "candidate", "3. before the repair it waits (publish_unknown)")

        def relanded(st):
            return ("newsha", "patch-id test") if st["candidate"]["sha"] == "oldsha" else None
        x.w.relanded = relanded
        x.w.is_pub = True
        for _ in range(3):
            x.tick()
        s1 = x.st("I0")
        ok(s1["candidate"]["sha"] == "newsha" and s1["candidate"].get("landed_from") == "oldsha" and s1["last_sha"] == "newsha",
           "3b. the candidate now records the landed sha and where it came from")
        ok(s1["status"] == "checking", "3c. and the check starts: %s" % s1["status"])
        ok(any(a.get("routed") == "relanded" for a in x.s.attempts("I0")), "3d. the repair is on the attempts record")
        x.done()
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
