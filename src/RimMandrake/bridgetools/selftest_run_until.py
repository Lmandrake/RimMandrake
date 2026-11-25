#!/usr/bin/env python3
"""Selftest: the generic hands of BRIDGE v2.0 (JawaBenchPathCore.cs, JawaBenchHandsCore.cs and the run they start). Page:
design/specs/2026-11-23-bridge-v2-hands/boundary.md; one test per promise: the 18 checks of the item, and 2 for the acts inside a
run. Each plant breaks one rule of a copy of a core and must turn its named check red (the item's plants are marked *). No game,
no bridge. Without dotnet.exe it FAILS as UNMEASURED.
Run: python3 src/RimMandrake/bridgetools/selftest_run_until.py [--no-plants]"""
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
import selftest_scene_tick_wiring as SLICE  # noqa: E402

CS = os.path.join(HERE, "JawaBench.BridgeTools")
CORES = ["JawaBenchCondCore.cs", "JawaBenchSceneTickCore.cs", "JawaBenchPathCore.cs", "JawaBenchHandsCore.cs"]
HANDS = os.path.join(CS, "JawaBenchHands.cs")
PROJ = os.path.join(HERE, "RunUntilSelfTest", "RunUntilSelfTest.csproj")
N_UNITS = 19                    # fewer printed = the harness did not run whole


class Unmeasured(Exception):
    pass


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def units(texts):
    """Build the harness with these core texts, run it -> {unit: "ok" | "FAIL why"}."""
    import winbuild
    d = tempfile.mkdtemp(prefix="RunUntilCore_", dir=winbuild.BUILD_ROOT)
    log = os.path.join(winbuild.BUILD_ROOT, "selftest_run_until.log")
    try:
        for n in CORES:
            with open(os.path.join(d, n), "w", encoding="utf-8") as f:
                f.write(texts[n])
        with open(log, "w") as lf:
            sys.stdout.flush()
            saved = os.dup(1)
            os.dup2(lf.fileno(), 1)
            try:
                rc, rec = winbuild.stage_build(PROJ, stage_name="RunUntilSelfTest", extra=("-p:CoreDir=" + winbuild.win(d) + "\\",))
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
    dll = winbuild.staged_win(rec, os.path.dirname(PROJ)) + "\\bin\\Release\\net8.0\\RunUntilSelfTest.dll"
    pr = winbuild.run_interop_captured([winbuild.dotnet_exe(), dll], capture_output=True, text=True, cwd="/mnt/d/Luke/dev", timeout=180)
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
        _CLEAN[0] = units({n: read(os.path.join(CS, n)) for n in CORES})
    return _CLEAN[0].get(name, "FAIL did not run")


def code(path):
    """The C# of a file with its comments and its strings blanked: what is wired, not what is described."""
    s = re.sub(r'@"(?:[^"]|"")*"|"(?:\\.|[^"\\\n])*"', '""', read(path))
    return re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", s, flags=re.S))


def wired(*needles):
    """None when the Verse half holds each of these calls, else what is missing: a rule of the core that no tool calls proves nothing."""
    s = re.sub(r"\s+", " ", code(HANDS))
    for n in needles:
        if n not in s:
            return "FAIL JawaBenchHands.cs does not hold: " + n
    return None


# ------------------------------------------------------------------------------------------------ the item's 18 checks
def t_the_slice_promises_hold_in_a_session():
    try:
        u = SLICE.units(read(SLICE.CORE), "session")
    except SLICE.Unmeasured as e:
        raise Unmeasured(str(e))
    red = sorted("%s: %s" % kv for kv in u.items() if kv[1] != "ok")
    acts = wired("new T.SceneRun(")
    body = code(HANDS)
    if acts is None and re.search(r"\bTakeDamage\(|FindPawn\(", body[body.index("> RunUntil("):body.index("> ReadPaths(")]):
        acts = "FAIL jawa/run_until holds an act or a pawn of its own"
    return "ok" if not red and acts is None else (acts or "FAIL " + "; ".join(red))


def t_one_session_one_trace_no_gap():
    return unit("one_session_one_trace_no_gap")


def t_true_at_start_plays_no_tick():
    return unit("true_at_start_plays_no_tick")


def t_hit_wins_over_limit():
    return unit("hit_wins_over_limit")


def t_an_unreadable_value_ends_as_unknown_and_is_named():
    return unit("an_unreadable_value_ends_as_unknown_and_is_named")


