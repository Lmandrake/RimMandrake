#!/usr/bin/env python3
"""RELENTLESS_BUNDLES_FIX_FOURTEEN_GIG_PATCHES: a bundle holds a worker's WIP, never a tree.

On 2026-11-04 a pool clone's `git fetch` was refused by GitHub after scratch_clone's `git clone --no-checkout`: a .git, no
index, no tree. Relentless read its 44k tracked files as deletions and wrote diff.patch, index.patch and real.patch, each
the whole 3.9 GB tree as --binary preimage: 14 GB a bundle, three such bundles, and nothing reaped them.

  half_made     a clone never checked out bundles to nothing (no deletion patch, no bundle dir).
  half_made_wip ... and a file a worker did write in it is still carried.
  deletion      a worker's deletion is a path in `deleted`, not a preimage; restore_bundle removes it again.
  one_copy      index.patch is dropped when it equals diff.patch; real.patch is a hard link to diff.patch.
  cap           a patch over BUNDLE_PATCH_MAX raises, and no partial bundle dir is left.
  scratch       scratch_clone removes a dest it made when its fetch fails.
  reap          reap_bundles takes a done item's old bundles, keeps an open item's, a young one's, and one still to restore.
"""
import importlib
import io
import contextlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless as R  # noqa: E402
import relentless_disk as D  # noqa: E402

FAILS = []


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def git(cwd, *a):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd, check=True,
                          capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout.strip()


def fx_for(base):
    store = R.Store(base)
    fx = types.SimpleNamespace(base=base, store=store)
    for n in ("bundle_clone", "_bundle_write", "restore_bundle", "restore_commits", "git", "git_ok",
              "changed_paths", "ignored_paths"):
        setattr(fx, n, types.MethodType(getattr(R.Effects, n), fx))
    return fx, store


def origin(base):
    src = os.path.join(base, "origin")
    os.makedirs(os.path.join(src, "d"))
    with open(os.path.join(src, "big.bin"), "wb") as f:
        f.write(os.urandom(2 * 10**6))
    for i in range(30):
        with open(os.path.join(src, "d", "f%d.txt" % i), "w") as f:
            f.write("line %d\n" % i * 50)
    git(base, "init", "-q", "-b", "main", src)
    git(src, "add", "big.bin", "d")
    git(src, "commit", "-q", "-m", "root")
    return src


def t_half_made(base, src):
    fx, store = fx_for(base)
    os.makedirs(store.p("items", "IT"))
    c = os.path.join(base, "half")
    git(base, "clone", "-q", "--no-checkout", src, c)       # the 2026-11-04 state: .git, no index, no tree
    ok(not os.path.exists(os.path.join(c, ".git", "index")), "half_made: the fixture has no index")
    out = fx.bundle_clone("IT", c)
    ok(out is None, "half_made: a never-checked-out clone has nothing to bundle (got %s)" % out)
    ok(not os.path.isdir(store.p("items", "IT", "bundles")) or not os.listdir(store.p("items", "IT", "bundles")),
       "half_made: no bundle dir written")
    c2 = os.path.join(base, "half2")
    git(base, "clone", "-q", "--no-checkout", src, c2)
    with open(os.path.join(c2, "note.md"), "w") as f:
        f.write("a worker wrote this\n")
    out = fx.bundle_clone("IT", c2)
    size = R.bundle_bytes(out) if out else -1
    ok(out is not None and 0 < size < 100000, "half_made_wip: the one file is carried, bundle %d bytes vs 2 MB tree" % size)
    ok(out is not None and not os.path.exists(os.path.join(out, "deleted")), "half_made_wip: nothing listed as deleted")
    ok(out is not None and os.path.getsize(os.path.join(out, "diff.patch")) == 0, "half_made_wip: no tracked patch")


def t_deletion_and_copies(base, src):
    fx, store = fx_for(base)
    os.makedirs(store.p("items", "DEL"), exist_ok=True)
    c = os.path.join(base, "work")
    git(base, "clone", "-q", src, c)
    os.unlink(os.path.join(c, "big.bin"))
    with open(os.path.join(c, "d", "f1.txt"), "a") as f:
        f.write("edited\n")
    git(c, "add", "-A", "d")        # staged and working the same: index.patch would be a second copy
    out = fx.bundle_clone("DEL", c)
    ok(out is not None and R.bundle_bytes(out) < 50000, "deletion: a 2 MB deleted binary costs no preimage (%s bytes)"
       % (R.bundle_bytes(out) if out else None))
    names = open(os.path.join(out, "deleted")).read().split("\0") if out and os.path.exists(os.path.join(out, "deleted")) else []
    ok(names == ["big.bin"], "deletion: the path is listed in `deleted`: %s" % names)
    ok(out is not None and not os.path.exists(os.path.join(out, "index.patch")), "one_copy: index.patch equal to diff.patch is dropped")
    ok(out is not None and os.stat(os.path.join(out, "real.patch")).st_ino == os.stat(os.path.join(out, "diff.patch")).st_ino,
       "one_copy: real.patch is diff.patch's inode")
    fresh = os.path.join(base, "fresh")
    git(base, "clone", "-q", src, fresh)
    bad = fx.restore_bundle("DEL", out, fresh)
    ok(not bad and not os.path.exists(os.path.join(fresh, "big.bin")), "deletion: restore removes it again (%s)" % bad)
    ok("edited" in open(os.path.join(fresh, "d", "f1.txt")).read(), "deletion: the edit comes back too")


