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

# ---- DRAWBRIDGE_WINCH_DIAGNOSE_UNLINKED_REBUILT (test pilot 2026-11-03): the first sweep's destroy of rock under a mountain
# roof is followed by a roof collapse that drops CollapsedRocks AFTER it (213 live). The post-reveal re-sweep must clear
# buildings, not only plants, or the site reads UNMEASURED SITE "rock/plants/ruins still standing".
class _Collapse(object):
    def __init__(self):
        self.things, self.sweeps, self.n = ["Granite"], [], 0

    def ticks(self, n):
        pass

    def probe(self, cmd):
        return {"pawns": []}                   # no free colonist: reveal() returns early

    def call(self, tool, **kw):
        if tool == "jawa/destroy_batch":
            self.sweeps.append(kw.get("categories"))
            self.n += 1
            if kw.get("categories") == "All":
                self.things = ["CollapsedRocks"] if self.n == 1 else []   # the collapse lands after the first sweep only
            elif kw.get("categories") == "Plant":
                self.things = [t for t in self.things if not t.startswith("Plant_")]
            return {"success": True}
        if tool == "jawa/list_things":
            return {"things": [{"defName": d} for d in self.things]}
        if tool == "jawa/get_roof_batch":
            return {"roofs": []}
        return {"success": True}


C = _Collapse()
_rows = []
try:
    _okc = V._prepare_site(C, (5, 5, 20, 10), _rows, "collapse_site")
except Exception as ex:      # a fake too thin for reveal() is a selftest defect, said by name
    _okc, _rows = None, [{"error": repr(ex)[:200]}]
ok(_okc is True and len(C.sweeps) >= 2 and C.sweeps[-1] == "All",
   "prepare_site: CollapsedRocks dropped after the first sweep are cleared by the re-sweep (sweeps=%s rows=%s)" % (C.sweeps, _rows))

# ---- OPEN SKY (owner 2026-11-12: a pit matrix staged under a mountain roof collapsed in front of him; "I believe you can
# remove overhead mountain yourself as part of a test map creation from now on"). Clear, then assert: roof off first, then
# rock, then a state read that refuses naming the cells. A planted roofed cell left in place must be caught.
class _Sky(object):
    def __init__(self, roofs, rock, stuck=()):
        self.roof = dict(roofs)                # (x, z) -> RoofDef
        self.rock = dict(rock)                 # (x, z) -> ThingDef
        self.stuck = set(stuck)                # roof cells the roof write cannot clear
        self.log = []

    def ticks(self, n):
        self.log.append(("ticks", n))

    def probe(self, cmd):
        return {"pawns": []}

    @staticmethod
    def _cells(r):
        x, z, w, h = (int(v) for v in r.split(","))
        return {(a, b) for a in range(x, x + w) for b in range(z, z + h)}

    def call(self, tool, **kw):
        self.log.append((tool, kw.get("categories")))
        if tool == "jawa/map_info":
            return {"sizeX": 250, "sizeZ": 250}
        if tool == "jawa/set_roof_batch":
            for op in kw["ops"].split(";"):
                k, r = op.split(":")
                for c in self._cells(r):
                    if k == "None" and c not in self.stuck:
                        self.roof.pop(c, None)
            return {"success": True}
        if tool == "jawa/get_roof_batch":
            cs = self._cells(kw["rects"])
            hit = sorted((c, k) for c, k in self.roof.items() if c in cs)
            return {"success": True, "ops": ";".join("%s:%d,%d,1,1" % (k, c[0], c[1]) for c, k in hit) or "None:" + kw["rects"],
                    "roofs": sorted({k for _c, k in hit}) or ["None"]}
        if tool == "jawa/list_things":
            if "rect" not in kw:               # reveal's map-wide fog-trigger listing: none on this map
                return {"things": [], "countMatched": 0, "isCompleteList": True}
            cs = self._cells(kw["rect"])
            th = [{"def": d, "x": c[0], "z": c[1]} for c, d in sorted(self.rock.items()) if c in cs]
            return {"things": th, "countMatched": len(th)}
        if tool == "jawa/get_defs":
            return {"defs": [{"defName": n.split("/")[1], "found": True, "fields": {"mineable": True}}
                             for n in kw["defs"].split(";")]}
        if tool == "jawa/destroy_batch":
            for r in kw["rects"].split(";"):
                if kw.get("categories") in ("Building", "All"):
                    for c in self._cells(r if r.count(",") == 3 else r + ",1,1"):
                        self.rock.pop(c, None)
            return {"success": True}
        return {"success": True}


