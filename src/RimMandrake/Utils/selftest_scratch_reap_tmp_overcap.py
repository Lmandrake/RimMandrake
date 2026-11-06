#!/usr/bin/env python3
"""selftest_scratch_reap_tmp_overcap.py — a /tmp git copy over the preserve cap is no longer refused forever
(TMPREAP_PRUNE_OVERCAP_COPY_STUCK_40_HOURS). The instance: /tmp/jpre, 2.2 GB, `git init`, one commit, no remote, src/ and
infrastructure/ untracked: REFUSED hourly for 40 h with "dirty files, over the 2.0 GB preserve cap".

Every path is a temp root; DIRTY_CAP is lowered to 64 KB so no fixture needs 2 GB. Proves: the jpre shape goes and its
commit and only its commit is archived; a file main lacks is kept and a file main holds is not; a remainder over the cap
is kept smallest first and the rest named; a clone with nothing of its own is plainly deleted; and the refusal stands
outside /tmp, with no mirror to vouch, for tracked changes over the cap, and for a young copy. Also that the filing of
this item, which names the directory, does not pin it while another item's mention still does.
"""
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scratch_reap as s                                    # noqa: E402
from selftest_scratch_reap_tmp import own_tree              # noqa: E402

FAILS = []
CAP = 64 * 1024


