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

## Owner ruling + findings 1, 2, 3 closed 2026-09-02 (FOUNDRY)

**Owner ruling on finding 1, verbatim, 2026-09-02:** *floods must become
recoverable, matching vanilla's SeasonalFlood pattern* — `SetTempTerrain`
instead of the permanent `SetTerrain`, not permanent floor destruction.

Implemented, and it carried 2 and 3 with it — the three are one change, not
three:

**1 — recoverable.** `Flood_FluidCanal.SpreadFlood` now writes the map's
TEMPORARY terrain layer (`terrainGrid.SetTempTerrain` +
`tempTerrain.QueueRemoveTerrain`), exactly as `RimWorld.SeasonalFlood` does.
`TerrainGrid.TerrainAt` returns the temp layer first, so a flooded cell reads
and behaves as water while it stands; `RemoveTempTerrain` clears `tempGrid`
and the cell's real terrain — a dug channel, a constructed floor — is back
untouched. `FluidDef.fullTerrain` is accordingly renamed `floodTerrain` and
`RM_Fluid_Water` repointed from `WaterShallow` to vanilla's own
`ShallowFloodwater` (the temporary sibling, carrying the plant-sparing `Flood`
tag). `SetTempTerrain` hard-refuses a terrain without `<temporary>true</temporary>`,
so `FluidDef.ConfigErrors` rejects one at load and `CompFluidReservoir.TrySpend`
refuses one at the moment of use.

⚠️ **`TempTerrainProps.destroysFloors` is deliberately NOT set**, against the
first reading of "a flood is destructive, just recoverable". Read
`TerrainGrid.SetTempTerrain`: that flag MOVES `underGrid` into `topGrid` and
nulls `underGrid`, and `RemoveTempTerrain` never puts it back — it is
permanent floor destruction with the water receding on top, i.e. precisely
what this ruling removes. Vanilla's `ShallowFloodwater` carries no
`tempTerrain` block for the same reason.

**3 — rate decoupled from duration, the finding's own preferred remedy.**
`MaxFloodDurationTicks` was a flat 30000 and base `Flood` divides it by
`estimatedFloodedTiles` to get the expand interval, so the "duration" was
really a rate divisor: 30000/12 = one tile per 2500 ticks. Now inverted —
`FluidDef.ticksPerTile` is the real per-fluid rate knob and
`MaxFloodDurationTicks => ticksPerTile * estimatedFloodedTiles` is derived
from it, so the base class's own division returns exactly `ticksPerTile` and
`FloodingTicks` is a genuine duration again. `estimatedFloodedTiles` is also
corrected in `SpawnSetup` to the tiles the reservoir can actually pay for
(`volume / volumePerTile`) instead of base's `seedCells × 12`, which is 12 for
any single-seeded release regardless of volume.

**2 — the immortal boxed-in flood.** `Tick` now destroys the flood past
`spawnedTick + 2 × FloodingTicks`. This is the cutoff finding 3 said would
"actively break normal operation" — and it would have, while
`MaxFloodDurationTicks` was a rate divisor. It is safe only *because* 3 was
fixed first: `FloodingTicks` is now exactly the time needed to place every
tile the reservoir can pay for, and the flood gets an equal grace on top for
cells that open up late (a pawn digging through, a wall coming down), which is
the one legitimate reason a healthy flood runs past its own budget. No
reflection needed — `noPossibleCell` is still private and still unread. An
expired flood leaks nothing: every tile it placed was queued for removal on
the map's own `TempTerrainManager`, which is independent of the flood Thing.

**The numbers, and why they are not guesses.** Both are per-fluid XML fields,
so a fluid that should behave differently says so without a code change.
`floodedTicks` 300000 is the midpoint of vanilla `SeasonalFlood`'s own
`FloodedTicksRange` (240000–360000) — the pattern the owner named.
`ticksPerTile` 60 (one in-game minute per tile) is the flow rate of water
running down a channel and sits in the same tens-of-ticks band vanilla's own
`Flood` engine works out to on a real map; a viscous fluid (tar, ooze) sets it
far higher. A 60-volume spring now spreads ~60 tiles in ~1.5 in-game hours and
the water drains ~5 days later, against the old ~2.5 in-game DAYS to spread
and never draining at all.

**Consequence the owner may want to rule on separately:** a canal's water is
now transient by construction — it recedes. That is the direct and intended
consequence of "recoverable", but it means this engine produces no standing
canal water today. If permanent-once-settled water is wanted, that is a
second, additive mechanic (a "settled" terrain the temp layer resolves to via
`TempTerrainProps.terrainOnRemoved`), not a reversal of this ruling.

Debug surface extended for exactly this change: `Report cell (RAW)` now prints
`tempTerrain=` and `underneath=` (recoverability is invisible to `GetTerrain`,
which returns the temp layer) and `expiresAtTick`/`nowTick` on a flood.

Compiles clean (`RimMandrake_FluidCanals.csproj`, 0 warnings / 0 errors).

🔴 **Owed: live verification.** Not deployed, not watched — nobody has seen a
flood recede or a floor come back. Filed for BENCH as
`FLUID_CANAL_FLOOD_LIVE_CHECK_1`, carrying the three decision strings
(temp-layer read, observed rate, boxed-in expiry) written BEFORE the launch.
A quicktest on the minimal mod list is enough; this needs no cold load.

**Remaining findings, unchanged:** 5 (perf — `Notify_CanalCellOpened` scans
`AllThings`; no correctness stake, revisit only if canal digging becomes a
common large-batch action), 7 (informational; the refill-model note stands
should a refill model ever be ruled).
