"""Behavioural selftest for watch.py + the suite/runner wiring, on rimdrive.fake.FakeWorld.

Asserts what happens to the WORLD and to the RECORD: a raid inside a wait stops the wait at the chunk
and leaves evidence; the budget refuses before spending; the game ends paused; settings come back.
Every check has a control (the quiet run) proving the harness does not cry wolf.
Run: python3 selftest_watch.py
"""
import json
import os
import shutil
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

import clockgate                                       # noqa: E402
import runner                                          # noqa: E402
from rimdrive.fake import FakeWorld, pawn_row          # noqa: E402
from suite import Suite, TestContext                   # noqa: E402
from watch import Watch, SurpriseAbort                 # noqa: E402

_results = []


def check(name, cond, detail=""):
    _results.append(bool(cond))
    print("%s %s%s" % ("ok  " if cond else "FAIL", name, ("  -- " + detail) if (detail and not cond) else ""))


def bland_world(tmp):
    w = FakeWorld(pawns=[pawn_row("Col1"), pawn_row("Col2", x=103), pawn_row("Col3", x=106)])
    w.shot_dir = tmp
    return w


def raid(world):
    world.stats["numRaidsEnemy"] += 1
    world.letters.append({"defName": "ThreatBig", "label": "Raid: Buton", "arrivalTick": world.ticks})
    world.pawns["Raider9"] = pawn_row("Raider9", kind="Tribal_Berserker", faction="TribeRough",
                                      is_player=False, hostile=True, x=110, z=110)


