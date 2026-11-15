#!/usr/bin/env python3
"""selftest_maturation.py: slice 1 of the Maturation Pipeline spine (maturation.py), offline, in a temp tree.

Item RIMMANDRAKE_BUILD_MATURATION_SPINE_WHILE_DESIGN_STILL_MOVES; plan design/plans/2026-11-14-maturation-pipeline-build.md
section 4, slice 1. Written before maturation.py and watched failing on it (the import fails), then passing.

    python3 src/RimMandrake/rimflow/selftest_maturation.py           exit 0 when every check prints PASS
    python3 src/RimMandrake/rimflow/selftest_maturation.py --blind   the blind challenge: brief, next's exit reading,
                                                                     launch (item
                                                                     RIMMANDRAKE_BUILD_BLIND_CHALLENGE_LAUNCHER_FOUR_MODS_PARKED;
                                                                     watched failing on the base da54e5338e, then passing)
    python3 src/RimMandrake/rimflow/selftest_maturation.py --launch  slice 4 (brief, capped launch) with a fake
                                                                     detached_helper (item
                                                                     RIMMANDRAKE_WIRE_DISPATCH_TO_LAUNCH_BUILDERS_MODS_SAT_IDLE;
                                                                     watched failing on the base: maturation.py had no
                                                                     brief_text, then passing)

What it proves:
  seeding from copies of the real journals lands each mod at the stage maturation_now.py reads, and a re-seed changes
  nothing; the committed records of the four advancing mods agree with their journals; an out-of-order move, a held
  stage, a version mismatch, failing exit tests, a missing hand step, a closed intake and a 4th blind cycle are refused,
  each with a verdict refusal_contract.check accepts, and a refusal writes nothing; a good move writes the record, one
  dated history entry and a "Stage now" line maturation_now reads back to the new stage; the Conductor decision on a
  4th cycle is an intervention line maturation_now parses; spend totals per stage; nothing in the repo is written.
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

import maturation as M          # noqa: E402
import maturation_now as MN     # noqa: E402
import refusal_contract as RC   # noqa: E402

FOUR = ("ExplosiveKnockback", "FlowWorks", "GimmeSomeSlack", "Pyrelands")
COPY = ("journal.md", "stage.json", "version/VERSION.json", "version/test_table.json", "version/preflight.json")
CLOCK = 1794703800.0            # 2026-11-14 4:10 PM PST, pinned
FAILS = []


def ok(cond, what):
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    if not cond:
        FAILS.append(what)


def git_status():
    return subprocess.run(["git", "-C", REPO, "status", "--porcelain", "--", "design/concepts"],
                          capture_output=True, text=True, timeout=120).stdout


# The mods' design/concepts files as these tests were written, read from git: the live tables move as builders land
# (2026-11-14: FlowWorks 7 -> 0 and Explosive Knockback 12 -> 1 refused bars turned both maturation selftests red).
FIXTURE_SHA = "f5d809fb03a59ccca0f72da4a509cfb15b01fd64"


def fixture(mod, rel):
    """-> the bytes of design/concepts/<mod>/<rel> at FIXTURE_SHA, or None when it was absent there."""
    r = subprocess.run(["git", "-C", REPO, "show", "%s:design/concepts/%s/%s" % (FIXTURE_SHA, mod, rel)],
                       capture_output=True, timeout=60)
    return r.stdout if r.returncode == 0 else None


def copy_mods(root):
    for mod in FOUR + ("PyrelandsMechanics",):
        for rel in COPY:
            data = fixture(mod, rel)
            if data is not None:
                dst = os.path.join(root, "design", "concepts", mod, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, "wb") as f:
                    f.write(data)


def synthetic(root, state="drafting"):
    c = os.path.join(root, "design", "concepts", "SpineTestMod")
    os.makedirs(os.path.join(c, "version"), exist_ok=True)
    with open(os.path.join(c, "version", "VERSION.json"), "w") as f:
        json.dump({"mod": "SpineTestMod", "version": "0.1.0", "state": state}, f)
    with open(os.path.join(c, "journal.md"), "w") as f:
        f.write("# Spine test mod: journal\n\n## The mod as it stands\n\n- **Design Version 0.1.0**, drafting.\n"
                "- **Stage now:** Stage 1 (Designer), drafting the bars.\n- **Waiting on:** nothing.\n\n"
                "## History (dated, added to only)\n\n### Conductor interventions (one line each)\n\n"
                "### 2026-11-14 9:00 AM PST, journal started\n\nA test mod.\n")


def read(root, mod, rel):
    with open(os.path.join(root, "design", "concepts", mod, rel), encoding="utf-8") as f:
        return f.read()


def well_formed(v, what):
    errs = RC.check(v["verdict"])
    ok(errs == [], "%s: the refusal is a well-formed refusal-contract record %s" % (what, errs[:3] if errs else ""))


def refused(res, clause, what):
    clauses = [r["clause"] for r in res["verdict"]["refusals"]]
    ok(not res["ok"] and clause in clauses, "%s: refused on clause %s (got %s)" % (what, clause, clauses))
    well_formed(res, what)
    for r in res["verdict"]["refusals"]:
        if r["clause"] == clause:
            ok(bool(r["would_pass"]) and bool(r["smallest_fix"]["what"]), "%s: the refusal carries its path to pass" % what)


def main():
    before = git_status()

    # ---- the committed records agree with the real journals ------------------------------------------------------
    names = MN.designer_names()
    for mod in FOUR:
        rec = M.load(REPO, mod)
        m = MN.read_mod(REPO, mod, names)
        ok(rec is not None, "%s: a committed stage record exists" % mod)
        if rec:
            ok(M.col_of(rec["stage"]) == m["column"], "%s: the record's stage %s is the journal's (%s)"
               % (mod, rec["stage"], m["column"]))
            ok(rec["version"] == m["version"], "%s: the record is for VERSION.json's version %s" % (mod, m["version"]))

    root = tempfile.mkdtemp(prefix="maturation_selftest_")
    os.environ["MATURATION_CLOCK"] = str(CLOCK)
    try:
        copy_mods(root)
        synthetic(root)

        # ---- seeding --------------------------------------------------------------------------------------------
        for mod in FOUR + ("PyrelandsMechanics", "SpineTestMod"):
            rec, made = M.seed_mod(root, mod, live=False)
            want = MN.read_mod(root, mod, names)["column"]
            ok(made and M.col_of(rec["stage"]) == want, "seed %s lands at %s (maturation_now reads %s)"
               % (mod, rec["stage"], want))
        for mod in FOUR:
            ok(M.load(root, mod)["stage"] == "offline_build", "seed %s: offline build, as the hand-run left it" % mod)
        ok(M.load(root, "PyrelandsMechanics")["stage"] == "intake", "seed PyrelandsMechanics: held at intake")
        snap = read(root, "ExplosiveKnockback", M.RECORD)
        rec, made = M.seed_mod(root, "ExplosiveKnockback", live=False)
        ok(not made and read(root, "ExplosiveKnockback", M.RECORD) == snap, "a re-seed changes nothing")
        dspend = [s for s in M.load(root, "ExplosiveKnockback")["spend"] if s["stage"] == "designer"]
        ok(dspend and dspend[0]["tokens"] == 97196907, "seed takes the Designer's tokens from VERSION.json")

        # ---- refusals that write nothing ------------------------------------------------------------------------
        j0, r0 = read(root, "ExplosiveKnockback", "journal.md"), read(root, "ExplosiveKnockback", M.RECORD)
        res = M.advance(root, "ExplosiveKnockback", "in_game", by="BENCH", why="skip ahead")
        refused(res, "order", "offline build to in-game (out of order)")
        res = M.advance(root, "ExplosiveKnockback", "designer", by="BENCH", why="back")
        refused(res, "order", "offline build to designer (no such road back)")
        res = M.advance(root, "ExplosiveKnockback", "blind_challenge", by="BENCH", why="try")
        refused(res, "every_bar_has_a_check_that_runs", "Explosive Knockback with 12 bars not runnable")
        bad = [r for r in res["verdict"]["refusals"] if r["clause"] == "every_bar_has_a_check_that_runs"][0]
        ok("sc_" in bad["observed"] or "_" in bad["observed"], "the refusal names the bars that are not runnable")
        ok(read(root, "ExplosiveKnockback", "journal.md") == j0 and read(root, "ExplosiveKnockback", M.RECORD) == r0,
           "a refused advance writes nothing")

        # version mismatch
        vp = os.path.join(root, "design", "concepts", "GimmeSomeSlack", "version", "VERSION.json")
        v = json.load(open(vp))
        v["version"] = "0.2.0"
        json.dump(v, open(vp, "w"))
        refused(M.advance(root, "GimmeSomeSlack", "blind_challenge", by="BENCH", why="x"), "version",
                "record 0.1.0 against VERSION.json 0.2.0")
        v["version"] = "0.1.0"
        json.dump(v, open(vp, "w"))
        # Gimme Some Slack's one unrunnable bar is decided in part by his stage-8 look: a hand step, not a refusal
        res = M.advance(root, "GimmeSomeSlack", "blind_challenge", by="BENCH", why="x")
        refused(res, "walk_bars_confirmed", "a bar his walk decides, without the steward's word")
        ok("every_bar_has_a_check_that_runs" not in [r["clause"] for r in res["verdict"]["refusals"]],
           "that bar is not counted as a missing check")
        ok(M.advance(root, "GimmeSomeSlack", "blind_challenge", by="BENCH", why="x",
                     steward="walk_scavenger_base: sc_walk's entry exists; only his look waits")["ok"],
           "with the steward's word Gimme Some Slack enters the blind challenge")

        # a hold: FlowWorks' real hold was released, so it is not held; a new hold line holds it
        ok(not M.held(read(root, "FlowWorks", "journal.md"), "offline_build"), "FlowWorks' released hold no longer holds")
        jp = os.path.join(root, "design", "concepts", "FlowWorks", "journal.md")
        with open(jp, "a") as f:
            f.write("\n- CONDUCTOR INTERVENED (stage 3, 2026-11-14 3:59 PM PST, kind hold): held for the selftest. "
                    "Source: selftest.\n")
        refused(M.advance(root, "FlowWorks", "blind_challenge", by="BENCH", why="x"), "hold", "a held stage")

        # intake is closed until a mod reaches his walk (his card, 2026-11-14)
        refused(M.advance(root, "PyrelandsMechanics", "designer", by="BENCH", why="x"), "intake_closed",
                "intake before any mod reached his walk")

        # designer to preflight needs the lock; preflight to offline build needs a preflight record
        refused(M.advance(root, "SpineTestMod", "preflight", by="BENCH", why="x"), "locked", "an unlocked version")
        synthetic(root, state="locked")
        r = M.advance(root, "SpineTestMod", "preflight", by="BENCH", why="locked on his word")
        ok(r["ok"], "a locked version moves to preflight")
        refused(M.advance(root, "SpineTestMod", "offline_build", by="BENCH", why="x"), "preflight_record",
                "no preflight record for this version")
        pp = os.path.join(root, "design", "concepts", "SpineTestMod", "version", "preflight.json")
        json.dump({"mod": "SpineTestMod", "version": "0.1.0", "verdict": "refuse", "refusals": 2,
                   "at": "2026-11-14T15:00:00-08:00"}, open(pp, "w"))
        refused(M.advance(root, "SpineTestMod", "offline_build", by="BENCH", why="x"), "steward_confirms",
                "a refusing preflight without the steward's word")
        ok(M.advance(root, "SpineTestMod", "offline_build", by="BENCH", why="x",
                     steward="both refusals are unbuilt tests: offline build work")["ok"],
           "the steward's word on the refusals left moves it to offline build")
        ok(M.advance(root, "SpineTestMod", "preflight", by="BENCH", why="x")["ok"] is False,
           "offline build back to preflight is no road")

        # ---- a good move: Pyrelands, every bar has a check that runs --------------------------------------------
        jtext0 = read(root, "Pyrelands", "journal.md")
        old_stage = MN.parse_journal(jtext0)["stage"]
        n_hist0 = len(MN.parse_journal(jtext0)["history"])
        res = M.advance(root, "Pyrelands", "blind_challenge", by="BENCH", why="every bar has a check that runs")
        ok(res["ok"], "Pyrelands moves from offline build to the blind challenge")
        rec = M.load(root, "Pyrelands")
        ok(rec["stage"] == "blind_challenge" and len(rec["moves"]) == 1, "the record holds the new stage and one move")
        ok(rec["cycles"] == {"visit": 1, "total": 1}, "entering the blind challenge is cycle 1 (%s)" % rec["cycles"])
        jt = read(root, "Pyrelands", "journal.md")
        pj = MN.parse_journal(jt)
        ok(len(pj["history"]) == n_hist0 + 1, "the journal gained exactly one dated history entry")
        ok(MN.stage_from_text(pj["stage"])[0] == "4+5", "maturation_now reads the new Stage now line as Stages 4 and 5")
        ok(MN.read_mod(root, "Pyrelands", names)["column"] == "4+5", "the status page places Pyrelands at Stages 4 and 5")
        ok(old_stage.split(".")[0][:40] in jt, "the replaced Stage now line is kept in the history entry")

        # cycles: two more blind judges, then a 4th needs the Conductor's decision
        for n in (2, 3):
            ok(M.advance(root, "Pyrelands", "blind_challenge", by="BENCH", why="fault fixed in place")["ok"],
               "cycle %d: a new blind judge" % n)
        refused(M.advance(root, "Pyrelands", "blind_challenge", by="BENCH", why="again"), "fourth_cycle",
                "a 4th blind cycle without the Conductor")
        res = M.advance(root, "Pyrelands", "blind_challenge", by="CONDUCTOR", why="one more",
                        conductor="allow one more cycle: the third fix touched only the ember test")
        ok(res["ok"] and M.load(root, "Pyrelands")["cycles"] == {"visit": 4, "total": 4},
           "with the Conductor's decision a 4th cycle runs")
        ivs, bad_iv = MN.parse_interventions(read(root, "Pyrelands", "journal.md"), "journal")
        ok(any(i["stage"] == "4+5" and i["kind"] == "decision" and "one more cycle" in i["what"] for i in ivs)
           and not bad_iv, "the decision is an intervention line maturation_now parses")

        # hand steps on the later stages
        refused(M.advance(root, "Pyrelands", "in_game", by="BENCH", why="x"), "steward_confirms",
                "leaving the blind challenge without the steward's reading of the verdict")
        for to in ("in_game", "pre_human", "his_walk"):
            ok(M.advance(root, "Pyrelands", to, by="CONDUCTOR", why="x", steward="read the run's verdict: clean")["ok"],
               "Pyrelands moves to %s on the steward's word" % to)
        ok(M.load(root, "Pyrelands")["pre_human_arrivals"] == 1, "arrivals at the pre-human check are counted")
        refused(M.advance(root, "Pyrelands", "passed", by="CONDUCTOR", why="x"), "owner_said",
                "a pass without his words")
        refused(M.advance(root, "PyrelandsMechanics", "designer", by="BENCH", why="x"), "owner_said",
                "intake after a mod reached his walk still asks him")
        ok(M.advance(root, "Pyrelands", "offline_build", by="CONDUCTOR", why="a Problem he saw: the ember")["ok"],
           "his walk sends a Problem back to offline build")
        ok(M.advance(root, "Pyrelands", "blind_challenge", by="BENCH", why="fixed")["ok"]
           and M.load(root, "Pyrelands")["cycles"] == {"visit": 1, "total": 5},
           "a new visit to the blind challenge counts from 1 again; the total keeps counting")

        # ---- spend --------------------------------------------------------------------------------------------
        M.add_spend(root, "Pyrelands", "blind_challenge", tokens=1000, usd=1.5, wall_s=60, source="run-a")
        M.add_spend(root, "Pyrelands", "blind_challenge", tokens=500, usd=None, wall_s=None, source="run-b",
                    estimate=True)
        tot = M.spend_by_stage(M.load(root, "Pyrelands"))["blind_challenge"]
        ok(tot["tokens"] == 1500 and tot["usd"] == 1.5 and tot["estimates"] == 1, "spend totals per stage (%s)" % tot)

        # ---- next ---------------------------------------------------------------------------------------------
        nx = M.next_step(root, "ExplosiveKnockback")
        ok(nx["stage"] == "offline_build" and nx["next"].startswith("NEXT") and "every_bar_has_a_check_that_runs"
           in json.dumps(nx["refusals"]), "next on Explosive Knockback names the failing exit test")
        nx = M.next_step(root, "SpineTestMod")
        ok("advance" in nx["next"] or "hand step" in nx["next"], "next on an offline-build mod says the move")
        cli = subprocess.run([sys.executable, os.path.join(HERE, "maturation.py"), "--root", root, "advance",
                              "ExplosiveKnockback", "--to", "in_game", "--by", "BENCH", "--why", "x"],
                             capture_output=True, text=True, env=dict(os.environ), timeout=120)
        ok(cli.returncode == 1 and "REFUSED" in cli.stdout, "the command line refuses with exit 1")
        cli = subprocess.run([sys.executable, os.path.join(HERE, "maturation.py"), "--root", root, "next",
                              "Pyrelands"], capture_output=True, text=True, env=dict(os.environ), timeout=120)
        ok(cli.returncode == 0 and "NEXT" in cli.stdout, "the command line prints a NEXT line")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    ok(git_status() == before, "nothing under design/concepts in the repo was written")
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0

FAKE_DH = """#!/usr/bin/env python3
import json, os, sys
with open(os.environ["FAKE_DH_LOG"], "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\\n")
n = len(open(os.environ["FAKE_DH_LOG"]).readlines())
print("DETACHED rm-detached-bench-fake-%d" % n)
"""


def launch_main():
    """Slice 4: the brief's mechanical half and the capped launch, through a fake detached_helper."""
    before = git_status()
    root = tempfile.mkdtemp(prefix="maturation_launch_")
    env_was = {k: os.environ.get(k) for k in ("MATURATION_DETACHED_HELPER", "FAKE_DH_LOG", "MATURATION_BRIEF_DIR",
                                              "MATURATION_CLOCK")}
    try:
        copy_mods(root)
        for mod in FOUR + ("PyrelandsMechanics",):
            # the records at the fixture sha, not the live ones (2026-11-15: all four live records moved to the blind
            # challenge and turned this test red)
            data = fixture(mod, "version/stage_record.json")
            if data is not None:
                with open(os.path.join(root, "design", "concepts", mod, "version", "stage_record.json"), "wb") as fh:
                    fh.write(data)
        fake, log = os.path.join(root, "fake_dh.py"), os.path.join(root, "fake_dh.log")
        with open(fake, "w") as f:
            f.write(FAKE_DH)
        open(log, "w").close()
        os.environ.update(MATURATION_DETACHED_HELPER=fake, FAKE_DH_LOG=log, MATURATION_CLOCK=str(CLOCK),
                          MATURATION_BRIEF_DIR=os.path.join(root, "briefs"))

        def calls():
            with open(log) as f:
                return [json.loads(x) for x in f if x.strip()]

        text, f = M.brief_text(root, "FlowWorks")
        ok(f["owed"] == "build" and isinstance(f["refused_bars"], list) and f["refused_bars"],
           "FlowWorks owes build work (%s bars refused)" % len(f.get("refused_bars") or []))
        ok(all(b in text for b in f["refused_bars"]), "the brief names every refused bar")
        ok("## Steward's decisions" in text and M.STANDING_DEFAULT[:60] in text,
           "a blank steward section carries the standing default, never a refusal")
        ok("Waiting on" in text and "does not run today" in text, "the brief carries the journal's Waiting on line "
                                                                   "and each decider that does not run")
        with open(os.path.join(root, "design", "concepts", "FlowWorks", M.STEWARD_FILE), "w") as fh:
            fh.write("Build the canal read first.\n")
        text, _ = M.brief_text(root, "FlowWorks")
        ok("Build the canal read first." in text and M.STANDING_DEFAULT[:60] not in text,
           "the Conductor's steward_decisions.md replaces the default")
        _, g = M.brief_text(root, "Pyrelands")
        ok(g["owed"] == "ready to advance", "Pyrelands owes nothing but the advance (%s)" % g.get("owed"))
        _, g = M.brief_text(root, "GimmeSomeSlack")
        ok(g["owed"] == "hand step", "Gimme Some Slack owes only a hand step (%s)" % g.get("owed"))

        for cap, what in ((None, "no cap"), (0, "a zero cap"), (-3, "a negative cap")):
            rc, out, unit = M.launch_mod(root, "FlowWorks", cap, "RIMMANDRAKE_X_Y_Z_Q")
            ok(rc == 2 and "cap" in out and not calls(), "%s refuses and launches nothing" % what)
        rc, out, _ = M.launch_mod(root, "FlowWorks", 15, "")
        ok(rc == 2 and not calls(), "no item refuses")
        rc, out, _ = M.launch_mod(root, "PyrelandsMechanics", 15, "RIMMANDRAKE_X_Y_Z_Q")
        ok(rc == 2 and "only an offline build" in out and not calls(), "a mod at intake refuses")
        rc, out, _ = M.launch_mod(root, "Pyrelands", 15, "RIMMANDRAKE_X_Y_Z_Q")
        ok(rc == 2 and "no build work" in out and not calls(), "a mod with no build work owed refuses")
        cli = subprocess.run([sys.executable, os.path.join(HERE, "maturation.py"), "--root", root, "launch",
                              "FlowWorks", "--item", "RIMMANDRAKE_X_Y_Z_Q"], capture_output=True, text=True,
                             env=dict(os.environ), timeout=120)
        ok(cli.returncode == 2 and "--budget-usd" in cli.stderr and not calls(),
           "the command line without --budget-usd refuses")
        rc, out, unit = M.launch_mod(root, "FlowWorks", 15, "RIMMANDRAKE_X_Y_Z_Q")
        c = calls()
        ok(rc == 0 and unit == "rm-detached-bench-fake-1" and len(c) == 1, "a good launch calls the launcher once")
        if c:
            a = c[0]
            ok(a[0] == "launch" and a[a.index("--budget-usd") + 1] == "15" and a[a.index("--model") + 1] == "opus"
               and a[a.index("--item") + 1] == "RIMMANDRAKE_X_Y_Z_Q" and a[a.index("--seat") + 1] == "BENCH",
               "the cap, model, item and seat pass through (%s)" % a)
            bf = a[a.index("--brief-file") + 1]
            ok(os.path.exists(bf) and "FlowWorks" in open(bf).read() and bf.startswith(root),
               "the brief file is written where MATURATION_BRIEF_DIR says")
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
#
# The four mods as they stood at the blind challenge, read from git: Explosive Knockback at visit 2 (cycles 1 and 2 hand
# launched), FlowWorks, Gimme Some Slack and Pyrelands at visit 1. Written before maturation.py had blind_facts and watched
# failing on the base da54e5338e (AttributeError), then passing.
BLIND_SHA = "da54e5338ea493e0cb1575b684791d7136756488"
BLIND_CLOCK = 1794736800.0      # 2026-11-15 1:20 AM PST, pinned
ITEM = "RIMMANDRAKE_X_Y_Z_Q"


