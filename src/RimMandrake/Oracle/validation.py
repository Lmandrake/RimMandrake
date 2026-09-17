"""validation.py -- modcheck suite for RimMandrake Oracle (mandrake.rm.oracle).

Read whole before writing this: `OracleClient.cs`, `OracleGameComponent.cs`,
`OracleValidator.cs`, `OracleSettings.cs`, `OracleRegisterBlocks.cs`,
`DebugActions_Oracle.cs`, the walk doc, and `Transient/bench_tools_dump.json`
for the three bridge tools this mod names (`jawa/oracle_selftest`,
`jawa/oracle_configure`, `jawa/oracle_test_ohm_letter`).

`git status --porcelain src/RimMandrake/Oracle/` was checked before touching
anything here: clean. `ORACLE_FALLBACK_UNVALIDATED_1`
(commit `81325f011`, tonight) already landed -- `DeliverFallback` now
re-validates `fallbackText` through `OracleValidator.TryValidateOhm` and
ships the hardcoded `SafeFallbackText` if even the CALLER's fallback string
is rejected, instead of shipping a rejected string verbatim.

WHAT THIS MOD IS: no XML defs at all (About.xml ships none); one Mod
Settings boolean toggle (`enabled`, the kill switch) plus three tunables
that are not on/off toggles (`claudeCliPath`, `timeoutSeconds`,
`godsBudgetPerDay`) -- `suite.toggles = ["enabled"]`, matching the
briefing's rule that only real checkbox toggles go in that list.
`OracleSettings`'s fields are INSTANCE (not `public static`, unlike Pits/
RimProperty/RustChrome... wait, RustChrome's `themeEnabled` is ALSO
instance) -- `t.set_setting` (BRIDGE_STATIC_SETTINGS_FIELDS_1's
static-then-instance fallback) reaches it either way.

TWO REAL, MOD-SPECIFIC STALENESS FINDINGS, same register CLAUDE.md records
for RustChrome tonight -- found by reading the CURRENT source against BOTH
the walk doc and the bridge tool dump, not assumed from either alone:

  1. THE WALK DOC'S OWN QUOTED FALLBACK STRING IS NOW STALE. The walk doc
     (written 2026-09-16, one day before `81325f011`) quotes
     `DebugActions_Oracle.cs:46` as shipping fallback text
     `"[FALLBACK] My spine settles where you touched it. Good work, small
     hands."` and files two `## north star` `must read` lines as "fails
     today" against that bracketed marker
     (`ohm_fallback_is_in_register`, `never_engineering_marker_in_player_
     text`). Reading the CURRENT file: `TestOhmLetter`'s fallback argument
     (line 47) is now `"My spine settles where you touched it. Good work,
     small hands."` -- no bracket. Those two north-star lines' "fails
     today" evidence is stale (the north star itself is DRAFT and binds
     nothing regardless, so this is not "corrected" here, only noted, per
     CLAUDE.md's own ruling on DRAFT sections).

  2. THE BRIDGE TOOL DUMP DESCRIBES THE PRE-REWRITE ORACLE. `jawa/
     oracle_configure`'s own schema (`Transient/bench_tools_dump.json`)
     still exposes `baseUrl`/`model`/`apiKey` params and its description
     talks about "the mock-endpoint quicktest gate" and a "127.0.0.1/
     localhost baseUrl" -- the shape of the OLD OpenAI-compatible HTTP
     client (`OracleHttpClient`, superseded per CLAUDE.md's "In-game LLM
     access is the Claude Code CLI, never a hosted API key", 2026-09-05).
     Current `OracleSettings.cs` has NO `baseUrl`/`model`/`apiKey` fields
     at all -- only `enabled`, `claudeCliPath`, `timeoutSeconds`,
     `godsBudgetPerDay`. Whether `jawa/oracle_configure`'s own C#
     implementation (JawaBench, not this mod, out of this task's scope)
     still compiles against a field set that no longer exists, or silently
     no-ops those three parameters, is UNMEASURED -- either way it has NO
     PARAMETER for `claudeCliPath` at all, so it cannot be used for the
     bad-CLI-path component below regardless. Every setting change in this
     suite therefore goes through the generic `t.set_setting` verb
     (`jawa/mod_settings_field`), never `jawa/oracle_configure`.
     `jawa/oracle_test_ohm_letter`'s own `fallback` PARAMETER DEFAULT is
     also the stale bracketed string -- every call below passes an
     explicit clean `fallback=` argument rather than relying on that
     default, so a run of this suite is never itself the thing that
     exercises the SafeFallbackText substitution path by accident.

A THIRD DISCREPANCY, not a staleness question (both sides are CURRENT,
they just disagree): `jawa/oracle_selftest`'s own description says it runs
"5 canned good/bad strings", but `DebugActions_Oracle.SelftestValidator`
(the walk doc's own step 2 target, run via `rimworld/execute_debug_action`)
has SIX cases in its array (clean / self-unification tell / names Zizzik /
empty / over length cap / bracket marker). Whether the JawaBench tool
carries its own, separate, shorter copy of the case list (plausible -- nothing
here suggests the bridge tool calls the debug action rather than
`OracleValidator.TryValidateOhm` directly with its own cases) was not
traceable from this mod's own source (JawaBench is a different project).
`selftest_lint_no_network` below therefore asserts the CONSISTENCY the
tool's own response owes (`passCount + failCount == len(cases)`,
`failCount == 0`), not a hardcoded 5 or 6 -- asserting either number
against the wrong tool would be exactly the guess CLAUDE.md warns against.

REAL, UNMEASURED RESPONSE-SHAPE RISK: `rimworld/list_letters`'s own
`outputSchema` in the tool dump is `{}` -- only its prose description
("native letter ids, semantic letter content") is known, not the actual
JSON key names. `_letter_texts()` below guesses `letters`/`text` as the
container/field names (the vocabulary the description itself uses); this
is the single most likely first-live-run correction in this file, per the
walk doc's own anti-guessing note ("Capture from the letter stack, never
from the def").

Still not proven / likely first-live-run corrections:
  1. `live_transport_completes`'s pass criterion is deliberately weak (a
     register-clean letter lands, and it is NOT the hardcoded
     `SafeFallbackText`) rather than "the model's own words arrived" --
     whether the Claude Code CLI is installed and logged in on whichever
     machine actually runs `modcheck run Oracle` is an environment fact
     this suite cannot control (CLAUDE.md: "a fact about his machine, not
     a config value"), so a component that demanded a genuine network
     success would be flaky by design rather than by bug.
  2. `godsCallsToday`/`lastBudgetResetDay` are private instance fields on
     the live `OracleGameComponent` with no bridge getter -- the budget
     mechanism itself (three real `RequestOhmLetter` calls across this
     suite's three call-making chains, safely under the bumped
     `godsBudgetPerDay=10`) is exercised but never independently read
     back; only inferred from "a call still landed a letter."
  3. `wait_ticks` budgets below are estimates (the async round trip is a
     `Task.Run` plus one `ConcurrentQueue` drain on the next
     `GameComponentTick`, which should be fast, but the LIVE call can take
     up to `timeoutSeconds` (60s default) if the CLI hangs) -- untested
     against real tick rates, same register as every other suite's own
     first-live-run caveat on this point.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("Oracle")
suite.toggles = ["enabled"]

SETTINGS_TYPE = "RimMandrake.Oracle.OracleSettings"

# Matches DebugActions_Oracle.cs:47's CURRENT fallback argument exactly (no
# bracket -- see module docstring finding #1). Passed explicitly to every
# jawa/oracle_test_ohm_letter call below so this suite never accidentally
# relies on that tool's own STALE bracketed default parameter.
CLEAN_FALLBACK = "My spine settles where you touched it. Good work, small hands."
SAFE_FALLBACK = ("The old machines hum on, patient, waiting for hands that "
                  "have not yet come.")   # OracleGameComponent.SafeFallbackText


def _letter_texts(t):
    """Best-guess field names against `rimworld/list_letters`' EMPTY
    outputSchema (see module docstring) -- `letters`/`text` are the nouns
    the tool's own description uses, nothing more certain was found."""
    r = t.bridge_call("rimworld/list_letters", limit=40)
    rows = (r or {}).get("letters") or (r or {}).get("results") or []
    return [row.get("text") or "" for row in rows]


