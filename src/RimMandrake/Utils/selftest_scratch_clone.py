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

        # transcript residue: noise already on origin is not unpushed work; a record is kept, then not unpushed; a record that
        # cannot be kept, ledger lines origin lacks, and real edits still are
        nz = BASE / "nz"
        sh("git", "clone", "-q", str(work), str(nz))
        (nz / "conversations").mkdir()
        (nz / "conversations" / "t.md").write_text("talk\n")
        kept = BASE / "transcripts"
        os.environ["RM_POOL_ROOT"] = str(BASE / "nopool")
        kept.write_text("in the way\n")     # no archive can be made: the record is all there is
        check(sc.clone_unpushed(nz) == ["dirty"], f"a transcript that cannot be kept is unpushed: {sc.clone_unpushed(nz)}")
        kept.unlink()
        check(sc.clone_unpushed(nz) == [], f"a transcript origin lacks is kept, not unpushed: {sc.clone_unpushed(nz)}")
        check([f.read_text() for f in kept.glob("t-*.md")] == ["talk\n"], "and its bytes are in the keep")
        (nz / "conversations" / "t.md").write_text("talk\nmore\n")
        check(sc.clone_unpushed(nz) == [] and len(list(kept.glob("t-*.md"))) == 2, "a grown record is kept again, the old one stays")
        (nz / "conversations" / "t.md").write_text("talk\n")
        (nz / "conversations" / "w.txt").write_text("not a record\n")
        check(sc.clone_unpushed(nz) == ["dirty"], "only a record is excused under conversations/")
        (nz / "conversations" / "w.txt").unlink()
        del os.environ["RM_POOL_ROOT"]
        commit_to_seed(work, "conversations/t.md", "talk\n")
        sh("git", "-C", str(nz), "fetch", "-q")
        check(sc.clone_unpushed(nz) == [], f"a transcript origin holds is not: {sc.clone_unpushed(nz)}")
        (nz / "a.txt").write_text("edited\n")
        check(sc.clone_unpushed(nz) == ["dirty"], "a real edit alongside it still is")
        sh("git", "-C", str(nz), "checkout", "-q", "--", "a.txt")
        led = nz / "infrastructure/state/ledger/events"
        led.mkdir(parents=True)
        (led / "X.jsonl").write_text('{"a":1}\n{"a":2}\n')
        commit_to_seed(work, "infrastructure/state/ledger/events/X.jsonl", '{"a":1}\n{"a":2}\n{"a":3}\n')
        sh("git", "-C", str(nz), "fetch", "-q")
        check(sc.clone_unpushed(nz) == [], "ledger lines already on origin are not unpushed")
        (led / "X.jsonl").write_text('{"a":1}\n{"a":9}\n')
        check(sc.clone_unpushed(nz) == ["dirty"], "a ledger line origin lacks is")

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
        # Operations' cause 1, the blind checker's fixture: idle, not in use, at origin, a transcript its only residue
        (pool / "p4" / "conversations").mkdir(exist_ok=True)
        (pool / "p4" / "conversations" / "run.md").write_text("a run's record\n")
        age(pool / "p4", 7300)
        rd = sc.pool_reading()
        check(rd["stranded"] == ["p2"] and rd["breach"] == 1, f"a transcript alone strands nothing: {rd['stranded']}")
        check(sc.pool_reuse(pool / "p6") == pool / "p6" and not (pool / "p4").exists(), "and blocks no reuse")
        # POOL_STATE_COMMITS_PIN_CLONE_FOREVER: a trailing lesson commit is not stranded work; a clone a live item owns is not stranded
        (pool / "p6" / "infrastructure/state/lessons").mkdir(parents=True, exist_ok=True)
        (pool / "p6" / "infrastructure/state/lessons/l.md").write_text("a lesson\n")
        sh("git", "-C", str(pool / "p6"), "add", "infrastructure/state/lessons/l.md")
        sh("git", "-C", str(pool / "p6"), "commit", "-q", "-m", "lesson")
        check(sc.clone_unpushed(pool / "p6") == [] and sc.clone_unpushed(pool / "p6", strict=True) == ["commits"],
              "a state-only commit is not stranded work, but reuse (strict) never drops it")
        # POOL_STRANDED_FIX_LANDED_COMMITS_STILL_HOWL: origin holding a commit's content under another hash strands nothing
        hw = BASE / "howl"
        hw.mkdir()
        saved_root = os.environ["RM_POOL_ROOT"]
        os.environ["RM_POOL_ROOT"] = str(hw)
        sh("git", "clone", "-q", str(BASE / "mirror.git"), str(hw / "h1"))
        h1 = hw / "h1"
        sh("git", "-C", str(h1), "fetch", "-q", str(BASE / "mirror.git"), "+refs/remotes/origin/main:refs/remotes/origin/main")
        sh("git", "-C", str(h1), "checkout", "-q", "-B", "main", "refs/remotes/origin/main")

        def local(c, name, text, msg):
            (c / name).parent.mkdir(parents=True, exist_ok=True)
            (c / name).write_text(text)
            sh("git", "-C", str(c), "add", name)
            sh("git", "-C", str(c), "commit", "-q", "-m", msg)
        aged = lambda c: age(c, 7300)
        # 1. a real commit origin has not got is stranded, and a stale ref is levelled for nothing
        local(h1, "real.txt", "real\n", "real")
        aged(h1)
        check(sc.clone_unpushed(h1) == ["commits"], "a real commit is at risk")
        idle0 = sc.clone_idle_s(h1)
        check(sc.pool_reading()["stranded"] == ["h1"], "and stranded when idle")
        check(sc.clone_idle_s(h1) >= idle0 - 60 and sc.clone_idle_s(h1) >= sc.POOL_IDLE_S,
              "the reading's fetch does not restart the idle clock it reads")
        # 2. the same patch lands under another hash: only the fetch shows it, and then git cherry covers it
        local(work, "real.txt", "real\n", "real, landed by another hand")
        sh("git", "-C", str(work), "push", "-q", str(BASE / "mirror.git"), "HEAD:refs/remotes/origin/main")
        check(sc.clone_unpushed(h1) == ["commits"], "against the stale ref it still reads at risk")
        rd = sc.pool_reading()
        check(rd["stranded"] == [] and rd["breach"] == 0, f"the reading fetches first, and a cherry-covered commit strands nothing: {rd['stranded']}")
        check(sc.clone_unpushed(h1) == [] and sc.clone_unpushed(h1, strict=True) == [], "a reuse's reset loses nothing either")
        # 2b. origin edited the file again since: the content differs now, only the patch id still shows it landed
        (h1 / "again.txt").write_text("first\n")
        sh("git", "-C", str(h1), "add", "again.txt")
        sh("git", "-C", str(h1), "commit", "-q", "-m", "again, here")
        local(work, "again.txt", "first\n", "again, landed")
        local(work, "again.txt", "first\nsecond\n", "again, edited on")
        sh("git", "-C", str(work), "push", "-q", str(BASE / "mirror.git"), "HEAD:refs/remotes/origin/main")
        sh("git", "-C", str(h1), "fetch", "-q", str(BASE / "mirror.git"), "+refs/remotes/origin/main:refs/remotes/origin/main")
        check(sc.clone_unpushed(h1) == [], "a landed patch origin has since edited on is covered by git cherry")
        # 3. mixed real + ledger whose patch id differs (origin's ledger grew around it): covered by content, line by line
        led = "infrastructure/state/ledger/events/H.jsonl"
        sh("git", "-C", str(h1), "fetch", "-q", str(BASE / "mirror.git"), "+refs/remotes/origin/main:refs/remotes/origin/main")
        sh("git", "-C", str(h1), "checkout", "-q", "-B", "main", "refs/remotes/origin/main")
        local(h1, led, '{"h":1}\n{"h":2}\n', "ledger only, under another hash")
        (h1 / "mix.txt").write_text("mixed\n")
        sh("git", "-C", str(h1), "add", "mix.txt")
        sh("git", "-C", str(h1), "commit", "-q", "--amend", "-m", "mixed real and ledger")
        check(sc.clone_unpushed(h1) == ["commits"], "a mixed commit origin lacks is at risk")
        (work / "mix.txt").write_text("mixed\n")
        sh("git", "-C", str(work), "add", "mix.txt")
        (work / led).parent.mkdir(parents=True, exist_ok=True)
        (work / led).write_text('{"h":0}\n{"h":1}\n{"h":2}\n{"h":3}\n')
        sh("git", "-C", str(work), "add", led)
        sh("git", "-C", str(work), "commit", "-q", "-m", "landed with more ledger")
        sh("git", "-C", str(work), "push", "-q", str(BASE / "mirror.git"), "HEAD:refs/remotes/origin/main")
        sh("git", "-C", str(h1), "fetch", "-q", str(BASE / "mirror.git"), "+refs/remotes/origin/main:refs/remotes/origin/main")
        check("-" not in sh("git", "-C", str(h1), "cherry", "refs/remotes/origin/main", "main")[:1], "fixture: git cherry alone does not cover this one")
        check(sc.clone_unpushed(h1) == [] and sc.clone_unpushed(h1, strict=True) == [], "every path on origin, ledger by line: covered")
        # 4. what must still howl: a ledger line origin lacks, a real line beside covered ones, a deletion, an empty commit, a stack
        (h1 / led).write_text('{"h":1}\n{"h":2}\n{"h":9}\n')
        sh("git", "-C", str(h1), "add", led)
        sh("git", "-C", str(h1), "commit", "-q", "--amend", "-m", "mixed, with a line origin lacks")
        check(sc.clone_unpushed(h1, strict=True) == ["commits"], "one ledger line origin lacks keeps a mixed commit at risk")
        sh("git", "-C", str(h1), "reset", "-q", "--hard", "refs/remotes/origin/main")
        (h1 / "mix2.txt").write_text("not landed\n")
        (h1 / led).write_text('{"h":1}\n')
        sh("git", "-C", str(h1), "add", "mix2.txt", led)
        sh("git", "-C", str(h1), "commit", "-q", "-m", "a covered ledger line beside a real file")
        check(sc.clone_unpushed(h1) == ["commits"], "a real file origin lacks keeps a mixed commit at risk")
        sh("git", "-C", str(h1), "reset", "-q", "--hard", "refs/remotes/origin/main")
        sh("git", "-C", str(h1), "rm", "-q", "mix.txt")
        sh("git", "-C", str(h1), "commit", "-q", "-m", "a deletion")
        check(sc.clone_unpushed(h1) == ["commits"], "a deletion proves nothing")
        sh("git", "-C", str(h1), "reset", "-q", "--hard", "refs/remotes/origin/main")
        sh("git", "-C", str(h1), "commit", "-q", "--allow-empty", "-m", "empty")
        check(sc.clone_unpushed(h1) == ["commits"], "an empty commit proves nothing")
        sh("git", "-C", str(h1), "reset", "-q", "--hard", "refs/remotes/origin/main")
        local(h1, "real.txt", "real again\n", "unlanded edit")
        sh("git", "-C", str(h1), "revert", "--no-edit", "HEAD")
        check(sc.clone_unpushed(h1) == ["commits"], "a stack with one uncovered commit is at risk")
        sh("git", "-C", str(h1), "reset", "-q", "--hard", "refs/remotes/origin/main")
        # 5. a lesson commit origin holds is reusable too; one it lacks stays strict-only, as p6 above proves
        local(h1, "infrastructure/state/lessons/h.md", "lesson\n", "lesson here")
        check(sc.clone_unpushed(h1, strict=True) == ["commits"], "a lesson origin lacks: reuse still refuses")
        local(work, "infrastructure/state/lessons/h.md", "lesson\n", "lesson landed")
        sh("git", "-C", str(work), "push", "-q", str(BASE / "mirror.git"), "HEAD:refs/remotes/origin/main")
        sh("git", "-C", str(h1), "fetch", "-q", str(BASE / "mirror.git"), "+refs/remotes/origin/main:refs/remotes/origin/main")
        check(sc.clone_unpushed(h1, strict=True) == [], "a lesson origin holds: reuse may reset")
        # 6. a store that cannot be read leaves the verdict as it was: stranded, not silently clean
        local(h1, "real3.txt", "x\n", "real 3")
        aged(h1)
        store = os.environ["RM_OBJSTORE"]
        os.environ["RM_OBJSTORE"] = str(BASE / "no-such-store.git")
        check(sc.pool_reading()["stranded"] == ["h1"], "no store to fetch from: still stranded")
        os.environ["RM_OBJSTORE"] = store
        os.environ["RM_POOL_ROOT"] = saved_root
        # the item says lesson OR LEDGER: each kind alone, in its own clone, and one commit that also holds real work
        led_c = BASE / "ledger_only"
        sh("git", "clone", "-q", str(work), str(led_c))
        (led_c / "infrastructure/state/ledger/events").mkdir(parents=True, exist_ok=True)
        (led_c / "infrastructure/state/ledger/events/BENCH.jsonl").write_text('{"tail":"after the landing"}\n')
        sh("git", "-C", str(led_c), "add", "infrastructure/state/ledger/events/BENCH.jsonl")
        sh("git", "-C", str(led_c), "commit", "-q", "-m", "ledger tail")
        check(sc.clone_unpushed(led_c) == [], f"a ledger-only commit is not stranded work: {sc.clone_unpushed(led_c)}")
        check(sc.clone_unpushed(led_c, strict=True) == ["commits"], "and reuse (strict) never drops it")
        # SCRATCH_STRANDED_FIX_SHARDS_CRY_WOLF cause 2: a one-line clean-mark (code_review shard) commit held through a game wait
        cr_c = BASE / "review_only"
        sh("git", "clone", "-q", str(work), str(cr_c))
        (cr_c / "infrastructure/state/code_review").mkdir(parents=True, exist_ok=True)
        (cr_c / "infrastructure/state/code_review/BENCH.jsonl").write_text('{"clean":"x.py"}\n')
        sh("git", "-C", str(cr_c), "add", "infrastructure/state/code_review/BENCH.jsonl")
        sh("git", "-C", str(cr_c), "commit", "-q", "-m", "mark clean")
        check(sc.clone_unpushed(cr_c) == [], f"a clean-mark-only commit is not stranded work: {sc.clone_unpushed(cr_c)}")
        check(sc.clone_unpushed(cr_c, strict=True) == ["commits"], "and reuse (strict) never drops a clean mark")
        (led_c / "infrastructure/state/ledger/events/BENCH.jsonl").write_text('{"tail":"after the landing"}\n{"tail":"and more"}\n')
        (led_c / "mixed_real.txt").write_text("real work\n")
        sh("git", "-C", str(led_c), "add", "infrastructure/state/ledger/events/BENCH.jsonl", "mixed_real.txt")
        sh("git", "-C", str(led_c), "commit", "-q", "-m", "ledger and real work")
        check(sc.clone_unpushed(led_c) == ["commits"], f"a commit holding real work beside a ledger line is stranded: {sc.clone_unpushed(led_c)}")
        owner = BASE / "owner" / "items" / "I" / "state.json"
        owner.parent.mkdir(parents=True)
        os.environ["RM_POOL_STATE_GLOB"] = str(BASE / "owner" / "items" / "*" / "state.json")
        for live in ({"status": "game", "game": {"phase": "proving"}}, {"status": "queued"}, {"status": "running"}):
            owner.write_text(json.dumps({**live, "clone": str(pool / "p2")}))
            rd = sc.pool_reading()
            check(rd["stranded"] == [] and rd["breach"] == 0, f"a live item's clone is the belt's, not stranded ({live}): {rd['stranded']}")
        # POOL_STRANDS_SALVAGE_BLOCKED_HOLD_THE_BAG: release_parked carries all a put-down item holds, so one still here is the alarm
        for down in ({"status": "blocked"}, {"status": "held"}, {"status": "game"}, {"status": "game", "game": {"phase": "waiting"}}):
            owner.write_text(json.dumps({**down, "clone": str(pool / "p2")}))
            check(not sc.owned_by_item(pool / "p2") and sc.pool_reading()["stranded"] == ["p2"], f"a put-down item's clone still holding work is stranded ({down})")
        owner.write_text(json.dumps({"status": "done", "clone": str(pool / "p2")}))
        check(sc.pool_reading()["stranded"] == ["p2"], "a finished item owns nothing")
        # the DEFAULT glob, which every other check here overrides, must find what relentless's own Store writes
        sys.path.insert(0, str(HERE.parent / "rimflow"))
        import relentless as R
        check(str(sc.RM / "relentless") == R.DEFAULT_ROOT, f"the store's root is relentless's: {sc.RM} {R.DEFAULT_ROOT}")
        # the two copies of "what a trailing commit may touch" must stay one list, or a clone relentless parks reads stranded here
        check(sc.POOL_STATE == R.POOL_STATE, f"scratch_clone's POOL_STATE is relentless's: {sc.POOL_STATE} {R.POOL_STATE}")
        check(sc.POOL_NOISE == R.POOL_NOISE, f"scratch_clone's POOL_NOISE is relentless's: {sc.POOL_NOISE} {R.POOL_NOISE}")
        real_rm, sc.RM = sc.RM, BASE / "rm"
        del os.environ["RM_POOL_STATE_GLOB"]
        store = R.Store(str(sc.RM / "relentless"))
        st = R.new_state("I", 0, "t")
        st["clone"] = str(pool / "p2")
        store.save(st)
        check(sc.pool_state_files() == [store.p("items", "I", "state.json")], f"the default glob sees a real state file: {sc.pool_state_files()}")
        check(sc.owned_by_item(pool / "p2"), "and through it a real item owns its clone")
        sc.RM = real_rm
        # a pool root this process may not look at is not an empty pool (POOL_READING_FIX_LOCKED_READS_EMPTY)
        os.environ["RM_POOL_STATE_GLOB"] = str(BASE / "nostate*.json")
        wall = BASE / "wall"
        (wall / "clones").mkdir(parents=True)
        walled_root, os.environ["RM_POOL_ROOT"] = os.environ["RM_POOL_ROOT"], str(wall / "clones")
        sc.pool_reading()
        last = (sc.state_dir() / "pool.json").read_text()
        os.chmod(wall, 0)
        try:
            blocked = False
            try:
                sc.pool_reading()
            except sc.PoolUnreadable:
                blocked = True
            check(blocked, "a denied pool root raises PoolUnreadable, it does not read count=0")
            check((sc.state_dir() / "pool.json").read_text() == last, "and writes no reading over the last good one")
            rc, said = quiet(sc.main, ["pool"])
            check(rc == 3 and '"unreadable"' in said and '"last_reading"' in said, f"pool says unreadable and shows the last reading: {rc} {said[:200]}")
        finally:
            os.chmod(wall, 0o755)
        os.environ["RM_POOL_ROOT"] = str(BASE / "no" / "such" / "root")
        check(sc.pool_reading()["count"] == 0, "a missing root is still measured empty")
        os.environ["RM_POOL_ROOT"] = walled_root
        os.environ["RM_POOL_STATE_GLOB"] = str(BASE / "nostate*.json")
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
                if ".git" not in f.parts and (f.is_file() or f.is_dir()):     # an untracked dir's own mtime is its age
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
        # SCRATCH_STRANDED_FIX_SHARDS_CRY_WOLF cause 1: a helper's shard whose every line main holds, judged against the MIRROR
        # (each clone's own origin/main is left at plant time, before the lines landed: the stale ref of a --shared clone)
        led = "infrastructure/state/ledger/events/BENCH.jsonl"
        for n in ("shardlanded", "shardnew", "shardgone"):
            plant(n)
        (work / led).parent.mkdir(parents=True, exist_ok=True)
        (work / led).write_text('{"a":1}\n{"b":2}\n{"c":3}\n')
        sh("git", "-C", str(work), "add", led)
        sh("git", "-C", str(work), "commit", "-q", "-m", "shard lines land")
        sh("git", "-C", str(work), "push", "-q", str(BASE / "mirror.git"), "HEAD:refs/remotes/origin/main")
        sr._MIRROR_TIPS = None
        for n, text in (("shardlanded", '{"a":1}\n{"c":3}\n'), ("shardnew", '{"a":1}\n{"never":"landed"}\n')):
            (scr / n / led).parent.mkdir(parents=True, exist_ok=True)
            (scr / n / led).write_text(text)
        (scr / "shardgone" / "infrastructure/state/code_review").mkdir(parents=True)
        (scr / "shardgone" / "infrastructure/state/code_review/BENCH.jsonl").write_text('{"main":"has no such file"}\n')
        check(not sc.noise_on_mirror(scr / "shardlanded", "a.txt", sr.mirror_tips()[0]), "a non-noise path is never excused")
        for n in ("pushed", "unpushed", "dirty", "built", "held", "rewritten", "shardlanded", "shardnew", "shardgone"):
            idle(scr / n)
        ss = sc.scratch_stranded()
        rows = {Path(r["path"]).name: r for r in ss["rows"]}
        names = {Path(p).name for p in ss["stranded"]}
        check(names == {"unpushed", "dirty", "held", "shardnew", "shardgone"}, f"exactly the unlanded idle clones are stranded: {sorted(names)}")
        check("shardlanded" not in rows, f"a shard whose lines main holds is not work, stale origin ref or not: {rows.get('shardlanded')}")
        check(rows.get("shardnew", {}).get("holds") == ["1 dirty file(s)"], f"a shard line main lacks is held: {rows.get('shardnew')}")
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
