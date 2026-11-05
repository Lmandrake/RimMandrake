#!/usr/bin/env python3
# selftest-timeout: 120
"""Selftest for selftest_own_dirs.py (REAPER_FIX_OWN_SELFTEST_LITTERS_FAKE_SAVES): a reaper selftest killed mid-run
leaves no fake CANONICAL_*.rws clone behind for longer than the next run, and nothing that is not provably its own
is removed: a live run's dir, a dir that lost its marker, a real-sized save."""
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


CHILD = r"""
import os, sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from selftest_own_dirs import own_dir
with own_dir("t", dir=sys.argv[2]) as d:
    c = Path(d) / "scratch" / "FOUNDRY" / "tracked_canon_clone"
    (c / ".git").mkdir(parents=True)
    (c / "CANONICAL_Tracked.rws").write_text("save")
    locked = Path(d) / "denied"
    locked.mkdir()
    (locked / "x").write_text("x")
    os.chmod(locked, 0)
    print(d, flush=True)
    time.sleep(120)
"""


def child(base: Path) -> tuple[subprocess.Popen, Path]:
    p = subprocess.Popen([sys.executable, "-c", CHILD, str(HERE), str(base)], stdout=subprocess.PIPE, text=True)
    return p, Path(p.stdout.readline().strip())


