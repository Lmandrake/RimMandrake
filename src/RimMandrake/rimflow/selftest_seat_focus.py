#!/usr/bin/env python3
"""selftest_seat_focus.py - the schedule's `seat_focus` limits what `next` offers a seat (SEAT_FOCUS_FILTER_FOR_NEXT).

    python3 src/RimMandrake/rimflow/selftest_seat_focus.py

Owner 2026-10-30: FOUNDRY does trial prep only. A game-dev item is not offered (so the Dispatcher's peek finds
no work and does not ring); an in-focus one is; a seat not listed is unfiltered; with none the output says
"no in-focus work"; the live schedule carries the key (delete it on trial day 1).
"""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rimflow import cli, model  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


class Args(object):
    target = "v1"


def ev(**kw):
    kw.setdefault("ts", "2026-10-29T00:00:00Z")
    return kw


def world(ids):
    evs = []
    for i in ids:
        evs.append(ev(seat="BENCH", event="file", id=i, title="t", kind="task", **{"for": "FOUNDRY"}))
        evs.append(ev(seat="FOUNDRY", event="claim", id=i, ts="2026-10-29T01:00:00Z"))
    return model.replay(evs, strict=True)


def main():
    d = tempfile.mkdtemp()
    sched = os.path.join(d, "s.json")
    json.dump({"seat_focus": {"FOUNDRY": {"until": "trial_day1", "include_prefixes": ["ARENA_", "RALPH"]}}},
              open(sched, "w"))
    fo = cli._seat_focus("FOUNDRY", sched)
    check(fo and fo["prefixes"] == ("ARENA_", "RALPH"), "focus read for FOUNDRY")
    check(cli._seat_focus("BENCH", sched) is None, "an unlisted seat is unfiltered")
    check(cli._seat_focus("FOUNDRY", os.path.join(d, "missing.json")) is None, "unreadable schedule = no filter")
    live = cli._seat_focus("FOUNDRY")
    check(live is not None and "ARENA_" in live["prefixes"], "the live schedule carries FOUNDRY's focus")

    game = ["EXPLOSIVE_GROWTH_RETHINK_SERIOUS_CONCERNS", "SPRINKLER_HEADS_BUILD_PUMP_REQUIRED"]
    ctx = {"now": model.epoch_now(), "focus": fo}
    w = world(game)
    ch = cli._choose(w, "FOUNDRY", Args(), ctx, None)
    check(ch["kind"] == "nothing", "only game-dev items: nothing offered (%s)" % ch["kind"])
    out = io.StringIO()
    with redirect_stdout(out):
        cli._nothing(w, "FOUNDRY", Args(), ctx)
    check("no in-focus work" in out.getvalue(), "the empty answer says 'no in-focus work'")
    w = world(game + ["ARENA_RACE_X", "OTHER_THING"])
    ch = cli._choose(w, "FOUNDRY", Args(), ctx, None)
    check(ch["item"] is not None and ch["item"].id == "ARENA_RACE_X", "an ARENA_ item is offered over game dev")
    ch = cli._choose(world(game), "FOUNDRY", Args(), {"now": ctx["now"]}, None)
    check(ch["item"] is not None, "control: without focus a game-dev item IS offered")

    # the bar ends by itself: `until_item` implemented lifts it, nothing else does
    gated = os.path.join(d, "g.json")
    json.dump({"seat_focus": {"FOUNDRY": {"until_item": "DAY_ZERO_GATE", "include_prefixes": ["ARENA_"]}}},
              open(gated, "w"))
    class It:
        def __init__(self, state):
            self.state = state
    class Wd:
        def __init__(self, state=None):
            self.items = {"DAY_ZERO_GATE": It(state)} if state else {}
    check(cli._seat_focus("FOUNDRY", gated) is not None, "no world given: the bar holds")
    check(cli._seat_focus("FOUNDRY", gated, Wd()) is not None, "gate item not filed: the bar holds")
    for state, barred in (("proposed", True), ("doing", True), ("dropped", True), ("built", False),
                          ("validated", False), ("done", False)):
        check((cli._seat_focus("FOUNDRY", gated, Wd(state)) is not None) == barred,
              "gate item %s: barred=%s" % (state, barred))
    check(cli._seat_focus("FOUNDRY", sched, Wd("done")) is not None, "an entry with no until_item never self-lifts")
    gate = json.load(open(cli.os.path.join(os.path.dirname(os.path.abspath(cli.__file__)), "dispatcher_schedule.json")))
    gate = gate["seat_focus"]["FOUNDRY"].get("until_item")
    _, real = cli.load()
    check(gate in real.items, "the live until_item is filed in the ledger: %s" % gate)

    print("%d FAIL" % len(FAILS) if FAILS else "ALL OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