def blind_fixture(mod, rel):
    r = subprocess.run(["git", "-C", REPO, "show", "%s:design/concepts/%s/%s" % (BLIND_SHA, mod, rel)],
                       capture_output=True, timeout=60)
    return r.stdout if r.returncode == 0 else None


def copy_blind(root):
    for mod in FOUR:
        for rel in COPY + ("version/stage_record.json",):
            data = blind_fixture(mod, rel)
            if data is not None:
                dst = os.path.join(root, "design", "concepts", mod, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, "wb") as f:
                    f.write(data)


def write_cycle(root, mod, n, exit_met=True, problems_open=0, red_bar=None, drop_bar=None, rerun_fail=None,
                pending_problem=False, fix_red_rc=1, lane1_fail=False, tree_clean=True, block=True, edited=True,
                fix_runs=None, lane1_after=None, record_decider=None):
    """A cycle record in the FORMAT_NOTES layout, every file a program reads, with one thing broken on request."""
    tt = json.load(open(os.path.join(root, "design", "concepts", mod, "version", "test_table.json")))
    bars = [b for b in tt["bars"] if str(b.get("proves_at")) in ("2", "4-5")]
    d = os.path.join(root, "design", "concepts", mod, "version", "blind_challenge", "cycle_%d" % n)
    shutil.rmtree(d, ignore_errors=True)
    for sub in ("lane1", "lane2"):
        os.makedirs(os.path.join(d, sub))
    shown = ", ".join("%s: %s" % (b["id"], "red" if b["id"] == red_bar else "green") for b in bars
                      if b["id"] != drop_bar)
    ex = ("offline_bars: {%s}\nproblems_open: %d\nexit_met: %s\n" % (shown, problems_open, str(exit_met).lower())
          if block else "(pending)\n")
    if record_decider:   # one decider becomes a record with no command; its rerun row reads not_rerunnable
        for b in bars:
            for t in b.get("offline_decides") or b.get("decides") or []:
                if t == record_decider:
                    tt["tests"][t] = {"id": t, "kind": "record", "observes": "a selftest approval"}
        with open(os.path.join(root, "design", "concepts", mod, "version", "test_table.json"), "w") as f:
            json.dump(tt, f)
    with open(os.path.join(d, "SUMMARY.md"), "w") as f:
        f.write("# cycle %d\n\n## Start time\n2026-11-15T08:00Z\n\n## Exit\n```\n%s```\n\n## Owed\nnone\n" % (n, ex)
                if block else "# cycle %d\n\n## Exit\n%s\n## Owed\n(pending)\n" % (n, ex))
    with open(os.path.join(d, "lane2", "reruns.jsonl"), "w") as f:
        for b in bars:
            for t in b.get("offline_decides") or b.get("decides") or []:
                f.write(json.dumps({"test": t, "result": "FAIL" if t == rerun_fail else
                                    "not_rerunnable" if t == record_decider else "PASS",
                                    "recorded_result": "PASS", "match": t != rerun_fail}) + "\n")
    faults = [{"id": "RIMMANDRAKE_FIX_SELFTEST_FAULT_SHOWN_RED", "class": "Problem", "status": "FIXED abc1234"},
              {"id": "RIMMANDRAKE_NOTE_SELFTEST_POLISH_LEFT_ALONE", "class": "Polish", "status": "NOTED_FOR_CONDUCTOR"}]
    if pending_problem:
        faults.append({"id": "RIMMANDRAKE_LEAVE_SELFTEST_PROBLEM_OPEN", "class": "Problem (criterion)",
                       "status": "NOTED_FOR_CONDUCTOR"})
    with open(os.path.join(d, "lane2", "faults.json"), "w") as f:
        json.dump({"cycle": n, "faults": faults}, f)
    with open(os.path.join(d, "lane2", "fixes.jsonl"), "w") as f:
        f.write(json.dumps({"fault": faults[0]["id"], "red": {"rc": [fix_red_rc, fix_red_rc]}, "green": {"rc": [0, 0]}}
                           if fix_runs is None else dict(fault=faults[0]["id"], **fix_runs)) + "\n")
    if lane1_after is not None:   # lane 1 rerun after the fixes: {id: verdict}
        with open(os.path.join(d, "lane2", "lane1_rows_after_fix.jsonl"), "w") as f:
            f.write("".join(json.dumps({"id": k, "verdict": v}) + "\n" for k, v in lane1_after.items()))
    with open(os.path.join(d, "lane1", "lane1_rows.jsonl"), "w") as f:
        f.write(json.dumps({"id": "L1_a", "verdict": "PASS"}) + "\n" + json.dumps({"id": "L1_b", "verdict": "UNSETTLED"})
                + "\n" + (json.dumps({"id": "L1_c", "verdict": "FAIL"}) + "\n" if lane1_fail else ""))
    if edited:
        with open(os.path.join(d, "tests_edited.json"), "w") as f:
            json.dump({"cycle": n, "edited": []}, f)
    with open(os.path.join(d, "lane2", "planted_results.jsonl"), "w") as f:
        f.write(json.dumps({"baseline": True}) + "\n" + json.dumps({"tree_clean_after": tree_clean}) + "\n")


