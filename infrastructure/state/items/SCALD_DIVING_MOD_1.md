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

## Owed (why this is BLOCKED, not closed)

This mechanism has never been observed running — FOUNDRY.md: "a live check
is owed only to a mechanism never once observed running." The game was
measured DOWN when this build finished, and shortly after came back UP
under another window's own session (bridge held by that window per this
item's own instructions — "stay off the bridge and world state entirely").
So:

1. `mandrake.rm.divinginteraction` is deployed to `Mods/` but deliberately
   **NOT added to ModsConfig.xml** — enabling it is a live mod-list write
   (CHARTER expensive-list item 3) and doing it while another window is
   mid-session risked their restart loading an unverified mod cold.
2. Next FOUNDRY/BENCH window with the bridge free: enable the mod, cold
   load (or minimal-list quicktest), confirm in Player.log there is no
   `Config error` and no red patch-mismatch for `RM_ScaldDiveEligibleTerrain`,
   then in a live/quicktest map right-click a tagged Scald shallow cell and
   confirm both float menu options appear, a dive job completes, HP drops
   from the terrain's own burn tick during it, and the mood thought /
   chitin drop resolve. Then `rimflow close SCALD_DIVING_MOD_1 --sha <commit>`.
