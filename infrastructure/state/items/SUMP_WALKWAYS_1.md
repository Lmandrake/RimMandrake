# SUMP_WALKWAYS_1 — duckboards and the glasswalk

Owner rulings 2026-09-24: the seed, typed — *"Maybe some advanced walkways you can
build that are resistant to the tar but are slippery so you can't walk full speed
ever but don't have to clean them anymore."* Structure and depth then ruled by
question card (decisions taken by card, 2026-09-24): **two tiers**, and **speed
cap + rare harmless pratfalls**.

## spec

1. **Duckboards** (early tier): cheap brindeth-wood plank path (`RM_Brindeth`,
   flora roster §3). Full speed when fresh; fouls with tar (accumulating filth
   slows it until scrubbed); flammable — a real liability in a biome whose
   defense economy is setting the ground on fire. The cleaning treadmill,
   ownable.
2. **Glasswalk** (advanced tier): poured bitumen cooled slick — manufactured
   glass reach (the biome's own precedent, sheet §8). Never fouls, never needs
   cleaning, tar-proof; permanently speed-capped (~80%, never full speed — his
   spec), plus rare slip-and-fall: a pawn moving fast or hauling sometimes goes
   prone, no real damage, just indignity (one small comp).
3. Materials ride the bitumen chain (korveth nodules, dig barrels). Chain ships
   in the mod; 🔴 road re-paving is OUT of campaign scope — owner, typed, same
   sitting: *"It's ok to make the mod to support that. But replacing the
   [road] isn't part of this campaign. There are other mods for that. And this
   one is about the ship."*
4. **Ship-buildable** (`BIOME_SHIP_CONTRIBUTIONS_1`): glasswalk flooring aboard
   the gravship is one of the owner's two named ship gifts from this biome —
   the slippery bitumen deck that never needs cleaning.
5. Both tiers are terrain/floor defs (path cost, filth acceptance, flammability);
   only the pratfall comp is new C#. Feature-gated in Mod Settings.

## verify

Quicktest: duckboards accumulate tar filth and slow; glasswalk accepts no filth
and caps speed; a hauling pawn on glasswalk occasionally slips prone without
injury; glasswalk is placeable on a gravship floor.

## criteria

The build progression is the biome's thesis: cheap-and-tidy is a treadmill; the
real answer is to stop fighting the tar and glaze it.

## build status — FOUNDRY, 2026-09-24, offline-complete, needs live proof

**Built and deployed** (UtinniPatches/FlowWorks/EnvironmentalHazards — `RM_TheSump`
mod does not exist yet, `THESUMP_RM_MOD_BUILD_1` still OWED, so this lands where
every other live Sump kit file currently lives, same tier convention as
`RUT_TarMoat.xml`):

- `src/RimUtinni/UtinniPatches/Defs/TerrainDefs/RUT_SumpWalkways.xml` —
  `RUT_Duckboards` (pathCost 0, Flammability 1.0, burnedDef
  `BurnedWoodPlankFloor`, costList WoodLog×4 **placeholder** for `RM_Brindeth`,
  which does not exist yet) and `RUT_Glasswalk` (pathCost 3 — calibrated
  against `GenPath.SpeedPercentString`'s own `13/(cost+13)` formula to read
  ~80% for a standard pawn, and *structurally* "never full speed" for every
  pawn since `Pawn_PathFollower.CostToMoveIntoCell` **adds** terrain pathCost
  to the pawn's own base cost rather than multiplying; `filthAcceptanceMask`
  None — the real vanilla gate `FilthMaker.TerrainAcceptsFilth` checks first,
  same field `RUT_TarShallow_FilthAcceptance.xml` had to *fix away* on
  `RM_TarShallow` — here it is deliberate; costList **REPOINTED**
  (`SUMP_TAR_NASTINESS_1`, 2026-09-24) from a Chemfuel×6 placeholder to
  `RUT_Bitumen`×6, a real def that item shipped — the bitumen/dig-barrel
  *supply chain* feeding `RUT_Bitumen` is still unbuilt, flagged on that
  def's own header, not this one's).
- `src/RimMandrake/FlowWorks/Defs/LiquidTypes/ThingDefs/RM_Filth_Tar.xml` —
  new FilthDef, pathCost 34 (`RM_GreentideChurnmud`-precedented mire value).
  **DEPLOY_HOLD'd** (`src/DEPLOY_HOLD.txt`): no real texture yet, and
  `validate_patch.py` refuses the vanilla `Things/Filth/Grainy` reuse as a
  hard ERROR once a mod ships its own `Things/` content (same trap
  `RUT_Filth_MouseTrack.xml` already hit, 2026-09-14).
- `src/RimUtinni/UtinniPatches/Patches/RUT_TarShallow_GeneratedFilth.xml` —
  new, isolated patch wiring `RM_TarShallow`'s `<generatedFilth>` to
  `RM_Filth_Tar` (vanilla's real foot-tracking mechanism,
  `Pawn_FilthTracker.TryPickupFilth`/`TryDropFilth` — duckboards' "fouls with
  tar" half, zero new C#). **DEPLOY_HOLD'd together with the FilthDef above**:
  `generatedFilth` is a direct ThingDef reference the loader resolves by
  name, so shipping it without the FilthDef deployed would be a real Config
  error, not a harmless unmatched-patch no-op — kept out of the *existing*,
  already-shipped `RUT_TarShallow_FilthAcceptance.xml` for exactly this
  reason (that file is untouched, still just its original filthAcceptanceMask
  fix).
- `src/RimMandrake/EnvironmentalHazards/Source/RM_MapComponent_GlasswalkSlip.cs`
  — new MapComponent (assembly `RimMandrake.EnvironmentalHazards`, already
  RM-tier, matches every other Sump kit C# file). Generic: watches for
  TerrainDef tag `RM_SlipperyWalkway` (`RUT_Glasswalk` carries it) on any
  map, and for a pawn that is hauling or whose job's `LocomotionUrgency` is
  Jog/Sprint, rolls `RM_EnvironmentalHazardsSettings.glasswalkSlipChancePerSweep`
  (default 2%, every 60 ticks) to call vanilla's own
  `pawn.stances.stunner.StunFor(...)` — a real, already-used, damage-free
  stagger (EMP/teleport/melee-stun's own mechanism), `addBattleLog:false`.
  No new hediff, no new animation. Wired into the `.csproj`
  (`<Compile Include>`), Mod Settings (`glasswalkSlipEnabled` toggle +
  `glasswalkSlipChancePerSweep` slider, checkbox/slider UI added, view-height
  bumped), and a Keyed translation string (`RM_GlasswalkSlip`).

**Validated offline**: `dotnet build` on `RM_EnvironmentalHazards.csproj` — 0
warnings/errors. `validate_patch.py` on all four touched/new XML files against
the live 621-mod set (Data+Workshop+Mods) — 0 errors on the three that should
be clean, 1 expected ERROR on `RM_Filth_Tar.xml`'s texPath (the held one,
above). Deployed via `deploy_custom_mods.py --apply` — plan matched
expectations exactly (2 files correctly HELD, rest `+`/`~`), `-> VERIFIED in
sync`.

**What a live proof needs** (no bridge access this pass — could not run any
of this):

1. Quicktest map on a scratch world with `RM_TarShallow` present: confirm a
   pawn standing in tar actually picks up `RM_Filth_Tar` and tracks it onto
   an adjacent `RUT_Duckboards` cell within a reasonable number of crossings
   (5% per-cell drop chance is vanilla's own rate, `Pawn_FilthTracker`) — and
   confirm the fouled cell's walk speed reads visibly lower.
2. Confirm `RUT_Glasswalk`'s displayed WalkSpeed tooltip reads ~80% and never
   100% for a normal colonist, and that a hauling/sprinting pawn occasionally
   staggers (StunFor) with a "RM_GlasswalkSlip" message and no HP loss.
   Tune `glasswalkSlipChancePerSweep` by feel if it reads too rare/frequent.
3. Confirm both terrains are actually placeable via the normal floor
   designator on ordinary Sump ground (Light affordance) — not yet checked
   in-engine.
4. **DONE, `SUMP_TAR_NASTINESS_1` (2026-09-24)**: `RM_Filth_Tar` now ships
   three placeholder blob sprites (procedurally drawn, not hand-authored)
   and both `src/DEPLOY_HOLD.txt` entries named above are lifted and
   deployed — live proof still owed that duckboards actually foul and slow
   in game, only that the def itself no longer blocks it.
5. `RM_Brindeth` (duckboards' wood) still doesn't exist — that cost is
   still a WoodLog placeholder. Glasswalk's own cost is **REPOINTED**
   (`SUMP_TAR_NASTINESS_1`) from Chemfuel to the real `RUT_Bitumen`; the
   bitumen/dig-barrel supply chain that would let a colony actually PRODUCE
   `RUT_Bitumen` is still unbuilt (flagged on that def's own header).
6. Not touched: ship-buildable placement aboard the gravship specifically
   (`BIOME_SHIP_CONTRIBUTIONS_1`) — should work automatically (ordinary
   Light-affordance floor) but unverified in-engine.
