#!/usr/bin/env python3
"""selftest_fixture_pit_prison_cleanup.py -- offline: fixture_pit_prison_cleanup.py passes every case on the worktree's
extensions.pit_prison_room (PITPRISON_CHAIN_FIX_LEFTOVERS_PICK_FIGHTS), and can FAIL: with the fake bridge's vanish calls
dropped, the abort and stray cases must report leftovers (the instrument sees)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import fixture_pit_prison_cleanup as F  # noqa: E402


def main():
    probs = []
    EXT = F.load_ext("WORKTREE")
    for name, fn in sorted(F.CASES.items()):
        got = fn(EXT)
        if got:
            probs.append("%s FAILs on the worktree: %s" % (name, got))
    for name in ("abort-mid-chain", "stray-hostiles", "clean"):
        if not F.CASES[name](EXT, drop_vanish=True):
            probs.append("sanity: %s passed with every vanish dropped (instrument blind)" % name)
    # regression sanity: the pre-fix shape (no finally-vanish; only the chain's own end-of-body cleanup) must FAIL the abort case
    real = EXT._vanish_own_fixtures
    EXT._vanish_own_fixtures = lambda t: []
    try:
        if not F.case_abort(EXT):
            probs.append("sanity: abort-mid-chain passed with the finally-vanish removed")
    finally:
        EXT._vanish_own_fixtures = real
    print("selftest_fixture_pit_prison_cleanup: %s" % ("PASS" if not probs else "FAIL"))
    for p in probs:
        print("  - " + p)
    return 0 if not probs else 1


if __name__ == "__main__":
    sys.exit(main())
