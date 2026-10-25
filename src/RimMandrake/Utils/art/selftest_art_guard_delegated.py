#!/usr/bin/env python3
"""A delegated art install (`--why "delegated: art <verdict file>"`, reason 'agent-why') passes art_guard when the verdict
file exists in the clone and displaces no owner-kept picture (ART_GUARD_FIX_REFUSES_THE_DELEGATE)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art_guard as G  # noqa: E402

FILE = "src/RimMandrake/Utils/art/art_guard.py"       # a file that exists in every clone
FAILS = []


class Idx:
    rulings = []

    def __init__(self, protected):
        self._p = protected

    def protected(self, sha):
        return self._p


def ev(why, prev="b" * 40):
    return {"reason": "agent-why", "why": why, "ts": "2026-10-24T00:00:00-0700", "mod": "M", "rel": "r",
            "sha": "a" * 40, "prev": prev}


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


check(G._authorized(ev("delegated: art " + FILE), Idx(False)) is None, "delegated + existing verdict file + free slot: authorized")
check(G._authorized(ev("delegated: art " + FILE), Idx(True)) is not None, "delegated install may not displace an owner-kept picture")
check(G._authorized(ev("delegated: art infrastructure/nope.json"), Idx(False)) is not None, "missing verdict file: refused")
check(G._authorized(ev("delegated: art ../../etc/passwd"), Idx(False)) is not None, "verdict path outside the clone: refused")
check(G._authorized(ev("delegated: art"), Idx(False)) is not None, "no verdict named: refused")
check(G._authorized(ev("because I felt like it"), Idx(False)) is not None, "any other --why alone is still refused")
sys.exit(1 if FAILS else 0)
