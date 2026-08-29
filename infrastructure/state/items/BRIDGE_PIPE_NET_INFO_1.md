# BRIDGE_PIPE_NET_INFO_1 — jawa/pipe_net_info, and place_pipe_line's "dirty step" question resolved as moot

Filed 2026-08-29, FOUNDRY. Owner ruled on the vague/uncertain item directly: asked
whether to build VEF-only-verified, all-three-generic, or skip pipes entirely —
**"All three, generic reflection."**

## Spec

`jawa/pipe_net_info` (new file `JawaBenchPipeTools.cs`, ungated, read-only):
- Detects all three frameworks by scanning `map.components` for a type name containing
  `PipeSystem.PipeNetManager`, `Rimefeller`, or `Hygiene`.
- **VEF PipeSystem: VERIFIED.** Read the mod's own vendored source
  (`vendor/mod_sources/VanillaExpandedFramework-main/Source/PipeSystem/`) — confirmed
  `PipeNetManager.pipeNets` (List<PipeNet>), and per-net `Stored`/`Consumption`/
  `Production`/`AvailableCapacity` plus connector/storage/producer/receiver counts. 🔴
  Also confirmed there is **no `CachedPipeNetManager` type** — the original roster's
  `strings`-scan sighting of that name was .NET heap suffix compression on a property
  backing field, not a second class. Settles that UNCERTAIN note for good.
- **Rimefeller, Dubs Bad Hygiene: UNVERIFIED, by design.** Both ship DLL-only in this
  repo's vendor tree (no `Source/` folder). Read via a generic reflection dump of
  whatever public simple-typed fields/properties exist on the matched MapComponent,
  every row tagged `verified: false` in the RESULT itself so a caller cannot mistake
  it for a curated read.

## A second finding, resolved without building anything
Checked whether `place_pipe_line`'s roster-flagged gap ("no modded pipe-grid dirty
step") is real for VEF PipeSystem: **it is not.** `CompResource.PostSpawnSetup` calls
`PipeNetManager.RegisterConnector(this)` automatically
(`vendor/mod_sources/.../Comps/CompResource.cs:39`) — any pipe thing spawned through
the normal `GenSpawn.Spawn` path (which `jawa/connect_cells` and `jawa/build_batch`
already use) self-registers into the network with no extra step. `jawa/connect_cells`
being def-generic already fully covers VEF pipe placement. No new tool needed; the
roster's own PARTIAL flag on `place_pipe_line` is stale for at least this framework.
Rimefeller/DBH's spawn-hook behavior is unverified for the same no-source reason as above.

## Verify
Builds clean, 0 errors 0 warnings. 279 unique `jawa/…` names, no duplicate aliases
(full-surface re-scan, same method that caught `JAWA_TOOLS_ALL_DARK_DUPLICATE_ALIAS_1`).
**Not deployed** — game is up, BENCH holds the bridge. Once deployed: confirm
`frameworks[].present` correctly detects whatever's active on the real 578+-mod list,
and that a VEF net's `stored`/`consumption` numbers read sane against something
visible in-game (a chemfuel or gas network).

## criteria
- [x] Owner ruling recorded verbatim, acted on exactly.
- [x] VEF PipeSystem read verified against real vendored source, not guessed.
- [x] Rimefeller/DBH honestly marked unverified in the result, not silently guessed.
- [x] `place_pipe_line`'s dirty-step question resolved (moot for VEF) without writing
      unverified code to "fix" a non-problem.
- [x] Builds clean, no duplicate alias (full surface re-scanned).
- [ ] Deployed and proven live. Needs the game down, then bridge.

--- history ---
