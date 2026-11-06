#!/usr/bin/env python3
"""CHECKER_REACH_FIX_GIT_DARK_SECOND: the git reach probe failed two ways, and nine items stayed blocked behind it.
  (1) The git_history grant could not be made: the supervisor's books clone held 22,844 LOOSE objects, 2.1 GB, over
      relentless_wall.GIT_COPY_MAX, though `pack-objects --local` of them measured 2.7 MB (nearly all already in its
      alternate store.git). CHECKER_REACH_FIX_GH_DARK_SECOND (c549cc8ab6) fixed it by hardlinking a borrower's own
      objects into the box; row 1 keeps this item's instance shape as a regression.
  (2) The git class's owner NIGHTLY_COP_FIX_RED_AQJSGV_CFVH also named /home/mandrake/rm/arena and the D: mirror's
      bundle_textures, which no git repair covers, so every probe failed on its own gaps while eight items blind on git
      history alone waited. The sweep now probes the rest of the repair without the owner's gaps; a pass releases the
      waiters and moves the owner alone to the class its gaps name, which it is never split back out of.
Rows: (1a) the instance shape (loose objects that the alternate already holds, over the cap) makes a grant; (1b) the
history still reads at the sha; (2a) waiters released
with the rest of the repair, the uncovered path not in it; (2b) the owner moves to `other`, not released; (2c) the git
book is ok; (2d) in `other` it is not split again: it files that class's ticket. Each red on the code before."""
import json
import os
import subprocess
import sys
import tempfile
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless_wall as W             # noqa: E402
import relentless_reachfix as RF        # noqa: E402
import selftest_relentless_blind as B   # noqa: E402
import selftest_relentless_reachfix as RT   # noqa: E402

FAILS = []
ARENA = "/home/mandrake/rm/arena"
OWNER_BLIND = ("a git checkout with HEAD needed by selftest_testq_steward.py (git rev-parse HEAD: not a git repository); "
               "%s needed by selftest_arm_sandbox.py (ls: Permission denied)" % ARENA)


def ok(cond, name):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def git(cwd, *a, text=True):
    env = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="t",
               GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    return subprocess.run(["git", "-C", cwd] + list(a), env=env, capture_output=True, text=text, timeout=120)


def t_grant_over_cap():
    with tempfile.TemporaryDirectory() as root:
        bor = os.path.join(root, "books")
        git(root, "init", "-q", "-b", "main", bor)
        git(bor, "config", "gc.auto", "0")
        for i in range(6):
            with open(os.path.join(bor, "f%d.bin" % i), "wb") as f:
                f.write(os.urandom(60000))
        git(bor, "add", *["f%d.bin" % i for i in range(6)])
        git(bor, "commit", "-q", "-m", "a")
        sha = git(bor, "rev-parse", "HEAD").stdout.strip()
        base = os.path.join(root, "store.git")       # the alternate takes every object the borrower wrote loose
        git(root, "clone", "-q", "--bare", bor, base)
        git(base, "repack", "-a", "-d", "-q")
        objs = os.path.join(bor, ".git", "objects")
        with open(os.path.join(objs, "info", "alternates"), "w") as f:
            f.write(os.path.join(base, "objects") + "\n")
        before = sum(os.path.getsize(os.path.join(d, n)) for d, _, ns in os.walk(objs) if "/info" not in d for n in ns)
        cap = W.GIT_COPY_MAX
        W.GIT_COPY_MAX = 20000
        try:
            dst = os.path.join(root, "copy")
            try:
                W._copy_objects(objs, dst)
                err = None
            except RuntimeError as e:
                err = str(e)
            ok(before > 300000 and err is None,
               "(1a) a borrower whose loose objects its alternate holds, over the cap, still makes a grant: %d bytes, %s"
               % (before, err))
            ok(git(bor, "cat-file", "-t", sha).stdout.strip() == "commit"
               and git(bor, "show", "%s:f0.bin" % sha, text=False).returncode == 0,
               "(1b) the history still reads after the repack")
        finally:
            W.GIT_COPY_MAX = cap


def t_split():
    r = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "relentless_rules.json")))
    prof = W.profile(r)
    shim = types.SimpleNamespace(**{k: getattr(W, k) for k in dir(W) if not k.startswith("__")})
    shim.profile = lambda _r: prof          # the rig runs wall-less; only the reach book sees the shipped masks
    real = RF.relentless_wall
    RF.relentless_wall = shim
    try:
        x = RT.rig(n=3)
        said = {"probe": []}

        def reach_probe(rr, paths, adapters, values, store_root, grants=()):
            said["probe"].append((list(paths), list(adapters), list(grants), values.get("item")))
            if any(p.startswith(ARENA) for p in paths):
                return False, "paths exit 3: UNREADABLE %s" % ARENA
            return x.w.probe_says
        x.w.reach_probe = reach_probe
        B.to_check(x, "I0")
        RT.blind(x, "I0", what=OWNER_BLIND)
        for i in ("I1", "I2"):
            B.to_check(x, i)
            RT.blind(x, i)
        x.tick()
        book = RF.load(x.s)
        ok(book.get("git", {}).get("owner") == "I0" and book["git"].get("waiters") == ["I1", "I2"],
           "(2) precondition: I0 owns the git repair, I1 and I2 wait: %s" % book.get("git"))
        gaps = RF.uncovered(r, RF.refreshed(r, x.st("I0")), [OWNER_BLIND])
        ok(gaps == [ARENA], "(2) precondition: the owner's text leaves the arena uncovered: %s" % gaps)
        tk = book["git"].get("ticket")
        x.w.items[tk or "CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS"] = "done"
        x.w.probe_says = (True, "git_history exit 0: HEAD reads")
        for _ in range(3):
            x.tick()
        sts = {i: x.st(i) for i in ("I0", "I1", "I2")}
        rel = {i: (s["status"], (s.get("reach") or {}).get("status")) for i, s in sts.items()}
        ok(all((sts[i].get("reach") or {}).get("status") == "applied" for i in ("I1", "I2"))
           and not any(ARENA in str(((sts[i].get("reach") or {}).get("proposal") or {}).get("paths")) for i in ("I1", "I2")),
           "(2a) both waiters are released with the rest of the repair, no arena path: %s" % rel)
        rp0 = sts["I0"].get("reach") or {}
        ok(sts["I0"]["status"] == "blocked" and rp0.get("class") == "other" and rp0.get("split_from") == ["git"],
           "(2b) the owner alone moves to `other`, still blocked: %s %s" % (rel["I0"], rp0.get("class")))
        book = RF.load(x.s)
        ok(book["git"].get("status") == "ok" and ARENA not in json.dumps(book["git"].get("ok_prop")),
           "(2c) the git book is ok, its passed repair without the arena: %s" % book["git"])
        for _ in range(3):
            x.tick()
        book = RF.load(x.s)
        rp0 = x.st("I0").get("reach") or {}
        ok(book.get("other", {}).get("owner") == "I0" and book["other"].get("status") == "ticket"
           and rp0.get("class") == "other" and x.st("I0")["status"] == "blocked",
           "(2d) in `other` it is not split again: it files that class's ticket: %s %s" % (book.get("other"), rp0.get("status")))
        x.done()
    finally:
        RF.relentless_wall = real


def main():
    t_grant_over_cap()
    t_split()
    print("RESULT: %s" % ("GREEN" if not FAILS else "RED %d: %s" % (len(FAILS), ", ".join(FAILS))))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
