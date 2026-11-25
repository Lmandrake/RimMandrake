#!/usr/bin/env python3
# selftest-timeout: 1800   (six harness builds of ~1-3 min each through winbuild: a hang guard, set far above a real run)
"""Selftest: the order through the giver, the motive and the force record of BRIDGE v2.0 (JawaBenchForceCore.cs, the pure half;
the Verse half JawaBenchForce.cs). Item RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER.
Page: design/specs/2026-11-23-bridge-v2/boundary.md §THE ORDER THROUGH THE GIVER, THE MOTIVE, THE FORCE RECORD; one test per
promise there, 4 checks:

  1 an order declared through the giver that the giver refuses returns given=False with the giver's reason, and starts no job
  2 the force level written to the record is the level that was used, not the level that was asked
  3 a motive for a pawn with no lord is refused by name
  4 a raw job is recorded as raw

Each check also reads the Verse half for the calls that make the rule true in the game (a rule of the core that no tool calls
proves nothing). Each plant breaks one rule of a COPY of the core and must turn its named check red; the first plant is the wrong
code that GPT named: an executor that always starts a raw job and copies the declared level onto the record.
An offline test proves the rules, never the game: prove_ordered_rescue.py compares the record with the job tap live.
No game, no bridge. Without dotnet.exe it FAILS as UNMEASURED.
Run: python3 src/RimMandrake/bridgetools/selftest_scene_force.py [--no-plants]"""
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

CS = os.path.join(HERE, "JawaBench.BridgeTools")
CORE = "JawaBenchForceCore.cs"
PROJ = os.path.join(HERE, "ForceSelfTest", "ForceSelfTest.csproj")
N_UNITS = 4                     # fewer printed = the harness did not run whole


class Unmeasured(Exception):
    pass


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def units(core_text):
    """Build the harness with this core, run it -> {unit: "ok" | "FAIL why"}."""
    import winbuild
    d = tempfile.mkdtemp(prefix="ForceCore_", dir=winbuild.BUILD_ROOT)
    log = os.path.join(winbuild.BUILD_ROOT, "selftest_scene_force.log")
    try:
        with open(os.path.join(d, CORE), "w", encoding="utf-8") as f:
            f.write(core_text)
        with open(log, "w") as lf:
            sys.stdout.flush()
            saved = os.dup(1)
            os.dup2(lf.fileno(), 1)
            try:
                rc, rec = winbuild.stage_build(PROJ, stage_name="ForceSelfTest", extra=("-p:CoreDir=" + winbuild.win(d) + "\\",))
            finally:
                sys.stdout.flush()
                os.dup2(saved, 1)
                os.close(saved)
    except (OSError, SystemExit) as e:
        raise Unmeasured("the harness could not be built: %s" % e)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    if rc:
        raise Unmeasured("the harness build failed (rc %s), log %s" % (rc, log))
    dll = winbuild.staged_win(rec, os.path.dirname(PROJ)) + "\\bin\\Release\\net8.0\\ForceSelfTest.dll"
    # timeout: a hang guard (a harness run takes about 1 s), set far above a real run
    pr = winbuild.run_interop_captured([winbuild.dotnet_exe(), dll], capture_output=True, text=True, cwd="/mnt/d", timeout=180)
    out = {}
    for ln in pr.stdout.splitlines():
        if ln.startswith("U ") and not ln.startswith("U-count"):
            name, _, rest = ln[2:].strip().partition(" ")
            out[name] = rest
    if "U-count %d" % N_UNITS not in pr.stdout or len(out) != N_UNITS:
        raise Unmeasured("the harness printed %d units, want %d: %s %s" % (len(out), N_UNITS, pr.stdout[-300:], pr.stderr[-400:]))
    return out


_CLEAN = [None]


def unit(name):
    if _CLEAN[0] is None:
        _CLEAN[0] = units(read(os.path.join(CS, CORE)))
    return _CLEAN[0].get(name, "FAIL did not run")


