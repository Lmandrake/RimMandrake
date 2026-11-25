#!/usr/bin/env python3
"""scene_flight_takeoff_and_flap - the flapping-bird scene (worked example 3 of
design/specs/2026-11-23-bridge-v2/02_needs_design.md), on the scene library. State only: no picture is made.

🔴 THE OWNER'S ACT. A live flight test of a flyer runs only with him present (CLAUDE.md §Only five acts stay his, act 1;
07_for_the_owner.md choice 1). This script refuses to start without `--with-owner "<his words that he is present>"`.
No helper, seat or tick runs it. Status at filing: UNRUN.

    python.exe src/RimMandrake/bridgetools/scene_flight_takeoff_and_flap.py <game> <KindDefName> --with-owner "<his words>"
        [--map <save>] [--limit 2500]

What it does: opens the game on the library, finds the wild birds of that kind on the map (jawa/pawn_flight report; at
most 16), records each bird's flight and selected flip-book frame on every tick (scene_cond.flight) while the game plays
on its own (natural job starts: the takeoff chance is the game's), and judges the kept trace with flight_frames.py.
The takeoff chance itself is checked offline, where runs are free.

Contract (kind B):
  claim:        a flyer that takes off flies through every flight state in order, beats its wings through its whole
                flip-book while in the air, and shows its grounded picture again after it lands
  spoils:       takeoff is a chance at each job start, by design
  tried:        many job starts per animal; up to 16 animals side by side
  budget:       one cluster of up to 16 birds, 2,500 ticks, one run
  exposure:     any bird reached Flying
  success:      for every bird that took off and landed in the window, flight_frames.judge_bird reads PASS
  forbidden:    a flight state that skips a step; a flip-book frame other than the one the clock selects; a landed bird
                that still shows a flying picture
  allowed miss: no bird took off in the window. A bird still in the air at the limit is not judged and is not a miss.
  end:          2,500 ticks
Exit: 0 SUCCESS, 1 MOD FAILURE, 3 any other outcome, 4 refused.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.join(HERE, "..", "Utils")
sys.path.insert(0, UTILS)

import flight_frames  # noqa: E402

BIRDS_MAX = 16       # the contract's cluster; more birds only lengthen the trace
LIMIT = 2500         # the contract's window (worked example 3)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("game")
    ap.add_argument("kind", help="the PawnKindDef of the flyer (one of ours: its flip-book is read from src)")
    ap.add_argument("--with-owner", required=False, help="his words that he is present: the first run is his act")
    ap.add_argument("--map", default=None, help="the save to load (default: the game's current map)")
    ap.add_argument("--limit", type=int, default=LIMIT)
    a = ap.parse_args(argv)
    if not (a.with_owner or "").strip():
        print("REFUSED: a live flight test of a flyer runs only with the owner present; pass --with-owner \"<his words>\"")
        return 4
    kind = flight_frames.kind_of(a.kind)
    if kind is None:
        print("REFUSED: no PawnKindDef of ours named %s sets a flip-book (flight_frames.kind_of)" % a.kind)
        return 4
    import scene
    from scene import cond as c
    needs = {"map": a.map} if a.map else None
    with scene.open(a.game, needs=needs) as s:
        rep = s.raw("jawa/pawn_flight", action="report", kind=a.kind)
        pawns = [p for p in rep.get("pawns") or [] if p.get("spawned") and not p.get("dead")][:BIRDS_MAX]
        if not pawns:
            print("COULD NOT LOOK: no living %s on the map" % a.kind)
            return 3
        record = []
        for p in pawns:
            record += c.flight(p["pawn"])
        r = s.run(until=a.limit, limit=a.limit, speed="Normal", record=record)
        with open(r.trace, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
    res = flight_frames.judge_trace(rows, {p["pawn"]: kind for p in pawns})
    res["owner_present"] = a.with_owner
    print(json.dumps(res, indent=1, sort_keys=True))
    return {"SUCCESS": 0, "MOD FAILURE": 1}.get(res["outcome"], 3)


if __name__ == "__main__":
    sys.exit(main())
