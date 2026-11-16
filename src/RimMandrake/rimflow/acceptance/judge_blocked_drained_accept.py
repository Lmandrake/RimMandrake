#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_DRAIN_ITEMS_WAITING_ON_A_JUDGE_THAT_RETIRED.

Relentless was retired 2026-11-13 (design/RimMandrake/retired_loops_2026-11-13.md), and with it the only program that
ran its binding-repair judge. Every open item still blocked with kind `judge` by a Relentless snag waits on nothing
that will ever come. Measured 2026-11-15 17:55 PST: 46 such items, 43 of them `binding_repair`, most saying their work
already landed.

Passes when no open item is blocked with kind `judge` on a reason naming Relentless: each was closed on its landed sha
(with a level-tagged pass on that sha), reopened to ready with its proof rewritten, or dropped with a probe.

    python3 src/RimMandrake/rimflow/acceptance/judge_blocked_drained_accept.py     exit 0 = pass, 1 = fail

Expected on a correct result: `PASS 0 open items wait on the retired judge`. Watched failing on the base 464c69ccf0
(46 listed). The builder does not edit this file.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import model  # noqa: E402


def stuck(world):
    return sorted(i.id for i in world.items.values()
                  if i.open and i.blocked and i.blocked_kind == "judge"
                  and "relentless" in (i.blocked_reason or "").lower())


def main():
    left = stuck(model.replay(model.read()))
    if left:
        print("FAIL %d open items wait on the retired judge:" % len(left))
        for i in left:
            print("  " + i)
        return 1
    print("PASS 0 open items wait on the retired judge")
    return 0


if __name__ == "__main__":
    sys.exit(main())