def blind_main():
    """The blind challenge: brief, next (a program's exit reading) and launch, offline, through a fake detached_helper."""
    before = git_status()
    root = tempfile.mkdtemp(prefix="maturation_blind_")
    env_was = {k: os.environ.get(k) for k in ("MATURATION_DETACHED_HELPER", "FAKE_DH_LOG", "MATURATION_BRIEF_DIR",
                                              "MATURATION_CLOCK")}
    try:
        copy_blind(root)
        fake, log = os.path.join(root, "fake_dh.py"), os.path.join(root, "fake_dh.log")
        with open(fake, "w") as f:
            f.write(FAKE_DH)
        open(log, "w").close()
        os.environ.update(MATURATION_DETACHED_HELPER=fake, FAKE_DH_LOG=log, MATURATION_CLOCK=str(BLIND_CLOCK),
                          MATURATION_BRIEF_DIR=os.path.join(root, "briefs"))

        def calls():
            with open(log) as f:
                return [json.loads(x) for x in f if x.strip()]

        # ---- no cycle yet: Gimme Some Slack ------------------------------------------------------------------------
        g = M.blind_facts(root, "GimmeSomeSlack")
        ok(g.get("owed") == "cycle" and g.get("cycle") == 1 and (g.get("exit") or {}).get("state") == "absent",
           "no cycle folder: cycle 1 is owed, the exit reads absent (%s)" % {k: g.get(k) for k in ("owed", "cycle")})
        nx = M.next_step(root, "GimmeSomeSlack")
        ok("maturation.py launch GimmeSomeSlack" in nx["launch"] and "steward_confirms" in nx["hand_steps"],
           "next names the launch, and steward_confirms stays a hand step (%s)" % nx["launch"])
        text, _ = M.brief_text(root, "GimmeSomeSlack")
        ok(text.startswith("# Blind challenge (Stages 4 and 5): GimmeSomeSlack 0.1.0, cycle 1")
           and "Offline build (Stage 3)" not in text, "the brief at the blind challenge is a blind-challenge brief")
        tt = json.load(open(os.path.join(root, "design/concepts/GimmeSomeSlack/version/test_table.json")))
        ok(all(b in text for b in ("no_hose", "no_hose_in_gss", "T_NO_HOSE", tt["tests"]["T_NO_HOSE"]["command"])),
           "the brief names the offline bars, their decider and its recorded command, from the mod's own table")
        ok("design/concepts/GimmeSomeSlack/version/blind_challenge/cycle_1/SUMMARY.md" in text
           and "exit_met: true|false" in text and "problems_open:" in text and "offline_bars:" in text,
           "the brief names the skeleton path and the machine-checkable exit block")
        ok("lane2/lane1_rows_after_fix.jsonl" in text and "may be a list of such runs" in text,
           "the brief names the after-fix lane-1 rerun and the list form of a fix's runs")
        ok("`design/concepts/GimmeSomeSlack/journal.md`" in text and "version/test_table.*" in text
           and "FORMAT_NOTES.md" in text, "the brief keeps the journal and the test table closed until lane 1")
        ok("## Steward's decisions (SEALED" in text and M.BLIND_DEFAULT[:60] in text,
           "no stage 4+5 intervention since the stage opened: the sealed section carries the standing default")
        jp = os.path.join(root, "design", "concepts", "GimmeSomeSlack", "journal.md")
        jsaved = open(jp).read()
        with open(jp, "w") as f:
            f.write(M.add_intervention(jsaved, "- CONDUCTOR INTERVENED (stage 4+5, 2026-11-15 12:40 AM PST, kind "
                                               "decision): selftest says judge the hose bar first. Source: selftest."))
        text, _ = M.brief_text(root, "GimmeSomeSlack")
        ok("selftest says judge the hose bar first" in text and M.BLIND_DEFAULT[:60] not in text,
           "a CONDUCTOR INTERVENED line since the stage opened fills the steward's section")
        rc, out, unit = M.launch_mod(root, "GimmeSomeSlack", 20, ITEM, model="sonnet")
        ok(rc == 2 and "opus" in out and not calls(), "a judging run below opus refuses (%s)" % out[:80])
        rc, out, unit = M.launch_mod(root, "GimmeSomeSlack", 20, ITEM)
        c = calls()
        ok(rc == 0 and unit and len(c) == 1 and c[0][c[0].index("--budget-usd") + 1] == "20"
           and c[0][c[0].index("--model") + 1] == "opus", "launch works at the blind challenge: one call, the cap, opus")
        if c:
            bf = c[0][c[0].index("--brief-file") + 1]
            ok("# Blind challenge" in open(bf).read(), "the launched brief is the blind-challenge brief")
        with open(jp, "w") as f:
            f.write(M.add_intervention(jsaved, "- CONDUCTOR INTERVENED (stage 4+5, 2026-11-15 12:41 AM PST, kind hold): "
                                               "selftest hold. Source: selftest."))
        g = M.blind_facts(root, "GimmeSomeSlack")
        rc, out, _ = M.launch_mod(root, "GimmeSomeSlack", 20, ITEM)
        ok(g.get("owed") == "blocked" and rc == 2 and len(calls()) == 1, "a hold on stage 4+5 blocks: no launch")
        with open(jp, "w") as f:
            f.write(jsaved)

        # ---- a met cycle and each way of not meeting it: FlowWorks ------------------------------------------------
        write_cycle(root, "FlowWorks", 1)
        f = M.blind_facts(root, "FlowWorks")
        ex = f.get("exit") or {}
        ok(f.get("owed") == "exit met" and ex.get("state") == "met" and ex.get("cycle") == 1,
           "a complete record whose block says exit_met true and whose files agree reads met (%s)" % ex.get("why"))
        nx = M.next_step(root, "FlowWorks")
        ok("steward_confirms" in nx["hand_steps"] and nx["launch"].startswith("none") and "exit met" in nx["next"],
           "next: exit met is a program reading, the steward still confirms, nothing to launch (%s)" % nx["next"][:90])
        rc, out, _ = M.launch_mod(root, "FlowWorks", 20, ITEM)
        ok(rc == 2 and "cycle 1" in out and len(calls()) == 1, "launch refuses a cycle already recorded (%s)" % out[:80])
        broken = (
            (dict(exit_met=False, problems_open=1, red_bar="inv_converters"), "the judge's block says exit_met false",
             "exit_met false"),
            (dict(rerun_fail="T_CONVERT"), "a decider of an offline bar FAILs on the rerun", "T_CONVERT"),
            (dict(pending_problem=True), "a Problem is NOTED_FOR_CONDUCTOR", "RIMMANDRAKE_LEAVE_SELFTEST_PROBLEM_OPEN"),
            (dict(fix_red_rc=0), "a FIXED Problem was never shown red", "red"),
            (dict(lane1_fail=True), "lane 1 has a FAIL row", "L1_c"),
            (dict(tree_clean=False), "the planted-fault loop did not prove the tree clean", "tree_clean_after"),
            (dict(drop_bar="inv_drilling"), "the block leaves out an offline bar", "inv_drilling"),
            (dict(edited=False), "tests_edited.json is missing", "tests_edited.json"),
        )
        for kw, what, word in broken:
            write_cycle(root, "FlowWorks", 1, **kw)
            ex = M.blind_facts(root, "FlowWorks").get("exit") or {}
            ok(ex.get("state") == "not_met" and word in " ".join(ex.get("why") or []),
               "%s: not met, and the reading says why (%s)" % (what, (ex.get("why") or ["-"])[0][:90]))
        # a fix shown as a list of runs (Pyrelands cycle 1 wrote it so); a lane-1 FAIL cleared by lane 1 after the fixes
        runs = dict(red=[{"cmd": "a", "rc": 1}, {"cmd": "b", "rc": 1}], green=[{"cmd": "a", "rc": 0}, {"cmd": "b", "rc": 0}])
        met = (
            (dict(fix_runs=runs), "a FIXED Problem shown red then green as lists of runs"),
            (dict(lane1_fail=True, lane1_after={"L1_a": "PASS", "L1_b": "UNSETTLED", "L1_c": "PASS"}),
             "a lane-1 FAIL that lane 1 after the fixes shows PASS"),
        )
        for kw, what in met:
            write_cycle(root, "FlowWorks", 1, **kw)
            ex = M.blind_facts(root, "FlowWorks").get("exit") or {}
            ok(ex.get("state") == "met", "%s reads met (%s)" % (what, (ex.get("why") or ["-"])[0][:120]))
        tt_saved = open(os.path.join(root, "design/concepts/FlowWorks/version/test_table.json")).read()
        broken = (
            (dict(fix_runs=dict(runs, red=[{"cmd": "a", "rc": 0}])), "a list-of-runs fix never shown red", "red"),
            (dict(fix_runs=dict(runs, green=[{"cmd": "a", "rc": 0}, {"cmd": "b"}])),
             "a list-of-runs green with an unrecorded rc", "green"),
            (dict(lane1_fail=True, lane1_after={"L1_a": "PASS", "L1_c": "FAIL"}),
             "a lane-1 FAIL still FAIL after the fixes", "still fails L1_c"),
            (dict(lane1_fail=True, lane1_after={"L1_a": "PASS"}), "a lane-1 FAIL dropped from the after-fix rerun",
             "does not show PASS for L1_c"),
            (dict(lane1_fail=True, lane1_after={"L1_c": "PASS", "L1_d": "FAIL"}),
             "a new FAIL in the after-fix rerun", "still fails L1_d"),
            (dict(record_decider="T_CONVERT"), "a record decider with no command", "record with no command"),
        )
        for kw, what, word in broken:
            write_cycle(root, "FlowWorks", 1, **kw)
            ex = M.blind_facts(root, "FlowWorks").get("exit") or {}
            ok(ex.get("state") == "not_met" and word in " ".join(ex.get("why") or []),
               "%s: not met, and the reading says why (%s)" % (what, (ex.get("why") or ["-"])[0][:110]))
        with open(os.path.join(root, "design/concepts/FlowWorks/version/test_table.json"), "w") as fh:
            fh.write(tt_saved)
        write_cycle(root, "FlowWorks", 1, block=False)
        f = M.blind_facts(root, "FlowWorks")
        ok(f.get("owed") == "no exit block" and (f.get("exit") or {}).get("state") == "no_exit_block",
           "a cycle folder whose Exit still reads (pending) has no exit block (%s)" % f.get("owed"))
        nx = M.next_step(root, "FlowWorks")
        ok(nx["launch"].startswith("none"), "next launches nothing on a cycle in progress")

        # ---- cycle 2 reads what changed since cycle 1 opened: Explosive Knockback ---------------------------------
        write_cycle(root, "ExplosiveKnockback", 1, exit_met=False, problems_open=0, red_bar="inv_proof_scenes")
        f = M.blind_facts(root, "ExplosiveKnockback")
        ok(f.get("cycle") == 2 and f.get("owed") == "cycle", "visit 2 with only cycle_1 recorded: cycle 2 is owed (%s)"
           % {k: f.get(k) for k in ("cycle", "owed")})
        text, _ = M.brief_text(root, "ExplosiveKnockback")
        ok("cycle 2" in text.split("\n")[0] and "f5e310809f" in text and "git diff --name-only f5e310809f" in text,
           "the cycle-2 brief diffs from the advance that opened cycle 1 (f5e310809f), found in git")
        ok("except `cycle_1/tests_edited.json`" in text and "miss_of" in text and "Changed files to bars" in text,
           "the cycle-2 brief seals the earlier cycles but shows their tests_edited, and asks for miss_of")
        ok("FORMAT_NOTES.md" in text and "names this mod's cycle-1 findings" in text,
           "Explosive Knockback's own FORMAT_NOTES is sealed until lane 1")
        ok("T_RESTORE" in text, "the brief lists every decider of the offline bars (T_RESTORE included)")

        # ---- offline build is unchanged ------------------------------------------------------------------------------
        data = fixture("FlowWorks", "version/stage_record.json")
        with open(os.path.join(root, "design/concepts/FlowWorks/version/stage_record.json"), "wb") as fh:
            fh.write(data)
        rec = json.loads(data)
        tt_old = fixture("FlowWorks", "version/test_table.json")
        with open(os.path.join(root, "design/concepts/FlowWorks/version/test_table.json"), "wb") as fh:
            fh.write(tt_old)
        text, f = M.brief_text(root, "FlowWorks")
        nx = M.next_step(root, "FlowWorks")
        ok(rec["stage"] == "offline_build" and text.startswith("# Offline build (Stage 3)") and f.get("owed") == "build"
           and nx["launch"].startswith("maturation.py launch FlowWorks --budget-usd"),
           "a mod at the offline build gets the same Stage 3 brief and launch line as before")
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
    a = sys.argv[1:]
    sys.exit(launch_main() if "--launch" in a else blind_main() if "--blind" in a else main())