def main():
    tmp = tempfile.mkdtemp(prefix="np_watch_")
    try:
        # ---- control: a quiet wait is quiet, budgeted, paused, and restores settings
        w = bland_world(tmp)
        before = dict(w.debug)
        with Watch(w, (100, 100), tmp, mod="M", chain="quiet", chunk=600) as wt:
            r = wt.wait(None, 2000)
        check("quiet wait advances the real ticks", w.ticks == 2000 and r["advanced"] == 2000, str(w.ticks))
        check("quiet wait: zero captures and zero serious hits",
              not wt.captures and not [h for h in wt.seen_hits if h["severity"] in ("SURPRISE", "FATAL")], str(wt.seen_hits))
        check("quiet wait swept every chunk (>=3 sweeps for 2000/600)", wt.sweeps >= 3, str(wt.sweeps))
        check("game left verified paused", w.paused and clockgate.verify_pause(w))
        check("debug settings restored exactly", w.debug == before, str(w.debug))
        check("ticks_spent matches the measured clock", wt.summary()["ticks_spent"] == 2000, str(wt.summary()["ticks_spent"]))

        # ---- a raid inside the wait stops it at the chunk, with evidence
        w = bland_world(tmp)
        w.at(1000, raid)
        with Watch(w, (100, 100), tmp, mod="M", chain="raid", chunk=600) as wt:
            try:
                wt.wait(None, 2600)
                aborted = None
            except SurpriseAbort as e:
                aborted = e
        check("a raid inside a wait aborts it", aborted is not None and aborted.kind == "surprise")
        check("it stops at the chunk boundary, not the full 2600 (<=1200)", w.ticks <= 1200, str(w.ticks))
        caps = wt.captures
        check("exactly one evidence capture for the sweep", len(caps) == 1)
        side = json.load(open(caps[0]["sidecar"]))
        check("sidecar names the detectors and carries the ledger",
              {h["detector"] for h in side["hits"]} >= {"raid_arrived"} and side["ledger"] is not None
              and side["snapshot"]["tick"] == w.ticks, str([h["detector"] for h in side["hits"]]))
        check("a real PNG was captured and verified", caps[0]["png"] and caps[0]["png_info"]["ok"], str(caps[0]["notes"]))
        check("the PNG sits next to its sidecar", os.path.dirname(caps[0]["png"]) == os.path.dirname(caps[0]["sidecar"]) and os.path.exists(caps[0]["png"]))
        check("the raiders were NOT touched (evidence before action)", not w.pawns["Raider9"]["dead"])
        check("paused after the abort", w.paused)

        # ---- a colonist death is FATAL
        w = bland_world(tmp)
        w.at(700, lambda world: world.kill("Col2"))
        with Watch(w, (100, 100), tmp, mod="M", chain="death", chunk=600) as wt:
            try:
                wt.wait(None, 3000)
                err = None
            except SurpriseAbort as e:
                err = e
        check("a colonist death aborts and names colonist_died",
              err is not None and any(h.detector == "colonist_died" and h.severity == "FATAL" for h in err.hits))

        # ---- the budget refuses BEFORE spending anything
        w = bland_world(tmp)
        with Watch(w, (100, 100), tmp, mod="M", chain="budget", chunk=600, session_cap=60000) as wt:
            try:
                wt.wait(None, 95000)
                err = None
            except SurpriseAbort as e:
                err = e
        check("an over-cap wait is refused as a harness abort with zero ticks spent",
              err is not None and err.kind == "harness" and w.ticks == 0 and "BudgetExceeded" in str(err), str(err))

        # ---- a stalled clock is a harness abort, not a hang
        w = bland_world(tmp)
        w.modes.add("step_zero")
        with Watch(w, (100, 100), tmp, mod="M", chain="stall", chunk=600) as wt:
            try:
                wt.wait(None, 1200)
                err = None
            except SurpriseAbort as e:
                err = e
        check("a stalled step_game_ticks aborts as harness", err is not None and err.kind == "harness" and "ClockStall" in str(err))

        # ---- policy 'record' keeps going and does not screenshot-storm
        w = bland_world(tmp)
        w.at(300, raid)
        with Watch(w, (100, 100), tmp, mod="M", chain="rec", chunk=300, policy="record") as wt:
            wt.wait(None, 2400)
        check("record policy runs the full wait", w.ticks == 2400)
        check("record policy captures once (dedup), not every chunk", len(wt.captures) == 1, str(len(wt.captures)))

        # ---- E6: a verb that moves the clock behind its back
        w = bland_world(tmp)
        def order_pawn(**p):
            w._t_rimworld_step_game_ticks(ticks=18000)
            return {"success": True}
        w._t_jawa_order_pawn = order_pawn
        with Watch(w, (100, 100), tmp, mod="M", chain="e6", chunk=600, session_cap=60000) as wt:
            ctx = TestContext(w, anchor=(100, 100), watch=wt)
            with ctx.component("walk") as c:
                ctx.order_to("Col1", (110, 110))
        comp = ctx.components[0]
        check("a non-wait verb that moves 18000 ticks aborts as clock_runaway (E6), UNMEASURED not FAIL",
              comp.verdict == "UNMEASURED" and "clock_runaway" in comp.detail, "%s | %s" % (comp.verdict, comp.detail))

        # ---- a DELIBERATE warp by name (jawa/time_set_ticks) is not a runaway (LIVE 2026-10-03, LeaningScrub)
        w = bland_world(tmp)
        def time_set_ticks(**p):
            w._t_rimworld_step_game_ticks(ticks=18000)
            return {"success": True}
        w._t_jawa_time_set_ticks = time_set_ticks
        with Watch(w, (100, 100), tmp, mod="M", chain="warp", chunk=600, session_cap=60000) as wt:
            ctx = TestContext(w, anchor=(100, 100), watch=wt)
            with ctx.component("warp") as c:
                ctx.bridge_call("jawa/time_set_ticks", ticks=18000)
        comp = ctx.components[0]
        check("a named time_set_ticks warp is re-based, not aborted as clock_runaway",
              "clock_runaway" not in (comp.detail or ""), "%s | %s" % (comp.verdict, comp.detail))

        # ---- through TestContext: surprise -> UNMEASURED, no finding, later components inherit the reason
        w = bland_world(tmp)
        w.at(500, raid)
        findings = []
        with Watch(w, (100, 100), tmp, mod="M", chain="ctx", chunk=600) as wt:
            ctx = TestContext(w, anchor=(100, 100), on_finding=findings.append, watch=wt)
            with ctx.component("first"):
                ctx.wait_ticks(2000)
            with ctx.component("second"):
                ctx.wait_ticks(10)
        v = [c.as_dict() for c in ctx.components]
        check("surprise component is UNMEASURED with evidence named, never FAIL",
              v[0]["verdict"] == "UNMEASURED" and v[0]["surprises"]["evidence"] and not findings, str(v[0]["detail"])[:200])
        check("the next component inherits the reason and spends no time", v[1]["verdict"] == "UNMEASURED" and "surprise" in v[1]["detail"])

        # ---- fixtures: the test's own pawn dying is not a surprise
        w = bland_world(tmp)
        with Watch(w, (100, 100), tmp, mod="M", chain="fix", chunk=600) as wt:
            ctx = TestContext(w, anchor=(100, 100), watch=wt)
            pid = ctx.spawn_pawn("Colonist", hostile=False)
            w.at(w.ticks + 300, lambda world: world.kill(pid))
            with ctx.component("kills its own walker"):
                ctx.wait_ticks(1200)
        check("a test-spawned player pawn dying inside a wait does not abort",
              ctx.components[0].verdict == "PASS" and not wt.captures, str(ctx.components[0].as_dict()["detail"]))

        # ---- a pawn spawned through bridge_call is a fixture too (measured: Droidworks spawns this way)
        w = bland_world(tmp)
        with Watch(w, (100, 100), tmp, mod="M", chain="bc", chunk=600) as wt:
            ctx = TestContext(w, anchor=(100, 100), watch=wt)
            with ctx.component("spawns via the escape valve"):
                r = ctx.bridge_call("jawa/spawn_pawn", kindDef="Colonist", x=100, z=100, faction="player")
                pid = r["pawns"][0]["id"]
                w.at(w.ticks + 200, lambda world: world.kill(pid))
                ctx.wait_ticks(900)
        check("bridge_call spawn_pawn registers a fixture: its death is not a surprise", ctx.components[0].verdict == "PASS" and pid in wt.fixture_ids, str(ctx.components[0].as_dict()["detail"]))

        # ---- run_suite end to end: a map that cannot be made bland is UNMEASURED, not a mod FAIL
        w = bland_world(tmp)
        w.pawns["Raider1"] = pawn_row("Raider1", kind="Tribal_Berserker", faction="TribeRough", is_player=False, hostile=True)
        w.modes.add("kill_noop")
        st = Suite("Probe")
        @st.chain("c1")
        def c1(t):
            with t.component("never reached"):
                t.wait_ticks(600)
        runner.SHEET_DIR = tmp
        out = runner.run_suite(st, w, anchor=(100, 100), situational=True)
        comp = out["chains"][0]["components"][0]
        check("unestablishable bland map => component UNMEASURED naming the cause, not FAIL",
              comp["verdict"] == "UNMEASURED" and "bland map" in comp["detail"] and w.ticks == 0, str(comp))
        check("summary carries the situational block", out["chains"][0]["situational"]["bland"] is False)
        w = bland_world(tmp)
        st2 = Suite("Probe2")
        @st2.chain("c1")
        def c2(t):
            with t.component("quiet"):
                t.wait_ticks(1200)
        out = runner.run_suite(st2, w, anchor=(100, 100), situational=True)
        check("run_suite situational on a clean map: PASS and a summary", out["all_green"] and out["chains"][0]["situational"]["sweeps"] >= 2)
        out2 = runner.run_suite(st2, bland_world(tmp), anchor=(100, 100), situational=False)
        check("situational=False leaves the old behaviour (no summary block)", out2["chains"][0]["situational"] is None)
        # ---- chain 2 must not be poisoned by chain 1's own torn-down walker (E1 root cause)
        w = bland_world(tmp)
        st3 = Suite("Probe3")
        @st3.chain("c1")
        def p1(t):
            pid = t.spawn_pawn("Colonist", hostile=False)
            with t.component("spawns a walker"):
                pass
        @st3.chain("c2")
        def p2(t):
            with t.component("runs after teardown"):
                t.wait_ticks(600)
        orig_sweep = w.sweep
        def killing_sweep():
            for l in list(w.litter):
                if l["kind"] == "pawn":
                    w.kill(l["id"])
            w.litter = []
            return {"swept": 1, "left": []}
        w.sweep = killing_sweep
        out = runner.run_suite(st3, w, anchor=(100, 100), situational=True)
        ok2 = out["chains"][1]["components"][0]["verdict"]
        check("chain 2 runs (PASS) after chain 1's litter teardown killed its own walker", ok2 == "PASS" and out["chains"][1]["situational"]["bland"], str(out["chains"][1]["situational"]["bland_problems"]))
        # ---- a failed check OUTSIDE any component must not kill the run (measured: Droidworks salvage_on_death)
        w = bland_world(tmp)
        st4 = Suite("Probe4")
        @st4.chain("setup_fails")
        def s1(t):
            t.expect_pawn_despawned("Col1")            # still on the map -> ExpectationFailed outside a component
            with t.component("never runs"):
                pass
        @st4.chain("next_chain_still_runs")
        def s2(t):
            with t.component("ran"):
                t.wait_ticks(300)
        out = runner.run_suite(st4, w, anchor=(100, 100), situational=True)
        c0 = out["chains"][0]["components"][0]
        check("an out-of-component failure is recorded as a FAIL component, not a crash",
              c0["verdict"] == "FAIL" and "outside any component" in c0["name"] and out["findings"], str(c0))
        check("the next chain still runs and passes", out["chains"][1]["components"][0]["verdict"] == "PASS")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    n = sum(_results)
    print("\n%d/%d passed" % (n, len(_results)))
    return 0 if n == len(_results) else 1


if __name__ == "__main__":
    sys.exit(main())
