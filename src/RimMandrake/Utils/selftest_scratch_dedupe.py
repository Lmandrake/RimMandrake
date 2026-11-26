#!/usr/bin/env python3
"""Selftest of scratch_clone.py dedupe: a borrower drops the objects its alternates already hold, and loses none it
needs. Page: design/specs/2026-11-22-clone-pool-disk-floor/boundary.md (promise borrowers-keep-no-copy-of-the-store).
A throwaway seed, store and borrowers under ~/.cache; every path env-overridden, so the real store is never touched.

    python3 selftest_scratch_dedupe.py      exit 0 green, 1 a red
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True
BASE = Path(tempfile.mkdtemp(prefix="dedupe-", dir=os.path.expanduser("~/.cache")))
os.environ.update({
    "RM_OBJSTORE": str(BASE / "store.git"), "RM_OBJSTORE_SEED": str(BASE / "mirror.git"),
    "RM_OBJSTORE_STATE": str(BASE / "state"), "RM_OBJSTORE_SCAN": str(BASE / "seats" / "*"),
    "RM_POOL_ROOT": str(BASE / "pool"), "RM_SCRATCH_ROOT": str(BASE / "scratch"), "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
})
import scratch_clone as sc  # noqa: E402

FAILS = []


def check(ok, what):
    print("%s %s" % ("PASS" if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


def g(*a):
    return subprocess.run(["git", *a], check=True, capture_output=True, text=True).stdout.strip()


def objects_mb(repo):
    o = sc.objects_dir(Path(repo))
    return sum(f.stat().st_blocks * 512 for f in o.rglob("*") if f.is_file()) / 1e6


def full_copy_borrowing(src, dest, alt):
    """A clone that holds every object itself (as a seat clone that fetched while the store was stale does), then
    borrows from `alt`. Its own commit on top, which no other store holds. -> that commit's sha."""
    g("clone", "-q", "--no-local", "--no-hardlinks", str(src), str(dest))
    (dest / ".git" / "objects" / "info" / "alternates").write_text(str(alt) + "\n")
    (dest / "mine.txt").write_text(os.urandom(200000).hex())
    g("-C", str(dest), "add", "mine.txt")
    g("-C", str(dest), "commit", "-q", "-m", "mine, on no remote")
    return g("-C", str(dest), "rev-parse", "HEAD")


def t_borrowers_keep_no_copy_of_the_store():
    work = BASE / "work"
    g("init", "-q", "-b", "main", str(work))
    for i in range(3):
        (work / ("f%d.bin" % i)).write_text(os.urandom(400000).hex())      # 2.4 MB the store will hold
        g("-C", str(work), "add", "-A")
        g("-C", str(work), "commit", "-q", "-m", "c%d" % i)
    g("init", "-q", "--bare", str(BASE / "mirror.git"))
    g("-C", str(work), "push", "-q", str(BASE / "mirror.git"), "HEAD:refs/remotes/origin/main")
    sc.init()
    store_objects = sc.store_path() / "objects"
    (BASE / "seats").mkdir()
    (BASE / "pool").mkdir()
    seat = BASE / "seats" / "runner"
    mine = full_copy_borrowing(work, seat, store_objects)
    pooled = BASE / "pool" / "SOME_ITEM.det"
    pmine = full_copy_borrowing(work, pooled, store_objects)
    mid = BASE / "seats" / "mid.git"                                   # the mirror's shape: bare, borrows the store
    g("clone", "-q", "--bare", "--shared", str(sc.store_path()), str(mid))
    chained = BASE / "seats" / "bench"
    cmine = full_copy_borrowing(work, chained, mid / "objects")
    alone = BASE / "seats" / "alone"
    g("clone", "-q", "--no-local", str(work), str(alone))             # borrows nothing: not the store's to judge
    before = {p: objects_mb(p) for p in (seat, pooled, chained, alone)}

    rec = sc.dedupe()
    after = {p: objects_mb(p) for p in (seat, pooled, chained, alone)}
    done = {d["repo"] for d in rec["done"]}
    check(str(seat) in done and str(pooled) in done and str(chained) in done
          and all(after[p] < before[p] / 4 for p in (seat, pooled, chained)),
          "borrowers-keep-no-copy-of-the-store: a seat clone, a pool clone and a clone that borrows the store through "
          "another repo drop the objects the store holds (MB before %s, after %s)"
          % ({p.name: round(before[p], 1) for p in before}, {p.name: round(after[p], 1) for p in after}))
    ok = True
    for repo, sha in ((seat, mine), (pooled, pmine), (chained, cmine)):
        r = subprocess.run(["git", "-C", str(repo), "fsck", "--connectivity-only", "--no-dangling"],
                           capture_output=True, text=True)
        ok = ok and r.returncode == 0 and g("-C", str(repo), "cat-file", "-t", sha) == "commit" \
            and len(g("-C", str(repo), "show", sha + ":mine.txt")) == 400000
    check(ok, "borrowers-keep-no-copy-of-the-store: each one still reads its whole history and its own commit, "
              "which the store does not hold")
    named = sc.dedupe([alone])
    check(str(alone) not in done and abs(after[alone] - before[alone]) < 0.01 and not named["done"]
          and [s["repo"] for s in named["skipped"]] == [str(alone)],
          "borrowers-keep-no-copy-of-the-store: a repo whose alternates do not reach the store is left as it is "
          "(%s)" % rec["skipped"])
    check(rec["freed_gb"] >= 0 and (sc.state_dir() / "dedupe.jsonl").is_file(),
          "borrowers-keep-no-copy-of-the-store: the run is recorded with the bytes it freed (%s GB)" % rec["freed_gb"])
    broken = BASE / "pool" / "BROKEN.det"
    (broken / ".git" / "objects" / "info").mkdir(parents=True)
    (broken / ".git" / "objects" / "info" / "alternates").write_text(str(store_objects) + "\n")
    rec = sc.dedupe()
    check(any(f["repo"] == str(broken) for f in rec["failed"]) and str(seat) in {d["repo"] for d in rec["done"]},
          "borrowers-keep-no-copy-of-the-store: a repo git cannot repack is reported failed, and the others are "
          "still done (%s)" % [f["repo"] for f in rec["failed"]])
    check(sc.main(["dedupe"]) == 1, "borrowers-keep-no-copy-of-the-store: the command exits 1 when one failed")
    shutil.rmtree(broken)
    check(sc.main(["dedupe"]) == 0, "borrowers-keep-no-copy-of-the-store: and 0 when none failed")


def main():
    try:
        t_borrowers_keep_no_copy_of_the_store()
    except Exception as e:                  # a crash is a red, named
        check(False, "borrowers-keep-no-copy-of-the-store crashed: %s: %s" % (type(e).__name__, e))
    finally:
        shutil.rmtree(BASE, ignore_errors=True)
    print("RESULT: %s" % ("GREEN" if not FAILS else "RED, %d failing" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