@suite.chain("selftest_lint_no_network")
def selftest_lint_no_network(t):
    """`jawa/oracle_selftest` -- pure register-lint, no subprocess, no map
    state, safe to run with the kill switch in either position (the lint
    itself has nothing to do with `enabled`). See module docstring for why
    this asserts internal consistency rather than a hardcoded case count."""
    t.clear_area(size=8)   # no map state involved; keeps the runner's
                            # evidence/screenshot machinery uniform

    with t.component("register_lint_all_pass", beyond_toggle=True):
        r = t.bridge_call("jawa/oracle_selftest")
        if t._guard():
            body = r or {}
            cases = body.get("cases") or []
            pass_count = body.get("passCount")
            fail_count = body.get("failCount")
            if not body.get("success", True):
                raise ExpectationFailed(
                    "jawa/oracle_selftest reported success=false: %r" % body)
            if fail_count != 0:
                raise ExpectationFailed(
                    "jawa/oracle_selftest failCount = %r, expected 0 -- "
                    "cases: %r" % (fail_count, cases))
            if cases and pass_count is not None and pass_count + fail_count != len(cases):
                raise ExpectationFailed(
                    "jawa/oracle_selftest passCount+failCount (%r+%r) != "
                    "len(cases) (%d) -- %r"
                    % (pass_count, fail_count, len(cases), cases))
        t.screenshot()


