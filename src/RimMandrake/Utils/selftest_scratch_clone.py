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

        # The bounded pool: cap at creation, reuse before create, stranded work is an alarm and is never reused.
        pool = BASE / "scratch" / "pool"
        os.environ.update({"RM_SEAT": "pool", "RM_POOL_ROOT": str(pool), "RM_POOL_MAX_CLONES": "2",
                           "RM_POOL_STATE_GLOB": str(BASE / "nostate*.json")})

        def age(c: Path, secs: int):
            for n in (".git/HEAD", ".git/logs/HEAD", ".git/index", ".git/FETCH_HEAD"):
                if (c / n).exists():
                    t0 = (c / n).stat().st_mtime - secs
                    os.utime(c / n, (t0, t0))

        r1, _ = quiet(sc.clone, "pool test", "p1", True, [], False, False)
        r2, _ = quiet(sc.clone, "pool test", "p2", True, [], False, False)
        check(r1 == 0 and r2 == 0 and (pool / "p1").is_dir() and (pool / "p2").is_dir(), "pool clones under the cap are made")
        rd = sc.pool_reading()
        check(rd["count"] == 2 and rd["breach"] == 0 and (sc.state_dir() / "pool.json").exists(), f"pool reading: {rd['count']}")
        r3, _ = quiet(sc.clone, "pool test", "p3", True, [], False, False)
        check(r3 == 1 and not (pool / "p3").exists(), "an over-cap attempt is REFUSED and makes no clone")
        check("POOL REFUSED" in (sc.read_jsonl("uses.jsonl")[-1].get("error") or ""), "the refusal is on the record")
        age(pool / "p1", 7200)
        r3, _ = quiet(sc.clone, "pool test", "p3", True, [], False, False)
        check(r3 == 0 and (pool / "p3").is_dir() and not (pool / "p1").exists() and sc.pool_reading()["count"] == 2,
              "at the cap an idle pushed clone is reused (renamed), not added")
        sh("git", "-C", str(pool / "p2"), "commit", "-q", "--allow-empty", "-m", "unpushed")
        age(pool / "p2", 7200)
        age(pool / "p3", 7200)
        rd = sc.pool_reading()
        check(rd["stranded"] == ["p2"] and rd["breach"] == 1, f"unpushed idle work is stranded and a breach: {rd['stranded']}")
        r4, _ = quiet(sc.clone, "pool test", "p4", True, [], False, False)
        check(r4 == 0 and (pool / "p4").is_dir() and (pool / "p2").is_dir()
              and sh("git", "-C", str(pool / "p2"), "log", "-1", "--format=%s") == "unpushed",
              "a clone with unpushed work is never reused")
        os.environ["RM_POOL_MAX_CLONES"] = "9"
        os.environ["RM_POOL_MAX_BYTES"] = "1"
        r5, _ = quiet(sc.clone, "pool test", "p5", True, [], False, False)
        check(r5 == 1 and not (pool / "p5").exists(), "the byte cap refuses too")

        # A helper's clone outside the pool: its unlanded work is an alarm too, and PROTECTED is no excuse for one.
        import scratch_reap as sr
        scr = BASE / "scratch" / "BENCH"
        os.environ.update({"SCRATCH_REAP_MIRRORS": str(BASE / "mirror.git"), "RM_SESSION_GLOB": str(BASE / "nosession*"),
                           "SCRATCH_REAP_PROTECTED": str(scr / "held"), "RM_SCRATCH_ROOT": str(scr)})
        sr._MIRROR_TIPS = sc._MAIN_PRINTS = None

        def plant(name: str) -> Path:
            c = scr / name
            sh("git", "clone", "-q", "--shared", str(work), str(c))
            sh("git", "-C", str(c), "update-ref", "refs/remotes/origin/main", "HEAD")
            return c

        def idle(c: Path):
            age(c, 7200)
            for f in c.rglob("*"):
                if ".git" not in f.parts and f.is_file():
                    t0 = f.stat().st_mtime - 7200
                    os.utime(f, (t0, t0))

        for n in ("pushed", "unpushed", "dirty", "built", "held", "fresh", "rewritten"):
            plant(n)
        subprocess.run(["git", "-C", str(scr / "unpushed"), "commit", "-q", "--allow-empty", "-m", "never pushed"], check=True,
                       env={**os.environ, "GIT_AUTHOR_DATE": "1700000000 +0000", "GIT_COMMITTER_DATE": "1700000000 +0000"})
        # a local tracking ref at the tip is what read as pushed before: only the mirror proves a push
        sh("git", "-C", str(scr / "unpushed"), "update-ref", "refs/remotes/origin/main", "HEAD")
        (scr / "dirty" / "a.txt").write_text("edited, never committed\n")
        (scr / "built" / "out.dll").write_text("built\n")
        (scr / "held" / "a.txt").write_text("held in PROTECTED\n")
        (scr / "fresh" / "a.txt").write_text("being worked on now\n")
        # main rewritten under the clone: same dates, new message and blobs, so the old commit is not reachable from the mirror
        cw = scr / "rewritten"
        (cw / "n.txt").write_text("old blob\n")
        sh("git", "-C", str(cw), "add", "n.txt")
        sh("git", "-C", str(cw), "commit", "-q", "-m", "before the rewrite")
        at, ct = sh("git", "-C", str(cw), "log", "-1", "--format=%at %ct").split()
        (work / "n.txt").write_text("rewritten blob\n")
        sh("git", "-C", str(work), "add", "n.txt")
        subprocess.run(["git", "-C", str(work), "commit", "-q", "-m", "after the rewrite"], check=True,
                       env={**os.environ, "GIT_AUTHOR_DATE": at + " +0000", "GIT_COMMITTER_DATE": ct + " +0000"})
        sh("git", "-C", str(work), "push", "-q", str(BASE / "mirror.git"), "HEAD:refs/remotes/origin/main")
        sr._MIRROR_TIPS = None
        sh("git", "-C", str(cw), "update-ref", "refs/remotes/origin/main", "HEAD")
        for n in ("pushed", "unpushed", "dirty", "built", "held", "rewritten"):
            idle(scr / n)
        ss = sc.scratch_stranded()
        rows = {Path(r["path"]).name: r for r in ss["rows"]}
        names = {Path(p).name for p in ss["stranded"]}
        check(names == {"unpushed", "dirty", "held"}, f"exactly the unlanded idle clones are stranded: {sorted(names)}")
        check("1 commit(s) on no remote" in rows.get("unpushed", {}).get("holds", []), f"the commit is named: {rows.get('unpushed')}")
        check("fresh" in rows and not rows["fresh"]["stranded"], "work edited a minute ago is held but not stranded yet")
        check("pushed" not in names and "built" not in names and "rewritten" not in names, "pushed, built and rewritten stay silent")
        check((sc.state_dir() / "scratch_stranded.json").exists(), "the reading is written where the alarm says")
        sr_git, sr.git = sr.git, lambda *a, **k: subprocess.CompletedProcess(a, 128, "", "fatal: planted")
        try:
            check("unreadable" in " ".join(sc.clone_unlanded(scr / "pushed")[0]), "a clone that cannot be read is held, not clean")
        finally:
            sr.git = sr_git
    finally:
        shutil.rmtree(BASE, ignore_errors=True)
    print(f"selftest_scratch_clone: {'FAIL ' + str(len(FAILS)) if FAILS else 'OK'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
