#!/usr/bin/env python3
"""selftest_owner_objections.py -- owner_objections.py reproduces the Crystallize 2026-W47 baseline.

    python3 src/RimMandrake/Utils/selftest_owner_objections.py [<expected arbitrary_limit blocks>]

The baseline of §No limit without the danger it guards (`design/RimMandrake/standing_rulings.md`): 8 `arbitrary_limit`
blocks for 2026-11-05..2026-11-19, read from the records as committed at PIN (records keep arriving for 2026-11-19, so
the live folder is not a fixed input). Pass another expected value to watch it go red. A pin this clone cannot read
(shallow or stale clone) exits 2: could not look, not a failure of the counter.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import owner_objections as O  # noqa: E402

PIN = "338b3cae50"     # origin/main when the baseline was adopted (2026-11-19)
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "conversations"))


def main():
    expected = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    try:
        recs = O.records_at_rev(ROOT, PIN, "2026-11-05", "2026-11-19")
    except OSError as e:
        print("COULD NOT LOOK: %s" % e)
        return 2
    n, hits = O.count(recs, "2026-11-05", "2026-11-19")
    got = len(hits["arbitrary_limit"])
    ok = got == expected and n > 0
    print(("PASS " if ok else "FAIL ") + "arbitrary_limit blocks 2026-11-05..19 at %s: %d, expected %d (%d typed blocks, %d records)"
          % (PIN, got, expected, n, len(recs)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
