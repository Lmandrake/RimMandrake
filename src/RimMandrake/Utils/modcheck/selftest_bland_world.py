"""Offline selftest for modcheck.bland_world against rimdrive.fake.FakeWorld. Every check has a negative control.
Run: python3 selftest_bland_world.py"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

import bland_world as BW                               # noqa: E402
from rimdrive.fake import FakeWorld, pawn_row, hediff  # noqa: E402

_results = []


def check(name, cond, detail=""):
    _results.append((name, bool(cond)))
    print("%s %s%s" % ("ok  " if cond else "FAIL", name, ("  -- " + detail) if (detail and not cond) else ""))


class S(object):                       # the Session surface bland_world uses
    def __init__(self, w):
        self.w = w

    def call(self, tool, **p):
        return self.w.call(tool, **p)


def dirty():
    w = FakeWorld(pawns=[
        pawn_row("Col1", hediffs=[hediff("Gunshot", "Shoulder")]),
        pawn_row("Col2"), pawn_row("Col3"),
        pawn_row("Raider1", kind="Tribal_Warrior", faction="TribeRough", is_player=False, hostile=True),
        pawn_row("Wolf1", kind="Wolf_Timber", faction=None, is_player=False, intelligence="Animal"),
    ])
    w.add_fire(10, 10)
    w.corpses = [{"id": "Corpse1", "def": "Corpse_Human", "x": 50, "z": 60}]
    w.queue = [{"defName": "RaidEnemy", "fireTick": 99999, "ticksUntilFire": 90000, "index": 0}]
    w.needs["Col2"] = {"Food": 0.05, "Rest": 1.0, "Joy": 1.0, "Mood": 0.5}
    return w


# 1. the world a hazard job leaves behind is NOT bland (the verifier can fail)
s = S(dirty())
probs = BW.assert_world(s)
check("assert_world flags hostiles/wildlife/fire/corpse/queued incident/injury on a dirty world",
      all(any(k in p for p in probs) for k in ("hostiles", "wildlife", "fires", "corpses", "incidents", "Col1")), str(probs))

# 2. reset leaves it provably bland, and says what it did
rep = BW.reset(s)
check("reset() makes the dirty world bland and reads it back", rep["bland"], str(rep["problems"]))
check("reset() actually removed the corpse and the queued incident",
      rep["steps"]["corpses_destroyed"] == 1 and rep["steps"]["incident_queue_cleared"] == 1, str(rep["steps"]))
check("reset() healed the injury and refilled hunger",
      not s.w.pawns["Col1"]["health"]["hediffs"] and s.w.needs["Col2"]["Food"] >= 0.95)

# 3. negative control: a corpse the destroy cannot reach stays reported, never claimed gone
w2 = dirty()
w2._t_jawa_destroy_batch = lambda **k: {"success": False, "message": "refused"}
rep2 = BW.reset(S(w2))
check("control: when destroy_batch refuses, reset() reports the corpse instead of claiming bland",
      (not rep2["bland"]) and any("corpses" in p for p in rep2["problems"]), str(rep2["problems"]))

# 4. feeding touches only LOW colonists
w3 = FakeWorld(pawns=[pawn_row("Col1"), pawn_row("Col2")])
w3.needs["Col1"] = {"Food": 0.9, "Rest": 0.5, "Joy": 0.5, "Mood": 0.5}
w3.needs["Col2"] = {"Food": 0.1, "Rest": 0.5, "Joy": 0.5, "Mood": 0.5}
fed = BW.feed_colonists(S(w3))
check("feed_colonists tops up only the hungry colonist", fed == ["Col2"] and w3.needs["Col1"]["Food"] == 0.9
      and w3.needs["Col2"]["Food"] >= 0.95 and w3.needs["Col2"]["Rest"] == 0.5, str((fed, w3.needs)))

# 5. tile candidate filter keeps the hint first and drops wet/hilly tiles
rows = [{"tile": "1", "hilliness": "Flat", "biome": "Desert", "swampiness": "0", "elevation": "10", "temperature": "20"},
        {"tile": "2", "hilliness": "Mountainous", "biome": "Desert", "swampiness": "0", "elevation": "10", "temperature": "20"},
        {"tile": "4375", "hilliness": "Flat", "biome": "AridShrubland", "swampiness": "0", "elevation": "10", "temperature": "20"},
        {"tile": "3", "hilliness": "Flat", "biome": "Desert", "swampiness": "0.4", "elevation": "10", "temperature": "20"}]
check("candidates(): dry flat tiles only, hint tile first", BW.candidates(rows) == [4375, 1], str(BW.candidates(rows)))

# 6. the naming prompt is not a modal surprise, a real modal still is
import detectors as D                                  # noqa: E402
snap = {"windows": [{"type": "RimWorld.Dialog_NamePlayerSettlement", "forcePause": True, "isDebug": False}]}
check("modal_open ignores the colony-naming prompt", D.modal_open(snap, None, None, {"suppressed": set()}) == [])
snap["windows"].append({"type": "RimWorld.Dialog_MessageBox", "forcePause": True, "isDebug": False})
check("control: modal_open still fires on any other force-pause dialog",
      len(D.modal_open(snap, None, None, {"suppressed": set()})) == 1)

# 7. rimbridge_client drops the late reply of a request that timed out, and still raises on a true desync
import rimbridge_client as RB                          # noqa: E402


class FakeBridge(RB.RimBridge):
    def __init__(self, msgs):
        self.msgs = list(msgs)
        self.events = []

    def _recv_raw(self):
        return self.msgs.pop(0)


b = FakeBridge([{"type": "response", "id": "late"}, {"type": "response", "id": "want", "result": 1}])
b.abandoned = {"late"}
check("stale reply of an abandoned request is dropped", b._recv_response("want")["id"] == "want" and not b.abandoned)
b2 = FakeBridge([{"type": "response", "id": "stranger"}])
try:
    b2._recv_response("want")
    ok = False
except RB.RimBridgeError:
    ok = True
check("control: an unknown id is still a desync error", ok)

bad = [n for n, c in _results if not c]
print("%d/%d passed" % (len(_results) - len(bad), len(_results)))
sys.exit(1 if bad else 0)
