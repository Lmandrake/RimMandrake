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
import re
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
# Likewise the live-run cap: the slots_full check puts two runs live and pins max_live to match, so it holds at any shipped max_live
# (2 -> 4 on 2026-11-15 by the owner's card).
FIXTURE_MAX_LIVE = 2
# And every other number the owner tunes, as shipped 2026-11-15 (RIMMANDRAKE_PIN_TUNABLES_OUT_OF_SELFTESTS: tunable_sweep.py
# found these checks red on a doubled cap_usd, settle_s, idle_alarm_min, blind_cap_usd, cycles or runs per visit).
FIXTURE_NUMBERS = {"cap_usd": 15, "settle_s": 180, "idle_alarm_min": 60, "blind_cap_usd": 20, "blind_auto_cycles_per_visit": 3,
                   "ingame_cap_usd": 30, "ingame_auto_runs_per_visit": 1, "steward_cap_usd": 8, "fix_cap_usd": 10,
                   "steward_max_per_version": 12, "stalled_min": 10}


def load_cfg():
    """-> the shipped settings with the fixture numbers (the shipped ones are range-checked where they are read)."""
    return dict(MD.load_cfg(), stage_ceiling_usd=FIXTURE_CEILING, **FIXTURE_NUMBERS)


def fixture(mod, rel):
    """-> the bytes of design/concepts/<mod>/<rel> at FIXTURE_SHA, or None when it was absent there."""
    r = subprocess.run(["git", "-C", REPO, "show", "%s:design/concepts/%s/%s" % (FIXTURE_SHA, mod, rel)],
                       capture_output=True, timeout=60)
    return r.stdout if r.returncode == 0 else None


def no_convergence(root, rd):
    """The fixture convergence source: no dispatch check reads the fixture mods' real rounds (item
    RIMMANDRAKE_ISOLATE_DISPATCH_SELFTEST_FROM_CONVERGENCE); the reading itself is selftest_maturation_convergence's."""
    rd["convergence"] = {}
    return rd


def redden(root, mod, last="3 of 3 runs failed"):
    """PRE_JUDGEMENT_CERTIFICATE cases: turn the mod's first offline bar decider red on its fixture build.
    -> (the table's saved text, that test's id, its file's path)."""
    tp = os.path.join(root, "design", "concepts", mod, "version", "test_table.json")
    saved = open(tp).read()
    tt = json.loads(saved)
    tid = next(d for b in tt["bars"] for d in b.get("offline_decides") or [] if d in tt["tests"])
    tt["tests"][tid]["runs_today"].update(rc=1, result="FAIL", last=last)
    with open(tp, "w") as f:
        json.dump(tt, f, indent=1)
    return saved, tid, os.path.join(root, tt["tests"][tid]["file"])


def restore(root, mod, saved):
    with open(os.path.join(root, "design", "concepts", mod, "version", "test_table.json"), "w") as f:
        f.write(saved)


def ok(cond, what):
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


def git_status():
    return subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--", "design/concepts"],
                          capture_output=True, text=True, timeout=120).stdout