def code(path):
    """The C# of a file with its comments and its strings blanked: what is wired, not what is described."""
    s = re.sub(r'@"(?:[^"]|"")*"|"(?:\\.|[^"\\\n])*"', '""', read(path))
    return re.sub(r"\s+", " ", re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", s, flags=re.S)))


def wired(path, *needles):
    """None when the file holds each of these calls, else what is missing."""
    s = code(os.path.join(CS, path))
    for n in needles:
        if n not in s:
            return "FAIL %s does not hold: %s" % (path, n)
    return None


def both(*vals):
    bad = [v for v in vals if v != "ok" and v is not None]
    return "ok" if not bad else "; ".join(bad)


# ------------------------------------------------------------------------------------------------ the 4 checks
def t_a_refused_giver_order_returns_the_reason_and_starts_nothing():
    return both(wired("JawaBenchForce.cs", "FC.Order(req, TheForceHost, ForceLog, JawaBenchHands.SessionId)",
                      "GetOption.Invoke(_provider, new object[] { p, wgd, t, fctx })", "if (opt.Disabled || opt.action == null) return No(via,",
                      "node.TryIssueJobPackage(p, default(JobIssueParams))"),
                unit("a_refused_giver_order_returns_the_reason_and_starts_nothing"))


def t_the_force_level_recorded_is_the_level_used():
    return both(wired("JawaBenchForce.cs", "opt.action();", "p.jobs.StartJob(res.Job, JobCondition.InterruptForced, res.SourceNode,",
                      "return JawaBenchHands.SessionRecord(rec, fields);"),
                # a float-menu work order starts from the job queue: the tap names its work giver, not ThinkNode_QueuedJob
                # (live/ordered_rescue/prove_base_577381c7_2026-11-25.txt: R4 red on the line that named the queue's node)
                wired("JawaBenchCast.cs", "if (j != null && j.workGiverDef != null && (giver == null || giver is ThinkNode_QueuedJob || fromQueue)) return \"\" + j.workGiverDef.defName;"),
                wired("JawaBenchHands.cs", "Core.Record(\"\", rec, fields)", "JawaBenchTerrainTools.ForceSummary("),
                unit("the_force_level_recorded_is_the_level_used"))


def t_a_motive_for_a_pawn_with_no_lord_is_refused_by_name():
    return both(wired("JawaBenchForce.cs", "FC.SetMotive(req, TheForceHost, ForceLog, JawaBenchHands.SessionId)",
                      "GetMethod(\"\", BindingFlags.Public | BindingFlags.Static)", "setJob.Invoke(null, new object[] { JawaBenchHands.InlineCtx, CancellationToken.None, idx, lord.loadID, m.LordJob, m.Args })", "p.GetLord()"),
                unit("a_motive_for_a_pawn_with_no_lord_is_refused_by_name"))


def t_a_raw_job_is_recorded_as_raw():
    return both(wired("JawaBenchForce.cs", "job.playerForced = true;", "p.jobs.TryTakeOrderedJob(job, JobTag.Misc)"),
                unit("a_raw_job_is_recorded_as_raw"))


CHECKS = [t_a_refused_giver_order_returns_the_reason_and_starts_nothing, t_the_force_level_recorded_is_the_level_used,
          t_a_motive_for_a_pawn_with_no_lord_is_refused_by_name, t_a_raw_job_is_recorded_as_raw]

# ------------------------------------------------------------------------------------------------ plants
PLANTS = [
    ("* an executor that always starts a raw job and copies the declared level onto the record",
     "a_refused_giver_order_returns_the_reason_and_starts_nothing",
     [("            if (lv == Giver)\n            {\n                var g = h.AskGiver(r);", "            if (false)\n            {\n                var g = h.AskGiver(r);"),
      ('var ex = Write(h, log, session, r.Actor, "order", Raw, Raw, "raw"', 'var ex = Write(h, log, session, r.Actor, "order", lv.Value, lv.Value, "raw"')]),
    ("a refused giver order that still starts the job", "a_refused_giver_order_returns_the_reason_and_starts_nothing",
     [("                if (!elseRaw)\n                {\n", "                if (!elseRaw)\n                {\n                    h.StartGiven(r, g);\n")]),
    ("the declared level copied onto the record of a fallback", "the_force_level_recorded_is_the_level_used",
     [('Write(h, log, session, r.Actor, "order", Giver, Raw, "raw"', 'Write(h, log, session, r.Actor, "order", Giver, Giver, "raw"')]),
    ("a motive that skips the lord check", "a_motive_for_a_pawn_with_no_lord_is_refused_by_name",
     [("            if (lord == null)\n", "            if (false)\n")]),
    ("a raw job recorded at the giver's level", "a_raw_job_is_recorded_as_raw",
     [('var ex = Write(h, log, session, r.Actor, "order", Raw, Raw, "raw"', 'var ex = Write(h, log, session, r.Actor, "order", Raw, Giver, "raw"')]),
]


def plants():
    good = True
    src = read(os.path.join(CS, CORE))
    for name, must, subs in PLANTS:
        text = src
        for old, new in subs:
            if text.count(old) != 1:
                print("FAIL plant %r: its text is in %s %d times, want 1: %r" % (name, CORE, text.count(old), old[:70]))
                good = False
            text = text.replace(old, new)
        red = sorted(u for u, v in units(text).items() if v != "ok")
        hit = must in red
        good = good and hit
        print("%s plant %r turns red: %s" % ("ok  " if hit else "FAIL", name, red), flush=True)
    return good


def main(argv):
    bad = 0
    try:
        for t in CHECKS:
            v = t()
            bad += v != "ok"
            print("%s %s%s" % ("ok  " if v == "ok" else "FAIL", t.__name__[2:], "" if v == "ok" else ": " + v), flush=True)
        good = True if "--no-plants" in argv else plants()
    except Unmeasured as e:
        print("FAIL scene force UNMEASURED: %s" % e)
        return 1
    print("scene force: %d of %d checks passed%s" % (len(CHECKS) - bad, len(CHECKS),
                                                    "" if "--no-plants" in argv else "; plants %s" % ("all red" if good else "NOT all red")))
    return 0 if bad == 0 and good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
