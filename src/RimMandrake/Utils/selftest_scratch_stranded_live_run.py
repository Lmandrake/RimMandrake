#!/usr/bin/env python3
"""Class guard of OPS_WORKER_CLONE_POOL_RESTORE_HMOQ_PBAL: scratch_clone.scratch_stranded() never calls a live run's clone
stranded, and still calls one stranded when its run has ended or it sits under a bare seat dir.

The instance (Archmagi, 2026-11-25T01:13Z): a live detached run, claude-seat-BENCH-rm-detached-bench-rimmandrake-feed-codex-
grouped-tickets-h-<n>, kept 9 Codex clones under rm/scratch/BENCH-rm-detached-bench-rimmandrake-feed-codex-grouped-tickets-h/
and landed them in turn; 6 idle over an hour read stranded, so disk.pool_breach read 6 and reopened this item. A second
instance (2026-11-25T09:42Z): a run's clone read stranded the pass after the run exited, before its last landing.

`--at <rev>` replays the instance on scratch_clone.py as it was at that commit (the guard's red, shown on the parent of the
fix). The fixture lives under rm/scratch/<seat>/ on ext4, every path env-overridden: the real store and state are untouched."""
from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
BASE = Path("/home/mandrake/rm/scratch") / os.environ.get("RM_SEAT", "BENCH") / f"_selftest_stranded_live_{os.getpid()}"
SCR = BASE / "scratch"
os.environ.update({
    "RM_SEAT": "SELFTEST", "RM_OBJSTORE": str(BASE / "store.git"), "RM_OBJSTORE_SEED": str(BASE / "mirror.git"),
    "RM_SCRATCH_ROOT": str(SCR), "RM_OBJSTORE_STATE": str(BASE / "state"), "RM_OBJSTORE_SCAN": str(SCR / "*" / "*"),
    "SCRATCH_REAP_MIRRORS": str(BASE / "mirror.git"), "RM_SESSION_GLOB": str(BASE / "nosession*"),
    "SCRATCH_REAP_PROTECTED": str(BASE / "noprotected"),
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
})
OLD = {**os.environ, "GIT_AUTHOR_DATE": "1700003000 +0000", "GIT_COMMITTER_DATE": "1700003000 +0000"}
WORK = {**os.environ, "GIT_AUTHOR_DATE": "1700009000 +0000", "GIT_COMMITTER_DATE": "1700009000 +0000"}   # its own second: a print main shares reads landed
LIVE, DEAD, BARE = "BENCH-rm-detached-live-run", "BENCH-rm-detached-dead-run", "BENCH"
FAILS: list[str] = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def sh(*a, env=None):
    return subprocess.run(a, check=True, capture_output=True, text=True, env=env).stdout.strip()


def load(at: str | None):
    if not at:
        import scratch_clone
        return scratch_clone
    src = sh("git", "-C", str(HERE), "show", "%s:./scratch_clone.py" % at)
    d = tempfile.mkdtemp(prefix="stranded_at_", dir=str(BASE))
    p = Path(d) / "scratch_clone.py"
    p.write_text(src)
    spec = importlib.util.spec_from_file_location("scratch_clone", p)
    m = importlib.util.module_from_spec(spec)
    sys.modules["scratch_clone"] = m
    spec.loader.exec_module(m)
    return m


def plant(rel: str) -> Path:
    c = SCR / rel
    sh("git", "clone", "-q", "--shared", str(BASE / "work"), str(c))
    sh("git", "-C", str(c), "update-ref", "refs/remotes/origin/main", "HEAD")
    sh("git", "-C", str(c), "commit", "-q", "--allow-empty", "-m", "codex work " + rel, env=WORK)
    for n in (".git/HEAD", ".git/logs/HEAD", ".git/index", ".git/FETCH_HEAD"):
        if (c / n).exists():
            t0 = (c / n).stat().st_mtime - 7200
            os.utime(c / n, (t0, t0))
    return c


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--at", help="replay on scratch_clone.py at this commit")
    a = ap.parse_args()
    BASE.mkdir(parents=True)
    try:
        work = BASE / "work"
        sh("git", "init", "-q", "-b", "main", str(work))
        (work / "a.txt").write_text("one\n")
        sh("git", "-C", str(work), "add", "a.txt")
        sh("git", "-C", str(work), "commit", "-q", "-m", "a", env=OLD)
        sh("git", "init", "-q", "--bare", str(BASE / "mirror.git"))
        sh("git", "-C", str(work), "push", "-q", str(BASE / "mirror.git"), "HEAD:refs/remotes/origin/main")
        sc = load(a.at)
        for rel in (LIVE + "/cxs-a", DEAD + "/cxs-b", BARE + "/own"):
            plant(rel)
        sc.live_seats = lambda: {LIVE, BARE}     # the claude-seat scopes alive now: the live run's, and the Conductor's
        ss = sc.scratch_stranded()
        rows = {Path(r["path"]).name: r for r in ss["rows"]}
        names = {Path(p).name for p in ss["stranded"]}
        check("cxs-a" in rows and "cxs-a" not in names, "a live run's idle clone with unlanded work is held, not stranded: %s"
              % rows.get("cxs-a"))
        check("cxs-b" in names, "a clone whose run has ended is stranded: %s" % rows.get("cxs-b"))
        check("own" in names, "a bare seat's clone is stranded though that seat is live: %s" % rows.get("own"))
        # The run-end race (2026-11-25T09:42Z, cxs-deployshard-1795594915): the run exited, its excuse ended that pass, and
        # its last commit landed minutes later. A run seen live in the last idle hour still holds its clones.
        sc.live_seats = lambda: {BARE}          # the live run has just ended
        ss = sc.scratch_stranded()
        names = {Path(p).name for p in ss["stranded"]}
        check("cxs-a" not in names, "a run that ended inside the idle hour still holds its clones (the landing race)")
        sf = sc.state_dir() / "scratch_stranded.json"
        import json as _json
        d = _json.loads(sf.read_text())
        d["live_seen"] = {k: v - sc.POOL_IDLE_S - 60 for k, v in (d.get("live_seen") or {}).items()}
        sf.write_text(_json.dumps(d))
        ss = sc.scratch_stranded()
        names = {Path(p).name for p in ss["stranded"]}
        check("cxs-a" in names, "a run last seen live over an idle hour ago no longer holds its clones")
    finally:
        shutil.rmtree(BASE, ignore_errors=True)
    print("selftest_scratch_stranded_live_run: %s" % ("FAIL %d" % len(FAILS) if FAILS else "OK"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
