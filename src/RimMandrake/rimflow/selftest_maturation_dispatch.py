#!/usr/bin/env python3
"""selftest_maturation_dispatch.py: the Dispatch step (maturation_dispatch.py), offline, in a temp tree, with a fake
detached_helper and a fake filer. Item RIMMANDRAKE_WIRE_DISPATCH_TO_LAUNCH_BUILDERS_MODS_SAT_IDLE. Written before
maturation_dispatch.py and watched failing on the base (the import fails), then passing.

    python3 src/RimMandrake/rimflow/selftest_maturation_dispatch.py      exit 0 when every check prints PASS
    python3 src/RimMandrake/rimflow/selftest_maturation_dispatch.py --ingame   in-game acceptance only (ingame_main)

What it proves: one builder launches for a mod with build-work refusals and nothing live on it, and nothing launches
when a run is live on it, when the last run did not reduce its refusals (and never again at the same refusals), when the
cap is missing, for a mod not on the list, for a mod not at the offline build, on a hold, past the stage's dollar
ceiling, past max_live, on an account hold, or in a dry pass; a run that reduced the refusals lets the next one start;
a failed launch is not retried; a mod ready to advance and one owing a hand step get a Needs Conductor line; the idle
reading fires on a planted idle mod and ops_watch's maturation family reads it (stale is UNMEASURED); the alarm target
is in ops_watch_rules.json; nothing in the repo is written. The blind challenge (blind_main): one automatic judge for
a mod whose cycle is owed with nothing live, never a second in the visit (live, settling, ended without a record, exit
not met, exit met, the Conductor's next cycle, a failed launch), nothing on a hand-launched cycle that is live, just
ended, ended with no exit block or with nothing written, nothing off the list, on a hold, with blind launches off, with
no cap, on an account hold or with the slots full. In-game acceptance (ingame_main): nothing as shipped
(ingame_enabled false, the bridge not even asked); on, one live driver for an owed visit on a takeable bridge, never a
second automatic try (live, settling, ended without a record, exit not met, exit met, no exit block, a failed launch),
nothing on a held bridge, while another mod's in-game run is live, for the second of two owed mods in one tick, on a
hand-launched run that wrote nothing, with no cap, on an account hold, with the slots full or in a dry pass.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

import maturation as M              # noqa: E402
import maturation_dispatch as MD    # noqa: E402

FOUR = ("ExplosiveKnockback", "FlowWorks", "GimmeSomeSlack", "Pyrelands")
COPY = ("journal.md", "stage.json", "version/VERSION.json", "version/test_table.json", "version/preflight.json",
        "version/stage_record.json")
CLOCK = 1794718800.0            # 2026-11-14 9:00 PM PST, pinned
FAILS = []
FAKE_DH = """#!/usr/bin/env python3
import json, os, sys
with open(os.environ["FAKE_DH_LOG"], "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\\n")
n = len(open(os.environ["FAKE_DH_LOG"]).readlines())
if os.environ.get("FAKE_DH_FAIL"):
    print("LAUNCH FAILED rm-detached-bench-fake-%d: pool full" % n)
    sys.exit(1)
