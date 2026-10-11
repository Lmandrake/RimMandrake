# FlowWorks P4-P8 independent review (2026-10-11)

Reviewer: FOUNDRY helper (wAI1). I read the diffs and the code around them, not the author's notes.
Commits: P4 c98e8e926, P5 5dcae23f0, P6a 57b4b4120, P6b ae21b56db, P8 18e516743. Reviewed on origin/main 9272c1344.

## Verdict

**0 code defects confirmed. 1 behaviour finding filed** (`FLOOD_SWITCH_OFF_PROVE_SPILLS_GO_NOWHERE`, P6a): with
"Spilled liquid fills channels properly" switched OFF, a FlowWorks spill now places nothing at all. The new settings
text understates this. Whether OFF should do that is a design call, so I filed it and changed no code.

All five fixes do what their commit says. Every new check goes red when the shipped rule is mutated back to the old
behaviour. Two gaps in coverage are listed below. Neither is a defect.

## Selftest run on origin/main

I ran `run_selftests.py --only` on all 16 `selftest*.py` files under `src/RimMandrake/FlowWorks` plus
`Utils/selftest_flowworks_stock.py` (the C# SelfTest exe), with WINBUILD_ROOT=_rmbuild/wAI1. Result: **PASS 17/17, GREEN**,
133 s wall.

## Can-it-fail probes (mutation of the shipped rule)

The "old rule" probes inside the new cases are lambdas written in the test itself (P5/P6a/P6b/P8), or a test-local
flag (P4). On their own they prove only that the test's copy of the old rule differs from the new one. So I mutated
the production pure functions back to the old behaviour in a throwaway `--shared` clone (wAI1_mut, never committed)
and rebuilt the SelfTest (stage _rmbuild/wAI1/mut):

| mutant (old behaviour restored in production code) | case | result |
|---|---|---|
| `RM_DriverInputs.NoteBackedUp` is a no-op | PUMP_FED_CHANNEL_STALL_PROVE_AFTER_RELOAD_... | **FAIL** (far end 0) |
| `FloodFillTarget` returns depth; `FloodLevelDebit` returns volumePerTile | P5_flood_debits_every_level_... | **FAIL** |
| `FloodPolicy(excavated, off)` returns TempTerrain | P6a_flood_switch_off_... | **FAIL** |
| `MayCoolToGlass` returns frontCell | P6b_tar_cooling_never_glazes_... | **FAIL** |
| `CanalLevelsToBurn` ignores burnableNow | P8_burn_pulse_never_consumes_... | **FAIL** |

No other case changed. A parent-file checkout cannot run these checks, because the parent files do not have the new
functions and would not compile. Mutating each function back is the real probe.

**Coverage gap (all five):** the CALL SITES depend on Verse and are not compiled into the SelfTest. Those are the
pump's backed-up loop in `Building_LiquidPump.TryPour`, `Building_LiquidDrill.TickRare`, `Flood_FlowWorks.PlaceFluid`
and `CoolFrontToGlass`, and `RM_LiquidFire.BurnPulse`. Deleting a call site leaves every test green. I checked these
by reading them, below. The P4 test also re-implements the pump cycle instead of running the pump's `cd`/`tk`
condition.

## Per-fix findings

### P4 (pump-fed channel stall after reload) — correct
- Engine-side logic: `NoteDriverBackedUp` marks a cell only when it is excavated and brimming (`fill >= depth`). The
  pump marks only brimming reach cells whose fluid matches a tank that can provide. The drill marks only after its
  power, yield, foreign-fluid and FluidAllowed guards have all passed. So a pump with an empty tank, a dry outlet or a
  foreign outlet never marks.
- A pump backed up for good in a settled closed channel keeps one cell at hop 0 permanently. `externalInput` only
  shapes the flow order (`ComputeFlowOrder` adds it as a hop-0 frontier, the same as a source), so the cost is
  ordering only. It does not move liquid and does not oscillate.
- Seams (4764c7143): the rotated-network path computes the order once over the whole network, inputs included, so the
  inputs reach every partition. No conflict.
- Save/load: the input set is still not saved, by design. The fix exists so that it re-derives within one 250-tick
  pump cycle (or TickRare for a drill) after a load. There are no new scribed fields, so existing saves are unaffected.
- Pump DRAW mode is untouched. Only `TryPour` marks.

### P5 (flood debit per level) — correct
- `FloodFillTarget` never goes below oldFill and clamps to depth. It overdraws at most one part-paid level, the same
  overdraw the surface path makes (`remainingVolume -= volumePerTile`). `TrySetDriverFillOutcome` clamps again, and
  the debit is read from `FillAt` after the write, so the debit matches the levels actually written.
- Behaviour change, and correct: a cell already brimming with the same liquid now costs 0, so a release passes
  through a full channel for free. It is still bounded, because `placedLookup` offers each cell once.
- volumePerTile is the same per-level unit the drill and pump use (`unitPerLevel`, `Stock.TryDebit(volumePerTile)`),
  so the units are consistent across drivers.
- Existing saves: `remainingVolume` is already scribed. A mid-release save simply continues under the new rule.
- Callers that tuned volumes for "a spill brims every channel cell" (TarPitBelch, ForgeCycle, HotLiquid) will now
  fill fewer channel cells per spill. That is the intended conservation, not a regression.

### P6a (flood switch off: hands off engine cells) — correct for the race; one behaviour finding
- Engine fact (RimSage, `TempTerrainManager.Tick`): a queued removal calls `terrainGrid.RemoveTempTerrain(cell)`
  unconditionally, whatever temp terrain is there. The engine writes its fill as temp terrain
  (`ApplyFillTerrain` → `SetTempTerrain`). So the old OFF path's queued removal really did strip the engine's fill.
  The race the commit describes is real, and the fix closes it.
- **Finding (filed): with the switch OFF a spill now spreads nowhere.** `CanFloodInto` admits only cells where
  `CanLiquidEnter` holds, that is `DepthAt > Surface`. Those are excavated cells, or natural-liquid read-through, and
  natural water is refused separately by `t.IsWater`. With OFF, every excavated cell is HandsOff, so a release places
  nothing except over natural non-water liquid terrain. Its frontier then empties and it is destroyed with its volume
  unspent. The new settings line ("Off: a spill never enters a dug channel, so it never clashes with the channel's own
  liquid") reads as if spills still happen elsewhere. That is no longer true. Default is ON, so shipped behaviour is
  unaffected.
- Minor (not filed): HandsOff and Refused cells go into `placedLookup` but not into the scribed `placedCells`. After a
  reload they are offered again, which is harmless (HandsOff again, no volume spent). `IsFrontCell` also stops
  counting them as placed, so a tar release's glass rim next to a channel can differ before and after a save. Refused
  already had this before P6a; P6a extends it to the OFF case.
- Residual for existing saves: removals queued before P6a on excavated cells, in a game run with the switch OFF, still
  fire once. That is a one-off and only applies to saves made with a non-default setting.

### P6b (tar cooling: no glass on engine cells) — correct
- `SetTerrain` writes the permanent layer, and an excavated cell's permanent layer is the engine's dry/depth terrain.
  So glass there gave the cell two owners. The guard reads `IsExcavated` at cooling time rather than at placement
  time. The edge case is a cell filled back in between placement and cooling, which would now glaze; that is
  negligible and arguably correct.
- Only fluids with `coolsToGlassEdge` (tar today) are affected. Water, brine, propane, chemfuel, slimes and lava
  (3f6213543) have no glass edge, so this path is a no-op for them.

### P8 (fire burn pulse timing) — correct
- `lit` is read at the start of BurnPulse, after the previous pulse's refill. Water standing on a lit cell burns no
  level, and its accumulator does not advance. The source-cell branch is unchanged: a body's fluid cannot change in
  place.
- Small behaviour change: a cell that drained to fill 0 is no longer extinguished inside BurnPulse (lit is null, so no
  levels are taken). `Maintain` puts it out within 30 ticks instead. Harmless.
- The `MinFlowPulseTicks` (60) > `FireCheckIntervalTicks` (30) floor matches the settings slider minimum (60), so no
  user setting can violate it.

## Interaction with today's other changes
- Seams 4764c7143: see P4. The inputs feed the network-wide order. No conflict.
- Quarry/sluice placer e569931e6: it does not call `NoteWrite` or `NoteDriverBackedUp`, and none of the P4-P8 call
  sites. No overlap found. It is untouched by these five diffs.
- Lava row 3f6213543: lava has no `coolsToGlassEdge` (P6b no-op). If it is burnable, P8's rule applies uniformly. P5
  debits at lava's own volumePerTile. No lava-specific path in these diffs.
