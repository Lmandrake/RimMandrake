## finding
`ORACLE_EXPERIMENT_SPIKE_1` (closed) built `mandrake.rm.oracle` as a thin
OpenAI-compatible HTTP client (`OracleHttpClient.cs`) with a Mod Settings API
key / base URL / model string (`OracleSettings.cs`), wired through
`OracleGameComponent.cs`. CLAUDE.md's "In-game LLM access is the Claude Code
CLI, never a hosted API key" (owner, 2026-09-05) explicitly supersedes this
exact design: *"no base URL, no model string, no API key field, no local
Ollama fallback"* — every mod that calls out to an LLM does it by shelling out
to `claude -p "<prompt>"` as a subprocess instead.

That ruling names the doc and the code to change but nobody ever turned it
into a queue item, so it sat as "owed" in handoff notes only
(`FOUNDRY_REBOOT_HANDOFF_202609070028.md` and others) with no tracked work.
Found via the standing code-review loop: `src/RimMandrake/Oracle/About/About.xml`
still describes the superseded design verbatim ("a thin OpenAI-compatible
client", "whatever endpoint is configured in Mod Settings ... a real
OpenAI-compatible cloud endpoint with an API key") — a shipped mod description
actively contradicting the owner's own standing doctrine.

## spec
Per CLAUDE.md's own note: **the two laws (text/menu authority only; the game
is whole with the LLM absent) and the async/timeout/kill-switch threading
shape are UNCHANGED — only the transport (HTTP → subprocess) moves.**

- Rebuild `OracleHttpClient.cs` (or replace it) to launch `claude -p "<prompt>"`
  via `System.Diagnostics.Process`, same off-tick `Task`-based async pattern
  already built, reading stdout instead of an HTTP response body.
- `OracleSettings.cs`: drop API key / base URL / model string fields; add
  whatever the subprocess path actually needs (e.g. a `claude` binary path
  override, if not always on PATH for the game process).
- 🔴 **Verify the exact invocation and output shape against a real local
  `claude -p` call before wiring it** — CLAUDE.md is explicit not to assume
  flags or JSON structure from its own note.
- New environment dependency this creates (already flagged in CLAUDE.md): the
  owner's machine must have Claude Code installed and logged in for any
  consumer to work — document this in About.xml, don't leave it implicit.
- Update `src/RimMandrake/Oracle/About/About.xml`'s description once the
  rewrite lands (or as part of the same commit) so it stops describing the
  superseded architecture.

## verify
```
PROVE   OracleGameComponent's "Test Ohm letter" debug action fires one real
        claude -p call and a letter is delivered (or the prescribed fallback
        fires on failure/timeout/reject, same as today)
EXPECT  a letter matching the register lint, OR the fallback text - never a
        raw HTTP-client code path being exercised
LIES    the selftest validator (no network call either way) passing proves
        nothing about the transport; only the live "Test Ohm letter" action does
```
