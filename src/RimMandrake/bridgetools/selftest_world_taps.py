#!/usr/bin/env python3
# selftest-timeout: 3600   (eleven harness builds of ~3 min each through winbuild, and selftest_bridge_hooks.py with its own C# build)
"""Selftest: the world tracks and the six world-event taps of BRIDGE v2.0 (JawaBenchWorldCore.cs, joined to the production
JawaBenchSceneTickCore.cs; the Verse half JawaBenchWorld.cs). Item RIMMANDRAKE_BUILD_WORLD_EVENT_TAPS_SECOND_FAMILY.
Page: design/specs/2026-11-23-bridge-v2/boundary.md §WORLD EVENT TAPS AND WORLD TRACKS; one test per promise there, 10 checks:

  1-6 the mental, quest, letter, message, fire and explosion taps each follow the six hook rules of HOOKS.md, and drop and
      count a record outside any run
  7 an attempt and a start are two records          8 a message is recorded before the rule that hides repeats
  9 the hook table check passes (selftest_bridge_hooks.py, with its C# units)
  10 the world tracks write on change, and their per-tick cost is in the result (a spec part that the build order's
     nine checks did not cover)

Each plant breaks one rule of a COPY of the world core and must turn its named check red.
An offline test proves the rules, never that a hook is connected in the game: the tap certificate ticket does that live.
No game, no bridge. Without dotnet.exe it FAILS as UNMEASURED.
Run: python3 src/RimMandrake/bridgetools/selftest_world_taps.py [--no-plants]"""
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
CORE = "JawaBenchWorldCore.cs"
VERSE = "JawaBenchWorld.cs"
PROJ = os.path.join(HERE, "WorldTapsSelfTest", "WorldTapsSelfTest.csproj")
N_UNITS = 9                     # fewer printed = the harness did not run whole


class Unmeasured(Exception):
    pass


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def units(core_text):
    """Build the harness with this world core, run it -> {unit: "ok" | "FAIL why"}."""
    import winbuild
    d = tempfile.mkdtemp(prefix="WorldCore_", dir=winbuild.BUILD_ROOT)
    log = os.path.join(winbuild.BUILD_ROOT, "selftest_world_taps.log")
    try:
        with open(os.path.join(d, CORE), "w", encoding="utf-8") as f:
            f.write(core_text)
        with open(log, "w") as lf:
            sys.stdout.flush()
            saved = os.dup(1)
            os.dup2(lf.fileno(), 1)
            try:
                rc, rec = winbuild.stage_build(PROJ, stage_name="WorldTapsSelfTest", extra=("-p:CoreDir=" + winbuild.win(d) + "\\",))
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
    dll = winbuild.staged_win(rec, os.path.dirname(PROJ)) + "\\bin\\Release\\net8.0\\WorldTapsSelfTest.dll"
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


def tap(g, rec, typ, pre, post):
    """The Verse hook pair of one tap holds the guard's two halves, calls its recorder, and is patched on its method."""
    return wired(VERSE, "Tp.%s.Admit(OnMain(), out __state.S)" % g, "Tp.%s.Commit(__state.S, __runOriginal)" % g, "Tp.%s(__state," % rec,
                 "typeof(%s)" % typ, "nameof(%s)" % pre, "nameof(%s)" % post)


def joined():
    """Every run gets the world tracks and the taps, and the run samples and closes them."""
    return both(wired("JawaBenchHands.cs", "JawaBenchWorld.Join(made, Host.MapId);"),
                wired("JawaBenchSceneTickCore.cs", "World.Sample(_row, tick, phase, all);", "(World != null ? "),
                wired(VERSE, "run.World = new K.Tracks(new Source(mapId), K.ClockMs, Tp);", "return r.EmitTap(rec, fields);"))


# ------------------------------------------------------------------------------------------------ the 10 checks
def t_the_mental_tap_follows_the_six_hook_rules():
    return both(tap("GMental", "RecordMental", "MentalStateHandler", "MentalPre", "MentalPost"), joined(), unit("mental_tap_follows_the_six_hook_rules"))


def t_the_quest_tap_follows_the_six_hook_rules():
    return both(tap("GQuest", "RecordQuest", "QuestManager", "QuestPre", "QuestPost"), unit("quest_tap_follows_the_six_hook_rules"))


def t_the_letter_tap_follows_the_six_hook_rules():
    return both(tap("GLetter", "RecordLetter", "LetterStack", "LetterPre", "LetterPost"), unit("letter_tap_follows_the_six_hook_rules"))


def t_the_message_tap_follows_the_six_hook_rules():
    return both(wired(VERSE, "Tp.GMessage.TryEnter(OnMain(), out __state.S)", "Tp.GMessage.Commit(__state.S, __runOriginal)", "Tp.RecordMessage(__state,",
                      "Tp.MessageExit(__state, __exception)", "nameof(MsgTargetPost)", "nameof(MsgTextPost)", "nameof(MsgObjPost)", "nameof(MsgFin)",
                      "typeof(Messages), \"\", new[] { typeof(string), typeof(LookTargets), typeof(MessageTypeDef), typeof(Quest), typeof(bool) }",
                      "typeof(Messages), \"\", new[] { typeof(string), typeof(LookTargets), typeof(MessageTypeDef), typeof(bool) }",
                      "typeof(Messages), \"\", new[] { typeof(string), typeof(MessageTypeDef), typeof(bool) }",
                      "typeof(Messages), \"\", new[] { typeof(Message), typeof(bool) }"),
                unit("message_tap_follows_the_six_hook_rules"))


