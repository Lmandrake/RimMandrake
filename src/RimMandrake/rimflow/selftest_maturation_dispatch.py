#!/usr/bin/env python3
"""selftest_maturation_dispatch.py: the Dispatch step (maturation_dispatch.py), offline, in a temp tree, with a fake
detached_helper and a fake filer. Item RIMMANDRAKE_WIRE_DISPATCH_TO_LAUNCH_BUILDERS_MODS_SAT_IDLE. Written before
maturation_dispatch.py and watched failing on the base (the import fails), then passing. It tests the per-stage
decision alone (fx autonomy False): what decide() reads. Since 2026-11-15 the tick's autonomy layer
(maturation_autonomy.py, selftest_maturation_autonomy.py) turns its hand-step and Needs Conductor decisions into steward
runs, PAUSED or OWNER; the "Needs Conductor" wording below names decide()'s reading, not the live outcome.

    python3 src/RimMandrake/rimflow/selftest_maturation_dispatch.py      exit 0 when every check prints PASS
    python3 src/RimMandrake/rimflow/selftest_maturation_dispatch.py --ingame   in-game acceptance only (ingame_main)
    python3 src/RimMandrake/rimflow/selftest_maturation_dispatch.py --release  the ceiling release command and digest only

Ceiling releases (RIMMANDRAKE_RELEASE_STAGE_CEILING_PER_MOD_ONLY_GLOBAL_KNOB), written with the code and watched failing on
the base (no `releases` fx, no `release` verb, no digest source): no record pauses and names the release command; a
record for that mod, stage and amount launches once and spends itself, and the mod re-pauses at the next ceiling;
another mod's, another stage's, a spent, a stale or a too-small record and malformed lines release nothing; the
release verb writes who, spend, amount and why and refuses the rest; the digest shows mod, stage and who (token-blind:
no dollars, no why), and `releases` lists the spend, amount and why.

What it proves: one builder launches for a mod with build-work refusals and nothing live on it, and nothing launches
when a run is live on it, when the last run did not reduce its refusals (and never again at the same refusals), when the
cap is missing, for a mod not on the list, for a mod not at the offline build, on a hold, past the stage's dollar
ceiling, past max_live, on an account hold, or in a dry pass; a run that reduced the refusals lets the next one start;
a failed launch is not retried; a mod ready to advance and one owing a hand step get a Needs Conductor line; the idle
reading fires on a planted idle mod and ops_watch's maturation family reads it (stale is UNMEASURED); the alarm target
is in ops_watch_rules.json; nothing in the repo is written. The blind challenge (blind_main): one automatic judge for
a mod whose cycle is owed with nothing live, never a second in the visit (live, settling, ended without a record, exit
not met, exit met, the Conductor's next cycle, a failed launch; a launch that never started on a
transient git fault retries the same item, three times at most), nothing on a hand-launched cycle that is live, just
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
import detached_helper as DH        # noqa: E402

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

# The ceiling these checks were written against, pinned so they pass with any shipped stage_ceiling_usd (item
# RIMMANDRAKE_RELEASE_STAGE_CEILING_PER_MOD_ONLY_GLOBAL_KNOB: the shipped 60 -> 100 turned a ceiling check red).
FIXTURE_CEILING = 60


def load_cfg():
    """-> the shipped settings with the fixture ceiling."""
    return dict(MD.load_cfg(), stage_ceiling_usd=FIXTURE_CEILING)


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

        fx = {"autonomy": False, "facts": facts, "account": lambda: world["account"], "known": lambda: set(),
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

        base = load_cfg()
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
        # RIMMANDRAKE_DERIVE_CHECKS_FROM_LOCKED_BARS: first a flag flipped with no check changed: not progress, a stop
        for b in tt["bars"]:
            if b.get("every_decider_runnable_today") is False:
                b["every_decider_runnable_today"] = True
                flip = b
                break
        with open(tp, "w") as f:
            json.dump(tt, f)
        world["live"] = {}
        st_path = os.path.join(sd, "state.json")
        st_keep = open(st_path).read()
        rd = tick(at=1200)
        ok(rd["mods"]["FlowWorks"]["decision"] == "stopped" and "flag flipped" in rd["mods"]["FlowWorks"]["why"]
           and len(launches()) == 1, "a refused bar turned runnable with its checks unchanged is not progress (%s)"
           % rd["mods"]["FlowWorks"]["why"][:90])
        with open(st_path, "w") as f:
            f.write(st_keep)
        pr = MD.progressed({"ids": ["b1", "b2"], "refused": 2}, ["b1", "b9"], {})
        ok(pr[0] is False and "rename" in pr[1], "a renamed refused bar (b2 -> b9) is not progress (%s)" % pr[1])
        # then the check is built: the bar's decider gains a command, so its fingerprint moves
        for t in flip.get("decides") or []:
            tt["tests"].setdefault(t, {})
            if isinstance(tt["tests"][t], dict):
                tt["tests"][t]["command"] = "python3 selftest_built_%s.py" % t
        with open(tp, "w") as f:
            json.dump(tt, f)
        rd = tick(at=1260)
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
                f["live_units"] = (MD.UNM if mod in world.get("unreadable", ()) else
                                   list(world["live"].get(mod, [])))
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
        # RIMMANDRAKE_RESERVE_CAP_BEFORE_LAUNCH: the cap is reserved, and an unknown occupancy fails closed
        rd = none_launched(dict(one, stage_ceiling_usd=60, cap_usd=15), "USD 50 spent plus a USD 15 cap passes the "
                           "60 ceiling", "stopped", stage_runs={"FlowWorks": {"u1": 50.0}})
        ok("cap passes" in rd["mods"]["FlowWorks"]["why"], "the refusal names the reserved cap (%s)"
           % rd["mods"]["FlowWorks"]["why"])
        reset()
        world.update(stage_runs={"FlowWorks": {"u1": 45.0}})
        rd = MD.tick(root, dict(one, stage_ceiling_usd=60, cap_usd=15), True,
                     fx=dict(fx, facts=lambda: facts_for(dict(one, stage_ceiling_usd=60, cap_usd=15))), now=CLOCK,
                     page=False)
        ok(rd["mods"]["FlowWorks"]["decision"] == "launched", "USD 45 spent plus a USD 15 cap fits the 60 ceiling: it "
           "launches (%s)" % rd["mods"]["FlowWorks"]["decision"])

        # ---- a ceiling release, at the offline build (RIMMANDRAKE_RELEASE_STAGE_CEILING_PER_MOD_ONLY_GLOBAL_KNOB) -----------
        c60 = dict(one, stage_ceiling_usd=60, cap_usd=15)

        def rel(**k):
            r = {"id": "rel-test-a", "ts": "2026-11-15T19:00:00Z", "mod": "FlowWorks", "stage": "offline_build",
                 "by": "BENCH", "read_usd": 50.0, "release_usd": 5.0, "why": "selftest"}
            r.update(k)
            return r

        def rtick(recs, bad=0, spent=50.0, used=None):
            reset()
            world.update(stage_runs={"FlowWorks": {"u1": spent}})
            if used:
                os.makedirs(sd, exist_ok=True)
                with open(os.path.join(sd, "state.json"), "w") as fh:
                    json.dump({"mods": {"FlowWorks": {"releases_used": used}}}, fh)
            return rtick_again(recs, bad)

        def rtick_again(recs, bad=0):
            return MD.tick(root, c60, True, fx=dict(fx, facts=lambda: facts_for(c60), releases=lambda: (list(recs), bad)),
                           now=CLOCK, page=False)

        def fw(rd):
            r = rd["mods"]["FlowWorks"]
            return "%s: %s" % (r["decision"], r.get("why"))

        cmd = "maturation_dispatch.py release FlowWorks --stage offline_build --read-usd 50.00 --usd 5 --why"
        rd = rtick([])
        ok(not launches() and fw(rd).startswith("stopped") and cmd in fw(rd), "no release record: USD 50 + a USD 15 cap "
           "past 60 stays paused, and the pause names the release command (%s)" % fw(rd))
        rd = rtick_again([rel()])
        used = json.load(open(os.path.join(sd, "state.json")))["mods"]["FlowWorks"].get("releases_used") or {}
        ok(len(launches()) == 1 and fw(rd).startswith("launched") and "rel-test-a" in used,
           "a release for this mod, stage and amount (USD 5, read at USD 50) lifts the ceiling stop: one launch, the "
           "release spent (%s; used %s)" % (fw(rd)[:40], sorted(used)))
        rd = rtick([rel()], spent=65.0, used={"rel-test-a": {"at": CLOCK}})
        ok(not launches() and fw(rd).startswith("stopped") and "its release is spent" in fw(rd)
           and "--read-usd 65.00 --usd 20 " in fw(rd), "the released run's USD 15 spent (65): the spent release frees "
           "nothing and the mod re-pauses at the next ceiling, naming the next release (%s)" % fw(rd))
        for r, what, says in ((rel(mod="ExplosiveKnockback"), "a release for another mod", cmd),
                              (rel(stage="blind_challenge"), "a release for another stage", cmd),
                              (rel(read_usd=40.0), "a release that read another spend (USD 40)", "the spend is now USD 50.00"),
                              (rel(release_usd=2.0), "a release smaller than the cap needs (USD 2)", "does not cover")):
            rd = rtick([r])
            ok(not launches() and fw(rd).startswith("stopped") and says in fw(rd), "%s: still paused (%s)" % (what, fw(rd)))
        rd = rtick([], bad=2)
        ok(not launches() and "2 malformed release line(s) ignored" in fw(rd), "malformed release lines: still paused, and "
           "the pause counts them (%s)" % fw(rd))
        rp = os.path.join(root, "releases_fixture.jsonl")
        with open(rp, "w") as fh:
            fh.write("\n".join([json.dumps(rel()), "{not json", json.dumps(dict(rel(), why="")),
                                 json.dumps(dict(rel(), release_usd=-5)), json.dumps(dict(rel(), stage="bogus")),
                                 json.dumps(dict(rel(), read_usd=True)), json.dumps(["a list"]), ""]) + "\n")
        recs, bad = MD.read_releases(rp)
        ok(len(recs) == 1 and bad == 6 and MD.read_releases(os.path.join(root, "absent.jsonl")) == ([], 0),
           "read_releases: one whole record, six malformed lines counted, no file is no release (%d, %d)" % (len(recs), bad))
        none_launched(dict(base, advancing=["ExplosiveKnockback", "FlowWorks"], max_live=2),
                      "Explosive Knockback's live runs cannot be read (occupancy unknown)", "slots_unknown",
                      unreadable={"ExplosiveKnockback"})
        world["unreadable"] = ()
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


def release_main():
    """The release command and the digest's reading of it (RIMMANDRAKE_RELEASE_STAGE_CEILING_PER_MOD_ONLY_GLOBAL_KNOB)."""
    import datetime as dt
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake"))      # the digest's contracts package
    import delegated_digest as DD
    before = git_status()
    sd = tempfile.mkdtemp(prefix="maturation_release_")
    path = os.path.join(sd, "releases.jsonl")
    env = dict(os.environ, RM_MATURATION_DISPATCH_DIR=sd)
    try:
        def run(*a, **e):
            r = subprocess.run([sys.executable, os.path.join(HERE, "maturation_dispatch.py"), "release"] + list(a),
                               capture_output=True, text=True, timeout=120, env=dict(env, **e))
            return r.returncode, (r.stdout + r.stderr).strip()

        rc, out = run("FlowWorks", "--stage", "in_game", "--read-usd", "40", "--usd", "30", "--why", "selftest release",
                      "--by", "BENCH")
        recs, bad = MD.read_releases(path)
        ok(rc == 0 and out.startswith("RELEASED FlowWorks") and len(recs) == 1 and not bad
           and (recs[0]["by"], recs[0]["read_usd"], recs[0]["release_usd"], recs[0]["why"]) == ("BENCH", 40, 30,
                                                                                               "selftest release"),
           "release writes one whole record: who, the spend read, the amount, why (%s)" % out[:90])
        args = ["--stage", "in_game", "--read-usd", "40", "--usd", "30", "--why", "x", "--by", "BENCH"]
        for a, what, e in ((["NotAMod"] + args, "a mod off the advancing list", {}),
                           (["FlowWorks"] + args[:4] + ["--usd", "0"] + args[6:], "a zero release", {}),
                           (["FlowWorks", "--stage", "nowhere"] + args[2:], "an unknown stage", {}),
                           (["FlowWorks"] + args[:-2], "no seat and no --by", {"AGENT_SEAT": "", "RIMFLOW_SEAT": ""}),
                           (["FlowWorks"] + args[:-1] + ["NOBODY"], "a --by that is no ledger seat", {})):
            rc, out = run(*a, **e)
            ok(rc != 0 and len(MD.read_releases(path)[0]) == 1, "release refuses %s, writing nothing (%s)" % (what, out[-60:]))
        # "CONDUCTOR" is the display name of seat BENCH: written as BENCH, or the page's closed seat set drops "who"
        cp = os.path.join(tempfile.mkdtemp(dir=sd), "releases.jsonl")
        rc, out = run(*(["FlowWorks"] + args[:-1] + ["CONDUCTOR"]), RM_MATURATION_DISPATCH_DIR=os.path.dirname(cp))
        cr = MD.read_releases(cp)[0]
        ok(rc == 0 and len(cr) == 1 and cr[0]["by"] == "BENCH",
           "release --by CONDUCTOR records seat BENCH (%s)" % (cr[0]["by"] if cr else out[-60:]))
        with open(path, "a") as fh:
            fh.write("{not json\n")
        rr = DD.release_read(path)
        ok(rr["state"] == "measured" and len(rr["items"]) == 1 and rr["malformed"] == 1,
           "the digest reads the release file: one record, one malformed line counted (%s)" % {k: rr[k] for k in
                                                                                             ("state", "malformed")})
        ab = DD.release_read(os.path.join(sd, "none.jsonl"))
        ok(ab["state"] == "measured" and not ab["items"], "no release file yet: measured and empty, not UNMEASURED")
        cut = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1)
        text, seen = DD.build(cut.strftime("%Y-%m-%d"), None, cut, {"release": rr})
        ok("release FlowWorks at in_game by BENCH" in text and "selftest release" not in text
           and len(seen["release"]) == 1, "the daily digest shows the release: mod, stage, who; never its why text "
           "or its dollars, the page being token-blind (%s)" % [x for x in text.splitlines() if "FlowWorks" in x][:1])
        lst = subprocess.run([sys.executable, os.path.join(HERE, "maturation_dispatch.py"), "releases"],
                             capture_output=True, text=True, timeout=120, env=env)
        ok(lst.returncode == 0 and "FlowWorks" in lst.stdout and "read USD 40.00" in lst.stdout
           and "released USD 30" in lst.stdout and "selftest release" in lst.stdout and "1 malformed" in lst.stdout,
           "`releases` lists each release with its spend, amount and why for the Conductor (%s)" % lst.stdout[:120])
    finally:
        shutil.rmtree(sd, ignore_errors=True)
    ok(git_status() == before, "nothing in the repo was written")
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


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
                f["box_runs"] = dict(world.get("box_runs", {}).get(mod, {}))
                f["ended_runs"] = list(world.get("ended", {}).get(mod, []))
                f["killed"] = dict(world.get("killed", {}).get(mod, {}))
                out[mod] = MD.add_blind(root, mod, f, world["runs"].get(mod, []))
            return out

        fx = {"autonomy": False, "account": lambda: world["account"], "known": lambda: set(),
              "file": lambda item, title, why: (filed.append((item, title, why)) or True, "filed %s" % item),
              "launch": lambda mod, cap, item, **kw: M.launch_mod(root, mod, cap, item, model="opus", seat="BENCH",
                                                                  **kw)}

        def tick(c, at=0, apply=True):
            return MD.tick(root, c, apply, fx=dict(fx, facts=lambda: facts_for(c)), now=BLIND_CLOCK + at, page=False)

        def reset():
            shutil.rmtree(sd, ignore_errors=True)
            open(log, "w").close()
            del filed[:]
            world.update(live={}, last_end={}, runs={}, box_runs={}, ended={}, killed={})

        def need(rd, mod):
            return " ".join(x for x in rd["needs_conductor"] if x.startswith(mod + ":"))

        base = load_cfg()
        ok(base.get("blind_enabled") is True and isinstance(base.get("blind_cap_usd"), (int, float))
           and base["blind_cap_usd"] > 0 and base.get("blind_auto_cycles_per_visit") == M.CYCLE_LIMIT,
           "the settings: blind launches on, a positive cap, automatic cycles per visit = his CYCLE_LIMIT (%s, %s, %s)" % (
               base.get("blind_enabled"), base.get("blind_cap_usd"), base.get("blind_auto_cycles_per_visit")))
        gss = dict(base, advancing=["GimmeSomeSlack"], blind_auto_cycles_per_visit=1)   # the spent-visit mechanism, at 1
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
        # RIMMANDRAKE_RESERVE_CAP_BEFORE_LAUNCH: the ceiling holds at the blind challenge too, cap reserved
        rd = none(dict(gss, stage_ceiling_usd=60, blind_cap_usd=20), "USD 45 spent at the blind challenge plus a USD 20 "
                  "cap passes the 60 ceiling", "ceiling", box_runs={"GimmeSomeSlack": {"4+5": {"u-j1": 45.0}}})
        ok("release GimmeSomeSlack --stage blind_challenge --read-usd 45.00 --usd 5 --why" in rd["mods"]["GimmeSomeSlack"]
           ["why"], "the blind ceiling pause names its release command (%s)" % rd["mods"]["GimmeSomeSlack"]["why"])
        # RIMMANDRAKE_RELEASE_STAGE_CEILING_PER_MOD_ONLY_GLOBAL_KNOB: a release is per stage
        c60 = dict(gss, stage_ceiling_usd=60, blind_cap_usd=20)
        for stage, want in (("offline_build", "ceiling"), ("blind_challenge", "launched")):
            reset()
            world.update(box_runs={"GimmeSomeSlack": {"4+5": {"u-j1": 45.0}}})
            brel = {"id": "rel-b-" + stage, "ts": "2026-11-15T19:00:00Z", "mod": "GimmeSomeSlack", "stage": stage,
                    "by": "BENCH", "read_usd": 45.0, "release_usd": 5.0, "why": "selftest"}
            rd = MD.tick(root, c60, True, fx=dict(fx, facts=lambda: facts_for(c60), releases=lambda: ([brel], 0)),
                         now=BLIND_CLOCK, page=False)
            dec = rd["mods"]["GimmeSomeSlack"]["decision"]
            ok(dec == want and len(launches()) == (1 if want == "launched" else 0), "a USD 5 release at the %s: the "
               "blind challenge %s (%s)" % (stage, "launches once" if want == "launched" else "stays paused", dec))
        # a finished blind run and a finished in-game run each write one spend row, once
        reset()
        landed = []
        ended = [{"unit": "u-blind-1", "item": "RIMMANDRAKE_JUDGE_GIMMESOMESLACK_BLIND_CYCLE_ONE_TESTS_FIRST",
                  "live": False, "at": BLIND_CLOCK - 3600, "end": BLIND_CLOCK - 600, "usd": 12.5, "tokens": 3013781,
                  "wall_s": 3000, "cap": 20, "stages": []},
                 {"unit": "u-ig-1", "item": "RIMMANDRAKE_DRIVE_GIMMESOMESLACK_IN_GAME_ACCEPTANCE_VISIT_ONE",
                  "live": False, "at": BLIND_CLOCK - 3600, "end": BLIND_CLOCK - 500, "usd": None, "said_usd": 18.0,
                  "tokens": None, "wall_s": 2000, "cap": 30, "stages": []},
                 {"unit": "u-live", "item": "RIMMANDRAKE_JUDGE_GIMMESOMESLACK_BLIND_CYCLE_TWO_TESTS_FIRST",
                  "live": True, "at": BLIND_CLOCK - 60, "end": None, "stages": []}]
        world["ended"] = {"GimmeSomeSlack": ended}
        fx2 = dict(fx, land_spend=lambda paths: landed.append(paths) or "PUBLISHED test")
        MD.tick(root, gss, True, fx=dict(fx2, facts=lambda: facts_for(gss)), now=BLIND_CLOCK, page=False)
        rows = M.read_run_spend(root, "GimmeSomeSlack")
        by = {x.get("unit"): x for x in rows}
        ok(set(by) == {"u-blind-1", "u-ig-1"} and by["u-blind-1"]["stage"] == "blind_challenge"
           and by["u-blind-1"]["tokens"] == 3013781 and by["u-ig-1"]["stage"] == "in_game"
           and by["u-ig-1"]["usd"] == 18.0, "a finished blind run and a finished in-game run each write a spend row; "
           "the live one does not (%s)" % sorted(by))
        ok(landed == [["design/concepts/GimmeSomeSlack/%s" % M.RUN_SPEND]], "the rows are landed, that file only (%s)"
           % landed)
        MD.tick(root, gss, True, fx=dict(fx2, facts=lambda: facts_for(gss)), now=BLIND_CLOCK + 60, page=False)
        ok(len(M.read_run_spend(root, "GimmeSomeSlack")) == 2 and len(landed) == 1,
           "a second tick writes no second row and lands nothing")
        sp = M.next_step(root, "GimmeSomeSlack")["spend"]
        ok(sp.get("blind_challenge", {}).get("tokens", 0) >= 3013781 and "in_game" in sp,
           "maturation.py next counts them under their stages (%s)" % sorted(sp))
        os.remove(os.path.join(root, "design/concepts/GimmeSomeSlack", M.RUN_SPEND))
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

        # ---- RIMMANDRAKE_RETRY_JUDGE_LAUNCH_GIT_LOCK_SPENT_THE_CYCLE: a launch that never started on a transient
        # publish fault (measured 2026-11-15: an index.lock at publish, then "not on origin/main") is not a cycle: the
        # next tick publishes again and launches the same item, up to launch_tries; any other failure spends (above)
        lock = "publish: publish stopped: index.lock present (0 s old, under 300 s: another git may be running)"
        refuse = "REFUSED: %s is not on origin/main; publish infrastructure/state/ledger/events/RUNNER.jsonl first"
        published = []

        def flaky(fails):
            """-> (calls, launch): the launch fails with fails[k] (a text, or None to launch for real) on call k."""
            calls = []

            def launch(mod, cap_, item):
                calls.append(item)
                why = fails[len(calls) - 1] if len(calls) <= len(fails) else None
                return (2, why % item if "%s" in why else why, None) if why else fx["launch"](mod, cap_, item)
            return calls, launch

        def fxr(launch, file_fails=0):
            tries = []

            def file_(item, title, why):
                tries.append(item)
                if len(tries) <= file_fails:
                    return False, "ingest.lock stayed busy; nothing filed"
                filed.append((item, title, why))
                return True, "filed %s; %s" % (item, lock)
            return dict(fx, launch=launch, file=file_,
                        publish=lambda item: (published.append(item) or True, "publish: PUBLISHED test"))

        def rtick(fx_, at=0):
            return MD.tick(root, gss, True, fx=dict(fx_, facts=lambda: facts_for(gss)), now=BLIND_CLOCK + at, page=False)

        def bk():
            return json.load(open(os.path.join(sd, "state.json")))["mods"]["GimmeSomeSlack"].get("blind_auto") or []

        def g(rd_):
            return rd_["mods"]["GimmeSomeSlack"]

        reset()
        del published[:]
        calls, fl = flaky([refuse])
        f1 = fxr(fl)
        r1, r2 = rtick(f1), rtick(f1, at=60)
        b = bk()
        ok(g(r1)["decision"] == "launch_retry" and g(r2)["decision"] == "launched" and len(launches()) == 1
           and len(filed) == 1 and published == [filed[0][0]] and calls == [filed[0][0]] * 2 and len(b) == 1
           and b[0].get("unit") and b[0].get("tries") == 2,
           "a blind launch that never started on a git lock (filed, publish stopped, not on origin/main): the next tick "
           "publishes again and launches the same item, one cycle in the book (%s, %s; filed %d, book %s)" % (
               g(r1)["decision"], g(r2)["decision"], len(filed), [(x.get("tries"), bool(x.get("unit"))) for x in b]))
        world["live"]["GimmeSomeSlack"] = [b[0]["unit"]] if b and b[0].get("unit") else []
        ok(g(rtick(f1, at=120))["decision"] == "live" and len(launches()) == 1, "the retried judge is live: nothing more")
        world["live"] = {}

        reset()
        del published[:]
        calls, fl = flaky([refuse] * 9)
        f3 = fxr(fl)
        rs = [rtick(f3, at=60 * k) for k in range(4)]
        b = bk()
        ok([g(x)["decision"] for x in rs] == ["launch_retry", "launch_retry", "launch_failed", "stopped"]
           and "3 times" in g(rs[3])["why"] and need(rs[3], "GimmeSomeSlack") and len(calls) == 3 and not launches()
           and len(filed) == 1 and len(b) == 1 and b[0].get("tries") == 3,
           "three transient faults in a row: stopped (PAUSED) naming the count, a Needs Conductor line, no fourth try "
           "(%s; %s)" % ([g(x)["decision"] for x in rs], g(rs[3])["why"][:90]))

        reset()
        calls, fl = flaky([refuse, "LAUNCH FAILED rm-detached-bench-fake: pool full"])
        f4 = fxr(fl)
        rs = [rtick(f4, at=60 * k) for k in range(3)]
        ok([g(x)["decision"] for x in rs] == ["launch_retry", "launch_failed", "stopped"] and not launches()
           and len(calls) == 2, "a transient fault, then a real launch failure: the real one spends the cycle (%s)"
           % [g(x)["decision"] for x in rs])

        reset()
        del published[:]
        calls, fl = flaky([])
        f5 = fxr(fl, file_fails=1)
        r1, r2 = rtick(f5), rtick(f5, at=60)
        ok(g(r1)["decision"] == "launch_retry" and g(r2)["decision"] == "launched" and len(filed) == 1
           and not published and len(launches()) == 1,
           "the ingest lock busy at filing (nothing filed): the next tick files and launches (%s, %s)" % (
               g(r1)["decision"], g(r2)["decision"]))

        # the live record as it stood 2026-11-15 10:25 PST (no tries, no filed field) retries without a clear
        reset()
        del published[:]
        calls, fl = flaky([refuse])
        f6 = fxr(fl)
        rtick(f6)
        p = os.path.join(sd, "state.json")
        st = json.load(open(p))
        x = st["mods"]["GimmeSomeSlack"]["blind_auto"][0]
        item = x["item"]
        for k in ("tries", "filed", "never_started"):
            x.pop(k, None)
        x["failed"] = ("filed %s; publish: publish stopped: index.lock present (0 s old, under 300 s: another git may be "
                       "running); refused: %s is not on origin/main; publish infrastructure/state/ledger/events/"
                       "RUNNER.jsonl first" % (item, item))
        with open(p, "w") as f:
            json.dump(st, f)
        r2 = rtick(f6, at=60)
        ok(g(r2)["decision"] == "launched" and published == [item] and calls == [item, item] and len(filed) == 1,
           "an older record (no tries field, the failed text measured live) retries the same item without a clear (%s)"
           % g(r2)["decision"])

        # ---- RIMMANDRAKE_RETRY_RUN_KILLED_BY_ACCOUNT_SWITCH_CYCLE_KEPT: a judge that STARTED and was killed from
        # outside before it wrote a result (measured 2026-11-15 ~12:00 PM PST: the account switch SIGTERMed two judges,
        # empty out and err, units gone, finish never ran) is not the cycle: the tick finishes it and starts its return,
        # waits for the clone, then relaunches the same item within launch_tries; one that ended by itself is still spent
        reset()
        del published[:]
        reaped = []
        kfx = dict(fx, publish=lambda item: (published.append(item) or True, "publish: PUBLISHED test"),
                   reap=lambda u: reaped.append(u) or "reaped %s (test)" % u)

        def kill(unit, **kw):
            k = dict(why="its unit died with no result JSON and its finish never ran", state="running", returned=False,
                     kept=False, return_going=False)
            k.update(kw)
            world["killed"] = {"GimmeSomeSlack": {unit: k}}
            world["runs"] = {"GimmeSomeSlack": [{"unit": unit, "item": bk()[-1]["item"], "at": BLIND_CLOCK + 5,
                                                  "live": False}]}

        r0 = rtick(kfx)
        b0 = bk()
        u0 = b0[0].get("unit") if b0 else None
        kill(u0)
        r1 = rtick(kfx, at=600)
        ok(g(r0)["decision"] == "launched" and g(r1)["decision"] == "launch_retry" and reaped == [u0]
           and len(launches()) == 1 and not need(r1, "GimmeSomeSlack"),
           "a judge killed before it wrote a result (finish never ran): not stopped, the tick finishes it and starts its "
           "return, nothing launches yet (%s, %s: %s)" % (g(r0)["decision"], g(r1)["decision"], g(r1)["why"][:120]))
        kill(u0, state="finished", return_going=True)
        r2 = rtick(kfx, at=660)
        ok(g(r2)["decision"] == "launch_retry" and reaped == [u0] and len(launches()) == 1,
           "its return is still giving the clone back: wait, no second reap, no launch (%s)" % g(r2)["decision"])
        kill(u0, state="finished", returned=True)
        r3 = rtick(kfx, at=720)
        b = bk()
        ok(g(r3)["decision"] == "launched" and len(launches()) == 2 and len(b) == 1 and b[0].get("tries") == 2
           and b[0].get("item") == b0[0]["item"] and b[0].get("killed_before") == [u0] and published == [b0[0]["item"]]
           and len(filed) == 1,
           "the clone back: the same item relaunches as the same cycle, one book entry, try 2 (%s; book %s)" % (
               g(r3)["decision"], [(x.get("tries"), x.get("killed_before")) for x in b]))
        a3 = launches()[-1] if launches() else []
        ok(a3 and "## Resume" in open(a3[a3.index("--brief-file") + 1]).read() and u0 in open(
            a3[a3.index("--brief-file") + 1]).read(), "the relaunch's brief opens with the Resume section naming the "
                                                       "killed run")
        u1 = b[0].get("unit")
        kill(u1, state="finished", returned=True)
        r4 = rtick(kfx, at=780)
        u2 = bk()[0].get("unit")
        kill(u2, state="finished", returned=True)
        r5 = rtick(kfx, at=840)
        ok(g(r4)["decision"] == "launched" and g(r5)["decision"] == "stopped" and len(launches()) == 3
           and bk()[0].get("tries") == 3 and need(r5, "GimmeSomeSlack"),
           "killed again and again: launch_tries (3) bound it, then stopped with a Needs Conductor line (%s, %s)" % (
               g(r4)["decision"], g(r5)["decision"]))

        # the measured case: the killed judge had already published lane 1, so cycle_N has a SUMMARY.md with no exit
        # block; its relaunch resumes that cycle instead of reading it as unfinished (PAUSED)
        reset()
        r0 = rtick(kfx)
        cdir = os.path.join(root, "design", "concepts", "GimmeSomeSlack", "version", "blind_challenge", "cycle_1")
        os.makedirs(os.path.join(cdir, "lane1"), exist_ok=True)
        with open(os.path.join(cdir, "SUMMARY.md"), "w") as fh:
            fh.write("# cycle 1\n\nLane 1 recorded blind.\n")
        try:
            world["runs"] = {"GimmeSomeSlack": [{"unit": bk()[0]["unit"], "item": bk()[0]["item"],
                                                  "at": BLIND_CLOCK + 5, "live": False}]}
            r1 = rtick(kfx, at=600)
            uk = bk()[0]["unit"]
            kill(uk, state="finished", returned=True)
            r2 = rtick(kfx, at=660)
            a2 = launches()[-1]
            ok(g(r1)["decision"] == "cycle_unfinished" and g(r2)["decision"] == "launched" and len(launches()) == 2
               and "## Resume" in open(a2[a2.index("--brief-file") + 1]).read(),
               "a half-written cycle: unfinished while its run reads as having ended by itself, resumed once it reads "
               "killed (%s, %s: %s)" % (g(r1)["decision"], g(r2)["decision"], g(r2)["why"][:100]))
            rc, text, _ = M.launch_mod(root, "GimmeSomeSlack", 20, "SOME_ITEM", model="opus")
            ok(rc == 2 and "owes no blind cycle" in text, "launch_mod without resume still refuses the half-written "
                                                          "cycle (%s)" % text[:80])
        finally:
            shutil.rmtree(cdir, ignore_errors=True)

        reset()
        r0 = rtick(kfx)
        world["killed"] = {}
        world["runs"] = {"GimmeSomeSlack": [{"unit": bk()[0]["unit"], "item": bk()[0]["item"], "at": BLIND_CLOCK + 5,
                                              "live": False}]}
        r1 = rtick(kfx, at=600)
        ok(g(r1)["decision"] == "stopped" and len(launches()) == 1,
           "a judge that ended by itself and wrote no record still spends the cycle (%s)" % g(r1)["decision"])
        kill(bk()[0]["unit"], state="finished", kept=True)
        r2 = rtick(kfx, at=660)
        ok(g(r2)["decision"] == "stopped" and "KEPT" in g(r2)["why"] and len(launches()) == 1,
           "a killed judge whose return KEPT its clone: stopped naming the return command (%s)" % g(r2)["why"][:100])

        # detached_helper.killed reads the record: no result JSON and a signal stop or a vanished unit is a kill
        kd = tempfile.mkdtemp(prefix="selftest_killed_")
        empty, full = os.path.join(kd, "e.json"), os.path.join(kd, "f.json")
        open(empty, "w").close()
        with open(full, "w") as fh:
            json.dump({"type": "result", "result": "done", "total_cost_usd": 1.0}, fh)

        def rec_(out, **kw):
            return dict(dict(unit="u-x", out=out, err=os.path.join(kd, "none.err"), at=BLIND_CLOCK), **kw)

        gone = lambda argv, **kw: subprocess.CompletedProcess(argv, 0, "inactive\n", "")   # noqa: E731
        st_hand = DH.outcome(rec_(empty), {})[0]
        st_term = DH.outcome(rec_(empty), {"SERVICE_RESULT": "exit-code", "EXIT_CODE": "exited", "EXIT_STATUS": "143"})[0]
        st_fail = DH.outcome(rec_(empty), {"SERVICE_RESULT": "exit-code", "EXIT_CODE": "exited", "EXIT_STATUS": "1"})[0]
        st_time = DH.outcome(rec_(empty), {"SERVICE_RESULT": "timeout", "EXIT_CODE": "killed", "EXIT_STATUS": "TERM"})[0]
        ok(st_hand.startswith("killed") and st_term.startswith("killed") and not st_fail.startswith("killed")
           and not st_time.startswith("killed"),
           "finish names a kill: by hand on a vanished unit, or a TERM exit with no result; a failure or its own time "
           "limit is not (%s | %s | %s | %s)" % (st_hand, st_term, st_fail, st_time))
        ok(DH.killed(rec_(empty, status="finished", result=st_term)) and DH.killed(rec_(empty, status="running"), gone)
           and not DH.killed(rec_(full, status="running"), gone) and not DH.killed(rec_(empty, status="finished",
                                                                                         result=st_fail))
           and not DH.killed(rec_(empty, status="finished", result=st_time)),
           "detached_helper.killed: a TERM stop or a dead unit with no result JSON is a kill; a result written, a plain "
           "failure or a timeout is not")
        recs = {"u-k": rec_(empty, unit="u-k", status="running"), "u-ok": rec_(full, unit="u-ok", status="running")}
        kr = MD.killed_runs([{"unit": "u-k", "item": "X_BLIND_CYCLE_TWO", "live": False},
                             {"unit": "u-ok", "item": "X_BLIND_CYCLE_TWO", "live": False},
                             {"unit": "u-live", "item": "X_BLIND_CYCLE_TWO", "live": True},
                             {"unit": "u-b", "item": "X_BUILD_STAGE_THREE", "live": False}], read=recs.get, runner=gone)
        ok(list(kr) == ["u-k"] and kr["u-k"]["state"] == "running" and not kr["u-k"]["returned"],
           "killed_runs keeps only the ended blind or in-game runs read as killed (%s)" % sorted(kr))
        shutil.rmtree(kd, ignore_errors=True)
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

        fx = {"autonomy": False, "account": lambda: world["account"], "known": lambda: set(), "bridge": bridge,
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

        base = load_cfg()
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

        def t_rule():
            # the fake filer above never meets rimflow's RUNNER spawn rule: ask the real rule about this very spawn
            # (file_and_publish: --from ITEM --for RELENTLESS) and the long-name fallback
            from rimflow import model
            evs = [{"event": "spawn", "seat": "RUNNER", "for": model.read_name("RELENTLESS"), "needs": "game-up",
                    "from": MD.ITEM, "name": n}
                   for n in (filed[0][0], MD.ingame_item_id("X" * 40, 2, set()))]
            return (model.RUNNER_INGAME_FROM == MD.ITEM and "IN_GAME_VISIT_TWO" in evs[1]["name"]
                    and all(model._who_refusal(e, None) is None for e in evs))
        chk(t_rule, "rimflow's RUNNER spawn rule admits the in-game item as file_and_publish spawns it")
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

        # RIMMANDRAKE_ADMIT_INGAME_SPAWN_RUNNER_REFUSES_GAME_UP: a launch refused at the spawn never started; the
        # Conductor's clear releases it and the next tick launches the visit; a run that started is never released
        def t_clear():
            reset()
            refused = "spawn refused: RUNNER spawns only for BENCH ...; got --for BENCH --needs game-up"
            fr = dict(fx, file=lambda item, title, why, **kw: (False, refused))
            r1 = MD.tick(root, on, True, fx=dict(fr, facts=lambda: facts_for(on)), now=T0, page=False)
            r2 = tick(on, at=600)
            c = MD.main(["clear", "Pyrelands", "--why", "selftest"])
            r3 = tick(on, at=1200)
            p = os.path.join(sd, "state.json")
            b = json.load(open(p))["mods"]["Pyrelands"]["ingame_auto"]
            MD.main(["clear", "Pyrelands", "--why", "selftest"])
            kept = json.load(open(p))["mods"]["Pyrelands"]["ingame_auto"]
            return (dec(r1) == "launch_failed" and dec(r2) == "stopped" and c == 0 and dec(r3) == "launched"
                    and len(launches()) == 1 and len(b) == 1 and b[0].get("unit") and kept == b)
        chk(t_clear, "an in-game launch refused at the spawn: the Conductor's clear releases it and the next tick "
                     "launches; a started run survives a clear")

        # RIMMANDRAKE_RETRY_JUDGE_LAUNCH_GIT_LOCK_SPENT_THE_CYCLE: a launch that never started on a transient publish
        # fault retries the same item, up to launch_tries; three in a row stop it naming the count
        lock = "publish: publish stopped: index.lock present (0 s old, under 300 s: another git may be running)"
        refuse = "REFUSED: %s is not on origin/main; publish infrastructure/state/ledger/events/RUNNER.jsonl first"
        published = []

        def fxr(n_fail):
            calls = []

            def launch(mod, cap_, item):
                calls.append(item)
                return (2, refuse % item, None) if len(calls) <= n_fail else fx["launch"](mod, cap_, item)
            return calls, dict(fx, launch=launch,
                               file=lambda item, title, why, **kw: (filed.append((item, title, why, kw)) or True,
                                                                    "filed %s; %s" % (item, lock)),
                               publish=lambda item: (published.append(item) or True, "publish: PUBLISHED test"))

        def rtick(fx_, at=0):
            return MD.tick(root, on, True, fx=dict(fx_, facts=lambda: facts_for(on)), now=T0 + at, page=False)

        def t_retry():
            reset()
            del published[:]
            calls, f1 = fxr(1)
            r1, r2 = rtick(f1), rtick(f1, at=60)
            b = json.load(open(os.path.join(sd, "state.json")))["mods"]["Pyrelands"]["ingame_auto"]
            return (dec(r1) == "launch_retry" and dec(r2) == "launched" and len(launches()) == 1 and len(filed) == 1
                    and filed[0][3].get("needs") == "game-up" and published == [filed[0][0]]
                    and calls == [filed[0][0]] * 2 and len(b) == 1 and b[0].get("unit") and b[0].get("tries") == 2)
        chk(t_retry, "an in-game launch that never started on a git lock: the next tick publishes again and launches "
                     "the same item, one run in the book")

        def t_retry_spent():
            reset()
            calls, f3 = fxr(9)
            rs = [rtick(f3, at=60 * k) for k in range(4)]
            return ([dec(x) for x in rs] == ["launch_retry", "launch_retry", "launch_failed", "stopped"]
                    and "3 times" in rs[3]["mods"]["Pyrelands"]["why"] and len(calls) == 3 and not launches()
                    and len(filed) == 1)
        chk(t_retry_spent, "three transient in-game launch faults in a row: stopped naming the count, no fourth try")
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
    if "--release" in sys.argv[1:]:
        sys.exit(release_main())
    rc = main()
    rc = release_main() or rc
    rc = blind_main() or rc
    sys.exit(ingame_main() or rc)
