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

## decision, 2026-09-21 — option 2, new FilthDef

Read the decompiled engine in full before choosing (`FilthMaker.cs`,
`FilthProperties.cs`, `TerrainDef.cs`, `Filth_Various.xml`, `Terrain_Natural.xml`,
`Alert_AnimalFilth.cs`, `Pawn_FilthTracker.cs`):

- **Option 1 confirmed dead, as the item already suspected.** Passing
  `FilthSourceFlags.Pawn` as `additionalFlags` only unlocks `CanMakeFilth`'s
  roof/enclosed-room escape hatch. On open Sand — no roof, room touches the map
  edge — `TerrainAcceptsFilth` still runs and still fails, because
  `filthSourceFlags = placementMask | additionalFlags` still carries the
  `Terrain` bit and `Unnatural & (Terrain|Pawn) != (Terrain|Pawn)`. This matches
  vanilla's OWN animal-filth mechanic exactly: `Pawn_FilthTracker` (the system
  behind every animal's ambient `FilthRate`) already passes `FilthSourceFlags.Pawn`
  on every tick, and `Alert_AnimalFilth.cs` — vanilla's own alert for "animal
  filth is piling up" — explicitly requires a roof before it even considers
  filth a problem. Animal dung accumulating only indoors is deliberate vanilla
  design, not a bug we'd be working around.
- **Option 2 IS viable, and the item's own text ("Filth_Sand and Filth_Dirt are
  also [Terrain]-only") pointed at the right family without checking the
  default.** `RimWorld/FilthProperties.cs`'s C# default for an unset
  `<placementMask>` is `FilthSourceFlags.Unnatural` — exactly what
  `NaturalTerrainBase` (Sand/SoftSand included) accepts. Every Core filth that
  omits `<placementMask>` (Filth_Blood, Filth_Vomit, Filth_Water, Filth_Ash,
  Filth_OilSmear, Filth_CorpseBile, etc. — the ones anyone has actually seen
  outdoors on grass/dirt) rides this default; every Core filth that explicitly
  sets `[Terrain]` (Filth_Dirt, Filth_Sand, Filth_AnimalFilth, Filth_Trash) does
  not. `TerrainDefGenerator_Stone.cs` and the UtinniPatches precedent
  (`RUT_Filth_MouseTrack`, `mandrake.rut.utinnipatches`) confirm a mod-defined
  FilthDef with a deliberately-chosen mask is an established pattern, not a new
  idea.

**Shipped:** `RSW_Filth_WhaleDung` (new FilthDef,
`src/RimStarWars/SWBestiary/Defs/ThingDefs_Misc/RSW_Filth_WhaleDung.xml`),
`placementMask: [Unnatural]` — accepted outright by Sand/SoftSand's
`filthAcceptanceMask [Unnatural]`, no roof, no enclosed room, no `Pawn` flag
needed. Same look as `Filth_AnimalFilth` (Core's `GrainyA` cluster texture,
same dung tint) — real Core art, extracted via `extract_bundle_textures.py`
and copied to this mod's own `Textures/Things/Filth/RSW_WhaleDung.png`, because
`validate_patch.py` refuses a bare cross-mod reference to Core's
`Things/Filth/Grainy` once a mod ships its own `Textures/Things/` namespace
(same rule `RUT_Filth_MouseTrack` hit). `RSW_ShadeWhale.xml`'s `dungFilthDef`
and `leavingsFilthDef` both repointed at it, with inline comments against
ever swapping back to `Filth_AnimalFilth`.

**Does NOT change:** Core's `Filth_AnimalFilth` def, any Core TerrainDef's
`filthAcceptanceMask`, or `RM_CompDungSeeder`/`RM_JobDriver_FilterFeedTerrain`'s
C# (the fix is entirely def-level, as the item predicted it should be).

Offline work complete: `validate_patch.py` clean on both files (0 errors), all
69 selftests pass, `deploy_custom_mods.py --mod SWBestiary --apply` deployed
(the new def, the new texture, the edited whale def — verified in sync).

**Live confirmation still owed.** The bridge was held by another FOUNDRY window
the whole time I was ready to verify (`ASHKARRFLORA_NOT_IN_MODLIST_1`, live and
non-stale — idle 15 min, well inside the 45-minute staleness gate — so per
`one-bridge-driver-at-a-time` I did not take it). Per this item's own
verification rule I am NOT closing on an unconfirmed live claim. Owed: spawn
`RSW_ShadeWhale` on open Sand, force a dung event and a filter-feed bout, and
confirm `RSW_Filth_WhaleDung` actually appears at the cell. Whoever gets the
bridge next and can reach this should do that and close with the confirming
observation, per the skill's own rule that whoever proves it closes it.
