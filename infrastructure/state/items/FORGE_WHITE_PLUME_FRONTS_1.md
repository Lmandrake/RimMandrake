# FORGE_WHITE_PLUME_FRONTS_1 — white plume fronts

Split from `FORGE_GPT_ENRICHMENT_1` §4 (owner-picked). Built at `09ccb3ca5` (offline, L0): the builder answered the four
questions below (record: `Transient/work_PLUME_20261003.md`; owner review owed as A7).

## spec (from the parent)

Quench steam rolls out from newly crusted vents as moving fronts. They briefly obscure shooters, soak the ground,
and heat exposed pawns faster through **vanilla heatstroke** (`SOLAR_HEAT_EXPOSURE_1`, one kind of heat).
Vapour-adapted creatures move normally inside them. Build: a phase-bound cell front, flecks, a ranged-accuracy
modifier, AI avoidance, and an adapted-species exemption.

## what exists to build on

`RM_GameCondition_ForgeCycle` knows every newly crusted cell (`FrozenCells`, filled in batches through the
freeze phase). Vanilla 1.6 has `GasType.BlindSmoke`. If it is used for the "obscure" half, ranged accuracy and AI
avoidance come from vanilla and no Harmony is needed. That is a suggestion, not a ruling.

## what was built (09ccb3ca5)

**No defs.** The fronts are code plus six Mod Settings: `RM_MapComponent_PlumeFronts` in
`src/RimMandrake/TheForge/Source/RM_ForgePlumeFronts.cs`, fed by `FreezeBatch` in `RM_GameCondition_ForgeCycle`.
It reuses vanilla `GasType.BlindSmoke` and vanilla `Filth_Water`. Settings: `plumeFrontsEnabled`,
`plumeObscureEnabled`, `plumeSoakEnabled`, `plumeHeatEnabled`, `plumeAdaptedExempt`, `plumeStrength`.

## builder-chosen answers (owner review owed, A7)

1. Obscuring: vanilla blind smoke, so ranged accuracy and line-of-sight refusal come from vanilla. There is no
   pathing avoidance.
2. Heat: a Harmony postfix adds +25 °C × strength to `Thing.AmbientTemperature` for flesh pawns in a front cell.
   Vanilla `HediffGiver_Heat` then gives the heatstroke.
3. Soak: vanilla `Filth_Water` puddles that evaporate in 0.2–0.4 days. FlowWorks is not used.
4. Vapour-adapted: any pawn carrying `RM_CompVaporDrifter` (`groundHazardImmune`), behind the toggle `plumeAdaptedExempt`.
