#!/usr/bin/env python3
"""Exhaustive truth table for art_guard._authorized on a mechanical live event with no ruling.

Pins the behaviour of the mechanical branch over every combination of (sha is None, said, prev, protected,
held_elsewhere), and proves the former second refusal ("retired an owner-kept picture without his words") was
unreachable: its condition implies the first refusal's, so the first always returned before it."""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import art_guard as G  # noqa: E402

L = G.L
FAILS = []


class Idx:
    rulings = []

    def __init__(self, protected):
        self._p = protected

    def protected(self, sha):
        return self._p


def oracle(sha_none, said, prev, protected, held):
    """What the mechanical branch must return."""
    if sha_none and said:
        return None  # an earlier branch: a retire on the owner's typed words
    if prev and protected and not (sha_none and held):
        return "mechanical install"
    return None


n = 0
orig = L.held_elsewhere
try:
    for sha_none, said, prev, protected, held in itertools.product([True, False], repeat=5):
        L.held_elsewhere = lambda idx, p, key, _h=held: _h
        ev = {"reason": "artpipe-collect", "ts": "2026-01-01T00:00:00-0700", "mod": "M", "rel": "r",
              "sha": None if sha_none else "a" * 40, "said": "owner words" if said else None,
              "prev": "b" * 40 if prev else None}
        got = G._authorized(ev, Idx(protected))
        want = oracle(sha_none, said, prev, protected, held)
        n += 1
        ok = (got is None) == (want is None) and (got is None or got.startswith("mechanical install"))
        if not ok or (got and "without his words" in got):
            FAILS.append((sha_none, said, prev, protected, held, got))
finally:
    L.held_elsewhere = orig
print("%d combination(s), %d failure(s)" % (n, len(FAILS)))
for f in FAILS:
    print("FAIL", f)
sys.exit(1 if FAILS else 0)
