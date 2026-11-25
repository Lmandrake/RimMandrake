#!/usr/bin/env python3
"""Selftest: the scene run stepped at the end of each tick (JawaBenchSceneTickCore.cs). Page:
design/specs/2026-11-23-bridge-v2/boundary.md; one test per promise, 11 checks. Each plant breaks one rule of a copy of the
core and must turn its named check red (the ticket's plants are marked *). No game, no bridge. Without dotnet.exe it FAILS as
UNMEASURED.
Run: python3 src/RimMandrake/bridgetools/selftest_scene_tick_wiring.py [--no-plants]"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
CORE = os.path.join(HERE, "JawaBench.BridgeTools", "JawaBenchSceneTickCore.cs")
VITALS = os.path.join(HERE, "JawaBench.BridgeTools", "JawaBenchVitals.cs")
PROJ = os.path.join(HERE, "SceneTickSelfTest", "SceneTickSelfTest.csproj")


N_UNITS = 11                    # one per promise; fewer printed = the harness did not run whole


class Unmeasured(Exception):
    pass


def units(text, *args):
    """Build the harness with this core text, run it -> {unit: "ok" | "FAIL why"}. args: `session` = each run in a session."""
    import winbuild
    fd, p = tempfile.mkstemp(prefix="SceneTickCore_", suffix=".cs", dir=winbuild.BUILD_ROOT)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    log = os.path.join(winbuild.BUILD_ROOT, "selftest_scene_tick_wiring.log")
    try:
        with open(log, "w") as lf:
            sys.stdout.flush()
            saved = os.dup(1)
            os.dup2(lf.fileno(), 1)
            try:
                rc, rec = winbuild.stage_build(PROJ, stage_name="SceneTickSelfTest", extra=("-p:CoreFile=" + winbuild.win(p),))
            finally:
                sys.stdout.flush()
                os.dup2(saved, 1)
                os.close(saved)
    except (OSError, SystemExit) as e:
        raise Unmeasured("the harness could not be built: %s" % e)
    finally:
        os.unlink(p)
    if rc:
        raise Unmeasured("the harness build failed (rc %s), log %s" % (rc, log))
    dll = winbuild.staged_win(rec, os.path.dirname(PROJ)) + "\\bin\\Release\\net8.0\\SceneTickSelfTest.dll"
    pr = winbuild.run_interop_captured([winbuild.dotnet_exe(), dll] + list(args), capture_output=True, text=True, cwd="/mnt/d/Luke/dev", timeout=180)
    out = {}
    for ln in pr.stdout.splitlines():
        if ln.startswith("U "):
            name, _, rest = ln[2:].strip().partition(" ")
            out[name] = rest
    if "U-count %d" % N_UNITS not in pr.stdout or len(out) != N_UNITS:
        raise Unmeasured("the harness printed %d units, want %d: %s" % (len(out), N_UNITS, pr.stderr[-400:]))
    return out


_CLEAN = [None]


def unit(name):
    if _CLEAN[0] is None:
        _CLEAN[0] = units(open(CORE, encoding="utf-8").read())
    return _CLEAN[0].get(name, "FAIL did not run")


def t_a_hit_on_tick_t_executes_t():
    """Also: the run is wired into the game's tick (the postfix on DoSingleTick), or the rule proves nothing."""
    src = open(VITALS, encoding="utf-8").read()
    post = src[src.index("private static void TickPost("):]
    post = post[:post.index("internal static void OnKill")]
    frame = src[src.index("internal static void Frame()"):][:700]
    if "JawaBenchSceneTick.TickEnd(" not in post or "JawaBenchSceneTick.Frame()" not in frame:
        return "FAIL the scene run is not called from TickPost and Frame of JawaBenchVitals.cs"
    return unit("a_hit_on_tick_t_executes_t")


def t_true_at_arm_executes_nothing():
    return unit("true_at_arm_executes_nothing")


def t_a_track_writes_on_change_only():
    return unit("a_track_writes_on_change_only")


def t_gone_is_gone_never_zero():
    return unit("gone_is_gone_never_zero")


def t_an_unknown_ends_the_run_as_unknown():
    return unit("an_unknown_ends_the_run_as_unknown")


def t_a_skipped_original_records_nothing():
    return unit("a_skipped_original_records_nothing")


def t_the_close_counts_the_dropped_and_waits_for_the_drain():
    return unit("the_close_counts_the_dropped_and_waits_for_the_drain")


def t_sample_before_act_inside_a_tick():
    return unit("sample_before_act_inside_a_tick")


def t_an_act_and_the_end_never_share_a_tick():
    return unit("an_act_and_the_end_never_share_a_tick")


def t_first_and_last_sample_of_every_track():
    return unit("first_and_last_sample_of_every_track")


def t_a_draw_in_the_sample_phase_is_reported():
    return unit("a_draw_in_the_sample_phase_is_reported")


