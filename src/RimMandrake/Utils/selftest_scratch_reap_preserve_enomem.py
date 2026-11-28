#!/usr/bin/env python3
"""Selftest: an archive survives a short ENOMEM from drvfs, and a failed archive leaves no .incoming- dir
(OPS_SCRATCH_DIRT_MEASURE_AT_END_YOGQ; page design/specs/2026-11-28-reap-preserve-transient/boundary.md).

On Archmagi the archive root is on /mnt/d (drvfs). Under load drvfs answers ENOMEM for a moment and works a moment
later. The reap of 2026-11-28 04:00Z ended with one failure, "tmp1otmqzap: [Errno 12] Cannot allocate memory", which
rang SCRATCH_DIRTY_END and reopened this item; the next run archived the same dir at 07:12Z with no error. That failed
attempt also left `.incoming-6_xh5zj6` (a clone.bundle and a status.txt) in the archive, because preserve() removed
its .incoming- dir only when the final rename failed. Same refusal on 2026-11-02 (a 1.7 GB session dir).

Each case's name is a promise of the page. `--at <rev>` runs the cases against scratch_reap.py as it was at <rev>.
"""
import errno
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def load(at):
    if at:
        out = Path(tempfile.mkdtemp(prefix="selftest_reap_enomem_at_"))
        rel = "src/RimMandrake/Utils/"
        for name in ("scratch_reap.py",):
            body = subprocess.run(["git", "-C", str(HERE), "show", f"{at}:{rel}{name}"], capture_output=True, check=True).stdout
            (out / name).write_bytes(body)
        sys.path.insert(0, str(HERE))       # its sibling imports stay at HEAD
        sys.path.insert(0, str(out))
    else:
        sys.path.insert(0, str(HERE))
    import scratch_reap
    return scratch_reap


def row_for(p: Path) -> dict:
    return {"path": str(p), "kind": "dir", "bytes": 5, "age_h": 30, "why": ["selftest residue"]}


def with_enomem(R, n, fn):
    """Run fn with os.fsync answering ENOMEM on its first n calls, as drvfs does under load."""
    real = os.fsync
    calls = {"n": 0}

    def fake(fd):
        if calls["n"] < n:
            calls["n"] += 1
            raise OSError(errno.ENOMEM, "Cannot allocate memory")
        return real(fd)

    os.fsync = fake
    saved_sleep = R.time.sleep
    R.time.sleep = lambda s: None           # the retry's wait is not under test
    try:
        return fn(), calls["n"]
    finally:
        os.fsync = real
        R.time.sleep = saved_sleep


def incoming(archive: Path) -> list:
    return list(archive.rglob(".incoming-*"))


def finals(archive: Path) -> list:
    return [p for p in archive.rglob("*") if p.is_dir() and p.parent.name == "scratch_expiry"
            and not p.name.startswith(".incoming-")]


class Bed:
    """One archive root and one source dir, both under a temp dir."""

    def __init__(self, R, td: Path):
        self.R = R
        self.archive = td / "archive"
        self.archive.mkdir()
        os.environ.update(LEFTOVERS_ARCHIVE_ROOT=str(self.archive), SCRATCH_REAP_STATE=str(td / "state"))
        self.src = td / "src" / "left_dir"
        self.src.mkdir(parents=True)
        (self.src / "a.txt").write_text("hello")
        # the reap's own call, or preserve itself at a rev that has no retry
        self.fn = R.preserve_retrying if hasattr(R, "preserve_retrying") else R.preserve

    def clear(self):
        for p in incoming(self.archive) + finals(self.archive):
            self.R.shutil.rmtree(p)

    def no_incoming(self, after):
        n = len(incoming(self.archive))
        check(n == 0, "a-failed-attempt-leaves-no-incoming: none after %s (%d left)" % (after, n))


def t_a_short_enomem_is_retried(b: Bed):
    b.clear()
    try:
        dest, n = with_enomem(b.R, 1, lambda: b.fn(row_for(b.src)))
        check(n == 1 and Path(dest).is_dir() and (Path(dest) / "manifest.json").is_file(),
              "a-short-enomem-is-retried: one ENOMEM, then the archive lands with its manifest")
    except OSError as e:
        check(False, "a-short-enomem-is-retried: one ENOMEM ended the archive (%s)" % e)
    check(len(finals(b.archive)) <= 1, "a-short-enomem-is-retried: one archive dir, not two (%d)" % len(finals(b.archive)))
    b.no_incoming("a retried ENOMEM")


def t_a_lasting_enomem_fails_loud(b: Bed):
    b.clear()
    try:
        with_enomem(b.R, 10 ** 6, lambda: b.fn(row_for(b.src)))
        check(False, "a-lasting-enomem-fails-loud: an ENOMEM that never clears still raises")
    except OSError as e:
        check(e.errno == errno.ENOMEM, "a-lasting-enomem-fails-loud: an ENOMEM that never clears still raises")
    check(b.src.is_dir() and (b.src / "a.txt").read_text() == "hello", "a-lasting-enomem-fails-loud: the source stays")
    b.no_incoming("a lasting ENOMEM")


def t_another_error_is_not_retried(b: Bed):
    b.clear()
    real_fsync, calls = os.fsync, {"n": 0}

    def eio(fd):
        calls["n"] += 1
        raise OSError(errno.EIO, "Input/output error")
    os.fsync = eio
    try:
        b.fn(row_for(b.src))
        check(False, "another-error-is-not-retried: EIO raises")
    except OSError:
        check(calls["n"] == 1, "another-error-is-not-retried: EIO raises at once (fsync calls %d)" % calls["n"])
    finally:
        os.fsync = real_fsync
    b.no_incoming("EIO")


def t_a_failed_attempt_leaves_no_incoming(b: Bed):
    """A copy that fails part way (the first fsync of a file in .incoming-) and is not retried."""
    b.clear()
    try:
        with_enomem(b.R, 10 ** 6, lambda: b.R.preserve(row_for(b.src)))
    except OSError:
        pass
    b.no_incoming("a failed copy in preserve()")


def main(argv) -> int:
    at = argv[argv.index("--at") + 1] if "--at" in argv else None
    R = load(at)
    with tempfile.TemporaryDirectory(prefix="selftest_reap_enomem_") as td:
        b = Bed(R, Path(td))
        t_a_short_enomem_is_retried(b)
        t_a_lasting_enomem_fails_loud(b)
        t_another_error_is_not_retried(b)
        t_a_failed_attempt_leaves_no_incoming(b)
    print("selftest_scratch_reap_preserve_enomem: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
