#!/usr/bin/env python3
"""selftest_maturation.py: slice 1 of the Maturation Pipeline spine (maturation.py), offline, in a temp tree.

Item RIMMANDRAKE_BUILD_MATURATION_SPINE_WHILE_DESIGN_STILL_MOVES; plan design/plans/2026-11-14-maturation-pipeline-build.md
section 4, slice 1. Written before maturation.py and watched failing on it (the import fails), then passing.

    python3 src/RimMandrake/rimflow/selftest_maturation.py        exit 0 when every check prints PASS

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
                          capture_output=True, text=True).stdout


def copy_mods(root):
    for mod in FOUR + ("PyrelandsMechanics",):
        for rel in COPY:
            src = os.path.join(REPO, "design", "concepts", mod, rel)
            if os.path.exists(src):
                dst = os.path.join(root, "design", "concepts", mod, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy(src, dst)


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
                             capture_output=True, text=True, env=dict(os.environ))
        ok(cli.returncode == 1 and "REFUSED" in cli.stdout, "the command line refuses with exit 1")
        cli = subprocess.run([sys.executable, os.path.join(HERE, "maturation.py"), "--root", root, "next",
                              "Pyrelands"], capture_output=True, text=True, env=dict(os.environ))
        ok(cli.returncode == 0 and "NEXT" in cli.stdout, "the command line prints a NEXT line")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    ok(git_status() == before, "nothing under design/concepts in the repo was written")
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
