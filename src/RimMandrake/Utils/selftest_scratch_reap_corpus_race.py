#!/usr/bin/env python3
"""Selftest: a corpus file that moves or vanishes between its listing and its read does not kill the reap
(OPS_SCRATCH_DIRT_MEASURE_AT_END_YOGQ).

The instance (Archmagi, 2026-11-25T20:51Z): the run died "ledger corpus unreadable:
~/.config/systemd/user/rm-probe-r4dropin371142-.service.d/50-rm-control-permit.conf: No such file or directory" - a probe
unit's drop-in, listed, then removed by its owner before the read. An item closed mid-read moves from items/ to
items/closed/ the same way. The corpus is safety evidence, so a moved file's text must still be read: corpus() lists
again and reads the fresh listing. A file that cannot be read for any other reason still stops the run.
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


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="selftest_reap_corpus_") as td:
        root = Path(td) / "clone"
        st = root / "infrastructure" / "state"
        for d in (st / "ledger" / "events", st / "items" / "closed", st / "handoffs"):
            d.mkdir(parents=True)
        (st / "ledger" / "events" / "BENCH.jsonl").write_text('{"id": "X"}\n')
        item = st / "items" / "ITEM_NAMES_CLONE.md"
        item.write_text("keeps /home/mandrake/rm/scratch/BENCH/precious\n")
        os.environ["SCRATCH_REAP_CORPUS"] = str(root)
        real_open = open
        moved = {"n": 0}

        def racing_open(f, *a, **k):        # the item is closed (moved) after its listing, before its read
            if str(f) == str(item) and not moved["n"]:
                moved["n"] = 1
                os.rename(item, st / "items" / "closed" / item.name)
                raise FileNotFoundError(errno.ENOENT, "No such file or directory", str(f))
            return real_open(f, *a, **k)

        R.open = racing_open
        R._CORPUS = None
        try:
            texts = R.corpus()
            check(any("precious" in t for _, t in texts), "the moved item's text is still in the corpus")
        except RuntimeError as e:
            check(False, "a file moved between listing and read does not kill the run (raised: %s)" % e)
        finally:
            del R.open
        R._CORPUS = None

        def broken_open(f, *a, **k):
            if str(f).endswith("BENCH.jsonl"):
                raise PermissionError(errno.EACCES, "Permission denied", str(f))
            return real_open(f, *a, **k)

        R.open = broken_open
        try:
            R.corpus()
            check(False, "an unreadable corpus file still stops the run")
        except RuntimeError as e:
            check("unreadable" in str(e), "an unreadable corpus file still stops the run (%s)" % e)
        finally:
            del R.open
            R._CORPUS = None
    print("selftest_scratch_reap_corpus_race: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
