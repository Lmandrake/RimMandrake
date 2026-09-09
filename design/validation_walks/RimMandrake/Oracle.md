# RimMandrake: Oracle — validation walk
subject: src/RimMandrake/Oracle  (packageId `mandrake.rm.oracle`)
deps: none (loadAfter Ludeon.RimWorld only)
list: minimal
status-hint: in-game LLM wiring — a register-lint selftest that launches nothing, plus one live-call debug action delivering an Ohm letter through `OracleGameComponent`, gated entirely behind two Debug Actions Menu entries, opt-in via Mod Settings, with a global kill switch. The transport is the Claude Code CLI as a child process (`claude -p`, `OracleClient.cs`), so there is no API key, endpoint or model setting to configure and the environment dependency is that the machine has Claude Code installed and logged in. This mod ships NO XML defs — walk built from its own C# log strings and the one bridge tool named for it.

## must be true
- "Selftest validator" runs the register lint against canned good/bad text with NO network call and logs a pass/fail/total tally that must show 0 unexpected failures on the canned cases.
- "Test Ohm letter" fires one real async call through `OracleGameComponent`; it is fire-and-forget (the tool/debug action returns immediately) and the letter lands on the letter stack within a few ticks — either the model's text (if it passes the register lint) or the prescribed fallback (call fails, times out, or output rejected), never a raw unfiltered subprocess response.
- With the Claude Code CLI absent, logged out, or pointed at a bad path in Mod Settings, the call must fall back silently rather than error the game — and no console window may flash over the game while a call runs.
- The global kill switch, when set, must prevent "Test Ohm letter" from making any call at all.
- No Harmony patch and no def patch ships in this mod — it must not alter any vanilla or third-party def.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.oracle" (this mod ships no defs to break, but the assembly must still load clean)
2. [B] rimworld/execute_debug_action `{path naming "RimMandrake.Oracle/Selftest validator (no network call)"}` → Player.log line `"RimMandrake.Oracle selftest: <pass> pass, <fail> fail, out of <cases> cases"` with `fail` = 0
3. [B] jawa/oracle_test_ohm_letter `{}` with the Mod Settings CLI path deliberately set to a nonexistent file → tool returns immediately; poll `rimworld/list_letters` or `rimworld/get_game_info` until a new letter appears; expect it to be the PRESCRIBED FALLBACK text, never an error dialog or a stuck async task
4. [B] clear that path back to blank (so the CLI resolves normally) and run jawa/oracle_test_ohm_letter again → expect the model's own text this time, still register-lint-passed. This is the ONLY step that proves the transport; nothing offline can
5. [D]/[L] toggle the global kill switch on (via whatever Mod Settings field `OracleSettings.cs` exposes — confirm the field name with `mcp__rimsage__read_csharp_symbol OracleSettings` before writing the concrete check) and repeat step 3 → expect NO new letter and a log line confirming the kill switch blocked the call, not silence that could equally mean "still pending"

## anti-guessing notes
- `jawa/oracle_test_ohm_letter` is cited verbatim from `Transient/bench_tools_dump.json`.
- The transport is `OracleClient.cs` launching `claude -p` (ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1, built 2026-09-08 against the owner's 2026-09-05 ruling). A call "succeeds" when the child exits 0 with non-empty stdout — stderr carries warnings on perfectly good runs and must never be read as failure. The 2.1.228 binary on the game machine and this checkout's 2.1.266 do not accept the same flags, so a call that suddenly fails everywhere is worth checking against `claude --version` on the game machine before anything else.
- No [S] line: the letter TEXT's tone/register is exactly what the selftest lint already checks mechanically; nothing here needs a human eyeball this pass.
