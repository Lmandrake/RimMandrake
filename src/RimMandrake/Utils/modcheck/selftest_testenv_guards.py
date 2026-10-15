#!/usr/bin/env python3
"""Offline selftest for modcheck/testenv_guards.py (no game, no bridge).
Run: python3 src/RimMandrake/Utils/modcheck/selftest_testenv_guards.py
Proves: the heat chunk keeps a colonist below moderate Heatstroke on the hottest site measured AND that the same math says
an unguarded long wait downs him (the guard can go red); heat_steps never lets exposure exceed the chunk; the trigger
disarm vanishes every trigger, reads back, and refuses to call a failed/truncated listing clean; the whole-map unfog stops a
later rock clear from lettering (and refuses on a map with a hostile), then re-sweeps what the unfog itself released and
fails SITE on a map that keeps releasing; calm_sky ends a storm's tail where one transition
does not; expected_hurt matches only the declared hediff on the staged subjects."""
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


class FogPocketMap(object):
    """A model of r6 map 3, from the 1.6 source: a fogged pocket behind rock holds mechs. remove_rock() is
    Building.DeSpawn -> FogGrid.Notify_FogBlockerRemoved -> FloodUnfogAdjacent: if the pocket is still fogged it floods,
    wakes what it uncovers and letters ThreatBig on a mechanoid. jawa/set_fog unfogAll is FogGrid.ClearAllFog (no letter)."""
    def __init__(self, hostiles=(), unfog_ok=True, fog_left=0, released=(), keeps_releasing=False):
        self.pocket_fogged, self.letters, self.calls = True, [], []
        self.hostiles, self.unfog_ok, self.fog_left = list(hostiles), unfog_ok, fog_left
        # released: hostiles the unfog brings onto the map (r7 calm_probe_2: 4 fleshbeasts at the same tick);
        # keeps_releasing: every sweep is followed by another release (a map that will not settle)
        self.released, self.keeps_releasing = list(released), keeps_releasing

    def call(self, tool, **p):
        self.calls.append((tool, p))
        if tool == "jawa/list_pawns":
            return {"success": True, "pawns": [{"id": h} for h in self.hostiles]}
        if tool == "jawa/set_fog":
            if not self.unfog_ok:
                return {"success": False, "message": "boom"}
            self.pocket_fogged = self.fog_left > 0
            self.hostiles += self.released
            return {"success": True, "foggedCellsBefore": 4000, "foggedCellsNow": self.fog_left}
        if tool == "jawa/destroy_bulk":
            self.hostiles = list(self.released) if self.keeps_releasing else []
            return {"success": True, "matchedCount": len(self.released)}
        return {"success": True}

    def remove_rock(self):
        if self.pocket_fogged:
            self.letters.append("ThreatBig: Area revealed")


def test_map_fog():
    m = FogPocketMap()
    r = G.clear_map_fog(m)
    m.remove_rock()
    check("clear_map_fog unfogs the swept map and verifies 0 fogged cells", r["verified"] and r["foggedNow"] == 0, r)
    check("after it, a site clear beside the pocket sends no 'Area revealed' letter", m.letters == [], m.letters)
    m2 = FogPocketMap()
    m2.remove_rock()
    check("can-fail: the same clear on a map left fogged letters ThreatBig (r6 map 3)", m2.letters == ["ThreatBig: Area revealed"])
    m3 = FogPocketMap(hostiles=["Mech_CentipedeGunner4795"])
    r = G.clear_map_fog(m3)
    check("refuses to unfog while a hostile is listed (Pawn.Notify_Unfogged would wake him)",
          not r["verified"] and "refused" in (r["error"] or "") and "jawa/set_fog" not in [c[0] for c in m3.calls], r)
    r = G.clear_map_fog(FogPocketMap(unfog_ok=False))
    check("a refused unfog is not verified", not r["verified"] and r["error"], r)
    r = G.clear_map_fog(FogPocketMap(fog_left=3))
    check("fog read back after the unfog is not verified", not r["verified"] and r["foggedNow"] == 3, r)
    # TESTENV_FLESHBEAST_HARDEN_FREED_BY_UNFOG (r7): the unfog releases hostiles the sweep before it could not list
    beasts = ["Fingerspike3818", "Fingerspike3819", "Fingerspike3821", "Bulbfreak3820"]
    m4 = FogPocketMap(released=beasts)
    m4.call("jawa/set_fog", action="unfogAll")
    check("can-fail: the unfog alone leaves the released fleshbeasts on the map (r7 calm_probe_2)", m4.hostiles == beasts)
    m5 = FogPocketMap(released=beasts)
    r = G.clear_map_fog(m5)
    tools = [c[0] for c in m5.calls]
    check("clear_map_fog re-sweeps after the unfog: released hostiles recorded and gone, read back empty",
          r["verified"] and m5.hostiles == [] and r["releasedByUnfog"] == beasts and r["sweepPasses"] == 1
          and r["hostilesAfter"] == [] and tools.index("jawa/set_fog") < tools.index("jawa/destroy_bulk"), r)
    r = G.clear_map_fog(FogPocketMap())
    check("control: a map the unfog releases nothing on needs no re-sweep", r["verified"] and r["sweepPasses"] == 0, r)
    m6 = FogPocketMap(released=["Mech_Pikeman3901"], keeps_releasing=True)
    r = G.clear_map_fog(m6)
    check("a map that keeps releasing hostiles fails SITE after MAX_UNFOG_SWEEPS (never verified)",
          not r["verified"] and "SITE" in (r["error"] or "") and r["sweepPasses"] == G.MAX_UNFOG_SWEEPS
          and [c[0] for c in m6.calls].count("jawa/destroy_bulk") == G.MAX_UNFOG_SWEEPS, r)


