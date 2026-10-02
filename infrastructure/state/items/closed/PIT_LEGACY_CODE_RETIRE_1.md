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

## evidence (2026-10-02, FOUNDRY helper; uncommitted at writing — FOUNDRY commits and closes)
- Saves re-checked: 63 `.rws` (Saves incl. archive, infrastructure/state, deployed); probe `<def>Wall</def>` in 62. Retired names appear 414× but only as `<li>` list entries (190), `<thingDef>` history/price records (170) and `<Workgiver>` priority keys (54) in 17 saves; **0 as `<def>` (no placed Thing)**. Those references drop on load with a cross-reference warning; accepted (world remake is last).
- Removed: 26 defs (18 concrete + 3 abstract pit ThingDefs, RM_DigPitDeeper ×3, RM_PinnedInPit, RM_SuperdeepPit with the holder item); `Source/Pits/` Holding/, Escape/, DigStage/ (6), Fitting/ (3), Debug/, SelfTest/ (+csproj), PitsMod.cs, RimMandrakePits_DefOf.cs, the dead Building_TerrainMimicCover class; Pit_Keys.xml; `Utils/selftest_pit_logic.py`. `Source/Pits/` now holds only Trigger/ (CompPitCoverTrigger via `IPitCoverHost`, no def carries it until PIT_COVER_FALL_REWIRE_1), PitCoverTier, TerrainMimicPrinter.cs. Four toggles rehoused into RimMandrakeFlowWorksSettings; RM_PitDrowning/RM_PitExposure merged into RimMandrakeFlowWorks_DefOf (writers owed by their REWIRE items); one FlowWorks settings screen (+ RiverSteam).
- Checks: winbuild 0 errors; run_selftests 119/119; validate_patch 0 errors; O1 census (26 retired absent, only RM_Ladder on TrapSpikeArmed; red against HEAD defs), O2 25 toggles + 2 Mod screens + no struggle/escape setting. Live `validation_v2_result_20261002T145340.json` GREEN 63/0/12 UNBUILT, `--compare` SAME vs both earlier runs.
- Left outside FlowWorks (precedent comments only, not code): FeverWood RUT_FeverTrunkCore.xml, UtinniPatches RUT_GreatboleCore.xml (cite RM_SuperdeepPit), Greentide hediffs (cites RM_PinnedInPit), Utils selftest_colony_visibility/selftest_stun_scaling/bridgetools selftest_tool_metadata (cite selftest_pit_logic.py), loadsweep/DECISION_STRINGS.md, modcheck suite.py/selftest.py/judge.py examples, Droidworks/Inhabited/RimProperty validation.py ("same shape as PitsSettings").
