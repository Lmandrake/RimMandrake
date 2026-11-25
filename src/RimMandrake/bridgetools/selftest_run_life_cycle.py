#!/usr/bin/env python3
"""Selftest: the life cycle of a run under faults, and the run lock (JawaBenchSceneTickCore.cs, JawaBenchHandsCore.cs,
JawaBenchRunLockCore.cs). Page: design/specs/2026-11-23-bridge-v2-life-cycle/boundary.md, one test per promise, 10 checks. Each
plant breaks one rule of a copy of a core and must turn its named check red (the ticket's plants are marked *). The call sites in the
game half are read from the source: a rule that nothing calls is red. No game, no bridge. Without dotnet.exe it FAILS as UNMEASURED.
Run: python3 src/RimMandrake/bridgetools/selftest_run_life_cycle.py [--no-plants]"""
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
SC, HC, CC, PC, LC = ["JawaBench%sCore.cs" % n for n in ("SceneTick", "Hands", "Cond", "Path", "RunLock")]
CORES = [SC, HC, CC, PC, LC]
PROJ = os.path.join(HERE, "RunLifeCycleSelfTest", "RunLifeCycleSelfTest.csproj")
N_UNITS = 9                     # the tenth check is the hook table


class Unmeasured(Exception):
    pass


def read(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def tools():
    """[(name, description)] of every [Tool] in the companion's source."""
    out = []
    for n in sorted(os.listdir(CS)):
        if not n.endswith(".cs"):
            continue
        for m in re.finditer(r'\[Tool\(\s*"(jawa/[^"]+)"(.*?)\)\]\s*(?:public|internal)', read(os.path.join(CS, n)), re.S):
            d = re.search(r'Description\s*=\s*((?:"(?:[^"\\]|\\.)*"\s*\+?\s*)+)', m[2])
            out.append((m[1], "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', d[1]))[:200] if d else ""))
    if len(out) < 300:
        raise Unmeasured("only %d tools were read from the source" % len(out))
    return out


def units(texts):
    """Build the harness with these core texts, run it -> {unit: "ok" | "FAIL why"}."""
    import winbuild
    d = tempfile.mkdtemp(prefix="RunLifeCycle_", dir=winbuild.BUILD_ROOT)
    log = os.path.join(winbuild.BUILD_ROOT, "selftest_run_life_cycle.log")
    try:
        for n in CORES:
            with open(os.path.join(d, n), "w", encoding="utf-8") as f:
                f.write(texts[n])
        with open(os.path.join(d, "tools.tsv"), "w", encoding="utf-8") as f:
            f.write("\n".join("%s\t%s" % (n, t.replace("\t", " ")) for n, t in tools()))
        with open(log, "w") as lf:
            sys.stdout.flush()
            saved = os.dup(1)
            os.dup2(lf.fileno(), 1)
            try:
                rc, rec = winbuild.stage_build(PROJ, stage_name="RunLifeCycleSelfTest", extra=("-p:CoreDir=" + winbuild.win(d) + "\\",))
            finally:
                sys.stdout.flush()
                os.dup2(saved, 1)
                os.close(saved)
        if rc:
            raise Unmeasured("the harness build failed (rc %s), log %s" % (rc, log))
        dll = winbuild.staged_win(rec, os.path.dirname(PROJ)) + "\\bin\\Release\\net8.0\\RunLifeCycleSelfTest.dll"
        # hang guard: a planted core may never end
        pr = winbuild.run_interop_captured([winbuild.dotnet_exe(), dll, winbuild.win(os.path.join(d, "tools.tsv"))], capture_output=True, text=True,
                                           cwd="/mnt/d/Luke/dev", timeout=180)
    except (OSError, SystemExit) as e:
        raise Unmeasured("the harness could not be built or run: %s" % e)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    out = {}
    for ln in pr.stdout.splitlines():
        if ln.startswith("U "):
            name, _, rest = ln[2:].strip().partition(" ")
            out[name] = rest
    if "U-count %d" % N_UNITS not in pr.stdout or len(out) != N_UNITS:
        raise Unmeasured("the harness printed %d units, want %d: %s" % (len(out), N_UNITS, pr.stderr[-400:]))
    return out


def texts():
    return {n: read(os.path.join(CS, n)) for n in CORES}


_CLEAN = [None]


def unit(name):
    if _CLEAN[0] is None:
        _CLEAN[0] = units(texts())
    return _CLEAN[0].get(name, "FAIL did not run")


def body(name, start, end):
    """The source of one file with no comment, between two marks."""
    s = re.sub(r"//[^\n]*", "", read(os.path.join(CS, name)))
    i = s.find(start)
    j = s.find(end, i + 1) if i >= 0 else -1
    return s[i:j] if j > i else ""


def wired(*wants):
    """Null when each (what, text, pattern) is there, else the first that is not."""
    for what, text, pat in wants:
        if not re.search(pat, text, re.S):
            return "FAIL not wired: %s" % what
    return None


def t_a_safety_stop_and_a_hit_on_one_tick_report_both():
    sa = body("JawaBenchVitals.cs", "internal static bool EndedByScene", "internal static void Finish(")
    return wired(("TickPost gives the step loop's stop to the run", body("JawaBenchVitals.cs", "private static void TickPost(", "private static void TickFin("),
                  r"TickEnd\(true, JawaBenchSafeAdvance\.StopOfTick\(\)\)"),
                 ("safe_advance stops on the run's tick", sa, r"tm\.DoSingleTick\(\);.{0,400}if \(EndedByScene\(r\)\) return;"),
                 ("run_scenes stops on the run's tick", body("JawaBenchSceneRunnerTools.cs", "private static async Task RunOneScene", "private sealed class SceneStop"),
                  r"tm\.DoSingleTick\(\);\s*o\.ticks\+\+;\s*if \(cond != null && !cond\.Running\)")) or unit("a_safety_stop_and_a_hit_on_one_tick_report_both")


def t_the_budget_stop_names_the_costliest_node():
    return unit("the_budget_stop_names_the_costliest_node")


def t_an_epoch_change_ends_the_run():
    s = read(os.path.join(CS, "JawaBenchSceneTick.cs"))
    return wired(("the tick and the frame both look for the game and the map", s, r"Find\.Maps\.Contains\(RunMap\).*string gone = Gone\(\);.*string gone = Gone\(\);")) \
        or unit("an_epoch_change_ends_the_run")


def t_two_runs_cannot_be_armed_at_once():
    s = body("JawaBenchSceneTick.cs", "internal static string Refuse(", "internal static string NewId")
    arm = read(os.path.join(CS, "JawaBenchSceneRunnerTools.cs"))
    return wired(("Refuse asks the lock core", s, r"LK\.RefuseArm\(Cur\?\.Id, Cur\?\.Stage,.*StepOwner, caller\)"),
                 ("run_scenes owns the step", arm, r"StepOwner = SceneRunnerTool;.*StepOwner = null;")) or unit("two_runs_cannot_be_armed_at_once")


def t_a_thrown_tick_still_writes_its_closing_record():
    fin = body("JawaBenchVitals.cs", "private static void TickFin(", "internal static void OnKill")
    return wired(("the finalizer is on DoSingleTick", read(os.path.join(CS, "JawaBenchVitals.cs")), r"finalizer: new HarmonyMethod\(t\.GetMethod\(nameof\(TickFin\)"),
                 ("the finalizer ends the run", fin, r"JawaBenchSceneTick\.TickThrew\(__exception\)"),
                 ("TickThrew forces the run", body("JawaBenchSceneTick.cs", "internal static void TickThrew(", "internal static void TickEnd("), r'r\.Force\("threw"')) \
        or unit("a_thrown_tick_still_writes_its_closing_record")


def t_a_changing_tool_during_a_run_is_refused_with_the_run_id():
    g = body("JawaBenchCompanionSafety.cs", "private static string Check(", "internal static string CheckReserved(")
    act = body("JawaBenchHands.cs", "public ActOutcome Act(string tool", "public bool Root(string of")
    return wired(("the gate asks the lock", g, r"JawaBenchSceneTick\.LockHolder\(\).*JawaBenchRunLockCore\.Refuse\(tool, read,.*run\.Id, JawaBenchSceneTick\.InsideAct > 0, run\.Lock\)"),
                 ("both gates hand over the arguments", g, r"GateTask\(MethodBase __originalMethod, object\[\] __args,.*Check\(__originalMethod, __args\).*"
                  r"GateObject\(MethodBase __originalMethod, object\[\] __args,.*Check\(__originalMethod, __args\)"),
                 ("an act of the run is inside", act, r"InsideAct\+\+;\s*try \{ r = m\.Invoke.*finally \{ JawaBenchSceneTick\.InsideAct--; \}")) \
        or unit("a_changing_tool_during_a_run_is_refused_with_the_run_id")


def t_a_read_tool_during_a_run_is_allowed_and_counted():
    return unit("a_read_tool_during_a_run_is_allowed_and_counted")


def t_a_cancelled_run_leaves_the_game_paused():
    """Also: an advance that ends for its own reason ends its run too."""
    return wired(("the end of an advance ends its run", body("JawaBenchVitals.cs", "internal static void Finish(", "internal static class ZZ") or
                  read(os.path.join(CS, "JawaBenchVitals.cs")).split("internal static void Finish(")[1], r"r\.Scene != null && r\.Scene\.Running.*r\.Scene\.Force\(")) \
        or unit("a_cancelled_run_leaves_the_game_paused")


def t_a_run_refused_for_no_player_control_changes_nothing():
    step = body("JawaBenchSceneTick.cs", "internal static T.SceneRun MakeStep(", "internal static void ArmStep(")
    adv = read(os.path.join(CS, "JawaBenchVitalsTools.cs"))
    return wired(("Refuse reads PlayerCanControl", body("JawaBenchSceneTick.cs", "internal static string Refuse(", "internal static string NewId"), r"PlayerCanControl.*Accepted\) return"),
                 ("a step run asks Refuse", step, r"Refuse\(caller\)"),
                 ("safe_advance makes the run before it changes anything", adv, r"MakeStep\(\"jawa/safe_advance\".*if \(scene == null\) return.*VT\.Arm\(V\.AutoArmTtlMin")) \
        or unit("a_run_refused_for_no_player_control_changes_nothing")


def t_the_hook_table_check_still_passes():
    # hang guard: the static audit alone takes about a second
    p = subprocess.run([sys.executable, os.path.join(HERE, "selftest_bridge_hooks.py"), "--no-cs"], capture_output=True, text=True, timeout=600)
    return "ok" if p.returncode == 0 else "FAIL exit %d: %s" % (p.returncode, (p.stdout + p.stderr)[-400:])


PLANTS = [
    ("* the lock covers one family only", "a_changing_tool_during_a_run_is_refused_with_the_run_id", LC,
     [("if (runId == null || inside) return null;", "if (runId == null || inside || tool == null || !tool.StartsWith(\"jawa/spawn\")) return null;")]),
    ("* a cancel that leaves the evaluator armed", "a_cancelled_run_leaves_the_game_paused", SC,
     [("                Stage = \"settling\";                  // first", "                if (_forced != \"cancelled\") Stage = \"settling\";                  // first")]),
    ("a cancel that does not pause", "a_cancelled_run_leaves_the_game_paused", SC, [("try { _paused = _h.Pause(); }", "try { _paused = _forced == \"cancelled\" || _h.Pause(); }")]),
    ("a lease that ends and leaves the run", "a_cancelled_run_leaves_the_game_paused", HC,
     [("if (RunLive) Cur.Last.Run.Force(\"cancelled\", \"the driver's lease ended\", _h.Tick());", "")]),
    ("the safety stop hides the hit", "a_safety_stop_and_a_hit_on_one_tick_report_both", CC, [("if (hit)\n                {\n                    trig.Add(\"cond\");", "if (hit && string.IsNullOrEmpty(stop))\n                {\n                    trig.Add(\"cond\");")]),
    ("the safety stop is dropped", "a_safety_stop_and_a_hit_on_one_tick_report_both", SC, [("_cond.Step(tick, epoch, stop);", "_cond.Step(tick, epoch, null);")]),
    ("the budget names the first node", "the_budget_stop_names_the_costliest_node", SC, [("if (n.Probe != null && n.Ms > ms)", "if (n.Probe != null && id == null)")]),
    ("no budget stop", "the_budget_stop_names_the_costliest_node", SC, [("if (_budgetMs > 0 && ms > _budgetMs)", "if (false)")]),
    ("a budget of 0 stops", "the_budget_stop_names_the_costliest_node", SC, [("if (_budgetMs > 0 && ms > _budgetMs)", "if (ms > _budgetMs)")]),
    ("the epoch is not compared", "an_epoch_change_ends_the_run", CC, [("if (!SameValue(epoch, _epoch))", "if (false)")]),
    ("a second run beside one that settles", "two_runs_cannot_be_armed_at_once", LC, [("if (liveId != null && liveStage != \"closed\")", "if (liveId != null && liveStage == \"running\")")]),
    ("a second run of the session", "two_runs_cannot_be_armed_at_once", HC,
     [("                if (RunLive) return Refusal(\"RUN_ACTIVE\", \"run \" + Cur.Last.Run.Id + \" is \" + Cur.Last.Run.Stage, \"read its status, then cancel it\");\n                if (!_h.Paused()) return Refusal(\"GAME_RUNNING\", \"the game is not paused\", \"something",
       "                if (!_h.Paused() && false) return Refusal(\"GAME_RUNNING\", \"the game is not paused\", \"something")]),
    ("a pause that throws leaves the run running", "a_thrown_tick_still_writes_its_closing_record", SC,
     [("                Stage = \"settling\";                  // first", "                _endTick = tick;                  // first")]),
    ("a last sample that throws is not said", "a_thrown_tick_still_writes_its_closing_record", SC, [("Fault(tick, \"last\", \"threw\", \"the last sample: \"", "Math.Abs(0); string.Concat(\"the last sample: \"")]),
    ("a run whose arm threw stays", "a_thrown_tick_still_writes_its_closing_record", SC, [("{ Force(\"aborted\", \"the arm threw \" + e.GetType().Name + \": \" + e.Message, tick); return; }", "{ if (e == null) return; return; }")]),
    ("an unreviewed tool passes", "a_changing_tool_during_a_run_is_refused_with_the_run_id", LC, [("return declaredRead && tool", "return tool.Contains(\"tomorrow\") || declaredRead && tool")]),
    ("static_call passes when declared a read", "a_changing_tool_during_a_run_is_refused_with_the_run_id", LC, [("return declaredRead && tool != NeverARead;", "return declaredRead;")]),
    ("a refused call is not on the record", "a_changing_tool_during_a_run_is_refused_with_the_run_id", LC, [("if (log != null) log.Refused(", "if (false) log.Refused(")]),
    ("a read is not counted", "a_read_tool_during_a_run_is_allowed_and_counted", LC, [("if (log != null && (!OwnCheck.Contains(tool))) log.Read();", "")]),
    ("a read is refused", "a_read_tool_during_a_run_is_allowed_and_counted", LC, [("if (OwnCheck.Contains(tool) || Reads.Contains(tool)) return true;", "if (OwnCheck.Contains(tool)) return true;")]),
    ("a refused run pauses the game", "a_run_refused_for_no_player_control_changes_nothing", HC,
     [("                string why = _h.RefuseRun();\n", "                string why = _h.RefuseRun();\n                if (why != null) _h.Pause();\n")]),
]


def plants():
    good, src = True, texts()
    for name, must, core, subs in PLANTS:
        t = dict(src)
        for old, new in subs:
            if t[core].count(old) != 1:
                print("FAIL plant %r: its text is in %s %d times, want 1: %r" % (name, core, t[core].count(old), old[:70]))
                good = False
            t[core] = t[core].replace(old, new)
        try:
            red = sorted(u for u, v in units(t).items() if v != "ok")
        except Unmeasured as e:
            red = ["UNMEASURED %s" % e]
        hit = must in red
        good = good and hit
        print("%s plant %r turns red: %s" % ("ok  " if hit else "FAIL", name, red), flush=True)
    return good


def main(argv):
    tests = [t_a_safety_stop_and_a_hit_on_one_tick_report_both, t_the_budget_stop_names_the_costliest_node, t_an_epoch_change_ends_the_run,
             t_two_runs_cannot_be_armed_at_once, t_a_thrown_tick_still_writes_its_closing_record,
             t_a_changing_tool_during_a_run_is_refused_with_the_run_id, t_a_read_tool_during_a_run_is_allowed_and_counted,
             t_a_cancelled_run_leaves_the_game_paused, t_a_run_refused_for_no_player_control_changes_nothing, t_the_hook_table_check_still_passes]
    bad = 0
    try:
        for t in tests:
            v = t()
            bad += v != "ok"
            print("%s %s%s" % ("ok  " if v == "ok" else "FAIL", t.__name__[2:], "" if v == "ok" else ": " + v))
        good = True if "--no-plants" in argv else plants()
    except Unmeasured as e:
        print("FAIL run life cycle UNMEASURED: %s" % e)
        return 1
    print("run life cycle: %d of %d checks passed%s" % (len(tests) - bad, len(tests), "" if "--no-plants" in argv else ", plants %s" % ("all red" if good else "NOT all red")))
    return 0 if not bad and good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
