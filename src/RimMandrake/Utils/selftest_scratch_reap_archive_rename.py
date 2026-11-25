#!/usr/bin/env python3
"""Selftest: an archive's last rename survives a short Windows refusal (OPS_SCRATCH_DIRT_MEASURE_AT_END_YOGQ).

On Archmagi the archive root is on /mnt/d (drvfs). Windows refuses a directory rename for a moment after files are written
into it (a scanner or indexer holds a handle): 2026-11-19, 2026-11-25 05:47Z and 18:39Z each ended a reap with
"Permission denied: .../scratch_expiry/.incoming-XXXX -> ...", left an .incoming- dir behind, and rang SCRATCH_DIRTY_END.
The case: os.rename refuses with EACCES twice, then works. preserve() must return the final dir, holding the manifest,
and leave no .incoming- dir. A rename that keeps refusing must still fail loud, with the .incoming- dir removed.
"""
import errno
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scratch_reap as R  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def row_for(p: Path) -> dict:
    return {"path": str(p), "kind": "dir", "bytes": 5, "age_h": 30, "why": ["selftest residue"]}


def with_refusals(n, fn):
    """Run fn with os.rename refusing EACCES on its first n calls into an .incoming- source."""
    real = os.rename
    calls = {"n": 0}

    def fake(src, dst, *a, **k):
        if ".incoming-" in os.path.basename(str(src)) and calls["n"] < n:
            calls["n"] += 1
            raise PermissionError(errno.EACCES, "Permission denied", str(src))
        return real(src, dst, *a, **k)

    os.rename = fake
    saved_sleep = R.time.sleep
    R.time.sleep = lambda s: None           # the retry's wait is not under test
    try:
        return fn(), calls["n"]
    finally:
        os.rename = real
        R.time.sleep = saved_sleep


def incoming(archive: Path) -> list:
    return [p for p in archive.rglob(".incoming-*")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="selftest_reap_rename_") as td:
        td = Path(td)
        archive = td / "archive"
        archive.mkdir()
        os.environ.update(LEFTOVERS_ARCHIVE_ROOT=str(archive), SCRATCH_REAP_STATE=str(td / "state"))
        src = td / "src" / "left_dir"
        src.mkdir(parents=True)
        (src / "a.txt").write_text("hello")

        try:
            (dest, n) = with_refusals(2, lambda: R.preserve(row_for(src)))
        except Exception as e:     # the instance: one refusal ends the archive
            dest, n = None, -1
            check(False, "two short refusals of the rename do not end the archive (raised %s: %s)" % (type(e).__name__, e))
        if dest:
            check(n == 2, "the rename was refused twice, then retried (refusals seen %d)" % n)
            check(Path(dest).is_dir() and (Path(dest) / "manifest.json").is_file(), "the final archive dir holds its manifest")
        check(not incoming(archive), "no .incoming- dir is left behind after a retried rename (%d left)" % len(incoming(archive)))

        for p in incoming(archive):
            R.shutil.rmtree(p)
        try:
            with_refusals(10 ** 6, lambda: R.preserve(row_for(src)))
            check(False, "a rename that never works fails loud")
        except OSError:
            check(True, "a rename that never works fails loud")
        check(not incoming(archive), "a failed archive removes its .incoming- dir (%d left)" % len(incoming(archive)))
    print("selftest_scratch_reap_archive_rename: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
