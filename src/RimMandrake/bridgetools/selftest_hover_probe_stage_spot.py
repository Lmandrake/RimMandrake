#!/usr/bin/env python3
"""Selftest for prove_hover_tooltip.stage_spot (GAMEENV_FIX_PROOFSITE_CF15524E_ITEMS_WAIT).

The A2 live proof of PLAYER_HOVER_PROBE_TOOLTIP_DRAWN stopped with "could not place a ButcherSpot" on a reply that
said placed=1, survived=1: jawa/build_batch's read-back (things[]) holds def/x/z but no ThingID, so the old probe
found no id. This replays that reply shape (JawaBenchMapTools.cs BuildBatch) and jawa/list_things' row shape
(JawaBenchTerrainTools.cs ThingListRow, key `id`) through a fake bridge, and checks each refusal stays a NO VERDICT.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prove_hover_tooltip as ph  # noqa: E402

# The build_batch reply recorded live 2026-11-06 (result_A2.json), with the read-back row the C# writes.
BUILT = {"success": True, "placed": 1, "survived": 1, "lostToLaterOps": 0, "failedCount": 0, "failed": [],
         "displacedCount": 0, "displaced": [], "message": "1 placed.",
         "things": [{"def": "ButcherSpot", "stuff": None, "x": 125, "z": 125, "rot": 0, "faction": "PlayerColony",
                     "hitPoints": None, "maxHitPoints": None, "quality": None, "destroyed": False}]}
LISTED = {"success": True, "things": [{"id": "ButcherSpot12345", "def": "ButcherSpot", "label": "Butcher spot"}],
          "countReturned": 1, "countMatched": 1, "scanned": 900, "isCompleteList": True}


class Fake:
    def __init__(self, replies):
        self.replies, self.calls = replies, []

    def call(self, tool, params=None):
        self.calls.append((tool, params or {}))
        return self.replies.get(tool, {"success": True})


def run(replies):
    p = Fake(replies)
    try:
        return ph.stage_spot(p, 250, 250), p
    except ph.NoVerdict as e:
        return "NOVERDICT: %s" % e, p


def main():
    fails = []

    def expect(name, ok, got):
        print("%s %s: %s" % ("PASS" if ok else "FAIL", name, str(got)[:200]))
        if not ok:
            fails.append(name)

    got, p = run({"jawa/build_batch": BUILT, "jawa/list_things": LISTED})
    expect("recorded reply yields the listed id", got == ("ButcherSpot12345", 125, 125), got)
    lt = [c for c in p.calls if c[0] == "jawa/list_things"]
    expect("id looked up at the built cell", bool(lt) and lt[0][1].get("rect") == "125,125,1,1"
           and lt[0][1].get("defName") == "ButcherSpot", lt)

    lost = dict(BUILT, survived=0, lostToLaterOps=1)
    got, _ = run({"jawa/build_batch": lost, "jawa/list_things": LISTED})
    expect("survived=0 is a NO VERDICT", str(got).startswith("NOVERDICT: could not place"), got)

    got, _ = run({"jawa/build_batch": {"success": False, "error": "x"}, "jawa/list_things": LISTED})
    expect("refused build is a NO VERDICT", str(got).startswith("NOVERDICT: could not place"), got)

    got, _ = run({"jawa/build_batch": BUILT, "jawa/list_things": {"success": True, "things": []}})
    expect("empty list_things is a NO VERDICT", str(got).startswith("NOVERDICT: placed"), got)

    # A hover the bridge never set must not read as the answer "no" (reviewer finding, 2026-11-06).
    dead = {"tooltip": {"drawn": False}, "readout": {"changed": False}, "hoverOk": False, "hoverReply": "{}"}
    try:
        got = ph.verdict([dead, dict(dead)], readout_counts=False)
    except ph.NoVerdict as e:
        got = "NOVERDICT: %s" % e
    expect("no hover accepted is a NO VERDICT, not NOT_DRAWN", str(got).startswith("NOVERDICT"), got)
    live = dict(dead, hoverOk=True)
    expect("an accepted hover with no box is a real no", ph.verdict([dead, live], readout_counts=False) is False, live)

    stray = dict(dead, tooltip={"drawn": True}, readout={"changed": True})
    expect("a box after a failed hover does not count as DRAWN",
           ph.verdict([stray, live], readout_counts=True) is False, stray)

    print("RESULT %s" % ("FAIL " + ",".join(fails) if fails else "PASS"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
