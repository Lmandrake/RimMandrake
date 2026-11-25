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
import build_match as BM        # noqa: E402
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


ISOLATE = ("RM_REFUSAL_DIR", "RM_OPS_WATCH_DIR", "RM_DISPATCHER_STATE", "RM_JUDGE_CALIBRATION")


def isolate(root):
    """Point the refusal store, the told ledger and the dispatcher state at this run's own temp tree, whatever the
    caller set: advance() submits its verdict (RIMMANDRAKE_COUNT_ADVANCE_REFUSALS_SO_A_LOOP_RINGS), and a test may
    neither write the real store nor raise a real alarm (lesson 20261112T234316Z). -> the saved values, for restore."""
    was = {k: os.environ.get(k) for k in ISOLATE}
    os.environ.update(RM_REFUSAL_DIR=os.path.join(root, "_refusals"), RM_OPS_WATCH_DIR=os.path.join(root, "_ops"),
                      RM_DISPATCHER_STATE=os.path.join(root, "_dispatcher"),
                      RM_JUDGE_CALIBRATION=os.path.join(root, "_no_calibration.json"))      # absent: every family UNTESTED
    for k in ISOLATE[:3]:       # incident.append does not make its directory: the real OPS dir is always there
        os.makedirs(os.environ[k], exist_ok=True)
    return was


def restore(was):
    for k, v in was.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


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
    certify_fixture(root, FOUR + ("PyrelandsMechanics",))


def certify_fixture(root, mods=None):
    """Stamp each fixture mod's offline bar deciders as run green on the fixture's build (a stub file where the scratch
    root has none, the command kept, known_red cleared), so a test of another clause is not refused by the
    pre-judgement certificate; the certificate's own cases un-stamp one test (certificate_cases)."""
    import judge_certificate as JC
    croot = os.path.join(root, "design", "concepts")
    for mod in mods or sorted(os.listdir(croot)):
        tt, _ = JC.read_table(root, mod)
        if tt is None:
            continue
        dec = {d for b in tt["bars"] if isinstance(b, dict) for d in b.get("offline_decides") or []}
        for d in sorted(dec):
            t = tt["tests"].get(d)
            if not isinstance(t, dict):
                tt["bars"] = [dict(b, offline_decides=[x for x in b.get("offline_decides") or [] if x != d])
                              if isinstance(b, dict) else b for b in tt["bars"]]
                continue
            t.setdefault("file", "src/fixture/%s.py" % d)
            t.setdefault("command", "true")
            fp = os.path.join(root, t["file"])
            if t["file"].endswith("/"):
                os.makedirs(fp, exist_ok=True)
            elif not os.path.isfile(fp):
                os.makedirs(os.path.dirname(fp), exist_ok=True)
                with open(fp, "w") as f:
                    f.write("# fixture stub of %s\n" % d)
            t.pop("known_red", None)
        for d in sorted(dec):       # stamped after every stub exists: one test's file can be another's read
            t = tt["tests"].get(d)
            if isinstance(t, dict):
                t["runs_today"] = {"ran": True, "rc": 0, "seconds": 0.1, "last": "fixture: passed", "at": "fixture",
                                   "result": "PASS", "build": JC.test_build(root, t)}
        with open(JC.tpath(root, mod), "w", encoding="utf-8") as f:
            json.dump(tt, f, indent=1)
        # red_seen: the fixture's stubs are grandfathered as they are now (a copied list names the real files' blobs)
        JC._write_evidence(root, mod, JC.GRANDFATHER, {d: JC.test_blob(root, tt["tests"][d]) for d in sorted(dec)
                                                       if isinstance(tt["tests"].get(d), dict)})


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


def redden_table(root, mod, last="T_CORE: 3 of 3 runs failed"):
    """-> the table's saved text, after turning its first offline bar decider red (PRE_JUDGEMENT_CERTIFICATE cases)."""
    tp = os.path.join(root, "design", "concepts", mod, "version", "test_table.json")
    saved = open(tp).read()
    tt = json.loads(saved)
    tid = next(d for b in tt["bars"] for d in b.get("offline_decides") or [] if d in tt["tests"])
    tt["tests"][tid]["runs_today"].update(rc=1, result="FAIL", last=last)
    with open(tp, "w") as f:
        json.dump(tt, f, indent=1)
    return saved


def restore_table(root, mod, saved):
    with open(os.path.join(root, "design", "concepts", mod, "version", "test_table.json"), "w") as f:
        f.write(saved)


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


def isolation_check():
    """The plain suite's advance verdicts are fixtures, not judgements: with the real registry showing the advance family
    CALIBRATED they must still be advisory (uncounted), or its 40-odd verdicts pool into one family window that rings
    REFUSAL_NOTHING_COULD_EVER_PASS on itself (RIMMANDRAKE_WIDEN_FAMILY_TRIP_MARGIN_SUITE_ALMOST_RANG)."""
    root = tempfile.mkdtemp(prefix="maturation_isolation_")
    keys = ISOLATE + ("RM_JUDGE_CALIBRATION", "RM_CALIBRATION_ROOT")
    was = {k: os.environ.get(k) for k in keys}
    try:
        with open(os.path.join(root, "brief.md"), "w") as f:
            f.write("a calibrated brief\n")
        cal = os.path.join(root, "ambient_cal.json")
        with open(cal, "w") as f:
            json.dump({"families": {FAM: {"brief": ["brief.md"], "hash": RC.brief_hash(["brief.md"], root),
                                          "status": "CALIBRATED", "cases": {}}}}, f)
        os.environ.update(RM_JUDGE_CALIBRATION=cal, RM_CALIBRATION_ROOT=root)
        ok(RC.status(FAM) == "CALIBRATED", "isolation probe: the ambient registry really calls the family CALIBRATED")
        isolate(root)
        ok(RC.advisory(FAM), "isolate() makes the advance family advisory even when the ambient registry calibrates it (%s)"
           % RC.status(FAM))
    finally:
        restore(was)
        shutil.rmtree(root, ignore_errors=True)


