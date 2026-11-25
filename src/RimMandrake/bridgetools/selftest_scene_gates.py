#!/usr/bin/env python3
# selftest-timeout: 3600   (fourteen harness builds of ~3 min each through winbuild, and selftest_bridge_hooks.py with its own C# build)
"""Selftest: the scene gates of BRIDGE v2.0 - incident, quest and mental-state gates with an allow list and an attempt count, and
the incident queue held aside and given back (JawaBenchGatesCore.cs; the Verse half JawaBenchGates.cs and the incident gate's call
in JawaBenchAwareness.IncPre). Item RIMMANDRAKE_BUILD_INCIDENT_QUEST_MENTAL_GATES_BEFORE_CERTIFICATE.
Page: design/specs/2026-11-23-bridge-v2/boundary.md §SCENE GATES; one test per promise there, 9 checks:

  1 the allow list lets one named incident through once    2 a held attempt is counted and recorded with its caller
  3 a gate that is off changes nothing and records nothing
  4-5 a held queue entry comes back with its fire tick moved, and with its retry window moved
  6 an entry past its retry window when held is reported, never dropped in silence
  7-8 the hook rules of the two new gate sites (quest, mental), and their rows on HOOKS.md (selftest_bridge_hooks.py)
  9 with a canonical save loaded (CAMPAIGN), every gate is refused

Each plant breaks one rule of a COPY of the gates core and must turn its named check red. The build order's plant is
"a queue return that moves the fire tick only" (GPT's case: the entry expires at once).
An offline test proves the rules, never that a hook is connected in the game: the tap certificate ticket does that live.
No game, no bridge. Without dotnet.exe it FAILS as UNMEASURED.
Run: python3 src/RimMandrake/bridgetools/selftest_scene_gates.py [--no-plants]"""
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
CORE = "JawaBenchGatesCore.cs"
VERSE = "JawaBenchGates.cs"
AWARE = "JawaBenchAwareness.cs"
PROJ = os.path.join(HERE, "GatesSelfTest", "GatesSelfTest.csproj")
N_UNITS = 9                     # fewer printed = the harness did not run whole


class Unmeasured(Exception):
    pass


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def units(core_text):
    """Build the harness with this gates core, run it -> {unit: "ok" | "FAIL why"}."""
    import winbuild
    d = tempfile.mkdtemp(prefix="GatesCore_", dir=winbuild.BUILD_ROOT)
    log = os.path.join(winbuild.BUILD_ROOT, "selftest_scene_gates.log")
    try:
        with open(os.path.join(d, CORE), "w", encoding="utf-8") as f:
            f.write(core_text)
        with open(log, "w") as lf:
            sys.stdout.flush()
            saved = os.dup(1)
            os.dup2(lf.fileno(), 1)
            try:
                rc, rec = winbuild.stage_build(PROJ, stage_name="GatesSelfTest", extra=("-p:CoreDir=" + winbuild.win(d) + "\\",))
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
    dll = winbuild.staged_win(rec, os.path.dirname(PROJ)) + "\\bin\\Release\\net8.0\\GatesSelfTest.dll"
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
_HOOKS = [None]


def hook_table():
    """selftest_bridge_hooks.py once: every patch site on HOOKS.md with its rules (the two gate sites included)."""
    if _HOOKS[0] is None:
        p = subprocess.run([sys.executable, os.path.join(HERE, "selftest_bridge_hooks.py")], capture_output=True, text=True, timeout=1500)
        tail = [ln for ln in p.stdout.splitlines() if ln.startswith(("FAIL", "RESULT", "static audit", "C# units"))]
        if p.returncode == 0 and "RESULT PASS" in p.stdout:
            _HOOKS[0] = "ok"
        elif any("UNMEASURED" in ln for ln in tail):
            raise Unmeasured("selftest_bridge_hooks.py: " + " | ".join(tail)[-400:])
        else:
            _HOOKS[0] = "FAIL selftest_bridge_hooks.py rc %d: %s" % (p.returncode, " | ".join(tail)[-600:])
    return _HOOKS[0]