def main():
    import selftest_maturation as SM
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
        SM.certify_fixture(root, FOUR + ("PyrelandsMechanics",))
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

        fx = {"autonomy": False, "convergence": no_convergence, "facts": facts, "account": lambda: world["account"], "known": lambda: set(),
              "clone": lambda: world.get("clone", (0, 0)),
              "file": lambda item, title, why: (filed.append((item, title, why)) or True, "filed %s" % item),
              "launch": lambda mod, cap, item, **kw: M.launch_mod(root, mod, cap, item, model=cfg["model"],
                                                                  seat=cfg["seat"], **kw)}

        def tick(apply=True, at=0):
            return MD.tick(root, cfg, apply, fx=fx, now=CLOCK + at, page=False)

        def reset():
            shutil.rmtree(sd, ignore_errors=True)
            open(log, "w").close()
            del filed[:]
            world.update(live={}, stage_runs={}, last_end={})

        base = load_cfg()
        cfg = dict(base, advancing=list(FOUR) + ["Graffiti", "PyrelandsMechanics"], max_live=4)  # pinned: these rows need several launches in one pass, at any shipped max_live
        world["live"] = {"ExplosiveKnockback": ["rm-detached-bench-rimmandrake-build-knockback-stage-three-1"]}

        # ---- a clone behind past the alarm's 5 min reads an old tree: it launches nothing --------------------------
        # (RIMMANDRAKE_HOLD_TICK_LAUNCHES_ON_STALE_CLONE_GHOST_STEWARD: 51 min behind, it filed a steward run for a
        # blind record whose exit block had landed 5 min before)
        os.makedirs(sd, exist_ok=True)
        with open(os.path.join(sd, "state.json"), "w") as f:
            json.dump({"clone": {"behind_since": CLOCK - 600}}, f)
        world["clone"] = (3, 0)
        rd = tick()
        ok(not launches() and rd["mods"]["FlowWorks"]["decision"] == "stale_clone"
           and any("stale_clone" in x or "behind origin/main" in x for x in rd["needs_conductor"]),
           "a clone 10 min behind launches nothing: FlowWorks reads stale_clone, a Needs Conductor line (%s)"
           % rd["mods"]["FlowWorks"].get("decision"))
        ok(str(rd.get("ledger_runs", "")).startswith("held") and str(rd.get("spend_rows", "")).startswith("held"),
           "nor does it seal, end or spend-record a run from the old tree (its 02:59 publish sealed a 19-line judge "
           "shard empty and dropped a re-seal line): ledger_runs %r, spend_rows %r"
           % (rd.get("ledger_runs"), rd.get("spend_rows")))
        world["clone"] = (3, 0)
        reset()
        world["live"] = {"ExplosiveKnockback": ["rm-detached-bench-rimmandrake-build-knockback-stage-three-1"]}
        rd = tick()
        ok(len(launches()) == 1 and rd["mods"]["FlowWorks"]["decision"] == "launched",
           "the first tick behind (0 min) still launches: a lag under the alarm holds nothing (%s)"
           % rd["mods"]["FlowWorks"].get("decision"))
        world["clone"] = (0, 0)
        reset()
        world["live"] = {"ExplosiveKnockback": ["rm-detached-bench-rimmandrake-build-knockback-stage-three-1"]}

        # ---- the first tick: one launch, on FlowWorks only ----------------------------------------------------------
        rd = tick()
        d = {m: r["decision"] for m, r in rd["mods"].items()}
        ok(len(launches()) == 1 and d["FlowWorks"] == "launched", "one builder launches, on FlowWorks (%s)" % d)
        ok(d["ExplosiveKnockback"] == "live", "Explosive Knockback has a live run: no second builder")
        ok(not rd.get("convergence") and not any("DIVERGING" in x for x in rd["needs_conductor"]),
           "the fixture convergence source: no real mod's rounds reach a dispatch check (%s)"
           % [x for x in rd["needs_conductor"] if "DIVERGING" in x])
        seen = []

        def one_diverging(root_, rd_):
            seen.append(root_)
            rd_.setdefault("needs_conductor", []).append("FlowWorks Stage 3 (coverage) DIVERGING, fixture")
            return rd_
        rdc = MD.tick(root, cfg, False, fx=dict(fx, convergence=one_diverging), now=CLOCK, page=False)
        ok(seen == [root] and "FlowWorks Stage 3 (coverage) DIVERGING, fixture" in rdc["needs_conductor"],
           "the tick reads convergence through its fx seam, on its own root (%s)" % seen)
        ok(d["GimmeSomeSlack"] == "hand_step" and any(x.startswith("GimmeSomeSlack: hand step")
                                                       for x in rd["needs_conductor"]),
           "Gimme Some Slack owes a hand step: a Needs Conductor line, no launch")
        ok(d["Pyrelands"] == "ready" and any("ready to advance" in x for x in rd["needs_conductor"]),
           "Pyrelands passes every exit test: 'ready to advance' for the Conductor, never an advance")
        # PRE_JUDGEMENT_CERTIFICATE: an offline build whose exit tests pass but whose certificate refuses waits on it
        saved, tid, _ = redden(root, "Pyrelands")
        rdx = MD.tick(root, cfg, False, fx=fx, now=CLOCK, page=False)
        ok(rdx["mods"]["Pyrelands"]["decision"] == "certificate" and "3 of 3" in " ".join(
            x for x in rdx["needs_conductor"] if x.startswith("Pyrelands:"))
           and "its certificate" in str(rdx["mods"]["Pyrelands"].get("waits_on")),
           "a red offline decider: Pyrelands waits on its certificate (the test's own last line), not 'ready to "
           "advance' (%s)" % rdx["mods"]["Pyrelands"]["decision"])
        restore(root, "Pyrelands", saved)
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
        # RIMMANDRAKE_SIZE_DISPATCH_BUILDS_THIRTY_THREE_BARS_ONE_RUN: one builder took all 33 refused Graffiti bars and
        # stalled; a set above build_batch_bars goes out in even batches of about that many, judged on the whole set
        bars7 = [i for i in M.refused_ids(M.build_facts(root, "FlowWorks")) or [] if i != "table_version"]
        br = open(a[a.index("--brief-file") + 1]).read() if a else ""
        bt = rd["mods"]["FlowWorks"].get("batch") or []
        ok(base.get("build_batch_bars") == 6 and len(bars7) == 7 and len(bt) == 4 and set(bt) < set(bars7),
           "7 refused bars over a batch of 6 go out as an even 4 + 3: this run takes 4 (%s)" % bt)
        nbar = lambda t: len(re.findall(r"^- \*\*\S+\*\* \(", t, re.M))      # a bar line, not the journal's
        ok(nbar(br) == 4 and all("**%s**" % b in br for b in bt)
           and not any("**%s**" % b in br for b in set(bars7) - set(bt))
           and "this run's batch: 4 of the 7" in br and all("`%s`" % b in br for b in set(bars7) - set(bt)),
           "the brief lists only the batch's bars and names the other 3 as later runs' (%d listed)" % nbar(br))
        ok(filed and "4 of the 7 bars" in filed[0][1], "the item title says 4 of the 7 bars (%s)" % (
            filed[0][1] if filed else None))
        ok([MD.batch_of(list("abcdefghijklm"), 6), MD.batch_of(list("abcdef"), 6), MD.batch_of(list("abcdefg"), 0),
            len(MD.batch_of(["b%02d" % k for k in range(33)], 6)), MD.batch_of([], 6)]
           == [list("abcde"), list("abcdef"), list("abcdefg"), 6, []],
           "batch_of: 13 -> 5 (even thirds), 6 -> whole, size 0 -> whole, 33 -> 6, empty -> empty")
        text_all, _ = M.brief_text(root, "FlowWorks", 15)
        ok(nbar(text_all) == 7 and "this run's batch" not in text_all,
           "a brief with no batch still lists every refused bar")
        rcb, tb, _ = M.launch_mod(root, "FlowWorks", 15, "SOME_ITEM", bars=bt[:1] + ["no_such_bar"])
        ok(rcb == 2 and "no_such_bar" in tb, "launch_mod refuses a batch naming a bar not refused (%s)" % tb[:80])
        rec = json.load(open(os.path.join(sd, "state.json")))
        unit = rec["mods"]["FlowWorks"]["watch"]["unit"]

        # ---- the run is live: nothing more; it ends with no fewer refusals: stopped for good -----------------------
        ok((rd.get("clone") or {}).get("measured") and rd["clone"].get("behind") == 0
           and rec.get("clone", {}).get("level_at") == CLOCK,
           "the tick measures its own clone: level, last level kept in state.json (%s)" % rd.get("clone"))
        world["live"]["FlowWorks"] = [unit]
        world["clone"] = (4, 1)      # RIMMANDRAKE_UNJAM_DISPATCH_CLONE_TWO_WRITERS_BLOCK_EACH_REBASE: stuck behind
        rd = tick(at=600)
        ok(rd["clone"].get("behind") == 4 and rd["clone"].get("behind_min") == 0.0
           and rd["clone"].get("behind_since") == CLOCK + 600 and rd["clone"].get("level_at") == CLOCK,
           "first tick behind: behind_since set, 0 min, last level unchanged (%s)" % rd["clone"])
        ok(len(launches()) == 1, "while the run is live, no second launch on FlowWorks")
        world["live"].pop("FlowWorks")
        world["last_end"]["FlowWorks"] = CLOCK + 900
        world["clone"] = (None, "fetch refused and origin/main unmoved for 20 min: x")
        rd = tick(at=960)      # 60 s after the end: its files may not have reached this clone yet
        ok(rd["clone"].get("measured") is False and "fetch refused" in rd["clone"].get("why", "")
           and json.load(open(os.path.join(sd, "state.json")))["clone"].get("behind_since") == CLOCK + 600,
           "a blind fetch is UNMEASURED, never level, and keeps the behind clock (%s)" % rd["clone"])
        ok(len(launches()) == 1 and rd["mods"]["FlowWorks"]["decision"] == "settling"
           and "stopped" not in json.load(open(os.path.join(sd, "state.json")))["mods"]["FlowWorks"]
           and "watch" in json.load(open(os.path.join(sd, "state.json")))["mods"]["FlowWorks"],
           "a tick 60 s after a run ends neither judges the refused count nor launches; the watch is kept")
        world["clone"] = (6, 0)
        rd = tick(at=1200)
        ok(rd["clone"].get("behind_min") == 10.0, "minutes behind count from the first tick behind, not from commit "
           "dates (%s)" % rd["clone"].get("behind_min"))
        ok(len(launches()) == 1 and rd["mods"]["FlowWorks"]["decision"] == "stopped"
           and any(x.startswith("FlowWorks: stopped") for x in rd["needs_conductor"]),
           "the run ended with the same 7 refused: stopped, a Needs Conductor line, no relaunch")
        world["clone"] = (0, 0)
        rd = tick(at=1800)
        ok(rd["clone"].get("behind") == 0 and rd["clone"].get("behind_min") == 0.0
           and rd["clone"].get("level_at") == CLOCK + 1800 and not rd["clone"].get("behind_since"),
           "levelled again: the behind clock clears, last level is this tick (%s)" % rd["clone"])
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
        rd = none_launched(one, "the stage's dollars past the ceiling", "stopped", stage_runs={"FlowWorks": {"u1": 61.0}})
        ok("weighted tokens" in rd["mods"]["FlowWorks"]["why"] and not re.search(r"USD|\$\s*\d",
                                                                                  rd["mods"]["FlowWorks"]["why"]),
           "the ceiling pause says weighted tokens, never a dollar figure (%s)" % rd["mods"]["FlowWorks"]["why"][:160])
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

        # the owner, 2026-11-16: "Please speak in terms of weighted tokens not money." The pause line and its release
        # command say weighted tokens; the ceiling is still kept in list dollars inside (RIMMANDRAKE_ENACT_TOKENS_NOT_
        # DOLLARS_NO_LIVE_HOLD)
        cmd = ("maturation_dispatch.py release FlowWorks --stage offline_build --read-tokens %d --tokens %d --why"
               % (MD.to_wt(50.0), MD.to_wt(5)))
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
           and "--read-tokens %d --tokens %d " % (MD.to_wt(65.0), MD.to_wt(20)) in fw(rd), "the released run's USD 15 spent (65): the spent release frees "
           "nothing and the mod re-pauses at the next ceiling, naming the next release (%s)" % fw(rd))
        for r, what, says in ((rel(mod="ExplosiveKnockback"), "a release for another mod", cmd),
                              (rel(stage="blind_challenge"), "a release for another stage", cmd),
                              (rel(read_usd=40.0), "a release that read another spend (USD 40)", "the spend is now %s" % MD.wt(50.0)),
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

        # ---- a Stage 3 launch that never started on a transient fault retries itself (owner, 2026-11-15: the pipeline
        # fixes its own defects; item RIMMANDRAKE_RETRY_STAGE_THREE_LAUNCH_TRANSIENT_FAULT_NOT_STOPPED). Before, a git
        # lock while filing stopped the mod for good and wrote a Needs Conductor line a hand had to `clear`.
        def t3(fx_, at=0):
            return MD.tick(root, one, True, fx=dict(fx_, facts=lambda: facts_for(one)), now=CLOCK + at, page=False)

        def d3(rd_):
            return rd_["mods"]["FlowWorks"]["decision"]

        def nc3(rd_):   # FlowWorks's own lines: the fixture's other mods carry real stage data (a DIVERGING line)
            return [x for x in rd_.get("needs_conductor") or [] if x.startswith("FlowWorks:")]

        def file_flaky(n_fail):
            calls = []

            def file_(item, title, why):
                calls.append(item)
                if len(calls) <= n_fail:
                    return False, "ingest.lock stayed busy; nothing filed"
                return fx["file"](item, title, why)
            return file_, calls

        reset()
        f1, c1 = file_flaky(1)
        r1, r2 = t3(dict(fx, file=f1)), t3(dict(fx, file=f1), at=600)
        st1 = json.load(open(os.path.join(sd, "state.json")))["mods"]["FlowWorks"]
        ok(d3(r1) == "launch_retry" and not nc3(r1) and d3(r2) == "launched" and len(launches()) == 1
           and not st1.get("stopped"),
           "a Stage 3 filing that hit a lock retries on the next tick, no stop, no Needs Conductor line (%s, %s, %s)"
           % (d3(r1), d3(r2), nc3(r1)))
        reset()
        pubs, lc = [], []

        def launch_once_unpublished(mod, cap_, item, **kw):
            lc.append(item)
            if len(lc) == 1:
                return 1, "refused: %s is not on origin/main" % item, None
            return fx["launch"](mod, cap_, item)
        fx_b = dict(fx, launch=launch_once_unpublished, publish=lambda item: (pubs.append(item) or True, "published"))
        r1, r2 = t3(fx_b), t3(fx_b, at=600)
        ok(d3(r1) == "launch_retry" and d3(r2) == "launched" and len(filed) == 1 and pubs == [filed[0][0]]
           and lc == [filed[0][0]] * 2 and r2["mods"]["FlowWorks"].get("item") == filed[0][0],
           "a Stage 3 launch refused as not yet on origin retries the SAME item, published again, never re-filed "
           "(filed %s, published %s, launched %s)" % ([x[0] for x in filed], pubs, lc))
        reset()
        f9, _ = file_flaky(99)
        rs = [t3(dict(fx, file=f9), at=600 * i) for i in range(4)]
        ok([d3(x) for x in rs] == ["launch_retry", "launch_retry", "launch_failed", "stopped"] and not launches()
           and nc3(rs[2]),
           "a transient fault that outlasts launch_tries stops with a Needs Conductor line (%s)" % [d3(x) for x in rs])

        # ---- a steward or fixer run is not a builder (RIMMANDRAKE_EXEMPT_STEWARD_RUNS_FROM_BUILDER_PROGRESS_STOP).
        # Graffiti 2026-11-15: its preflight steward moved it into the offline build and was still live, so the tick
        # watched it as a builder and wrote "stopped, 33 -> 33" when it ended. Its own book and cap govern its retries.
        for book, key in (("steward", "0.1.0|preflight"), ("fixers", "RIMMANDRAKE_FIX_FLOWWORKS_SOME_TICKET")):
            reset()
            u = "rm-detached-bench-rimmandrake-%s-flowworks-1" % book
            os.makedirs(sd, exist_ok=True)
            with open(os.path.join(sd, "state.json"), "w") as f:
                json.dump({"mods": {"FlowWorks": {book: {key: {"unit": u, "item": "X", "at": CLOCK - 60}}}}}, f)
            world["live"] = {"FlowWorks": [u]}
            r1 = t3(fx)
            world["live"] = {}
            r2 = t3(fx, at=600)
            s2 = json.load(open(os.path.join(sd, "state.json")))["mods"]["FlowWorks"]
            ok(d3(r1) == "live" and d3(r2) == "launched" and not s2.get("stopped") and not nc3(r2)
               and len(launches()) == 1 and (s2.get("last_run") or {}).get("unit") == u,
               "a %s run that ends with the refused bars unchanged is not judged as a builder: no stop, the builder "
               "launches (%s -> %s, stopped %s)" % (book, d3(r1), d3(r2), s2.get("stopped")))
        # the stop such a run already wrote (Graffiti's, before the fix) lifts itself on the next tick
        reset()
        u = "rm-detached-bench-rimmandrake-steward-flowworks-preflight-s-1"
        os.makedirs(sd, exist_ok=True)
        with open(os.path.join(sd, "state.json"), "w") as f:
            json.dump({"mods": {"FlowWorks": {
                "steward": {"0.1.0|preflight": {"unit": u, "item": "X", "at": CLOCK - 900}},
                "last_run": {"unit": u, "refused_before": 7, "refused_after": 7, "ended_seen": CLOCK - 300},
                "stopped": {"ids": [], "at": CLOCK - 300,
                            "why": "run %s ended and the refused bars went 7 -> 7, none resolved" % u}}}}, f)
        r1 = t3(fx)
        ok(d3(r1) == "launched" and "as a builder" in str(r1["mods"]["FlowWorks"].get("stop_lifted"))
           and not nc3(r1) and len(launches()) == 1,
           "a stop already written on a steward run lifts itself, the builder launches (%s, %s)"
           % (d3(r1), r1["mods"]["FlowWorks"].get("stop_lifted")))

        # ---- the idle reading and its Operations family ---------------------------------------------------------------
        reset()
        gss = dict(base, advancing=["GimmeSomeSlack"])
        os.makedirs(sd, exist_ok=True)
        with open(os.path.join(sd, "state.json"), "w") as f:
            json.dump({"mods": {"GimmeSomeSlack": {"owed_since": CLOCK - 2 * 3600}},
                       "clone": {"behind_since": CLOCK - 480, "level_at": CLOCK - 540}}, f)
        world["clone"] = (3, 0)
        rd = MD.tick(root, gss, True, fx=dict(fx, facts=lambda: facts_for(gss)), now=CLOCK, page=False)
        world["clone"] = (0, 0)
        ok(rd["mods"]["GimmeSomeSlack"].get("klass") == "paused" and rd["idle_owed_max_min"] == 0
           and rd["idle_owed_mods"] == [],
           "a paused mod (only a hand step is left, the steward is off) is not idle owed (%s)" % rd["idle_owed_max_min"])
        # a genuinely idle mod (klass wait, nothing on it) alarms: put its reading where ops_watch reads it
        idle = MD.reading(gss, [{"mod": "GimmeSomeSlack", "stage": "offline_build", "owed": "ready to advance",
                                 "live": [], "decision": "queued", "klass": "wait", "idle_min": 120}], CLOCK)
        ok(idle["idle_owed_max_min"] == 120 and idle["idle_owed_mods"] == ["GimmeSomeSlack"],
           "a planted idle mod (owed 2 h, nothing on it) reads 120 min idle (%s)" % idle["idle_owed_max_min"])
        rp = os.path.join(MD.sdir(), "reading.json")
        cur = json.load(open(rp))
        cur.update({k: idle[k] for k in ("idle_owed_max_min", "idle_owed_mods", "idle_alarm_min")})
        json.dump(cur, open(rp, "w"))
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
        got = OW.c_maturation(CLOCK + 60, {}, {}).get("maturation.clone_behind_min") or {}
        ok(got.get("v") == 8.0 and got.get("m") == "MEASURED" and (got.get("x") or {}).get("behind") == 3,
           "ops_watch reads the dispatch clone's minutes behind from the reading (%s)" % got)
        t = [x for x in rules["targets"] if x.get("name") == MD.CLONE_ALARM_NAME]
        ok(len(t) == 1 and t[0]["key"] == "maturation.clone_behind_min" and t[0]["alarm"] is True
           and t[0]["op"] == ">" and t[0]["value"] == 5,
           "one fixed-id alarm, %s, when the dispatch clone is behind over 5 min" % MD.CLONE_ALARM_NAME)
        rd = MD.tick(root, gss, True, fx=dict(fx, facts=lambda: facts_for(gss)), now=CLOCK + 60, page=False)
        got = OW.c_maturation(CLOCK + 90, {}, {}).get("maturation.clone_behind_min") or {}
        ok(got.get("v") == 0 and got.get("m") == "MEASURED", "synced again: the reading is 0, so the alarm re-arms (%s)"
           % got)
        world["clone"] = (None, "clone unreadable: x")
        rd = MD.tick(root, gss, True, fx=dict(fx, facts=lambda: facts_for(gss)), now=CLOCK + 120, page=False)
        world["clone"] = (0, 0)
        got = OW.c_maturation(CLOCK + 150, {}, {}).get("maturation.clone_behind_min") or {}
        ok(got.get("m") == "UNMEASURED", "a clone the tick cannot read is UNMEASURED, never 0 (%s)" % got)
        reset()
        rd = MD.tick(root, gss, True, fx=dict(fx, facts=lambda: facts_for(gss)), now=CLOCK, page=False)
        ok(rd["idle_owed_max_min"] == 0 and rd["mods"]["GimmeSomeSlack"].get("klass") == "paused",
           "a mod first seen owed but paused (hand step, steward off) is not idle owed (%s min)" % rd["idle_owed_max_min"])
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


def clone_status_main():
    """The dispatch clone's distance from origin (clone_counts, on real git) and `status`'s first line and dead units
    (RIMMANDRAKE_UNJAM_DISPATCH_CLONE_TWO_WRITERS_BLOCK_EACH_REBASE; the status reading that went stale unsaid)."""
    root = tempfile.mkdtemp(prefix="md_clone_")
    try:
        bare, disp, rival = (os.path.join(root, n) for n in ("origin.git", "dispatch", "rival"))

        def sh(*a, cwd=None):
            return subprocess.run(["git"] + list(a), cwd=cwd, capture_output=True, text=True, timeout=60)
        sh("init", "-q", "--bare", "-b", "main", bare)
        sh("clone", "-q", bare, rival)
        for d in (rival,):
            sh("config", "user.email", "st@x", cwd=d)
            sh("config", "user.name", "st", cwd=d)
        sh("commit", "-q", "--allow-empty", "-m", "a", cwd=rival)
        sh("push", "-q", "origin", "HEAD:main", cwd=rival)
        sh("clone", "-q", bare, disp)
        ok(MD.clone_counts(disp) == (0, 0), "a level clone reads (0 behind, 0 ahead) (%s)" % (MD.clone_counts(disp),))
        for m in ("b", "c"):
            sh("commit", "-q", "--allow-empty", "-m", m, cwd=rival)
        sh("push", "-q", "origin", "HEAD:main", cwd=rival)
        ok(MD.clone_counts(disp) == (2, 0), "the tick's own fetch sees origin move: 2 behind (sanity probe: the "
           "instrument can see) (%s)" % (MD.clone_counts(disp),))
        sh("remote", "set-url", "origin", os.path.join(root, "gone.git"), cwd=disp)
        ref = os.path.join(disp, ".git", "logs", "refs", "remotes", "origin", "main")
        os.utime(ref, (CLOCK - 3600, CLOCK - 3600))
        got = MD.clone_counts(disp)
        ok(got[0] is None and "fetch refused" in got[1], "a refused fetch on an old ref is no reading, not level (%s)"
           % (got,))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    states = {"rm-maturation-dispatch.timer": "inactive", "rm-role-designer-17": "inactive", "rm-blind-x-1": "active"}
    rd = {"at": CLOCK - 600, "at_pac": "old", "clone": {"measured": True, "behind": 49, "ahead": 7, "behind_min": 38.0,
                                                        "level_pac": "11:41 AM"},
          "mods": {"Pyrelands": {"klass": "wait", "decision": "designer_wait", "for_min": 40,
                                 "status": "waiting on rm-role-designer-17"},
                   "Graffiti": {"klass": "wait", "decision": "live", "for_min": 3, "status": "waiting on rm-blind-x-1"}}}
    lines = MD.status_lines(rd, CLOCK, unit_state=lambda u: states.get(u, "unknown"))
    ok(lines[0].startswith("reading is 10 min old: the tick is paused/stopped"),
       "a reading older than two ticks says its age first, in plain words (%r)" % lines[0])
    ok(any(ln.startswith("clone: BEHIND origin/main by 49 (ahead 7) for 38.0 min") for ln in lines),
       "status shows the clone's distance and minutes behind")
    py = [ln for ln in lines if ln.startswith("Pyrelands")]
    gf = [ln for ln in lines if ln.startswith("Graffiti")]
    ok(py and "DEAD: rm-role-designer-17 inactive" in py[0], "a wait on a dead unit is marked DEAD (%s)" % py)
    ok(gf and "DEAD" not in gf[0], "a wait on a live unit is not (%s)" % gf)
    states["rm-maturation-dispatch.timer"] = "active"
    lines = MD.status_lines(dict(rd, at=CLOCK - 30), CLOCK, unit_state=lambda u: states.get(u, "unknown"))
    ok(lines[0] == "reading at old", "a fresh reading leads with its time as before (%r)" % lines[0])
    lines = MD.status_lines(rd, CLOCK, unit_state=lambda u: states.get(u, "unknown"))
    ok(lines[0].startswith("reading is 10 min old: the tick is not writing it"),
       "a stale reading with its timer active says the tick is not writing it (%r)" % lines[0])
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


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
        tp = os.path.join(tempfile.mkdtemp(dir=sd), "releases.jsonl")
        rc, out = run("FlowWorks", "--stage", "in_game", "--read-tokens", str(MD.to_wt(40.0)), "--tokens",
                      str(MD.to_wt(30)), "--why", "selftest tokens", "--by", "BENCH",
                      RM_MATURATION_DISPATCH_DIR=os.path.dirname(tp))
        tr = MD.read_releases(tp)[0]
        ok(rc == 0 and len(tr) == 1 and abs(tr[0]["read_usd"] - 40) <= MD.READ_SLACK
           and abs(tr[0]["release_usd"] - 30) <= MD.READ_SLACK and "weighted tokens" in out
           and not re.search(r"USD|\$\s*\d", out),
           "release takes the pause line's weighted tokens (--read-tokens/--tokens) and says tokens, never dollars (%s)"
           % out[:160])
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
        ok(lst.returncode == 0 and "FlowWorks" in lst.stdout and "read %s" % MD.wt(40) in lst.stdout
           and "released %s" % MD.wt(30) in lst.stdout and not re.search(r"USD|\$\s*\d", lst.stdout) and "selftest release" in lst.stdout and "1 malformed" in lst.stdout,
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
        SM.certify_fixture(root, FOUR)
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

        filed, reruns = [], []
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

        fx = {"autonomy": False, "convergence": no_convergence, "account": lambda: world["account"], "known": lambda: set(),
              "file": lambda item, title, why: (filed.append((item, title, why)) or True, "filed %s" % item),
              "launch": lambda mod, cap, item, **kw: M.launch_mod(root, mod, cap, item, model="opus", seat="BENCH",
                                                                  **kw),
              # the zero-token certificate rerun at the cycle gate, never a real systemd-run from a selftest
              "cert_rerun": lambda mod, key: (reruns.append((mod, key)) or 0, "STARTED rm-cert-rerun-t%d" % len(reruns),
                                              "rm-cert-rerun-t%d" % len(reruns))}

        def tick(c, at=0, apply=True):
            return MD.tick(root, c, apply, fx=dict(fx, facts=lambda: facts_for(c)), now=BLIND_CLOCK + at, page=False)

        def reset():
            shutil.rmtree(sd, ignore_errors=True)
            open(log, "w").close()
            del filed[:]
            world.update(live={}, last_end={}, runs={}, box_runs={}, ended={}, killed={})

        def need(rd, mod):
            return " ".join(x for x in rd["needs_conductor"] if x.startswith(mod + ":"))

        real, base = MD.load_cfg(), load_cfg()
        ok(real.get("blind_enabled") is True and isinstance(real.get("blind_cap_usd"), (int, float))
           and real["blind_cap_usd"] > 0 and isinstance(real.get("blind_auto_cycles_per_visit"), int)
           and 1 <= real["blind_auto_cycles_per_visit"] <= M.CYCLE_LIMIT,
           "the settings: blind launches on, a positive cap, automatic cycles per visit within his CYCLE_LIMIT (%s, %s, %s)" % (
               real.get("blind_enabled"), real.get("blind_cap_usd"), real.get("blind_auto_cycles_per_visit")))
        gss = dict(base, advancing=["GimmeSomeSlack"], blind_auto_cycles_per_visit=1)   # the spent-visit mechanism, at 1
        cap = "%g" % base.get("blind_cap_usd", 0)

        # ---- PRE_JUDGEMENT_CERTIFICATE: no judge goes in while a program can see a bar red or run on another build --
        saved, tid, tfile = redden(root, "GimmeSomeSlack")
        rd = tick(gss)
        d = rd["mods"]["GimmeSomeSlack"]
        ok(d["decision"] == "certificate" and not launches() and not filed and "3 of 3" in need(rd, "GimmeSomeSlack")
           and "certificate GimmeSomeSlack --to blind_challenge" in need(rd, "GimmeSomeSlack"),
           "cycle 1 owed but a deciding test is red: no judge, a Needs Conductor line with the test's last line and the "
           "certificate command (%s: %s)" % (d["decision"], d["why"][:80]))
        restore(root, "GimmeSomeSlack", saved)
        with open(tfile, "a") as f:
            f.write("# edited after its recorded run\n")
        rd = tick(gss, at=60)
        # RIMMANDRAKE_RERUN_STALE_CERTIFICATE_AT_VISIT_AND_CYCLE_GATES: the fix `certificate --run` is the tick's own
        # zero-token rerun now (it was a Needs Conductor line, and Gimme Some Slack sat on it 137 min at its visit gate)
        ok(rd["mods"]["GimmeSomeSlack"]["decision"] == "launched" and not launches() and len(reruns) == 1
           and reruns[0][0] == "GimmeSomeSlack",
           "a deciding test edited after its recorded run: no judge, the tick starts the zero-token `certificate --run` "
           "itself (%s: %s; reruns %s)" % (rd["mods"]["GimmeSomeSlack"]["decision"],
                                           str(rd["mods"]["GimmeSomeSlack"].get("why"))[:120], reruns))
        rd = tick(gss, at=120)
        ok(rd["mods"]["GimmeSomeSlack"]["decision"] == "live" and not launches() and len(reruns) == 1,
           "a deciding test edited after its recorded run: the next tick, the rerun running, still no judge and no "
           "second rerun (%s)" % rd["mods"]["GimmeSomeSlack"]["decision"])
        del reruns[:]
        SM.certify_fixture(root, ["GimmeSomeSlack"])
        reset()

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
        # RIMMANDRAKE_PAUSE_HAND_RUN_ONLY_ON_JUDGE_VERB_ITEMS: a builder or fixer whose item merely has BLIND in it is
        # no blind judge (2026-11-17: Pyrelands paused 416 min on UNSTICK_DISPATCH_BLIND_CYCLES_..., Graffiti 545 min
        # on BUILD_GRAFFITI_RAIDER_PRESSURE_BLIND_FOUND_ZERO_HITS); a JUDGE/CHALLENGE/PILOT item still is.
        judge_item = world["runs"]["FlowWorks"][0]["item"]
        for other in ("RIMMANDRAKE_UNSTICK_DISPATCH_BLIND_CYCLES_WAITED_SIX_HOURS",
                      "RIMMANDRAKE_BUILD_FLOWWORKS_RAIDER_PRESSURE_BLIND_FOUND_ZERO_HITS",
                      "RIMMANDRAKE_FIX_DESIGNER_STALL_READING_BLIND_TO_CODEX_LANE"):
            world["runs"]["FlowWorks"][0]["item"] = other
            rd = tick(fw, apply=False)
            ok(rd["mods"]["FlowWorks"]["decision"] != "hand_run_seen" and not launches(),
               "a non-judge run %s is no hand-launched blind cycle (%s)" % (other, rd["mods"]["FlowWorks"]["decision"]))
        world["runs"]["FlowWorks"][0]["item"] = judge_item
        ok([i for i in ("RIMMANDRAKE_JUDGE_PYRELANDS_BLIND_CYCLE_TWO_TESTS_FIRST",
                        "RIMMANDRAKE_PILOT_BLIND_CHALLENGE_ON_KNOCKBACK_NEVER_RUN_BEFORE",
                        "RIMMANDRAKE_CHALLENGE_GSS_BLIND_RESTS_ON_ONE_TEST", "X_BLIND_CYCLE_TWO")
            if not MD._is_blind_item(i)] == []
           and [i for i in ("RIMMANDRAKE_BUILD_BLIND_CHALLENGE_LAUNCHER_FOUR_MODS_PARKED",
                            "RIMMANDRAKE_PROVE_SPEND_BLIND_DETACHED_RUN_ONE_TINY_TURN",
                            "RIMMANDRAKE_JUDGE_PYRELANDS_IN_GAME_VISIT_TWO", "") if MD._is_blind_item(i)] == [],
           "_is_blind_item: a judge verb with BLIND is a blind run; any other verb, or no BLIND, is not")
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
        ok("release GimmeSomeSlack --stage blind_challenge --read-tokens %d --tokens %d --why" % (
            MD.to_wt(45.0), MD.to_wt(5)) in rd["mods"]["GimmeSomeSlack"]
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

        fx = {"autonomy": False, "convergence": no_convergence, "account": lambda: world["account"], "known": lambda: set(), "bridge": bridge,
              # the zero-token certificate rerun at the visit gate, never a real systemd-run from a selftest
              "cert_rerun": lambda mod, key: (1, "selftest: no real certificate rerun", None),
              "file": lambda item, title, why, **kw: (filed.append((item, title, why, kw)) or True, "filed %s" % item),
              "launch": lambda mod, cap, item, **kw: M.launch_mod(root, mod, cap, item, model="opus", seat="BENCH",
                                                                  bridge=lambda p, s: world["bridge"], **kw)}

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

        real, base = MD.load_cfg(), load_cfg()
        # ingame_enabled shipped false and was set true 2026-11-15 by the Conductor once the first visit (Pyrelands)
        # had run by hand, as the settings' _ingame_doc says; the pin is now "a bool", and the off case is built
        # explicitly below rather than read from the shipped file.
        chk(lambda: isinstance(real.get("ingame_enabled"), bool) and isinstance(real.get("ingame_cap_usd"), (int, float))
            and real["ingame_cap_usd"] > 0 and isinstance(real.get("ingame_auto_runs_per_visit"), int)
            and real["ingame_auto_runs_per_visit"] >= 1 and real.get("ingame_model") == "opus",
            "the settings as shipped: in-game launches a bool (the Conductor ran the first by hand), a positive cap, at "
            "least one automatic run per visit, opus (%s, %s, %s)" % (real.get("ingame_enabled"), real.get("ingame_cap_usd"),
                                                                     real.get("ingame_auto_runs_per_visit")))
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

        # ---- PRE_JUDGEMENT_CERTIFICATE: no visit goes in while a deciding test is red -----------------------------
        def t_cert():
            saved, _, _ = redden(root, "Pyrelands")
            try:
                r = tick(on)
                return (dec(r) == "certificate" and not launches() and not filed and not asked
                        and "3 of 3" in need(r, "Pyrelands") and "--to in_game" in need(r, "Pyrelands"))
            finally:
                restore(root, "Pyrelands", saved)
                reset()
        chk(t_cert, "on, visit 1 owed, a deciding test red: no live driver, the bridge not even asked, the certificate's "
                    "path to pass on a Needs Conductor line")

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
                   # 28: the short form is exactly 64; a 40-char mod name has no name `file` takes (it once got 76)
                   for n in (filed[0][0], MD.ingame_item_id("X" * 28, 2, set()))]
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
            c = dict(on, advancing=["Pyrelands", "ExplosiveKnockback"], max_live=FIXTURE_MAX_LIVE)
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


def land_views_main():
    """RIMMANDRAKE_FIX_DISPATCH_VIEWS_LANDED_BLIND_TO_PEER_SHARDS: a peer clone lands a HOLDER shard (and its views) on
    origin after the Dispatch root was cloned; the Dispatch appends to its DISPATCH shard and lands through land_ledger
    with the real land.sh against a local bare origin. Origin's views must still list the peer shard (no VIEW_STALE)."""
    import modledger as ML
    tmp = tempfile.mkdtemp(prefix="dispatch_land_views_")
    mod = "LandViewsFixture"
    rel = "design/concepts/%s/ledger" % mod

    def git(repo, *a):
        r = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, timeout=120)
        return r.stdout.strip() if r.returncode == 0 else None

    def clone(name):
        d = os.path.join(tmp, name)
        subprocess.run(["git", "clone", "-q", origin, d], check=True, capture_output=True, timeout=120)
        for k, v in (("user.name", "selftest"), ("user.email", "selftest@example.invalid"), ("commit.gpgsign", "false")):
            git(d, "config", k, v)
        return d

    saved = os.environ.get("RM_STAGE_LAND")
    os.environ.pop("RM_STAGE_LAND", None)
    try:
        origin = os.path.join(tmp, "origin.git")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", origin], check=True, timeout=120)
        peer = clone("peer")
        ML.grant(peer, mod, "L1", version="1")                          # DISPATCH#1: the lease the holder runs under
        git(peer, "add", rel)
        git(peer, "commit", "-q", "-m", "fixture: lease granted")
        git(peer, "push", "-q", "origin", "HEAD:main")
        root = clone("dispatch")                                        # the Dispatch root, cloned now
        ML.append(peer, mod, "HOLDER.L1", "session.id", "session",
                  body={"session_id": "s-1", "context_tokens": 1000}, token=1)
        git(peer, "add", rel)
        git(peer, "commit", "-q", "-m", "fixture: the holder's shard lands from another clone")
        ok(git(peer, "push", "-q", "origin", "HEAD:main") is not None, "land-views fixture: the peer shard is on origin")
        ML.grant(root, mod, "L2")                                       # the Dispatch appends, blind to the peer shard
        got = MD.land_ledger(root, [mod], "run L2 on %s granted" % mod)
        print("     land_ledger -> %s" % got)
        check = clone("check")
        hist = open(os.path.join(check, rel, "views", "history.md"), encoding="utf-8").read() \
            if os.path.exists(os.path.join(check, rel, "views", "history.md")) else ""
        ok("HOLDER.L1#1" in hist and "DISPATCH#2" in hist,
           "land-views: origin's history view lists the peer HOLDER.L1 shard and the Dispatch's new grant")
        stale = [f for f in ML._lint_views(check, mod) if f[0] == "VIEW_STALE"]
        ok(not stale, "land-views: origin's views are not VIEW_STALE (got %s)" % (stale[:1],))
        ok(os.path.exists(os.path.join(check, rel, "HOLDER.L1.jsonl")), "land-views: the peer shard is still on origin")
        ok(not os.path.exists(os.path.join(root, rel, "HOLDER.L1.jsonl"))
           or git(root, "ls-files", rel + "/HOLDER.L1.jsonl"),
           "land-views: no peer file was written untracked into the Dispatch root's worktree")
    finally:
        if saved is not None:
            os.environ["RM_STAGE_LAND"] = saved
        shutil.rmtree(tmp, ignore_errors=True)
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


def item_names_main():
    """RIMMANDRAKE_UNSTICK_DISPATCH_CLONE_PUBLISH_LINT_REFUSES_HEAD (2026-11-16 04:59): Gimme Some Slack's in-game visit 1
    item stood filed, so the next launch wanted a second name; its 61-char base only got shortened when the base
    itself was over 64, so every `_RUN_<N>` (69 chars, 10 words) was over and the launch read "no free item name"."""
    FAILS.clear()
    sys.path.insert(0, os.path.dirname(HERE))
    from rimflow import model
    for fn, mod, n in ((MD.ingame_item_id, "GimmeSomeSlack", 1), (MD.blind_item_id, "GimmeSomeSlack", 1),
                       (MD.ingame_item_id, "Contagion", 2), (MD.blind_item_id, "ExplosiveKnockback", 3),
                       (MD.item_id, "ExplosiveKnockback", 23), (MD.item_id, "Graffiti", 4)):
        known, names = set(), []
        for _ in range(4):
            name = fn(mod, n, known)
            if not name:
                break
            names.append(name)
            known.add(name)
        bad = [x for x in names if len(x) > model.NAME_MAX_LEN
               or not model.NAME_MIN_WORDS <= len(x.split("_")) <= model.NAME_MAX_WORDS]
        ok(len(names) == 4 and len(set(names)) == 4 and not bad,
           "item names: %s %s %d gets four distinct names a rimflow file takes (%s; bad %s)" % (
               fn.__name__, mod, n, names[-1:] or names, bad))
        if fn is MD.ingame_item_id:
            ok(all(MD._is_ingame_item(x) for x in names), "item names: every %s in-game name reads as an in-game run" % mod)
    # 2026-11-16 05:05: the tick's own launch_failed record (systemd-run never ran) read as "a hand-launched run worked
    # here" (hand_run_seen) and paused Gimme Some Slack: a run that never started is no run
    saved = MD.M.ingame_facts, MD.M.certificate
    try:
        MD.M.ingame_facts = lambda root, mod: {"opened": "2026-11-16T03:25:09-08:00"}
        MD.M.certificate = lambda root, mod, stage: {}
        t0 = MD._ts("2026-11-16T03:25:09-08:00")
        runs = [{"unit": "u-failed", "item": "RIMMANDRAKE_DRIVE_X_IN_GAME_VISIT_ONE", "at": t0 + 60, "end": None,
                 "live": False, "state": "launch_failed"},
                {"unit": "u-ran", "item": "RIMMANDRAKE_DRIVE_X_IN_GAME_VISIT_ONE_RUN_TWO", "at": t0 + 120, "end": t0 + 900,
                 "live": False, "state": "finished"}]
        f = MD.add_ingame(".", "X", {"stage": "in_game"}, runs)
        ok(f.get("ingame_runs") == ["u-ran"], "never ran: a launch_failed record is not an in-game run that worked (%s)"
           % f.get("ingame_runs"))
    finally:
        MD.M.ingame_facts, MD.M.certificate = saved
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


def cert_rerun_main():
    """RIMMANDRAKE_RERUN_STALE_CERTIFICATE_STAMPS_NOBODY_OWNS_IT (2026-11-16 12:28 PM PST): Explosive Knockback waited on
    its certificate with 11 of 44 bars refused only because their deciders' runs were stamped on an older build, no
    decider red; cert_red_decide returned None and nothing ran `certificate <Mod> --run`. A stale-only certificate gets
    ONE zero-token rerun per build (a detached unit, not inside the tick), never a builder, never a loop. Written before
    the code and watched failing on the base."""
    FAILS.clear()
    cfg = dict(load_cfg(), advancing=["ExplosiveKnockback"], max_live=0, launch_tries=3)
    now = CLOCK

    def stale(tests, build="b1"):
        return [{"bar": "bar_" + t.lower(), "test": t, "clause": "ran_on_this_build", "status": "REFUSED",
                 "observed": "the recorded run (2026-11-15T01:00:00Z) was on build old; ... hash to %s-%s now" % (t, build),
                 "would_pass": "runs_today.build == %s-%s (the content of %s's reads and file now)" % (t, build, t),
                 "smallest_fix": "python3 src/RimMandrake/rimflow/maturation.py certificate ExplosiveKnockback --run"}
                for t in tests]

    def facts(rows, result=None, live=()):
        return {"ExplosiveKnockback": {
            "stage": "offline_build", "owed": "certificate", "live_units": list(live), "stage_runs": {}, "run_usd": {},
            "certificate": {"ok": not any(r["status"] == "REFUSED" for r in rows), "rows": rows},
            "certificate_why": "refused: 11 of 44 bars", "certificate_fix": "certificate --run", "bar_fp": "fp",
            "cert_rerun_result": result}}
    calls, filed, briefs = [], [], []

    def fake_rerun(mod, key):
        calls.append((mod, key))
        return 0, "STARTED rm-cert-rerun-%d" % len(calls), "rm-cert-rerun-%d" % len(calls)
    fx = {"cert_rerun": fake_rerun, "file": lambda *a, **k: filed.append(a) or (True, "filed"),
          "launch_brief": lambda *a, **k: briefs.append(a) or (0, "DETACHED x", "x"), "known": lambda: set(),
          "launch": lambda *a, **k: briefs.append(a) or (0, "DETACHED y", "y")}
    two = stale(["PY_KNOCK_A", "PY_KNOCK_B"])
    st = {"mods": {}}
    has = all(hasattr(MD, n) for n in ("stale_key", "cert_rerun_unit", "cert_rerun_worker", "rerun_result"))
    ok(has, "cert rerun: maturation_dispatch has stale_key, cert_rerun_unit, cert_rerun_worker and rerun_result")
    rows, la = MD.decide(cfg, st, facts(two), now, (True, "ok"), releases=[])
    r = rows[0]
    ok(la == ["ExplosiveKnockback"] and r.get("decision") == "launch" and r.get("cert_rerun_key") and not r.get("cert_reds"),
       "cert rerun: stale stamps alone, no red decider, slots full (max_live 0): the tick owes one zero-token rerun "
       "(%s: %s)" % (r.get("decision"), r.get("why")))
    key = r.get("cert_rerun_key")
    try:
        MD.execute(".", cfg, st, rows, la, now, fx)
    except Exception as e:      # noqa: BLE001  the base falls through to a Stage 3 builder and dies on refused_ids
        r["decision"] = "crashed: %s: %s" % (type(e).__name__, e)
    ok(calls == [("ExplosiveKnockback", key)] and not filed and not briefs and r.get("decision") == "launched",
       "cert rerun: execute starts exactly one rerun unit, files no item and briefs no builder (%s; %s; %s)" % (
           calls, filed, r.get("decision")))
    book = (st["mods"].get("ExplosiveKnockback") or {}).get("cert_rerun") or {}
    ok(book.get("key") == key and book.get("unit") == "rm-cert-rerun-1",
       "cert rerun: the run is booked against its build key (%s)" % book)
    rows, la = MD.decide(cfg, st, facts(two), now + 60, (True, "ok"), releases=[])
    ok(not la and rows[0].get("decision") == "live" and "rm-cert-rerun-1" in str(rows[0].get("why")),
       "cert rerun: the next tick on the same build, the unit still running, launches nothing (%s: %s)" % (
           rows[0].get("decision"), rows[0].get("why")))
    done = {"unit": "rm-cert-rerun-1", "key": key, "key_after": key, "ok": False, "published": None,
            "error": "publish refused: hook", "end": now + 600}
    rows, la = MD.decide(cfg, st, facts(two, result=done), now + 900, (True, "ok"), releases=[])
    ok(not la and rows[0].get("decision") == "certificate" and "rm-cert-rerun-1" in str(rows[0].get("need")),
       "cert rerun: it ended and the same build is still stale: never a second run, a Needs Conductor line naming it "
       "(%s: %s)" % (rows[0].get("decision"), rows[0].get("need")))
    rows, la = MD.decide(cfg, st, facts(two, result=done), now + 7200, (True, "ok"), releases=[])
    ok(not la, "cert rerun: still none two hours later on that build (%s)" % rows[0].get("decision"))
    new = stale(["PY_KNOCK_A", "PY_KNOCK_B"], build="b2")
    rows, la = MD.decide(cfg, st, facts(new, result=done), now + 7300, (True, "ok"), releases=[])
    ok(la == ["ExplosiveKnockback"] and rows[0].get("cert_rerun_key") not in (None, key),
       "cert rerun: a new build (someone landed a change) gets its own one rerun (%s)" % rows[0].get("decision"))
    own = {"unit": "rm-cert-rerun-2", "key": "kprev", "key_after": MD.stale_key({"rows": new}) if has else None,
           "ok": False, "published": "abc1234", "end": now + 7000}
    st2 = {"mods": {"ExplosiveKnockback": {"cert_rerun": {"key": "kprev", "unit": "rm-cert-rerun-2", "at": now + 6000}}}}
    rows, la = MD.decide(cfg, st2, facts(new, result=own), now + 7300, (True, "ok"), releases=[])
    ok(not la and rows[0].get("need") and "stale" in str(rows[0].get("need")),
       "cert rerun: the rerun itself left this build stale (a decider rewrites what it reads): no loop, a Needs "
       "Conductor line (%s: %s)" % (rows[0].get("decision"), rows[0].get("need")))
    red = two + [{"bar": "bar_t", "test": "T_RED", "clause": "green", "status": "REFUSED", "observed": "rc 1",
                  "smallest_fix": "fix"}]
    rows, la = MD.decide(dict(cfg, max_live=4), {"mods": {}}, facts(red), now, (True, "ok"), releases=[])
    ok(rows[0].get("cert_reds") == ["T_RED"] and not rows[0].get("cert_rerun_key"),
       "cert rerun: stale stamps beside a red decider stay cert_red_decide's builder (it reruns first)")
    reg = two + [{"bar": "bar_r", "test": "T_GONE", "clause": "registered", "status": "REFUSED", "observed": "no file",
                  "smallest_fix": "build it"}]
    rows, la = MD.decide(cfg, {"mods": {}}, facts(reg), now, (True, "ok"), releases=[])
    ok(not la and rows[0].get("decision") == "certificate",
       "cert rerun: a refusal a rerun cannot pass (registered) is no rerun: the certificate wait stands")
    rows, la = MD.decide(cfg, {"mods": {}}, facts(two, live=["rm-builder"]), now, (True, "ok"), releases=[])
    ok(not la and rows[0].get("decision") == "live", "cert rerun: nothing while a run is live on the mod")
    failed = {"mods": {"ExplosiveKnockback": {"cert_rerun": {"key": key, "unit": None, "at": now, "tries": 1,
                                                             "failed": "systemd-run exit 1: bad unit", "code": "t1"}}}}
    rows, la = MD.decide(dict(cfg, _code="t1"), failed, facts(two), now + 120, (True, "ok"), releases=[])
    ok(not la and rows[0].get("need"), "cert rerun: a start refused on a defect is not retried on the same code (%s)"
       % rows[0].get("decision"))
    rows, la = MD.decide(dict(cfg, _code="t2"), failed, facts(two), now + 120, (True, "ok"), releases=[])
    ok(la == ["ExplosiveKnockback"], "cert rerun: it is retried once the pipeline's code changed (%s)" % rows[0].get("decision"))
    if not has:
        print("%d failed" % len(FAILS))
        return 1
    # through the autonomy layer: no road back, the rerun stays the tick's launch (no steward or fixer takes it); an open
    # road-back item gets its fixer first (the road back's items before any launch), the rerun on a later tick
    aut_fx = {"open_items": lambda ids: [], "designer_state": lambda m: None, "version_locked": lambda m: True,
              "version_evidence": lambda m: None}
    st3 = {"mods": {}}
    rows, la = MD.decide(cfg, st3, facts(two), now, (True, "ok"), releases=[])
    rows, la = MD.AUT.resolve(".", cfg, st3, facts(two), rows, la, now, aut_fx)
    ok(la == ["ExplosiveKnockback"] and rows[0].get("cert_rerun_key") and not rows[0].get("aut"),
       "cert rerun: the autonomy layer leaves the rerun the tick's own launch (%s: %s)" % (
           rows[0].get("decision"), rows[0].get("why")))
    st4 = {"mods": {"ExplosiveKnockback": {"road_back": {"caused_by": "RIMMANDRAKE_STEWARD_X", "opened": now - 600}}}}
    rows, la = MD.decide(dict(cfg, max_live=4), st4, facts(two), now, (True, "ok"), releases=[])
    rows, la = MD.AUT.resolve(".", dict(cfg, max_live=4), st4, facts(two), rows, la, now, dict(
        aut_fx, open_items=lambda ids: [{"id": "RIMMANDRAKE_BREAK_X", "needs": "offline"}]))
    ok(rows[0].get("aut") == "fixer" and rows[0].get("fix_item") == "RIMMANDRAKE_BREAK_X",
       "cert rerun: an open road-back item gets its fixer before the rerun (%s: %s)" % (
           rows[0].get("decision"), rows[0].get("why")))
    d = tempfile.mkdtemp(prefix="cert_rerun_")
    was = os.environ.get("RM_MATURATION_DISPATCH_DIR")
    os.environ["RM_MATURATION_DISPATCH_DIR"] = d
    # the unit: systemd-run, detached, zero tokens, bounded
    seen = []
    rc, text, unit = MD.cert_rerun_unit("ExplosiveKnockback", key, runner=lambda argv, **k: seen.append(argv) or
                                        subprocess.CompletedProcess(argv, 0, "", ""), now=now)
    a = seen[0] if seen else []
    ok(rc == 0 and unit and a[:2] == ["systemd-run", "--user"] and "--collect" in a and unit in a
       and any(str(x).startswith("RuntimeMaxSec=") for x in a) and "cert-rerun" in a and "ExplosiveKnockback" in a
       and key in a and not any(os.path.basename(str(x)) == "claude" for x in a),
       "cert rerun: the unit is a bounded systemd-run of `maturation_dispatch.py cert-rerun`, no claude (%s)" % a)
    # the worker: its own clone, `certificate --run`, publish the table, a result the tick reads
    clone = os.path.join(d, "clone")
    tdir = os.path.join(clone, "design", "concepts", "ExplosiveKnockback", "version")
    os.makedirs(tdir)
    open(os.path.join(tdir, "test_table.json"), "w").write("{}")
    ran = []

    def runner(argv, **k):
        ran.append(argv)
        if "certificate" in argv:
            return subprocess.CompletedProcess(argv, 0, json.dumps({"ok": True, "rows": [], "run": {"ran": 2}}), "")
        if argv[:2] == ["git", "status"] or "status" in argv:
            return subprocess.CompletedProcess(argv, 0, " M design/concepts/ExplosiveKnockback/version/test_table.json\n", "")
        if argv and argv[0] == "./publish":
            return subprocess.CompletedProcess(argv, 0, "PUBLISHED 0123abcd\n", "")
        return subprocess.CompletedProcess(argv, 0, "", "")
    try:
        res = MD.cert_rerun_worker("ExplosiveKnockback", key, "rm-cert-rerun-1", runner=runner,
                                   take=lambda name: (clone, "made"), now=lambda: now)
        got = MD.rerun_result("ExplosiveKnockback")
    finally:
        if was is None:
            os.environ.pop("RM_MATURATION_DISPATCH_DIR", None)
        else:
            os.environ["RM_MATURATION_DISPATCH_DIR"] = was
        shutil.rmtree(d, ignore_errors=True)
    cert = [x for x in ran if "certificate" in x]
    pub = [x for x in ran if x and x[0] == "./publish"]
    ok(cert and "--run" in cert[0] and pub and "design/concepts/ExplosiveKnockback/version/test_table.json" in pub[0]
       and "-A" not in pub[0], "cert rerun: the worker runs `certificate --run` and publishes the table by path (%s)" % ran)
    ok(got and got.get("unit") == "rm-cert-rerun-1" and got.get("key") == key and got.get("published") == "0123abcd"
       and got.get("ok") is True and got.get("key_after") is None and res == got,
       "cert rerun: the result the tick reads names the unit, the key, the sha and the key after (%s)" % got)
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


def cert_rerun_gates_main():
    """RIMMANDRAKE_RERUN_STALE_CERTIFICATE_AT_VISIT_AND_CYCLE_GATES (measured 2026-11-17 11:45 AM PST): Gimme Some Slack
    sat 137 min at in-game visit 2 'waiting on its certificate' whose 29 refusals were all stale stamps
    (ran_on_this_build), no decider red: the zero-token rerun (cert_rerun_decide) was wired only at the offline build, and
    cert_wait at the blind cycle and in-game visit gates only put the wait. The same one rerun per build key must run at
    both gates, take no run slot (max_live 1 with a run live elsewhere) and no live-game driver, need no account, and
    name the right gate when it waits. Written before the fix and watched failing on the base."""
    FAILS.clear()
    now = CLOCK
    mod = "GimmeSomeSlack"

    def stale(tests, build="b1"):
        return [{"bar": "bar_" + t.lower(), "test": t, "clause": "ran_on_this_build", "status": "REFUSED",
                 "observed": "the recorded run was on build old; ... hash to %s-%s now" % (t, build),
                 "would_pass": "runs_today.build == %s-%s" % (t, build),
                 "smallest_fix": "python3 src/RimMandrake/rimflow/maturation.py certificate %s --run" % mod}
                for t in tests]

    def facts(stage, rows, result=None, live=()):
        f = {"mod": mod, "stage": stage, "version": "0.1.0", "exit": {"state": "absent"}, "live_units": list(live),
             "stage_runs": {}, "run_usd": {}, "killed": {}, "ingame_live": [], "ingame_games": {},
             "certificate": {"ok": not any(r["status"] == "REFUSED" for r in rows), "rows": rows,
                             "to": stage, "mod": mod},
             "cert_rerun_result": result}
        if stage == "in_game":
            f.update(owed="run", visit=2, ingame_runs=[])
        else:
            f.update(owed="cycle", cycle=2, visit_first=1, blind_runs=[])
        return {mod: f}

    rows5 = stale(["T_CORE", "T_NO_HOSE", "T_CORD_GEOMETRY_OFFLINE", "T_SETTINGS_SWEEP_OFFLINE", "T_SHOCK_RULE_OFFLINE"])
    for stage, gate, word in (("in_game", "in-game visit 2", "--to in_game"),
                              ("blind_challenge", "blind cycle 2", "--to blind_challenge")):
        cfg = dict(load_cfg(), advancing=[mod], max_live=0, launch_tries=3, ingame_enabled=True, blind_enabled=True)
        calls, other = [], []

        def fake_rerun(m, key, calls=calls):
            calls.append((m, key))
            return 0, "STARTED rm-cert-rerun-%d" % len(calls), "rm-cert-rerun-%d" % len(calls)
        fx = {"cert_rerun": fake_rerun, "file": lambda *a, **k: other.append(("file", a)) or (True, "filed"),
              "launch_brief": lambda *a, **k: other.append(("brief", a)) or (0, "DETACHED x", "x"),
              "known": lambda: set(), "launch": lambda *a, **k: other.append(("launch", a)) or (0, "DETACHED y", "y")}
        st = {"mods": {}}
        for acct in ((True, "ok"), (False, "account hold: every account at its floor")):
            rows, la = MD.decide(cfg, dict(st, mods={}), facts(stage, rows5), now, acct, releases=[])
            r = rows[0]
            ok(la == [mod] and r.get("decision") == "launch" and r.get("cert_rerun_key"),
               "cert rerun gates (%s, account %s): stale stamps alone at %s, slots full (max_live 0): one zero-token "
               "rerun is owed, read 1 mod (%s: %s)" % (stage, acct[0], gate, r.get("decision"), r.get("why")))
        rows, la = MD.decide(cfg, st, facts(stage, rows5), now, (True, "ok"), releases=[])
        key = rows[0].get("cert_rerun_key")
        ok(not MD.takes_slot(rows[0]) and not rows[0].get("game"),
           "cert rerun gates (%s): the rerun takes no run slot and no game (%s)" % (stage, rows[0].get("game")))
        try:
            MD.execute(".", cfg, st, rows, la, now, fx)
        except Exception as e:      # noqa: BLE001  the base never gets here with a rerun row
            rows[0]["decision"] = "crashed: %s: %s" % (type(e).__name__, e)
        ok(calls == [(mod, key)] and not other and rows[0].get("decision") == "launched",
           "cert rerun gates (%s): execute starts exactly one rerun unit and nothing else (%s; %s; %s)" % (
               stage, calls, other, rows[0].get("decision")))
        rows, la = MD.decide(cfg, st, facts(stage, rows5), now + 60, (True, "ok"), releases=[])
        ok(not la and rows[0].get("decision") == "live" and "rm-cert-rerun-1" in str(rows[0].get("why")),
           "cert rerun gates (%s): the next tick, the unit still running, launches nothing (%s: %s)" % (
               stage, rows[0].get("decision"), rows[0].get("why")))
        done = {"unit": "rm-cert-rerun-1", "key": key, "key_after": key, "ok": False, "published": None,
                "error": "publish refused: hook", "end": now + 600}
        rows, la = MD.decide(cfg, st, facts(stage, rows5, result=done), now + 900, (True, "ok"), releases=[])
        need = str(rows[0].get("need"))
        ok(not la and rows[0].get("decision") == "certificate" and "rm-cert-rerun-1" in need and word in need
           and gate in need,
           "cert rerun gates (%s): it ended and the build is still stale: never a second run, a Needs Conductor line "
           "naming the unit and the %s gate (%s: %s)" % (stage, gate, rows[0].get("decision"), need[:300]))
        red = rows5 + [{"bar": "bar_t", "test": "T_RED", "clause": "green", "status": "REFUSED", "observed": "rc 1",
                        "smallest_fix": "fix"}]
        rows, la = MD.decide(cfg, {"mods": {}}, facts(stage, red), now, (True, "ok"), releases=[])
        ok(not la and rows[0].get("decision") == "certificate" and not rows[0].get("cert_rerun_key"),
           "cert rerun gates (%s): a red decider beside the stale stamps is no rerun: the wait stands (%s)" % (
               stage, rows[0].get("decision")))
        rows, la = MD.decide(cfg, {"mods": {}}, facts(stage, rows5, live=["rm-other"]), now, (True, "ok"), releases=[])
        ok(not la and rows[0].get("decision") == "live", "cert rerun gates (%s): nothing while a run is live on the mod"
           % stage)
        aut_fx = {"open_items": lambda ids: [], "designer_state": lambda m: None, "version_locked": lambda m: True,
                  "version_evidence": lambda m: None}
        st3 = {"mods": {}}
        rows, la = MD.decide(cfg, st3, facts(stage, rows5), now, (True, "ok"), releases=[])
        rows, la = MD.AUT.resolve(".", cfg, st3, facts(stage, rows5), rows, la, now, aut_fx)
        ok(la == [mod] and rows[0].get("cert_rerun_key") and not rows[0].get("aut"),
           "cert rerun gates (%s): the autonomy layer leaves the rerun the tick's own launch (%s: %s)" % (
               stage, rows[0].get("decision"), rows[0].get("why")))
    # the rerun takes no slot and no game in the tick itself: at max_live 1 and one game, a second mod's owed in-game
    # visit behind it still launches (decide's live_total and drivers are not spent on it)
    two = facts("in_game", rows5)
    two["Twin"] = dict(facts("in_game", [])[mod], mod="Twin")
    cfg = dict(load_cfg(), advancing=[mod, "Twin"], max_live=1, ingame_enabled=True, game_instances=["a"])
    rows, la = MD.decide(cfg, {"mods": {}}, two, now, (True, "ok"), releases=[])
    got = [(r["mod"], r.get("decision"), bool(r.get("cert_rerun_key"))) for r in rows]
    ok(la == [mod, "Twin"] and got == [(mod, "launch", True), ("Twin", "launch", False)],
       "cert rerun gates: at max_live 1 on one game, the rerun ahead spends neither, the next mod's visit launches (%s)"
       % got)
    print("cert rerun gates: %d checks failed of the cases read (2 gates x 9 + 1)" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


def kill_clear_main():
    """RIMMANDRAKE_ENACT_TOKENS_NOT_DOLLARS_NO_LIVE_HOLD, measured 2026-11-16: Gimme Some Slack's in-game visit 1 started
    on try 3 (two launches had failed on a transient fault), the Conductor stopped it at 5:59 AM PST to stage his look,
    and the tick read `stopped` for good: the kill was refused a retry because the launch faults' tries were counted
    against it, and `clear` answered "was: not stopped" and released nothing, since it released only launches that
    never started. Written before the fix and watched failing on the base d9fb01950b."""
    cfg = {"launch_tries": 3}
    u = "rm-detached-bench-drive-x-in-game-1"
    killed = {u: {"why": "killed with no result JSON", "state": "finished", "returned": True}}
    third = {"visit_id": "0.1.0#1", "visit": 1, "unit": u, "failed": None, "tries": 3, "filed": True,
             "never_started": False}
    ok(MD.retriable(cfg, third, killed), "a run that started on its third LAUNCH try and was then killed is retried: "
                                         "launch faults are not kills")
    worn = dict(third, tries=1, killed_before=["k1", "k2"])
    ok(not MD.retriable(cfg, worn, {u: killed[u]}), "a run killed for the third time is not retried (launch_tries "
                                                     "still bounds the kills)")
    ok(not MD.retriable(cfg, dict(third, tries=1), {}), "a run that ended by itself with no record is not retried")

    # the owner, 2026-11-16: "Do not hold live testing when I can't go to the desktop such as now." The live driver's
    # brief says a staged look is kept as a save and never waited on, and keeps the saves a look was staged on
    rules = " ".join(MD.M.BRIDGE_RULES)
    ok("staged look" in rules and "never wait" in rules and "OWNER_LOOK" in rules,
       "the in-game brief: a staged owner look is a kept save, never a reason to hold or wait on the game")

    sd = tempfile.mkdtemp(prefix="maturation_dispatch_clear_")
    was = (os.environ.get("RM_MATURATION_DISPATCH_DIR"), MD.DH.read_record)
    try:
        os.environ["RM_MATURATION_DISPATCH_DIR"] = sd
        live = dict(third, unit="u-live", visit_id="0.1.0#2", visit=2)
        with open(os.path.join(sd, "state.json"), "w") as f:
            json.dump({"mods": {"X": {"ingame_auto": [third, live], "blind_auto": []}}}, f)
        MD.DH.read_record = lambda unit, root=None: {"status": "finished" if unit == u else "running"}
        import io
        import contextlib
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = MD.main(["clear", "X", "--why", "selftest"])
        st = json.load(open(os.path.join(sd, "state.json")))["mods"]["X"]
        text = out.getvalue()
        ok(rc == 0 and [x.get("unit") for x in st["ingame_auto"]] == ["u-live"],
           "clear releases a started automatic run that has ENDED (the derived stop), keeps a live one (%s)"
           % [x.get("unit") for x in st["ingame_auto"]])
        ok("not stopped" not in text and u in text, "clear names the ended run it released, never 'was: not stopped' "
                                                     "(%s)" % text.splitlines()[0][:200])
    finally:
        if was[0] is None:
            os.environ.pop("RM_MATURATION_DISPATCH_DIR", None)
        else:
            os.environ["RM_MATURATION_DISPATCH_DIR"] = was[0]
        MD.DH.read_record = was[1]
        shutil.rmtree(sd, ignore_errors=True)
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


def priority_main():
    """RIMMANDRAKE_LAUNCH_PYRELANDS_FIRST_AT_ONE_SLOT: launch priority is the advancing list's order over every layer.
    At max_live 1, mod P (first) owes a fixer run that maturation_autonomy.resolve adds, and mod G (second) owes a launch
    decide() gave it: P's fixer launches and G waits slots_full, in either input order of the launches; with G first, G
    keeps it. A settling P (its run just ended) keeps the slot from G; a pilot holder on P beats G's build; a zero-token
    certificate rerun takes no slot. Watched failing 5 of 7 on 4d4dad7bcf's maturation_dispatch.py with prioritise as the
    identity (P read slots_full, G launched)."""
    print("== launch priority across layers (max_live 1) ==")
    if not hasattr(MD, "prioritise"):
        ok(False, "priority: maturation_dispatch has no prioritise pass (a later mod's launch takes an earlier mod's "
           "fixer slot)")
        return 1
    now = 1794750000.0
    stop = {"status": "blocked", "stage": 5, "item": "CONCEPT_P", "blocked_on": "x",
            "history": [{"at": "2026-11-15T14:05:35Z", "what": "coverage_stop", "why": "round 6"}]}
    cfg = {"enabled": True, "cap_usd": 15, "max_live": 1, "fix_cap_usd": 10, "steward_cap_usd": 5, "seat": "BENCH",
           "steward_model": "opus", "stalled_min": 10, "settle_s": 180}
    fx = {"designer_state": lambda m: stop if m == "P" else None, "version_locked": lambda m: False,
          "open_items": lambda ids: [], "version_evidence": lambda m: [], "designer_unit": lambda m: None,
          "designer_chain": lambda m: None, "stop_tickets": lambda m, d, s: [{"id": "FIX_T"}],
          "ticket_runs": lambda i: []}

    def tick_of(order, g_extra=None, p_row=None, base_live=0):
        facts = {"P": {"version": "0.1.0", "live_units": []}, "G": {"version": "0.1.0", "live_units": []},
                 "L": {"version": "0.1.0", "live_units": ["rm-u%d" % i for i in range(base_live)]}}
        rows = {"P": dict(p_row or {"mod": "P", "stage": "offline_build", "decision": "ready", "why": "r"}),
                "G": dict({"mod": "G", "stage": "blind_challenge", "decision": "launch", "why": "cycle owed"},
                          **(g_extra or {}))}
        rs = [rows[m] for m in order]
        st = {"mods": {}}
        c = dict(cfg, advancing=list(order))
        rs, la = MD.AUT.resolve("/nonexistent", c, st, facts, rs, ["G"], now, fx)
        la = MD.prioritise(c, st, facts, rs, la)
        return la, {r["mod"]: r for r in rs}

    la, r = tick_of(["P", "G"])
    ok(la == ["P"] and r["P"].get("aut") == "fixer" and r["G"].get("decision") == "slots_full",
       "priority: P first owes a fixer, G second owes a decide launch: P's fixer gets the one slot, G waits (read "
       "launches %s, P %s, G %s)" % (la, r["P"].get("decision"), r["G"].get("decision")))
    ok("P" in str(r["G"].get("waits_on")), "priority: G's wait names the mod ahead of it (read %s)" % r["G"].get(
        "waits_on"))
    la, r = tick_of(["G", "P"])
    ok(la == ["G"] and r["P"].get("decision") == "slots_full",
       "priority: with G first, G keeps the slot and P's fixer waits (read %s, P %s)" % (la, r["P"].get("decision")))
    la, r = tick_of(["P", "G"], base_live=1)
    ok(la == [] and r["P"].get("decision") == "slots_full" and r["G"].get("decision") == "slots_full",
       "priority: one run already live: neither launches (read %s, P %s, G %s)" % (
           la, r["P"].get("decision"), r["G"].get("decision")))
    la, r = tick_of(["P", "G"], p_row={"mod": "P", "stage": "blind_challenge", "decision": "settling", "why": "ended"})
    ok(la == [] and r["G"].get("decision") == "slots_full",
       "priority: P settling (its run ended under settle_s ago) keeps the slot from G (read %s, G %s)" % (
           la, r["G"].get("decision")))
    la, r = tick_of(["P", "G"], g_extra={"cert_rerun_key": "k"})
    ok("G" in la, "priority: G's zero-token certificate rerun takes no slot and still launches (read %s)" % la)
    # a pilot holder on P (its road-back fixers spent) and a decide launch on G
    facts = {"P": {"version": "0.1.0", "live_units": []}, "G": {"version": "0.1.0", "live_units": []}}
    st = {"mods": {"P": {"road_back": {"caused_by": "ROUTE_P"}}}}
    rs = [{"mod": "P", "stage": "blind_challenge", "decision": "fixer_spent", "why": "spent"},
          {"mod": "G", "stage": "blind_challenge", "decision": "launch", "why": "cycle owed"}]
    c = dict(cfg, advancing=["P", "G"])
    rs, la = MD.pilot_holders(".", c, st, facts, rs, ["G"], now, {
        "open_items": lambda ids: [{"id": "RB_1"}], "pilot": lambda root, m: True, "account": lambda: (True, "ok")})
    la = MD.prioritise(c, st, facts, rs, la)
    ok(la == ["P"] and rs[0].get("holder_items") and rs[1].get("decision") == "slots_full",
       "priority: P's pilot holder beats G's later launch (read %s, P %s, G %s)" % (
           la, rs[0].get("decision"), rs[1].get("decision")))
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    if "--priority" in sys.argv[1:]:
        sys.exit(priority_main())
    if "--cert-rerun" in sys.argv[1:]:
        sys.exit(cert_rerun_main())
    if "--cert-rerun-gates" in sys.argv[1:]:
        sys.exit(cert_rerun_gates_main())
    if "--kill-clear" in sys.argv[1:]:
        sys.exit(kill_clear_main())
    if "--item-names" in sys.argv[1:]:
        sys.exit(item_names_main())
    if "--land-views" in sys.argv[1:]:
        sys.exit(land_views_main())
    if "--ingame" in sys.argv[1:]:
        sys.exit(ingame_main())
    if "--release" in sys.argv[1:]:
        sys.exit(release_main())
    rc = main()
    rc = clone_status_main() or rc
    rc = release_main() or rc
    rc = blind_main() or rc
    rc = land_views_main() or rc
    rc = item_names_main() or rc
    rc = cert_rerun_main() or rc
    rc = cert_rerun_gates_main() or rc
    rc = kill_clear_main() or rc
    rc = priority_main() or rc
    sys.exit(ingame_main() or rc)