_site = (40, 40, 10, 10)
S1 = _Sky({(41, 41): "RoofRockThick", (35, 45): "RoofRockThin"}, {})
_v = V.assert_open_sky(S1, _site)
ok(_v["ok"] is False and (41, 41, "RoofRockThick") in _v["roofCells"] and (35, 45, "RoofRockThin") in _v["roofCells"],
   "assert_open_sky: a planted thick roof in the site and a thin one in the 6-cell margin are refused by cell (%s)" % _v["why"])
S2 = _Sky({}, {})
ok(V.assert_open_sky(S2, _site)["ok"] is True, "assert_open_sky: an open-sky, rock-free site is accepted")
S3 = _Sky({(c, d): "RoofRockThick" for c in range(25, 66) for d in range(25, 66)},
          {(44, 44): "Granite", (37, 50): "CollapsedRocks"})
_v3 = V.open_sky_site(S3, _site)
_order = [t for t, _c in S3.log if t in ("jawa/set_roof_batch", "jawa/destroy_batch")]
ok(_v3["ok"] is True and not S3.roof.get((41, 41)) and not S3.rock and _order[:1] == ["jawa/set_roof_batch"],
   "open_sky_site: thick roof over site+margin+buffer cleared BEFORE the rock and rubble are destroyed (%s %s)" % (_order, _v3["why"]))
ok(not [c for c in S3.roof if 27 <= c[0] < 63 and 27 <= c[1] < 63],
   "open_sky_site: the roof buffer reaches 7 cells past the margin (no unsupported roof left beside the cleared rock)")
S4 = _Sky({(42, 47): "RoofRockThick"}, {}, stuck={(42, 47)})
_v4 = V.open_sky_site(S4, _site)
ok(_v4["ok"] is False and (42, 47, "RoofRockThick") in _v4["roofCells"],
   "open_sky_site: a roofed cell the write could not clear is still refused, naming it (%s)" % _v4["why"])
_r5 = []
S5 = _Sky({(42, 47): "RoofRockThick"}, {}, stuck={(42, 47)})
ok(V._prepare_site(S5, _site, _r5, "sky_site") is False and "42, 47" in str(_r5),
   "prepare_site: a planted roof left in place makes the site UNMEASURED/SITE with the cell named (%s)" % str(_r5)[:200])
_r6 = []
S6 = _Sky({(c, d): "RoofRockThick" for c in range(30, 60) for d in range(30, 60)}, {(45, 45): "Granite"})
ok(V._prepare_site(S6, _site, _r6, "sky_site_clean") is True and not _r6,
   "prepare_site: a mountain-roofed site is cleared and then accepted (%s)" % str(_r6)[:200])


# ---- PROOF_SITE_HARDEN_HUGE_TRUNKS_SURVIVE_CLEAR (run6 2026-10-25): a giant standing OUTSIDE the rect re-plans its trunk
# blocker INSIDE it after every destroy, so the site read "TrunkBlocker still standing" until clear_huge_plants ran first.
# prepare_site must clear the giant itself, for every caller.
class _Giant(object):
    GIANT = (20, 3)                            # outside the site (5,5,20,10); inside the blocker tile's margin

    def __init__(self):
        self.giant, self.blocker, self.order = True, True, []

    def ticks(self, n):
        if self.giant:
            self.blocker = True                # Huge Things re-plans a vanished blocker while its plant stands

    def probe(self, cmd):
        return {"pawns": []}

    def call(self, tool, **kw):
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [], "truncated": 0}
        if tool == "jawa/destroy_batch":
            x, z, w, h = [int(v) for v in kw["rects"].split(",")]
            self.order.append(kw.get("categories"))
            if kw.get("categories") in ("Plant", "All") and x <= self.GIANT[0] < x + w and z <= self.GIANT[1] < z + h:
                self.giant = False
            if kw.get("categories") == "All":
                self.blocker = False
            self.ticks(1)
            return {"success": True}
        if tool == "jawa/list_things":
            bl = [{"defName": "RM_HugeTrunkBlocker", "x": 10, "z": 10}] if self.blocker else []
            return {"things": bl}
        if tool == "jawa/get_roof_batch":
            return {"roofs": []}
        return {"success": True}


fresh()
G = _Giant()
_rows = []
try:
    _okg = V.prepare_site(G, (5, 5, 20, 10), _rows, "giant_site")
except Exception as ex:
    _okg, _rows = None, [{"error": repr(ex)[:200]}]
ok(_okg is True and not G.giant and G.order and G.order[0] == "Plant" and not _rows,
   "prepare_site: huge plants are cleared before the site prep, so no re-planned TrunkBlocker survives (order=%s rows=%s)"
   % (G.order, _rows))
