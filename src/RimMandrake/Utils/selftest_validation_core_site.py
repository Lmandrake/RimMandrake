#!/usr/bin/env python3
"""Offline selftest of validation_core's SITE-disturbance handling (TESTENV_GOVERNOR_STOP_SITE_NOT_MOD, 2026-10-19).
A scripted fake bridge stands in for the game: a wild Fingerspike arriving mid-prepare, a colonist bruised in a fight, and the
cases that MUST still stop the block. Run: python3 selftest_validation_core_site.py  (prints N/N)."""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "modcheck"))

import validation_core as V  # noqa: E402
import clockgate as cg  # noqa: E402
from rimdrive import fake as F  # noqa: E402

RES = []


def ok(cond, label):
    print("%-4s %s" % ("ok" if cond else "FAIL", label))
    RES.append(bool(cond))


def stop(kind, detail, severity="damage", subject=5, executed=10, requested=30, extra=()):
    t = {"seq": 1, "kind": kind, "severity": severity, "tick": 100, "subjectId": subject, "critical": False,
         "declared": False, "detail": detail}
    return {"state": "stopped", "executed": executed, "requested": requested, "stopBy": t,
            "triggers": [t] + list(extra)}


FINGER = lambda: stop("hostile_arrival", "arrived: Fingerspike Fingerspike (other)", "threat", 77)   # noqa: E731
BRUISE = lambda: stop("hurt", "health 0.89 -> 0.79; newest hediff Bruise/Leg age 0 from Human", "damage", 5)   # noqa: E731


class Fake(V._BridgeBase):
    """safe_advance replays `script` (a stop result, or None for done); everything else is a tiny pawn world."""
    def __init__(self, script):
        self.script, self.calls = list(script), []
        self.tools = {cg.SAFE_ADVANCE}
        self.pawns = {1: F.pawn_row(1), 5: F.pawn_row(5)}
        self.pawns[77] = F.pawn_row(77, kind="Fingerspike", faction="Entities", is_player=False, hostile=True,
                                    intelligence="ToolUser", x=10, z=10)
        self.mental = {5: "SocialFighting"}
        self.hediffs = {5: [{"def": "Bruise", "part": "Leg"}]}
        self.advanced = 0

    def _raw(self, tool, kw):
        self.calls.append(tool)
        if tool == cg.SAFE_ADVANCE:
            if self.script:
                r = self.script.pop(0)
                if r is not None:
                    self.advanced += r["executed"]
                    return r
            self.advanced += kw.get("ticks", 0)
            return {"success": True, "state": "done", "executed": kw.get("ticks", 0)}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [copy.deepcopy(p) for p in self.pawns.values()], "truncated": 0}
        if tool == "jawa/pawn_force_incapacitate":
            self.pawns.pop(kw["pawn"], None)
            return {"success": True}
        if tool == "jawa/pawn_mental":
            if kw["action"] == "end":
                self.mental.pop(kw["pawn"], None)
            return {"success": True, "currentState": self.mental.get(kw["pawn"])}
        if tool == "jawa/pawn_health":
            self.hediffs[kw["pawn"]] = []
            return {"success": True}
        return {"success": True}


def fresh():
    V.SITE_NOTES[:] = []
    V.SITE_RECOVERED[0] = 0
    V.SITE_PHASE[0] = "measure"


# ---- pure classifier: each can go red
fresh()
c = V.classify_site_stop(FINGER())
ok(c and c["kind"] == "intruder", "classify: hostile arrival is an intruder")
c = V.classify_site_stop(BRUISE())
ok(c and c["kind"] == "fight" and c["hurt"] == [(5, "Bruise", "Leg")], "classify: bruise 'from Human' is a fight, wound named")
ok(V.classify_site_stop(stop("hurt", "health 1 -> 0.95; newest hediff Bruise/Torso age 30")) is None,
   "classify: the mod's own bruise (no pawn source) is a REAL stop")
ok(V.classify_site_stop(stop("death", "died")) is None, "classify: a death is a REAL stop")
ok(V.classify_site_stop(stop("downed", "downed", "damage")) is None, "classify: a downed colonist is a REAL stop")
ok(V.classify_site_stop(dict(FINGER(), triggers=FINGER()["triggers"] + [stop("death", "died")["stopBy"]])) is None,
   "classify: a death riding along a hostile arrival is a REAL stop")
