# SCALD_DIVING_MOD_1 — Deep Diving (RimMandrake tier)

Owner ruling (2026-09-12, `scald_kit_spec.md` open card 3, verbatim): "Diving
interaction, and make the diving mod v1 content now!!" Ban 4 in
`the_scald.md` ("no macro-life in the boil itself") is superseded exactly
this far: a DEEP interaction exists; the boiling SURFACE stays no-swim.

## What shipped

`src/RimMandrake/DivingInteraction/` — packageId `mandrake.rm.divinginteraction`,
namespace `RimMandrake.DivingInteraction`, defName prefix `RM_` (naming_lint:
0 violations).

**The mechanism, and why it's a dive SITE, not a bottom-walker pawn**:
`measure`/RimSage confirm zero bottom-walker PawnKindDef/ThingDef exist in
the live def set — `scald_kit_spec.md` S5 ships walkers only as a
non-resident surfacing incident. Simulating a full huntable swimming pawn
for a creature with no def and an explicit "not a resident pawn" ruling
would invent lore outside this item's charter. Instead: any TerrainDef
tagged `RM_DiveEligible` and Standable becomes a cell a colonist can be sent
to dive at. Right-click it (a `FloatMenuOptionProvider`, auto-discovered by
`FloatMenuMakerMap.Init()`'s reflection scan — no Harmony) for "Dive to
hunt" or "Dive to commune"; the pawn walks onto the cell and holds position
for a tunable duration (`RM_JobDriver_DiveBase` + two outcome subclasses).

**"Priced in burns" reuses the existing mechanism, not a parallel one**:
verified via RimSage that `HediffGiver_Terrain`
(`Source/Verse/HediffGiver_Terrain.cs:17`) already fires on any pawn
standing on `burnDamage`-carrying terrain, wired globally via
`Core/HediffGiverSetDefs/HediffGiverSets.xml`. This mod adds zero damage
code — the dive job's only job is holding the pawn on the tagged cell long
enough to eat that terrain's own burn ticks. The one exception (a hunt
"lashback" on a failed roll) reuses the SAME `DamageDefOf.Burn` the terrain
giver uses, verified the same way.

**Wiring to the Scald** (`Defs/Patches/RM_ScaldDiveEligibleTerrain.xml`):
three `PatchOperationAdd` ops, each `MayRequire="mandrake.rut.patches"`, tag
`RUT_ScaldWaterShallow` / `RUT_ScaldWaterMovingShallow` /
`RUT_ScaldWaterMovingChestDeep` (all Standable — `WaterShallowBase`/
`WaterChestDeepBase` descendants, verified against
`Defs/Core/TerrainDefs/Terrain_Water.xml`) with `RM_DiveEligible`.
`RUT_ScaldWaterDeep`/`OceanDeep` are deliberately untouched: `WaterDeepBase`
descendants, `passability Impassable`, verified same file — a walking pawn
cannot path there regardless of any tag, so the boiling surface stays
structurally no-swim. `RM_DiveUtility.CellIsDiveSite` also re-checks
`Standable()` at runtime as a second gate.

**Mod Settings** (`RM_DivingSettings`, MOD_OPTIONS_RETROFIT_1 doctrine):
master on/off, hunt/commune independent toggles, dive duration (the actual
burn-exposure dial), per-cell cooldown, hunt success/lashback chances, hunt
yield range, commune mood offset (live-tunable via a `Thought_Memory`
subclass overriding `MoodOffset()`, not a static XML placebo). Every default
matches the shipped description.

**Hunt reward**: `RM_ScaldWalkerChitin` (new ResourceBase item, not
meat/leather — no fauna def exists to derive those from; the roster/bestiary
pass can retire this once a real walker pawnkind ships).

## Verification done

- `dotnet build RM_DivingInteraction.csproj -c Release` — 0 errors, 0
  warnings (this is the load-bearing check: every API used —
  `FloatMenuOptionProvider`, `Toils_General.Wait`, `JobMaker.MakeJob`,
  `Thought_Memory.MoodOffset()`, `pawn.Reserve(IntVec3, ...)` — is
  compiler-verified against the real Assembly-CSharp.dll, not guessed).
- `naming_lint.py` — 0 violations for this mod.
- `validate_patch.py --live <2026-09-12T05-56-05Z capture>` — 0 errors, 4
  advisory warnings (a `PatchOperationAdd` not wrapped in
  `PatchOperationFindMod` — already `MayRequire`-gated by packageId, which
  is the stable identifier per `NAMING_SCHEME_PLAN.md`; and a texPath
  warning for reusing vanilla `Things/Item/Resource/Leather`, which the
  validator itself flags as a known false-positive category since vanilla
  textures live in asset bundles, not loose files — confirmed real via
  `RimSage.get_def_details(Leather_Plain)`).
