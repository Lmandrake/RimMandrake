"""validation.py -- modcheck suite for Load Tracer (local)
(mandrake.rm.loadtracer).

Run with:

    python.exe src/RimMandrake/Utils/modcheck/cli.py run LoadTracer

Grounded in `Source/LoadTracer.cs` (the whole file -- ~100 lines, read in
full) and its own top-of-file comment. No `About.xml` Mod Settings class
exists (`suite.toggles = []`): this is a diagnostic instrument for
COLD_LOAD_STALL_INTERMITTENT_1, "not player-facing content", meant for
removal once the stall is attributed, per its own description.

*** THE CENTRAL FINDING THIS PASS MADE, WHICH SHAPES EVERYTHING BELOW ***

`jawa/drain_log` -- the ONLY log-reading bridge tool this suite family has
ever used (every other 17 suites) -- reads `Log.Messages`
(`JawaBenchTerrainTools.cs:1857`, `var msgs = Log.Messages.ToList();`). That
is Verse's OWN in-memory message list, the exact thing capped at 1000
entries that `LoadTracer.cs`'s own top comment says its per-type trace
lines are designed to bypass: "Per-type lines go through
UnityEngine.Debug.Log DIRECTLY: Verse.Log stops logging after its message
cap (1000), and a 592-mod trace would blow through it mid-list." Calling
`UnityEngine.Debug.Log` directly (instead of `Verse.Log.Message`) skips the
`Log.Messages` recording step entirely, while Unity's own log handler still
writes the text to the Player.log FILE regardless of source.

**Consequence: `jawa/drain_log` is structurally blind to every one of this
mod's own `[LoadTracer]` per-type/bracket trace lines, by the mod's own
deliberate design.** Every walk-doc assertion in this file is an [L]
Player.log check for exactly this reason (the walk doc has zero [B] bridge
steps at all) -- but simply calling `t.expect_log_contains`/
`jawa/drain_log` the way every other suite does would silently test
NOTHING here, an invented-pass risk this suite refuses to take. The trace-
line chains below therefore read Player.log the FILE directly
(`game_paths.PLAYER_LOG`), with NO bridge/session call at all -- the same
register KotORBandolierNorthFix's offline PIL chains use, for the same
reason (the claim is checkable without a live session, and the bridge's own
instrument cannot see it anyway).

ONE line is the exception and DOES use Verse.Log (and is therefore
bridge-visible): the ctor's own catch-block, `Log.Error("[LoadTracer]
failed to arm - tracing is ABSENT this load: " + ex)`. That single failure
path is checked via `jawa/drain_log` in the one bridge-dependent chain
below.

A SECOND FINDING, from reading `JawaBenchHarmonyInspect.cs` directly rather
than trusting a sibling suite: `jawa/harmony_patches`' REAL signature is
`(typeName, methodName=null)` -- there is no `harmonyId` parameter at all.
`Aftermath/validation.py`'s own `harmony_patches_registered` chain calls it
as `t.bridge_call("jawa/harmony_patches", harmonyId=HARMONY_ID)`, which
(per that mod's own gap #3, "read from its tool Description text, not a
live call") looks like it may be passing a parameter the tool does not
accept. This suite calls it correctly, by `typeName`/`methodName`, and
checks the returned patch list's `owner` field for `mandrake.rm.loadtracer`
-- not repeating the (possibly wrong) sibling pattern uncritically.

Still not proven / structurally offline-only:
  1. Walk step 5 (deliberately reproducing a KNOWN-STALLING large mod list
     to confirm the last log line names the stuck site) is a manual
     diagnostic scenario -- automating a genuine stall is out of scope for
     a smoke suite that must complete.
  2. The trace-line chains below assume the CURRENT `Player.log` is from
     the load `modcheck run LoadTracer` itself just triggered (the
     runner's own swap-to-test-list + restart, per `runner.py`). Read
     cold, before any such restart, `Player.log` will correctly NOT
     contain `[LoadTracer]` lines (confirmed this pass: neither the
     current `Player.log` nor `Player-prev.log` contains the string, since
     neither load had this mod active) -- that is the walk doc's own step
     1 semantics ("its absence means tracing is OFF for this load"), not a
     suite bug.
  3. `jawa/harmony_patches`' exact result shape for `prefixes`/`postfixes`
     entries' `owner` field was read from its `ResultDescription` string,
     not a live call -- the substring check below is defensive for that
     reason, same register Aftermath's own chain already uses.
"""
import os

