# FILTH_ON_NATURAL_TERRAIN_NOOP_1 — `Filth_AnimalFilth` cannot be placed on natural ground

## what is wrong

Two shipped mechanisms drop `Filth_AnimalFilth` through
`FilthMaker.TryMakeFilth(cell, map, def, count)` and **neither one can ever produce
a single filth outdoors on this planet**:

- `RM_CompDungSeeder` — `dungFilthDef Filth_AnimalFilth`, `dungFilthCount 4`, on
  `RSW_ShadeWhale`. This is the *"they leave massive dung at shade patches"* half of
  desert.md §4c.
- `RM_JobDriver_FilterFeedTerrain.LeaveChurnedGround` — `leavingsFilthDef
  Filth_AnimalFilth`, `leavingsFilthCount 1`, on the same creature's
  `RM_FilterFeedExtension`.

## MEASURED, live, 2026-09-21 (`SHADE_WHALE_ECOLOGY_LIVEPROOF_1`)

- **Six completed filter-feed bouts** on Sand, each with `leavingsFilthCount 1` →
  **0 `Filth_AnimalFilth` anywhere on the 62,500-cell map.**
- **Eight shaded dung events** with `dungFilthCount 4` → 0 filth at every site but one.
  The exception (a whale under `RoofRockThick`) accumulated 5 → 18 across ~40,000
  ticks, a cadence far faster than a 15,000–30,000-tick dung interval — that is the
  whale's own `FilthRate 24` through `Pawn_FilthTracker`, which passes
  `FilthSourceFlags.Pawn` and so takes an exemption the comps do not.

## why — the engine source, read from the decompiled 1.6 tree

- `Filth_AnimalFilth.filth.placementMask` is **`[Terrain]`** — Core
  `Defs/Core/ThingDefs_Misc/Filth_Various.xml`.
- Every terrain inheriting `NaturalTerrainBase` — Sand, SoftSand, Soil, Gravel, the
  rough stones, all of it — declares `filthAcceptanceMask` **`[Unnatural]`** — Core
  `Defs/Core/TerrainDefs/Terrain_Natural.xml`.
- `FilthMaker.TerrainAcceptsFilth` requires `(acceptance & placement) == placement`.
  `Unnatural & Terrain` is 0, so it is **false for every natural terrain**.
- `FilthMaker.CanMakeFilth` has a roof/enclosed-room escape hatch, but it is gated on
  `filthSourceFlags.HasFlag(FilthSourceFlags.Pawn)`. `Filth_AnimalFilth` does not carry
  `Pawn` in its placement mask, and the `TryMakeFilth(cell, map, def, count)` overload
  both comps call never supplies it as `additionalFlags`.

## why it matters

The dung is not decoration — desert.md §4c makes the megafauna *"the biome's
circulatory system … fertilising every harbour they stop at"*, and a player is meant
to SEE where a whale stopped. Today they see nothing. Separately, filth is the
indicator a future agent will reach for to check "did the comp tick", and it will
report a healthy mechanism as dead.

## the work

Decide which, then do it — this is a def/flag question, not new mechanism:

1. Pass `FilthSourceFlags.Pawn` (or the appropriate flag) as `additionalFlags` on both
   `TryMakeFilth` calls. ⚠️ That only buys the ROOFED/enclosed case, per `CanMakeFilth`
   above — on open sand it still fails. Check that before choosing it.
2. Or use a filth def whose `placementMask` the desert's terrain actually accepts.
   ⚠️ `Filth_Sand` and `Filth_Dirt` are also `[Terrain]`-only and fail the same test —
   verify any candidate against `TerrainAcceptsFilth` before wiring it.
3. Or drop the filth from both comps as unachievable on natural ground and say so in
   the def comments, so nobody re-adds it.

⛔ Do NOT "fix" this by changing a Core TerrainDef's `filthAcceptanceMask`.

## verify

A live whale, on open Sand, leaves visible filth at its cell after one dung event and
after one filter-feed bout — or both comments say plainly that it cannot and why.

## criteria

Filth appears where the design says it appears, or the claim is removed from both
comps and from `desert.md`'s expectations. No third state.
