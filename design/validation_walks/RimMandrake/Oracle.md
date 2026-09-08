# RimMandrake: Oracle — validation walk
subject: src/RimMandrake/Oracle  (packageId `mandrake.rm.oracle`)
deps: none (loadAfter Ludeon.RimWorld only)
list: minimal
status-hint: in-game LLM wiring spike (ORACLE_EXPERIMENT_SPIKE_1) — a register-lint selftest with no network call, plus one live-call debug action delivering an Ohm letter through `OracleGameComponent`, gated entirely behind two Debug Actions Menu entries, opt-in via Mod Settings, defaults to a blank API key (silent fallback) with a global kill switch. This mod ships NO XML defs — walk built from its own C# log strings and the one bridge tool named for it.

## must be true
- "Selftest validator" runs the register lint against canned good/bad text with NO network call and logs a pass/fail/total tally that must show 0 unexpected failures on the canned cases.
- "Test Ohm letter" fires one real async call through `OracleGameComponent`; it is fire-and-forget (the tool/debug action returns immediately) and the letter lands on the letter stack within a few ticks — either the model's text (if it passes the register lint) or the prescribed fallback (call fails, times out, or output rejected), never a raw unfiltered network response.
- With a blank API key in Mod Settings, the call must fall back silently rather than error the game.
- The global kill switch, when set, must prevent "Test Ohm letter" from making any call at all.
- No Harmony patch and no def patch ships in this mod — it must not alter any vanilla or third-party def.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.oracle" (this mod ships no defs to break, but the assembly must still load clean)
2. [B] rimworld/execute_debug_action `{path naming "RimMandrake.Oracle/Selftest validator (no network call)"}` → Player.log line `"RimMandrake.Oracle selftest: <pass> pass, <fail> fail, out of <cases> cases"` with `fail` = 0
3. [B] jawa/oracle_test_ohm_letter `{}` with Mod Settings at the default blank API key → tool returns immediately; poll `rimworld/list_letters` or `rimworld/get_game_info` until a new letter appears; expect it to be the PRESCRIBED FALLBACK text (blank key = no real call fired), never an error dialog or a stuck async task
4. [B] (if a local mock stub / 127.0.0.1 baseUrl is configured per the tool's own description) jawa/oracle_test_ohm_letter again → expect the model's own text this time, still register-lint-passed
5. [D]/[L] toggle the global kill switch on (via whatever Mod Settings field `OracleSettings.cs` exposes — confirm the field name with `mcp__rimsage__read_csharp_symbol OracleSettings` before writing the concrete check) and repeat step 3 → expect NO new letter and a log line confirming the kill switch blocked the call, not silence that could equally mean "still pending"

## anti-guessing notes
- `jawa/oracle_test_ohm_letter` is cited verbatim from `Transient/bench_tools_dump.json`.
- Per CLAUDE.md's Oracle note, the transport this build's code actually runs today is still the original OpenAI-compatible HTTP client (`OracleHttpClient.cs`) — the `claude -p` CLI rewrite has NOT landed. This walk targets the code AS IT STANDS; re-author it once `OracleClient` is rebuilt against the CLI transport (owner ruling 2026-09-05), since the concrete mechanics of "what counts as a call succeeding" will change.
- No [S] line: the letter TEXT's tone/register is exactly what the selftest lint already checks mechanically; nothing here needs a human eyeball this pass.