def ok(cond, what):
    print(("PASS " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def git(cwd, *a):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


def blob(seed: str, n: int) -> bytes:
    return (seed.encode() + b"\n") * (n // (len(seed) + 1) + 1)


def copy_of(top: Path, name: str, main_files: dict, extra: dict | None = None) -> Path:
    """The jpre shape: git init, one commit of `.k`, no remote, a tree that is all untracked."""
    c = top / name
    c.mkdir(parents=True)
    git(c, "init", "-q", "-b", "main")
    (c / ".k").write_text("x\n")
    git(c, "add", ".k")
    git(c, "commit", "-q", "-m", "x")
    for rel, data in {**main_files, **(extra or {})}.items():
        (c / rel).parent.mkdir(parents=True, exist_ok=True)
        (c / rel).write_bytes(data)
    return c


def archive_of(row) -> dict:
    d = Path(row["archive"])
    names = {}
    if (d / "dirty.tar.gz").exists():
        with tarfile.open(d / "dirty.tar.gz") as t:
            names["dirty"] = sorted(m.name for m in t.getmembers() if m.isfile())
    names["bundle"] = (d / "clone.bundle").exists()
    names["manifest"] = json.loads((d / "manifest.json").read_text())
    return names


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="selftest_scratch_reap_tmp_overcap_") as td:
        t = Path(td)
        tmp, other, work = t / "tmp", t / "roots", t / "work"
        for d in (tmp, other, work, t / "transcripts", t / "archive"):
            d.mkdir()
        os.environ.update(SCRATCH_REAP_ROOTS=os.pathsep.join([str(other), str(tmp)]), SCRATCH_REAP_TMP=str(tmp),
                          SCRATCH_REAP_SCAN=os.pathsep.join([str(other), str(tmp)]), SCRATCH_REAP_CORPUS=str(t / "corpus"),
                          SCRATCH_REAP_STATE=str(t / "state"), SCRATCH_REAP_TRANSCRIPTS=str(t / "transcripts"),
                          SCRATCH_REAP_RM_SCRATCH="/nonexistent", LEFTOVERS_ARCHIVE_ROOT=str(t / "archive"),
                          SCRATCH_REAP_MIRRORS=str(t / "mirror.git"), SCRATCH_REAP_TTL_HOURS="0")
        for k in ("SCRATCH_REAP_UNIT", "SCRATCH_REAP_PROTECTED"):
            os.environ.pop(k, None)
        s.DIRTY_CAP = CAP
        s.CTIME_COUNTS = False
        s.proc_entries = own_tree       # a stranger's unreadable /proc in a walled box holds everything

        # main: 200 KB of source, three times the cap, in files of 40 KB
        main_files = {f"src/m{i}/a.py": blob(f"main file {i}", 40 * 1024) for i in range(5)}
        for rel, data in main_files.items():
            (work / rel).parent.mkdir(parents=True, exist_ok=True)
            (work / rel).write_bytes(data)
        git(work, "init", "-q", "-b", "main")
        git(work, "add", "src")
        git(work, "commit", "-q", "-m", "main")
        git(t, "clone", "-q", "--bare", str(work), str(t / "mirror.git"))

        st = t / "corpus" / "infrastructure" / "state"
        (st / "ledger" / "events").mkdir(parents=True)
        (st / "items").mkdir()
        stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        (st / "ledger" / "events" / "BENCH.jsonl").write_text(json.dumps(   # the filing that named jpre pinned it
            {"seat": "RELENTLESS", "event": "file", "id": "TMPREAP_PRUNE_OVERCAP_COPY_STUCK_40_HOURS", "ts": stamp,
             "spec": f"{tmp / 'jpre'} is REFUSED every hourly run"}) + "\n")
        ctx = s.Ctx(time.time())

        def judged(c):
            ctx.refresh()
            return s.judge_clone(c, ctx)

        # the instance
        c = copy_of(tmp, "jpre", main_files)
        row = judged(c)
        ok(row["verdict"] == "ARCHIVE" and row["unique"] == 1, f"the jpre shape is no longer refused ({row['verdict']}: {row['why'][:2]})")
        ok(row["dirty"] == [], f"none of its tree is kept: main holds every byte (dirty={row['dirty'][:3]})")
        ok(any("5 file(s)" in w and "blobs main holds" in w for w in row["why"]), "the row says what was not kept and why")
        failures = []
        s.act(row, ctx, failures)
        ok(row["verdict"] == "DELETED" and not c.exists() and not failures, f"it goes ({row['verdict']}, {failures})")
        got = archive_of(row)
        ok(got["bundle"] and "dirty" not in got, "its one commit is bundled; no dirty tar was made")

        # a file main lacks is kept, a file main holds is not
        mine = blob("an agent's own edit", 300)
        c = copy_of(tmp, "mixed", main_files, {"src/mine.txt": mine})
        row = judged(c)
        ok(row["verdict"] == "ARCHIVE" and row["dirty"] == ["src/mine.txt"], f"only the file main lacks is owed ({row['dirty'][:3]})")
        s.act(row, ctx, failures)
        got = archive_of(row)
        ok(row["verdict"] == "DELETED" and got.get("dirty") == ["src/mine.txt"], f"the archive holds exactly it ({got.get('dirty')})")

        # same bytes as an old main version count: the check is by blob, not by name
        c = copy_of(tmp, "renamed", {f"elsewhere/{i}": d for i, d in enumerate(main_files.values())})
        row = judged(c)
        ok(row["verdict"] == "ARCHIVE" and row["dirty"] == [], "a blob main holds under another name is still held")
        s.act(row, ctx, failures)

        # a remainder over the cap: smallest first, the rest named, and it still goes
        huge = {"own/huge.bin": blob("huge own file", 100 * 1024), "own/small.bin": blob("small own file", 2048),
                "own/mid.bin": blob("mid own file", 30 * 1024)}
        c = copy_of(tmp, "huge", main_files, huge)
        row = judged(c)
        ok(row["verdict"] == "ARCHIVE" and row["dirty"] == ["own/small.bin", "own/mid.bin"], f"smallest first up to the cap ({row['dirty']})")
        ok(row.get("dropped") == ["own/huge.bin"] and any("own/huge.bin" in w and "unkept" in w for w in row["why"]), "what did not fit is named in the row")
        s.act(row, ctx, failures)
        got = archive_of(row)
        ok(row["verdict"] == "DELETED" and not c.exists(), "an over-cap remainder no longer pins it")
        ok(got["manifest"]["dropped_paths"] == ["own/huge.bin"], "the manifest lists what went unkept")

        # a remainder with only one file, itself over the cap, and no commit of its own: nothing to archive, no refusal
        c = t / "tmp" / "solo"
        git(t, "clone", "-q", str(t / "mirror.git"), str(c))
        (c / "own").mkdir()
        (c / "own" / "huge.bin").write_bytes(huge["own/huge.bin"])
        row = judged(c)
        ok(row["verdict"] == "DELETE" and row.get("dropped") == ["own/huge.bin"], f"nothing preservable is a plain delete, not 'nothing to preserve' ({row['verdict']}: {row['why'][:2]})")
        s.act(row, ctx, failures)
        ok(row["verdict"] == "DELETED" and not c.exists(), "and it goes")

        # a copy of main's clone with main's tree copied in beside it: nothing of its own at all
        c = t / "tmp" / "plain"
        git(t, "clone", "-q", str(t / "mirror.git"), str(c))
        for i, d in enumerate(main_files.values()):
            (c / f"dup{i}").write_bytes(d)
        row = judged(c)
        ok(row["verdict"] == "DELETE" and row["why"] and not row.get("dirty"), f"a clone with nothing of its own is plainly deleted ({row['verdict']})")
        s.act(row, ctx, failures)
        ok(row["verdict"] == "DELETED" and not c.exists() and not failures, f"and it goes ({failures})")

        # the refusal stands: outside /tmp the cap still protects something
        c = copy_of(other, "outside", main_files)
        row = judged(c)
        ok(row["verdict"] == "REFUSE" and any("preserve cap" in w for w in row["why"]), f"outside /tmp the cap still refuses ({row['verdict']})")

        # tracked changes over the cap: a patch of them is not ours to cut
        c = copy_of(tmp, "tracked", {"big.bin": blob("tracked big", CAP * 2)})
        git(c, "add", "big.bin")
        git(c, "commit", "-q", "-m", "big")
        (c / "big.bin").write_bytes(blob("tracked big edited", CAP * 2))
        row = judged(c)
        ok(row["verdict"] == "REFUSE" and any("preserve cap" in w for w in row["why"]), f"tracked changes over the cap still refuse ({row['verdict']})")

        # no mirror to vouch: nothing is proved, so nothing is dropped
        c = copy_of(tmp, "nomirror", main_files)
        os.environ["SCRATCH_REAP_MIRRORS"] = str(t / "no-such.git")
        s._PROVED = None
        row = judged(c)
        ok(row["verdict"] == "REFUSE" and any("preserve cap" in w for w in row["why"]), f"no readable mirror keeps the refusal ({row['verdict']})")
        os.environ["SCRATCH_REAP_MIRRORS"] = str(t / "mirror.git")
        s._PROVED = None

        # young: the day's idle line still comes first
        os.environ["SCRATCH_REAP_TTL_HOURS"] = "24"
        row = judged(copy_of(tmp, "young", main_files))
        ok(row["verdict"] == "YOUNG", f"a copy touched today is not judged ({row['verdict']})")
        os.environ["SCRATCH_REAP_TTL_HOURS"] = "0"

        # the cleaner's own items report a directory; they do not use it
        now = time.time()
        for item, holds in (("TMPREAP_PRUNE_OVERCAP_COPY_STUCK_40_HOURS", False), ("TMP_SCRATCH_PRUNE_SIXTEEN_GIGS_NOBODY_CLAIMS", False),
                            ("CREEP_WEB_HARVEST_LIVE_1", True)):
            line = json.dumps({"seat": "BENCH", "event": "file", "id": item, "ts": stamp, "spec": "/tmp/jpre (2.2 GB)"})
            ok(s.mention_blocks("BENCH.jsonl", line, now) is holds, f"a fresh ledger mention by {item} {'pins' if holds else 'does not pin'}")

    print(f"{len(FAILS)} failed")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