@suite.chain("kill_switch_blocks_call")
def kill_switch_blocks_call(t):
    """`enabled=False` makes `RequestOhmLetter` call `DeliverFallback`
    DIRECTLY on the calling thread (no `Task.Run`, no queue) -- read from
    `OracleGameComponent.cs`'s own early-return, confirmed before writing
    this rather than assumed. So the delivered letter should be `t`'s exact
    `CLEAN_FALLBACK` text with NO tick wait needed for the async round
    trip. Restores `enabled=True` at the end so later chains in this suite
    can make a real call."""
    t.clear_area(size=8)

    with t.component("kill_switch_off_ships_fallback_synchronously", toggle="enabled"):
        t.set_setting(SETTINGS_TYPE, {"enabled": False})
        before = _letter_texts(t)
        t.bridge_call("jawa/oracle_test_ohm_letter",
                      context="modcheck kill-switch probe", fallback=CLEAN_FALLBACK)
        t.expect_log_contains("RimMandrake.Oracle: falling back", field=None, value=None)
        if t._guard():
            after = _letter_texts(t)
            new_texts = [x for x in after if x not in before]
            if CLEAN_FALLBACK not in new_texts:
                raise ExpectationFailed(
                    "no new letter with text=%r after a kill-switch-off call "
                    "-- new letters seen: %r" % (CLEAN_FALLBACK, new_texts))
        t.screenshot()
        t.set_setting(SETTINGS_TYPE, {"enabled": True})


@suite.chain("bad_cli_path_falls_back")
def bad_cli_path_falls_back(t):
    """`claudeCliPath` pointed at a file that cannot exist -- `OracleClient.
    Candidates()` takes an explicit override "at its word" (its own doc
    comment), so `Invoke` throws `Win32Exception` (caught, no retry
    candidates left) then `RunOnce` throws `FileNotFoundException`, which
    `RunWithRetry` re-throws without retrying (a missing binary "will be
    just as missing", per its own comment) -- lands in
    `OracleGameComponent`'s `catch (Exception e)` and enqueues
    `DeliverFallback` for the next tick. Bumps `godsBudgetPerDay` to 10
    first (default 3, and this suite makes 2 real-call chains after this
    one -- see module docstring item 2) and restores the CLI path to blank
    afterward so later chains resolve it normally."""
    t.clear_area(size=8)
    t.set_setting(SETTINGS_TYPE, {"enabled": True, "godsBudgetPerDay": 10})

    with t.component("missing_binary_ships_fallback", beyond_toggle=True):
        t.set_setting(SETTINGS_TYPE,
                      {"claudeCliPath": "C:\\does\\not\\exist\\claude_modcheck_probe.exe"})
        before = _letter_texts(t)
        t.bridge_call("jawa/oracle_test_ohm_letter",
                      context="modcheck bad-path probe", fallback=CLEAN_FALLBACK)
        t.wait_ticks(300)   # Task.Run + one GameComponentTick drain; no real
                             # subprocess wait on this path (Win32Exception is
                             # near-instant), so this is generous, not tight
        if t._guard():
            after = _letter_texts(t)
            new_texts = [x for x in after if x not in before]
            if CLEAN_FALLBACK not in new_texts:
                raise ExpectationFailed(
                    "no new letter with text=%r after pointing claudeCliPath "
                    "at a nonexistent file -- new letters seen: %r"
                    % (CLEAN_FALLBACK, new_texts))
        t.screenshot()
        t.set_setting(SETTINGS_TYPE, {"claudeCliPath": ""})


@suite.chain("live_transport_completes")
def live_transport_completes(t):
    """The one step the walk doc itself says "nothing offline can prove" --
    a real `claude -p` child process, `claudeCliPath` blank (PATH
    resolution). Whether the CLI is actually installed/logged in on the
    machine running this suite is an environment fact this suite cannot
    control (module docstring item 1), so the pass bar is deliberately
    weaker than "the model's own words arrived": a register-clean letter
    lands at all, and it is NOT the hardcoded `SafeFallbackText` (which
    would mean even OUR OWN clean fallback string got rejected -- a real
    bug in `OracleValidator`, since `CLEAN_FALLBACK` has no bracket, no
    self-unification tell, and does not name Zizzik). Restores
    `godsBudgetPerDay` to its 3 default at the end, since this is the last
    chain in the suite to spend budget."""
    t.clear_area(size=8)
    t.set_setting(SETTINGS_TYPE, {"enabled": True})

    with t.component("call_completes_register_clean", beyond_toggle=True):
        before = _letter_texts(t)
        t.bridge_call(
            "jawa/oracle_test_ohm_letter",
            context="The crew just repaired a damaged hull plate near the "
                    "reactor. React to it in your voice.",
            fallback=CLEAN_FALLBACK)
        t.wait_ticks(1200)   # up to timeoutSeconds=60s if the CLI hangs;
                              # generous, unmeasured against real tick rate
        if t._guard():
            after = _letter_texts(t)
            new_texts = [x for x in after if x not in before]
            if not new_texts:
                raise ExpectationFailed(
                    "no new letter landed at all after a live-transport call "
                    "-- either the async task never enqueued a delivery, or "
                    "it is still pending past this suite's wait budget")
            if SAFE_FALLBACK in new_texts:
                raise ExpectationFailed(
                    "delivered SafeFallbackText -- CLEAN_FALLBACK (%r) was "
                    "itself rejected by OracleValidator, which should not "
                    "happen for a bracket-free, non-taboo, under-length "
                    "string" % CLEAN_FALLBACK)
        t.screenshot()
        t.set_setting(SETTINGS_TYPE, {"godsBudgetPerDay": 3})