def main() -> int:
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds)
        os.environ["SELFTEST_OWN_DIRS_REG"] = str(td / "reg")
        import selftest_own_dirs as O
        base = td / "tmp"
        base.mkdir()

        # SIGKILL: the run cannot clean; the next run's reap does, unreadable dir and all
        p, d = child(base)
        check(d.is_dir() and (d / "scratch/FOUNDRY/tracked_canon_clone/CANONICAL_Tracked.rws").exists(),
              "the child planted a fake canonical save in its own dir")
        live = O.reap("t")
        check(live == [] and d.exists(), "a live run's dir is never reaped")
        p.send_signal(signal.SIGKILL)
        p.wait()
        check(d.exists(), "SIGKILL strands the dir (the leak this item names)")
        gone = O.reap("t")
        check(gone == [str(d)] and not os.path.lexists(d), "the next run removes a killed run's dir, unreadable fixture included")
        check(not list((td / "reg" / "t").glob("*.json")), "and drops its registry entry")

        # SIGTERM (a runner's timeout): the run unwinds through its own cleanup
        p, d = child(base)
        p.send_signal(signal.SIGTERM)
        p.wait(timeout=30)
        check(not os.path.lexists(d), "SIGTERM removes the run's own dir")
        check(not list((td / "reg" / "t").glob("*.json")), "and its registry entry")

        # own_dir reaps on entry: a later run cleans before it plants
        p, d = child(base)
        p.send_signal(signal.SIGKILL)
        p.wait()
        p2, d2 = child(base)
        check(not os.path.lexists(d) and d2.is_dir(), "a new run removes the killed one's dir before planting its own")
        p2.send_signal(signal.SIGTERM)
        p2.wait(timeout=30)

        # a registry entry is not licence: the dir must hold the same identity
        real = base / "real_canon"
        real.mkdir()
        (real / "CANONICAL_Colony.rws").write_text("a real save")
        ent = td / "reg" / "t" / "real.json"
        ent.write_text(json.dumps({"pid": 999999999, "start": "1", "path": str(real), "tag": "t"}))
        O.reap("t")
        check(real.exists() and not ent.exists(), "a registered dir without our marker stays; only the entry goes")
        (real / O.MARK).write_text(json.dumps({"pid": 999999999, "start": "2", "path": str(real), "tag": "t"}))
        ent.write_text(json.dumps({"pid": 999999999, "start": "1", "path": str(real), "tag": "t"}))
        O.reap("t")
        check(real.exists(), "a marker naming another identity stays")
        me = {"pid": os.getpid(), "start": "not-my-start", "path": str(real), "tag": "t"}
        check(not O.alive(me) and O.alive({**me, "start": O.proc_start(os.getpid())}), "a reused pid is not the run we recorded")

        # legacy litter: the fixture's shape, small saves, old, unused
        root = td / "seat-tmp" / "BENCH"
        os.environ["SELFTEST_OWN_DIRS_LEGACY_ROOTS"] = str(root)
        old = time.time() - 3 * 86400

        def plant(path: Path, save="save", age=True):
            for n in ("origin.git/objects", "origin.git/refs", "archive", "live_elsewhere",
                      "scratch/FOUNDRY/tracked_canon_clone/.git"):
                (path / n).mkdir(parents=True, exist_ok=True)
            (path / "origin.git/HEAD").write_text("ref: refs/heads/main\n")
            if save is not None:
                (path / "scratch/FOUNDRY/tracked_canon_clone/CANONICAL_Tracked.rws").write_text(save)
            if age:
                for dp, dns, fns in os.walk(path):
                    for n in dns + fns:
                        os.utime(os.path.join(dp, n), (old, old))
                os.utime(path, (old, old))
            return path

        litter = plant(root / "tmpab3_x9zq")
        (litter / "denied").mkdir()
        (litter / "denied" / "CANONICAL_Dropped.rws").write_text("save")
        os.utime(litter / "denied" / "CANONICAL_Dropped.rws", (old, old))
        os.utime(litter / "denied", (old, old))
        os.chmod(litter / "denied", 0)
        os.utime(litter, (old, old))
        hidden = plant(root / "tmphid_x9zq")
        (hidden / "denied").mkdir()
        (hidden / "denied" / "CANONICAL_Colony.rws").write_text("x" * 4096)
        os.utime(hidden / "denied", (old, old))
        os.chmod(hidden / "denied", 0)
        os.utime(hidden, (old, old))
        run = root / "selftest_run_abcdefgh"
        inner = plant(run / "tmpzz3_x9zq")
        (run / "selftest_scratch_reap.lock").write_text("")
        big = plant(root / "tmpbig_x9zq", save="x" * 4096)
        young = plant(root / "tmpyng_x9zq", age=False)
        other = root / "tmpoth_x9zq"
        (other / "work").mkdir(parents=True)
        (other / "CANONICAL_Colony.rws").write_text("save")
        busy = plant(root / "tmpbsy_x9zq")
        sl = subprocess.Popen(["sleep", "60"], cwd=busy / "archive")
        nosave = plant(root / "tmpnos_x9zq", save=None)                 # the shape, but no fake save: not this litter
        files = root / "tmpfil_x9zq"                                    # the names, as plain files: real work, not a fixture
        files.mkdir()
        for n in ("origin.git", "archive", "live_elsewhere"):
            (files / n).write_text("work")
        (files / "CANONICAL_Tracked.rws").write_text("save")
        for n in [*files.iterdir(), files]:
            os.utime(n, (old, old))
        moved = plant(root / "tmpmov_x9zq")
        os.utime(moved, None)                                           # an old tree moved in just now: young by its dir
        runb = root / "selftest_run_busyrunr"
        inb = plant(runb / "tmpinb_x9zq")
        sl2 = subprocess.Popen(["sleep", "60"], cwd=runb)               # a live runner sits in the parent, not the fixture
        try:
            r = O.legacy_litter(apply=False)
            v = {Path(x["path"]).name: x["verdict"] for x in r["rows"]}
            check(v.get("tmpzz3_x9zq") == "LITTER", "the fixture's shape is litter, inside a runner's dir too")
            check(v.get("tmpab3_x9zq") == "KEEP" and (litter / "denied").stat().st_mode & 0o777 == 0,
                  "report mode leaves an unreadable fixture shut and unjudged")
            check("tmpnos_x9zq" not in v and "tmpfil_x9zq" not in v, "the shape without a fake save, or as plain files, is not litter")
            check(v.get("tmpmov_x9zq") == "KEEP", "an old tree moved into a fresh dir is young")
            check(v.get("tmpinb_x9zq") == "KEEP", "a fixture whose runner dir a live process uses stays")
            check(v.get("tmphid_x9zq") == "KEEP", "a real-sized save behind an unreadable dir is seen and kept")
            check(v.get("tmpbig_x9zq") == "KEEP" and v.get("tmpyng_x9zq") == "KEEP" and v.get("tmpbsy_x9zq") == "KEEP",
                  "a real-sized save, a young dir and a dir a process uses stay")
            check("tmpoth_x9zq" not in v, "a dir not shaped like the fixture is not even a candidate")
            check(litter.exists() and inner.exists(), "report only touches nothing")
            O.legacy_litter(apply=True)
            check(not litter.exists() and not run.exists(), "--apply removes the litter (unreadable fixture dir too) and the emptied runner dir")
            check(big.exists() and young.exists() and busy.exists() and other.exists() and hidden.exists()
                  and nosave.exists() and files.exists() and moved.exists() and inb.exists() and runb.exists(), "and nothing else")
        finally:
            for x in (sl, sl2):
                x.kill()
                x.wait()
    print(f"selftest_scratch_reap_litter: {'FAIL' if FAILS else 'PASS'}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
