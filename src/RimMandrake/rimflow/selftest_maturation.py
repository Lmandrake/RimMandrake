#!/usr/bin/env python3
"""selftest_maturation.py: slice 1 of the Maturation Pipeline spine (maturation.py), offline, in a temp tree.

Item RIMMANDRAKE_BUILD_MATURATION_SPINE_WHILE_DESIGN_STILL_MOVES; plan design/plans/2026-11-14-maturation-pipeline-build.md
section 4, slice 1. Written before maturation.py and watched failing on it (the import fails), then passing.

    python3 src/RimMandrake/rimflow/selftest_maturation.py           exit 0 when every check prints PASS
    python3 src/RimMandrake/rimflow/selftest_maturation.py --blind   the blind challenge: brief, next's exit reading,
                                                                     launch (item
                                                                     RIMMANDRAKE_BUILD_BLIND_CHALLENGE_LAUNCHER_FOUR_MODS_PARKED;
                                                                     watched failing on the base da54e5338e, then passing)
    python3 src/RimMandrake/rimflow/selftest_maturation.py --ingame  in-game acceptance: brief, next's exit reading,
                                                                     launch and its bridge gate (item
                                                                     RIMMANDRAKE_BUILD_IN_GAME_STAGE_LAUNCHER_PYRELANDS_ARRIVED_FIRST;
                                                                     watched failing on the base ab858016ee, then passing)
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


def synthetic(root, state="drafting", locked_by=None, **more):
    c = os.path.join(root, "design", "concepts", "SpineTestMod")
    os.makedirs(os.path.join(c, "version"), exist_ok=True)
    with open(os.path.join(c, "version", "VERSION.json"), "w") as f:
        json.dump(dict({"mod": "SpineTestMod", "version": "0.1.0", "state": state},
                       **({"locked_by": locked_by} if locked_by else {}), **more), f)
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
        # a concept still at the Designer has a journal but no version/ folder (Graffiti, 2026-11-15: seed crashed)
        jd = os.path.join(root, "design", "concepts", "JournalOnlyMod")
        os.makedirs(jd)
        with open(os.path.join(jd, "journal.md"), "w", encoding="utf-8") as f:
            f.write("# J\n\n## The mod as it stands\n\n- **Stage now:** Stage 1, the Designer.\n")
        try:
            rec, made = M.seed_mod(root, "JournalOnlyMod", live=False)
            ok(made and rec["stage"] == "designer", "seed a journal-only concept (no version/): lands at the Designer")
        except OSError as e:
            ok(False, "seed a journal-only concept (no version/) crashed: %s" % e)
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
        # ...unless his words admit this one mod (owner, 2026-11-15: "pick the next most mature biome mod to add")
        e = M.evaluate(root, "PyrelandsMechanics", "designer", by="BENCH", why="x", owner="add this mod now")
        ok("intake_closed" not in [r["clause"] for r in e["verdict"]["refusals"]]
           and "intake_closed" in [p["clause"] for p in e["verdict"]["passed"]],
           "his words open intake for one mod before any walk")

        # designer to preflight needs the lock; preflight to offline build needs a preflight record
        refused(M.advance(root, "SpineTestMod", "preflight", by="BENCH", why="x"), "locked", "an unlocked version")
        # RIMMANDRAKE_REQUIRE_OWNER_EVENT_TO_PASS: the lock is the word "locked", by him
        synthetic(root, state="locked-without-owner", locked_by="owner")
        refused(M.advance(root, "SpineTestMod", "preflight", by="BENCH", why="x"), "locked", "a 'locked-without-owner' state")
        synthetic(root, state="locked")
        refused(M.advance(root, "SpineTestMod", "preflight", by="BENCH", why="x"), "locked", "a lock with no locked_by owner")
        # RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME: the pipeline's 0.1.0 lock under his ruling counts;
        # a bare "pipeline" with no ruling named does not
        efa = getattr(M, "EVIDENCE_FOR_ASK", "RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME")
        synthetic(root, state="locked", locked_by="pipeline")
        refused(M.advance(root, "SpineTestMod", "preflight", by="BENCH", why="x"), "locked",
                "a pipeline lock that names no ruling")
        synthetic(root, state="locked", locked_by="pipeline", per_ruling=efa)
        e = M.evaluate(root, "SpineTestMod", "preflight", by="BENCH", why="x")
        ok("locked" in [p["clause"] for p in e["verdict"]["passed"]],
           "evidence-for-ask: VERSION.json locked by the pipeline under the Evidence-for-Ask ruling passes the lock "
           "clause (read %s)" % [r["clause"] for r in e["verdict"]["refusals"]])
        synthetic(root, state="locked", locked_by="owner")
        refused(M.advance(root, "SpineTestMod", "preflight", by="", why="x"), "by", "a move that names no seat")
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

        next_version_main(root)
        lock_bars_main(root)

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

        # RIMMANDRAKE_SEND_FIXES_TO_NEW_BLIND_JUDGE: the counter counts judge runs; no record of cycle 1 yet, no count
        res = M.advance(root, "Pyrelands", "blind_challenge", by="BENCH", why="a self-move with no judge run")
        rec = M.load(root, "Pyrelands")
        ok(res["ok"] and rec["cycles"] == {"visit": 1, "total": 1} and rec["moves"][-1].get("cycle_not_counted"),
           "a blind-to-blind move before any judge recorded cycle 1 does not raise the counter (%s)" % rec["cycles"])
        bdir = os.path.join(root, "design/concepts/Pyrelands/version/blind_challenge")
        # cycles: two more blind judges, then a 4th needs the Conductor's decision
        for n in (2, 3):
            os.makedirs(os.path.join(bdir, "cycle_%d" % (n - 1)), exist_ok=True)   # the judge of cycle n-1 recorded it
            ok(M.advance(root, "Pyrelands", "blind_challenge", by="BENCH", why="fault fixed in place")["ok"]
               and M.load(root, "Pyrelands")["cycles"]["total"] == n, "cycle %d: a new blind judge" % n)
        os.makedirs(os.path.join(bdir, "cycle_3"), exist_ok=True)
        refused(M.advance(root, "Pyrelands", "blind_challenge", by="BENCH", why="again"), "fourth_cycle",
                "a 4th blind cycle without the Conductor")
        res = M.advance(root, "Pyrelands", "blind_challenge", by="CONDUCTOR", why="one more",
                        conductor="allow one more cycle: the third fix touched only the ember test")
        ok(res["ok"] and M.load(root, "Pyrelands")["cycles"] == {"visit": 4, "total": 4},
           "with the Conductor's decision a 4th cycle runs")
        shutil.rmtree(bdir, ignore_errors=True)
        ivs, bad_iv = MN.parse_interventions(read(root, "Pyrelands", "journal.md"), "journal")
        ok(any(i["stage"] == "4+5" and i["kind"] == "decision" and "one more cycle" in i["what"] for i in ivs)
           and not bad_iv, "the decision is an intervention line maturation_now parses")

        # RIMMANDRAKE_WRITE_STAGE_MOVES_ATOMICALLY: a failed record write leaves no journal line
        jbefore, rbefore = read(root, "Pyrelands", "journal.md"), read(root, "Pyrelands", M.RECORD)
        real_write = M.write_text

        def failing(r, m, p, text):
            if p == M.RECORD:
                raise OSError("disk full (selftest)")
            return real_write(r, m, p, text)
        M.write_text = failing
        try:
            M.advance(root, "Pyrelands", "blind_challenge", by="BENCH", why="a write that fails", conductor="selftest: one more")
            raised = False
        except OSError:
            raised = True
        finally:
            M.write_text = real_write
        ok(raised and read(root, "Pyrelands", "journal.md") == jbefore and read(root, "Pyrelands", M.RECORD) == rbefore,
           "a failed record write raises and leaves the journal and the record as they were")
        calls_ = []

        def failing_j(r, m, p, text):
            calls_.append(p)
            if p == "journal.md":
                raise OSError("journal write failed (selftest)")
            return real_write(r, m, p, text)
        M.write_text = failing_j
        try:
            M.advance(root, "Pyrelands", "blind_challenge", by="BENCH", why="a journal write that fails", conductor="selftest: one more")
        except OSError:
            pass
        finally:
            M.write_text = real_write
        ok(read(root, "Pyrelands", M.RECORD) == rbefore and read(root, "Pyrelands", "journal.md") == jbefore
           and calls_[:2] == [M.RECORD, "journal.md"],
           "the record is written first; a failed journal write puts the record back (%s)" % calls_[:3])

        # hand steps on the later stages
        refused(M.advance(root, "Pyrelands", "in_game", by="BENCH", why="x"), "steward_confirms",
                "leaving the blind challenge without the steward's reading of the verdict")
        for to in ("in_game", "pre_human", "his_walk"):
            ok(M.advance(root, "Pyrelands", to, by="CONDUCTOR", why="x", steward="read the run's verdict: clean")["ok"],
               "Pyrelands moves to %s on the steward's word" % to)
        ok(M.load(root, "Pyrelands")["pre_human_arrivals"] == 1, "arrivals at the pre-human check are counted")
        refused(M.advance(root, "Pyrelands", "passed", by="CONDUCTOR", why="x"), "owner_said",
                "a pass without his words")
        # RIMMANDRAKE_REQUIRE_OWNER_EVENT_TO_PASS: only his event on the OWNER shard passes, and not a refusal
        refused(M.advance(root, "Pyrelands", "passed", by="CONDUCTOR", why="x", owner="Do not pass this"), "owner_said",
                "arbitrary --owner text")
        shard = os.path.join(root, "infrastructure", "state", "ledger", "events", "OWNER.jsonl")
        os.makedirs(os.path.dirname(shard), exist_ok=True)
        with open(shard, "a") as f:
            f.write(json.dumps({"seat": "OWNER", "event": "note", "id": "SELFTEST", "tsn": 4242000000000000001,
                                "ownerSaid": "Pyrelands 0.1.0 passes, ship it"}) + "\n")
            f.write(json.dumps({"seat": "OWNER", "event": "note", "id": "SELFTEST", "tsn": 4242000000000000002,
                                "ownerSaid": "Do not pass this yet"}) + "\n")
        refused(M.advance(root, "Pyrelands", "passed", by="CONDUCTOR", why="x", owner="OWNER:4242000000000000002"),
                "owner_said", "his event that refuses the pass")
        refused(M.advance(root, "Pyrelands", "passed", by="CONDUCTOR", why="x", owner="OWNER:4242000000000000009"),
                "owner_said", "an OWNER:<tsn> not on the shard")
        ok(M.evaluate(root, "Pyrelands", "passed", by="CONDUCTOR", why="x", owner="OWNER:4242000000000000001")["ok"],
           "his real OWNER event passing the version moves it")
        e = M.evaluate(root, "PyrelandsMechanics", "designer", by="BENCH", why="x")
        cl = [r["clause"] for r in e["verdict"]["refusals"]]
        ok("owner_said" not in cl and "intake_closed" not in cl and "owner_said" not in e["hand_steps"],
           "intake after a mod reached his walk asks him nothing (Evidence-for-Ask: his card only said wait for one "
           "full pass): %s" % cl)
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
        # RIMMANDRAKE_REFUSE_EXIT_ON_OWED_SCENE_PARTS_STALE_FLAG: a deciding scene whose scenes.json entry still owes
        # script parts to an open ledger item is no check that runs, whatever the table's stored flag says
        ok(M.load(root, "FlowWorks")["stage"] == "offline_build", "FlowWorks still sits at offline build")
        tt = json.loads(read(root, "FlowWorks", "version/test_table.json"))
        bar = next(b for b in tt["bars"] if b.get("decides") and b.get("every_decider_runnable_today") is True)
        owed = "RIMMANDRAKE_BUILD_SELFTEST_SCENE_PARTS_STILL_OWED"
        sp = os.path.join(root, "design", "concepts", "FlowWorks", "scenes.json")
        with open(sp, "w") as f:
            json.dump({"scenes": [{"id": bar["decides"][0], "owed_parts_item": [owed]}]}, f)
        ev = os.path.join(root, "infrastructure", "state", "ledger", "events")
        os.makedirs(ev, exist_ok=True)
        with open(os.path.join(ev, "BENCH.jsonl"), "w") as f:
            f.write(json.dumps({"seat": "BENCH", "event": "file", "id": owed, "title": "selftest"}) + "\n")

        def owed_refusal():
            return [r for r in M.next_step(root, "FlowWorks")["refusals"]
                    if r["clause"] == "every_bar_has_a_check_that_runs"]
        cl = owed_refusal()
        ok(cl and owed in json.dumps(cl) and bar["id"] in json.dumps(cl),
           "a bar whose deciding scene owes parts to an open item is not runnable (%s)" % json.dumps(cl)[:200])
        with open(os.path.join(ev, "BENCH.jsonl"), "a") as f:
            f.write(json.dumps({"seat": "BENCH", "event": "close", "id": owed}) + "\n")
        cl = owed_refusal()
        listed = cl[0]["observed"].split("not runnable: ", 1)[-1].split(";")[0].split(", ") if cl else []
        ok(owed not in json.dumps(cl) and bar["id"] not in listed,
           "once the owed item closes the bar runs again (only the table's own refusals are left)")
        os.remove(sp)
        shutil.rmtree(os.path.join(root, "infrastructure"))
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


def next_version_main(root):
    """RIMMANDRAKE_WRITE_STAGE_MOVES_ATOMICALLY: next-version moves a passed or newly versioned mod to a new record."""
    mod = "GimmeSomeSlack"
    vp = os.path.join(root, "design", "concepts", mod, "version", "VERSION.json")
    v = json.load(open(vp))
    old = M.load(root, mod)
    r = M.next_version(root, mod, "BENCH", "selftest")
    ok(not r["ok"] and "not newer" in r["why"], "next-version refuses while VERSION.json names the record's version (%s)"
       % r["why"][:80])
    v2 = dict(v, version="9.9.9", state="locked 2026-11-15")
    with open(vp, "w") as f:
        json.dump(v2, f)
    r = M.next_version(root, mod, "BENCH", "selftest: the Designer locked 9.9.9")
    rec = M.load(root, mod)
    kept = read(root, mod, "version/stage_record_%s.json" % old["version"])
    ok(r["ok"] and rec["version"] == "9.9.9" and rec["stage"] == "preflight" and rec["cycles"]["total"] == 0
       and json.loads(kept) == old, "a locked new version: a new record at preflight, the old one kept whole (%s)" % r)
    ok("version change: %s to 9.9.9" % old["version"] in (read(root, mod, "journal.md") or ""),
       "the journal says the version moved")
    ok(MN.read_mod(root, mod, MN.designer_names())["column"] == "2",
       "the status page reads the stage from the record (preflight, column 2)")
    with open(vp, "w") as f:
        json.dump(v, f)


def lock_bars_main(root):
    """RIMMANDRAKE_DERIVE_CHECKS_FROM_LOCKED_BARS: the lock records its bar ids; the table is compared with them."""
    mod, card = "GimmeSomeSlack", "OWNER:1794693278631337978"     # his 2026-11-14 card adding a bar to each of four
    c = os.path.join(root, "design", "concepts", mod, "version")
    vp, tp = os.path.join(c, "VERSION.json"), os.path.join(c, "test_table.json")
    v0, t0 = open(vp).read(), open(tp).read()
    tt = json.loads(t0)
    ids = [b["id"] for b in tt["bars"]]
    v = dict(json.loads(v0), state="locked", locked_from_commit="c0ffee", bars_moved_to_next_version=["moved_out"],
             bars_added_after_lock=[ids[-1]])
    with open(vp, "w") as f:
        json.dump(v, f)
    shown = {"design/concepts/%s/record.json" % mod: {"inventory": [{"id": i} for i in ids[:3]]},
             "design/concepts/%s/tree.json" % mod: {"leaves": [{"id": i} for i in ids[3:-1]] + [{"id": "moved_out"}]}}
    show = lambda commit, path: shown.get(path) if commit == "c0ffee" else None     # noqa: E731
    lb = getattr(M, "lock_bars", None)
    if lb is None:
        ok(False, "lock-bars exists (maturation.lock_bars)")
    else:
        try:
            r = lb(root, mod, "BENCH", "selftest", show=show)
            ok(r["ok"] and r["ids"] == ids, "lock-bars derives the locked bars: required_ids at locked_from_commit, less "
               "the moved, plus the added after lock (%s)" % r["why"][:80])
            r2 = lb(root, mod, "BENCH", "selftest", show=show)
            ok(not r2["ok"] and "already records" in r2["why"], "a second lock-bars with no change is refused")
            r3 = lb(root, mod, "BENCH", "selftest", add=["invented_bar"], show=show)
            ok(not r3["ok"] and "OWNER" in r3["why"], "a bar added with no source is refused: only his card adds one")
            r4 = lb(root, mod, "BENCH", "selftest", add=["invented_bar"], source="OWNER:1", show=show)
            ok(not r4["ok"], "a bar added citing an OWNER event that does not exist is refused")
            r5 = lb(root, mod, "BENCH", "selftest", remove=["not_a_bar"], source=card, show=show)
            ok(not r5["ok"] and "not a locked bar" in r5["why"], "removing a bar that is not locked is refused")
            # the table equals the locked bars: read exactly as before
            ok(M._table_runnable(tt, v, M.locked_bars(root, mod, v)[0]) == M._table_runnable(tt, v),
               "a table holding exactly the locked bars reads as it did with no lock record")
            # the table drops a bar: refused by the reader, the offline-build clause and the Dispatch facts
            short = dict(tt, bars=tt["bars"][1:])
            with open(tp, "w") as f:
                json.dump(short, f)
            bad, why = M._table_runnable(short, v, ids)
            ok(bad is None and "missing %s" % ids[0] in why, "a table missing a locked bar is refused (%s)" % str(why)[:90])
            rp = os.path.join(c, "stage_record.json")
            r_was = open(rp).read() if os.path.exists(rp) else None
            with open(rp, "w") as f:
                json.dump(dict(M.load(root, mod) or {}, mod=mod, version=v["version"], stage="offline_build"), f)
            fa = M.build_facts(root, mod)
            ok("missing %s" % ids[0] in str(fa.get("table_error")) and fa.get("refused_bars") == "UNMEASURED",
               "the Dispatch facts name the missing bar and read no refused-bar count (%s)" % str(fa.get("table_error"))[:60])
            ev = M.evaluate(root, mod, "blind_challenge", by="selftest", why="selftest")
            cl = [x for x in ev["verdict"]["refusals"] if x["clause"] == "every_bar_has_a_check_that_runs"]
            ok(cl and "missing %s" % ids[0] in str(cl[0].get("observed")),
               "the offline build's exit refuses a table missing a locked bar")
            if r_was is None:
                os.remove(rp)
            else:
                with open(rp, "w") as f:
                    f.write(r_was)
            inv = dict(tt, bars=tt["bars"] + [dict(tt["bars"][0], id="invented_bar")])
            bad, why = M._table_runnable(inv, v, ids)
            ok(bad is None and "not locked invented_bar" in why, "a table inventing a bar is refused (%s)" % str(why)[:90])
            r6 = lb(root, mod, "BENCH", "selftest: his card added it", add=["invented_bar"], source=card, show=show)
            ok(r6["ok"] and M._table_runnable(inv, v, M.locked_bars(root, mod, v)[0])[0] is not None,
               "a bar his card added (OWNER:<tsn>) is recorded, and the table holding it reads again")
            ok(M.locked_bars(root, mod, dict(v, version="9.9.9"))[0] is None
               and "records version" in str(M.locked_bars(root, mod, dict(v, version="9.9.9"))[1]),
               "a record of another version's bars is not this version's (it is re-recorded at the new Lock)")
            with open(vp, "w") as f:
                json.dump(dict(v, state="drafting"), f)
            os.remove(os.path.join(c, "locked_bars.json"))
            r7 = lb(root, mod, "BENCH", "selftest", show=show)
            ok(not r7["ok"] and "recorded at Lock" in r7["why"], "an unlocked version has no locked bars to record")
            ok(M.locked_bars(root, mod, v) == (None, None), "no locked_bars.json: the old shape reads as before")
        except Exception as e:      # noqa: BLE001
            ok(False, "lock-bars cases ran (%s: %s)" % (type(e).__name__, e))
    # the reader alone, on a hand-written record (so the base program, which has no lock-bars, is seen to miss it)
    with open(vp, "w") as f:
        json.dump(v, f)
    with open(os.path.join(c, "locked_bars.json"), "w") as f:
        json.dump({"schema": 1, "mod": mod, "version": v["version"], "ids": ids}, f)
    rp = os.path.join(c, "stage_record.json")
    r_was = open(rp).read() if os.path.exists(rp) else None
    with open(rp, "w") as f:
        json.dump(dict(M.load(root, mod) or {}, mod=mod, version=v["version"], stage="offline_build"), f)
    for label, table, needle in (("drops", dict(tt, bars=tt["bars"][1:]), "missing %s" % ids[0]),
                                 ("invents", dict(tt, bars=tt["bars"] + [dict(tt["bars"][0], id="invented_bar")]),
                                  "not locked invented_bar")):
        with open(tp, "w") as f:
            json.dump(table, f)
        try:
            ev = M.evaluate(root, mod, "blind_challenge", by="selftest", why="selftest")
            cl = [x for x in ev["verdict"]["refusals"] if x["clause"] == "every_bar_has_a_check_that_runs"]
            fa = M.build_facts(root, mod)
            ok(cl and needle in str(cl[0].get("observed")) and needle in str(fa.get("table_error")),
               "reader: a table that %s a locked bar fails the offline build's exit and the Dispatch facts (%s)" % (
                   label, str(fa.get("table_error"))[:70]))
        except Exception as e:      # noqa: BLE001
            ok(False, "reader: a table that %s a locked bar (%s: %s)" % (label, type(e).__name__, e))
    if r_was is None:
        os.remove(rp)
    else:
        with open(rp, "w") as f:
            f.write(r_was)
    with open(vp, "w") as f:
        f.write(v0)
    with open(tp, "w") as f:
        f.write(t0)
    if os.path.exists(os.path.join(c, "locked_bars.json")):
        os.remove(os.path.join(c, "locked_bars.json"))


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
                fix_runs=None, lane1_after=None, record_decider=None, fault_key="class", polish_cites=None,
                lane1_extra=None, lane1_rows=True, edited_text=None, planted=None, rerun_row=None, fixed=False,
                lane1_row=None):
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
                row = {"test": t, "command": "python3 selftest_%s.py" % t, "rc": 1 if t == rerun_fail else 0,
                       "result": "FAIL" if t == rerun_fail else "not_rerunnable" if t == record_decider else "PASS",
                       "recorded_result": "PASS", "match": t != rerun_fail}
                if rerun_row and t == rerun_row[0]:
                    row = {k: v for k, v in dict(row, **rerun_row[1]).items() if v is not None}
                f.write(json.dumps(row) + "\n")
    # a FIXED Problem only when the case is about a fix: a cycle's own fixes owe a new blind judge (never met)
    fixed = fixed or fix_runs is not None or fix_red_rc != 1
    faults = [{"id": "RIMMANDRAKE_FIX_SELFTEST_FAULT_SHOWN_RED", "class": "Problem", "status": "FIXED abc1234"},
              {"id": "RIMMANDRAKE_NOTE_SELFTEST_POLISH_LEFT_ALONE", "class": "Polish", "status": "NOTED_FOR_CONDUCTOR"}]
    if not fixed:
        faults[0] = {"id": "RIMMANDRAKE_NOTE_SELFTEST_SECOND_POLISH", "class": "Polish", "status": "NOTED_FOR_CONDUCTOR"}
    if pending_problem:
        faults.append({"id": "RIMMANDRAKE_LEAVE_SELFTEST_PROBLEM_OPEN", "class": "Problem (criterion)",
                       "status": "NOTED_FOR_CONDUCTOR"})
    if polish_cites:   # the Polish fault names a lane-1 row in its evidence
        faults[1]["evidence"] = ["lane1 %s FAIL: one cell short on an exact fit" % polish_cites]
    if fault_key != "class":   # FlowWorks cycle 1 wrote `cls`; None drops the class altogether
        for x in faults:
            c = x.pop("class")
            if fault_key:
                x[fault_key] = c
    with open(os.path.join(d, "lane2", "faults.json"), "w") as f:
        json.dump({"cycle": n, "faults": faults}, f)
    with open(os.path.join(d, "lane2", "fixes.jsonl"), "w") as f:
        f.write(json.dumps({"fault": faults[0]["id"], "red": {"cmd": "python3 t.py", "rc": [fix_red_rc, fix_red_rc]},
                            "green": {"cmd": "python3 t.py", "rc": [0, 0]}}
                           if fix_runs is None else dict(fault=faults[0]["id"], **fix_runs)) + "\n")
    if lane1_after is not None:   # lane 1 rerun after the fixes: {id: verdict}
        with open(os.path.join(d, "lane2", "lane1_rows_after_fix.jsonl"), "w") as f:
            f.write("".join(json.dumps({"id": k, "verdict": v}) + "\n" for k, v in lane1_after.items()))
    with open(os.path.join(d, "lane1", "lane1_rows.jsonl"), "w") as f:
        if lane1_rows:   # the happy fixture has no UNSETTLED row (RIMMANDRAKE_CLOSE_EXIT_READER_LOOPHOLES)
            f.write(json.dumps({"id": "L1_a", "verdict": "PASS"}) + "\n" + json.dumps({"id": "L1_b", "verdict": "INFO"})
                    + "\n" + (json.dumps({"id": "L1_c", "verdict": "FAIL"}) + "\n" if lane1_fail else "")
                    + (json.dumps({"id": "L1_d", "verdict": lane1_extra}) + "\n" if lane1_extra else "")
                    + (json.dumps(lane1_row) + "\n" if lane1_row else ""))
    if edited:
        with open(os.path.join(d, "tests_edited.json"), "w") as f:
            f.write(edited_text if edited_text is not None else json.dumps({"cycle": n, "edited": []}))
    with open(os.path.join(d, "lane2", "planted_results.jsonl"), "w") as f:
        rows = planted if planted is not None else [{"id": "PF_A", "planted": True, "caught": True,
                                                     "tree_clean_after": True}]
        f.write(json.dumps({"baseline": True}) + "\n" + "".join(json.dumps(r) + "\n" for r in rows)
                + json.dumps({"tree_clean_after": tree_clean}) + "\n")


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
            # RIMMANDRAKE_CLOSE_EXIT_READER_LOOPHOLES: one per loophole
            (dict(fix_runs=dict(red={"rc": [1]}, green={"rc": [0]})), "a FIXED Problem whose runs name no command",
             "names no command"),
            (dict(edited_text="not json at all"), "tests_edited.json is not JSON", "not a list of edits"),
            (dict(edited_text='{"cycle": 1}'), "tests_edited.json holds no edits list", "not a list of edits"),
            (dict(planted=[]), "planted_results.jsonl plants no fault", "plants no fault"),
            (dict(planted=[{"id": "PF_A", "planted": True, "caught": False, "tree_clean_after": True}]),
             "no planted fault was caught", "was caught"),
            (dict(planted=[{"id": "PF_A", "caught": True, "tree_clean_after": False}]),
             "a middle planted row left the tree dirty", "not clean"),
            (dict(lane1_extra="UNSETTLED"), "lane 1 has an UNSETTLED row", "L1_d"),
            (dict(lane1_rows=False), "lane 1 has no rows", "no rows"),
            (dict(rerun_row=("T_CONVERT", {"rc": None})), "a decider's rerun PASS has no rc", "T_CONVERT"),
            (dict(rerun_row=("T_CONVERT", {"rc": 1})), "a decider's rerun PASS has rc 1", "rc 1"),
            (dict(rerun_row=("T_CONVERT", {"command": None})), "a decider's rerun PASS names no command",
             "no command"),
        )
        for kw, what, word in broken:
            write_cycle(root, "FlowWorks", 1, **kw)
            ex = M.blind_facts(root, "FlowWorks").get("exit") or {}
            ok(ex.get("state") == "not_met" and word in " ".join(ex.get("why") or []),
               "%s: not met, and the reading says why (%s)" % (what, (ex.get("why") or ["-"])[0][:90]))
        # a fix shown as a list of runs (Pyrelands cycle 1 wrote it so); a lane-1 FAIL cleared by lane 1 after the fixes
        runs = dict(red=[{"cmd": "a", "rc": 1}, {"cmd": "b", "rc": 1}], green=[{"cmd": "a", "rc": 0}, {"cmd": "b", "rc": 0}])
        # RIMMANDRAKE_SEND_FIXES_TO_NEW_BLIND_JUDGE: a cycle whose Problems were FIXED owes a new judge, never met
        for kw, what in ((dict(fix_runs=runs), "a FIXED Problem shown red then green as lists of runs"),
                         (dict(fixed=True), "a FIXED Problem shown red then green")):
            write_cycle(root, "FlowWorks", 1, **kw)
            g = M.blind_facts(root, "FlowWorks")
            ex = g.get("exit") or {}
            ok(ex.get("state") == "not_met" and ex.get("checks", {}).get("judge_owed") is True
               and "new blind judge is owed" in " ".join(ex.get("why") or []) and g.get("owed") == "exit not met",
               "%s: a new blind judge is owed, not met (%s)" % (what, (ex.get("why") or ["-"])[0][:100]))
        # RIMMANDRAKE_DEFER_BLIND_EXIT_STAGE_SIX_ROWS_NEVER_OFFLINE's rows: one bar proving live, one offline
        fw_tt = json.load(open(os.path.join(root, "design/concepts/FlowWorks/version/test_table.json")))
        live_bar = next(b["id"] for b in fw_tt["bars"] if str(b.get("proves_at")) not in M.OFFLINE_PROVES)
        off_bar = next(b["id"] for b in fw_tt["bars"] if str(b.get("proves_at")) in M.OFFLINE_PROVES)
        nk = lambda bars: {"id": "L1_NK_X", "kind": "not_kernel", "verdict": "UNSETTLED", "bars": bars}  # noqa: E731
        met = (
            (dict(lane1_fail=True, lane1_after={"L1_a": "PASS", "L1_b": "INFO", "L1_c": "PASS"}),
             "a lane-1 FAIL that lane 1 after the fixes shows PASS"),
            (dict(lane1_extra="UNSETTLED", lane1_after={"L1_a": "PASS", "L1_d": "PASS"}),
             "a lane-1 UNSETTLED row that lane 1 after the fixes shows PASS"),
            (dict(lane1_fail=True, lane1_after={"L1_a": "PASS", "L1_c": "FAIL"}, polish_cites="L1_c"),
             "a lane-1 FAIL still FAIL after the fixes that a Polish fault names (Polish is not part of passing)"),
            # no fixes at all, so no lane 1 after the fixes: a FAIL a Polish fault owns still clears
            # (RIMMANDRAKE_CLEAR_POLISH_LANE1_FAIL_WITHOUT_ANY_FIX)
            (dict(lane1_fail=True, polish_cites="L1_c"),
             "a lane-1 FAIL a Polish fault names, in a cycle with no fixes (no lane1_rows_after_fix.jsonl)"),
            (dict(lane1_row=nk([live_bar])), "a not_kernel UNSETTLED row on stage-6 bars only (deferred to Stage 6)"),
        )
        for kw, what in met:
            write_cycle(root, "FlowWorks", 1, **kw)
            ex = M.blind_facts(root, "FlowWorks").get("exit") or {}
            ok(ex.get("state") == "met" and (not kw.get("polish_cites") or "Polish" in (ex.get("why") or [""])[0]
                                             and "L1_c" in (ex.get("why") or [""])[0])
               and (not kw.get("lane1_row") or ex.get("checks", {}).get("lane1_deferred_to_stage6") == ["L1_NK_X"]
                    and "deferred to Stage 6" in (ex.get("why") or [""])[0]),
               "%s reads met (%s)" % (what, (ex.get("why") or ["-"])[-1][-120:]))
        # a Polish row later fixed: lane 1 after the fixes shows it PASS, so the reading must not call it left as Polish
        write_cycle(root, "FlowWorks", 1, lane1_fail=True, lane1_after={"L1_a": "PASS", "L1_c": "PASS"}, polish_cites="L1_c")
        ex = M.blind_facts(root, "FlowWorks").get("exit") or {}
        ok(ex.get("state") == "met" and "Polish" not in " ".join(ex.get("why") or []),
           "a Polish lane-1 FAIL that lane 1 after the fixes shows PASS reads met, not left as Polish (%s)"
           % (ex.get("why") or ["-"])[-1][-120:])
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
            (dict(fault_key="cls", fix_red_rc=0), "faults written with `cls`: a FIXED Problem never shown red", "red"),
            (dict(fault_key=None), "faults with no class at all", "no class Problem or Polish"),
            (dict(lane1_fail=True, lane1_after={"L1_a": "PASS", "L1_c": "FAIL"}, polish_cites="L1_cc"),
             "a Polish fault naming another row does not clear a lane-1 FAIL", "still fails L1_c"),
            (dict(fix_runs=dict(red={"cmd": "lint planted copy", "rc": 0}, green={"cmd": "lint planted copy", "rc": 1})),
             "a fix row in the failing direction (red rc 0, green rc 1)", "inverted"),
            (dict(fix_runs=dict(red={"command": "t.py --source <parent Source>", "rc": 1},
                                green={"command": "t.py --source <parent Source>", "rc": 0})),
             "a fix row whose command holds a placeholder", "<parent Source>"),
        )
        # RIMMANDRAKE_DEFER_BLIND_EXIT_STAGE_SIX_ROWS_NEVER_OFFLINE: a not_kernel UNSETTLED row on Stage-6 bars only is
        # deferred to Stage 6; one naming an offline bar, a bar the table lacks, or no bar still blocks
        broken = broken + (
            (dict(lane1_row=nk([live_bar, off_bar])), "a not_kernel UNSETTLED row naming an offline bar", "L1_NK_X"),
            (dict(lane1_row=nk(["no_such_bar_in_the_table"])), "a not_kernel UNSETTLED row naming an unknown bar",
             "L1_NK_X"),
            (dict(lane1_row=nk([])), "a not_kernel UNSETTLED row naming no bar", "L1_NK_X"),
            (dict(lane1_row=dict(nk([live_bar]), kind="fixed")), "a kernel UNSETTLED row on a stage-6 bar", "L1_NK_X"),
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
        ok("rc 0 means the fix holds" in text and "rc 0 when caught" in text,
           "the brief says a fix's command is a test whose rc 0 means the fix holds, a planted-fault catch included")

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


# ---- in-game acceptance (item RIMMANDRAKE_BUILD_IN_GAME_STAGE_LAUNCHER_PYRELANDS_ARRIVED_FIRST) ---------------------
#
# Pyrelands as it stood when it arrived first at in-game acceptance (visit 1), read from git with its blind cycle 1
# record. Written before maturation.py had ingame_facts and watched failing on the base ab858016ee (every check FAIL:
# each runs in chk(), so a missing function fails that check and the next still runs), then passing.
INGAME_SHA = "ab858016ee6b6fcb74e663ddd3487e4b3c5a86a1"
INGAME_CLOCK = 1794741600.0     # 2026-11-15 2:40 AM PST, pinned
INGAME_CYCLE = ("SUMMARY.md", "lane2/faults.json", "lane2/planted_faults.json", "lane2/planted_results.jsonl",
                "lane2/lane1_rows_after_fix.jsonl", "lane1/lane1_rows.jsonl")
FAKE_IDLE = """#!/usr/bin/env python3
import os, sys
with open(os.environ["FAKE_IDLE_LOG"], "a") as f:
    f.write(" ".join(sys.argv[1:]) + "\\n")