crit = FINGER()
crit["stopBy"] = dict(crit["stopBy"], critical=True)
ok(V.classify_site_stop(crit) is None, "classify: a critical actor is a REAL stop")
ok(V.classify_site_stop({"state": "done"}) is None, "classify: a finished chunk is nothing")

# ---- mock: a wild Fingerspike arrives mid-prepare -> the block continues and records SITE
fresh()
B = Fake([FINGER()])
V.SITE_PHASE[0] = "prepare"
r = B.ticks(30)
ok(r["advanced"] == 30 and B.advanced == 30, "mock: Fingerspike mid-prepare -> all 30 ticks run (%s)" % B.advanced)
ok(77 not in B.pawns, "mock: the Fingerspike was removed (vanished)")
n = [x for x in V.SITE_NOTES if x["id"] == "SITE_DISTURBANCE_INTRUDER"]
ok(len(n) == 1 and n[0]["detail"]["phase"] == "prepare" and n[0]["detail"]["recovered"] and n[0]["detail"]["removed"] == [77],
   "mock: recorded as a SITE note, phase prepare, recovered")

# ---- mock: colonist fight bruise -> fight ended, wound healed, run continues
fresh()
B = Fake([BRUISE()])
B.pawns.pop(77)
r = B.ticks(30)
ok(r["advanced"] == 30 and 5 not in B.mental and B.hediffs[5] == [], "mock: fight ended, bruise healed, 30 ticks run")
ok(any(x["id"] == "SITE_DISTURBANCE_FIGHT" and x["detail"]["healed"] == [(5, "Bruise", "Leg", True)] for x in V.SITE_NOTES),
   "mock: fight recorded with the heal read back")

# ---- must still stop: a real stop propagates; a recovery that does not read back propagates
fresh()
B = Fake([stop("death", "died")])
try:
    B.ticks(30)
    ok(False, "mock: a death must raise GovernorStop")
except cg.GovernorStop:
    ok(not V.SITE_NOTES, "mock: a death raises GovernorStop and records no SITE recovery")
fresh()
B = Fake([FINGER()])
B._kill = B._raw
B._raw = lambda tool, kw: ({"success": True} if tool == "jawa/pawn_force_incapacitate" else B._kill(tool, kw))   # kill lies
try:
    B.ticks(30)
    ok(False, "mock: an intruder that will not go must raise")
except cg.GovernorStop:
    ok(any(x["detail"].get("recovered") is False for x in V.SITE_NOTES), "mock: failed recovery raises and is noted unrecovered")

# ---- the cap: a site that keeps raising them stops
fresh()
B = Fake([FINGER() for _ in range(V.SITE_RECOVER_MAX + 1)])


def refill(tool, kw, _o=B._raw):
    if tool == cg.SAFE_ADVANCE and not any(p["id"] == 77 for p in B.pawns.values()):
        B.pawns[77] = F.pawn_row(77, kind="Fingerspike", faction="Entities", is_player=False, hostile=True,
                                 intelligence="ToolUser", x=10, z=10)
    return _o(tool, kw)


B._raw = refill
try:
    B.ticks(30 * (V.SITE_RECOVER_MAX + 2))
    ok(False, "cap: the %dth recovery must raise" % (V.SITE_RECOVER_MAX + 1))
except cg.GovernorStop:
    ok(V.SITE_RECOVERED[0] == V.SITE_RECOVER_MAX, "cap: stops after %d recoveries" % V.SITE_RECOVER_MAX)

# ---- prepare_site sweeps a wild animal near the plot before the colonist walks in; far ones are left alone
fresh()
B = Fake([])
B.pawns.pop(77)
B.pawns[80] = F.pawn_row(80, kind="Hare", faction=None, is_player=False, intelligence="Animal", x=12, z=12)
B.pawns[81] = F.pawn_row(81, kind="Hare", faction=None, is_player=False, intelligence="Animal", x=240, z=240)
sw = V.remove_intruders(B, (5, 5, 20, 10))
ok(sw["removed"] == [80] and 81 in B.pawns and 80 not in B.pawns and 1 in B.pawns,
   "sweep: near hare vanished, far hare and colonists kept (%s)" % sw)

print("selftest_validation_core_site: %d/%d" % (sum(RES), len(RES)))
sys.exit(0 if all(RES) else 1)