def main():
    before = git_status()
    isolation_check()

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
    env_was = isolate(root)
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
        # RIMMANDRAKE_KEEP_UNREADABLE_RECORD_WHEN_SEEDING_SAYS_NEVER: an unreadable record is not an absent one
        with open(os.path.join(M.mod_dir(root, "ExplosiveKnockback"), M.RECORD), "w", encoding="utf-8") as f:
            f.write("{not json (selftest)")
        try:
            M.seed_mod(root, "ExplosiveKnockback", live=False)
            seed_err = None
        except ValueError as e:
            seed_err = e
        ok(seed_err is not None and read(root, "ExplosiveKnockback", M.RECORD) == "{not json (selftest)",
           "seeding over an unreadable record refuses and leaves the file as it was (%r)" % (seed_err,))
        with open(os.path.join(M.mod_dir(root, "ExplosiveKnockback"), M.RECORD), "w", encoding="utf-8") as f:
            f.write(snap)
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
        # PRE_JUDGEMENT_CERTIFICATE (RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN): a red deciding test
        # refuses the move into the blind challenge with its path to pass, and writes nothing
        gw = "walk_scavenger_base: sc_walk's entry exists; only his look waits"
        tsaved = redden_table(root, "GimmeSomeSlack")
        j0, r0 = read(root, "GimmeSomeSlack", "journal.md"), read(root, "GimmeSomeSlack", M.RECORD)
        res = M.advance(root, "GimmeSomeSlack", "blind_challenge", by="BENCH", why="x", steward=gw)
        refused(res, "judge_certificate", "a red deciding test at the move into the blind challenge")
        jc = [r for r in res["verdict"]["refusals"] if r["clause"] == "judge_certificate"]
        ok(jc and "3 of 3" in str(jc[0]["observed"]) and "--run" in str(jc[0]["smallest_fix"]["what"]),
           "the certificate refusal quotes the test's own last line and names the rerun that passes it")
        ok(read(root, "GimmeSomeSlack", "journal.md") == j0 and read(root, "GimmeSomeSlack", M.RECORD) == r0,
           "a certificate refusal writes nothing")
        restore_table(root, "GimmeSomeSlack", tsaved)
        ok(M.advance(root, "GimmeSomeSlack", "blind_challenge", by="BENCH", why="x", steward=gw)["ok"],
           "with the steward's word Gimme Some Slack enters the blind challenge")
        tsaved = redden_table(root, "GimmeSomeSlack")
        e = M.evaluate(root, "GimmeSomeSlack", "in_game", steward="the cycle read")
        ok("judge_certificate" in [r["clause"] for r in e["verdict"]["refusals"]],
           "a red deciding test refuses the move into the in-game stage too (%s)" % [
               r["clause"] for r in e["verdict"]["refusals"]])
        with open(os.path.join(root, "design", "concepts", "GimmeSomeSlack", "version", "test_table.json"), "w") as f:
            f.write("{ not json")
        e = M.evaluate(root, "GimmeSomeSlack", "in_game", steward="the cycle read")
        ok("judge_certificate" in [p["clause"] for p in e["verdict"]["passed"]],
           "an unreadable table: the certificate did not run and lets the move through")
        restore_table(root, "GimmeSomeSlack", tsaved)
        # a known_red mark whose item has closed still refuses, and says the mark is stale
        tt = json.loads(tsaved)
        kid = next(d for b in tt["bars"] for d in b.get("offline_decides") or [] if d in tt["tests"])
        tt["tests"][kid]["known_red"] = "SELFTEST_CLOSED_ITEM"
        with open(os.path.join(root, "design", "concepts", "GimmeSomeSlack", "version", "test_table.json"), "w") as f:
            json.dump(tt, f, indent=1)
        shard = os.path.join(root, "infrastructure", "state", "ledger", "events", "SELFTEST.jsonl")
        os.makedirs(os.path.dirname(shard), exist_ok=True)
        with open(shard, "a") as f:
            f.write(json.dumps({"seat": "BENCH", "event": "close", "id": "SELFTEST_CLOSED_ITEM", "tsn": 1}) + "\n")
        e = M.evaluate(root, "GimmeSomeSlack", "in_game", steward="the cycle read")
        jc = [r for r in e["verdict"]["refusals"] if r["clause"] == "judge_certificate"]
        ok(jc and "stale" in str(jc[0]["smallest_fix"]["what"]) and "SELFTEST_CLOSED_ITEM" in str(jc[0]["observed"]),
           "a known_red naming a closed item refuses with the fix: the mark is stale")
        os.remove(shard)
        restore_table(root, "GimmeSomeSlack", tsaved)

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
        # RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS: the Conductor window's lock counts (it names its ledger
        # event); the same lock by a launched helper does not
        import conductor_acts as CA
        cshard = os.path.join(root, "infrastructure", "state", "ledger", "events", "OWNER.jsonl")
        os.makedirs(os.path.dirname(cshard), exist_ok=True)
        cwhy = CA.tagged("lock SpineTestMod at 0.1.0: the Designer pass is complete", "design version lock")
        with open(cshard, "a") as f:
            f.write(json.dumps({"seat": "OWNER", "event": "note", "id": "X", "ts": "2026-11-19T16:00:00Z",
                                "tsn": 9190000001, "perRuling": CA.RULING, "why": cwhy, "ranBy": "BENCH"}) + "\n")
            f.write(json.dumps({"seat": "OWNER", "event": "note", "id": "X", "ts": "2026-11-19T16:00:01Z",
                                "tsn": 9190000002, "perRuling": CA.RULING, "why": cwhy, "ranBy": "BENCH",
                                "role_unit": "rm-detached-bench-x-1"}) + "\n")
        synthetic(root, state="locked", locked_by="conductor", per_ruling=CA.RULING, conductor_event="OWNER:9190000001")
        e = M.evaluate(root, "SpineTestMod", "preflight", by="BENCH", why="x")
        ok("locked" in [p["clause"] for p in e["verdict"]["passed"]],
           "five acts: the Conductor window's lock passes the lock clause (read %s)"
           % [r["clause"] for r in e["verdict"]["refusals"]])
        synthetic(root, state="locked", locked_by="conductor", per_ruling=CA.RULING, conductor_event="OWNER:9190000002")
        refused(M.advance(root, "SpineTestMod", "preflight", by="BENCH", why="x"), "locked",
                "a 'conductor' lock whose event a launched helper wrote")
        synthetic(root, state="locked", locked_by="conductor", per_ruling=CA.RULING)
        refused(M.advance(root, "SpineTestMod", "preflight", by="BENCH", why="x"), "locked",
                "a 'conductor' lock that names no ledger event")
        # the pass at his walk stays his: a Conductor event is not his word (owner_event)
        ev_, why_ = M.owner_event(root, "OWNER:9190000001")
        ok(ev_ is None and "no byCard or ownerSaid" in why_, "five acts: the Conductor's act never passes his walk (%s)"
           % why_)
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
        # RIMMANDRAKE_FINISH_ROLLBACK_WHEN_A_RESTORE_WRITE_FAILS: a put-back that fails does not stop the others, and
        # the error names every file left unrestored
        rec_ = M.load(root, "Pyrelands")
        nrec_ = dict(rec_, why_selftest="a move whose rollback half-fails")
        rec_writes = []

        def failing_back(r, m, p, text):
            if p == "journal.md":
                raise OSError("journal write failed (selftest)")
            if p == M.RECORD:
                rec_writes.append(text)
                if len(rec_writes) == 2:
                    raise OSError("record put-back failed (selftest)")
            return real_write(r, m, p, text)
        M.write_text = failing_back
        err_ = None
        try:
            M.commit_move(root, "Pyrelands", nrec_, "journal (selftest)\n", first={"selftest_first.json": "{}\n"})
        except Exception as e:
            err_ = e
        finally:
            M.write_text = real_write
        first_left = os.path.lexists(os.path.join(M.mod_dir(root, "Pyrelands"), "selftest_first.json"))
        ok(isinstance(err_, getattr(M, "RollbackIncomplete", ())) and M.RECORD in str(err_) and "selftest_first.json" not in str(err_)
           and not first_left and read(root, "Pyrelands", "journal.md") == jbefore,
           "a failed record put-back still removes the new pass file and names the record as unrestored (%r, first "
           "left %s)" % (err_, first_left))
        real_write(root, "Pyrelands", M.RECORD, rbefore)
        # two put-backs fail (the record write and the new file's removal): both are named
        rec_writes.clear()
        real_remove = os.remove

        def failing_remove(path):
            if path.endswith("selftest_first.json"):
                raise PermissionError("remove refused (selftest)")
            return real_remove(path)
        M.write_text, os.remove = failing_back, failing_remove
        err_ = None
        try:
            M.commit_move(root, "Pyrelands", nrec_, "journal (selftest)\n", first={"selftest_first.json": "{}\n"})
        except Exception as e:
            err_ = e
        finally:
            M.write_text, os.remove = real_write, real_remove
        ok(isinstance(err_, getattr(M, "RollbackIncomplete", ())) and M.RECORD in str(err_)
           and "selftest_first.json" in str(err_) and read(root, "Pyrelands", "journal.md") == jbefore,
           "a failed removal and a failed record put-back are both named (%r)" % (err_,))
        real_remove(os.path.join(M.mod_dir(root, "Pyrelands"), "selftest_first.json"))
        real_write(root, "Pyrelands", M.RECORD, rbefore)
        # an existing file that cannot be read is never written over: its old text could not be put back
        upath = os.path.join(M.mod_dir(root, "Pyrelands"), "journal.md")
        real_read = M.read_text
        M.read_text = lambda r, m, p: None if p == "journal.md" else real_read(r, m, p)
        err_ = None
        try:
            M.commit_move(root, "Pyrelands", nrec_, "journal (selftest)\n")
        except Exception as e:
            err_ = e
        finally:
            M.read_text = real_read
        ok(err_ is not None and os.path.exists(upath) and read(root, "Pyrelands", "journal.md") == jbefore
           and read(root, "Pyrelands", M.RECORD) == rbefore,
           "an unreadable existing journal refuses the move and the record is put back (%r)" % (err_,))

        # hand steps on the later stages
        refused(M.advance(root, "Pyrelands", "in_game", by="BENCH", why="x"), "steward_confirms",
                "leaving the blind challenge without the steward's reading of the verdict")
        # RIMMANDRAKE_BIND_ADVANCE_TO_EXIT_READINGS: the steward's word alone no longer moves a mod past an unmet exit
        refused(M.advance(root, "Pyrelands", "in_game", by="CONDUCTOR", why="x", steward="read the run's verdict: clean"),
                "exit_met", "a steward's word alone on a blind cycle with no exit reading")
        oshard = os.path.join(root, "infrastructure", "state", "ledger", "events", "OWNER.jsonl")
        os.makedirs(os.path.dirname(oshard), exist_ok=True)
        with open(oshard, "a") as f:
            f.write(json.dumps({"seat": "OWNER", "event": "note", "id": "SELFTEST", "tsn": 1000000000000000000,
                                "ownerSaid": "Pyrelands may go in game"}) + "\n")
            f.write(json.dumps({"seat": "OWNER", "event": "note", "id": "SELFTEST", "tsn": 4242000000000000003,
                                "ownerSaid": "Pyrelands goes to the in-game stage as it is"}) + "\n")
        refused(M.advance(root, "Pyrelands", "in_game", by="CONDUCTOR", why="x", steward="read the run's verdict: clean",
                          owner="OWNER:1000000000000000000"), "exit_met", "his event older than the cycle it would override")
        # newer than the cycle's opening is not enough: his event must be newer than the reading's newest evidence
        import time as _time
        t_mid = int(_time.time() * 1e9)
        with open(oshard, "a") as f:
            f.write(json.dumps({"seat": "OWNER", "event": "note", "id": "SELFTEST", "tsn": t_mid,
                                "ownerSaid": "Pyrelands goes in game"}) + "\n")
        cyc = os.path.join(root, "design", "concepts", "Pyrelands", M.BLIND_DIR, "cycle_%d" % M.blind_facts(
            root, "Pyrelands")["cycle"])
        os.makedirs(cyc, exist_ok=True)
        _time.sleep(0.05)
        with open(os.path.join(cyc, "SUMMARY.md"), "w") as f:
            f.write("# a cycle written after his word\n")
        refused(M.evaluate(root, "Pyrelands", "in_game", steward="the cycle read", owner="OWNER:%d" % t_mid),
                "exit_met", "his event newer than the cycle's opening but older than its evidence")
        real_bf = M.blind_facts
        M.blind_facts = lambda *a, **k: (_ for _ in ()).throw(AttributeError("'NoneType' object has no attribute 'get'"))
        try:
            e = M.evaluate(root, "Pyrelands", "in_game", steward="the cycle read")
        except Exception as x:  # noqa: BLE001
            e = {"verdict": {"refusals": [{"clause": "raised %r" % x}]}}
        finally:
            M.blind_facts = real_bf
        ok(any(r["clause"] == "exit_met" and "raised" in str(r.get("observed")) for r in e["verdict"]["refusals"]),
           "an exit reader that cannot parse its evidence is a refusal, not a crash and not met")
        ok(M.advance(root, "Pyrelands", "in_game", by="CONDUCTOR", why="x", steward="read the run's verdict: clean",
                     owner="OWNER:4242000000000000003")["ok"],
           "Pyrelands moves to in_game past an unmet exit only on his newer OWNER event")
        # the BUILD MATCH at the Stage 6 exit (owner, 2026-11-17): a check made on another build is re-run
        for brk, what in (("hash", "on another mod hash than his walk's"), ("build", "on another game build"),
                          ("list", "on its tier's mods in another order"), ("none", "with no build identity")):
            write_visit(root, "Pyrelands", 1, off_build=brk)
            refused(M.advance(root, "Pyrelands", "pre_human", by="CONDUCTOR", why="x", steward="read the visit: met"),
                    "build_match", "a check whose last row is %s" % what)
        ex = M.read_ingame_exit(root, "Pyrelands", 1)
        ok(ex["state"] == "not_met" and any("re-run it" in w for w in ex["why"]),
           "the exit reader names the off-build check to re-run (%s)" % (ex["why"] or ["-"])[0][:90])
        refused(M.advance(root, "Pyrelands", "pre_human", by="CONDUCTOR", why="x", steward="read the visit: met"),
                "exit_met", "a steward's word alone on a visit whose exit reads not met")
        write_visit(root, "Pyrelands", 1)
        os.environ[BM.STANDIN_ENV] = os.path.join(root, "no_walk_build.json")
        try:
            refused(M.advance(root, "Pyrelands", "pre_human", by="CONDUCTOR", why="x", steward="read the visit: met"),
                    "build_match", "a walk build that cannot be read counts nothing")
        finally:
            write_visit(root, "Pyrelands", 1)
        ok(M.advance(root, "Pyrelands", "pre_human", by="CONDUCTOR", why="x", steward="read the visit: met")["ok"],
           "Pyrelands moves to pre_human when every check's last row is on the walk build")
        ok(M.load(root, "Pyrelands")["pre_human_arrivals"] == 1, "arrivals at the walk brief are counted")
        # Stage 7 judges nothing: one fresh reader writes the walk brief; it has no veto and needs no steward
        ok("pre_human" not in M.ROADS_BACK, "Stage 7 has no road back (%s)" % M.ROADS_BACK.get("pre_human"))
        refused(M.advance(root, "Pyrelands", "his_walk", by="CONDUCTOR", why="x"), "walk_brief",
                "no walk brief written")
        wb = os.path.join(root, "design", "concepts", "Pyrelands", M.WALK_BRIEF_DIR, "arrival_1.md")
        os.makedirs(os.path.dirname(wb), exist_ok=True)
        body = "".join("## %s\nselftest text under %s\n\n" % (h, h) for h in M.WALK_BRIEF_HEADINGS)
        for text, what in (("written_by: %s\n\n%s" % (ROW_UNIT, body), "a brief by a unit that wrote an in-game row"),
                           ("written_by: fresh-reader-1\n\n%s" % body.replace("selftest text under What I noticed "
                                                                               "first", ""), "a heading left empty"),
                           ("%s" % body, "no written_by line"),
                           ("written_by: fresh-reader-1\n\n%s" % body.split("## What I noticed")[0],
                            "a heading missing")):
            with open(wb, "w") as f:
                f.write(text)
            refused(M.advance(root, "Pyrelands", "his_walk", by="CONDUCTOR", why="x"), "walk_brief", what)
        with open(wb, "w") as f:
            f.write("written_by: fresh-reader-1\n\n%s" % body)
        ok(M.advance(root, "Pyrelands", "his_walk", by="CONDUCTOR", why="walk brief arrival_1 written")["ok"],
           "Pyrelands moves to his_walk on a fresh reader's brief, no --steward-confirms")
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
        # RIMMANDRAKE_BIND_STAGE_EVIDENCE_TO_ONE_BUILD: the pass record names the one build he walked
        standin = os.environ.get(BM.STANDIN_ENV)
        os.environ[BM.STANDIN_ENV] = os.path.join(root, "no_walk_build.json")
        try:
            refused(M.evaluate(root, "Pyrelands", "passed", by="CONDUCTOR", why="x", owner="OWNER:4242000000000000001"),
                    "walk_build", "a pass whose walk build cannot be read (no build identity)")
        finally:
            os.environ[BM.STANDIN_ENV] = standin
        with open(os.path.join(root, "half_walk_build.json"), "w") as f:
            json.dump({"mod_hash": WALK_HASH, "game_build": WALK_GAME_BUILD}, f)
        os.environ[BM.STANDIN_ENV] = os.path.join(root, "half_walk_build.json")
        try:
            refused(M.evaluate(root, "Pyrelands", "passed", by="CONDUCTOR", why="x", owner="OWNER:4242000000000000001"),
                    "walk_build", "a pass whose walk build has no mod list")
        finally:
            os.environ[BM.STANDIN_ENV] = standin
        with open(os.path.join(root, "redeployed_walk_build.json"), "w") as f:
            json.dump(dict(json.load(open(standin)), mod_hash="selftest-redeployed-hash"), f)
        os.environ[BM.STANDIN_ENV] = os.path.join(root, "redeployed_walk_build.json")
        try:
            refused(M.evaluate(root, "Pyrelands", "passed", by="CONDUCTOR", why="x", owner="OWNER:4242000000000000001"),
                    "walk_build", "a pass after a redeploy: the visit's mod_sha and the deployed hash name different builds")
        finally:
            os.environ[BM.STANDIN_ENV] = standin
        real_wb, reads = BM.walk_build, []

        def walk_build_drifts(*a, **kw):
            reads.append(1)
            w = real_wb(*a, **kw)
            return dict(w, mod_hash="selftest-second-read-hash") if len(reads) > 1 else w
        BM.walk_build = walk_build_drifts
        try:
            wid_ = M.walk_identity(root, "Pyrelands", M.load(root, "Pyrelands"))
        finally:
            BM.walk_build = real_wb
        ok(wid_.get("mod_hash") == WALK_HASH and not wid_.get("why"),
           "the identity recorded is the one the build match checked, never a second reading (%s, %d reads)"
           % (wid_.get("mod_hash"), len(reads)))
        twin = root + "_pass"
        shutil.copytree(root, twin)
        real_eval = M.evaluate

        def eval_then_moved(r_, m_, to_, **kw):
            out = real_eval(r_, m_, to_, **kw)
            rc_ = M.load(r_, m_)
            rc_["stage"] = "offline_build"
            M.write_text(r_, m_, M.RECORD, M.dump(rc_))
            return out
        M.evaluate = eval_then_moved
        try:
            r = M.advance(twin, "Pyrelands", "passed", by="CONDUCTOR", why="x", owner="OWNER:4242000000000000001")
        finally:
            M.evaluate = real_eval
        prd_twin = os.path.join(twin, "design", "concepts", "Pyrelands", M.PASS_RECORD_DIR)
        ok(not r["ok"] and M.load(twin, "Pyrelands")["stage"] == "offline_build" and not os.path.isdir(prd_twin),
           "a stage that moved after the evaluation is not moved again, and no pass record is written (%s)"
           % r.get("moved_meanwhile"))
        shutil.rmtree(twin)
        shutil.copytree(root, twin)
        real_commit = M.commit_move

        def commit_after_a_race(r_, m_, rec_, *a, **kw):
            on_disk = M.load(r_, m_)
            on_disk.setdefault("moves", []).append({"from": "his_walk", "to": "his_walk", "by": "selftest-race"})
            M.write_text(r_, m_, M.RECORD, M.dump(on_disk))
            return real_commit(r_, m_, rec_, *a, **kw)
        M.commit_move = commit_after_a_race
        try:
            r = M.advance(twin, "Pyrelands", "passed", by="CONDUCTOR", why="x", owner="OWNER:4242000000000000001")
        finally:
            M.commit_move = real_commit
        ok(not r["ok"] and M.load(twin, "Pyrelands")["stage"] == "his_walk" and not os.path.isdir(prd_twin),
           "a record that changed after the check, before the lock, is not overwritten and gets no pass record (%s)"
           % r.get("moved_meanwhile"))
        shutil.rmtree(twin)
        shutil.copytree(root, twin)
        try:
            ver = M.load(twin, "Pyrelands").get("version")
            visit_build = M.read_ingame_exit(twin, "Pyrelands", 1).get("build")
            M.add_spend(twin, "Pyrelands", "in_game", 1234, source="selftest-ingame-run")
            rc_ = M.load(twin, "Pyrelands")
            rc_["seeded"] = dict(rc_.get("seeded") or {}, at="2026-11-01T00:00:00Z")
            M.write_text(twin, "Pyrelands", M.RECORD, M.dump(rc_))
            rsp = os.path.join(twin, "design", "concepts", "Pyrelands", M.RUN_SPEND)
            os.makedirs(os.path.dirname(rsp), exist_ok=True)
            with open(rsp, "a") as f:
                f.write(json.dumps({"stage": "in_game", "stages": ["in_game"], "tokens": 50, "token_unit": "weighted_v2",
                                    "unit": "rm-old-version-run",
                                    "at": "2026-10-20T00:00:00Z"}) + "\n")
                f.write(json.dumps({"stage": "in_game", "stages": ["in_game"], "tokens": 70, "token_unit": "weighted_v2",
                                    "unit": "rm-this-version-run",
                                    "at": "2026-11-05T00:00:00Z"}) + "\n")
            rows_ = M.spend_rows(twin, "Pyrelands", M.load(twin, "Pyrelands"))
            # weighted_v2 rows only: the live record's older rows are weighted_v1 history, summed apart (row_unit)
            want_tokens = sum(x["tokens"] for x in rows_ if isinstance(x.get("tokens"), (int, float))
                              and x.get("unit") != "rm-old-version-run" and M.row_unit(x) == "weighted_v2")
            # RIMMANDRAKE_TUNE_ADVANCE_REFUSAL_ALARM_BLOCKS_NOTHING_AS_CODED: the advance alarm only tells: an OPEN
            # item alarm on this mod@version blocks no advance
            ap = RC.alarms_path()
            alarms_was = open(ap).read() if os.path.isfile(ap) else None
            os.makedirs(os.path.dirname(ap), exist_ok=True)
            with open(ap, "w") as f:
                json.dump({"item:Pyrelands@%s" % ver: {"id": RC.ALARM_ID, "subject": "item:Pyrelands@%s" % ver,
                                                         "open": True, "why": "selftest: a tripped advance alarm"}}, f)
            r = M.advance(twin, "Pyrelands", "passed", by="CONDUCTOR", why="his walk passed it",
                          owner="OWNER:4242000000000000001")
            ok(r["ok"] and M.load(twin, "Pyrelands")["stage"] == "passed", "the pass moves the record (%s)"
               % [x["clause"] for x in r["verdict"]["refusals"]])
            ok(r["ok"] and not RC.may_judge("Pyrelands@%s" % ver),
               "an open advance alarm on the mod@version (may_judge False) blocks no advance: it only tells")
            if alarms_was is None:
                os.remove(ap)
            else:
                with open(ap, "w") as f:
                    f.write(alarms_was)
            pr = os.path.join(twin, "design", "concepts", "Pyrelands", M.PASS_RECORD_DIR, "%s.json" % ver)
            rec_ = json.load(open(pr)) if os.path.isfile(pr) else {}
            need = ("mod", "version", "passed_on", "commit", "owner_said", "bars", "evidence", "cost", "cycles", "build")
            ok(all(k in rec_ for k in need), "the pass record carries %s (missing %s)"
               % (", ".join(need), [k for k in need if k not in rec_]))
            bd = rec_.get("build") or {}
            ok(bd.get("mod_hash") == WALK_HASH and bd.get("game_build") == WALK_GAME_BUILD
               and bd.get("active_mods") == WALK_LIST and bd.get("mod_sha") and bd.get("mod_sha") == visit_build,
               "the pass record's build is the walk's mod hash, game build and mod list in order, and the visit's one "
               "mod_sha (%s)" % bd)
            ok(rec_.get("version") == ver and rec_.get("owner_said", {}).get("tsn") == "4242000000000000001"
               and "ship it" in str(rec_.get("owner_said", {}).get("words")), "the pass record quotes his event (%s)"
               % rec_.get("owner_said"))
            ok(isinstance(rec_.get("bars"), dict) and (rec_.get("cost") or {}).get("weighted_tokens") == want_tokens
               and want_tokens >= 1234 + 70, "the pass record holds the bars and this version's spend rows' weighted "
               "tokens, the Dispatch run rows included and an earlier version's left out (%s, want %s: %s)"
               % (rec_.get("bars"), want_tokens, rec_.get("cost")))
        finally:
            shutil.rmtree(twin, ignore_errors=True)
        blind = M.pass_cost(root, "Pyrelands", {"spend": [{"stage": "designer", "tokens": M.UNM, "usd": M.UNM}]})
        ok(blind["weighted_tokens"] == M.UNM and blind["tokens_unmeasured"] == 1,
           "spend whose tokens were never measured is UNMEASURED, never 0 (%s)" % blind)
        prd = os.path.join(root, "design", "concepts", "Pyrelands", M.PASS_RECORD_DIR)
        os.makedirs(prd, exist_ok=True)
        with open(os.path.join(prd, "%s.json" % M.load(root, "Pyrelands").get("version")), "w") as f:
            f.write("{}")
        refused(M.evaluate(root, "Pyrelands", "passed", by="CONDUCTOR", why="x", owner="OWNER:4242000000000000001"),
                "pass_record_new", "a version whose pass record already exists (a pass record is never rewritten)")
        shutil.rmtree(prd)
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
        nx = M.gate_step(root, "ExplosiveKnockback")
        ok(nx["stage"] == "offline_build" and nx["next"].startswith("NEXT") and "every_bar_has_a_check_that_runs"
           in json.dumps(nx["refusals"]), "next on Explosive Knockback names the failing exit test")
        nx = M.gate_step(root, "SpineTestMod")
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
            return [r for r in M.gate_step(root, "FlowWorks")["refusals"]
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
        # RIMMANDRAKE_ROUTE_LIVE_ONLY_DECIDER_STAGE_THREE_NO_ROAD: a live decider whose known red's fix is implemented
        # (published) and whose only remainder needs the live game is a check that runs, UNRUN and owed to Stage 6;
        # an unlanded fix, an offline remainder or an offline known red still refuses
        tp = os.path.join(root, "design", "concepts", "FlowWorks", "version", "test_table.json")
        t_was = read(root, "FlowWorks", "version/test_table.json")
        kr, kro = "RIMMANDRAKE_SELFTEST_KNOWN_RED_LIVE_ONLY", "RIMMANDRAKE_SELFTEST_KNOWN_RED_OFFLINE_TEST"
        tk = json.loads(t_was)
        bk, bo = tk["bars"][0]["id"], tk["bars"][1]["id"]
        tk["tests"]["SELFTEST_KR"] = {"id": "SELFTEST_KR", "kind": "live_minimal", "stage": "6", "entry_exists": True,
                                      "known_red": kr, "command": "bridge: selftest.py KR"}
        tk["tests"]["SELFTEST_KR_PASS"] = {"id": "SELFTEST_KR_PASS", "kind": "offline", "stage": "4-5",
                                           "runs_today": {"ran": True, "result": "PASS"}}
        tk["tests"]["SELFTEST_KRO"] = {"id": "SELFTEST_KRO", "kind": "offline", "stage": "4-5", "known_red": kro,
                                       "runs_today": {"ran": True, "result": "FAIL"}}
        for b in tk["bars"]:
            if b["id"] == bk:
                b.update(decides=["SELFTEST_KR", "SELFTEST_KR_PASS"], every_decider_runnable_today=False)
            elif b["id"] == bo:
                b.update(decides=["SELFTEST_KRO"], every_decider_runnable_today=False)
        with open(tp, "w") as f:
            json.dump(tk, f)

        def kr_listed():
            c = owed_refusal()
            return (c[0]["observed"].split("not runnable: ", 1)[-1].split(";")[0].split(", ") if c else []), c
        with open(os.path.join(ev, "BENCH.jsonl"), "a") as f:
            for i in (kr, kro):
                f.write(json.dumps({"seat": "BENCH", "event": "file", "id": i, "needs": "offline", "ts": "1"}) + "\n")
        lst, _ = kr_listed()
        ok(bk in lst and bo in lst, "a known red whose fix has not landed is no check that runs (%s)" % lst[:4])
        with open(os.path.join(ev, "BENCH.jsonl"), "a") as f:
            f.write(json.dumps({"seat": "BENCH", "event": "implemented", "id": kr, "sha": "abcdef123456",
                                "needs": "offline", "ts": "2"}) + "\n")
        lst, _ = kr_listed()
        ok(bk in lst, "a known red implemented with an offline remainder still refuses")
        with open(os.path.join(ev, "BENCH.jsonl"), "a") as f:
            f.write(json.dumps({"seat": "BENCH", "event": "needs", "id": kr, "to": "bridge", "ts": "3"}) + "\n")
            f.write(json.dumps({"seat": "BENCH", "event": "needs", "id": kro, "to": "bridge", "ts": "3"}) + "\n")
        lst, c = kr_listed()
        ok(bk not in lst and kr in json.dumps(c) and "Stage 6" in json.dumps(c),
           "a live decider whose known red is implemented and needs only the game runs, UNRUN and owed to Stage 6 "
           "(%s)" % json.dumps(c)[:240])
        ok(bo in lst, "an OFFLINE known red still refuses, whatever its item's needs")
        with open(os.path.join(ev, "BENCH.jsonl"), "a") as f:
            f.write(json.dumps({"seat": "BENCH", "event": "live", "id": kr, "result": "broken", "ts": "4"}) + "\n")
        lst, _ = kr_listed()
        ok(bk in lst, "a reopen after the known red's implementation refuses again (the fix it rested on died)")
        with open(os.path.join(ev, "BENCH.jsonl"), "a") as f:
            f.write(json.dumps({"seat": "BENCH", "event": "close", "id": kr, "ts": "5"}) + "\n")
        lst, _ = kr_listed()
        ok(bk not in lst, "a closed known red is red no longer: its live decider runs")
        tk["tests"]["SELFTEST_KR"]["entry_exists"] = False
        with open(tp, "w") as f:
            json.dump(tk, f)
        lst, _ = kr_listed()
        ok(bk in lst, "a live known red whose entry does not exist is no check that runs")
        with open(tp, "w") as f:
            f.write(t_was)
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
        os.environ.pop(BM.STANDIN_ENV, None)
        restore(env_was)
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
    import modledger
    modledger.append(root, mod, "DISPATCH", "stage.accepted", "stage", body={"from": "his_walk", "to": "passed",
                     "by": "BENCH"}, version=str(old["version"]), env_writer=None)   # the mod has a ledger at the old version
    r = M.next_version(root, mod, "BENCH", "selftest: the Designer locked 9.9.9")
    rec = M.load(root, mod)
    # RIMMANDRAKE_OPEN_MOD_LEDGER_VERSION_WITH_ITS_NEXT_VERSION: the mod ledger opens the new version with the record;
    # GimmeSomeSlack's ledger read 0.1.0 after next-version opened 0.1.1, so every 0.1.1 event was tagged 0.1.0
    lv = modledger.reduce(modledger.read(root, mod)).get("version")
    ok(lv == "9.9.9", "next-version opens the new version in the mod ledger too (ledger reads %s, want 9.9.9)" % lv)
    kept = read(root, mod, "version/stage_record_%s.json" % old["version"])
    ok(r["ok"] and rec["version"] == "9.9.9" and rec["stage"] == "preflight" and rec["cycles"]["total"] == 0
       and json.loads(kept) == old, "a locked new version: a new record at preflight, the old one kept whole (%s)" % r)
    ok("version change: %s to 9.9.9" % old["version"] in (read(root, mod, "journal.md") or ""),
       "the journal says the version moved")
    # RIMMANDRAKE_SCOPE_RUN_SPEND_TO_VERSION_OLD_RUNS_LINGER: RUN_SPEND outlives next-version and its rows name no
    # version; show and next report only this version's (at on or after seeded.at), and record_run_spend still writes
    # no second row for an old unit
    rsp = os.path.join(root, "design", "concepts", mod, M.RUN_SPEND)
    had = os.path.isfile(rsp)
    keep = open(rsp).read() if had else None
    os.makedirs(os.path.dirname(rsp), exist_ok=True)
    with open(rsp, "a") as f:
        f.write(json.dumps({"stage": "designer", "stages": ["designer"], "tokens": 50, "unit": "rm-old-version-run",
                            "token_unit": "weighted_v2", "at": "2000-01-01T00:00:00Z"}) + "\n")
        f.write(json.dumps({"stage": "designer", "stages": ["designer"], "tokens": 70, "unit": "rm-new-version-run",
                            "token_unit": "weighted_v2", "at": "2999-01-01T00:00:00Z"}) + "\n")
    try:
        rec = M.load(root, mod)
        own = sum(x["tokens"] for x in rec.get("spend") or [] if isinstance(x.get("tokens"), (int, float)))
        nx = M.gate_step(root, mod)["spend"]
        got = sum(t["tokens"] for t in nx.values())
        ok(got == own + 70, "next: this version's spend leaves out the earlier version's run row (%s, want %s)"
           % (got, own + 70))
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            M.main(["--root", root, "show", mod])
        shown = sum(int(x.split("weighted tokens")[0].split(":")[-1]) for x in buf.getvalue().splitlines()
                    if x.strip().startswith("spend ") and "weighted tokens" in x)
        ok(shown == own + 70, "show: the same (%s, want %s)" % (shown, own + 70))
        # the fall-back hour (Codex review): seeded 01:50-07:00, a run ended 20 min later at 01:10-08:00 is this version's
        dst = dict(rec, seeded=dict(rec.get("seeded") or {}, at="2026-11-01T01:50:00-07:00"))
        rows_dst = M.version_spend_rows(root, mod, dict(dst, spend=[]))
        with open(rsp, "a") as f:
            f.write(json.dumps({"stage": "designer", "stages": ["designer"], "tokens": 5, "unit": "rm-dst-run",
                                "at": "2026-11-01T01:10:00-08:00"}) + "\n")
        rows_dst = M.version_spend_rows(root, mod, dict(dst, spend=[]))
        ok(any(x.get("unit") == "rm-dst-run" for x in rows_dst) and not any(
            x.get("unit") == "rm-old-version-run" for x in rows_dst),
           "times compare as instants, never as strings: a run 20 min after the seed across the DST fall-back counts")
        new = M.record_run_spend(root, mod, [{"unit": "rm-old-version-run", "end": 946684800.0, "live": False}],
                                 lambda r: ["designer"])
        ok(new == [], "record_run_spend writes no second row for an old version's unit (%s)" % new)
    finally:
        if had:
            with open(rsp, "w") as f:
                f.write(keep)
        else:
            os.remove(rsp)
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
            # RIMMANDRAKE_PIN_BARS_MD_WHEN_PIPELINE_LOCKS_A_MOD: the first record also pins the locked files in bars.md
            bp = os.path.join(c, "bars.md")
            if os.path.exists(bp):
                os.remove(bp)
            blobs = {"design/concepts/%s/tree.json" % mod: "a" * 40, "design/concepts/%s/scenes.json" % mod: "b" * 40}
            blob = lambda commit, path: blobs.get(path) if commit == "c0ffee" else None     # noqa: E731
            try:
                r = lb(root, mod, "BENCH", "selftest", show=show, blob=blob)
            except TypeError:
                r = lb(root, mod, "BENCH", "selftest", show=show)
            ok(r["ok"] and r["ids"] == ids, "lock-bars derives the locked bars: required_ids at locked_from_commit, less "
               "the moved, plus the added after lock (%s)" % r["why"][:80])
            bm = open(bp).read() if os.path.exists(bp) else ""
            ok("| `design/concepts/%s/tree.json` | `%s` |" % (mod, "a" * 40) in bm and "`c0ffee`" in bm
               and "sheet.md" not in bm, "the first lock-bars pins each locked file that exists at locked_from_commit "
               "in version/bars.md (a pipeline lock had no pins)")
            # RIMMANDRAKE_PIN_BARS_MD_AT_EACH_VERSION_LOCK_NOT_ONLY_FIRST: a next version's lock finds the earlier
            # version's bars.md; its pins are of an earlier lock commit, so they are set aside and the file re-pinned
            old = ("# %s 0.0.9: the bars, locked as they stood on 2026-11-01\n\nLock commit: `deadbeef`.\n\n"
                   "| `design/concepts/%s/tree.json` | `%s` | the leaves |\n" % (mod, mod, "c" * 40))
            with open(bp, "w") as f:
                f.write(old)
            pv = os.path.join(c, "previous", "0.0.9", "bars.md")
            M.pin_bars_md(root, mod, v, ids, blob)
            bm = open(bp).read()
            ok("`c0ffee`" in bm and "| `design/concepts/%s/tree.json` | `%s` |" % (mod, "a" * 40) in bm
               and "c" * 40 not in bm and os.path.exists(pv) and open(pv).read() == old,
               "a next version's lock re-pins bars.md at its own lock commit and keeps the earlier file as "
               "previous/<its version>/bars.md (the earlier pins never pass for this version's)")
            M.pin_bars_md(root, mod, v, ids, lambda commit, path: "d" * 40)
            ok("d" * 40 not in open(bp).read(), "a bars.md already pinned at this lock commit is never rewritten")
            shutil.rmtree(os.path.join(c, "previous", "0.0.9"), ignore_errors=True)
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
    env_was.update(isolate(root))
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
    certify_fixture(root, FOUR)


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
    env_was.update(isolate(root))
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
        nx = M.gate_step(root, "GimmeSomeSlack")
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
        nx = M.gate_step(root, "FlowWorks")
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
        # RIMMANDRAKE_READ_TESTS_EDITED_KEY_JUDGE_NAMED_ITS_OWN: the brief names no shape, and a judge wrote
        # {"tests_edited": [...]} (EK cycle 6); a fault of form is read, never a refusal; its paths count as edited
        write_cycle(root, "FlowWorks", 1, edited_text=json.dumps({"tests_edited": [{"path": "tests/t1.py"}]}))
        ex = M.blind_facts(root, "FlowWorks").get("exit") or {}
        ok(ex.get("state") == "met" and M._edited_paths({"tests_edited": [{"path": "a.py"}]}) == {"a.py"},
           "tests_edited.json as {\"tests_edited\": [...]} reads met and its paths count (%s)" % ex.get("why"))
        # RIMMANDRAKE_PASS_BLIND_EXIT_ZERO_OFFLINE_BARS_GRAFFITI_STUCK: a locked table whose every bar proves live (Graffiti
        # 0.1.0, 47 of 47 at stage 6) has no offline bar to be green; a clean record meets the exit on its Problems alone
        ttp = os.path.join(root, "design/concepts/FlowWorks/version/test_table.json")
        tt_saved = open(ttp).read()
        tt0 = json.loads(tt_saved)
        for b in tt0["bars"]:
            b["proves_at"] = "6"
        with open(ttp, "w") as f:
            json.dump(tt0, f)
        write_cycle(root, "FlowWorks", 1)
        ex = M.blind_facts(root, "FlowWorks").get("exit") or {}
        ok(ex.get("state") == "met" and ex.get("checks", {}).get("offline_bars") == 0,
           "a table with no offline bar: a clean record reads met, and the reading counts 0 offline bars (%s)"
           % ex.get("why"))
        write_cycle(root, "FlowWorks", 1, pending_problem=True)
        ex = M.blind_facts(root, "FlowWorks").get("exit") or {}
        ok(ex.get("state") == "not_met" and "RIMMANDRAKE_LEAVE_SELFTEST_PROBLEM_OPEN" in " ".join(ex.get("why") or []),
           "a table with no offline bar: an open Problem still reads not met (%s)" % (ex.get("why") or ["-"])[0][:90])
        with open(ttp, "w") as f:
            f.write(tt_saved)
        # a fix shown as a list of runs (Pyrelands cycle 1 wrote it so); a lane-1 FAIL cleared by lane 1 after the fixes
        runs = dict(red=[{"cmd": "a", "rc": 1}, {"cmd": "b", "rc": 1}], green=[{"cmd": "a", "rc": 0}, {"cmd": "b", "rc": 0}])
        # a cycle whose mod Problems were FIXED owes one fresh reader of each fix, never a new blind cycle (owner,
        # 2026-11-20: "I agree with your blind judge -> fresh reader argument."); not met until the reader reads
        for kw, what in ((dict(fix_runs=runs), "a FIXED Problem shown red then green as lists of runs"),
                         (dict(fixed=True), "a FIXED Problem shown red then green")):
            write_cycle(root, "FlowWorks", 1, **kw)
            g = M.blind_facts(root, "FlowWorks")
            ex = g.get("exit") or {}
            ok(ex.get("state") == "not_met" and ex.get("checks", {}).get("fix_reader_owed")
               and "one fresh reader is owed" in " ".join(ex.get("why") or []) and g.get("owed") == "exit not met",
               "%s: one fresh reader of the fix is owed, not met (%s)" % (what, (ex.get("why") or ["-"])[0][:100]))
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
        nx = M.gate_step(root, "FlowWorks")
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
        nx = M.gate_step(root, "FlowWorks")
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

FAKE_DEPLOY = """#!/usr/bin/env python3
import os, sys
with open(os.environ["FAKE_DEPLOY_LOG"], "a") as f:
    f.write(" ".join(sys.argv[1:]) + "\\n")
v = os.environ.get("FAKE_DEPLOY", "SYNC")
if v == "SYNC":
    print("GimmeSomeSlack   mandrake.rm.gimmesomeslack\\n\\nEverything in sync.")
elif v == "DRIFT":
    print("GimmeSomeSlack   mandrake.rm.gimmesomeslack\\n    ~  Assemblies/RimMandrakeGimmeSomeSlack.dll\\n"
          "    ~  Assemblies/RimMandrakeGimmeSomeSlack.dll.srchash\\n\\nDrift found. Re-run with --apply to deploy.")
    sys.exit(1)
else:
    sys.exit("deploy_custom_mods.py: no such mod in the repo: Pyrelands")
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
    certify_fixture(root, [as_mod or mod])


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


# the build he walks, as build_match.py's stand-in (MATURATION_WALK_BUILD) gives it: never this machine's game
WALK_HASH, WALK_GAME_BUILD = "selftest-walk-hash", "1.6.4871 rev590"
WALK_LIST = ["Ludeon.RimWorld", "mandrake.rm.pyrelands", "selftest.other.mod"]
TIER_LIST = ["Ludeon.RimWorld", "mandrake.rm.pyrelands"]
ROW_UNIT = "selftest-ingame-runner"


def walk_standin(root, tt):
    """Write the walk-build stand-in for this tree and point build_match.py at it."""
    tiers = {t: TIER_LIST for t in {"minimal"} | {x.get("tier") for x in tt["tests"].values() if x.get("tier")}}
    p = os.path.join(root, "walk_build.json")
    with open(p, "w") as f:
        json.dump({"mod_hash": WALK_HASH, "game_build": WALK_GAME_BUILD, "active_mods": WALK_LIST, "tiers": tiers}, f)
    os.environ[BM.STANDIN_ENV] = p


def identity(spec, broken=None):
    """The fields `build_match.py identity` prints for one row, one of them broken on request."""
    if spec.get("why_full_list"):
        out = {"full_list": True, "active_mods": list(WALK_LIST)}
    else:
        out = {"tier": spec.get("tier") or "minimal", "active_mods": list(TIER_LIST)}
    out.update(mod_hash=WALK_HASH, game_build=WALK_GAME_BUILD, unit=ROW_UNIT)
    if broken == "hash":
        out["mod_hash"] = "a-build-before-a-redeploy"
    elif broken == "build":
        out["game_build"] = "1.5.4409 rev1118"
    elif broken == "list":
        out["active_mods"] = list(reversed(out["active_mods"]))
    elif broken == "none":
        out = {}
    return out


def write_visit(root, mod, n, exit_met=True, drop=None, fail=None, rerun_pass=False, site=True, game="archmagi",
                sha="abc1234", strange=None, strange_open=None, strange_file=True, save=True, rows_file=True,
                block=True, sha2=None, save_text="<?xml version=\"1.0\"?>\n<savegame><meta/></savegame>",
                site_reading={"biome": "Pyrelands", "colonists_alive": 3}, off_build=None, off_build_all=False,
                earlier=None):
    """A visit record in the layout maturation.py reads, every file present, with one thing broken on request.
    off_build: "hash"/"build"/"list"/"none" breaks the last check's build identity (every check's with off_build_all).
    earlier: (test, verdict, class) writes one earlier row of that check before its own row."""
    tt = json.load(open(os.path.join(root, "design", "concepts", mod, "version", "test_table.json")))
    walk_standin(root, tt)
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
                row.update(identity(tt["tests"][t], off_build if (off_build_all or t == ids[-1]) else None))
                if earlier and t == earlier[0]:
                    f.write(json.dumps(dict({k: v for k, v in row.items() if v is not None}, verdict=earlier[1],
                                            **({"class": earlier[2]} if earlier[2] else {}))) + "\n")
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
            "MATURATION_BRIDGE_IDLE", "FAKE_IDLE", "FAKE_IDLE_LOG", BM.STANDIN_ENV, M.COMPANION_ENV,
            "MATURATION_DEPLOY_PLAN", "FAKE_DEPLOY", "FAKE_DEPLOY_LOG")
    env_was = {k: os.environ.get(k) for k in keys}
    env_was.update(isolate(root))
    try:
        copy_ingame(root)
        sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "bridgetools"))
        import companion_identity as CI
        want = CI.srchash_at(REPO, "HEAD")
        fresh_dll = CI.write_fixture(os.path.join(root, "companion", "fresh", CI.DLL_NAME), want)
        stale_dll = CI.write_fixture(os.path.join(root, "companion", "stale", CI.DLL_NAME), "0" * 64)
        os.environ[M.COMPANION_ENV] = fresh_dll
        dep, dlog = os.path.join(root, "fake_deploy.py"), os.path.join(root, "fake_deploy.log")
        with open(dep, "w") as f:
            f.write(FAKE_DEPLOY)
        open(dlog, "w").close()
        os.environ.update({"MATURATION_DEPLOY_PLAN": "%s %s" % (sys.executable, dep), "FAKE_DEPLOY_LOG": dlog,
                           "FAKE_DEPLOY": "SYNC"})
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
                     and "version/in_game/visit_1" in nx["next"])(M.gate_step(root, P)),
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
            and "pipeline_admit.py" in text[0] and "Pipeline tests only" not in text[0],
            "the brief says no check names a modcheck chain (no testq block), and cites no 2026-11-14 pipeline-only limit")
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
        chk(lambda: all(w not in text[0] for w in ("supersedes the FAIL", "Do not fix the mod in the sitting"))
            and all(w in " ".join(text[0].split()) for w in (
                "fix it in the sitting", "re-run the checks that the fix touches", "one fresh reader", "road back",
                "a new visit reruns", "the row stays FAIL")),
            "brief and exit reader agree on a FAIL: a mod fault the driver can fix is fixed in the sitting, the checks it "
            "touches re-run on the fixed build, one fresh reader of the fix (owner, 2026-11-20); one it cannot fix stays FAIL, "
            "goes down its road back, a new visit reruns it")
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
        # RIMMANDRAKE_REFUSE_INGAME_VISIT_ON_STALE_COMPANION: a visit never drives an old companion's checks
        free = lambda p, s: (True, "free")  # noqa: E731
        os.environ[M.COMPANION_ENV] = stale_dll
        chk(lambda: (lambda r: r[0] == 2 and "companion" in r[1] and "STALE" in r[1] and "build.py --gm --apply" in r[1]
                     and not calls())(M.launch_mod(root, P, 20, ITEM, bridge=free)),
            "the game folder's companion STALE against HEAD: launch refuses, names it and the rebuild, launches nothing")
        os.environ[M.COMPANION_ENV] = os.path.join(root, "companion", "none", CI.DLL_NAME)
        chk(lambda: (lambda r: r[0] == 2 and "MISSING" in r[1] and not calls())(M.launch_mod(root, P, 20, ITEM,
                                                                                             bridge=free)),
            "no companion in the game folder: launch refuses (MISSING), launches nothing")
        os.environ[M.COMPANION_ENV] = fresh_dll
        chk(lambda: M.companion_current()[0] is True, "a companion stamped with HEAD's companion sources reads current")
        chk(lambda: (lambda r: r[0] == 2 and "stand-in says old" in r[1] and not calls())(
            M.launch_mod(root, P, 20, ITEM, bridge=free, companion=lambda game="a": (False, "stand-in says old"))),
            "a companion stand-in that says not current refuses, with its words")
        # the deployed mod copy matches the repo before a visit plays (2026-11-19: GSS's game DLL and .srchash differed
        # from the repo build, and nothing in code checked)
        os.environ["FAKE_DEPLOY"] = "DRIFT"
        chk(lambda: (lambda r: r[0] == 2 and "Assemblies/RimMandrakeGimmeSomeSlack.dll" in r[1]
                     and "deploy_custom_mods.py --mod %s --apply" % P in r[1] and not calls())(
            M.launch_mod(root, P, 20, ITEM, bridge=free)),
            "the deploy plan finds drift: launch refuses, names the differing files and the deploy command, launches "
            "nothing")
        chk(lambda: open(dlog).read().split("\n")[-2] == "--mod %s" % P,
            "the deploy check runs the plan only (no --apply) for the mod's own folder")
        os.environ["FAKE_DEPLOY"] = "BROKEN"
        chk(lambda: (lambda r: r[0] is False and "could not read" in r[1] and "no such mod" in r[1])(
            M.mod_deployed(root, P)),
            "a deploy plan that cannot run is could-not-look, never in sync, and says why")
        os.environ["FAKE_DEPLOY"] = "SYNC"
        chk(lambda: M.mod_deployed(root, P)[0] is True, "a plan that reads Everything in sync reads deployed")
        chk(lambda: (lambda r: r[0] == 2 and "stand-in says stale" in r[1] and not calls())(
            M.launch_mod(root, P, 20, ITEM, bridge=free, deployed=lambda root_, mod: (False, "stand-in says stale"))),
            "a deploy stand-in that says not current refuses, with its words")
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
                     and nx["launch"].startswith("none") and "steward_confirms" in nx["hand_steps"])(M.gate_step(root, P)),
            "next: exit met is a program reading, the steward confirms the move to pre_human, nothing to launch")
        chk(lambda: M.launch_mod(root, P, 20, ITEM, bridge=lambda p, s: (True, "free"))[0] == 2 and len(calls()) == 1,
            "launch refuses a visit already recorded")
        chk(lambda: reads(dict(fail=live6[1], rerun_pass=True), "not_met", "an earlier row reads FAIL"),
            "a FAIL rerun PASS in the sitting: the later PASS does not hide the FAIL, not met "
            "(RIMMANDRAKE_CLOSE_EXIT_READER_LOOPHOLES)")
        chk(lambda: reads(dict(earlier=(live6[1], "UNMEASURED", None)), "met"),
            "an earlier UNMEASURED row (a harness split: visit 1's sc_four_looks) before a PASS spends nothing: met "
            "(standing_rulings: no trial is spent by a system failure)")
        chk(lambda: reads(dict(earlier=(live6[1], "FAIL", "HARNESS")), "met"),
            "an earlier FAIL row the driver classed HARNESS before a PASS spends nothing: met")
        chk(lambda: reads(dict(earlier=(live6[1], "FAIL", "MOD")), "not_met", "an earlier row reads FAIL"),
            "an earlier FAIL row classed MOD before a PASS still counts: not met")
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
        )
        # his ruling of 2026-11-21 (RIMMANDRAKE_RERUN_ONLY_CHECKS_THE_CHANGE_TOUCHES_NOT_ALL_203) narrows
        # RIMMANDRAKE_BIND_STAGE_EVIDENCE_TO_ONE_BUILD: rows on two builds count when the build match counts each
        chk(lambda: reads(dict(sha2="def5678"), "met"),
            "rows on two builds whose deployed folders equal the walk's: each counts, met (only the checks a change "
            "touches run again)")
        for kw, what, word in broken:
            chk(lambda kw=kw, word=word: reads(kw, "not_met", word), "%s: not met, and the reading says why" % what)
        chk(lambda: reads(dict(block=False), "no_exit_block") and M.ingame_facts(root, P)["owed"] == "no exit block"
            and M.gate_step(root, P)["launch"].startswith("none"),
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


# ---- the refusal contract's count of advance refusals (RIMMANDRAKE_COUNT_ADVANCE_REFUSALS_SO_A_LOOP_RINGS) -----------
#
# Watched failing on the base 84ca416f3a, where `--submit` was not a mode at all: the flag fell through to main() and
# the store directory was never created. Written before maturation.py submitted anything.
FAM = "maturation_advance"          # the brief advance judges with; judge_calibration.json is an exact lookup
ITEM0 = "SpineTestMod@0.1.0"


def rows_in_store():
    p = RC.records_path()
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def item_counts():
    return RC.counters()["items"].get(ITEM0) or {}


def said(res):
    """What the run says about the contract, or why it says nothing (on the base there is no submit_line at all)."""
    f = getattr(M, "submit_line", None)
    return (f(res) or "") if f else "<maturation.py has no submit_line>"


def alarm_rows():
    """-> (the rows of the store's alarms.json, why it could not be read). No file at all is its own answer: it is not
    a store that holds no alarm."""
    if not os.path.exists(RC.alarms_path()):
        return {}, "%s was never written" % RC.alarms_path()
    try:
        with open(RC.alarms_path(), encoding="utf-8") as f:
            return json.load(f), None
    except (OSError, ValueError) as e:
        return {}, "%s: %s" % (type(e).__name__, e)


def reset_spine(root, **kw):
    """Put SpineTestMod back at the Designer with a fresh VERSION.json (harness housekeeping, owner 2026-11-17): the
    item string, and so the contract's count for it, does not change."""
    synthetic(root, **kw)
    p = os.path.join(root, "design", "concepts", "SpineTestMod", M.RECORD)
    if os.path.exists(p):
        os.remove(p)
    M.seed_mod(root, "SpineTestMod", live=False)


def submit_main():
    """Every advance verdict goes through refusal_contract.submit, and a stage refused again and again rings the one
    alarm. Six regimes, each with its own answer: counted / counted repeat (tagged from the counters) / cached (not
    counted) / advisory (stored, not counted) / the store could not be reached (the count is UNREADABLE, not zero) /
    malformed. Doubles as the maturation_advance family's free_check: it writes $RM_CALIBRATION_RESULTS."""
    before = git_status()
    root = tempfile.mkdtemp(prefix="maturation_submit_")
    keys = ISOLATE + ("MATURATION_CLOCK", "RM_JUDGE_CALIBRATION", "RM_CALIBRATION_ROOT")
    was = {k: os.environ.get(k) for k in keys}
    cases, store = [], os.path.join(root, "_refusals")
    try:
        isolate(root)
        os.environ["MATURATION_CLOCK"] = str(CLOCK)
        # the family's own registry, CALIBRATED at a measured brief hash: only a CALIBRATED brief's refusal counts
        with open(os.path.join(root, "brief.md"), "w") as f:
            f.write("the advance gate's brief (fixture for this test)\n")
        cal, h = os.path.join(root, "cal.json"), RC.brief_hash(["brief.md"], root)

        def write_cal(status="CALIBRATED", hash_=None):
            with open(cal, "w") as f:
                json.dump({"families": {FAM: {"brief": ["brief.md"], "hash": hash_ or h, "status": status,
                                              "cases": {}}}}, f)

        write_cal()
        os.environ.update(RM_JUDGE_CALIBRATION=cal, RM_CALIBRATION_ROOT=root)
        copy_mods(root)
        reset_spine(root)       # at the Designer, state "drafting": the `locked` clause is its one refusal

        def try_advance(label, **kw):
            r = M.advance(root, "SpineTestMod", kw.pop("to", "preflight"), by=kw.pop("by", "BENCH"),
                          why=kw.pop("why", "the contract counts this"), **kw)
            return r, (r.get("submit") or {}), label

        # ---- A: the first refusal is submitted, counted, and tagged "first" -------------------------------------
        r, s, _ = try_advance("first")
        refused(r, "locked", "an unlocked version")
        ok(r["verdict"]["family"] == FAM, "the verdict's family is the brief %r, not the move (%r)"
           % (FAM, r["verdict"]["family"]))
        rows = rows_in_store()
        ok(len(rows) == 1 and rows[0]["kind"] == "refusal" and rows[0]["item"] == ITEM0
           and rows[0]["record"]["clause"] == "locked",
           "one submitted refusal row lands in %s (%d row(s): %s)" % (RC.records_path(), len(rows),
                                                                      [x.get("kind") for x in rows]))
        ok(s.get("counted") and s.get("calibration") == "CALIBRATED" and item_counts().get("refused") == 1,
           "the first refusal is counted (counted=%s, calibration=%s, refused=%s of limit %d)"
           % (s.get("counted"), s.get("calibration"), item_counts().get("refused"), RC.ITEM_ALARM_AT))
        ok(r["verdict"]["refusals"][0]["new_since"] == "first",
           "its new_since reads first (%r)" % r["verdict"]["refusals"][0].get("new_since"))
        cases.append({"id": "unlocked_version_refuses", "expect": "refuse", "got": "refuse" if not r["ok"] else "pass"})

        # ---- C: the same refusal again, with nothing changed, is answered from the cache and not counted ---------
        r, s, _ = try_advance("cached", why="nothing has changed")
        ok(not r["ok"] and s.get("cached") == ["locked"] and not s.get("counted")
           and item_counts().get("refused") == 1,
           "an identical re-ask is cached, not counted (cached=%s, counted=%s, refused=%s)"
           % (s.get("cached"), s.get("counted"), item_counts().get("refused")))
        cases.append({"id": "cached_repeat_still_refuses", "expect": "refuse",
                      "got": "refuse" if not r["ok"] else "pass"})

        # ---- B and the repeat limit: each fresh refusal is tagged from the counters, the 3rd and 4th ring -------
        alarms, limit = [], max(RC.CLAUSE_REPAIR_AT, RC.ITEM_ALARM_AT)
        for n in range(2, limit + 1):
            synthetic(root, state="drafting round %d" % n)       # the cited evidence moves: a fresh refusal
            r, s, _ = try_advance("round %d" % n)
            tag = r["verdict"]["refusals"][0].get("new_since")
            ok(not r["ok"] and s.get("counted") and item_counts().get("refused") == n and tag == "unfixed:locked",
               "refusal %d of %d is counted and tagged unfixed:locked (refused=%s, tag=%r)"
               % (n, limit, item_counts().get("refused"), tag))
            if n == RC.CLAUSE_REPAIR_AT:
                ok(s.get("repair_due") == ["locked"], "the %dth refusal of one clause asks for a criteria repair (%s)"
                   % (RC.CLAUSE_REPAIR_AT, s.get("repair_due")))
            alarms += [a for a in s.get("alarms") or []]
        subs = [a.get("subject") for a in alarms]
        ok("item:%s" % ITEM0 in subs, "the alarm rises on the item at the repeat limit (%s)" % subs)
        ok(all(a.get("id") == RC.ALARM_ID for a in alarms) and any("%d refused verdicts" % RC.ITEM_ALARM_AT
                                                                   in str(a.get("why")) for a in alarms),
           "it is %s, and says the count that raised it (%s)" % (RC.ALARM_ID, [a.get("why") for a in alarms][-1:]))
        saved, unread = alarm_rows()
        row = saved.get("item:%s" % ITEM0) or {}
        ok(row.get("open") and row.get("id") == RC.ALARM_ID and row.get("family") == FAM,
           "the alarm row stands open in %s (%s)" % (RC.alarms_path(), unread or {k: row.get(k) for k in
                                                                                  ("id", "open", "trips")}))
        tp = os.path.join(root, "_ops", "told.jsonl")
        told = [x for x in open(tp, encoding="utf-8") if RC.ALARM_ID in x] if os.path.exists(tp) else []
        ok(len(told) >= 1, "the Conductor is told of the fresh trip (%s)"
           % ("%d told row(s)" % len(told) if os.path.exists(tp) else "%s was never written" % tp))
        ok(not RC.may_judge(ITEM0), "with the alarm open the item may not be judged again")

        # ---- a clause refused for the first time after earlier refusals is a regression, not an unfixed gap -----
        tag = getattr(M, "tag_new_since", None)
        v = {"item": ITEM0, "refusals": [{"clause": "hold"}, {"clause": "locked"}]}
        prior = tag(v) if tag else None
        ok(prior == RC.ITEM_ALARM_AT, "tag_new_since reads the item's prior count from the counters (%s)"
           % (prior if tag else "maturation.py has no tag_new_since"))
        ok(tag and [r["new_since"] for r in v["refusals"]] == ["regression:hold", "unfixed:locked"],
           "a clause not refused before is a regression, one refused before is unfixed (%s)"
           % ([r.get("new_since") for r in v["refusals"]] if tag else "no tag_new_since"))

        # ---- D: an uncalibrated brief's refusal is stored and shown, never counted ------------------------------
        write_cal(status="UNTESTED")
        synthetic(root, state="drafting advisory")
        n_before = len(rows_in_store())
        r, s, _ = try_advance("advisory")
        ok(not r["ok"] and not s.get("counted") and s.get("advisory") and s.get("calibration") == "UNTESTED"
           and item_counts().get("refused") == RC.ITEM_ALARM_AT and len(rows_in_store()) == n_before + 1,
           "an UNTESTED brief's refusal is stored but not counted (counted=%s, refused=%s, rows %d->%d)"
           % (s.get("counted"), item_counts().get("refused"), n_before, len(rows_in_store())))
        ok("NOT COUNTED" in said(r), "and the run says so: %r" % said(r))
        write_cal()
        # a brief whose files moved since it was calibrated is UNTESTED again, by the hash alone
        write_cal(status="CALIBRATED", hash_="0" * 16)
        ok(RC.status(FAM) == "UNTESTED", "an edited brief is UNTESTED until it is calibrated again (%s)"
           % RC.status(FAM))
        write_cal()

        # ---- F: a malformed verdict (a gate bug) is stored as malformed, counted against nothing, and exits 3 ---
        orig, n_before = M.evaluate, len(rows_in_store())
        try:
            def broken(*a, **k):
                res = orig(*a, **k)
                for rec in res["verdict"]["refusals"]:
                    rec["would_pass"] = "yes"        # says nothing checkable
                return res

            M.evaluate = broken
            synthetic(root, state="drafting malformed")
            r, s, _ = try_advance("malformed")
            bad = [x for x in rows_in_store() if x.get("kind") == "malformed"]
            ok(not r["ok"] and r.get("malformed") and len(bad) == 1 and not s.get("counted")
               and item_counts().get("refused") == RC.ITEM_ALARM_AT,
               "a malformed verdict is stored as malformed and counted against nothing (%s)"
               % (r.get("malformed") or [])[:1])
            rc = M.main(["--root", root, "advance", "SpineTestMod", "--to", "preflight", "--by", "BENCH", "--why", "x"])
            ok(rc == 3, "the command line answers a malformed verdict with exit 3 (got %s)" % rc)
        finally:
            M.evaluate = orig

        # ---- E: the store could not be reached. The count is unreadable, which is not a count of zero -----------
        rec_was = read(root, "SpineTestMod", M.RECORD)
        synthetic(root, state="drafting unreachable")
        os.makedirs(store, exist_ok=True)       # on a build that never submits, the store does not exist yet
        cpath = os.path.join(store, "counters.json")
        # the counters are put back afterwards, not deleted: a deleted count IS zero, and this case is about a count
        # that cannot be read while the four refusals already counted still stand
        cwas = open(cpath, encoding="utf-8").read() if os.path.exists(cpath) else None
        with open(cpath, "w") as f:
            f.write("this is not JSON\n")
        r, s, _ = try_advance("corrupt counters")
        line = said(r)
        ok(not r["ok"] and r.get("submit") is None and "counters could not be read" in (r.get("submit_error") or ""),
           "corrupt counters: nothing is submitted, and the reason is said (%r)" % r.get("submit_error"))
        ok("UNREADABLE, not zero" in line, "it is told apart from a count of zero: %r" % line)
        ok(read(root, "SpineTestMod", M.RECORD) == rec_was, "and the refused move still writes nothing")
        rc = M.main(["--root", root, "advance", "SpineTestMod", "--to", "preflight", "--by", "BENCH", "--why", "x"])
        ok(rc == 4, "the command line answers an uncountable refusal with exit 4, not the plain 1 (got %s)" % rc)
        if cwas is None:
            os.remove(cpath)
        else:
            with open(cpath, "w") as f:
                f.write(cwas)

        ro = os.path.join(root, "_readonly")
        os.makedirs(ro)
        os.chmod(ro, 0o500)
        try:
            os.environ["RM_REFUSAL_DIR"] = ro
            r, s, _ = try_advance("unwritable store")
            ok(not r["ok"] and r.get("submit") is None and "could not be" in (r.get("submit_error") or "")
               and "UNREADABLE, not zero" in said(r),
               "an unwritable store is not reported as submitted (%r, said %r)" % (r.get("submit_error"), said(r)))
            # the pass path: the move is the mod's, not the contract's, so it stands - said out loud, exit 0
            reset_spine(root, state="locked", locked_by="owner")
            rc = M.main(["--root", root, "advance", "SpineTestMod", "--to", "preflight", "--by", "BENCH",
                         "--why", "locked on his word"])
            moved = M.load(root, "SpineTestMod")["stage"] == "preflight"
            ok(rc == 0 and moved, "a passing move whose count cannot be written still stands, exit 0 (rc=%s, %s)"
               % (rc, M.load(root, "SpineTestMod")["stage"]))
        finally:
            os.chmod(ro, 0o700)
            os.environ["RM_REFUSAL_DIR"] = store

        # ---- the pass path, counted: a pass row keeps the family's history from being all-refused ---------------
        reset_spine(root, state="locked", locked_by="owner")
        fam_before = len(RC.counters()["families"].get(FAM) or [])
        r, s, _ = try_advance("pass", why="locked on his word")
        ok(r["ok"] and s.get("counted") and item_counts().get("refused") == RC.ITEM_ALARM_AT,
           "a good move is counted as a verdict, not as a refusal (counted=%s, refused=%s)"
           % (s.get("counted"), item_counts().get("refused")))
        kept = [x for x in rows_in_store() if x.get("kind") == "pass"]
        ok(len(kept) == 1 and kept[0]["item"] == ITEM0, "the passing verdict is stored whole (%d pass row(s))"
           % len(kept))
        hist = RC.counters()["families"].get(FAM) or []
        ok(len(hist) == fam_before + 1 and hist[-1]["refused"] is False,
           "the family's history carries the pass, so an all-refused window is a reading, not a certainty (%s)"
           % [x["refused"] for x in hist[-3:]])
        cases.append({"id": "locked_version_passes", "expect": "pass", "got": "pass" if r["ok"] else "refuse"})
    finally:
        restore(was)
        shutil.rmtree(root, ignore_errors=True)
    res_path = os.environ.get(RC.RESULTS_ENV)
    if res_path:        # this mode is the family's free_check: its planted cases, both ways
        with open(res_path, "w", encoding="utf-8") as f:
            json.dump({"cases": cases}, f)
    ok(git_status() == before, "nothing under design/concepts in the repo was written")
    print("%d failed" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


MODES = ("--ingame", "--blind", "--launch", "--submit")


def every_mode():
    """The door runs a test file with no arguments (pipeline_tests.json), so the bare run is EVERY mode, each in its own
    process: a fault in one reader alone must turn the door red (RIMMANDRAKE_RUN_SELFTEST_MODES_AT_THE_DOOR).
    -> 0 only if the default run and every mode passed; a mode that did not run to a verdict is a failure, never silence."""
    rc = main()
    for m in MODES:
        r = subprocess.run([sys.executable, os.path.abspath(__file__), m], capture_output=True, text=True, timeout=600)
        tail = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
        print("mode %s: exit %d, %s" % (m, r.returncode, tail))
        if r.returncode != 0:
            print(r.stdout[-1500:] + r.stderr[-500:])
            rc = 1
    return rc


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(launch_main() if "--launch" in a else blind_main() if "--blind" in a else ingame_main() if "--ingame" in a
             else submit_main() if "--submit" in a else main() if "--default" in a else every_mode())