v = os.environ.get("FAKE_IDLE", "NOT")
print("TAKEABLE  delegated: bridge idle (free)" if v == "YES" else "NOT TAKEABLE  driver lock held by BENCH (selftest)")
sys.exit(0 if v == "YES" else 1)
"""


def chk(fn, what):
    """ok(fn(), what), with an exception read as FAIL: on the base each check fails by itself."""
    try:
        cond = fn()
    except Exception as e:  # noqa: BLE001
        cond, what = False, "%s (raised %s: %s)" % (what, type(e).__name__, str(e)[:80])
    ok(bool(cond), what)


def copy_ingame(root, mod="Pyrelands", as_mod=None):
    for rel in COPY + ("version/stage_record.json",) + tuple("version/blind_challenge/cycle_1/" + x for x in INGAME_CYCLE):
        r = subprocess.run(["git", "-C", REPO, "show", "%s:design/concepts/%s/%s" % (INGAME_SHA, mod, rel)],
                           capture_output=True, timeout=60)
        if r.returncode == 0:
            dst = os.path.join(root, "design", "concepts", as_mod or mod, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "wb") as f:
                f.write(r.stdout)


def write_ledger(root):
    """One open item caused by a cycle-1 fault, one closed: only the open one is owed."""
    d = os.path.join(root, "infrastructure", "state", "ledger", "events")
    os.makedirs(d, exist_ok=True)
    evs = [{"seat": "CONDUCTOR", "event": "file", "id": "RIMMANDRAKE_PROVE_SELFTEST_HERD_LIVE_OPEN",
            "title": "selftest: prove the herd live", "caused_by": "RIMMANDRAKE_FIX_HERD_ANCHOR_FALLS_BACK_TO_FRESH_ASH"},
           {"seat": "CONDUCTOR", "event": "file", "id": "RIMMANDRAKE_PROVE_SELFTEST_RAIN_LIVE_CLOSED",
            "title": "selftest: closed already", "caused_by": "RIMMANDRAKE_FIX_FORCED_WEATHER_SKIPS_THE_RAIN_LIST"},
           {"seat": "CONDUCTOR", "event": "close", "id": "RIMMANDRAKE_PROVE_SELFTEST_RAIN_LIVE_CLOSED"}]
    with open(os.path.join(d, "BENCH.jsonl"), "w") as f:
        f.write("".join(json.dumps(e) + "\n" for e in evs))


def write_visit(root, mod, n, exit_met=True, drop=None, fail=None, rerun_pass=False, site=True, game="archmagi",
                sha="abc1234", strange=None, strange_open=None, strange_file=True, save=True, rows_file=True,
                block=True, sha2=None, save_text="<?xml version=\"1.0\"?>\n<savegame><meta/></savegame>",
                site_reading={"biome": "Pyrelands", "colonists_alive": 3}):
    """A visit record in the layout maturation.py reads, every file present, with one thing broken on request."""
    tt = json.load(open(os.path.join(root, "design", "concepts", mod, "version", "test_table.json")))
    ids = [k for k, t in tt["tests"].items() if str(t.get("kind", "")).startswith("live") and str(t.get("stage")) == "6"]
    d = os.path.join(root, "design", "concepts", mod, "version", "in_game", "visit_%d" % n)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    sv = os.path.join(root, "Saves", "%s_stage6_visit%d.rws" % (mod, n))
    os.makedirs(os.path.dirname(sv), exist_ok=True)
    if save:
        open(sv, "w").write(save_text)
    elif os.path.exists(sv):
        os.remove(sv)
    if rows_file:
        with open(os.path.join(d, "rows.jsonl"), "w") as f:
            for t in ids:
                if t == drop:
                    continue
                row = {"test": t, "verdict": "FAIL" if t == fail else "PASS", "site_checked": site, "game": game,
                       "mod_sha": sha2 if (sha2 and t == ids[-1]) else sha, "command": tt["tests"][t].get("command"), "evidence": "selftest",
                       "site": site_reading}
                f.write(json.dumps({k: v for k, v in row.items() if v is not None}) + "\n")
                if t == fail and rerun_pass:
                    f.write(json.dumps(dict(row, verdict="PASS")) + "\n")
    strange = ([{"what": "a selftest oddity", "explained": "vanilla does it too, seen on an unmodded control map"}]
               if strange is None else strange)
    if strange_file:
        with open(os.path.join(d, "strange.jsonl"), "w") as f:
            f.write("".join(json.dumps(x) + "\n" for x in strange))
    left = sum(1 for x in strange if not M._strange_settled(x))
    shown = ", ".join("%s: %s" % (t, "fail" if (t == fail and not rerun_pass) else "pass") for t in ids if t != drop)
    with open(os.path.join(d, "SUMMARY.md"), "w") as f:
        if block:
            f.write("# visit %d\n\n## Exit\n```\ningame_rows: {%s}\nstrange_open: %d\nsavegame: %s\nexit_met: %s\n```\n"
                    "\n## Owed\nnone\n" % (n, shown, left if strange_open is None else strange_open, sv,
                                           str(exit_met).lower()))
        else:
            f.write("# visit %d\n\n## Exit\n(pending)\n" % n)
    return ids


def ingame_main():
    """In-game acceptance: brief, next (a program's exit reading) and launch, offline, through a fake detached_helper
    and a fake bridge reading. Never touches the real bridge: MATURATION_BRIDGE_IDLE is a stand-in throughout."""
    before = git_status()
    root = tempfile.mkdtemp(prefix="maturation_ingame_")
    keys = ("MATURATION_DETACHED_HELPER", "FAKE_DH_LOG", "MATURATION_BRIEF_DIR", "MATURATION_CLOCK",
            "MATURATION_BRIDGE_IDLE", "FAKE_IDLE", "FAKE_IDLE_LOG")
    env_was = {k: os.environ.get(k) for k in keys}
    try:
        copy_ingame(root)
        write_ledger(root)
        fake, log = os.path.join(root, "fake_dh.py"), os.path.join(root, "fake_dh.log")
        idle, ilog = os.path.join(root, "fake_idle.py"), os.path.join(root, "fake_idle.log")
        with open(fake, "w") as f:
            f.write(FAKE_DH)
        with open(idle, "w") as f:
            f.write(FAKE_IDLE)
        open(log, "w").close()
        open(ilog, "w").close()
        os.environ.update(MATURATION_DETACHED_HELPER=fake, FAKE_DH_LOG=log, MATURATION_CLOCK=str(INGAME_CLOCK),
                          MATURATION_BRIEF_DIR=os.path.join(root, "briefs"), MATURATION_BRIDGE_IDLE=idle,
                          FAKE_IDLE="NOT", FAKE_IDLE_LOG=ilog)
        P = "Pyrelands"

        def calls():
            with open(log) as f:
                return [json.loads(x) for x in f if x.strip()]

        tt = json.load(open(os.path.join(root, "design/concepts/Pyrelands/version/test_table.json")))
        live6 = [k for k, t in tt["tests"].items() if str(t.get("kind", "")).startswith("live") and t.get("stage") == "6"]

        # ---- visit 1 owed --------------------------------------------------------------------------------------------
        chk(lambda: (lambda g: g["owed"] == "run" and g["visit"] == 1 and g["checks"] == live6 and g["testq"] == []
                     and g["exit"]["state"] == "absent")(M.ingame_facts(root, P)),
            "Pyrelands at in_game, no visit folder: visit 1 is owed, the %d stage-6 checks named, none with testq"
            % len(live6))
        chk(lambda: (lambda nx: nx["launch"].startswith("maturation.py launch Pyrelands --budget-usd")
                     and "in-game visit 1" in nx["launch"] and "steward_confirms" in nx["hand_steps"]
                     and "version/in_game/visit_1" in nx["next"])(M.next_step(root, P)),
            "next names the launch (not \"none at this stage\"), its record folder, and the steward stays a hand step")
        text = [""]

        def brief():
            text[0] = M.brief_text(root, P)[0]
            return text[0].startswith("# In-game acceptance (Stage 6): Pyrelands 0.1.0, visit 1")
        chk(brief, "the brief at in_game is an in-game acceptance brief")
        chk(lambda: all(("`%s`" % k) in text[0] and ("`%s`" % tt["tests"][k]["command"]) in text[0] for k in live6),
            "the brief names every stage-6 check with its exact command, from the mod's own table")
        chk(lambda: all(w in text[0] for w in ("bridge take --idle-ok --for \"Pyrelands in-game acceptance visit 1\"",
                                               "bridge release --seat BENCH", "Never a flyer's flight",
                                               "Never leave a broken game running", "all five DLC",
                                               "smallest list", "never restore his list")),
            "the brief carries the bridge rules: idle-ok take, release at stop, no flight, no broken game, DLC, list")
        chk(lambda: "none of this mod's %d checks carries one" % len(live6) in text[0]
            and "pipeline_admit.py" in text[0], "the brief says SteveDesktop's queue admits none (no testq block)")
        chk(lambda: all(w in text[0] for w in ("RIMMANDRAKE_FIX_FORCED_WEATHER_SKIPS_THE_RAIN_LIST",
                                               "RIMMANDRAKE_EXTEND_NO_RAIN_SCENE_WITH_FORCED_WEATHER", "`sc_no_rain`",
                                               "PF_PROBE_CALLER_NEVER_WET", "PF_HERD_CALLER_ANCHOR_ALWAYS",
                                               "nk_flamefang_venom", "forced RainyThunderstorm")),
            "the brief lists what the blind cycle left owed: the rain fix and its scene, both planted misses, lane 1's "
            "UNSETTLED rows, its Owed text")
        chk(lambda: "RIMMANDRAKE_PROVE_SELFTEST_HERD_LIVE_OPEN" in text[0]
            and "RIMMANDRAKE_PROVE_SELFTEST_RAIN_LIVE_CLOSED" not in text[0],
            "an open ledger item caused by a cycle fault is owed; a closed one is not")
        chk(lambda: all(w in text[0] for w in ("design/concepts/Pyrelands/version/in_game/visit_1/SUMMARY.md",
                                               "ingame_rows:", "strange_open:", "savegame:", "exit_met: true|false",
                                               "diagnose it by experiment", "Never run `maturation.py advance`")),
            "the brief names the skeleton, the machine-checkable exit block, diagnosis in the sitting, no advance")
        chk(lambda: M.INGAME_DEFAULT[:50] in text[0], "no stage-6 decision written: the standing default")
        t2 = json.loads(json.dumps(tt))
        t2["tests"][live6[0]]["testq"] = {"chain": "selftest"}
        ttp = os.path.join(root, "design/concepts/Pyrelands/version/test_table.json")
        with open(ttp, "w") as f:
            json.dump(t2, f)
        chk(lambda: M.ingame_facts(root, P)["testq"] == [live6[0]] and "1 of %d of this mod's checks carry one (%s)" % (
            len(live6), live6[0]) in M.brief_text(root, P)[0], "a check with a testq block is named for SteveDesktop")
        with open(ttp, "w") as f:
            json.dump(tt, f)

        # ---- launch --------------------------------------------------------------------------------------------------
        chk(lambda: M.launch_mod(root, P, 20, ITEM, model="sonnet", bridge=lambda p, s: (True, "free"))[0] == 2
            and not calls(), "a live driver below opus refuses")
        chk(lambda: M.launch_mod(root, P, 20, ITEM, model="fable", bridge=lambda p, s: (True, "free"))[0] == 2
            and not calls(), "fable refuses too (never on a live resource)")
        chk(lambda: (lambda r: r[0] == 2 and "held by SOMEONE" in r[1] and not calls())(
            M.launch_mod(root, P, 20, ITEM, bridge=lambda p, s: (False, "held by SOMEONE"))),
            "the bridge held by another: launch refuses, naming the holder, and launches nothing")
        chk(lambda: (lambda r: r[0] == 2 and "NOT TAKEABLE" in r[1] and not calls()
                     and "bridge idle --for Pyrelands in-game acceptance visit 1 --seat BENCH" in open(ilog).read())(
            M.launch_mod(root, P, 20, ITEM)),
            "with no stand-in, launch asks `rimflow bridge idle` (here the fake): NOT TAKEABLE refuses")
        os.environ["FAKE_IDLE"] = "YES"
        chk(lambda: M.bridge_idle("x")[0] is True, "bridge_idle reads TAKEABLE rc 0 as takeable")
        os.environ["FAKE_IDLE"] = "NOT"
        chk(lambda: M.bridge_idle("x") == (False, "NOT TAKEABLE  driver lock held by BENCH (selftest)"),
            "bridge_idle reads NOT TAKEABLE rc 1 as not takeable, with its line")
        asked = []

        def go():
            r = M.launch_mod(root, P, 20, ITEM, bridge=lambda p, s: (asked.append((p, s)) or (True, "free")))
            c = calls()
            return (r[0] == 0 and r[2] and len(c) == 1 and c[0][c[0].index("--budget-usd") + 1] == "20"
                    and c[0][c[0].index("--model") + 1] == "opus" and asked == [("Pyrelands in-game acceptance visit 1",
                                                                                 "BENCH")]
                    and "# In-game acceptance (Stage 6)" in open(c[0][c[0].index("--brief-file") + 1]).read())
        chk(go, "the bridge takeable: one launch, the cap, opus, the in-game brief")

        # ---- the exit reading ----------------------------------------------------------------------------------------
        def reads(kw, state, word=None):
            write_visit(root, P, 1, **kw)
            ex = M.ingame_facts(root, P)["exit"]
            return ex["state"] == state and (word is None or word in " ".join(ex["why"]))
        chk(lambda: reads({}, "met"), "a complete visit record whose block and files agree reads met")
        chk(lambda: (lambda nx: "exit met" in nx["next"] and "--to pre_human" in nx["next"]
                     and nx["launch"].startswith("none") and "steward_confirms" in nx["hand_steps"])(M.next_step(root, P)),
            "next: exit met is a program reading, the steward confirms the move to pre_human, nothing to launch")
        chk(lambda: M.launch_mod(root, P, 20, ITEM, bridge=lambda p, s: (True, "free"))[0] == 2 and len(calls()) == 1,
            "launch refuses a visit already recorded")
        chk(lambda: reads(dict(fail=live6[1], rerun_pass=True), "not_met", "an earlier row reads FAIL"),
            "a FAIL rerun PASS in the sitting: the later PASS does not hide the FAIL, not met "
            "(RIMMANDRAKE_CLOSE_EXIT_READER_LOOPHOLES)")
        broken = (
            (dict(exit_met=False), "the driver's block says exit_met false", "exit_met false"),
            (dict(fail=live6[1]), "a check's last row FAILs", live6[1]),
            (dict(drop=live6[2]), "a check has no row and is left out of the block", live6[2]),
            (dict(site=False), "a row does not say the site was checked", "site_checked"),
            (dict(game=None), "a row names no game", "names no game"),
            (dict(sha=None), "a row names no mod_sha", "mod_sha"),
            (dict(strange=[{"what": "a pawn walking on lava"}]), "a strange thing neither explained nor filed",
             "neither explained nor filed"),
            (dict(strange=[{"what": "odd", "filed": "RIMMANDRAKE_X_Y_Z_Q"}], strange_open=1),
             "the block's strange_open disagrees with the file", "strange_open 1"),
            (dict(strange_file=False), "strange.jsonl is missing", "strange.jsonl"),
            (dict(save=False), "the savegame is not on disk", "not on disk"),
            (dict(rows_file=False), "rows.jsonl is missing", "rows.jsonl is missing"),
            # RIMMANDRAKE_CLOSE_EXIT_READER_LOOPHOLES: one per loophole
            (dict(save_text="just some text"), "the savegame file is not a RimWorld save", "not a RimWorld save"),
            (dict(strange=[{"what": "odd", "filed": "yes"}]), "a strange thing filed as 'yes', no item named",
             "neither explained"),
            (dict(strange=[{"what": "odd", "explained": "ok"}]), "a strange thing explained as 'ok'",
             "neither explained"),
            (dict(site_reading=None), "site_checked true with no site reading and no evidence file",
             "nothing to show it"),
            (dict(sha="latest"), "a mod_sha that is not a hash", "not a commit hash"),
            (dict(sha2="def5678"), "rows on two builds (RIMMANDRAKE_BIND_STAGE_EVIDENCE_TO_ONE_BUILD)", "more than one build"),
        )
        for kw, what, word in broken:
            chk(lambda kw=kw, word=word: reads(kw, "not_met", word), "%s: not met, and the reading says why" % what)
        chk(lambda: reads(dict(block=False), "no_exit_block") and M.ingame_facts(root, P)["owed"] == "no exit block"
            and M.next_step(root, P)["launch"].startswith("none"),
            "a visit folder whose Exit reads (pending) has no exit block, and next launches nothing")
        chk(lambda: M.native_to_here("C:\\Users\\Mandrake\\Saves\\a.rws") == "/mnt/c/Users/Mandrake/Saves/a.rws",
            "a Windows savegame path is read as this machine reads it")
        shutil.rmtree(os.path.join(root, "design/concepts/Pyrelands/version/in_game"), ignore_errors=True)
        jp = os.path.join(root, "design/concepts/Pyrelands/journal.md")
        jsaved = open(jp).read()
        with open(jp, "w") as f:
            f.write(M.add_intervention(jsaved, "- CONDUCTOR INTERVENED (stage 6, 2026-11-15 2:30 AM PST, kind hold): "
                                               "selftest hold. Source: selftest."))
        chk(lambda: M.ingame_facts(root, P)["owed"] == "blocked"
            and M.launch_mod(root, P, 20, ITEM, bridge=lambda p, s: (True, "free"))[0] == 2 and len(calls()) == 1,
            "a hold on stage 6 blocks: no launch")
        with open(jp, "w") as f:
            f.write(M.add_intervention(jsaved, "- CONDUCTOR INTERVENED (stage 6, 2026-11-15 2:31 AM PST, kind "
                                               "decision): selftest says run the rain scene first. Source: selftest."))
        chk(lambda: "selftest says run the rain scene first" in M.brief_text(root, P)[0]
            and M.INGAME_DEFAULT[:50] not in M.brief_text(root, P)[0],
            "a stage-6 CONDUCTOR INTERVENED line fills the steward's section")
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
    sys.exit(launch_main() if "--launch" in a else blind_main() if "--blind" in a else ingame_main() if "--ingame" in a
             else main())
