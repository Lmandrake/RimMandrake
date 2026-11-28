#!/usr/bin/env python3
"""selftest_scratch_reap_lock_wait.py — a dry run held by hand never costs the hourly apply run its slot
(LIVE_RESTORE_RM_SCRATCH_REAP).

The failure (Archmagi, 2026-11-27): a helper ran two dry runs of scratch_reap.py by hand, 6:47 to 6:54 PM and 6:59 to
7:05 PM PST. The 7:03 PM timer run of rm-scratch-reap.service found run.lock held, printed "another reaper run holds the
lock" and exited 0. A dry run writes no last_run.json, so the reading aged from the 6:24 PM run until the 8:00 PM run
ended, past the 2 h line of three live promises.

Proves, each against the real scratch_reap.py in an isolated state dir:
(1) an apply run that finds a dry run holding the lock waits, and runs and writes last_run.json when the dry run ends;
(2) an apply run that finds another apply run holding the lock stands down at once and writes nothing;
(3) a dry run that finds any run holding the lock stands down at once;
(4) a holder that names no mode (an older reaper, or the moment before the holder writes its name) is read as an apply
    run: the contender stands down, as before;
(5) the holder names its mode and pid in run.lock, a contender's open does not erase that name, and the name is gone
    when the holder ends.
Page: design/specs/2026-11-27-reap-apply-waits-out-dry-run/boundary.md (each check names its promise)."""
import fcntl
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
F = []
QUICK_S = 120       # hang guard only: an empty-fixture run takes about 2 s; a stand-down takes under 1 s


def ck(c, w):
    print(("PASS " if c else "FAIL ") + w)
    if not c:
        F.append(w)


def fixture(t: Path) -> dict:
    for d in ("roots", "corpus", "state", "mirrors", "transcripts", "archive", "tmp"):
        (t / d).mkdir(exist_ok=True)
    return dict(os.environ, SCRATCH_REAP_ROOTS=str(t / "roots"), SCRATCH_REAP_SCAN=str(t / "roots"),
                SCRATCH_REAP_CORPUS=str(t / "corpus"), SCRATCH_REAP_STATE=str(t / "state"),
                SCRATCH_REAP_MIRRORS=str(t / "mirrors"), SCRATCH_REAP_TRANSCRIPTS=str(t / "transcripts"),
                SCRATCH_REAP_RM_SCRATCH="/nonexistent", SCRATCH_REAP_TMP=str(t / "tmp"),
                LEFTOVERS_ARCHIVE_ROOT=str(t / "archive"), SCRATCH_REAP_UNIT="rm-scratch-reap-selftest.service")


def reaper(env, *args):
    return subprocess.Popen([sys.executable, str(HERE / "scratch_reap.py"), *args], env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def hold(state: Path, name: str):
    """Take run.lock as another run would, and write `name` into it (an empty name: an unnamed holder)."""
    fd = os.open(state / "run.lock", os.O_RDWR | os.O_CREAT, 0o664)
    lk = os.fdopen(fd, "r+")
    fcntl.flock(lk, fcntl.LOCK_EX)
    lk.seek(0)
    lk.truncate()
    lk.write(name)
    lk.flush()
    return lk


def t_an_apply_run_waits_out_a_dry_run():
    with tempfile.TemporaryDirectory(prefix="selftest_reap_lockwait_") as td:
        t = Path(td)
        env = fixture(t)
        lk = hold(t / "state", "dry 4242\n")
        p = reaper(env, "--apply")
        time.sleep(3)
        waited = p.poll() is None and not (t / "state" / "last_run.json").exists()
        lk.close()
        try:
            out, _ = p.communicate(timeout=QUICK_S)
        except subprocess.TimeoutExpired:
            p.kill()
            out, _ = p.communicate()
        ck(waited, "an-apply-run-waits-out-a-dry-run: while a dry run holds the lock, the apply run waits "
                   "(rc %r, out %r)" % (p.returncode, out[-300:]))
        ck(p.returncode == 0 and (t / "state" / "last_run.json").exists(),
           "an-apply-run-waits-out-a-dry-run: when the dry run ends, the apply run runs and writes last_run.json "
           "(rc %r, out %r)" % (p.returncode, out[-300:]))


def stands_down(name: str, *args) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix="selftest_reap_lockwait_") as td:
        t = Path(td)
        env = fixture(t)
        lk = hold(t / "state", name)
        p = reaper(env, *args)
        try:
            out, _ = p.communicate(timeout=QUICK_S)
            ok = p.returncode == 0 and "holds the lock" in out and not (t / "state" / "last_run.json").exists() \
                and not (t / "state" / "last_dry_run.json").exists()
        except subprocess.TimeoutExpired:
            p.kill()
            out, _ = p.communicate()
            ok = False
        lk.close()
        return ok, out[-300:]


