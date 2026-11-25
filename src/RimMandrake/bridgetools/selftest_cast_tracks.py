#!/usr/bin/env python3
# selftest-timeout: 1800   (three harness builds of ~3 min each through winbuild, and selftest_bridge_hooks.py with its own C# build)
"""Selftest: the standard cast tracks and the job and reservation taps of BRIDGE v2.0 (JawaBenchCastCore.cs, joined to the
production JawaBenchSceneTickCore.cs; the Verse half JawaBenchCast.cs). Item RIMMANDRAKE_BUILD_CAST_TRACKS_AND_JOB_TAPS_FIRST_FAMILY.
Page: design/specs/2026-11-23-bridge-v2/boundary.md §CAST TRACKS AND JOB TAPS; one test per promise there, 9 checks:

  1 the job tap follows the six hook rules of HOOKS.md (and names the job it replaced)   2 the reservation tap follows them
  3 two job starts in one tick keep their order      4 a record outside any run is dropped and counted
  5 an alias whose object is replaced writes a link  6 a track on a replaced job re-binds
  7 the settle reconciliation catches a death with no kill record
  8 the hook table check passes (selftest_bridge_hooks.py, with its C# units)
  9 the per-tick cost of the tracks is in the result

Each plant breaks one rule of a COPY of the cast core and must turn its named check red (the item's two plants are marked *).
An offline test proves the rules, never that a hook is connected in the game: the tap certificate ticket does that live.
No game, no bridge. Without dotnet.exe it FAILS as UNMEASURED.
Run: python3 src/RimMandrake/bridgetools/selftest_cast_tracks.py [--no-plants]"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))

CS = os.path.join(HERE, "JawaBench.BridgeTools")
CORE = "JawaBenchCastCore.cs"
PROJ = os.path.join(HERE, "CastTracksSelfTest", "CastTracksSelfTest.csproj")
N_UNITS = 9                     # fewer printed = the harness did not run whole


class Unmeasured(Exception):
    pass


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def units(core_text):
    """Build the harness with this cast core, run it -> {unit: "ok" | "FAIL why"}."""
    import winbuild
    d = tempfile.mkdtemp(prefix="CastCore_", dir=winbuild.BUILD_ROOT)
    log = os.path.join(winbuild.BUILD_ROOT, "selftest_cast_tracks.log")
    try:
        with open(os.path.join(d, CORE), "w", encoding="utf-8") as f:
            f.write(core_text)
        with open(log, "w") as lf:
            sys.stdout.flush()
            saved = os.dup(1)
            os.dup2(lf.fileno(), 1)
            try:
                rc, rec = winbuild.stage_build(PROJ, stage_name="CastTracksSelfTest", extra=("-p:CoreDir=" + winbuild.win(d) + "\\",))
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
    dll = winbuild.staged_win(rec, os.path.dirname(PROJ)) + "\\bin\\Release\\net8.0\\CastTracksSelfTest.dll"
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
    """None when the Verse file holds each of these calls, else what is missing: a rule of the core that no hook calls proves nothing."""
    s = code(os.path.join(CS, path))
    for n in needles:
        if n not in s:
            return "FAIL %s does not hold: %s" % (path, n)
    return None


def both(*vals):
    bad = [v for v in vals if v != "ok" and v is not None]
    return "ok" if not bad else "; ".join(bad)


# ------------------------------------------------------------------------------------------------ the 9 checks
def t_the_job_tap_follows_the_six_hook_rules():
    return both(wired("JawaBenchCast.cs", "Tp.GStart.Admit(OnMain(), out __state.S)", "Tp.GStart.Commit(__state.S, __runOriginal)", "Tp.RecordStart(__state,",
                      "Tp.GEnd.Admit(OnMain(), out __state.S)", "Tp.GEnd.Commit(__state.S, __runOriginal)", "Tp.RecordEnd(__state,",
                      "typeof(Pawn_JobTracker), \"\"", "nameof(StartPost)", "nameof(EndPost)"),
                unit("job_tap_follows_the_six_hook_rules"), unit("a_job_start_names_the_job_it_replaced"))


def t_the_reservation_tap_follows_the_six_hook_rules():
    return both(wired("JawaBenchCast.cs", "Tp.GReserve.Admit(OnMain(), out __state.S)", "Tp.GReserve.Commit(__state.S, __runOriginal)",
                      "Tp.RecordReserve(__state,", "typeof(ReservationManager), \"\"", "nameof(ReservePost)"),
                unit("reserve_tap_follows_the_six_hook_rules"))


def t_two_job_starts_in_one_tick_keep_their_order():
    return unit("two_job_starts_in_one_tick_keep_their_order")


def t_a_record_outside_any_run_is_dropped_and_counted():
    return both(wired("JawaBenchCast.cs", "ReferenceEquals(JawaBenchSceneTick.Cur, r)) return -2;", "return r.EmitTap(rec, fields);"),
                unit("a_record_outside_any_run_is_dropped_and_counted"))


def t_an_alias_whose_object_is_replaced_writes_a_link():
    return both(wired("JawaBenchHands.cs", "JawaBenchCast.Join(made, Host.CastPawns(Core.GroupSize));"),
                unit("an_alias_whose_object_is_replaced_writes_a_link"))


def t_a_track_on_a_replaced_job_rebinds():
    return unit("a_track_on_a_replaced_job_rebinds")


def t_the_settle_reconciliation_catches_a_death_with_no_kill_record():
    return both(wired("JawaBenchSituationalTools.cs", "JawaBenchCast.OnKill(__instance, dinfo, exactCulprit);"),
                wired("JawaBenchSceneTickCore.cs", "if (Cast != null) Cast.Reconcile("),
                unit("settle_catches_a_death_with_no_kill_record"))


def t_the_hook_table_check_passes():
    p = subprocess.run([sys.executable, os.path.join(HERE, "selftest_bridge_hooks.py")], capture_output=True, text=True, timeout=1500)
    tail = [ln for ln in p.stdout.splitlines() if ln.startswith(("FAIL", "RESULT", "static audit", "C# units"))]
    if p.returncode == 0 and "RESULT PASS" in p.stdout:
        return "ok"
    if any("UNMEASURED" in ln for ln in tail):
        raise Unmeasured("selftest_bridge_hooks.py: " + " | ".join(tail)[-400:])
    return "FAIL selftest_bridge_hooks.py rc %d: %s" % (p.returncode, " | ".join(tail)[-600:])


def t_the_per_tick_cost_of_the_tracks_is_in_the_result():
    return both(wired("JawaBenchSceneTickCore.cs", "(Cast != null ? "), unit("the_per_tick_cost_of_the_tracks_is_in_the_result"))


CHECKS = [t_the_job_tap_follows_the_six_hook_rules, t_the_reservation_tap_follows_the_six_hook_rules, t_two_job_starts_in_one_tick_keep_their_order,
          t_a_record_outside_any_run_is_dropped_and_counted, t_an_alias_whose_object_is_replaced_writes_a_link, t_a_track_on_a_replaced_job_rebinds,
          t_the_settle_reconciliation_catches_a_death_with_no_kill_record, t_the_hook_table_check_passes,
          t_the_per_tick_cost_of_the_tracks_is_in_the_result]

# ------------------------------------------------------------------------------------------------ plants
PLANTS = [
    ("* a job tap that records the new job only", "a_job_start_names_the_job_it_replaced",
     [(' +\n                                             ",\\"current\\":" + (current ? "true" : "false") + ",\\"prev\\":" + S(st.Prev.Text()) +\n'
       '                                             ",\\"prevEnd\\":" + S(st.Prev.Has ? (st.Suspend ? "Suspended" : prevEnd) : null));',
       ' +\n                                             ",\\"current\\":" + (current ? "true" : "false"));')]),
    ("* an alias that silently moves to a corpse", "an_alias_whose_object_is_replaced_writes_a_link",
     [('                    row(tick, phase, "link", "\\"alias\\":" + S(m.Alias) + ",\\"from\\":" + m.Thing + ",\\"to\\":" + next + ",\\"why\\":" + S(why ?? ""));\n'
       '                    Rows++; Links++;\n', '')]),
    ("a toil track that does not re-bind", "a_track_on_a_replaced_job_rebinds",
     [("bool jobMoved = m.Has &&", "bool jobMoved = false && m.Has &&")]),
    ("a death taken as reconciled without its kill record", "settle_catches_a_death_with_no_kill_record",
     [("if (!m.DeadSeen || m.DeadAtFirst) continue;", "continue;")]),
    ("a record outside the run counted as written", "a_record_outside_any_run_is_dropped_and_counted",
     [("if (seq == -2) Outside++;\n", "if (seq == -2) Records++;\n")]),
    ("an entry ordinal taken at the postfix", "two_job_starts_in_one_tick_keep_their_order",
     [('Record(st, pawn, "job_start", ', 'st.Ord = ++_ord; Record(st, pawn, "job_start", ')]),
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
        print("FAIL cast tracks UNMEASURED: %s" % e)
        return 1
    print("cast tracks: %d of %d checks passed%s" % (len(CHECKS) - bad, len(CHECKS),
                                                    "" if "--no-plants" in argv else "; plants %s" % ("all red" if good else "NOT all red")))
    return 0 if bad == 0 and good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