ok(any(n["id"] == "giant_site_huge_plants" for n in V.SITE_NOTES), "prepare_site: the huge-plant clear is noted as SITE")

# ---- Watchdog (LEVEL_REHEARSAL_UNSTICK_WAITS_FOR_GODOT): a dead probe channel or a spent budget aborts, a live reply resets
class _Probe(object):
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = 0

    def hp(self, cmd, wait_s=20.0, answer=False):
        return self.replies.pop(0)

    def call(self, tool, **kw):
        self.calls += 1
        return {"success": True}


DEAD = {"success": False, "error": "probe timed out (no frame serviced it)"}
LIVE = {"success": True, "units": 3}
now = [0.0]
w = V.Watchdog(_Probe([DEAD, DEAD, LIVE, DEAD, DEAD, DEAD]), budget_s=100, dead_max=3, clock=lambda: now[0])
got = [w.hp("x"), w.hp("x"), w.hp("x"), w.hp("x"), w.hp("x")]
try:
    w.hp("x")
    ok(False, "watchdog: third dead reply in a row aborts")
except V.WatchdogAbort as ex:
    ok("probe channel dead" in str(ex) and got[2] is LIVE, "watchdog: third dead reply in a row aborts; a live one reset the count")
w2 = V.Watchdog(_Probe([]), budget_s=10, clock=lambda: now[0])
ok(w2.call("jawa/x").get("success") is True, "watchdog: a call inside the budget passes through")
now[0] = 11.0
try:
    w2.call("jawa/x")
    ok(False, "watchdog: a spent budget aborts the next call")
except V.WatchdogAbort as ex:
    ok("budget" in str(ex) and w2._B.calls == 1, "watchdog: a spent budget aborts the next call before it is sent")
ok(V.Watchdog(_Probe([]), 5).calls == 0, "watchdog: other attributes pass through")

# ---- HARNESS_REPAIR_CAUSE_8135787B: site_calm tops up a starving colonist's Food before the driver's first advance
class Hungry(Fake):
    """Colonist 1 at Food 0 (the sweep sighting: 'starving: food category Starving'), colonist 5 fed, a hostile 77 that
    is no colonist. Thirst is low on both and must be left alone."""
    def __init__(self):
        Fake.__init__(self, [])
        self.needs = {1: {"Food": 0.0, "RM_Thirst": 0.1}, 5: {"Food": 0.95, "RM_Thirst": 0.1}, 6: {"Food": 0.3},
                      77: {"Food": 0.0}}
        self.pawns[6] = F.pawn_row(6)      # 0.3: above the suite's 0.25 yet starving within ~11,000 ticks of a driver
        self.need_sets = []

    def _raw(self, tool, kw):
        if tool == "jawa/pawn_need":
            if kw.get("action") == "list":
                return {"success": True, "needs": [{"need": k, "level": v} for k, v in self.needs[kw["pawn"]].items()]}
            self.need_sets.append((kw["pawn"], kw["need"], kw["level"]))
            self.needs[kw["pawn"]][kw["need"]] = kw["level"]
            return {"success": True}
        return Fake._raw(self, tool, kw)


V._CALM.clear()
hb = Hungry()
cr = V.site_calm(hb)
V._CALM.clear()
ok(sorted(hb.need_sets) == [(1, "Food", 1.0), (6, "Food", 1.0)] and sorted(cr.get("fed")) == [1, 6] and "fedError" not in cr,
   "site_calm feeds the starving and the soon-hungry colonist, not the fed one or the hostile, Food only: %s fed=%s err=%s" % (hb.need_sets, cr.get("fed"),
                                                                              cr.get("fedError") or cr.get("error")))


class HungryBroken(Hungry):
    """The calm's own pieces break (list_pawns answers, quiet_site does not): the feed still runs."""
    def _raw(self, tool, kw):
        if tool == "jawa/quiet_site":
            raise RuntimeError("quiet_site unavailable")
        return Hungry._raw(self, tool, kw)


hb2 = HungryBroken()
cr2 = V.site_calm(hb2)
V._CALM.clear()
ok(cr2.get("ok") is False and sorted(hb2.need_sets) == [(1, "Food", 1.0), (6, "Food", 1.0)],
   "a calm piece that breaks still feeds the starving colonist (ok=False names it): %s" % hb2.need_sets)

print("selftest_validation_core_site: %d/%d" % (sum(RES), len(RES)))
sys.exit(0 if all(RES) else 1)