def t_an_apply_run_stands_down_for_an_apply_run():
    ok, out = stands_down("apply 4242\n", "--apply")
    ck(ok, "an-apply-run-stands-down-for-an-apply-run: it exits 0 at once and writes no record (%r)" % out)


def t_a_dry_run_stands_down_for_any_run():
    for name in ("apply 4242\n", "dry 4242\n"):
        ok, out = stands_down(name)
        ck(ok, "a-dry-run-stands-down-for-any-run: held by %r, the dry run exits 0 at once (%r)" % (name.strip(), out))


def t_an_unnamed_holder_reads_as_an_apply_run():
    ok, out = stands_down("", "--apply")
    ck(ok, "an-unnamed-holder-reads-as-an-apply-run: the apply run stands down, as before (%r)" % out)


def t_the_holder_names_itself_until_it_ends():
    sys.path.insert(0, str(HERE))
    with tempfile.TemporaryDirectory(prefix="selftest_reap_lockwait_") as td:
        t = Path(td)
        os.environ.update(fixture(t))
        import scratch_reap as R
        lk = R.take_lock(t / "state", apply=False)
        ck(lk is not None and (t / "state" / "run.lock").read_text() == "dry %d\n" % os.getpid(),
           "the-holder-names-itself-until-it-ends: a dry holder writes 'dry <pid>' (%r)"
           % (t / "state" / "run.lock").read_text())
        p = reaper(fixture(t))                 # a contender: it must stand down and leave the name in place
        p.communicate(timeout=QUICK_S)
        ck((t / "state" / "run.lock").read_text() == "dry %d\n" % os.getpid(),
           "the-holder-names-itself-until-it-ends: a contender's open leaves the holder's name in place")
        R.release_lock(lk)
        ck((t / "state" / "run.lock").read_text() == "",
           "the-holder-names-itself-until-it-ends: the name is gone when the holder ends")
        # the apply holder's name is what makes a second apply run stand down: one named "dry" would have it wait the
        # whole run (1.5-2.3 h) and then reap again
        lk = R.take_lock(t / "state", apply=True)
        named = (t / "state" / "run.lock").read_text()
        R.release_lock(lk)
        ck(lk is not None and named == "apply %d\n" % os.getpid(),
           "the-holder-names-itself-until-it-ends: an apply holder writes 'apply <pid>' (%r)" % named)


def main() -> int:
    t_an_apply_run_waits_out_a_dry_run()
    t_an_apply_run_stands_down_for_an_apply_run()
    t_a_dry_run_stands_down_for_any_run()
    t_an_unnamed_holder_reads_as_an_apply_run()
    try:
        t_the_holder_names_itself_until_it_ends()
    except AttributeError as e:             # the parent has no take_lock: a red, not a crash
        ck(False, "the-holder-names-itself-until-it-ends: scratch_reap has take_lock and release_lock (%s)" % e)
    print("%d FAIL" % len(F) if F else "ALL PASS")
    return 1 if F else 0


if __name__ == "__main__":
    sys.exit(main())