PLANTS = [
    ("* sampling after the act steps", "sample_before_act_inside_a_tick",
     [("                Sample(tick, \"end_of_tick\", false);\n", ""),
      ("                    Emit(tick, \"end_of_tick\", \"act\",", "                    Emit(tick, \"end_of_tick\", \"act\","),
      ("S(d ?? \"\"));\n                }\n", "S(d ?? \"\"));\n                }\n                Sample(tick, \"end_of_tick\", false);\n")]),
    ("* the closing record before the writer drained", "the_close_counts_the_dropped_and_waits_for_the_drain",
     [("if (!drained && _h.NowMs() - _settleFrom < DrainMs) return;", "")]),
    ("* a stop that lets one more tick run", "a_hit_on_tick_t_executes_t",
     [("try { _paused = _h.Pause(); }", "try { _paused = true; }"),
      ("                if (Stage != \"running\") return;\n", "                if (Stage == \"settling\") _h.Pause();\n                if (Stage != \"running\") return;\n")]),
    ("a true start that runs a tick", "true_at_arm_executes_nothing", [("if (_cond.State != \"running\") End(tick, \"first\");", "")]),
    ("a row on every tick", "a_track_writes_on_change_only",
     [("if (!all && t.Has && r.Status == t.Last.Status && JawaBenchCondCore.SameValue(r.V, t.Last.V)) continue;", "")]),
    ("an allocation on every tick", "a_track_writes_on_change_only",
     [("                Sample(tick, \"end_of_tick\", false);\n", "                Sample(tick, \"end_of_tick\", false);\n                new List<object>(4).Add(_h);\n")]),
    ("gone written as 0", "gone_is_gone_never_zero", [("\",\\\"v\\\":\" + S(r.V)", "\",\\\"v\\\":\" + S(r.V ?? 0.0)")]),
    ("an unknown read as the deadline", "an_unknown_ends_the_run_as_unknown", [("\"\\\"state\\\":\" + S(State)", "\"\\\"state\\\":\" + S(State == \"unknown\" ? \"done\" : State)")]),
    ("a skipped tick sampled", "a_skipped_original_records_nothing", [("if (!runOriginal) { _skipped++; return; }", "if (!runOriginal) _skipped++;")]),
    ("a dropped row not counted", "the_close_counts_the_dropped_and_waits_for_the_drain", [("if (seq < 0) _dropped++; else _rows++;", "_rows++;")]),
    ("the acts before the end test", "an_act_and_the_end_never_share_a_tick",
     [("                if (_cond.State != \"running\") { End(tick, \"end_of_tick\"); return; }\n", ""),
      ("S(d ?? \"\"));\n                }\n", "S(d ?? \"\"));\n                }\n                if (_cond.State != \"running\") End(tick, \"end_of_tick\");\n")]),
    ("no last sample", "first_and_last_sample_of_every_track", [("Sample(tick, \"last\", true);", "")]),
    ("no first sample", "first_and_last_sample_of_every_track", [("Sample(tick, \"first\", true);", "")]),
    ("a draw not reported", "a_draw_in_the_sample_phase_is_reported", [("if (after == before) return;", "return;")]),
]


def plants():
    good = True
    src = open(CORE, encoding="utf-8").read()
    for name, must, subs in PLANTS:
        text = src
        for old, new in subs:
            if text.count(old) != 1:
                print("FAIL plant %r: its text is in the core %d times, want 1: %r" % (name, text.count(old), old[:70]))
                good = False
            text = text.replace(old, new)
        red = sorted(u for u, v in units(text).items() if v != "ok")
        hit = must in red
        good = good and hit
        print("%s plant %r turns red: %s" % ("ok  " if hit else "FAIL", name, red))
    return good


def main(argv):
    bad = 0
    tests = [t_a_hit_on_tick_t_executes_t, t_true_at_arm_executes_nothing, t_a_track_writes_on_change_only, t_gone_is_gone_never_zero,
             t_an_unknown_ends_the_run_as_unknown, t_a_skipped_original_records_nothing, t_the_close_counts_the_dropped_and_waits_for_the_drain,
             t_sample_before_act_inside_a_tick, t_an_act_and_the_end_never_share_a_tick, t_first_and_last_sample_of_every_track,
             t_a_draw_in_the_sample_phase_is_reported]
    try:
        for t in tests:
            v = t()
            bad += v != "ok"
            print("%s %s%s" % ("ok  " if v == "ok" else "FAIL", t.__name__[2:], "" if v == "ok" else ": " + v))
        good = True if "--no-plants" in argv else plants()
    except Unmeasured as e:
        print("FAIL scene tick wiring UNMEASURED: %s" % e)
        return 1
    print("scene tick wiring: %d of %d checks passed%s" % (len(tests) - bad, len(tests), "" if "--no-plants" in argv else ", plants %s" % ("all red" if good else "NOT all red")))
    return 0 if not bad and good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