def on_table(*hooks):
    """None when HOOKS.md has the JawaBenchGates.cs row with each of these hooks and its rules, else what is missing."""
    rows = [ln for ln in read(os.path.join(HERE, "HOOKS.md")).splitlines() if ln.startswith("| `%s`" % VERSE)]
    if len(rows) != 1:
        return "FAIL HOOKS.md has %d rows for %s, want 1" % (len(rows), VERSE)
    for h in hooks:
        if h not in rows[0]:
            return "FAIL the HOOKS.md row of %s does not hold %s" % (VERSE, h)
    return None


def t_the_allow_list_lets_one_named_incident_through_once():
    return both(wired(AWARE, "run = JawaBenchGates.IncidentGate(__instance, parms, __runOriginal);", "if (!run) __result = false;", "return run;",
                      "bool __runOriginal, ref bool __result, out IncState __state"),
                wired(VERSE, "return g.Decide(OnMain(), runOriginal, Current.Game, Campaign(), worker != null && worker.def != null ? worker.def.defName : null,"),
                unit("the_allow_list_lets_one_named_incident_through_once"))


def t_a_held_attempt_is_counted_and_recorded_with_its_caller():
    return both(wired(VERSE, "foreach (var g in G.All) g.Sink = () => JawaBenchWorld.LiveSink;", "() => CallerOf(typeof(IncidentWorker), ",
                      "() => CallerOf(typeof(QuestManager), ", "() => CallerOf(typeof(MentalStateHandler), "),
                wired("JawaBenchWorld.cs", "internal static ICastSink LiveSink { get { return TheSink; } }"),
                unit("a_held_attempt_is_counted_and_recorded_with_its_caller"))


def t_a_gate_that_is_off_changes_nothing_and_records_nothing():
    s = code(os.path.join(CS, VERSE))
    n = s.count("if (!g.On) return true;")
    return both(None if n == 3 else "FAIL %s checks `if (!g.On) return true;` %d times, want 3 (one per gate hook)" % (VERSE, n),
                unit("a_gate_that_is_off_changes_nothing_and_records_nothing"))


def t_a_held_queue_entry_comes_back_with_its_fire_tick_moved():
    return both(wired(VERSE, "_fireTick(qi) = (int)e.FireTick;", "q.Add(qi);", "FireTick = qi.FireTick, RetryEnd = (long)qi.FireTick + qi.RetryDurationTicks, Tried = qi.TriedToFire"),
                unit("a_held_queue_entry_comes_back_with_its_fire_tick_moved"))


def t_a_held_queue_entry_comes_back_with_its_retry_window_moved():
    return both(wired(VERSE, "_retry(qi) = (int)e.RetryDuration;"), unit("a_held_queue_entry_comes_back_with_its_retry_window_moved"))


def t_an_entry_past_its_retry_window_when_held_is_reported_never_dropped_in_silence():
    return both(wired(VERSE, "var why = G.Queue.Hold(Current.Game, JawaBenchCompanionSafety.PolicyNow().DenyCampaignFamilies, Tick(), entries, report);",
                      "if (why == null) list.Clear();", "var back = G.Queue.GiveBack("),
                unit("an_entry_past_its_retry_window_when_held_is_reported_never_dropped_in_silence"))


def t_the_quest_gate_follows_the_hook_rules():
    return both(wired(VERSE, "h.Patch(quest, prefix: Hm(nameof(QuestGatePre)));", "private static bool QuestGatePre(Quest quest, bool __runOriginal)",
                      "{ priority = Priority.First }"),
                on_table("QuestGatePre[c,ro,th]"), unit("the_quest_gate_follows_the_hook_rules"), hook_table())


def t_the_mental_gate_follows_the_hook_rules():
    return both(wired(VERSE, "h.Patch(mental, prefix: Hm(nameof(MentalGatePre)));", "Pawn ___pawn, bool __runOriginal, ref bool __result)",
                      "if (!run) __result = false;"),
                on_table("MentalGatePre[c,ro,th]"), unit("the_mental_gate_follows_the_hook_rules"), hook_table())