def t_the_fire_tap_follows_the_six_hook_rules():
    return both(tap("GFire", "RecordFire", "Fire", "FirePre", "FirePost"), wired(VERSE, "Who(__instance.instigator)", "respawningAfterLoad);"),
                unit("fire_tap_follows_the_six_hook_rules"))


def t_the_explosion_tap_follows_the_six_hook_rules():
    return both(tap("GExplosion", "RecordExplosion", "GenExplosion", "BoomPre", "BoomPost"), wired(VERSE, "Who(instigator)"),
                unit("explosion_tap_follows_the_six_hook_rules"))


def t_an_attempt_and_a_start_are_two_records():
    return both(wired(VERSE, "__result, now != null"), unit("an_attempt_and_a_start_are_two_records"))


def t_a_message_is_recorded_before_the_rule_that_hides_repeats():
    return both(wired(VERSE, "__state.Ref = LastLive();", "!ReferenceEquals(now, st.Ref)"), unit("a_message_is_recorded_before_the_rule_that_hides_repeats"))


def t_the_hook_table_check_passes():
    p = subprocess.run([sys.executable, os.path.join(HERE, "selftest_bridge_hooks.py")], capture_output=True, text=True, timeout=1500)
    tail = [ln for ln in p.stdout.splitlines() if ln.startswith(("FAIL", "RESULT", "static audit", "C# units"))]
    if p.returncode == 0 and "RESULT PASS" in p.stdout:
        return "ok"
    if any("UNMEASURED" in ln for ln in tail):
        raise Unmeasured("selftest_bridge_hooks.py: " + " | ".join(tail)[-400:])
    return "FAIL selftest_bridge_hooks.py rc %d: %s" % (p.returncode, " | ".join(tail)[-600:])


def t_the_world_tracks_write_on_change_and_their_cost_is_in_the_result():
    return both(joined(), unit("the_world_tracks_write_on_change_and_their_cost_is_in_the_result"))


CHECKS = [t_the_mental_tap_follows_the_six_hook_rules, t_the_quest_tap_follows_the_six_hook_rules, t_the_letter_tap_follows_the_six_hook_rules,
          t_the_message_tap_follows_the_six_hook_rules, t_the_fire_tap_follows_the_six_hook_rules, t_the_explosion_tap_follows_the_six_hook_rules,
          t_an_attempt_and_a_start_are_two_records, t_a_message_is_recorded_before_the_rule_that_hides_repeats, t_the_hook_table_check_passes,
          t_the_world_tracks_write_on_change_and_their_cost_is_in_the_result]

# ------------------------------------------------------------------------------------------------ plants
PLANTS = [
    ("a mental start that is not a record of its own", "an_attempt_and_a_start_are_two_records",
     [('if (started) Record(st, "mental_start",', 'if (false) Record(st, "mental_start",')]),
    ("a message tap that records only what the repeat rule lets through", "a_message_is_recorded_before_the_rule_that_hides_repeats",
     [("if (st.S.Depth > 1) { Inner++; return; }", "if (st.S.Depth > 1 || !shown) { Inner++; return; }")]),
    ("a message written twice by the nested overloads", "message_tap_follows_the_six_hook_rules",
     [("if (st.S.Depth > 1) { Inner++; return; }", "")]),
    ("an entry ordinal taken at the postfix", "mental_tap_follows_the_six_hook_rules",
     [('sink.EmitTap(rec, "\\"ord\\":" + st.Ord + ","', 'sink.EmitTap(rec, "\\"ord\\":" + (++_ord) + ","')]),
    ("a record outside the run counted as written", "fire_tap_follows_the_six_hook_rules",
     [("if (seq == -2) Outside++;", "if (seq == -2) Records++;")]),
    ("a refused quest read as added", "quest_tap_follows_the_six_hook_rules",
     [('",\\"added\\":" + B(added)', '",\\"added\\":" + B(true)')]),
    ("a delayed letter read as shown now", "letter_tap_follows_the_six_hook_rules",
     [('",\\"queued\\":" + B(delay > 0)', '",\\"queued\\":" + B(false)')]),
    ("a fire restored by a load taken as a start", "fire_tap_follows_the_six_hook_rules",
     [("if (loaded) { Loaded++; return; }", "if (loaded) Loaded++;")]),
    ("an instigator that never names a pawn", "explosion_tap_follows_the_six_hook_rules",
     [('return !Has ? "none" : Pawn ? "pawn" : "thing";', 'return !Has ? "none" : "thing";')]),
    ("a world track written at every sample", "the_world_tracks_write_on_change_and_their_cost_is_in_the_result",
     [("if (!force && JawaBenchCondCore.SameValue(_cur[f], _last[f])) continue;", "")]),
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
        print("FAIL world taps UNMEASURED: %s" % e)
        return 1
    print("world taps: %d of %d checks passed%s" % (len(CHECKS) - bad, len(CHECKS),
                                                   "" if "--no-plants" in argv else "; plants %s" % ("all red" if good else "NOT all red")))
    return 0 if bad == 0 and good else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
