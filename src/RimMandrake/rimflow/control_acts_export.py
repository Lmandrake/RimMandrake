#!/usr/bin/env python3
"""control_acts_export.py — copy the control store's acts to git, so the record outlives this machine.

Item RIMMANDRAKE_EXPORT_CONTROL_ACTS_BELT_SPLIT_FROM_SLICE_FOUR; page design/specs/2026-11-19-control-acts-export/boundary.md
(every promise named there has a test of its name in selftest_control_acts_export.py). Run by
rm-control-acts-export.timer from the dispatch clone.

    control_acts_export.py              export every act and push it to origin/main as infrastructure/state/control/acts.jsonl
    control_acts_export.py --dry        say what a run would do; push nothing, write no reading

The commit is built by plumbing in a temporary index seeded from origin/main: this clone's working tree, index and
HEAD are never touched. A run that pushed or found nothing to push rewrites the reading; any other run leaves it to
age, which is how rm-deadman sees a dead belt.

Exit: 0 PUBLISHED <sha> or unchanged · 2 REFUSED (the export lacks a line the published file holds) · 3 COULD NOT
LOOK (the store is missing or corrupt) · 4 FAILED (git or the push; cause named).
"""
import argparse
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE) if HERE not in sys.path else None
import control as C  # noqa: E402

PATH = "infrastructure/state/control/acts.jsonl"
TRIES = 5
OK, REFUSED, BLIND, FAILED = 0, 2, 3, 4
REJECT_WORDS = ("rejected", "non-fast-forward", "fetch first")


class GitFailed(Exception):
    pass


def default_reading():
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
    import rmpaths
    return rmpaths.rm_str("control", "acts_export.json")


def _git(repo, *args, env=None, inp=None):
    r = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True, input=inp, timeout=120,
                       env=dict(os.environ, **(env or {})))
    if r.returncode:
        raise GitFailed("git %s exited %d: %s" % (args[0], r.returncode, (r.stderr or r.stdout).strip()[-300:]))
    return r.stdout


def _published(repo, up):
    """-> origin's file at `up` as text, or None where it has none."""
    r = subprocess.run(["git", "-C", repo, "cat-file", "-e", "%s:%s" % (up, PATH)], capture_output=True, timeout=60)
    return _git(repo, "show", "%s:%s" % (up, PATH)) if r.returncode == 0 else None


def _lost(old, new):
    """-> the first line of `old` that `new` does not hold, else None (never-loses-a-published-act)."""
    have = set(new.splitlines())
    return next((ln for ln in old.splitlines() if ln and ln not in have), None)


def _commit(repo, up, text, msg):
    """A commit on `up` with PATH set to `text`, built in a temporary index (touches-no-working-tree). -> sha."""
    blob = _git(repo, "hash-object", "-w", "--stdin", inp=text).strip()
    fd, idx = tempfile.mkstemp(prefix="acts-export-", suffix=".idx")
    os.close(fd)
    os.unlink(idx)
    try:
        env = {"GIT_INDEX_FILE": idx}
        _git(repo, "read-tree", up, env=env)
        _git(repo, "update-index", "--add", "--cacheinfo", "100644,%s,%s" % (blob, PATH), env=env)
        tree = _git(repo, "write-tree", env=env).strip()
    finally:
        if os.path.exists(idx):
            os.unlink(idx)
    return _git(repo, "commit-tree", tree, "-p", up, "-m", msg).strip()


def _write_reading(reading, verdict, n, top, sha, now):
    os.makedirs(os.path.dirname(os.path.abspath(reading)), exist_ok=True)
    tmp = "%s.tmp.%d" % (reading, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"at": C.utc(now), "at_pacific": C.pac(now), "verdict": verdict, "acts": n, "rev": top, "sha": sha,
                   "path": PATH}, f, sort_keys=True)
        f.write("\n")
    os.replace(tmp, reading)