def t_a_group_is_frozen():
    return unit("a_group_is_frozen")


def t_private_fields_and_statics_are_read():
    return wired("P.Read(") or unit("private_fields_and_statics_are_read")


def t_a_wrong_field_is_an_error_with_the_fields():
    return unit("a_wrong_field_is_an_error_with_the_fields")


def t_an_unreviewed_method_is_refused_by_name():
    return unit("an_unreviewed_method_is_refused_by_name")


def t_a_thousand_reads_change_nothing():
    return unit("a_thousand_reads_change_nothing")


def t_only_the_driver_drives_an_open_session():
    s = code(os.path.join(CS, "JawaBenchSceneTick.cs"))
    cancel = re.search(r'if \(a == ""\)\s*\{([^{}]*r\.Force\([^{}]*)\}', s)
    if not cancel or not re.search(r'if \(JawaBenchHands\.Busy\) return Fail\(""\);.*r\.Force\(', cancel[1], re.S):
        return "FAIL jawa/scene_slice can reach Force while a session is open"
    return unit("only_the_driver_drives_an_open_session")


def t_a_taken_session_is_read_and_ended_never_played():
    return unit("a_taken_session_is_read_and_ended_never_played")


def t_a_session_past_its_lease_stays_open_and_paused():
    """Also: the session's clock is wired into the game's frame."""
    if "JawaBenchHands.Frame()" not in code(os.path.join(CS, "JawaBenchSceneTick.cs")):
        return "FAIL JawaBenchSceneTick.Frame does not call JawaBenchHands.Frame"
    return unit("a_session_past_its_lease_stays_open_and_paused")


def t_no_session_no_run():
    return unit("no_session_no_run")


def t_the_slice_tool_still_passes():
    p = subprocess.run([sys.executable, os.path.join(HERE, "selftest_scene_tick_wiring.py"), "--no-plants"], capture_output=True, text=True, timeout=600)
    tool = re.search(r'"jawa/scene_slice"', read(os.path.join(CS, "JawaBenchSceneTick.cs")))
    return "ok" if p.returncode == 0 and "11 of 11 checks passed" in p.stdout and tool else "FAIL exit %d: %s" % (p.returncode, p.stdout[-300:])


def t_no_frame_inside_a_batch():
    """Also: the tool makes its whole batch one hop, and a tool body inside it runs on this hop's own main thread."""
    return wired("JawaBenchHandsCore.OneHop(f => ctx.MainThread.InvokeAsync(f", "class InlineMainThread : IRimBridgeMainThread") or unit("no_frame_inside_a_batch")


def t_a_repeated_id_returns_the_first_reply():
    return unit("a_repeated_id_returns_the_first_reply")


def t_a_changed_repeat_is_refused():
    return unit("a_changed_repeat_is_refused")


def t_a_thrown_act_keeps_the_acts_before_it():
    return unit("a_thrown_act_keeps_the_acts_before_it")


# ------------------------------------------------------------------------------------------------ added by experiment A
def t_an_act_at_zero_shares_the_hop_that_starts_the_clock():
    return unit("an_act_at_zero_shares_the_hop_that_starts_the_clock")


def t_an_act_on_a_tick_is_any_tool_call():
    return unit("an_act_on_a_tick_is_any_tool_call")


