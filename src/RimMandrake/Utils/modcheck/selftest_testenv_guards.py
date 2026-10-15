#!/usr/bin/env python3
"""Offline selftest for modcheck/testenv_guards.py (no game, no bridge).
Run: python3 src/RimMandrake/Utils/modcheck/selftest_testenv_guards.py
Proves: the heat chunk keeps a colonist below moderate Heatstroke on the hottest site measured AND that the same math says
an unguarded long wait downs him (the guard can go red); heat_steps never lets exposure exceed the chunk; the trigger
disarm vanishes every trigger, reads back, and refuses to call a failed/truncated listing clean."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import testenv_guards as G  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


def test_heat_math():
    check("no gain at or below the safe max", G.heatstroke_gain(60000, G.SAFE_MAX_WORST_C) == 0.0)
    # vanilla floor: 0.000375 per 60-tick interval just above the safe max
    check("minimum step applies just above the safe max", abs(G.heatstroke_gain(600, G.SAFE_MAX_WORST_C + 0.1) - 0.00375) < 1e-9)
    g = G.heatstroke_gain(G.HEAT_CHUNK_TICKS, G.HOTTEST_SITE_C)
    check("one chunk at the hottest site stays below moderate Heatstroke", 0 < g < G.HEATSTROKE_MODERATE, g)
    check("the margin site is hotter than every r5 measurement (56.7, 58.3 C)", G.HOTTEST_SITE_C > 58.3)
    # can-fail: r5's real scorchfruit_spoils_fast wait (half a day per sample) at the measured 56.7 C downs a colonist
    check("unguarded half-day at 56.7 C reaches extreme (0.62): the guard is needed", G.heatstroke_gain(30000, 56.7) >= 0.62,
          G.heatstroke_gain(30000, 56.7))
    check("curve interpolates (25->25, 37.5->32.5)", G._curve(25.0) == 25.0 and abs(G._curve(37.5) - 32.5) < 1e-9)


def test_heat_steps():
    for n, carried in ((30000, 0), (100, 0), (6000, 0), (6001, 5999), (12345, 4000), (0, 0), (500, 6000)):
        st = G.heat_steps(n, carried)
        check("heat_steps(%d, %d) sums to n" % (n, carried), sum(s for s, _ in st) == n, st)
        have, worst = carried, carried
        for s, guard in st:
            have += s
            worst = max(worst, have)
            if guard:
                have = 0
        check("heat_steps(%d, %d) never carries more than the chunk" % (n, carried),
              worst <= max(G.HEAT_CHUNK_TICKS, carried) and (carried < G.HEAT_CHUNK_TICKS or st[0] == (0, True) or n == 0), st)
    check("a 30000-tick wait is 5 guarded chunks", G.heat_steps(30000) == [(6000, True)] * 5, G.heat_steps(30000))
    check("a short wait after 5000 carried guards at the boundary",
          G.heat_steps(2000, 5000) == [(1000, True), (1000, False)], G.heat_steps(2000, 5000))
    try:
        G.heat_steps(10, chunk=0)
        check("chunk 0 refused", False)
    except ValueError:
        check("chunk 0 refused", True)


class FakeMap(object):
    def __init__(self, things, fail_list=False, truncate=False, ignore_destroy=False, pawns=None, refuse_remove=()):
        self.things = list(things)
        self.fail_list, self.truncate, self.ignore_destroy = fail_list, truncate, ignore_destroy
        self.pawns = pawns or []
        self.refuse_remove = set(refuse_remove)
        self.calls = []

    def call(self, tool, **p):
        self.calls.append((tool, p))
        if tool == "jawa/list_things":
            if self.fail_list:
                return {"success": False, "message": "boom"}
            want = set(p["defName"].split(","))
            rows = [t for t in self.things if t["def"] in want]
            if self.truncate:
                return {"success": True, "things": rows[:1], "countMatched": len(rows), "isCompleteList": False}
            return {"success": True, "things": rows, "countMatched": len(rows), "isCompleteList": True}
        if tool == "jawa/destroy_batch":
            assert p["categories"] == "Ethereal", p
            cells = set(tuple(int(v) for v in r.split(",")[:2]) for r in p["rects"].split(";"))
            gone = [t for t in self.things if (t["x"], t["z"]) in cells]
            if not self.ignore_destroy:
                self.things = [t for t in self.things if (t["x"], t["z"]) not in cells]
            return {"success": True, "destroyed": len(gone)}
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": self.pawns}
        if tool == "jawa/pawn_health":
            if p["pawn"] in self.refuse_remove:
                return {"success": False, "message": "Pawn has no hediff 'Heatstroke'."}
            for pw in self.pawns:
                if pw["id"] == p["pawn"]:
                    pw["health"]["hediffs"] = [h for h in pw["health"]["hediffs"] if h["def"] != p["hediff"]]
            return {"success": True}
        return {"success": True}


ARMED = [{"id": "TriggerUnfogged1", "def": "TriggerUnfogged", "x": 10, "z": 10},
         {"id": "SignalAction_Ambush2", "def": "SignalAction_Ambush", "x": 10, "z": 10},
         {"id": "SignalAction_DormancyWakeUp3", "def": "SignalAction_DormancyWakeUp", "x": 40, "z": 12},
         {"id": "RectTrigger4", "def": "RectTrigger", "x": 70, "z": 70}]


def test_disarm():
    m = FakeMap(ARMED)
    r = G.disarm_fog_triggers(m)
    check("disarm finds all four and verifies", r["found"] == 4 and r["left"] == 0 and r["verified"], r)
    check("disarm counts by def", r["byDef"].get("SignalAction_Ambush") == 1 and r["byDef"].get("TriggerUnfogged") == 1, r)
    check("one destroy_batch call for the overlapping cells", [c[0] for c in m.calls].count("jawa/destroy_batch") == 1)
    m = FakeMap([])
    r = G.disarm_fog_triggers(m)
    check("a clean map is verified with no destroy call", r["verified"] and r["found"] == 0
          and "jawa/destroy_batch" not in [c[0] for c in m.calls], r)
    r = G.disarm_fog_triggers(FakeMap(ARMED, fail_list=True))
    check("a failed listing is NOT verified", not r["verified"] and r["error"], r)
    r = G.disarm_fog_triggers(FakeMap(ARMED, truncate=True))
    check("a truncated listing is NOT verified", not r["verified"] and "truncated" in (r["error"] or ""), r)
    r = G.disarm_fog_triggers(FakeMap(ARMED, ignore_destroy=True))
    check("triggers that survive the destroy read back as left, not verified",
          not r["verified"] and r["left"] == 4 and "TriggerUnfogged" in r["leftDefs"], r)
    check("every trigger def the module names is a Core trigger or signal action",
          all(d in ("TriggerUnfogged", "RectTrigger", "RadialTrigger", "TriggerContainerEmptied") or d.startswith("SignalAction_")
              for d in G.FOG_TRIGGER_DEFS))


def _pawn(pid, sev=None, dead=False, intel="Humanlike"):
    hed = [{"def": "Heatstroke", "severity": sev}] if sev is not None else []
    return {"id": pid, "dead": dead, "intelligence": intel, "health": {"hediffs": hed + [{"def": "Asthma", "severity": 0.1}]}}


def test_clear_heatstroke():
    m = FakeMap([], pawns=[_pawn("a", 0.31), _pawn("b"), _pawn("c", 0.5, dead=True), _pawn("dog", 0.4, intel="Animal"),
                           _pawn("keep", 0.2), _pawn("r", 0.1)], refuse_remove=["r"])
    r = G.clear_heatstroke(m, keep_ids=["keep"])
    check("heatstroke cleared on a hot colonist, severity recorded first", r["cleared"] == [("a", 0.31)], r)
    check("a refused removal is reported, not hidden", r["failed"] and r["failed"][0][0] == "r", r)
    removes = [c[1]["pawn"] for c in m.calls if c[0] == "jawa/pawn_health"]
    check("never touches the dead, animals, kept ids or pawns without it", sorted(removes) == ["a", "r"], removes)
    check("other hediffs are left alone", any(h["def"] == "Asthma" for h in m.pawns[0]["health"]["hediffs"]))

    class Broken(object):
        def call(self, tool, **p):
            raise RuntimeError("socket")
    r = G.clear_heatstroke(Broken())
    check("a dead socket is a reported failure, never a crash", not r["read"] and r["failed"], r)


def test_reveal_disarms_first():
    """validation_core.reveal (the fog reveal GSS/FlowWorks site prep uses) vanishes the triggers BEFORE a colonist's sight
    unfogs anything, and reports the read-back."""
    sys.path.insert(0, os.path.dirname(HERE))
    import validation_core as VC

    class B(FakeMap):
        def __init__(self):
            FakeMap.__init__(self, ARMED)
            self.order = []

        def call(self, tool, **p):
            self.order.append(tool)
            return FakeMap.call(self, tool, **p)

        def probe(self, cmd):
            self.order.append("probe:" + cmd.split("=")[-1].split(":")[0])
            if cmd == "colonists":
                return {"pawns": [{"id": 7, "pos": [5, 5], "downed": False}]}
            return {"success": True}

        def ticks(self, n):
            self.order.append("ticks")

    b = B()
    r = VC.reveal(b, (20, 20, 10, 10))
    first_tp = b.order.index("probe:tp")
    check("reveal: triggers vanished before the colonist moves", b.order.index("jawa/destroy_batch") < first_tp, b.order)
    check("reveal: read-back reported and verified", r.get("revealed") and r["fogTriggers"]["verified"], r)

    class Site(B):
        """prepare_site's other calls answer clean; the triggers ignore destroy when `sticky`."""
        def __init__(self, sticky):
            B.__init__(self)
            self.ignore_destroy = sticky

        def call(self, tool, **p):
            if tool == "jawa/list_things" and "defName" not in p:
                return {"success": True, "things": []}
            if tool == "jawa/destroy_batch" and p.get("categories") != "Ethereal":
                return {"success": True}
            if tool == "jawa/get_roof_batch":
                return {"success": True, "roofs": []}
            return B.call(self, tool, **p)

    rows = []
    check("prepare_site: a disarmed site is ready", VC.prepare_site(Site(False), (20, 20, 10, 10), rows, "S") and not rows, rows)
    rows = []
    ok = VC.prepare_site(Site(True), (20, 20, 10, 10), rows, "S")
    check("can-fail: prepare_site refuses a site whose triggers read back armed (UNMEASURED/SITE)",
          not ok and rows and rows[0]["status"] == "UNMEASURED" and "still armed" in str(rows[0]["detail"]), rows)


def main():
    for t in (test_heat_math, test_heat_steps, test_disarm, test_clear_heatstroke, test_reveal_disarms_first):
        try:
            t()
        except Exception as ex:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            check("%s raised" % t.__name__, False, repr(ex))
    print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