print("DETACHED rm-detached-bench-fake-%d" % n)
"""


# The mods' design/concepts files as these tests were written, read from git: the live tables move as builders land
# (2026-11-14: FlowWorks 7 -> 0 and Explosive Knockback 12 -> 1 refused bars turned both maturation selftests red).
FIXTURE_SHA = "f5d809fb03a59ccca0f72da4a509cfb15b01fd64"


def fixture(mod, rel):
    """-> the bytes of design/concepts/<mod>/<rel> at FIXTURE_SHA, or None when it was absent there."""
    r = subprocess.run(["git", "-C", REPO, "show", "%s:design/concepts/%s/%s" % (FIXTURE_SHA, mod, rel)],
                       capture_output=True, timeout=60)
    return r.stdout if r.returncode == 0 else None


def ok(cond, what):
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


def git_status():
    return subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--", "design/concepts"],
                          capture_output=True, text=True, timeout=120).stdout


def main():
    before = git_status()
    root = tempfile.mkdtemp(prefix="maturation_dispatch_")
    keys = ("MATURATION_DETACHED_HELPER", "FAKE_DH_LOG", "MATURATION_BRIEF_DIR", "MATURATION_CLOCK",
            "RM_MATURATION_DISPATCH_DIR", "FAKE_DH_FAIL")
    env_was = {k: os.environ.get(k) for k in keys}
    try:
        for mod in FOUR + ("PyrelandsMechanics",):
            for rel in COPY:
                data = fixture(mod, rel)
                if data is not None:
                    dst = os.path.join(root, "design", "concepts", mod, rel)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    with open(dst, "wb") as f:
                        f.write(data)
        fake, log =os.path.join(root, "fake_dh.py"), os.path.join(root, "fake_dh.log")
        with open(fake, "w") as f:
            f.write(FAKE_DH)
        open(log, "w").close()
        sd = os.path.join(root, "state")
        os.environ.update(MATURATION_DETACHED_HELPER=fake, FAKE_DH_LOG=log, MATURATION_CLOCK=str(CLOCK),
                          MATURATION_BRIEF_DIR=os.path.join(root, "briefs"), RM_MATURATION_DISPATCH_DIR=sd)
        os.environ.pop("FAKE_DH_FAIL", None)

        def launches():
            with open(log) as f:
                return [json.loads(x) for x in f if x.strip()]

        filed = []
        world = {"live": {}, "stage_runs": {}, "last_end": {}, "account": (True, "test account KEEP")}

        def facts():
            out = {}
            for mod in cfg["advancing"]:
                f = M.build_facts(root, mod)
                f["live_units"] = list(world["live"].get(mod, []))
                f["last_end"] = world["last_end"].get(mod)
                f["stage_runs"] = dict(world["stage_runs"].get(mod, {}))
                f["run_usd"] = {}
                out[mod] = f
            return out

        fx = {"facts": facts, "account": lambda: world["account"], "known": lambda: set(),
              "file": lambda item, title, why: (filed.append((item, title, why)) or True, "filed %s" % item),
              "launch": lambda mod, cap, item: M.launch_mod(root, mod, cap, item, model=cfg["model"],
                                                            seat=cfg["seat"])}

        def tick(apply=True, at=0):
            return MD.tick(root, cfg, apply, fx=fx, now=CLOCK + at, page=False)

        def reset():
            shutil.rmtree(sd, ignore_errors=True)
            open(log, "w").close()
            del filed[:]
            world.update(live={}, stage_runs={}, last_end={})

        base = MD.load_cfg()
        cfg = dict(base, advancing=list(FOUR) + ["Graffiti", "PyrelandsMechanics"])
        world["live"] = {"ExplosiveKnockback": ["rm-detached-bench-rimmandrake-build-knockback-stage-three-1"]}

        # ---- the first tick: one launch, on FlowWorks only ----------------------------------------------------------
        rd = tick()
        d = {m: r["decision"] for m, r in rd["mods"].items()}
        ok(len(launches()) == 1 and d["FlowWorks"] == "launched", "one builder launches, on FlowWorks (%s)" % d)
        ok(d["ExplosiveKnockback"] == "live", "Explosive Knockback has a live run: no second builder")
        ok(d["GimmeSomeSlack"] == "hand_step" and any(x.startswith("GimmeSomeSlack: hand step")
                                                       for x in rd["needs_conductor"]),
           "Gimme Some Slack owes a hand step: a Needs Conductor line, no launch")
        ok(d["Pyrelands"] == "ready" and any("ready to advance" in x for x in rd["needs_conductor"]),
           "Pyrelands passes every exit test: 'ready to advance' for the Conductor, never an advance")
        ok(d["Graffiti"] == "not_offline" and d["PyrelandsMechanics"] == "not_offline",
           "Graffiti (no record, the Designer) and Pyrelands Mechanics (intake) launch nothing")
        ok(len(filed) == 1 and filed[0][0] == "RIMMANDRAKE_AUTOBUILD_FLOWWORKS_SEVEN_BARS_LEFT",
           "the build item is filed once, named by the refused count (%s)" % [x[0] for x in filed])
        nc = subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), "namecheck", filed[0][0] if filed else "X"],
                            capture_output=True, text=True, timeout=120)
        ok(nc.returncode == 0, "the minted item name passes rimflow namecheck")
        a = launches()[0] if launches() else []
        ok(a and a[a.index("--budget-usd") + 1] == "15" and a[a.index("--model") + 1] == "opus",
           "the launch carries the 15 USD cap and opus")
        rec = json.load(open(os.path.join(sd, "state.json")))
        unit = rec["mods"]["FlowWorks"]["watch"]["unit"]

        # ---- the run is live: nothing more; it ends with no fewer refusals: stopped for good -----------------------
        world["live"]["FlowWorks"] = [unit]
        tick(at=600)
        ok(len(launches()) == 1, "while the run is live, no second launch on FlowWorks")
        world["live"].pop("FlowWorks")
        world["last_end"]["FlowWorks"] = CLOCK + 900
        rd = tick(at=960)      # 60 s after the end: its files may not have reached this clone yet
        ok(len(launches()) == 1 and rd["mods"]["FlowWorks"]["decision"] == "settling"
           and "stopped" not in json.load(open(os.path.join(sd, "state.json")))["mods"]["FlowWorks"]
           and "watch" in json.load(open(os.path.join(sd, "state.json")))["mods"]["FlowWorks"],
           "a tick 60 s after a run ends neither judges the refused count nor launches; the watch is kept")
        rd = tick(at=1200)
        ok(len(launches()) == 1 and rd["mods"]["FlowWorks"]["decision"] == "stopped"
           and any(x.startswith("FlowWorks: stopped") for x in rd["needs_conductor"]),
           "the run ended with the same 7 refused: stopped, a Needs Conductor line, no relaunch")
        rd = tick(at=1800)
        ok(len(launches()) == 1 and rd["mods"]["FlowWorks"]["decision"] == "stopped",
           "the next tick still never tries the same refusals again")
        r = subprocess.run([sys.executable, os.path.join(HERE, "maturation_dispatch.py"), "clear", "FlowWorks",
                            "--why", "selftest"], capture_output=True, text=True, env=dict(os.environ), timeout=120)
        rd = tick(at=2400)
        ok(r.returncode == 0 and len(launches()) == 2, "the Conductor's clear lets one launch through")

        # ---- a run that reduced the refusals lets the next one start ----------------------------------------------
        reset()
        world["live"] = {}
        cfg = dict(base, advancing=["FlowWorks"])
        tick()
        unit = json.load(open(os.path.join(sd, "state.json")))["mods"]["FlowWorks"]["watch"]["unit"]
        world["live"]["FlowWorks"] = [unit]
        tick(at=600)
        tp = os.path.join(root, "design", "concepts", "FlowWorks", "version", "test_table.json")
        saved = open(tp).read()
        tt = json.loads(saved)
        for b in tt["bars"]:
            if b.get("every_decider_runnable_today") is False:
                b["every_decider_runnable_today"] = True
                break
        with open(tp, "w") as f:
            json.dump(tt, f)
        world["live"] = {}
        rd = tick(at=1200)
        ok(len(launches()) == 2 and rd["mods"]["FlowWorks"]["decision"] == "launched"
           and filed[-1][0] == "RIMMANDRAKE_AUTOBUILD_FLOWWORKS_SIX_BARS_LEFT",
           "the run took the refused bars 7 -> 6: the next builder starts (%s)" % rd["mods"]["FlowWorks"]["decision"])
        with open(tp, "w") as f:
            f.write(saved)

        # ---- each refusal to launch --------------------------------------------------------------------------------
        def none_launched(c, what, want=None, **w):
            reset()
            world.update(w)
            nonlocal_cfg[0] = c
            rd = MD.tick(root, c, True, fx=dict(fx, facts=lambda: facts_for(c)), now=CLOCK, page=False)
            dec = rd["mods"].get("FlowWorks", {}).get("decision")
            ok(not launches() and (want is None or dec == want), "%s: nothing launches (%s)" % (what, dec))
            return rd

        nonlocal_cfg = [cfg]

        def facts_for(c):
            out = {}
            for mod in c["advancing"]:
                f = M.build_facts(root, mod)
                f["live_units"] = list(world["live"].get(mod, []))
                f["last_end"], f["stage_runs"], f["run_usd"] = None, dict(world["stage_runs"].get(mod, {})), {}
                out[mod] = f
            return out

        one = dict(base, advancing=["FlowWorks"])
        none_launched(dict(one, cap_usd=None), "no cap in the settings", "no_cap")
        none_launched(dict(one, cap_usd=0), "a zero cap", "no_cap")
        none_launched(dict(base, advancing=["Pyrelands"]), "FlowWorks not on the advancing list")
        none_launched(dict(base, advancing=["ExplosiveKnockback", "GimmeSomeSlack", "FlowWorks"], max_live=2),
                      "two live runs on other advancing mods (max_live 2)", "slots_full",
                      live={"ExplosiveKnockback": ["u-ek"], "GimmeSomeSlack": ["u-gss"]})
        rd = none_launched(dict(base, advancing=["ExplosiveKnockback", "FlowWorks"], max_live=1),
                           "the Conductor's live builder on Explosive Knockback fills the one slot", "slots_full",
                           live={"ExplosiveKnockback": ["u-ek"]})
        none_launched(one, "the stage's dollars past the ceiling", "stopped", stage_runs={"FlowWorks": {"u1": 61.0}})
        none_launched(one, "the account pick holds role launches", "account_hold",
                      account=(False, "the Dispatcher's account pick reads HOLD"))
        world["account"] = (True, "test account KEEP")
        none_launched(dict(one, enabled=False), "the step disabled", "disabled")
        reset()
        rd = MD.tick(root, one, False, fx=dict(fx, facts=lambda: facts_for(one)), now=CLOCK, page=False)
        ok(not launches() and rd["mods"]["FlowWorks"]["decision"] == "would_launch"
           and not os.path.exists(os.path.join(sd, "state.json")), "a dry pass launches nothing and writes no state")
        jp = os.path.join(root, "design", "concepts", "FlowWorks", "journal.md")
        jsaved = open(jp).read()
        with open(jp, "w") as f:
            f.write(M.add_intervention(jsaved, "- CONDUCTOR INTERVENED (stage 3, 2026-11-14 8:00 PM PST, kind hold): "
                                               "selftest hold. Source: selftest."))
        none_launched(one, "a Conductor hold on Stage 3", "held")
        with open(jp, "w") as f:
            f.write(jsaved)
        none_launched(dict(base, advancing=["PyrelandsMechanics"]), "a mod at intake")

        # ---- a failed launch is not retried --------------------------------------------------------------------------
        reset()
        os.environ["FAKE_DH_FAIL"] = "1"
        rd = MD.tick(root, one, True, fx=dict(fx, facts=lambda: facts_for(one)), now=CLOCK, page=False)
        os.environ.pop("FAKE_DH_FAIL")
        rd2 = MD.tick(root, one, True, fx=dict(fx, facts=lambda: facts_for(one)), now=CLOCK + 600, page=False)
        ok(len(launches()) == 1 and rd["mods"]["FlowWorks"]["decision"] == "launch_failed"
           and rd2["mods"]["FlowWorks"]["decision"] == "stopped" and rd["needs_conductor"],
           "a failed launch gets a Needs Conductor line and no automatic retry")

        # ---- the idle reading and its Operations family ---------------------------------------------------------------
        reset()
        gss = dict(base, advancing=["GimmeSomeSlack"])
        os.makedirs(sd, exist_ok=True)
        with open(os.path.join(sd, "state.json"), "w") as f:
            json.dump({"mods": {"GimmeSomeSlack": {"owed_since": CLOCK - 2 * 3600}}}, f)
        rd = MD.tick(root, gss, True, fx=dict(fx, facts=lambda: facts_for(gss)), now=CLOCK, page=False)
        ok(rd["idle_owed_max_min"] == 120 and rd["idle_owed_mods"] == ["GimmeSomeSlack"],
           "a planted idle mod (owed 2 h, nothing on it) reads 120 min idle (%s)" % rd["idle_owed_max_min"])
        import ops_watch as OW
        got = OW.c_maturation(CLOCK + 60, {}, {})["maturation.idle_owed_max_min"]
        ok(got.get("v") == 120 and got.get("m") == "MEASURED", "ops_watch's maturation family reads it (%s)" % got)
        got = OW.c_maturation(CLOCK + 3 * 3600, {}, {})["maturation.idle_owed_max_min"]
        ok(got.get("m") == "UNMEASURED", "a stale reading is UNMEASURED, never 0")
        rules = json.load(open(os.path.join(REPO, "src", "RimMandrake", "Utils", "ops_watch_rules.json")))
        t = [x for x in rules["targets"] if x.get("name") == MD.ALARM_NAME]
        ok(len(t) == 1 and t[0]["key"] == "maturation.idle_owed_max_min" and t[0]["alarm"] is True
           and t[0]["op"] == ">" and t[0]["value"] == 60, "one fixed-id alarm over 60 min in ops_watch_rules.json")
        ok("maturation" in OW.FAMILIES and "maturation" in OW.ORDER and OW.COLLECTORS.get("maturation"),
           "the family is registered in ops_watch")
        reset()
        rd = MD.tick(root, gss, True, fx=dict(fx, facts=lambda: facts_for(gss)), now=CLOCK, page=False)
        ok(rd["idle_owed_max_min"] > 60, "a mod first seen owed counts its idle time from its stage's since (%s min)"
           % rd["idle_owed_max_min"])
    finally:
        for k, v in env_was.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(root, ignore_errors=True)
    ok(git_status() == before, "nothing under design/concepts in the repo was written")
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


# ---- the blind challenge (item RIMMANDRAKE_BUILD_BLIND_CHALLENGE_LAUNCHER_FOUR_MODS_PARKED) ----------------------------
# The four records as they stood at the blind challenge, read from git (all four hand-launched that night). Written before
# maturation_dispatch.py had add_blind and watched failing on the base 7e85866394 (AttributeError), then passing.
BLIND_SHA = "da54e5338ea493e0cb1575b684791d7136756488"
BLIND_CLOCK = 1794736800.0      # 2026-11-15 1:20 AM PST, pinned
FW_JUDGE_AT = 1794729034.9711447    # the hand-launched FlowWorks judge's start (rm-detached-...-1794729034)


def blind_main():
    sys.path.insert(0, HERE)
    import selftest_maturation as SM
    before = git_status()
    root = tempfile.mkdtemp(prefix="maturation_dispatch_blind_")
    keys = ("MATURATION_DETACHED_HELPER", "FAKE_DH_LOG", "MATURATION_BRIEF_DIR", "MATURATION_CLOCK",
            "RM_MATURATION_DISPATCH_DIR", "FAKE_DH_FAIL")
    env_was = {k: os.environ.get(k) for k in keys}
    try:
        for mod in FOUR:
            for rel in COPY:
                r = subprocess.run(["git", "-C", REPO, "show", "%s:design/concepts/%s/%s" % (BLIND_SHA, mod, rel)],
                                   capture_output=True, timeout=60)
                if r.returncode == 0:
                    dst = os.path.join(root, "design", "concepts", mod, rel)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    with open(dst, "wb") as f:
                        f.write(r.stdout)
        fake, log = os.path.join(root, "fake_dh.py"), os.path.join(root, "fake_dh.log")
        with open(fake, "w") as f:
            f.write(FAKE_DH)
        open(log, "w").close()
        sd = os.path.join(root, "state")
        os.environ.update(MATURATION_DETACHED_HELPER=fake, FAKE_DH_LOG=log, MATURATION_CLOCK=str(BLIND_CLOCK),
                          MATURATION_BRIEF_DIR=os.path.join(root, "briefs"), RM_MATURATION_DISPATCH_DIR=sd)
        os.environ.pop("FAKE_DH_FAIL", None)

        def launches():
            with open(log) as f:
                return [json.loads(x) for x in f if x.strip()]

        filed = []
        world = {"live": {}, "last_end": {}, "runs": {}, "account": (True, "test account KEEP")}

        def facts_for(c):
            out = {}
            for mod in c["advancing"]:
                f = M.build_facts(root, mod)
                f["live_units"] = list(world["live"].get(mod, []))
                f["last_end"], f["stage_runs"], f["run_usd"] = world["last_end"].get(mod), {}, {}
                out[mod] = MD.add_blind(root, mod, f, world["runs"].get(mod, []))
            return out

        fx = {"account": lambda: world["account"], "known": lambda: set(),
              "file": lambda item, title, why: (filed.append((item, title, why)) or True, "filed %s" % item),
              "launch": lambda mod, cap, item: M.launch_mod(root, mod, cap, item, model="opus", seat="BENCH")}

        def tick(c, at=0, apply=True):
            return MD.tick(root, c, apply, fx=dict(fx, facts=lambda: facts_for(c)), now=BLIND_CLOCK + at, page=False)

        def reset():
            shutil.rmtree(sd, ignore_errors=True)
            open(log, "w").close()
            del filed[:]
            world.update(live={}, last_end={}, runs={})

        def need(rd, mod):
            return " ".join(x for x in rd["needs_conductor"] if x.startswith(mod + ":"))

        base = MD.load_cfg()
        ok(base.get("blind_enabled") is True and isinstance(base.get("blind_cap_usd"), (int, float))
           and base["blind_cap_usd"] > 0 and base.get("blind_auto_cycles_per_visit") == 1,
           "the settings: blind launches on, a positive cap, ONE automatic cycle per visit (%s, %s, %s)" % (
               base.get("blind_enabled"), base.get("blind_cap_usd"), base.get("blind_auto_cycles_per_visit")))
        gss = dict(base, advancing=["GimmeSomeSlack"])
        cap = "%g" % base.get("blind_cap_usd", 0)

        # ---- no cycle, nothing live: one automatic cycle, then never a second in the visit --------------------------
        rd = tick(gss)
        d = rd["mods"]["GimmeSomeSlack"]
        a = launches()
        ok(d["decision"] == "launched" and len(a) == 1, "Gimme Some Slack, cycle 1 owed and nothing live: one judge "
                                                        "launches (%s: %s)" % (d["decision"], d["why"][:80]))
        ok(a and a[0][a[0].index("--budget-usd") + 1] == cap and a[0][a[0].index("--model") + 1] == "opus"
           and "# Blind challenge" in open(a[0][a[0].index("--brief-file") + 1]).read(),
           "the launch carries the settings' blind cap, opus and the blind-challenge brief")
        nc = subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), "namecheck", filed[0][0] if filed else "X"],
                            capture_output=True, text=True, timeout=120)
        ok(len(filed) == 1 and nc.returncode == 0 and "BLIND" in filed[0][0],
           "the judge's item is filed once and its name passes namecheck (%s)" % [x[0] for x in filed])
        unit = json.load(open(os.path.join(sd, "state.json")))["mods"]["GimmeSomeSlack"]["blind_auto"][0]["unit"]
        world["live"]["GimmeSomeSlack"] = [unit]
        rd = tick(gss, at=600)
        ok(rd["mods"]["GimmeSomeSlack"]["decision"] == "live" and len(launches()) == 1, "while it is live: nothing more")
        world["live"] = {}
        world["last_end"]["GimmeSomeSlack"] = BLIND_CLOCK + 900
        rd = tick(gss, at=960)
        ok(rd["mods"]["GimmeSomeSlack"]["decision"] == "settling" and len(launches()) == 1,
           "60 s after it ends: settling, nothing judged or launched")
        rd = tick(gss, at=1200)
        ok(rd["mods"]["GimmeSomeSlack"]["decision"] == "stopped" and need(rd, "GimmeSomeSlack")
           and len(launches()) == 1, "it ended and wrote no record: stopped, a Needs Conductor line, no second try")
        SM.write_cycle(root, "GimmeSomeSlack", 1, exit_met=False, problems_open=1, pending_problem=True)
        rd = tick(gss, at=1300)
        ok(rd["mods"]["GimmeSomeSlack"]["decision"] == "exit_not_met" and "exit not met" in need(rd, "GimmeSomeSlack")
           and len(launches()) == 1, "a cycle that ends with exit not met: a Needs Conductor line, nothing launched")
        SM.write_cycle(root, "GimmeSomeSlack", 1)
        rd = tick(gss, at=1400)
        rec = json.load(open(os.path.join(root, "design/concepts/GimmeSomeSlack/version/stage_record.json")))
        ok(rd["mods"]["GimmeSomeSlack"]["decision"] == "exit_met" and "steward-confirms" in need(rd, "GimmeSomeSlack")
           and rec["stage"] == "blind_challenge" and len(launches()) == 1,
           "exit met: the steward's confirmation is named, the record is not advanced, nothing launched")
        res = M.advance(root, "GimmeSomeSlack", "blind_challenge", by="CONDUCTOR", why="selftest: a new blind judge")
        rd = tick(gss, at=1500)
        ok(res["ok"] and rd["mods"]["GimmeSomeSlack"]["decision"] == "auto_spent" and len(launches()) == 1
           and "by hand" in need(rd, "GimmeSomeSlack"),
           "the Conductor opens cycle 2 in the same visit: the visit's one automatic cycle is spent, no launch (%s)"
           % rd["mods"]["GimmeSomeSlack"]["decision"])

        # ---- hand-launched cycles: live, just ended, ended without an exit, ended with nothing written -------------
        fw = dict(base, advancing=["FlowWorks"])
        reset()
        world["live"]["FlowWorks"] = ["rm-detached-bench-rimmandrake-challenge-flowworks-blind-cy-1794729034"]
        world["runs"]["FlowWorks"] = [{"unit": world["live"]["FlowWorks"][0], "at": FW_JUDGE_AT, "end": None,
                                       "live": True, "item": "RIMMANDRAKE_CHALLENGE_FLOWWORKS_BLIND_CYCLE_ONE_FIFTY_SEVEN_BARS"}]
        rd = tick(fw)
        ok(rd["mods"]["FlowWorks"]["decision"] == "live" and not launches(),
           "a hand-launched judge is live and has written nothing yet: no second cycle")
        world["live"] = {}
        world["runs"]["FlowWorks"][0].update(live=False, end=BLIND_CLOCK - 60)
        world["last_end"]["FlowWorks"] = BLIND_CLOCK - 60
        rd = tick(fw)
        ok(rd["mods"]["FlowWorks"]["decision"] == "settling" and not launches(),
           "it ended a minute ago: settling, no second cycle")
        world["last_end"]["FlowWorks"] = BLIND_CLOCK - 3600
        rd = tick(fw)
        ok(rd["mods"]["FlowWorks"]["decision"] == "hand_run_seen" and not launches() and need(rd, "FlowWorks"),
           "it ended an hour ago and wrote no cycle folder: a Needs Conductor line, no second cycle")
        SM.write_cycle(root, "FlowWorks", 1, block=False)
        rd = tick(fw)
        ok(rd["mods"]["FlowWorks"]["decision"] == "cycle_unfinished" and not launches() and need(rd, "FlowWorks"),
           "it ended with its Exit still (pending): a Needs Conductor line, no second cycle")

        # ---- each refusal to launch ---------------------------------------------------------------------------------
        def none(c, what, want, **w):
            reset()
            world.update(w)
            rd = tick(c)
            dec = rd["mods"].get("GimmeSomeSlack", {}).get("decision")
            ok(not launches() and dec == want, "%s: nothing launches (%s)" % (what, dec))
            return rd

        p = os.path.join(root, "design/concepts/GimmeSomeSlack/version/blind_challenge")
        shutil.rmtree(p, ignore_errors=True)
        rp = os.path.join(root, "design/concepts/GimmeSomeSlack/version/stage_record.json")
        r = subprocess.run(["git", "-C", REPO, "show", "%s:design/concepts/GimmeSomeSlack/version/stage_record.json"
                            % BLIND_SHA], capture_output=True, timeout=60)
        with open(rp, "wb") as f:
            f.write(r.stdout)
        jp = os.path.join(root, "design/concepts/GimmeSomeSlack/journal.md")
        jsaved = open(jp).read()
        none(dict(gss, blind_enabled=False), "blind launches off in the settings", "blind_off")
        none(dict(gss, blind_cap_usd=0), "no blind cap", "no_cap")
        none(gss, "the account pick holds role launches", "account_hold",
             account=(False, "the Dispatcher's account pick reads HOLD"))
        world["account"] = (True, "test account KEEP")
        none(dict(base, advancing=["ExplosiveKnockback", "FlowWorks", "GimmeSomeSlack"], max_live=2),
             "two live runs on other advancing mods", "slots_full", live={"ExplosiveKnockback": ["u1"], "FlowWorks": ["u2"]})
        with open(jp, "w") as f:
            f.write(M.add_intervention(jsaved, "- CONDUCTOR INTERVENED (stage 4+5, 2026-11-15 12:50 AM PST, kind hold): "
                                               "selftest hold. Source: selftest."))
        none(gss, "a Conductor hold on stage 4+5", "held")
        with open(jp, "w") as f:
            f.write(jsaved)
        reset()
        rd = tick(dict(base, advancing=["Graffiti"]))
        ok(not launches() and "GimmeSomeSlack" not in rd["mods"], "a mod not on the advancing list: no row, no launch")
        reset()
        rd = tick(gss, apply=False)
        ok(not launches() and rd["mods"]["GimmeSomeSlack"]["decision"] == "would_launch",
           "a dry pass launches nothing")
        reset()
        os.environ["FAKE_DH_FAIL"] = "1"
        rd = tick(gss)
        os.environ.pop("FAKE_DH_FAIL")
        rd2 = tick(gss, at=600)
        ok(len(launches()) == 1 and rd["mods"]["GimmeSomeSlack"]["decision"] == "launch_failed"
           and rd2["mods"]["GimmeSomeSlack"]["decision"] == "stopped",
           "a failed blind launch spends the visit's one automatic cycle: never retried")
    finally:
        for k, v in env_was.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(root, ignore_errors=True)
    ok(git_status() == before, "nothing under design/concepts in the repo was written")
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


def ingame_main():
    """In-game acceptance (item RIMMANDRAKE_BUILD_IN_GAME_STAGE_LAUNCHER_PYRELANDS_ARRIVED_FIRST): off as shipped; on,
    one live driver per visit and one across all mods, only on a takeable bridge, never a second automatic try, every
    ended visit a Needs Conductor line. Written before maturation_dispatch.py had decide_ingame and watched failing on
    the base ab858016ee (each check runs in SM.chk, so each fails by itself), then passing. The real bridge is never
    read: MATURATION_BRIDGE_IDLE is a stand-in that says NOT TAKEABLE, and every reading here is the world's."""
    sys.path.insert(0, HERE)
    import selftest_maturation as SM
    before = git_status()
    root = tempfile.mkdtemp(prefix="maturation_dispatch_ingame_")
    keys = ("MATURATION_DETACHED_HELPER", "FAKE_DH_LOG", "MATURATION_BRIEF_DIR", "MATURATION_CLOCK",
            "RM_MATURATION_DISPATCH_DIR", "FAKE_DH_FAIL", "MATURATION_BRIDGE_IDLE", "FAKE_IDLE", "FAKE_IDLE_LOG")
    env_was = {k: os.environ.get(k) for k in keys}

    def chk(fn, what):
        """SM.chk's rule with this file's ok(), so a FAIL here counts in this file's FAILS (SM.chk's would not)."""
        try:
            cond = fn()
        except Exception as e:  # noqa: BLE001
            cond, what = False, "%s (raised %s: %s)" % (what, type(e).__name__, str(e)[:80])
        ok(bool(cond), what)
    try:
        SM.copy_ingame(root)
        SM.copy_ingame(root, as_mod="PyrelandsTwin")
        fake, log = os.path.join(root, "fake_dh.py"), os.path.join(root, "fake_dh.log")
        idle, ilog = os.path.join(root, "fake_idle.py"), os.path.join(root, "fake_idle.log")
        with open(fake, "w") as f:
            f.write(FAKE_DH)
        with open(idle, "w") as f:
            f.write(SM.FAKE_IDLE)
        open(log, "w").close()
        open(ilog, "w").close()
        sd = os.path.join(root, "state")
        os.environ.update(MATURATION_DETACHED_HELPER=fake, FAKE_DH_LOG=log, MATURATION_CLOCK=str(SM.INGAME_CLOCK),
                          MATURATION_BRIEF_DIR=os.path.join(root, "briefs"), RM_MATURATION_DISPATCH_DIR=sd,
                          MATURATION_BRIDGE_IDLE=idle, FAKE_IDLE="NOT", FAKE_IDLE_LOG=ilog)
        os.environ.pop("FAKE_DH_FAIL", None)
        T0 = SM.INGAME_CLOCK

        def launches():
            with open(log) as f:
                return [json.loads(x) for x in f if x.strip()]

        filed, asked = [], []
        world = {"live": {}, "last_end": {}, "runs": {}, "account": (True, "test account KEEP"), "bridge": (True, "free")}

        def facts_for(c):
            out = {}
            for mod in c["advancing"]:
                f = M.build_facts(root, mod)
                f["live_units"] = list(world["live"].get(mod, []))
                f["last_end"], f["stage_runs"], f["run_usd"] = world["last_end"].get(mod), {}, {}
                runs = world["runs"].get(mod, [])
                out[mod] = MD.add_ingame(root, mod, MD.add_blind(root, mod, f, runs), runs)
            return out

        def bridge(p):
            asked.append(p)
            return world["bridge"]

        fx = {"account": lambda: world["account"], "known": lambda: set(), "bridge": bridge,
              "file": lambda item, title, why, **kw: (filed.append((item, title, why, kw)) or True, "filed %s" % item),
              "launch": lambda mod, cap, item: M.launch_mod(root, mod, cap, item, model="opus", seat="BENCH",
                                                            bridge=lambda p, s: world["bridge"])}

        def tick(c, at=0, apply=True):
            return MD.tick(root, c, apply, fx=dict(fx, facts=lambda: facts_for(c)), now=T0 + at, page=False)

        def reset():
            shutil.rmtree(sd, ignore_errors=True)
            open(log, "w").close()
            del filed[:]
            del asked[:]
            world.update(live={}, last_end={}, runs={}, bridge=(True, "free"))
            shutil.rmtree(os.path.join(root, "design/concepts/Pyrelands/version/in_game"), ignore_errors=True)

        def need(rd, mod):
            return " ".join(x for x in rd["needs_conductor"] if x.startswith(mod + ":"))

        def dec(rd, mod="Pyrelands"):
            return rd["mods"][mod]["decision"]

        base = MD.load_cfg()
        # ingame_enabled shipped false and was set true 2026-11-15 by the Conductor once the first visit (Pyrelands)
        # had run by hand, as the settings' _ingame_doc says; the pin is now "a bool", and the off case is built
        # explicitly below rather than read from the shipped file.
        chk(lambda: isinstance(base.get("ingame_enabled"), bool) and isinstance(base.get("ingame_cap_usd"), (int, float))
            and base["ingame_cap_usd"] > 0 and base.get("ingame_auto_runs_per_visit") == 1
            and base.get("ingame_model") == "opus",
            "the settings as shipped: in-game launches a bool (the Conductor ran the first by hand), a positive cap, one "
            "automatic run per visit, opus (%s, %s, %s)" % (base.get("ingame_enabled"), base.get("ingame_cap_usd"),
                                                           base.get("ingame_auto_runs_per_visit")))
        off = dict(base, advancing=["Pyrelands"], ingame_enabled=False)
        on = dict(off, ingame_enabled=True)
        cap = "%g" % base.get("ingame_cap_usd", 0)

        # ---- off as shipped ------------------------------------------------------------------------------------------
        rd = [None]

        def t_off():
            rd[0] = tick(off)
            return (dec(rd[0]) == "ingame_off" and not launches() and not filed and not asked
                    and "by hand" in need(rd[0], "Pyrelands"))
        chk(t_off, "off (ingame_enabled false), visit 1 owed: no launch, the bridge not even asked, a Needs "
                   "Conductor line saying run it by hand")

        # ---- on: one launch, then never a second automatic try -------------------------------------------------------
        def t_on():
            rd[0] = tick(on)
            a = launches()
            return (dec(rd[0]) == "launched" and len(a) == 1 and a[0][a[0].index("--budget-usd") + 1] == cap
                    and a[0][a[0].index("--model") + 1] == "opus"
                    and "# In-game acceptance (Stage 6)" in open(a[0][a[0].index("--brief-file") + 1]).read()
                    and asked == ["Pyrelands in-game acceptance visit 1"])
        chk(t_on, "on, visit 1 owed, the bridge takeable: one live driver launches (the cap, opus, the in-game brief)")

        def t_item():
            nc = subprocess.run([sys.executable, os.path.join(HERE, "cli.py"), "namecheck", filed[0][0]],
                                capture_output=True, text=True, timeout=120)
            return (len(filed) == 1 and nc.returncode == 0 and "IN_GAME_ACCEPTANCE" in filed[0][0]
                    and filed[0][3].get("needs") == "game-up" and MD._is_ingame_item(filed[0][0]))
        chk(t_item, "its item is filed once, needs game-up, passes namecheck and reads as an in-game run")
        chk(lambda: not MD._is_ingame_item("RIMMANDRAKE_BUILD_IN_GAME_STAGE_LAUNCHER_PYRELANDS_ARRIVED_FIRST"),
            "this launcher's own build item is not an in-game run (a bare IN_GAME is not enough)")
        unit = [None]

        def t_live():
            unit[0] = json.load(open(os.path.join(sd, "state.json")))["mods"]["Pyrelands"]["ingame_auto"][0]["unit"]
            world["live"]["Pyrelands"] = [unit[0]]
            world["runs"]["Pyrelands"] = [{"unit": unit[0], "item": filed[0][0], "live": True, "at": T0}]
            return dec(tick(on, at=600)) == "live" and len(launches()) == 1
        chk(t_live, "while it is live: nothing more")

        def t_settle():
            world["live"] = {}
            world["runs"]["Pyrelands"][0]["live"] = False
            world["last_end"]["Pyrelands"] = T0 + 900
            return dec(tick(on, at=960)) == "settling" and len(launches()) == 1
        chk(t_settle, "60 s after it ends: settling, nothing read or launched")

        def t_stop():
            rd[0] = tick(on, at=1200)
            return dec(rd[0]) == "stopped" and need(rd[0], "Pyrelands") and len(launches()) == 1
        chk(t_stop, "it ended and wrote no record: stopped, a Needs Conductor line, no second try")

        def t_notmet():
            SM.write_visit(root, "Pyrelands", 1, exit_met=False, fail="sc_no_rain")
            rd[0] = tick(on, at=1300)
            return dec(rd[0]) == "exit_not_met" and "exit not met" in need(rd[0], "Pyrelands") and len(launches()) == 1
        chk(t_notmet, "a visit that ends with exit not met: a Needs Conductor line, nothing launched")

        def t_met():
            SM.write_visit(root, "Pyrelands", 1)
            rd[0] = tick(on, at=1400)
            rec = json.load(open(os.path.join(root, "design/concepts/Pyrelands/version/stage_record.json")))
            return (dec(rd[0]) == "exit_met" and "--to pre_human" in need(rd[0], "Pyrelands")
                    and rec["stage"] == "in_game" and len(launches()) == 1)
        chk(t_met, "exit met: the steward's confirmation is named, the record is not advanced, nothing launched")

        def t_unfinished():
            SM.write_visit(root, "Pyrelands", 1, block=False)
            rd[0] = tick(on, at=1500)
            return dec(rd[0]) == "visit_unfinished" and need(rd[0], "Pyrelands") and len(launches()) == 1
        chk(t_unfinished, "a visit record with no exit block and nothing live: a Needs Conductor line, no launch")

        # ---- gates before a launch -----------------------------------------------------------------------------------
        def t_bridge():
            reset()
            world["bridge"] = (False, "NOT TAKEABLE  driver lock held by BENCH (another helper)")
            rd[0] = tick(on)
            return (dec(rd[0]) == "bridge_held" and "driver lock" in rd[0]["mods"]["Pyrelands"]["why"]
                    and not launches() and not filed)
        chk(t_bridge, "the bridge not takeable (another live driver): bridge_held, nothing filed or launched")

        def t_bridge_free_later():
            world["bridge"] = (True, "free")
            return dec(tick(on, at=60)) == "launched" and len(launches()) == 1
        chk(t_bridge_free_later, "a held bridge spends nothing: the next tick with it free launches")

        def t_driver():
            reset()
            world["runs"]["PyrelandsTwin"] = [{"unit": "rm-detached-x", "item": "RIMMANDRAKE_DRIVE_PYRELANDSTWIN_IN_GAME_"
                                               "ACCEPTANCE_VISIT_ONE", "live": True, "at": T0}]
            c = dict(on, advancing=["Pyrelands", "PyrelandsTwin"])
            world["live"]["PyrelandsTwin"] = ["rm-detached-x"]
            rd[0] = tick(c)
            return dec(rd[0]) == "driver_busy" and not launches() and not asked
        chk(t_driver, "an in-game run live on another mod: driver_busy, one live-game driver at a time, bridge not asked")

        def t_two():
            reset()
            c = dict(on, advancing=["Pyrelands", "PyrelandsTwin"], max_live=5)
            rd[0] = tick(c)
            return (dec(rd[0]) == "launched" and dec(rd[0], "PyrelandsTwin") == "driver_busy" and len(launches()) == 1)
        chk(t_two, "two mods owed a visit in one tick: the first launches, the second waits (driver_busy)")

        def t_hand():
            reset()
            world["runs"]["Pyrelands"] = [{"unit": "rm-detached-hand", "item": "RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_"
                                           "ACCEPTANCE_VISIT_ONE", "live": False, "at": T0, "end": T0 + 100}]
            rd[0] = tick(on, at=1000)
            return dec(rd[0]) == "hand_run_seen" and need(rd[0], "Pyrelands") and not launches()
        chk(t_hand, "a hand-launched in-game run that ended with no record: a Needs Conductor line, no launch")

        def t_misc():
            out = []
            for c, word in ((dict(on, ingame_cap_usd=0), "no_cap"), (on, "account_hold")):
                reset()
                if word == "account_hold":
                    world["account"] = (False, "held by the account pick")
                out.append(dec(tick(c)) == word and not launches())
                world["account"] = (True, "test account KEEP")
            reset()
            world["live"]["ExplosiveKnockback"] = ["a", "b"]
            c = dict(on, advancing=["Pyrelands", "ExplosiveKnockback"])
            out.append(dec(tick(c)) == "slots_full" and not launches())
            reset()
            out.append(dec(tick(on, apply=False)) == "would_launch" and not launches())
            return all(out)
        chk(t_misc, "no cap, an account hold, max_live reached, a dry pass: nothing launches")

        def t_fail():
            reset()
            os.environ["FAKE_DH_FAIL"] = "1"
            r1 = tick(on)
            os.environ.pop("FAKE_DH_FAIL")
            r2 = tick(on, at=600)
            return dec(r1) == "launch_failed" and dec(r2) == "stopped" and len(launches()) == 1
        chk(t_fail, "a failed in-game launch spends the visit's one automatic run: never retried")
    finally:
        for k, v in env_was.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(root, ignore_errors=True)
    ok(git_status() == before, "nothing under design/concepts in the repo was written")
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    if "--ingame" in sys.argv[1:]:
        sys.exit(ingame_main())
    rc = main()
    rc = blind_main() or rc
    sys.exit(ingame_main() or rc)
