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

## Live-verified 2026-08-30, FOUNDRY — PASS on all three frameworks

Full 585-mod list, fresh `start_debug_game_ready` quicktest map, bridge live.

**Framework detection — all three present, real component types, no guessing:**
```
VEF PipeSystem     present: true   componentType: PipeSystem.PipeNetManager
Rimefeller         present: true   componentType: Rimefeller.MapComponent_Rimefeller
Dubs Bad Hygiene   present: true   componentType: DubsBadHygiene.MapComponent_Hygiene
```

**VEF read proven by TOPOLOGY, not by one number.** A fresh map has no pipes, so
`netCount: 0` — which alone proves nothing. Built a network and watched the tool
track it:

1. Six `AB_PropanePipe` in a row at x=130..135,z=130 **plus** one
   `AB_PropaneStorage` at x=137,z=130 — deliberately leaving a one-cell gap at
   x=136. `jawa/map_commit`, then read:
   ```
   netCount: 2
   net A  connectorCount 6  storageCount 0  availableCapacity    0.0
   net B  connectorCount 1  storageCount 1  availableCapacity 1500.0
   ```
   Two nets, split exactly where the gap is; the pipe-only run correctly has zero
   capacity and the tank correctly carries all 1500.
2. Placed ONE pipe at x=136,z=130 to bridge the gap, `map_commit`, re-read:
   ```
   netCount: 1
   connectorCount 8   storageCount 1   availableCapacity 1500.0
   ```
   6 + 1 + 1 = 8 connectors, the two nets fused, capacity carried through.

⇒ The tool reads **live `PipeNetManager.pipeNets` topology**, not a static dump.
The numbers are self-consistent against a geometry chosen so a wrong read could
not match it. Every VEF row carries `verified: true`.

**And this re-proves the item's second finding, incidentally and for free**: no
pipe-specific registration call was ever made — `jawa/build_batch`'s ordinary
`GenSpawn.Spawn` path was enough for `CompResource.PostSpawnSetup` to register
every connector into the net. `place_pipe_line`'s "no modded pipe-grid dirty step"
flag is confirmed moot for VEF PipeSystem, live.

**Rimefeller / Dubs Bad Hygiene — honest as designed.** Both returned a generic
reflection dump under an explicit
`"UNVERIFIED - no vendored source ... Generic reflection dump."` note, every row
tagged `verified: false` (Rimefeller: `LimitOilStorage`, `FuelPumpLimit`,
`masterID`, `MannedConsole`…; DBH: `WaterGridSeed`, `DeepWaterGridSeed`,
`InitFinalized`, `UpdateCapacities`…). Real live values, and un-mistakable for a
curated read. Nothing here claims more than it verified.

## criteria
- [x] Owner ruling recorded verbatim, acted on exactly.
- [x] VEF PipeSystem read verified against real vendored source, not guessed.
- [x] Rimefeller/DBH honestly marked unverified in the result, not silently guessed.
- [x] `place_pipe_line`'s dirty-step question resolved (moot for VEF) without writing
      unverified code to "fix" a non-problem.
- [x] Builds clean, no duplicate alias (full surface re-scanned).
- [x] Deployed and proven live — all three frameworks detected on the real
      585-mod list; the VEF read tracked a built network splitting into 2 nets and
      merging back into 1, with connector counts and capacity self-consistent.

--- history ---
