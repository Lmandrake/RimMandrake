# PIT_LEGACY_CODE_RETIRE_1 — Delete the old Pits building model from FlowWorks (21 pit defs, dig chain, PitsMod, escape, fittings)

Part of the pit collapse (`PIT_SUPERDEEP_COLLAPSE_1` carries the rulings; `design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md` is the one model). A pit is a canal cell dug to SUPERDEEP (D=4) and nothing else.

## spec
The table in §4 of the unified model is the list. In short:
- RETIRE `Defs/Pits/ThingDefs/*` (18 concrete + 3 abstract — the last `TrapSpikeArmed` texPaths in the pit tree), `RM_DigPitDeeper` Designation/Job/WorkGiver, `RM_PinnedInPit` (DEFAULT).
- RETIRE `Source/Pits/`: Holding/, Escape/, DigStage/ (6), Fitting/ (3), `PitsMod.cs`, `Debug/PitDebugActions.cs`, `SelfTest/` (+ csproj).
- REWIRE: surviving toggles (`trapTriggerEnabled`, `trapSensitivityMultiplier`, `fallDamageEnabled`, `fallDamageMultiplier`) into `RimMandrakeFlowWorksSettings`; `RimMandrakePits_DefOf` merged into `RimMandrakeFlowWorks_DefOf` (hediffs `RM_PitDrowning`, `RM_PitExposure` only); cell-level debug actions in `FlowWorksDebugActions.cs`.
- Keep `PitCoverTier.cs` and `TerrainMimicPrinter` (the cover item uses them).
- Lift `CompPitFitting.OccupyingLiquid()` into the fill-effects code before deleting.
- `bridgetools/JawaBench.BridgeTools/JawaBenchBedTools.cs`: drop PitCell gizmo references.
- `About.xml`: the `mandrake.rm.pits` prose line goes.

## verify
`winbuild.py FlowWorks` 0 errors; `run_selftests.py` N/N; `validate_patch.py` 0 errors; a def census shows none of the 26 retired defNames and no FlowWorks def on `Things/Building/Security/TrapSpikeArmed` except `RM_Ladder` until its art lands; one FlowWorks settings screen. Saves: 0 of 41 hold any retired def (MEASURED 2026-10-02) — re-check before deleting.

## criteria
`src/RimMandrake/FlowWorks/Source/Pits/` holds only the cover trigger/tier and the terrain-mimic printer, or is gone with those moved.

## depends
`SUPERDEEP_HOLDER_RETIRE_1` (the holder inherits from `Building_OpenPit`).

## northstar
O1 def census row: the 26 retired defNames are absent (sanity probe: `RM_Channel_Superdeep` present); the settings floor lists the four rehoused toggles and no `struggle`/`escape` toggle.