from modcheck import Suite, ExpectationFailed

suite = Suite("LoadTracer")
suite.toggles = []   # no ModSettings class at all -- see docstring

HARMONY_ID = "mandrake.rm.loadtracer"
ARMED_LINE = "[LoadTracer] armed: CallAll per-type trace + FloatMenuMakerMap.Init/BakeStaticAtlases brackets"
FAILED_TO_ARM_NEEDLE = "[LoadTracer] failed to arm"


def _player_log_path():
    import sys
    utils = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "RimMandrake", "Utils")
    if utils not in sys.path:
        sys.path.insert(0, utils)
    from game_paths import PLAYER_LOG
    return PLAYER_LOG


def _read_player_log():
    path = _player_log_path()
    if not os.path.isfile(path):
        raise ExpectationFailed("Player.log not found at %s" % path)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


@suite.chain("harmony_patch_group_registered")
def harmony_patch_group_registered(t):
    """Bridge-dependent (the one chain in this suite that needs a live
    session): confirms the 3 methods LoadTracer's ctor patches
    (`StaticConstructorOnStartupUtility.CallAll`, `FloatMenuMakerMap.Init`,
    `GlobalTextureAtlasManager.BakeStaticAtlases`) each carry a patch owned
    by `mandrake.rm.loadtracer`, and that the ONE Verse.Log-visible failure
    line (`[LoadTracer] failed to arm`) is absent from the error log."""
    with t.component("three_methods_patched_by_loadtracer", beyond_toggle=True):
        targets = [
            ("StaticConstructorOnStartupUtility", "CallAll"),
            ("FloatMenuMakerMap", "Init"),
            ("GlobalTextureAtlasManager", "BakeStaticAtlases"),
        ]
        misses = []
        for type_name, method_name in targets:
            r = t.bridge_call("jawa/harmony_patches", typeName=type_name,
                              methodName=method_name)
            if not r or HARMONY_ID not in repr(r):
                misses.append("%s.%s: %r does not mention owner %r"
                              % (type_name, method_name, r, HARMONY_ID))
        if misses:
            raise ExpectationFailed(
                "%d/%d patch targets missing %r as an owner: %r"
                % (len(misses), len(targets), HARMONY_ID, misses))

    with t.component("no_failed_to_arm_error", beyond_toggle=True):
        r = t.bridge_call("jawa/drain_log", limit=200, errorsOnly=True,
                          contains=FAILED_TO_ARM_NEEDLE)
        msgs = [m.get("text", "") for m in ((r or {}).get("messages") or [])]
        if msgs:
            raise ExpectationFailed(
                "'%s' found in the error log -- tracing is ABSENT this "
                "load, and every other check in this suite is meaningless "
                "per the mod's own design: %r" % (FAILED_TO_ARM_NEEDLE, msgs))


