#!/usr/bin/env python3
"""Selftest for scratch_clone.py — a throwaway seed/store/scratch tree under
/home/mandrake/rm/scratch/<SEAT>/ (ext4, never /tmp), every path env-overridden so the real
store and ~/.local/state/rm-objstore are never touched."""
# selftest-timeout: 180
from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

SEAT = "SELFTEST"
BASE = Path("/home/mandrake/rm/scratch") / os.environ.get("RM_SEAT", "BENCH") / f"_selftest_objstore_{os.getpid()}"
os.environ.update({
    "RM_SEAT": SEAT,
    "RM_OBJSTORE": str(BASE / "store.git"),
    "RM_OBJSTORE_SEED": str(BASE / "mirror.git"),
    "RM_SCRATCH_ROOT": str(BASE / "scratch"),
    "RM_OBJSTORE_STATE": str(BASE / "state"),
    "RM_OBJSTORE_SCAN": str(BASE / "scratch" / "*" / "*"),
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
})
import scratch_clone as sc  # noqa: E402

FAILS: list[str] = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
        print("FAIL", msg)


def sh(*a, cwd=None):
    return subprocess.run(a, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def commit_to_seed(work: Path, fname: str, text: str):
    (work / fname).parent.mkdir(parents=True, exist_ok=True)
    (work / fname).write_text(text)
    sh("git", "-C", str(work), "add", fname)
    sh("git", "-C", str(work), "commit", "-q", "-m", fname)
    sh("git", "-C", str(work), "push", "-q", str(BASE / "mirror.git"), "HEAD:refs/remotes/origin/main")


def quiet(fn, *a, **k):
    buf = io.StringIO()
    with redirect_stdout(buf):
        r = fn(*a, **k)
    return r, buf.getvalue()


def main() -> int:
    BASE.mkdir(parents=True)
    try:
        work = BASE / "work"
        sh("git", "init", "-q", "-b", "main", str(work))
        sh("git", "init", "-q", "--bare", str(BASE / "mirror.git"))
        commit_to_seed(work, "a.txt", "one\n")
        commit_to_seed(work, "sub/b.txt", "two\n")
        sh("git", "-C", str(BASE / "mirror.git"), "repack", "-q", "-a", "-d")   # a pack to hard-link

        r = sc.init()
        check(r["created"] and r["packs_linked"] >= 2, f"init hard-links seed packs: {r}")
        for k, v in sc.STORE_CONFIG.items():
            check(sh("git", "--git-dir", os.environ["RM_OBJSTORE"], "config", k) == v, f"store config {k}")
        own, linked = sc.own_bytes(BASE / "store.git/objects/pack")
        check(linked > 0 and own == 0, f"init re-uses the seed packs, writes no duplicate: own={own}")

        rc, out = quiet(sc.clone, "selftest plain", "plain", False, [], False, False)
        dest = Path(out.strip())
        check(rc == 0 and dest == BASE / "scratch" / SEAT / "plain", f"clone path {out!r}")
        alt = (dest / ".git/objects/info/alternates").read_text().strip()
        check(os.path.realpath(alt) == os.path.realpath(BASE / "store.git/objects"),
              f"borrower points at the STORE: {alt}")
        check(sh("git", "-C", str(dest), "remote", "get-url", "origin") == sc.ORIGIN_URL, "origin is GitHub")
        check(not (dest / "a.txt").exists(), "no-checkout is the default")

        rc, out = quiet(sc.clone, "selftest full", "full", True, [], False, False)
        check(rc == 0 and (BASE / "scratch" / SEAT / "full" / "sub/b.txt").read_text() == "two\n", "--checkout")
        commit_to_seed(work, "c/d.txt", "three\n")       # store must pick this up on the next clone
        rc, out = quiet(sc.clone, "selftest sparse", "sparse", False, ["c"], False, False)
        sp = BASE / "scratch" / SEAT / "sparse"
        check(rc == 0 and (sp / "c/d.txt").exists() and not (sp / "sub/b.txt").exists(),
              "--sparse checks out only the cone and sees the refreshed store")
        rc, out = quiet(sc.clone, "selftest durable", "durable", False, [], False, True)
        check(rc == 0 and not (BASE / "scratch" / SEAT / "durable/.git/objects/info/alternates").exists(),
              "--dissociate leaves no alternates")
        rc, _ = quiet(sc.clone, "selftest dup", "plain", False, [], False, False)
        check(rc == 1, "existing destination refused")

        uses = sc.read_jsonl("uses.jsonl")
        check(len(uses) == 5, f"one record per use: {len(uses)}")
        need = {"ts", "seat", "purpose", "path", "wall_s", "git_dir_own_bytes", "full_clone_bytes",
                "objects_borrowed", "ok", "error"}
        check(need <= set(uses[0]), f"record fields missing: {need - set(uses[0])}")
        check(uses[0]["seat"] == SEAT and uses[0]["objects_borrowed"] > 0, "seat + borrowed objects recorded")
        check(uses[-1]["ok"] is False and "already exists" in uses[-1]["error"], "failure recorded with error")

        # A seat-clone gc cannot reach a store borrower; the store's own gc keeps everything.
        sh("git", "--git-dir", os.environ["RM_OBJSTORE"], "gc", "-q")
        s = sc.sample()
        check(s["borrowers_store"] == 3 and s["borrowers_seat"] == 0, f"borrowers counted: {s}")
        check(s["borrowers_broken"] == [] and s["fsck_sampled"], "healthy borrowers pass the check")
        check(s["disk_free_bytes"] > 0 and s["store_objects"] > 0, "store + disk recorded")

        # Corruption is detected and lands as an incident.
        objs = BASE / "store.git/objects"
        objs.rename(BASE / "objects.aside")
        s = sc.sample()
        (BASE / "objects.aside").rename(objs)
        check(len(s["borrowers_broken"]) == 3 and len(sc.read_jsonl("incidents.jsonl")) == 3,
              f"missing store objects become incidents: {s['borrowers_broken']}")

        rep = sc.report()
        check("corruption incidents" in rep and "VERDICT: BAD" in rep, "report verdict reflects incidents")
        check("4 / 1" in rep, "report counts uses")
    finally:
        shutil.rmtree(BASE, ignore_errors=True)
    print(f"selftest_scratch_clone: {'FAIL ' + str(len(FAILS)) if FAILS else 'OK'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
