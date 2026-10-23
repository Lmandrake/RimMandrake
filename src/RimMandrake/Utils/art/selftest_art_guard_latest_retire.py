#!/usr/bin/env python3
"""selftest_art_guard_latest_retire.py — the art guard judges a deletion by the LATEST ledger event that explains it: an older,
since-restored retire of the same bytes with no authority must not shadow a later retire made on the owner's words
(GREENTIDE ants, 2026-10-22)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art_guard  # noqa: E402

FAILS = []
SX = "a" * 64
PATH = "src/RimUtinni/Zz/Textures/a/b.png"


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def ev(i, ts, sha, prev, reason, **k):
    return {"id": i, "type": "live", "mod": "src/RimUtinni/Zz", "rel": "a/b.png", "sha": sha, "prev": prev,
            "reason": reason, "ts": ts, **k}


def main():
    chain = [ev("1", "2026-10-22T18:00:00", SX, None, "backfill-observed"),
             ev("2", "2026-10-22T18:10:00", None, SX, "no-such-authority"),
             ev("3", "2026-10-22T18:20:00", SX, None, "backfill-observed"),
             ev("4", "2026-10-22T19:00:00", None, SX, "retire", said="his card words")]
    check(art_guard.check([(PATH, SX, None)], chain) == [], "a later retire on his words explains the deletion")
    check(art_guard.check([(PATH, SX, None)], chain[:3]) != [], "no event carrying his words: the deletion is refused")
    # the reverse must hold too: an OLD retire on his words never covers a LATER unauthorised retire of the same bytes
    rev = [ev("1", "2026-10-22T18:00:00", SX, None, "backfill-observed"),
           ev("2", "2026-10-22T18:10:00", None, SX, "retire", said="his card words"),
           ev("3", "2026-10-22T18:20:00", SX, None, "backfill-observed"),
           ev("4", "2026-10-22T19:00:00", None, SX, "no-such-authority")]
    check(art_guard.check([(PATH, SX, None)], rev) != [], "an older authorised retire does not shadow a later unauthorised one")
    print("ALL PASS" if not FAILS else f"{len(FAILS)} FAIL")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
