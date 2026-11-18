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
    "ModGame": {"stage": "in_game"},
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

    def fresh():
        shutil.rmtree(sd, ignore_errors=True)
        os.makedirs(sd)

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
        # a mutant forecast that drops one layer must fail the same comparison
        for mod in PATHS:
            mutant = [m for m in pred0 if m != mod]
            ok(mutant != sorted(got0), "mutant forecast without layer %s fails the comparison" % mod)
        # the mutant that is a second copy of the logic missing the autonomy layer (rows with aut)
        second = sorted(m for m in pred0 if not PATHS.get(m, {}).get("aut"))
        ok(second != sorted(got0), "a forecast blind to the autonomy layer (steward, fixer, autolock) fails")

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
        got, rd = tick(0)
        ok("ModBuild" not in got and set(PATHS) - {"ModBuild"} <= set(got), "pause ModBuild: only ModBuild held")
        ok(not RL.pipeline_held("Designer", {}, "design/concepts/ModBlind", CLOCK, lambda **k: None)
           and RL.pipeline_held("Designer", {}, "design/concepts/ModBuild", CLOCK, lambda **k: None),
           "a per-mod pause holds that concept only in the Dispatcher")
        PP.resume("ModBuild", "done", "TEST", now=CLOCK + 1)

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
                          (json.dumps({"all": None, "mods": [], "history": []}), "mods not a mapping")):
            fresh()
            with open(pf, "w") as f:
                f.write(bad)
            got, rd = tick(0)
            ok(got == [] and "cannot be read" in str(rd["mods"]["ModBuild"].get("why")),
               "a %s pause file reads PAUSED: nothing launches, the why says it cannot be read" % what)
        ok(RL.pipeline_held("Designer", {}, None, CLOCK, lambda **k: acts.append(k)) and
           any(a.get("do") == "alarm" for a in acts), "the Dispatcher holds on an unreadable pause file, alarmed")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = MD.main(["resume", "--why", "x", "--by", "BENCH"])
        ok(rc == 1 and "cannot be read" in out.getvalue(), "resume refuses over an unreadable store")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = MD.main(["pause", "--why", "over a torn file", "--by", "BENCH", "--until", "+30m"])
        ok(rc == 0 and PP.load()["all"]["why"] == "over a torn file" and any(
            x.startswith("pause.json.unreadable.") for x in os.listdir(sd)), "pause over a torn file writes the pause "
           "and keeps the torn bytes beside it")

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
        h = [x for x in PP.load()["history"] if x.get("act") == "stop_live"]
        ok(rc == 0 and calls == [["systemctl", "--user", "stop", "rm-detached-fake-live"]] and h and h[-1][
            "void_owed"] and h[-1]["units"][0]["unit"] == "rm-detached-fake-live",
           "--stop-live stops the live run and records it for voiding (%s)" % calls)
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