def run(repo=REPO, store=None, reading=None, remote="origin", branch="main", dry=False, before_push=None, now=None):
    """One run. -> (exit code, lines). `before_push` (tests) is called before every push attempt."""
    now = time.time() if now is None else now
    d = tempfile.mkdtemp(prefix="acts-export-")
    try:
        out = os.path.join(d, "acts.jsonl")
        try:
            n = C.export_acts(out, p=store)
        except (C.Unreadable, sqlite3.Error) as e:
            return BLIND, ["COULD NOT LOOK: the control store %s: %s (nothing pushed)" % (store or C.db_path(), e)]
        with open(out, encoding="utf-8") as f:
            text = f.read()
    finally:
        for x in os.listdir(d):
            os.unlink(os.path.join(d, x))
        os.rmdir(d)
    top = json.loads(text.splitlines()[-1])["rev"] if text else 0
    if reading is None and not dry:
        try:
            reading = default_reading()
        except Exception as e:      # noqa: BLE001  rmpaths fails by name; a run with no reading is not a success
            return FAILED, ["FAILED: no reading path (%s: %s); pass --reading" % (type(e).__name__, e)]
    last = ""
    for attempt in range(1, TRIES + 1):
        try:
            _git(repo, "fetch", "-q", remote, branch)
            up = _git(repo, "rev-parse", "--verify", "-q", "%s/%s^{commit}" % (remote, branch)).strip()
            old = _published(repo, up)
        except GitFailed as e:
            return FAILED, ["FAILED: %s (nothing pushed)" % e]
        if old == text:
            if not dry:
                _write_reading(reading, "unchanged", n, top, up, now)
            return OK, ["%d act(s) to rev %d: unchanged on %s/%s (%s)" % (n, top, remote, branch, up[:10])]
        lost = _lost(old or "", text)
        if lost:
            aid = json.loads(lost).get("id", "?") if lost.startswith("{") else "?"
            return REFUSED, ["REFUSED: the export lacks act %s that %s:%s holds (a store set up again, replaced or "
                             "rewritten); origin's file kept, nothing pushed" % (aid, branch, PATH)]
        if dry:
            return OK, ["would push %d act(s) to rev %d onto %s/%s (%s)" % (n, top, remote, branch, up[:10])]
        try:
            sha = _commit(repo, up, text, "control: acts export, %d act(s) to rev %d" % (n, top))
        except GitFailed as e:
            return FAILED, ["FAILED: %s (nothing pushed)" % e]
        if before_push:
            before_push()
        r = subprocess.run(["git", "-C", repo, "push", "-q", remote, "%s:refs/heads/%s" % (sha, branch)],
                           # budget: danger=a hung push holds the export tick; never reached in the 14 days to 2026-11-24; no
                           # budget: record of its run
                           capture_output=True, text=True, timeout=120)
        if r.returncode == 0:
            subprocess.run(["git", "-C", repo, "update-ref", "refs/remotes/%s/%s" % (remote, branch), sha],
                           capture_output=True, timeout=30)
            _write_reading(reading, "published", n, top, sha, now)
            return OK, ["%d act(s) to rev %d pushed (try %d)" % (n, top, attempt), "PUBLISHED %s" % sha]
        said = (r.stderr or r.stdout).strip()      # the reject words lead git's message: read it whole
        last = " ".join(ln for ln in said.splitlines() if not ln.startswith("hint:"))[:300]
        if not any(w in said for w in REJECT_WORDS):
            return FAILED, ["FAILED: the push exited %d: %s" % (r.returncode, last)]
    return FAILED, ["FAILED: the push was refused %d times, origin kept moving: %s" % (TRIES, last)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--store", help="the control store (default: control.db_path())")
    ap.add_argument("--reading", help="the reading file (default: <data root>/control/acts_export.json)")
    ap.add_argument("--dry", action="store_true")
    o = ap.parse_args(argv)
    code, lines = run(repo=o.repo, store=o.store, reading=o.reading, dry=o.dry)
    for ln in lines:
        print(ln)
    return code


if __name__ == "__main__":
    sys.exit(main())
