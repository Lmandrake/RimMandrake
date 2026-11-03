#!/usr/bin/env python3
"""Selftest for site.despawn_pawns_in (DESTROY_BATCH_NEVER_KILLS_PAWNS_1). Offline; no bridge.

    python3 src/RimMandrake/Utils/northstar_driver/selftest_despawn_pawns.py

jawa/destroy_batch never removes pawns, so despawn_pawns_in must kill each living pawn
inside the rect by id with jawa/damage. A fake session records every call; the test
asserts exactly one lethal jawa/damage per living in-rect pawn (by thingId, colonists
allowed), none for pawns outside the rect / dead / unplaced, no destroy_batch call,
the returned count, and that a failed damage call raises instead of being counted.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from northstar_driver import site            # noqa: E402
from northstar_driver.bars import Unmeasured  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, detail))
    if not cond:
        FAILS.append(name)


class FakeSession:
    def __init__(self, pawns, damage_ok=True):
        self.pawns = pawns
        self.damage_ok = damage_ok
        self.calls = []

    def call(self, tool, **kw):
        self.calls.append((tool, kw))
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [dict(p) for p in self.pawns]}
        if tool == "jawa/damage":
            if not self.damage_ok:
                return {"success": False, "error": "refused"}
            for p in self.pawns:
                if p["id"] == kw.get("thingId"):
                    p["dead"] = True
            return {"success": True}
        return {"success": True}


RECT = (10, 20, 5, 4)   # x 10..14, z 20..23
PAWNS = [
    {"id": "Human1", "x": 10, "z": 20},             # in (corner)
    {"id": "Colonist2", "x": 14, "z": 23},          # in (far corner)
    {"id": "Animal3", "x": 12, "z": 21},            # in
    {"id": "Dead4", "x": 11, "z": 21, "dead": True},  # in, already dead
    {"id": "Out5", "x": 15, "z": 21},               # out (x == x+w)
    {"id": "Out6", "x": 12, "z": 24},               # out (z == z+h)
    {"id": "Out7", "x": 9, "z": 20},                # out (x < x)
    {"id": "Unplaced8", "x": None, "z": None},      # not on map
]
WANT = {"Human1", "Colonist2", "Animal3"}


def main():
    s = FakeSession([dict(p) for p in PAWNS])
    n = site.despawn_pawns_in(s, RECT)
    tools = [t for t, _ in s.calls]
    dmg = [kw for t, kw in s.calls if t == "jawa/damage"]
    ids = [kw.get("thingId") for kw in dmg]
    check("returns count of killed pawns", n == len(WANT), "n=%r" % n)
    check("one jawa/damage per living in-rect pawn", sorted(ids) == sorted(WANT), "ids=%r" % ids)
    check("no destroy_batch call", "jawa/destroy_batch" not in tools, "tools=%r" % tools)
    check("damage is lethal", all((kw.get("amount") or 0) >= 1000 for kw in dmg), "%r" % dmg)
    check("damage allows colonists", all(kw.get("allowColonists") is True for kw in dmg), "%r" % dmg)
    check("damage names a damageDef", all(kw.get("damageDef") for kw in dmg), "%r" % dmg)
    alive_in = [p["id"] for p in s.pawns if p["id"] in WANT and not p.get("dead")]
    check("no in-rect pawn left alive", not alive_in, "alive=%r" % alive_in)
    out_hit = [p["id"] for p in s.pawns if p["id"].startswith("Out") and p.get("dead")]
    check("no out-of-rect pawn touched", not out_hit, "%r" % out_hit)

    s2 = FakeSession([dict(p) for p in PAWNS], damage_ok=False)
    try:
        site.despawn_pawns_in(s2, RECT)
        raised = False
    except Unmeasured:
        raised = True
    check("failed damage raises Unmeasured, never counted", raised)

    s3 = FakeSession([{"id": "Out5", "x": 15, "z": 21}])
    check("empty rect kills none", site.despawn_pawns_in(s3, RECT) == 0
          and not any(t == "jawa/damage" for t, _ in s3.calls))

    print("RESULT: %s" % ("GREEN" if not FAILS else "RED %d: %s" % (len(FAILS), ", ".join(FAILS))))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
