# JAWABENCH_COMPANION_NOT_LOADING_1

## Mechanism never observed running

RimBridgeServer's companion-discovery step succeeding after the exact
sequence "deploy the DLL while the game is down, restart" has been assumed
all session but never actually confirmed by reading a fresh log for the
`[JawaBench] ready:` line — every session before this one either deployed
earlier in a longer-running session, or the deploy and the restart it
verified against weren't this tightly time-boxed. This restart is the
first observation of that exact sequence, and it failed.

## spec

On the 2026-09-02 23:5x restart (BENCH's "land 2 mod removals + Inhabited.dll"
reboot, companion deployed by FOUNDRY during the preceding DOWN window at
16:34 local), `[RimMandrake.Inhabited] ready: ... 294 characters ...` fired
correctly, but `[JawaBench] ready:` never appears anywhere in the log —
not present, not an error, nothing at all naming "JawaBench" or
"companion". Confirmed:
- `RimBridge` itself started clean: "Startup conditions satisfied after
  play-data load; initializing bridge services", GABP server running on
  port 5174, bridge token printed.
- The DLL is present and correctly sized on disk:
  `BridgeTools/JawaBench/JawaBench.BridgeTools.dll`, 2772992 bytes,
  written 16:34 (matches the last successful `--apply`).
- `harvest_log.py`'s standing checks are all green/expected (0 dead mods,
  1 known Harmony failure, 0 unexpected patch failures) — this isn't a
  broader load problem, just JawaBench specifically.

## verify

Needs the bridge (currently held by BENCH, mid-reboot-scoring — did not
grab it to investigate, per one-driver-at-a-time). Once free:
1. Try a bare RimBridge core call (`rimworld/get_ui_state`) to confirm the
   bridge itself answers.
2. Try any `jawa/*` tool call to confirm/deny the companion's tools are
   registered at all (vs. just not logging its own ready line).
3. If genuinely absent, check whether `RimBridgeServer`'s own companion
   scan logs elsewhere (a different log file, or a level this project's
   log-triage doesn't grep for) before concluding the scan itself
   silently skipped the folder.

## criteria

Either `[JawaBench] ready: N tools` fires on the next restart (transient,
closed), or the actual failure point is named (folder scan skipped,
assembly load exception not logged where expected, RimBridgeServer version
mismatch, etc.) and fixed.

## Resolved 2026-09-02 (FOUNDRY) — false alarm, companion is fine

Bridge freed up; took it for a 2-call diagnostic. `rimworld/get_ui_state`
returned `programState: "Entry", inEntryScene: true, hasCurrentGame: false`
— the game was sitting at the **main menu**, not stalled or broken.
`jawa/list_pawns` returned a proper `"No current map. Load a game first."`
response with a real `CapabilityId`
(`jawa-bench.-bridge-tools/jawa-bench-terrain-tools/list-pawns`) —
the companion's tools ARE registered and responding correctly. The missing
`[JawaBench] ready:` line was either a timing/log-search artifact or the
line simply hadn't been reached yet at the point the log was read; the
functional evidence (a real tool call round-tripping through the
companion) outranks it. Not a regression. Closed.