def t_with_a_canonical_save_loaded_every_gate_is_refused():
    s = code(os.path.join(CS, VERSE))
    n = s.count("Current.Game, Campaign(),")
    return both(wired(VERSE, "bool campaign = JawaBenchCompanionSafety.PolicyNow().DenyCampaignFamilies;", "if (campaign) return g.Arm(Current.Game, true, allow);"),
                None if n == 3 else "FAIL %s hands Campaign() to Decide %d times, want 3" % (VERSE, n),
                unit("with_a_canonical_save_loaded_every_gate_is_refused"))


CHECKS = [t_the_allow_list_lets_one_named_incident_through_once, t_a_held_attempt_is_counted_and_recorded_with_its_caller,
          t_a_gate_that_is_off_changes_nothing_and_records_nothing, t_a_held_queue_entry_comes_back_with_its_fire_tick_moved,
          t_a_held_queue_entry_comes_back_with_its_retry_window_moved,
          t_an_entry_past_its_retry_window_when_held_is_reported_never_dropped_in_silence, t_the_quest_gate_follows_the_hook_rules,
          t_the_mental_gate_follows_the_hook_rules, t_with_a_canonical_save_loaded_every_gate_is_refused]

# ------------------------------------------------------------------------------------------------ plants
PLANTS = [
    ("a queue return that moves the fire tick only (GPT's case: the entry expires at once)", "a_held_queue_entry_comes_back_with_its_retry_window_moved",
     [("m.RetryEnd = e.RetryEnd + held;", "m.RetryEnd = e.RetryEnd;")]),
    ("a queue return that moves nothing", "a_held_queue_entry_comes_back_with_its_fire_tick_moved",
     [("m.FireTick = e.FireTick + held;", "m.FireTick = e.FireTick;")]),
    ("an allow entry that is never used up", "the_allow_list_lets_one_named_incident_through_once",
     [("if (allowed) _allow[name] = _allow[name] - 1;", "if (false) _allow[name] = _allow[name] - 1;")]),
    ("a held attempt with no caller", "a_held_attempt_is_counted_and_recorded_with_its_caller",
     [("try { a.Caller = caller == null ? null : caller(); }", "try { a.Caller = null; }")]),
    ("an off gate that counts", "a_gate_that_is_off_changes_nothing_and_records_nothing",
     [("if (!_on) return true;", "if (!_on) { Attempts++; return true; }")]),
    ("an expired entry dropped in silence at the give-back", "an_entry_past_its_retry_window_when_held_is_reported_never_dropped_in_silence",
     [('if (report != null) report.Add("not given back, past its retry window when held: " + e.Text());', "")]),
    ("a foreign-thread call decided by the gate", "the_quest_gate_follows_the_hook_rules",
     [("if (!onMain) { System.Threading.Interlocked.Increment(ref ForeignPassed); return true; }", "")]),
    ("another prefix's skip held again and counted", "the_mental_gate_follows_the_hook_rules",
     [("if (!runOriginal) { AlreadySkipped++; return true; }", "")]),
    ("a fault in the log that lets a held attempt through", "the_quest_gate_follows_the_hook_rules",
     [('                    try { Log(a); }\n                    catch (Exception e) { Faults++; try { LastFault = "log: " + e.GetType().Name + ": " + e.Message; } catch { } }   // the decision stands',
       "                    Log(a);")]),
    ("a gate that arms under CAMPAIGN", "with_a_canonical_save_loaded_every_gate_is_refused",
     [('if (campaign) return "REFUSED: the " + Kind', 'if (false) return "REFUSED: the " + Kind')]),
    ("an armed gate that holds on under CAMPAIGN", "with_a_canonical_save_loaded_every_gate_is_refused",
     [("if (campaign) { Release(", "if (false) { Release(")]),
    ("a queue held under CAMPAIGN", "with_a_canonical_save_loaded_every_gate_is_refused",
     [('if (campaign) return "REFUSED: the incident queue', 'if (false) return "REFUSED: the incident queue')]),
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
        print("FAIL scene gates UNMEASURED: %s" % e)
        return 1
    print("scene gates: %d of %d checks passed%s" % (len(CHECKS) - bad, len(CHECKS),
                                                   "" if "--no-plants" in argv else "; plants %s" % ("all red" if good else "NOT all red")))
    return 0 if bad == 0 and good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