SC, PC, HC, CC = "JawaBenchSceneTickCore.cs", "JawaBenchPathCore.cs", "JawaBenchHandsCore.cs", "JawaBenchCondCore.cs"
PLANTS = [
    ("* a second run starts a new trace", "one_session_one_trace_no_gap", HC,
     [("var run = make(runId, ticks, Cur.Trace);", "var run = make(runId, ticks, Cur.Runs.Count > 0 ? new T.Trace { Session = Cur.Id } : Cur.Trace);")]),
    ("* an unreadable condition value counted as false", "an_unreadable_value_ends_as_unknown_and_is_named", CC,
     [("else if (n.Optional) { v = false;", "else { v = false;")]),
    ("an unknown value with no name", "an_unreadable_value_ends_as_unknown_and_is_named", SC,
     [("d[\"value\"] = n != null && n.Probe != null ? n.Probe.Key : null;", "d[\"value\"] = \"\";")]),
    ("an optional node let through", "an_unreadable_value_ends_as_unknown_and_is_named", HC,
     [("if (d.TryGetValue(\"optional\", out opt) && !(opt is bool && !(bool)opt))", "if (d.TryGetValue(\"nothing\", out opt))")]),
    ("* a group that drops its dead member", "a_group_is_frozen", SC,
     [("t.Has = true; t.Last = r;", "if (r.Status == \"gone\") { _tracks.RemoveAt(i--); continue; } t.Has = true; t.Last = r;")]),
    ("* a read that returns 0 for a gone thing", "a_group_is_frozen", PC,
     [("if (!h.Root(of, out o, out st, out bad)) return bad;", "if (!h.Root(of, out o, out st, out bad)) return bad.State == \"gone\" ? PathValue.Ok(0.0) : bad;")]),
    ("private members not seen", "private_fields_and_statics_are_read", PC,
     [("BindingFlags.Instance | BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly", "BindingFlags.Instance | BindingFlags.Static | BindingFlags.Public | BindingFlags.DeclaredOnly")]),
    ("an error that does not list the fields", "a_wrong_field_is_an_error_with_the_fields", PC,
     [("+ t.FullName + \"; it has: \" + string.Join(\", \", Fields(t, isStatic).ToArray());", "+ t.FullName;")]),
    ("any property is called", "an_unreviewed_method_is_refused_by_name", PC,
     [("if (Reviewed.Contains(ListName(p))) { a.P = p; break; }", "a.P = p; break;")]),
    ("a read with an effect", "a_thousand_reads_change_nothing", PC,
     [("if (Reviewed.Contains(ListName(p))) { a.P = p; break; }", "a.P = p; break;")]),
    ("* a run lock that refuses the session's own driver", "only_the_driver_drives_an_open_session", HC,
     [("if (string.IsNullOrEmpty(driver) || driver != Cur.Driver)", "if (true)")]),
    ("a session that anyone drives", "only_the_driver_drives_an_open_session", HC,
     [("if (string.IsNullOrEmpty(driver) || driver != Cur.Driver)", "if (false)")]),
    ("a taken session may be played", "a_taken_session_is_read_and_ended_never_played", HC, [("return Cur.Taken ? Refusal(", "return false ? Refusal(")]),
    ("a live lease is taken with no name", "a_taken_session_is_read_and_ended_never_played", HC, [("if (!string.IsNullOrEmpty(from) ? from != old : !Cur.LeaseEnded)", "if (!string.IsNullOrEmpty(from) && from != old)")]),
    ("a take leaves the run playing", "a_taken_session_is_read_and_ended_never_played", HC, [("if (RunLive) Cur.Last.Run.Force(\"cancelled\", \"the session was taken over from", "if (false) Cur.Last.Run.Force(\"cancelled\", \"the session was taken over from")]),
    ("a lease that closes the session", "a_session_past_its_lease_stays_open_and_paused", HC,
     [("Cur.LeaseEnded = true;\n", "Cur.LeaseEnded = true; Cur.End = \"aborted\"; Cur.Stage = \"closing\";\n")]),
    ("a lease that pauses nothing", "a_session_past_its_lease_stays_open_and_paused", HC,
     [("Cur.Last.Run.Force(\"cancelled\", \"the driver's lease ended\", _h.Tick());\n                    bool p = _h.Pause();", "{ }\n                    bool p = true;")]),
    ("a run with no session", "no_session_no_run", HC,
     [("if (!IsOpen) return Refusal(\"NO_SESSION\",", "if (Cur == null) Open(driver, 600);\n                if (!IsOpen) return Refusal(\"NO_SESSION\",")]),
    ("a true start that plays", "true_at_start_plays_no_tick", SC,
     [("if (_cond.State != \"running\") End(tick, \"first\");", "")]),
    ("the limit wins over the hit", "hit_wins_over_limit", CC,
     [("                else if (hit) State = \"hit\";", "                else if (hit && k < _c.MaxTicks) State = \"hit\";")]),
    ("* a batch that hops once for each act", "no_frame_inside_a_batch", HC,
     [("ActOutcome o;\n                try { o = _h.Act(a.Tool, a.Args); }", "ActOutcome o = null;\n                try { Hop1(() => o = _h.Act(a.Tool, a.Args)); }"),
      ("            List<object> DoAll(", "            internal static Func<Func<object>, Task<object>> HopOf;\n            void Hop1(Func<object> f) { if (HopOf != null) HopOf(f); else f(); }\n            List<object> DoAll("),
      ("            return hop(body);", "            Hands.HopOf = hop; try { return hop(body); } finally { Hands.HopOf = null; }")]),
    ("* a repeated id done twice", "a_repeated_id_returns_the_first_reply", HC,
     [("if (Cur.Acts.TryGetValue(a.Id, out known))\n                    return new", "if (Cur.Acts.TryGetValue(a.Id, out known) && a.Id == \"\")\n                    return new")]),
    ("a run request played twice", "a_repeated_id_returns_the_first_reply", HC,
     [("if (Cur.Runs.TryGetValue(request, out known))", "if (Cur.Runs.TryGetValue(request + \"?\", out known))")]),
    ("a changed repeat answered with the first reply", "a_changed_repeat_is_refused", HC,
     [("Cur.Acts.TryGetValue(a.Id, out known) && known.Canon != a.Canon)", "Cur.Acts.TryGetValue(a.Id, out known) && false)")]),
    ("a batch that goes on after a thrown act", "a_thrown_act_keeps_the_acts_before_it", HC,
     [("if (!\"done\".Equals(r[\"state\"])) firstBad = a.Id;", "")]),
    ("a thrown act that loses the batch", "a_thrown_act_keeps_the_acts_before_it", HC,
     [("catch (Exception e) { o = new ActOutcome { State = \"failed\", Error = e.GetType().Name + \": \" + e.Message }; }", "finally { }")]),
    ("the clock starts before the act at zero", "an_act_at_zero_shares_the_hop_that_starts_the_clock", HC,
     [("                if (run.Running && starts.Count > 0)\n", "                if (run.Running && starts.Count > 0) go();\n                if (run.Running && starts.Count > 0)\n")]),
    ("the clock starts after a failed act", "an_act_at_zero_shares_the_hop_that_starts_the_clock", HC,
     [("if (bad != null) run.Force(", "if (false) run.Force(")]),
    ("an act on a tick with no record of its own", "an_act_on_a_tick_is_any_tool_call", HC,
     [("var r = DoOne(act, \"end_of_tick\");", "var r = new Dictionary<string, object> { { \"state\", _h.Act(act.Tool, act.Args).State }, { \"error\", null } };")]),
]


