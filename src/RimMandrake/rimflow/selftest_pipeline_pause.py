#!/usr/bin/env python3
"""selftest_pipeline_pause.py: the pipeline's pause switch and its "up next" forecast, offline, in a temp tree.

Item RIMMANDRAKE_ADD_PAUSE_ALL_AND_UP_NEXT_HOLD_LEAKED. The owner, 2026-11-18 ~10:27 AM PST: "I think we may need to have
Dispatch have a "pause all pipeline items" setting we can easily toggle (non-code-editing) ... And perhaps some kind of
"up next" feature we can ping that says what WILL happen in some amount of time if we do nothing, so we can confirm
using its own code..." Written with the code and watched failing on the base (no pipeline_pause module, no pause /
next verbs, `disabled` counted paused).

The tick's decision layer is replaced by one launch row per tick layer of the census
(design/RimMandrake/pipeline_launch_paths_census_2026-11-18.md, T1 to T9) plus a mod whose run is settling and one with
a live run; everything after the decision (prioritise, the pause gate, the dry/apply split, classify, the reading) is
the real code, and execute is a recorder: what the tick hands execute is what it launches.

What it proves: the forecast's first predicted launch per layer equals what a following `tick --apply` hands execute,
at the moment the forecast named (a settle timer and a pause's --until included), and a forecast with any one layer
dropped fails that comparison; pause all blocks every tick layer, the Dispatcher's pipeline roles (pipeline_held, the
gate owner_held and the launch point read) and red_dispatch; a per-mod pause blocks that mod only; a live run is left
alone without --stop-live and stopped and recorded for voiding with it; no idle, paused or stalled reading while
paused, and `enabled: false` is no paused alarm either; an expired --until resumes by itself and says so; an unreadable
or misshapen pause file reads PAUSED and resume refuses over it; `rimflow pipeline` and the status page show it.

    python3 src/RimMandrake/rimflow/selftest_pipeline_pause.py      exit 0 when every check prints PASS
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "Utils"))
FAILS = []
CLOCK = 1795000000.0
SETTLE_AT = CLOCK + 420
# mod -> the launch row of one tick layer (the census's T1..T9)
PATHS = {
    "ModBuild": {"stage": "offline_build"},
    "ModBlind": {"stage": "blind_challenge"},
    "ModGame": {"stage": "in_game", "stage_usd": 0},
    "ModRed": {"stage": "offline_build", "cert_reds": ["T_RED"]},
    "ModRerun": {"stage": "offline_build", "cert_rerun_key": "k1"},
    "ModHolder": {"stage": "blind_challenge", "holder_items": ["ITEM_ONE"]},
    "ModSteward": {"stage": "blind_challenge", "aut": "steward", "steward_key": "v|exit"},
    "ModFixer": {"stage": "offline_build", "aut": "fixer", "fix_item": "FIX_ONE"},
    "ModLock": {"stage": "preflight", "aut": "autolock", "steward_key": "v|lock"},
}
MODS = list(PATHS) + ["ModSettle", "ModLive", "ModIdle"]


def ok(cond, what):
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


def main():
    try:
        import pipeline_pause as PP
        import maturation_dispatch as MD
        import maturation_autonomy as AUT
        import role_launch as RL
        import red_dispatch as RD
    except ImportError as e:
        ok(False, "the pause store and its readers import (%s)" % e)
        return 1
    root = tempfile.mkdtemp(prefix="pipeline_pause_")
    keys = ("RM_MATURATION_DISPATCH_DIR", "RM_PIPELINE_PAUSE_FILE")
    was = {k: os.environ.get(k) for k in keys}
    sd, pf = os.path.join(root, "state"), os.path.join(root, "state", "pause.json")
    os.environ.update(RM_MATURATION_DISPATCH_DIR=sd, RM_PIPELINE_PAUSE_FILE=pf)
    saved = {n: getattr(MD, n) for n in ("decide", "execute", "record_spend", "end_ledger_runs", "book_refunds",
                                         "slow_chores", "stop_live")}
    saved_aut = AUT.execute
    executed, stops = [], []

    def fake_decide(cfg, st, facts, now, account=(True, ""), bridge=None, releases=None):
        rows, launches = [], []
        for mod in cfg["advancing"]:
            st.setdefault("mods", {}).setdefault(mod, {})
            if mod == "ModLive":
                rows.append({"mod": mod, "stage": "offline_build", "decision": "live", "why": "a run is live",
                             "live": ["rm-detached-fake-live"]})
            elif mod == "ModIdle":
                rows.append({"mod": mod, "stage": "offline_build", "decision": "slots_full", "owed": "build",
                             "idle_min": 999, "why": "no free slot", "waits_on": "a free slot"})
            elif mod == "ModSettle" and now < SETTLE_AT:
                rows.append({"mod": mod, "stage": "offline_build", "decision": "settling", "why": "a run ended"})
            else:
                rows.append(dict({"mod": mod, "decision": "launch", "why": "work owed", "owed": "build"},
                                 **PATHS.get(mod, {"stage": "offline_build"})))
                launches.append(mod)
        return rows, launches

    def rec_execute(root_, cfg, st, rows, launches, now, fx=None):
        for r in rows:
            if r["mod"] in launches:
                executed.append(r["mod"])
                r.update(decision="launched", unit="rm-fake-%s" % r["mod"])

    def no_stop(*a, **k):
        stops.append(("tick", a))
        return []
    MD.decide, MD.execute, AUT.execute = fake_decide, rec_execute, rec_execute
    MD.record_spend = MD.end_ledger_runs = lambda *a, **k: "off in the selftest"
    MD.book_refunds = lambda *a, **k: None
    MD.slow_chores = lambda *a, **k: None
    MD.stop_live = no_stop
    facts = {m: {"mod": m, "live_units": ["rm-detached-fake-live"] if m == "ModLive" else []} for m in MODS}
    fx = {"autonomy": False, "convergence": lambda root_, rd: rd.update(convergence={}), "facts": lambda: facts,
          "account": lambda: (True, "test"), "releases": lambda: ([], 0), "code": lambda: "tree0", "known": lambda: set(),
          "clone": lambda: (0, 0), "hands": None, "rescue": None}
    cfg = dict(MD.load_cfg(), advancing=list(MODS), enabled=True, max_live=99)

    def tick(at, apply=True):
        del executed[:]
        rd = MD.tick(root, cfg, apply, fx=fx, now=CLOCK + at, page=False)
        return list(executed), rd

    import control as C     # `pause` writes the control store (control.py); each fresh() gets an empty one

    def fresh():
        shutil.rmtree(sd, ignore_errors=True)
        os.makedirs(sd)
        os.environ["RM_CONTROL_DB"] = os.path.join(sd, "control.db")
        C.init(os.environ["RM_CONTROL_DB"])

    def at_first(fc, t):
        return sorted(x["mod"] for x in fc["launches"] if x["at"] == t)

    try:
        # ---- the forecast equals the tick, per layer --------------------------------------------------------------
        fresh()
        fc = MD.forecast(root, cfg, within_s=600, step_s=60, fx=fx, now=CLOCK)
        got0, rd0 = tick(0)
        pred0 = at_first(fc, CLOCK)
        ok(pred0 == sorted(got0) and set(PATHS) <= set(got0),
           "forecast at now = what tick --apply hands execute, every layer T1..T9 (%s vs %s)" % (pred0, sorted(got0)))
        for mod in PATHS:
            ok(mod in pred0 and mod in got0, "layer %s (%s): forecast and tick both launch it" % (
                mod, PATHS[mod].get("aut") or PATHS[mod].get("stage")))
        st_ = next((x for x in fc["launches"] if x["mod"] == "ModSettle"), None)
        ok(st_ is not None and st_["at"] == SETTLE_AT, "the settle timer: forecast names %s for ModSettle (%s)" % (
            MD.pac(SETTLE_AT), st_ and MD.pac(st_["at"])))
        fresh()
        early, _ = tick(SETTLE_AT - CLOCK - 60)
        fresh()
        late, _ = tick(SETTLE_AT - CLOCK)
        ok("ModSettle" not in early and "ModSettle" in late, "tick --apply launches ModSettle at the forecast's "
           "minute, not the minute before")
        kinds = {x["mod"]: x["launch"] for x in fc["launches"]}
        ok(kinds["ModGame"]["model"] == cfg.get("ingame_model", "opus") and kinds["ModRerun"]["model"].startswith(
            "none") and kinds["ModLock"]["kind"] == "autolock" and kinds["ModFixer"]["kind"] == "fixer"
           and kinds["ModHolder"]["kind"] == "holder", "each prediction names its kind, model and rule")
        ok(any("UNMEASURED" in u and "ModLive" in u for u in fc["unmeasured"]),
           "a live run's end reads UNMEASURED, never nothing")
        # a mutated forecast that loses one layer (its dry tick's rows of that kind dropped) must fail the comparison
        real_tick = MD._tick

        def mutant(kind):
            def t(root_, cfg_, apply, fx=None, now=None, page=True):
                rd_ = real_tick(root_, cfg_, apply, fx, now, page)
                if not apply:
                    for r_ in rd_["mods"].values():
                        if r_.get("decision") == "would_launch" and (r_.get("launch") or {}).get("kind") == kind:
                            r_["decision"] = "dropped_by_mutant"
                return rd_
            return t
        try:
            for mod in PATHS:
                MD._tick = mutant(kinds[mod]["kind"])
                fresh()
                fm = MD.forecast(root, cfg, within_s=60, step_s=60, fx=fx, now=CLOCK)
                MD._tick = real_tick
                fresh()
                gm, _ = tick(0)
                ok(at_first(fm, CLOCK) != sorted(gm), "a forecast mutated to lose layer %s (%s) fails the comparison"
                   % (mod, kinds[mod]["kind"]))
        finally:
            MD._tick = real_tick
        # the holder cap: what execute's holder_launch will set, by the one rule
        pl_was = MD.pilot_ledger
        MD.pilot_ledger = lambda root_, mod: mod == "ModGame"
        try:
            k = MD.launch_kind(dict(cfg, stage_ceiling_usd=60, ingame_cap_usd=30), {"mod": "ModGame", "stage": "in_game",
                                                                                  "stage_usd": 0}, root)
        finally:
            MD.pilot_ledger = pl_was
        ok(k["cap_usd"] == 60 == MD.holder_cap(dict(cfg, stage_ceiling_usd=60), {"stage_usd": 0}, 30),
           "a pilot holder's forecast cap is holder_cap's, as execute sets it (%s)" % k["cap_usd"])
        # the stale-clone gate reads alike in the dry pass
        fresh()
        fst = MD.forecast(root, cfg, within_s=120, step_s=60, fx=dict(fx, clone_seen={
            "measured": True, "behind_min": 10, "ahead": 0, "behind": 3, "behind_since": CLOCK - 600}), now=CLOCK)
        ok(fst["launches"] == [] and any(b["decision"] == "stale_clone" for b in fst["blocked"]),
           "a stale dispatch clone: the forecast predicts no launch, as the applying tick would refuse")
        for bad_step in (-60, 0):
            try:
                MD.forecast(root, cfg, within_s=120, step_s=bad_step, fx=fx, now=CLOCK)
                ok(False, "--step %s is refused" % bad_step)
            except ValueError:
                ok(True, "--step %s is refused" % bad_step)
        # the clone gate ages on the forecast's clock: behind 4 min at the last tick, past the 5 min line 2 min later
        fresh()
        seen = {"measured": True, "behind": 3, "ahead": 0, "behind_since": CLOCK - 200, "behind_min": 3.3, "at": CLOCK}
        fca = MD.forecast(root, cfg, within_s=120, step_s=60, fx=dict(fx, clone_seen=seen), now=CLOCK)
        PP.pause(None, "clone age", "TEST", until=CLOCK + 180, now=CLOCK)
        fcb = MD.forecast(root, cfg, within_s=300, step_s=60, fx=dict(fx, clone_seen=seen), now=CLOCK)
        PP.resume(None, "clone age", "TEST", now=CLOCK)
        ok(fca["launches"] and fcb["launches"] == [] and any(b["decision"] == "stale_clone" for b in fcb["blocked"]),
           "the forecast's clone gate ages: 3.3 min behind launches now; a pause ending at +3 min meets a clone 6.3 min "
           "behind, so nothing launches, as the applying tick would refuse")
        # the forecast reads each mod's walk_owed once, as it reads the facts once: the read does not move with its
        # clock (2026-11-25: 31 simulated ticks of about 50 s each kept `next --within 30m` past 30 minutes)
        import maturation as M_
        wcalls, wo_was, tick_was = [], M_.walk_owed, MD._tick

        def counting_wo(root_, mod, rec=None):
            wcalls.append(mod)
            return {"owed": {}, "why": []}

        def tick_reads_walk(root_, cfg_, apply, fx=None, now=None, page=False):
            (fx.get("walk_owed") or M_.walk_owed)(root_, "ModWalk")
            return {"mods": {}}
        M_.walk_owed, MD._tick = counting_wo, tick_reads_walk
        try:
            fresh()
            MD.forecast(root, cfg, within_s=600, step_s=60, fx=dict(fx), now=CLOCK)
        finally:
            M_.walk_owed, MD._tick = wo_was, tick_was
        ok(wcalls == ["ModWalk"], "the forecast reads a mod's walk_owed once over its 11 simulated ticks (%d reads)"
           % len(wcalls))

        # ---- pause all ------------------------------------------------------------------------------------------
        fresh()
        idle_base = tick(0)[1]
        ok("ModIdle" in (idle_base.get("idle_owed_mods") or []), "the idle reading fires unpaused (it can see)")
        fresh()
        PP.pause(None, "selftest stop", "TEST", now=CLOCK)
        got, rd = tick(0)
        ok(got == [], "pause all: tick --apply hands execute nothing (%s)" % got)
        ok(all(rd["mods"][m]["decision"] == "pipeline_paused" and rd["mods"][m].get("klass") == "planned"
               for m in PATHS), "pause all: every layer's row reads pipeline_paused, class planned")
        ok(rd["mods"]["ModLive"]["decision"] == "live" and not stops, "pause all: the live run is untouched")
        ok(not rd.get("idle_owed_mods") and not rd.get("paused") and not rd.get("stalled"),
           "pause all: no idle, paused or stalled reading (%s / %s / %s)" % (
               rd.get("idle_owed_mods"), rd.get("paused"), rd.get("stalled")))
        ok("selftest stop" in str((rd.get("pipeline_pause") or {}).get("all")), "the reading carries why, who, until")
        fcp = MD.forecast(root, cfg, within_s=600, step_s=60, fx=fx, now=CLOCK)
        ok(fcp["launches"] == [] and any("NOTHING WILL START" in x for x in MD.forecast_lines(fcp)),
           "the forecast under pause says nothing will start, explicitly")
        ok(any("nothing starts" in x for x in MD.forecast_roles(CLOCK, 600, {"roles": [
            {"name": "Designer", "chain_stages": True, "enabled": True}]})), "the forecast's Designer line is paused")
        # the Dispatcher's pipeline roles and red_dispatch
        acts = []
        rs = {}
        ok(RL.pipeline_held("Designer", rs, None, CLOCK, lambda **k: acts.append(k)), "pause all: a pipeline role's "
           "launch point is held (pipeline_held, concept None)")
        ok(RL.pipeline_held("Designer", rs, "design/concepts/ModBuild", CLOCK, lambda **k: acts.append(k)),
           "pause all: a concept's chain or run-now is held")
        ok(RL.owner_held("Designer", {}, "design/concepts/ModBuild", CLOCK, lambda **k: acts.append(k)),
           "pause all: owner_held (chain_next, chain_sweep, run-now) holds")
        ok(all(a.get("do") == "role_hold" for a in acts), "a pause is a role_hold note, never an alarm")
        n = len(acts)
        RL.pipeline_held("Designer", rs, None, CLOCK + 60, lambda **k: acts.append(k))
        ok(len(acts) == n, "said once a day per scope")
        src = open(os.path.join(HERE, "role_launch.py")).read()
        ok('cfg.get("chain_stages") is True and pipeline_held(' in src, "decide_roles' launch point reads the pause "
           "for pipeline roles (slots and resumes)")
        rf = {"reds": [{"item": "RED_ONE", "tests": ["t"], "due": 0, "said": []}], "items": {"RED_ONE": {
            "state": "open", "owner": None, "blocked": False}}, "runs": {}, "night": None}
        rrows, rl = RD.decide({"enabled": True, "max_live": 2}, {}, rf, CLOCK)
        ok(rl == [] and rrows[0]["decision"] == "pipeline_paused", "pause all: red_dispatch launches nothing (%s)" %
           rrows[0].get("decision"))
        PP.resume(None, "selftest", "TEST", now=CLOCK + 1)
        rrows, _ = RD.decide({"enabled": True, "max_live": 2}, {}, rf, CLOCK)
        ok(rrows[0]["decision"] != "pipeline_paused", "resumed: red_dispatch decides as before (%s)" %
           rrows[0].get("decision"))

        # ---- enabled: false is a planned stop too ----------------------------------------------------------------
        fresh()
        del executed[:]
        rd = MD.tick(root, dict(cfg, enabled=False), True, fx=fx, now=CLOCK, page=False)
        ok(executed == [] and not rd.get("paused") and rd["mods"]["ModBuild"].get("klass") == "planned",
           "enabled: false launches nothing and raises no paused reading (%s)" % rd.get("paused"))

        # ---- one mod ---------------------------------------------------------------------------------------------
        fresh()
        PP.pause("ModBuild", "one mod", "TEST", now=CLOCK)
        del executed[:]
        MD.tick(root, dict(cfg, advancing=["ModBuild", "ModBlind"], max_live=1), True, now=CLOCK, page=False,
                fx=dict(fx, facts=lambda: {m: facts[m] for m in ("ModBuild", "ModBlind")}))
        ok(executed == ["ModBlind"], "max_live 1: a mod paused alone takes no slot from the mod behind it (%s)" % executed)
        fresh()
        PP.pause("ModBuild", "one mod", "TEST", now=CLOCK)
        got, rd = tick(0)
        ok("ModBuild" not in got and set(PATHS) - {"ModBuild"} <= set(got), "pause ModBuild: only ModBuild held")
        ok(not RL.pipeline_held("Designer", {}, "design/concepts/ModBlind", CLOCK, lambda **k: None)
           and RL.pipeline_held("Designer", {}, "design/concepts/ModBuild", CLOCK, lambda **k: None),
           "a per-mod pause holds that concept only in the Dispatcher")
        PP.resume("ModBuild", "done", "TEST", now=CLOCK + 1)
        fresh()
        PP.pause(None, "the results cannot be read", "TEST", now=CLOCK)
        a2 = []
        RL.pipeline_held("Designer", {}, None, CLOCK, lambda **k: a2.append(k))
        ok(a2 and not any(a.get("do") == "alarm" for a in a2), "a planned pause whose why says 'cannot be read' is "
           "no alarm")

        # ---- --until: the forecast sees the end, the tick resumes by itself and says so ---------------------------
        fresh()
        PP.pause(None, "until test", "TEST", until=CLOCK + 600, now=CLOCK)
        fcu = MD.forecast(root, cfg, within_s=900, step_s=60, fx=fx, now=CLOCK)
        ok(fcu["launches"] and all(x["at"] == CLOCK + 600 for x in fcu["launches"]),
           "the forecast names the pause's end as the first launch (%s)" % sorted({MD.pac(x["at"]) for x in
                                                                                   fcu["launches"]}))
        mid, _ = tick(300)
        end, rd = tick(600)
        ok(mid == [] and sorted(end) == at_first(fcu, CLOCK + 600), "tick --apply: nothing at +5 min, the forecast's "
           "set at +10 min")
        ok(any("RESUMED BY ITSELF" in str(x) for x in (rd.get("pipeline_pause") or {}).get("said") or []) and
           PP.load()["all"] is None and any(h.get("act") == "auto_resume" for h in PP.load()["history"]),
           "an expired --until resumes by itself, says so, and is history")

        # ---- unreadable = PAUSED ---------------------------------------------------------------------------------
        for bad, what in (("{not json", "torn"), (json.dumps({"all": {"why": ""}, "mods": {}, "history": []}),
                                                  "an entry with no why"),
                          (json.dumps({"all": None, "mods": [], "history": []}), "mods not a mapping"),
                          ("{}", "an empty mapping"),
                          ('{"all": {"why": "x", "at": 1, "until": NaN}, "mods": {}, "history": []}', "a NaN until"),
                          ('{"all": null, "mods": {}, "history": [null]}', "a null history record"),
                          ('{"all": null, "mods": {}, "history": [{"act": "auto_resume", "at": "bad"}]}',
                           "a history record with a bad at")):
            fresh()
            with open(pf, "w") as f:
                f.write(bad)
            got, rd = tick(0)
            ok(got == [] and "cannot be read" in str(rd["mods"]["ModBuild"].get("why")),
               "a %s pause file reads PAUSED: nothing launches, the why says it cannot be read" % what)
        ok(RL.pipeline_held("Designer", {}, None, CLOCK, lambda **k: acts.append(k)) and
           any(a.get("do") == "alarm" for a in acts), "the Dispatcher holds on an unreadable pause file, alarmed")
        os.chmod(sd, 0o600)     # the folder unreadable: the file cannot be proved absent
        try:
            st_blind = PP.state(CLOCK)
        finally:
            os.chmod(sd, 0o755)
        ok(bool(st_blind.get("error")) and PP.reason(st_blind), "a pause file behind an unreadable folder reads "
           "PAUSED, not absent (%s)" % st_blind.get("error"))
        # the pause verbs write the control store (pause = `pipe off`): a torn retired pause.json does not stop them,
        # and it still reads PAUSED until it is repaired (an unreadable store is never read as "not paused")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = MD.main(["pause", "ModBuild", "--why", "one over torn", "--by", "BENCH"])
        ok(rc == 0 and "PAUSED ModBuild" in out.getvalue() and PP.reason(PP.state()), "a one-mod pause writes the "
           "control store; the torn file still reads PAUSED for every mod")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = MD.main(["resume", "--why", "x", "--by", "BENCH"])
        ok(rc == 0 and "STILL" in out.getvalue() and "cannot be read" in out.getvalue(), "resume over a torn file "
           "says it is STILL paused (the file cannot be read)")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = MD.main(["pause", "--why", "over a torn file", "--by", "BENCH", "--until", "+30m"])
        ok(rc == 0 and [r for r in C.switches() if r["scope"] == "all" and r["why"] == "over a torn file"],
           "pause over a torn file writes the pause into the control store")
        os.environ["RM_CONTROL_DB"] = os.path.join(sd, "absent.db")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = MD.main(["resume", "--why", "x", "--by", "BENCH"])
        ok(rc == 1 and "cannot be read" in out.getvalue(), "resume refuses over an unreadable control store")

        # ---- the verbs, --stop-live, rimflow pipeline, the page ---------------------------------------------------
        fresh()
        calls = []
        MD.stop_live = saved["stop_live"]
        MD.STOP_RUNNER[0] = lambda argv, **k: calls.append(argv) or subprocess.CompletedProcess(argv, 0, "", "")
        gather_was = MD.gather
        MD.gather = lambda root_, cfg_, live=True: facts
        try:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = MD.main(["pause", "--why", "stop now", "--by", "BENCH", "--stop-live"])
        finally:
            MD.gather = gather_was
            MD.STOP_RUNNER[0] = subprocess.run
        h = [json.loads(a["after"]) for a in C._q("SELECT after FROM acts WHERE kind='stop_live'")]
        ok(rc == 0 and calls == [["systemctl", "--user", "stop", "rm-detached-fake-live"]] and h and h[-1][
            "void_owed"] and h[-1]["units"][0]["unit"] == "rm-detached-fake-live",
           "--stop-live stops the live run and records it for voiding (%s)" % calls)
        del calls[:]
        r_ = saved["stop_live"](root, cfg, facts={"ModX": {"live_units": "UNMEASURED"}},
                                runner=lambda argv, **k: calls.append(argv))
        ok(calls == [] and r_ and r_[0]["rc"] == 2 and "UNMEASURED" in r_[0]["said"],
           "--stop-live on unreadable live runs stops nothing and says UNMEASURED, never 'none live'")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            MD.main(["status"])
        ok("PIPELINE PAUSED (all): stop now" in out.getvalue(), "status leads with the pause")
        r = subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), "pipeline", "status"], capture_output=True,
                           text=True, timeout=120, env=dict(os.environ))
        ok("PIPELINE PAUSED (all): stop now" in r.stdout, "rimflow pipeline status reaches the same verb (rc %d: %s)" % (
            r.returncode, (r.stdout + r.stderr)[-200:]))
        MD.stop_live = no_stop
        got, rd = tick(0)
        import maturation_now as MN
        lines = MN.dispatch_pipeline(CLOCK, [])
        ok(any(x.startswith("PIPELINE PAUSED (all): stop now") for x in lines), "the status page leads with it")
        for t, want in (("+90m", CLOCK + 5400), ("+2h", CLOCK + 7200)):
            ok(PP.parse_until(t, CLOCK) == want, "--until %s" % t)
        for t in ("yesterday", "2020-01-01T00:00"):
            try:
                PP.parse_until(t, CLOCK)
                ok(False, "--until %s refused" % t)
            except ValueError:
                ok(True, "--until %s refused" % t)
        # ---- decide_roles itself: a pipeline role's scheduled slot does not start under the pause -----------------
        os.environ["TZ"] = "UTC"
        import time as _t
        _t.tzset()
        import selftest_dispatcher as SD

        def drive(now_):
            role = SD.operations(chain_stages=True)
            o = SD.robs(SD.ops_status(now_))
            o["stage_concepts"] = lambda: []
            acts_ = []
            RL.decide_roles({"roles": [role]}, {"roles": {}}, o, now_, lambda **k: acts_.append(k), set(), None)
            return [a for a in acts_ if a.get("do") == "role_launch"], acts_
        fresh()
        t730 = SD.at_local("07:30")
        la, _ = drive(t730)
        ok(len(la) == 1, "decide_roles launches a chain_stages role's due slot unpaused (it can see: %d)" % len(la))
        PP.pause(None, "slot test", "TEST", now=t730 - 60)
        la, aa = drive(t730)
        ok(la == [] and any(a.get("do") == "role_hold" and "slot test" in str(a.get("why")) for a in aa),
           "decide_roles under pause: the slot does not launch, a role_hold note says why")
    finally:
        for n, f in saved.items():
            setattr(MD, n, f)
        AUT.execute = saved_aut
        for k, v in was.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(root, ignore_errors=True)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
