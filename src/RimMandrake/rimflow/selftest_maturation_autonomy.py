#!/usr/bin/env python3
"""selftest_maturation_autonomy.py: no mod waits on the Conductor's hand (item
RIMMANDRAKE_AUTOMATE_MATURATION_HAND_STEPS_MODS_SAT_WAITING). Each check is one dispatch tick: a fixture of facts in,
the mod's class (launch / wait / paused / owner) and the launch out. It drives maturation_dispatch.tick only (fake filer,
fake launchers, a temp state folder, a temp root), so on the base it runs and fails check by check (no class, a Needs
Conductor line instead of a launch). Watched failing on c0cec5b054 before the build.

    python3 src/RimMandrake/rimflow/selftest_maturation_autonomy.py       exit 0 when every check prints PASS

The six waits measured 2026-11-15: (1) a locked change with no chain after it, (2) a Designer concept with no record,
(3) an in-game visit owed with the game free, a not-met visit's failed lines routed back and fixed, then the next visit,
a fair queue across mods, (5) is out of scope here (SteveDesktop, its own item), (6) a stall raises maturation.stalled.
Input kinds: no record, a stale exam (locked change newer than the last look), a held game, a dead steward run (spent),
a refused judge (exit not met), an unreadable file (PAUSED, never a crash), a launch that fails, a full slot.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
if os.environ.get("MAT_AUT_BASE_DIR"):      # watch it fail: a folder holding the base maturation_dispatch.py
    sys.path.insert(0, os.environ["MAT_AUT_BASE_DIR"])
import maturation_dispatch as MD    # noqa: E402

CLOCK = 1794750000.0
FAILS = []
CFG = {"enabled": True, "advancing": [], "cap_usd": 15, "max_live": 2, "settle_s": 180, "blind_enabled": True,
       "blind_cap_usd": 20, "blind_auto_cycles_per_visit": 3, "ingame_enabled": True, "ingame_cap_usd": 30,
       "ingame_auto_runs_per_visit": 1, "steward_cap_usd": 5, "fix_cap_usd": 10, "steward_model": "opus",
       "stalled_min": 10, "seat": "BENCH"}


def ok(cond, what):
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


def ingame(mod, owed, visit=1, live=(), why=(), ingame_live=()):
    return {"mod": mod, "stage": "in_game", "version": "0.1.0", "owed": owed, "visit": visit, "live_units": list(live),
            "last_end": None, "ingame_live": list(ingame_live), "ingame_runs": [], "opened": "2026-11-15T01:00:00-08:00",
            "exit": {"state": {"run": "absent", "exit not met": "not_met", "exit met": "met"}.get(owed, owed),
                     "why": list(why) or ["-"], "record": "design/concepts/%s/version/in_game/visit_%d" % (mod, visit)},
            "blocked": []}


def offline(mod, owed, refused=(), hand=()):
    return {"mod": mod, "stage": "offline_build", "version": "0.1.0", "owed": owed, "refused_bars": list(refused),
            "build_refusals": ["every_bar_has_a_check_that_runs"] if refused else [], "hand_steps": list(hand),
            "other_refusals": [], "observed": {}, "live_units": [], "last_end": None, "stage_runs": {}, "run_usd": {},
            "ingame_live": [], "since": "2026-11-15T01:00:00-08:00"}


class World:
    def __init__(self, facts, dstate=None, open_items=None, locked=False, found=(), bridge=(True, "free")):
        self.facts, self.dstate, self.items = facts, dstate or {}, open_items or {}
        self.locked, self.found, self.bridge = locked, list(found), bridge
        self.filed, self.launched, self.briefs, self.cards, self.seeded = [], [], [], [], []
        self.fail_launch = False
        self.dunits = {}
        self.dchain = {}

    def fx(self):
        def launch(mod, cap, item):
            self.launched.append(("stage", mod, item))
            return 0, "DETACHED rm-fake-%d" % len(self.launched), "rm-fake-%d" % len(self.launched)

        def launch_brief(item, text, model, cap, seat):
            self.launched.append(("brief", item, model))
            self.briefs.append(text)
            if self.fail_launch:
                return 1, "LAUNCH FAILED pool full", None
            return 0, "DETACHED rm-fake-%d" % len(self.launched), "rm-fake-%d" % len(self.launched)

        def file(item, title, why, needs="offline"):
            self.filed.append(item)
            return True, "filed %s" % item

        def seed(root, mod):
            self.seeded.append(mod)
            if mod == "Unseedable":
                raise ValueError("its stage cannot be read")
            return "PUBLISHED fake"
        return {"facts": lambda: self.facts, "account": lambda: (True, "ok"), "bridge": lambda p: self.bridge,
                "file": file, "launch": launch, "launch_brief": launch_brief, "known": lambda: set(),
                "open_items": lambda ids: self.items.get(ids[0], []) if self.items is not None else None,
                "designer_state": lambda m: self.dstate.get(m), "designer_unit": lambda m: self.dunits.get(m),
                "designer_chain": lambda m: self.dchain.get(m), "version_locked": lambda m: self.locked,
                "discovered": lambda: self.found, "seed": seed, "card": self.cards.append,
                "page": lambda: type("R", (), {"returncode": 0})()}


def run(world, mods, root, now=CLOCK, cfg=None):
    c = dict(cfg or CFG, advancing=list(mods))
    rd = MD.tick(root, c, True, fx=world.fx(), now=now)
    return rd, (lambda m: (rd["mods"].get(m) or {}))


def fresh_state():
    d = os.environ["RM_MATURATION_DISPATCH_DIR"]
    for f in ("state.json", "reading.json", "ticks.jsonl"):
        if os.path.exists(os.path.join(d, f)):
            os.remove(os.path.join(d, f))


def main():
    if os.environ.get("MAT_AUT_BASE_DIR"):
        print("against the base dispatcher in %s" % os.path.dirname(MD.__file__))
    tmp = tempfile.mkdtemp(prefix="mat_aut_")
    root = os.path.join(tmp, "root")
    os.makedirs(os.path.join(root, "design", "concepts"))
    os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(tmp, "state")
    os.environ["MATURATION_BRIEF_DIR"] = os.path.join(tmp, "briefs")
    os.makedirs(os.environ["RM_MATURATION_DISPATCH_DIR"])
    try:
        # (3) an in-game visit owed, the game free: launch; two owed, one driver: the second waits with a queue position
        fresh_state()
        w = World({"A": ingame("A", "run"), "B": ingame("B", "run")})
        rd, g = run(w, ["A", "B"], root)
        ok(g("A").get("klass") == "launch" and ("stage", "A", "RIMMANDRAKE_DRIVE_A_IN_GAME_ACCEPTANCE_VISIT_ONE")
           in w.launched, "wait 3: an owed visit on a free game launches its live driver (item name ends in a word)")
        ok(g("B").get("klass") == "wait" and g("B").get("queue") == 1,
           "wait 3: the second owed visit waits on the driver with its game-queue position recorded")
        # fairness: B queued first; next tick A is owed again (visit 2) and B, the longer waiter, goes first
        w2 = World({"A": ingame("A", "run", visit=2), "B": ingame("B", "run")})
        rd, g = run(w2, ["A", "B"], root, now=CLOCK + 600)
        ok(g("B").get("klass") == "launch" and g("A").get("klass") == "wait",
           "wait 3: visits queue fairly: the mod queued longest gets the free game, not the first in list order")
        # held game: wait, never a launch
        fresh_state()
        w = World({"A": ingame("A", "run")}, bridge=(False, "OWNER hold"))
        rd, g = run(w, ["A"], root)
        ok(g("A").get("klass") == "wait" and not w.launched, "a held game: wait (bridge held), nothing launched")
        # a refused judge (visit not met): ONE steward run routes the failed lines back
        fresh_state()
        w = World({"A": ingame("A", "exit not met", why=["sc_ruins reads UNMEASURED at 100% of rows"])})
        rd, g = run(w, ["A"], root)
        st = [x for x in w.launched if x[0] == "brief"]
        ok(g("A").get("klass") == "launch" and st and "ROUTE_A_VISIT_ONE_FAILURES_BACK" in st[0][1] and st[0][2] == "opus",
           "wait 5: a not-met visit launches one opus steward run that files the failed lines and routes them back")
        ok(w.briefs and "--caused-by RIMMANDRAKE_ROUTE_A_VISIT_ONE_FAILURES_BACK" in w.briefs[0]
           and "Never certify" in w.briefs[0], "the steward brief files items caused by its own item and forbids "
           "certify/lock/classify")
        # the steward ended, the state did not move: PAUSED, never a second try
        rd, g = run(w, ["A"], root, now=CLOCK + 900)
        ok(g("A").get("klass") == "paused" and len([x for x in w.launched if x[0] == "brief"]) == 1
           and "A: " in " ".join(rd.get("paused") or []), "a dead steward run on an unmoved state: PAUSED, listed for "
           "the alarm, no second launch")
        # the road back: the steward moved A to the offline build and filed two items: one fixer per item
        w.facts = {"A": offline("A", "ready to advance")}
        w.items = {"RIMMANDRAKE_ROUTE_A_VISIT_ONE_FAILURES_BACK": [{"id": "RIMMANDRAKE_FIX_A_RUINS_SCENE_SPAWNS"},
                                                                   {"id": "RIMMANDRAKE_FIX_A_ULLAI_SCENE_READS"}]}
        n0 = len(w.launched)
        rd, g = run(w, ["A"], root, now=CLOCK + 1200)
        ok(g("A").get("klass") == "launch" and w.launched[n0:] == [("brief", "RIMMANDRAKE_FIX_A_RUINS_SCENE_SPAWNS",
                                                                     "opus")],
           "wait 5: an open road-back item gets one fixer run (the existing item, not a new one)")
        # every road-back item closed: the mod moves on (ready to advance -> a steward advance)
        w.items = {"RIMMANDRAKE_ROUTE_A_VISIT_ONE_FAILURES_BACK": []}
        n0 = len(w.launched)
        rd, g = run(w, ["A"], root, now=CLOCK + 1500)
        ok(g("A").get("klass") == "launch" and any("ADVANCE_A_PAST_OFFLINE_BUILD" in x[1] for x in w.launched[n0:]),
           "wait 5: when the road-back items close, ready-to-advance is a steward advance, not a Conductor line")
        ok(not rd.get("needs_conductor"), "no Needs Conductor line for a ready mod")
        # (1) a locked change newer than every look: the chain
        fresh_state()
        ds = {"status": "blocked", "stage": 5, "history": [
            {"at": "2026-11-15T06:14:43Z", "what": "coverage_stop"},
            {"at": "2026-11-15T13:23:41Z", "what": "locked_change", "why": "his card: fix all 12"}]}
        w = World({"P": ingame("P", "exit not met", why=["x"])}, dstate={"P": ds})
        rd, g = run(w, ["P"], root)
        ok(g("P").get("klass") == "launch" and any("RETAKE_P_EXAM_AFTER_LOCKED_CHANGE" in x[1] for x in w.launched),
           "wait 1: a locked change with no look after it launches the chain (re-pin, exam retake, one look)")
        ds2 = dict(ds, history=ds["history"] + [{"at": "2026-11-15T15:00:00Z", "what": "coverage_release"}])
        fresh_state()
        w = World({"P": offline("P", "build", refused=["b1"])}, dstate={"P": ds2})
        rd, g = run(w, ["P"], root)
        ok(not any("RETAKE" in x[1] for x in w.launched), "wait 1: a look after the change: no second chain")
        # (2) a Designer concept with no record is discovered and seeded; a fixture marker keeps one out
        fresh_state()
        os.makedirs(os.path.join(root, "design", "concepts", "Gr"))
        open(os.path.join(root, "design", "concepts", "Gr", "stage.json"), "w").write("{}")
        os.makedirs(os.path.join(root, "design", "concepts", "_fixture"))
        open(os.path.join(root, "design", "concepts", "_fixture", "stage.json"), "w").write("{}")
        open(os.path.join(root, "design", "concepts", "_fixture", ".maturation-exclude"), "w").write("test fixture\n")
        try:
            import maturation_autonomy as AUT
            found = AUT.discovered(root)
        except ImportError as e:
            found = "ImportError: %s" % e
        ok(found == ["Gr"], "wait 2: discovery sees a Designer concept and skips one carrying .maturation-exclude "
           "(read %s)" % found)
        w = World({"Gr": {"mod": "Gr", "stage": "designer", "version": "0.1.0", "live_units": []}},
                  dstate={"Gr": {"status": "waiting_owner", "stage": 5, "history": [{"why": "parked"}],
                                 "pending_decision": "fix gaps"}}, found=found)
        rd, g = run(w, [], root)
        ok(w.seeded == ["Gr"] and "Gr" in rd["mods"], "wait 2: the tick seeds the concept's record and decides on it")
        ok(g("Gr").get("klass") == "owner" and len(w.cards) == 1 and "Gr" in w.cards[0],
           "a Designer turn waiting on him: OWNER, its card text written to the Conductor log")
        rd, g = run(w, [], root, now=CLOCK + 60)
        ok(len(w.cards) == 1, "the owner card is written once, not every tick")
        w = World({}, found=["Unseedable"])
        rd, g = run(w, [], root, now=CLOCK + 120)
        ok(g("Unseedable").get("klass") == "paused", "a concept whose record cannot be seeded: PAUSED, not a crash")
        # his walk: OWNER
        fresh_state()
        w = World({"H": {"mod": "H", "stage": "his_walk", "version": "0.1.0", "live_units": []}})
        rd, g = run(w, ["H"], root)
        ok(g("H").get("klass") == "owner" and not w.launched, "his walk: OWNER, nothing launched")
        # an unreadable designer state: PAUSED
        w = World({"U": {"mod": "U", "stage": "designer", "version": "0.1.0", "live_units": []}}, dstate={})
        rd, g = run(w, ["U"], root)
        ok(g("U").get("klass") == "paused", "an unreadable stage.json: PAUSED, not a crash")
        # exit met: a steward confirmation run, not a hand step
        fresh_state()
        w = World({"A": ingame("A", "exit met", why=["all rows PASS"])})
        rd, g = run(w, ["A"], root)
        ok(any("CONFIRM_A_VISIT_ONE_EXIT_MET" in x[1] for x in w.launched), "an exit met: a steward reads and confirms")
        # a failed steward launch: PAUSED, not retried
        fresh_state()
        w = World({"A": offline("A", "hand step", hand=["walk_bars_confirmed"])})
        w.fail_launch = True
        rd, g = run(w, ["A"], root)
        rd, g = run(w, ["A"], root, now=CLOCK + 60)
        ok(g("A").get("klass") == "paused" and len(w.launched) == 1, "a failed steward launch: PAUSED, never retried")
        # full slots: wait
        fresh_state()
        f = offline("A", "ready to advance")
        f["live_units"] = []
        w = World({"A": f, "L1": dict(offline("L1", "build", ["x"]), live_units=["rm-u1"]),
                   "L2": dict(offline("L2", "build", ["y"]), live_units=["rm-u2"])})
        rd, g = run(w, ["L1", "L2", "A"], root)
        ok(g("A").get("klass") == "wait" and g("L1").get("waits_on") == "rm-u1",
           "two live runs fill the slots: the steward waits; a live mod waits on its named unit")
        # (6) a stall: a wait with nothing running for 10 minutes
        fresh_state()
        w = World({"D": {"mod": "D", "stage": "designer", "version": "0.1.0", "live_units": []}},
                  dstate={"D": {"status": "ready", "stage": 2, "history": []}})
        rd, g = run(w, ["D"], root)
        ok(not rd.get("stalled"), "a fresh Designer wait is not a stall yet")
        rd, g = run(w, ["D"], root, now=CLOCK + 660)
        ok(rd.get("stalled") == ["D"], "wait 6: nothing running on it for 10 minutes: maturation.stalled names it")
        w.dunits = {"D": "rm-role-designer-7"}
        rd, g = run(w, ["D"], root, now=CLOCK + 720)
        ok(not rd.get("stalled") and g("D").get("waits_on") == "rm-role-designer-7",
           "a live Designer role run on the concept: wait on that unit, not a stall")
        # stalled blind spot 1: the Designer run ends; the stall counts from its end, not from the first wait
        w.dunits = {}
        rd, g = run(w, ["D"], root, now=CLOCK + 780)
        ok(not rd.get("stalled") and g("D").get("for_min") == 0,
           "stalled 1: a Designer run that just ended restarts the clock (read for_min %s, stalled %s)" % (
               g("D").get("for_min"), rd.get("stalled")))
        rd, g = run(w, ["D"], root, now=CLOCK + 780 + 660)
        ok(rd.get("stalled") == ["D"], "stalled 1: 11 minutes with nothing running after the run ended: stalled")
        # stalled blind spot 2: the Designer chain daily cap is named, PAUSED, with its cure
        fresh_state()
        w = World({"G": {"mod": "G", "stage": "designer", "version": "0.1.0", "live_units": []}},
                  dstate={"G": {"status": "ready", "stage": 3, "history": []}})
        w.dchain = {"G": (8, 8)}
        rd, g = run(w, ["G"], root)
        ok(g("G").get("klass") == "paused" and "chain_max_per_day" in str(g("G").get("status"))
           and "run-now --role Designer --concept design/concepts/G" in str(g("G").get("status")),
           "stalled 2: a concept at the Designer's daily chain cap reads PAUSED naming the cap and the run-now cure "
           "(read %s)" % str(g("G").get("status"))[:120])
        w.dchain = {"G": (3, 8)}
        rd, g = run(w, ["G"], root, now=CLOCK + 60)
        ok(g("G").get("decision") == "designer_wait", "stalled 2: under the cap it is still a Designer wait")
        # stalled blind spot 3: a coverage stop pauses the mod on the judge stop, never slots_full or a launch
        fresh_state()
        stop = {"status": "blocked", "stage": 5, "blocked_on": "REFUSAL_NOTHING_COULD_EVER_PASS: judging stopped",
                "history": [{"at": "2026-11-15T13:54:40Z", "what": "locked_change"},
                            {"at": "2026-11-15T13:56:22Z", "what": "coverage_release"},
                            {"at": "2026-11-15T14:05:35Z", "what": "coverage_stop", "why": "round 6 not_covered"}]}
        w = World({"P": offline("P", "ready to advance"), "L1": dict(offline("L1", "build", ["x"]), live_units=["rm-u1"]),
                   "L2": dict(offline("L2", "build", ["y"]), live_units=["rm-u2"])}, dstate={"P": stop})
        rd, g = run(w, ["L1", "L2", "P"], root)
        ok(g("P").get("klass") == "paused" and g("P").get("decision") == "coverage_stop"
           and "coverage_judge.py release" in str(g("P").get("status")),
           "stalled 3: a coverage-stopped mod reads PAUSED on the judge stop, not slots_full (read %s)" % g("P").get(
               "decision"))
        fresh_state()
        w = World({"P": offline("P", "build", refused=["b1"])}, dstate={"P": stop})
        rd, g = run(w, ["P"], root)
        ok(not w.launched and g("P").get("decision") == "coverage_stop",
           "stalled 3: a coverage-stopped mod is never launched on (read %s, launched %s)" % (
               g("P").get("decision"), w.launched))
        # every class is one of four, on every row of every tick above
        ok(all(m.get("klass") in ("launch", "wait", "paused", "owner") for m in rd["mods"].values()),
           "every row has one of the four classes")
        # the ops_watch side: the alarm targets and the route exist
        rules = json.load(open(os.path.join(HERE, "..", "Utils", "ops_watch_rules.json")))
        names = {t.get("name"): t.get("key") for t in rules.get("targets") or []}
        ok(names.get("OPS_MATURATION_MOD_PAUSED") == "maturation.paused"
           and names.get("OPS_MATURATION_MOD_STALLED") == "maturation.stalled",
           "ops_watch_rules.json carries the two fixed alarms (paused, stalled)")
        routes = json.load(open(os.path.join(HERE, "alarm_routes.json")))
        rs = routes.get("routes", routes) if isinstance(routes, dict) else routes
        ok("maturation.stalled" in json.dumps(rs), "alarm_routes.json routes maturation.stalled")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
