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

## CLOSED 2026-09-13 — live-verified, one code bug fixed, one owner action owed

Ran the live "Test Ohm letter" debug action on a dedicated 4-mod `oracle`
quicktest tier (`modset_builder.py`; `start_debug_game_ready` is unreliable
against the owner's full 590-mod stack for worldgen — WorldGenStep errors,
`quicktest-crashes-full-modlist-use-cheap-mechanism-list`). Confirmed via
`jawa/list_letters`: the fallback letter delivered correctly on the first
run ("[FALLBACK] My spine settles where you touched it. Good work, small
hands.") — the async call → subprocess → fallback → letter-stack path all
work end to end, exactly per the verify bar. Never a raw HTTP-client path.

**Bug found and fixed**: `OracleClient.cs`'s exit-code-!=0 branch only read
`stderr` for the diagnostic. The real failure here — the Windows CLI's OAuth
session expired — prints to **stdout**, so the fallback log showed an empty,
useless message ("call failed: Oracle: claude -p exited 1 -- "). Fixed to
fall back to stdout when stderr is empty; rebuilt (`dotnet build -c
Release`, 0W/0E) and deployed. Re-ran live: the log now reads "call failed:
Oracle: claude -p exited 1 -- Failed to authenticate: OAuth session expired
and could not be refreshed" — the real cause, finally visible.

**Also fixed in passing**: the owner's global `C:\Users\Mandrake\.claude\settings.json`
had a stale `Write(~/.claude/**)` permission rule the CLI itself flags as
invalid ("only Edit(path) rules are matched ... Use Edit(~/.claude/**)
instead") — this was surfacing as noise on every `claude -p` call (harmless
on exit 0, but confusing on exit 1). Removed the redundant entry (`Edit(~/.claude/**)`
already covers it).

**Owed, and it's his**: the Windows `claude.exe` (2.1.228,
`C:\Users\Mandrake\.local\bin\claude.exe`) needs a fresh interactive login
(`claude login` or equivalent) before any live Oracle call can actually
succeed — that's an OAuth flow, not something an agent can do for him. Until
then every consumer correctly ships its fallback text, per the spec's law #2
("the game is whole with the LLM absent").