def plants():
    good = True
    src = {n: read(os.path.join(CS, n)) for n in CORES}
    for name, must, file, subs in PLANTS:
        texts = dict(src)
        for old, new in subs:
            if texts[file].count(old) != 1:
                print("FAIL plant %r: its text is in %s %d times, want 1: %r" % (name, file, texts[file].count(old), old[:70]))
                good = False
            texts[file] = texts[file].replace(old, new)
        red = sorted(u for u, v in units(texts).items() if v != "ok")
        hit = must in red
        good = good and hit
        print("%s plant %r turns red: %s" % ("ok  " if hit else "FAIL", name, red), flush=True)
    return good


def main(argv):
    item = [t_the_slice_promises_hold_in_a_session, t_one_session_one_trace_no_gap, t_true_at_start_plays_no_tick, t_hit_wins_over_limit,
            t_an_unreadable_value_ends_as_unknown_and_is_named, t_a_group_is_frozen, t_private_fields_and_statics_are_read,
            t_a_wrong_field_is_an_error_with_the_fields, t_an_unreviewed_method_is_refused_by_name, t_a_thousand_reads_change_nothing,
            t_only_the_driver_drives_an_open_session, t_a_taken_session_is_read_and_ended_never_played, t_a_session_past_its_lease_stays_open_and_paused, t_no_session_no_run,
            t_the_slice_tool_still_passes, t_no_frame_inside_a_batch, t_a_repeated_id_returns_the_first_reply, t_a_changed_repeat_is_refused,
            t_a_thrown_act_keeps_the_acts_before_it]
    added = [t_an_act_at_zero_shares_the_hop_that_starts_the_clock, t_an_act_on_a_tick_is_any_tool_call]
    bad = {}
    try:
        for t in item + added:
            v = t()
            bad[t] = v != "ok"
            print("%s %s%s" % ("ok  " if v == "ok" else "FAIL", t.__name__[2:], "" if v == "ok" else ": " + v), flush=True)
        good = True if "--no-plants" in argv else plants()
    except Unmeasured as e:
        print("FAIL run until UNMEASURED: %s" % e)
        return 1
    print("run until: %d of %d checks passed; acts inside a run: %d of %d%s" % (
        sum(not bad[t] for t in item), len(item), sum(not bad[t] for t in added), len(added),
        "" if "--no-plants" in argv else "; plants %s" % ("all red" if good else "NOT all red")))
    return 0 if not any(bad.values()) and good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
