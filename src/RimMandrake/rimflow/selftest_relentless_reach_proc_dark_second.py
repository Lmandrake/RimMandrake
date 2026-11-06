#!/usr/bin/env python3
"""CHECKER_REACH_FIX_PROC_DARK_SECOND: the proc reach repair for OPS_TMP_DRAIN_RESTORE_DEVU (one waiter,
OPS_TMP_DRAIN_RESTORE_JVCO) failed its probe at 13:21Z on 2026-11-06 with "git_history: the grant could not be made at
91f784b5e2: ... books/.git/objects holds 2152159325 bytes of its own objects (cap 2147483648)". Its blind text says /proc
AND git history, so the probe makes the git_history grant before it runs proc_cwds; the grant then copied every own
object and refused past GIT_COPY_MAX. CHECKER_REACH_FIX_GH_DARK_SECOND (c549cc8ab6, 14:03Z) hardlinks them instead; a
dry re-probe at that code with DEVU's seeded proposal read GOOD. This test pins the instance: its exact text is
classed proc, carries the git_history grant and every adapter it needs, leaves nothing uncovered, and a borrower whose
OWN (not alternate-held) objects are over the cap still makes a grant, while the cap still binds bytes that must copy.
Rows: (1) class proc; (2) git_history grant; (3) proc_cwds plus the three git adapters, no gap; (4) books borrows; (4a) own objects over the
cap link in, grant made; (4b) the history reads in the box; (5) a link that fails copies and the cap refuses."""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless_wall as W             # noqa: E402
import relentless_reachfix as RF        # noqa: E402

FAILS = []
DEVU_BLIND = ("process visibility the reaper's hold check needs: 'ls -l /proc/1/cwd' -> Permission denied; the in-box "
              "proof is red only for that reason; git history/origin/main for the committed-saves guard: the tree is a "
              "git-less export, so 'git show <rev>:...' cannot run")


def ok(cond, name):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def git(cwd, *a, text=True):
    env = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="t",
               GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    return subprocess.run(["git", "-C", cwd] + list(a), env=env, capture_output=True, text=text, timeout=120)


def t_proposal():
    r = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "relentless_rules.json")))
    ok(RF.classify(r, [DEVU_BLIND]).get("class") == "proc", "(1) DEVU's blind text is classed proc")
    st = {"reach": {"class": "proc", "proposal": {"adapters": ["proc_cwds"], "by": "seed", "paths": [], "refused": {}},
                    "still_blind": DEVU_BLIND}, "blind": {"what": DEVU_BLIND}}
    prop = RF.fill(r, "proc", RF.reseed(r, "proc", RF.refreshed(r, st)), [DEVU_BLIND, DEVU_BLIND])
    ok(W.GIT_GRANT in (prop.get("grants") or []), "(2) the proc repair carries the git_history grant: %s" % prop)
    need = {"proc_cwds", "git_log_candidate", "git_stat_candidate", "git_origin_main"}
    gaps = RF.uncovered(r, prop, [DEVU_BLIND])
    ok(need <= set(prop.get("adapters") or []) and not gaps,
       "(3) proc_cwds and the git adapters, nothing uncovered: %s gaps %s" % (prop.get("adapters"), gaps))


def t_grant():
    with tempfile.TemporaryDirectory() as root:
        seed = os.path.join(root, "seed")     # the instance: books borrows store.git, its own objects loose on top
        git(root, "init", "-q", "-b", "main", seed)
        with open(os.path.join(seed, "base.txt"), "w") as f:
            f.write("base\n")
        git(seed, "add", "base.txt")
        git(seed, "commit", "-q", "-m", "base")
        store = os.path.join(root, "store.git")
        git(root, "clone", "-q", "--bare", seed, store)
        bor = os.path.join(root, "books")
        git(root, "clone", "-q", "--shared", store, bor)
        git(bor, "config", "gc.auto", "0")
        for i in range(6):
            with open(os.path.join(bor, "f%d.bin" % i), "wb") as f:
                f.write(os.urandom(60000))
        git(bor, "add", *["f%d.bin" % i for i in range(6)])
        git(bor, "commit", "-q", "-m", "a")
        sha = git(bor, "rev-parse", "HEAD").stdout.strip()
        objs = os.path.join(bor, ".git", "objects")
        ok(os.path.exists(os.path.join(objs, "info", "alternates")), "(4) precondition: books borrows store.git")
        own = sum(os.path.getsize(os.path.join(d, n)) for d, _, ns in os.walk(objs) if "/info" not in d for n in ns)
        cap, link = W.GIT_COPY_MAX, getattr(W, "_link", os.link)
        W.GIT_COPY_MAX = 20000          # the instance: own objects many times over the cap
        try:
            box = os.path.join(root, "box")
            for sub in ("projects", "tmp", "tree"):
                os.makedirs(os.path.join(box, sub))
            try:
                W.grant_git(box, bor, sha)
                err = None
            except (OSError, RuntimeError, subprocess.SubprocessError) as e:
                err = str(e)[-200:]
            ok(own > 300000 and err is None, "(4a) %d bytes of own objects over the cap still make a grant: %s"
               % (own, err))
            gd = os.path.join(box, "tree", ".git")     # books' own objects are linked in: they read with no bind
            ok(err is None and git(gd, "rev-parse", "HEAD").stdout.strip() == sha
               and git(gd, "cat-file", "-e", sha + "^{commit}").returncode == 0
               and git(gd, "cat-file", "-e", "%s:f0.bin" % sha).returncode == 0,
               "(4b) the candidate commit and its own blobs read in the granted tree")

            def nolink(s, d):
                raise OSError("cross-device")
            W._link = nolink
            try:
                W._copy_objects(objs, os.path.join(root, "copy"))
                err = None
            except RuntimeError as e:
                err = str(e)
            ok(err is not None and "would be copied" in err, "(5) a copy past the cap still refuses: %s" % err)
        finally:
            W.GIT_COPY_MAX, W._link = cap, link


if __name__ == "__main__":
    t_proposal()
    t_grant()
    print("FAILS: %d" % len(FAILS))
    sys.exit(1 if FAILS else 0)