- `deploy_custom_mods.py --mod DivingInteraction --apply` — deployed clean,
  7 files, VERIFIED in sync.

## 🔴 The 2026-09-12 build had never actually applied its own patch

Re-verifying live 2026-09-20 (bridge free all day, no contention) found the
patch file deployed at `Defs/Patches/RM_ScaldDiveEligibleTerrain.xml` —
**inside** the `Defs/` tree. RimWorld's Defs loader tried to parse it as a
Defs file and rejected it twice (`root element named Patch; should be
named Defs`, then `Type PatchOperationAdd is not a Def type`). **The
`RM_DiveEligible` tag had never once landed on any Scald terrain, live or
on disk, since the mod was built** — moved to a mod-root `Patches/` folder
(sibling of `Defs/`, matching `FlowWorks/Patches/` and `RimUtinni
Patches/Patches/`; commit `d38274fb3`) and redeployed.

## Verification done, live, post-fix (2026-09-20)

Added a `diving` tier to `modset_builder.py`
(`brrainz.rimbridgeserver` + `mandrake.rut.patches` +
`mandrake.rm.divinginteraction`) and drove it through the bridge
(`jawa/get_defs`, `jawa/set_terrain`, `jawa/spawn_pawn`,
`jawa/ordered_job`, `rimworld/step_game_ticks`, `jawa/pawn_thoughts`,
`jawa/list_things`, `jawa/mod_settings_field`):

- **Tag now applies correctly**: `jawa/get_defs` on the four terrains shows
  `RUT_ScaldWaterShallow`/`MovingShallow`/`MovingChestDeep` all carrying
  `RM_DiveEligible` + `Standable`; `RUT_ScaldWaterDeep` carries neither the
  tag nor `Standable` (`Impassable`) — ban 4's boiling-surface exclusion
  holds structurally, not just by intent.
- **"Priced in burns" fires live**: painted `RUT_ScaldWaterShallow` onto a
  quicktest map, stood colonists on it — the vanilla `Burn` hediff
  accumulated on every pawn standing there, unprompted, from the terrain's
  own `burnDamage`/`burnIntervalTicks`.
- **`RM_Job_DiveCommune` runs to completion**: given directly via
  `jawa/ordered_job` (same `TryTakeOrderedJob` call the float menu's
  `Action()` makes) at a tagged cell, ran ~2500 ticks, and applied
  `RM_Thought_CommunedWithDeep` at `moodOffset: 6.0` — matching
  `RM_DivingSettings.communeMoodOffset`'s live default, confirming the
  `Thought_Memory.MoodOffset()` override actually reads the setting.
- **`RM_Job_DiveHunt` runs to completion**: same call shape, produced one
  `RM_ScaldWalkerChitin` on the map afterward.
- **`RM_DivingSettings` loads live**: `jawa/mod_settings_field` lists all
  10 fields (`masterEnabled`, `huntEnabled`, `communeEnabled`,
  `diveDurationTicks`, `diveCooldownTicks`, `huntSuccessChance`,
  `huntLashbackChance`, `huntYieldMin/Max`, `communeMoodOffset`) at exactly
  their documented shipped defaults.
- **Clean load twice** (the diving tier, then the real 618-mod full list
  with this mod now added): no `Config error`, no cross-reference error, no
  patch-failure line naming this mod or `RM_ScaldDiveEligibleTerrain.xml`
  either time.
- `mandrake.rm.divinginteraction` added to `ModsConfig.FULL.LATEST.xml`
  (right after its `mandrake.rut.patches` `loadAfter`) and to the live
  `ModsConfig.xml` — it now ships as real content, not deployed-but-inert.

## Owed — one gap, deliberately not chased here

**Not verified**: the literal right-click float menu presenting "Dive to
hunt"/"Dive to commune" as two clickable UI rows. No bridge tool queries
`FloatMenuMakerMap`'s output at a cell, and simulating the click would need
a screen-coordinate/camera-projection tool that does not exist yet. What
*is* verified is the exact code both menu rows execute
(`JobMaker.MakeJob(jobDef, cell)` + `pawn.jobs.TryTakeOrderedJob`, driven
identically via `jawa/ordered_job`) end to end, and that
`RM_FloatMenuOptionProvider_Dive.AppliesInt` (`masterEnabled` +
`CellIsDiveSite`) reads live-true data. `FloatMenuOptionProvider`
auto-discovery via `FloatMenuMakerMap.Init()`'s reflection scan is a
standard RimWorld mechanism with no custom registration to fail. Residual
risk is low but real — if this specific UI presentation is ever doubted,
the check is one screenshot after an OS-level right-click at the tagged
cell's projected screen position, not a re-build.
