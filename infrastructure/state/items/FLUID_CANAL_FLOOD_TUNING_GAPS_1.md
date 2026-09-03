# FLUID_CANAL_FLOOD_TUNING_GAPS_1

Opus code review (2026-09-02) of `FLUID_CANAL_MECHANIC_1`'s FluidCanals mod
(never independently reviewed since being built/deployed by an
unsupervised fork). One CRITICAL crash bug (a live-collection-mutated-
while-enumerating `InvalidOperationException` on the mod's only functional
path) plus 4 smaller issues were fixed same-session in
`CompFluidReservoir.cs`/`Flood_FluidCanal.cs`/`FluidCanalsDebugActions.cs`.
These remaining findings are intertwined with tuning/design decisions this
project's own "AFK batch, needs a tuning rig" pattern applies to (see
Ninefold's untuned event magnitudes for the same shape of open question) —
deliberately NOT rushed into a fix.

## spec

1. **Terrain overwrite is permanent and destructive; undisclosed.**
   `Flood_FluidCanal.SpreadFlood` calls `terrainGrid.SetTerrain` (not
   `SetTempTerrain`, which vanilla's own `SeasonalFlood` uses) with a
   non-`layerable` terrain — any constructed floor on a flooded cell is
   erased with no way back (plants/blueprints on it are also destroyed via
   `DoTerrainChangedEffects`), and `Designator_DigCanal` refuses to
   re-designate water terrain, so a mistakenly flooded tile can never be
   re-dug. `FLUID_CANAL_MECHANIC_1`'s item file documents "not
   channel-constrained" as deliberate but does NOT document "permanent,
   floor-destroying, unrecoverable." Needs an owner/BENCH call: is
   permanent floor destruction the intended cost of an uncontrolled flood,
   or should `SetTempTerrain` + the plant-sparing `IsFlood` tag be used
   instead (matching vanilla's own pattern)?
2. **The flood Thing can tick forever if boxed in.** Base `Flood.Tick()`
   has no destroy path when `noPossibleCell` becomes true (walled-in
   canal, boxed by water) — only `Flood_FluidCanal.Tick()`'s own
   `remainingVolume <= 0f` check destroys it, so a flood that exhausts its
   reachable open ground before its volume does lives forever: ticking
   every tick, scribed into every save. `noPossibleCell` is a PRIVATE
   field on the base class with no protected accessor, so a subclass
   can't read it directly without reflection.
3. **`MaxFloodDurationTicks` (30000) is actually a rate divisor, not a
   duration.** `GetInitialCells` yields exactly one cell, so
   `estimatedFloodedTiles = 1 × FloodWidthRange.max = 12`, and
   `ExpandIntervalTicks = MaxFloodDurationTicks / estimatedFloodedTiles =
   2500` — the flood spreads exactly ONE tile per 2500 ticks (one in-game
   hour), regardless of `remainingVolume`. A 60-volume reservoir takes
   ~2.5 in-game DAYS to fully spend, not the half-day `30000` implies, and
   raising `volume` only makes it last longer, never faster (there's no
   rate knob on `FluidDef` at all). **This is why fixing finding 2 (a hard
   duration cutoff) would actively break normal operation** — a
   `spawnedTick + FloodingTicks` cutoff at the current `MaxFloodDurationTicks`
   would kill every flood at 30000 ticks, long before a typical reservoir
   naturally exhausts its volume. Fixing 2 and 3 together needs a real
   tuning pass: either raise `MaxFloodDurationTicks` to genuinely bound
   worst-case duration, decouple rate from `MaxFloodDurationTicks`
   entirely with a real per-tile rate field, or both.
4. **Reactive dig/flood oscillation.** `WorkGiver_DigCanal.HasJobOnCell`
   never re-validates terrain after a cell is designated — if a live flood
   converts a still-designated cell to water before the pawn reaches it,
   the pawn digs it back, which fires `Notify_TerrainChanged` and resets
   `noPossibleCell`, and the flood re-floods it. Each cycle burns the
   full 3200-work dig cost. Add a terrain guard to `HasJobOnCell`, or
   delete the designation when the cell becomes invalid.
5. **Performance**: `Notify_CanalCellOpened` still scans
   `map.listerThings.AllThings` (now safely, post-crash-fix, via
   `.ToList()`) for every dug cell — thousands of things, mostly plants,
   linear `TryGetComp` per thing. Fine at today's scale; worth switching
   to a radius-based cell scan (`GenAdj.CellsAdjacent8Way` +
   `cell.GetThingList`) if canal digging becomes a common, large-batch
   action.
6. **Debug report blind spot**: `FluidCanalsDebugActions`'s cell report
   prints `Props.fluidDef`/`Props.volume` (static XML config, never
   changes) next to the flood's genuinely-live `remainingVolume` — reads
   like live state and isn't. The comp's one real runtime field (`spent`)
   is never printed, so re-triggering an already-spent reservoir reports
   identically to a fresh one in the tool meant to verify exactly that.
   Expose `spent` via a public getter and print it.
7. **Refill-model save-state note** (informational, from the review's
   answer to `FLUID_CANAL_MECHANIC_1`'s own open finite-vs-refill
   question): the code cleanly implements finite/one-shot with no
   internal contradiction — `FLUID_CANAL_MECHANIC_1`'s "code vs. ruling"
   framing is correct. If a refill model is later ruled, note the
   reservoir keeps NO runtime volume state today (`Props.volume` is
   shared immutable XML config, the only scribed field is `bool spent`) —
   a refill rework needs new scribed per-instance state
   (`currentVolume`/`lastRefillTick`), which is cheapest to add before any
   save contains a reservoir instance.

## verify

1 needs an owner/BENCH design call before any code change. 2-3 need a
tuning pass (their own dedicated pass, not a quick fix, per the note
above). 4 and 6 are bounded code fixes, offline-verifiable. 5 is
perf-only, no correctness stake.

## criteria

1 gets an explicit owner ruling (documented either way). 2+3 get a real
tuning decision, not a guessed number. 4 and 6 fixed. 5 and 7 noted/
deferred with reasons.

## Partial progress 2026-09-02 (FOUNDRY)

Fixed 4 and 6:
- `WorkGiver_DigCanal.HasJobOnCell` now re-checks terrain (mirroring
  `Designator_DigCanal.CanDesignateCell`'s own gate) before handing out a
  job, and deletes the designation if a live flood already converted the
  cell — breaks the dig/flood oscillation instead of burning 3200 work
  per cycle.
- Exposed `CompFluidReservoir.Spent` and added it to the debug cell
  report, next to the fluid/volume config it was previously printed
  alone next to (which never changes and read like live state).

Compiles clean (`RimMandrake_FluidCanals.csproj`, 0/0).

**Still open**: 1 (permanent floor destruction, owner call), 2+3 (the
immortal-flood-if-boxed-in bug and the rate/duration tuning it's
entangled with — needs a real tuning pass, not a guess), 5 (perf, no
correctness stake, deferred), 7 (informational only, no action needed).