class SkyMap(object):
    """WeatherManager in miniature (1.6 source): TransitionTo sets lastWeather=cur, cur=new; lastWeather keeps ticking at
    (1 - lerp) for TransitionTicks, so a storm just left still strikes. settle() lights a fire per storm still ticking."""
    def __init__(self, refuse_second=False):
        self.cur, self.last, self.fires, self.calls, self.refuse_second, self.n = "DryThunderstorm", "DryThunderstorm", 177, [], refuse_second, 0

    def call(self, tool, **p):
        self.calls.append((tool, p))
        if tool == "jawa/weather_set":
            self.n += 1
            if self.refuse_second and self.n == 2:
                return {"success": False, "message": "boom"}
            if p.get("weather"):
                self.last, self.cur = self.cur, p["weather"]
            return {"success": True, "after": self.cur}
        if tool == "jawa/map_fire":
            n, self.fires = self.fires, 0
            return {"success": True, "firesExtinguished": n}
        if tool == "jawa/list_things":
            return {"success": True, "things": [{"def": "Fire"}] * self.fires, "countMatched": self.fires}
        return {"success": True}

    def settle(self):
        self.fires += sum(1 for w in (self.cur, self.last) if w == "DryThunderstorm")


def test_calm_sky():
    m = SkyMap()
    r = G.calm_sky(m, (250, 250), settle=m.settle)
    check("calm_sky: two transitions to Clear end the storm tail; no stray Fire after the settle",
          r["verified"] and r["strayFires"] == 0 and m.last == "Clear" and r["extinguished"] == 177, r)
    m2 = SkyMap()
    m2.call("jawa/weather_set", unlock=True)
    m2.call("jawa/map_fire", action="extinguish")
    m2.settle()
    check("can-fail: the old teardown (unlock + extinguish) leaves the storm lighting fires (r6 p4: 177 burning)", m2.fires > 0)
    m3 = SkyMap()
    m3.call("jawa/weather_set", weather="Clear", lockWeather=True)
    m3.call("jawa/map_fire", action="extinguish")
    m3.settle()
    check("can-fail: ONE transition to Clear still strikes from lastWeather", m3.fires > 0)
    r = G.calm_sky(SkyMap(refuse_second=True), (250, 250))
    check("a refused weather call is not verified", not r["verified"] and r["error"], r)
    m4 = SkyMap()
    r = G.calm_sky(m4, (250, 250), settle=lambda: setattr(m4, "fires", 2))
    check("a fire read back after the calm is not verified (the row goes UNMEASURED, never reads a decoy)",
          not r["verified"] and r["strayFires"] == 2, r)


def test_expected_hurt():
    pred = G.expected_hurt(["Human460415", 77], "Bruise")
    bruise = {"kind": "hurt", "severity": "damage", "subjectId": 460415, "detail": "health 1 -> 0.95; newest hediff Bruise/Torso age 30"}
    check("a Bruise on a staged pawn (ThingID form) matches", pred(bruise))
    check("a bare-number staged id matches", pred(dict(bruise, subjectId=77)))
    check("another pawn's Bruise does not match", not pred(dict(bruise, subjectId=460416)))
    check("another hediff does not match", not pred(dict(bruise, detail="health 1 -> 0.9; newest hediff Burn/Torso age 1")))
    check("a hediff that only starts with Bruise does not match",
          not pred(dict(bruise, detail="health 1 -> 0.9; newest hediff BruiseX/Torso age 1")))
    check("a downed staged pawn is not the expected bruise", not pred(dict(bruise, kind="downed")))
    check("no staged ids, nothing matches", not G.expected_hurt([], "Bruise")(bruise))


# Pyrelands' consumer of calm_sky. The wiring check lives HERE, not in Pyrelands/selftest_pyrelands_site.py: a file in the
# mod folder outside validation.py/northstar/ is part of modcheck.status.mod_hash, and editing it would turn the r6
# Pyrelands proofs STALE for a harness-only change.
PYRE_VALIDATION = os.path.join(os.path.dirname(os.path.dirname(HERE)), "Pyrelands", "validation.py")