def t_cap(base, src):
    fx, store = fx_for(base)
    os.makedirs(store.p("items", "CAP"), exist_ok=True)
    c = os.path.join(base, "capw")
    git(base, "clone", "-q", src, c)
    with open(os.path.join(c, "big.bin"), "wb") as f:
        f.write(os.urandom(2 * 10**6))
    keep = R.BUNDLE_PATCH_MAX
    R.BUNDLE_PATCH_MAX = 10**6
    try:
        raised = None
        try:
            fx.bundle_clone("CAP", c)
        except RuntimeError as e:
            raised = str(e)
    finally:
        R.BUNDLE_PATCH_MAX = keep
    ok(raised is not None and "over the bundle cap" in raised, "cap: a binary patch over a 1 MB cap raises: %s" % raised)
    root = store.p("items", "CAP", "bundles")
    ok(not os.path.isdir(root) or not os.listdir(root), "cap: no partial bundle dir is left")


def t_scratch(base, src):
    os.environ.update({"RM_OBJSTORE": os.path.join(base, "sc", "store.git"), "RM_OBJSTORE_SEED": os.path.join(base, "seed.git"),
                       "RM_SCRATCH_ROOT": os.path.join(base, "sc", "scratch"), "RM_OBJSTORE_STATE": os.path.join(base, "sc", "state"),
                       "RM_OBJSTORE_SCAN": os.path.join(base, "sc", "scratch", "*", "*"), "RM_SEAT": "T"})
    git(base, "clone", "-q", "--bare", src, os.path.join(base, "seed.git"))
    git(os.path.join(base, "seed.git"), "update-ref", "refs/remotes/origin/main", "refs/heads/main")
    sc = importlib.import_module("scratch_clone")
    keep = sc.ORIGIN_URL
    sc.ORIGIN_URL = os.path.join(base, "no-such-origin.git")      # the fetch is refused, as GitHub refused it
    try:
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            rc = sc.clone("t", "HALF", True, [], True, False)
    finally:
        sc.ORIGIN_URL = keep
    dest = os.path.join(base, "sc", "scratch", "T", "HALF")
    last = (sc.read_jsonl("uses.jsonl") or [{}])[-1]
    ok("fetch" in (last.get("error") or "") and last.get("removed_half_made") is True,
       "scratch: it failed at the fetch, after the clone was made, and said it removed it: %s" % {
           k: last.get(k) for k in ("error", "removed_half_made")})
    ok(rc == 1 and not os.path.exists(dest), "scratch: a failed fetch leaves no half-made clone (rc=%s, exists=%s)"
       % (rc, os.path.exists(dest)))


def t_reap(base):
    store = R.Store(os.path.join(base, "reap"))
    now = time.time()
    for item, status, age, extra in (("DONE_OLD", "done", 4 * 86400, {}), ("DONE_YOUNG", "done", 3600, {}),
                                     ("OPEN_OLD", "blocked", 9 * 86400, {}), ("RETIRED_OLD", "retired", 9 * 86400, {}),
                                     ("DONE_TO_RESTORE", "done", 9 * 86400, {"bundle": "x"})):
        b = store.p("items", item, "bundles", "20261101T000000Z-" + item)
        os.makedirs(b)
        with open(os.path.join(b, "diff.patch"), "w") as f:
            f.write("x")
        os.utime(b, (now - age, now - age))
        store.save(dict({"item": item, "status": status, "gen": 1}, **extra))
    acts = []
    got = D.reap_bundles(store, {}, now, acts)
    gone = [x for x in ("DONE_OLD", "DONE_YOUNG", "OPEN_OLD", "RETIRED_OLD", "DONE_TO_RESTORE")
            if not os.path.isdir(store.p("items", x, "bundles"))]
    ok(gone == ["DONE_OLD"], "reap: only the done item's 4-day-old bundles go: %s" % gone)
    ok(len(got) == 1 and acts and acts[0].get("do") == "bundles_reaped", "reap: one removed and said: %s %s" % (got, acts))


def main():
    base = tempfile.mkdtemp(prefix="bundsz_", dir=os.environ.get("RM_SELFTEST_TMP"))
    try:
        src = origin(base)
        t_half_made(base, src)
        t_deletion_and_copies(base, src)
        t_cap(base, src)
        t_scratch(base, src)
        t_reap(base)
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("%d failed" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
