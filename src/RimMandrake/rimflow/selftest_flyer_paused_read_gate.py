#!/usr/bin/env python3
"""selftest_flyer_paused_read_gate.py -- the delegated bridge take admits a PAUSED flyer state read, and nothing else
that names flight (RIMMANDRAKE_ADMIT_PAUSED_FLYER_READS_AT_BRIDGE_TAKE).

His card (2026-11-13, on RIMMANDRAKE_ADMIT_PAUSED_FLYER_READS_AT_BRIDGE_TAKE): "Flyer flight state read with the game
paused, without him -> Yes, paused reads allowed (no ticks, no pictures; anything moving still waits for him)".
src/RimMandrake/Utils/art/flyer_tier_three_state_read.py refuses unless the game is paused and still, so a purpose
naming that read is admitted; every other flight wording, and --flyer, still refuses.

    python3 src/RimMandrake/rimflow/selftest_flyer_paused_read_gate.py      exit 0: every check passes
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cli  # noqa: E402

FAILS = []
READ = "paused flyer state read (flyer_tier_three_state_read.py)"


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def refused(purpose, flyer=False):
    return cli._delegated_gate(None, "BENCH", False, purpose, flyer)[1] is not None


def main():
    check(not refused(READ), "the ticket's acceptance: a paused flyer state read takes a free bridge")
    check(not refused("Paused Flyer State Read (flyer_tier_three_state_read.py) on RSW_Mynock"),
          "the read is admitted in any case, with the subject after it")
    check(refused("flyer flight test"), "a flyer flight test still refuses")
    check(refused(READ, flyer=True), "--flyer still refuses, whatever the purpose says")
    for bad in ("paused flyer state read", "flyer_tier_three_state_read.py", "paused flyer state read "
                "(flyer_tier_three_state_read.py), then unpause and watch it fly",
                "paused flyer state read (flyer_tier_three_state_read.py) and a takeoff picture",
                "unpaused flyer state read (flyer_tier_three_state_read.py)", "paused flight read",
                "glide test", "butterfly airborne check"):
        check(refused(bad), "still refused: %r" % bad)
    check(not refused("FlowWorks pump stage"), "a purpose naming no flight is unchanged (FlowWorks is no flight)")
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