def _load_pyrelands_validation():
    import importlib.util
    utils = os.path.dirname(HERE)
    if utils not in sys.path:
        sys.path.insert(0, utils)
    try:
        spec = importlib.util.spec_from_file_location("pyre_validation_testenv", PYRE_VALIDATION)
        v = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(v)
        return v
    except Exception as ex:  # noqa: BLE001
        check("Pyrelands validation.py loads", False, repr(ex))
        return None


def test_pyrelands_storm_wiring():
    """TESTENV_STORM_FIRES_HARDEN_DECOY_BURN: the herd drive calms the sky (Clear x2, extinguish, stray Fire read back)
    before burn A; stray fire makes it UNMEASURED/SITE (never a decoy read as the burn); a weather chain's teardown ends
    the storm outright instead of only unlocking it."""
    v = _load_pyrelands_validation()
    if v is None:
        check("Pyrelands validation.py importable for the wiring check", False)
        return

    class _Sess(object):
        def __init__(self, fires_after):
            self.calls, self.fires_after = [], fires_after

        def call(self, tool, **q):
            self.calls.append((tool, q))
            if tool == "jawa/map_info":     # _wait re-asserts the Pyrelands site first (as in the heat-guard fake)
                return {"success": True, "sizeX": 250, "sizeZ": 250, "mapId": 2, "mapBiome": "RM_Pyrelands"}
            if tool == "jawa/name_colony":
                return {"success": True, "settlements": [{"tile": 5}]}
            if tool == "jawa/list_pawns":
                return {"success": True, "pawns": []}
            if tool == "jawa/pawn_need" and q.get("action") == "list":
                return {"success": True, "needs": [{"need": "Food", "level": 0.9}]}
            if tool == "jawa/list_things":
                return {"success": True, "things": [{"def": "Fire"}] * self.fires_after, "countMatched": self.fires_after}
            if tool == "jawa/weather_set":
                return {"success": True, "after": q.get("weather")}
            return {"success": True}

    class _T(object):
        upstream_failed, watch = False, None

        def __init__(self, fires_after):
            self.session, self.components, self.rec, self.waits = _Sess(fires_after), [], [], []

        def bridge_call(self, tool, **q):
            return self.session.call(tool, **q)

        def wait_ticks(self, n):
            self.waits.append(n)
            return n

        def _record(self, *a):
            self.rec.append(a)

    v._GEN.clear()
    t = _T(0)
    r = v._calm_sky(t)
    tools = [c[0] for c in t.session.calls]
    wcalls = [c[1] for c in t.session.calls if c[0] == "jawa/weather_set"]
    check("calm sky: Clear locked, then Clear again (lastWeather Clear), map extinguished, Fire read back",
          r["verified"] and wcalls[:2] == [{"weather": "Clear", "lockWeather": True}, {"weather": "Clear"}]
          and tools.index("jawa/map_fire") < tools.index("jawa/list_things"), (r, tools))
    check("calm sky settles one short governed wait before the read-back", t.waits == [v.CALM_SETTLE_TICKS], t.waits)
    t = _T(177)
    try:
        v._calm_sky(t)
        check("can-fail: 177 stray fires after the calm make the row UNMEASURED", False)
    except v._Unmeasured as e:
        check("can-fail: 177 stray fires after the calm make the row UNMEASURED (SITE)", "SITE" in str(e) and t.upstream_failed, str(e))
    src = open(PYRE_VALIDATION, encoding="utf-8").read()
    herd = src.split("def herd_follows_drive")[1].split("\ndef ")[0]
    check("the herd drive calms the sky before burn A", "_calm_sky(t)" in herd
          and herd.index("_calm_sky(t)") < herd.index('_herd_burn(t, PAD_HERD_OLD, "A")'))
    tail = herd.split("    finally:\n")[-1] if "    finally:\n" in herd else ""
    check("the calm's Clear lock is released in a finally (it never outlives the herd row)",
          herd.index("try:") < herd.index("_calm_sky(t)") and 'jawa/weather_set", unlock=True' in tail)
    t = _T(0)
    v._tear_down(t, False, True)
    w = [c[1] for c in t.session.calls if c[0] == "jawa/weather_set"]
    check("a weather chain's teardown unlocks and then transitions to Clear twice (no storm tail leaks into the next chain)",
          w == [{"unlock": True}, {"weather": "Clear"}, {"weather": "Clear"}], w)


def main():
    for t in (test_heat_math, test_heat_steps, test_disarm, test_clear_heatstroke, test_reveal_disarms_first, test_map_fog,
              test_calm_sky, test_expected_hurt, test_pyrelands_storm_wiring):
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
