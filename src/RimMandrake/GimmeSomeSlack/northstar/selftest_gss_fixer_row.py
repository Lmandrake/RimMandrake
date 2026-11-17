#!/usr/bin/env python3
"""SC_floor_end_fixer_spared_other_builder_shocked's verdict (scene_rows.fixer_verdict) and its driver against a scripted bridge.

    python3 src/RimMandrake/GimmeSomeSlack/northstar/selftest_gss_fixer_row.py      # exit 0 = every check passes
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "..", "Utils"))
import scene_rows  # noqa: E402


def t(shocked, on=True, job="HaulToContainer", target=(1, 1)):
    return {"onEnd": on, "job": job, "target": list(target) if target else None, "shocked": shocked}


class Bridge:
    """Two builders; the blueprint whose id the fixer's job carries decides who the mod would shock."""
    def __init__(self, shock_fixer=False, shock_other=True, builders=2, place=True):
        self.shock = {1: shock_fixer, 2: shock_other}
        self.builders, self.place, self.hold_off, self.n = builders, place, False, 100
        self.jobs = {}

    def probe(self, cmd):
        if cmd == "colonists":
            return {"pawns": [{"id": i, "pos": [5, 5]} for i in range(1, self.builders + 1)]}
        return {"success": True}

    def ticks(self, n):
        pass

    def call(self, tool, **kw):
        if tool == "jawa/pawn_get":
            pid = kw["pawn"]
            hed = [{"def": "RM_FallenWireShock"}] if self.jobs.get(pid) and self.shock.get(pid) else []
            return {"pawns": [{"skills": [{"skill": "Construction", "disabled": False}], "hediffs": hed, "pos": [0, 0]}]}
        if tool in ("jawa/blueprint_place", "rimworld/spawn_thing"):
            self.n += 1
            return {"success": True, "thingId": self.n} if self.place else {"success": False, "error": "refused"}
        if tool == "jawa/ordered_job":
            self.jobs[int(kw["pawnId"])] = kw
            return {"success": True, "curJob": {"def": kw["jobDef"]}}
        return {}


def main():
    fails = []

    def check(ok, msg):
        print(("ok   " if ok else "FAIL ") + msg)
        if not ok:
            fails.append(msg)

    check(scene_rows.fixer_verdict(t(False), t(True)) == "PASS", "the fixer unharmed on the end, the other builder shocked on it: passes")
    check(scene_rows.fixer_verdict(t(True), t(True)) == "FAIL", "planted: the fixer shocked fails")
    check(scene_rows.fixer_verdict(t(False), t(False)) == "FAIL", "planted: a builder of something else spared fails (the exemption is too wide)")
    check(scene_rows.fixer_verdict(t(False, on=False), t(True)) == "UNMEASURED", "a fixer who never stood on the end measures nothing")
    check(scene_rows.fixer_verdict(t(False, job=None), t(True)) == "UNMEASURED", "a fixer with no job measures nothing")
    check(scene_rows.fixer_verdict(t(None), t(True)) == "UNMEASURED", "health not read measures nothing")
    check(scene_rows.fixer_verdict(None, t(True)) == "UNMEASURED", "a missing trial measures nothing")
    args = ((10, 10), (11, 10), (11, 4))
    st, cause, d = scene_rows.fixer_and_other_builder(Bridge(), None, *args)
    check((st, cause) == ("PASS", "MOD"), "driver: a mod that spares the fixer and shocks the other passes (%s %s)" % (st, cause))
    check(d["trials"]["fixer"]["target"] == [11, 10] and d["trials"]["other"]["target"] == [11, 4], "driver: the fixer's job goes to the cut cell's blueprint, the other's to the far one")
    st, _, _ = scene_rows.fixer_and_other_builder(Bridge(shock_fixer=True), None, *args)
    check(st == "FAIL", "driver, planted: a mod that shocks the fixer fails (%s)" % st)
    st, _, _ = scene_rows.fixer_and_other_builder(Bridge(shock_other=False), None, *args)
    check(st == "FAIL", "driver, planted: a mod that spares every builder fails (%s)" % st)
    st, cause, _ = scene_rows.fixer_and_other_builder(Bridge(builders=1), None, *args)
    check((st, cause) == ("UNMEASURED", "SITE"), "driver: one builder on the map is unmeasured (site) (%s %s)" % (st, cause))
    st, cause, _ = scene_rows.fixer_and_other_builder(Bridge(place=False), None, *args)
    check((st, cause) == ("UNMEASURED", "HARNESS"), "driver: a refused blueprint is unmeasured (harness), never a pass (%s %s)" % (st, cause))
    # SC_shock_reach_deck_cord_per_value: the FlowWorks deck cord under each shockReach value
    def dk(a, o, n, fell=True):
        return {"All": {"fell": fell, "shocked": a}, "OnlyDownedLines": {"fell": True, "shocked": o}, "None": {"fell": True, "shocked": n}}
    check(scene_rows.deck_verdict(dk(True, True, False)) == "PASS", "deck cord: bites under All and Only downed lines, not under None: passes")
    check(scene_rows.deck_verdict(dk(True, True, True)) == "FAIL", "planted: a deck cord that bites under None fails")
    check(scene_rows.deck_verdict(dk(True, False, False)) == "FAIL", "planted: a deck cord that spares under Only downed lines fails")
    check(scene_rows.deck_verdict(dk(False, True, False)) == "FAIL", "planted: a deck cord that spares under All fails")
    check(scene_rows.deck_verdict(dk(True, True, False, fell=False)) == "UNMEASURED", "a collapse that dropped no live cord measures nothing")
    check(scene_rows.deck_verdict({"All": {"fell": True, "shocked": True}}) == "UNMEASURED", "a value not run measures nothing")

    class Fw:
        def __init__(self, loaded=True):
            self.loaded, self.value = loaded, "All"

        def call(self, tool, **kw):
            return {"success": True} if self.loaded else {"success": False, "error": "unknown tool"}

        def ap(self, cmd):
            if cmd.startswith("set:shockReach="):
                self.value = cmd.split("=", 1)[1]
            return {"success": True}

        def ticks(self, n):
            pass
    fw = Fw()
    st, cause, d = scene_rows.deck_cord_per_value(fw, None, run_collapse=lambda o: {"status": "PASS", "detail": {
        "cordsDropped": 4, "liveFalls60": 1, "liveHalves": 1, "shocks": 0 if fw.value == "None" else 1, "hediffs": [] if fw.value == "None" else ["RM_FallenWireShock"]}})
    check((st, cause) == ("PASS", "MOD") and fw.value == "All", "deck driver: three collapses read per value pass, and the setting is put back to All (%s %s %s)" % (st, cause, fw.value))
    st, _, _ = scene_rows.deck_cord_per_value(fw, None, run_collapse=lambda o: {"detail": {"cordsDropped": 4, "liveFalls60": 1, "liveHalves": 1, "hediffs": ["RM_FallenWireShock"]}})
    check(st == "FAIL", "deck driver, planted: a mod that shocks under None fails (%s)" % st)
    st, cause, _ = scene_rows.deck_cord_per_value(Fw(loaded=False), None)
    check((st, cause) == ("UNMEASURED", "SITE"), "deck driver: without FlowWorks unmeasured (site) (%s %s)" % (st, cause))
    print("PASS" if not fails else "FAIL: %d" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
