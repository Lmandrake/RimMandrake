#!/usr/bin/env python3
"""Acceptance for plan.md step 5: the follow-through audit's sample and its two rates. The reading of each sampled
need is a fresh reader's judgement and has no test here; this script tests the program around it.

Contract: a new module src/RimMandrake/Utils/follow_through.py
  sample(streams, n, seed) -> {stream: list or None}
      streams = {name: list of needs, or None when the stream could not be read}; n needs from each stream (all of
      them when it has fewer), the same needs for the same seed, a different draw for another seed; None stays None.
  rates(judged) -> {"by_stream": {name: float or None}, "headline": float or None, "unmeasured": [name]}
      judged = {name: list of verdicts, or None}; a verdict is "outcome", "disposed" or "moved". "outcome" (the need
      reached its result) and "disposed" (dropped for a stated reason) count as followed through. "moved" (a new
      note, a follow-on item, a new date) does not. A stream with no verdicts, or None, has rate None and is named in
      "unmeasured". The headline is the LOWER rate, and it is None while any stream is unmeasured.
  hands_off(items) -> {"share": float or None, "closed": int, "hands_off": int}
      the Conductor's share, read the other way round: of the list items closed in the week, the share that passed
      every stage with no act by the Conductor window. items = list of {"closed": bool, "window_acts": int or None};
      an open item is not counted; an item whose acts could not be read (None) makes the share None, never a guess;
      no closed item is None, never 0.
Expected: PASS 15/15. Seen FAIL 0/15 on c0b85fb125 (follow_through.py absent), PASS 15/15 on the build."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _harness as H  # noqa: E402

FT, why = H.load("follow_through")
TALK = ["t%d" % i for i in range(50)]
PIPE = ["p%d" % i for i in range(7)]


def ft():
    if FT is None:
        raise RuntimeError(why)
    return FT


H.check("n needs from a stream that has more", lambda: len(ft().sample({"talk": TALK}, 20, 1)["talk"]) == 20)
H.check("the whole stream when it has fewer than n", lambda: sorted(ft().sample({"pipe": PIPE}, 20, 1)["pipe"]) == sorted(PIPE))
H.check("no need is drawn twice", lambda: len(set(ft().sample({"talk": TALK}, 20, 1)["talk"])) == 20)
H.check("the same seed gives the same draw", lambda: ft().sample({"talk": TALK}, 20, 7) == ft().sample({"talk": TALK}, 20, 7))
H.check("another seed gives another draw", lambda: ft().sample({"talk": TALK}, 20, 7) != ft().sample({"talk": TALK}, 20, 8))
H.check("a stream that could not be read stays None, never an empty list",
        lambda: ft().sample({"talk": None, "pipe": PIPE}, 20, 1)["talk"] is None)
H.check("outcome and disposed count; moved does not",
        lambda: ft().rates({"talk": ["outcome", "disposed", "moved", "moved"]})["by_stream"]["talk"] == 0.5)
H.check("the headline is the lower of the two rates",
        lambda: ft().rates({"talk": ["outcome", "moved", "moved", "moved"], "pipe": ["outcome"] * 4})["headline"] == 0.25)
H.check("a stream with no verdicts has rate None, never 0",
        lambda: (lambda r: r["by_stream"]["talk"] is None and r["unmeasured"] == ["talk"])(ft().rates({"talk": [], "pipe": ["outcome"]})))
H.check("the headline is None while a stream is unmeasured",
        lambda: ft().rates({"talk": None, "pipe": ["outcome"]})["headline"] is None)
H.check("all needs followed through is 1.0", lambda: ft().rates({"talk": ["outcome"], "pipe": ["disposed"]})["headline"] == 1.0)
H.check("the share of closed items with no Conductor act",
        lambda: ft().hands_off([{"closed": True, "window_acts": 0}, {"closed": True, "window_acts": 2},
                                {"closed": True, "window_acts": 0}, {"closed": True, "window_acts": 1}]) ==
        {"share": 0.5, "closed": 4, "hands_off": 2})
H.check("an open item is not counted",
        lambda: ft().hands_off([{"closed": True, "window_acts": 0}, {"closed": False, "window_acts": 0}])["closed"] == 1)
H.check("no closed item is None, never 0", lambda: ft().hands_off([{"closed": False, "window_acts": 0}])["share"] is None)
H.check("an item whose acts could not be read makes the share None",
        lambda: ft().hands_off([{"closed": True, "window_acts": 0}, {"closed": True, "window_acts": None}])["share"] is None)
H.done(15)