@suite.chain("cold_load_trace_well_formed")
def cold_load_trace_well_formed(t):
    """Walk steps 1-3, read from the Player.log FILE directly -- no
    bridge/session call at all (see module docstring on why
    `jawa/drain_log` cannot see any of these lines). Verifies the armed
    line precedes CallAll begin, the ctor i/N sequence is contiguous
    1..N with no gaps or duplicates, and CallAll complete follows the
    last ctor line."""
    with t.component("armed_and_ctor_sequence_contiguous", beyond_toggle=True):
        text = _read_player_log()
        if ARMED_LINE not in text:
            raise ExpectationFailed(
                "'%s' not found in Player.log -- tracing is OFF for this "
                "load (walk doc step 1: 'no other check in this file means "
                "anything')" % ARMED_LINE)
        armed_pos = text.index(ARMED_LINE)
        begin_needle = "[LoadTracer] CallAll begin"
        if begin_needle not in text:
            raise ExpectationFailed("'%s' not found in Player.log" % begin_needle)
        if text.index(begin_needle) < armed_pos:
            raise ExpectationFailed(
                "'%s' appears BEFORE '%s' in Player.log -- wrong order"
                % (begin_needle, ARMED_LINE))

        import re
        count_m = re.search(r"\[LoadTracer\] CallAll: (\d+) static ctors to run", text)
        if not count_m:
            raise ExpectationFailed(
                "'[LoadTracer] CallAll: <N> static ctors to run' line not found")
        n_expected = int(count_m.group(1))

        ctor_lines = re.findall(r"\[LoadTracer\] ctor (\d+)/(\d+):", text)
        indices = [int(i) for i, n in ctor_lines if int(n) == n_expected]
        if not indices:
            raise ExpectationFailed(
                "no '[LoadTracer] ctor i/%d:' lines found at all" % n_expected)
        expected_seq = list(range(1, n_expected + 1))
        if indices != expected_seq:
            missing = sorted(set(expected_seq) - set(indices))
            dupes = [i for i in set(indices) if indices.count(i) > 1]
            raise ExpectationFailed(
                "ctor index sequence is not contiguous 1..%d: missing=%r "
                "duplicated=%r (got %d lines, expected %d)"
                % (n_expected, missing, dupes, len(indices), n_expected))

        complete_needle = "[LoadTracer] CallAll complete"
        if complete_needle not in text:
            raise ExpectationFailed(
                "'%s' not found -- the trace started but never reported "
                "completion (this IS the diagnostic payoff for a stalled "
                "load, but a healthy smoke run should reach it)" % complete_needle)
        last_ctor_pos = text.rindex(
            "[LoadTracer] ctor %d/%d:" % (n_expected, n_expected))
        if text.index(complete_needle) < last_ctor_pos:
            raise ExpectationFailed(
                "'%s' appears before the last ctor line -- wrong order"
                % complete_needle)

        fallback_fired = "[LoadTracer] type enumeration FAILED" in text
        t._record("type-enumeration fallback fired: %s (informational -- "
                  "the mod's own graceful-degradation path, not a failure "
                  "of THIS mod if it happened)" % fallback_fired, True)


@suite.chain("float_menu_and_bake_brackets_complete")
def float_menu_and_bake_brackets_complete(t):
    """Walk step 4, same offline file-read register. Each bracket's
    'begin' must be followed (order-preserving) by its own 'done' --
    checked independently of the ctor trace chain so a failure here
    localizes to the bracket, not the whole cold-load trace."""
    with t.component("both_bracket_pairs_complete", beyond_toggle=True):
        text = _read_player_log()
        pairs = [
            ("[LoadTracer] FloatMenuMakerMap.Init begin",
             "[LoadTracer] FloatMenuMakerMap.Init done"),
            ("[LoadTracer] BakeStaticAtlases begin",
             "[LoadTracer] BakeStaticAtlases done"),
        ]
        misses = []
        for begin, done in pairs:
            if begin not in text:
                misses.append("%r missing entirely" % begin)
                continue
            if done not in text:
                misses.append("%r has no matching %r -- if this is the "
                              "LAST line in the file, this bracket is "
                              "exactly where a stalled load got stuck"
                              % (begin, done))
                continue
            if text.index(done) < text.index(begin):
                misses.append("%r appears before %r -- wrong order" % (done, begin))
        if misses:
            raise ExpectationFailed(
                "%d/%d bracket pair(s) incomplete: %r" % (len(misses), len(pairs), misses))
