# FlowWorks 0.1.0 — blind challenge, cycle 2 (run judge-1794833810)

## Start time
2026-11-16T12:57:30Z (UTC), written before any input was opened.

## Changed files to bars
`git diff --name-only 0356fed0f7 origin/main` (blind_challenge excluded): 228 files [measured]. Mod and kernel files only
(ledger shards, in_game evidence, journal, test table and SelfTest are records, not bar inputs):

| changed file(s) | bars whose inputs it touches |
|---|---|
| `Source/RM_SheetMath.cs` (+5) | **inv_overflow_sheet** (offline) |
| `Source/Machinery/RM_ConversionMath.cs` (+7/-) | **inv_converters** (offline) |
| `Source/Sprinklers/RM_SprinklerKernel.cs`, `RM_SprinklerSettings.cs` | **inv_sprinklers** (offline) |
| `Source/Drilling/Building_LiquidDrill.cs` (+4) | **inv_drilling** (offline; caller of RM_DrillSurveyMath) |
| (no thirst file changed) | **inv_bottles_thirst** (offline): lane 1 still rerun as a decider bar |
| `Source/RM_TossFlame.cs` (new), JobDef `RM_TossFlame` | inv_toss_flame, toss_flame_from_rim, moat_raid_sequence |
| `Source/Superdeep/RM_RaiderFetchFallen.cs` (new), `RM_RaiderTrench.cs`, `FlowWorks_RaiderTrench.xml`, `FlowWorks_RaiderTrenchDuties.xml`, JobDef `RM_RaiderFetchFallen` | inv_raider_fetch_fallen, raiders_fetch_their_fallen, trench_gives_cover, inv_trench_cover |
| `Source/RM_LiquidCoating.cs` (new), `FluidDef.cs`, `FlowWorks_Fluids.xml`, `FlowWorks_PitFluids.xml`, `Pit_Hediffs.xml` (RM_LiquidCoat) | inv_liquid_coating, inv_liquid_roster, inv_pits |
| `Source/RM_MapComponent_Excavation.cs` (+2) | inv_dig_depth |
| `Source/RimMandrakeFlowWorksMod.cs`, `Keyed/FlowWorks_Keys.xml`, `_DefOf.cs`, `.csproj`, DLL + srchash | inv_settings (and the build of everything above) |
| `Source/RM_NorthstarProofs.cs`, `Machinery/RM_WreckedLinksProof.cs`, `northstar/*.py`, `validation.py`, `selftest_*.py` | proof harness for the live leaves: moat_raid_sequence, drained_hole_is_a_prison, covered_pit_springs, island_bridges_trap_and_fail, ice_cuts_and_melts, pawn_height_follows_depth, hose_reads_as_hose, source_pays_and_refills, walk_moat_season, raiders_fetch_their_fallen, trench_gives_cover |
| `src/RimMandrake/Utils/selftest_flowworks_stock.py` | the offline deciders T_SHEET, T_CONVERT, T_THIRST, T_DRILL, T_SPRINKLER (lane 2 reruns) |

Lane-1 scope: the 5 offline bars in full (their kernels), plus one `not_kernel` row per game-side bar above.

## Lane 1
Written blind from record.json's inventory rows, sheet.md, plan.md, bars.md, the shipped settings (defaults and slider
ranges) and the kernels `RM_SheetMath.cs`, `RM_ConversionMath.cs`, `RM_DrillSurveyMath.cs`, `RM_SprinklerKernel.cs`,
`RM_ThirstMath.cs` (with `RM_Volume.cs`, `RM_FireMath.cs`, `RM_StockMath.cs` linked to compile). Command:
`python3 design/concepts/FlowWorks/version/blind_challenge/cycle_2/lane1/run_lane1.py` (about 3 s).

- **60 rows: 39 PASS, 0 FAIL, 1 INFO, 20 UNSETTLED** [measured]. The 20 UNSETTLED are `not_kernel` rows, one per
  game-side bar whose inputs changed (each names only its own bar; all owed to Stage 6, none an offline bar).
- Per offline bar [measured]: inv_overflow_sheet 16/16 PASS (600 random op sequences with save/load, ledger closing to the
  dL after every op; save/load continuation; order-free spills; preview exact; crop week and its slider; tiers; levelling;
  freeze; cap lowering; sink; door seal; soak; 648 settings-extreme runs), inv_converters 6/6, inv_drilling 4/4,
  inv_sprinklers 5/5 + 1 INFO, inv_bottles_thirst 8/8.
- Sanity: the instrument can fail. Dropping `s.Soaked += take` in the sheet kernel and the cap headroom in
  `CapAccrued` turned 4 rows red [measured, /tmp, before commit].
- INFO worth the steward's eye (not faults): the overflow master switch `sheetOverflowEnabled` ships OFF
  (`RM_SheetSettings.cs:21`, "until the Stage 4 live acceptance validates it"); radius choices water 9 / 25 / 45 squares.

## Lane 2 reruns
(pending)

## Planted
(pending)

## Faults
(pending)

## Fixes
(pending)

## Steward's decisions enacted
(pending)

## Tests edited
(pending)

## Unsettled
(pending)

## Exit
(pending)

## Owed
(pending)
