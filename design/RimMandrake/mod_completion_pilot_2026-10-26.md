# Mod completion pilot -- 2026-10-26 (MOD_COMPLETION_MEASURE_HOW_DONE_IS_DONE)

Status: PILOT, for the owner to judge before any skill is made. Instrument: `src/RimMandrake/Utils/mod_completion.py <Mod> [--json F] [--md F] [--asof YYYY-MM-DD]`.
Runs: `D:\ClaudeWork\rimmandrake\mod_completion\r1.md` (first, invalid) to `r6.md` (this report).

## Headlines (as of 2026-10-26)

| | GimmeSomeSlack | FlowWorks |
|---|---|---|
| Inventory (denominator) | 31 (6 player-facing defs + 25 setting switches) | 406 (defs, terrain depth families grouped, + switches) |
| Verified working at L2+ | **77.4%** (24/31; 45% without the owner-walk credit) | **18.7%** (76/406), 3.4% broken |
| Art explicitly accepted, of in-use slots | 5.4% (6 slots; +94.6% only seen, unchanged, in the owner's L4 walk) | **70.7%** (389 of 550 in-use slots) |
| Settledness | still finding: 10 bugs in the last 2 weeks vs 0 before (slicing/perf work) | still finding: 175 bugs in the last 2 weeks vs 13 before |
| Open bug items / waiting on owner | 4 / 0 | 63 / 10 |

Nothing here is a single %complete: the parts have no shared unit, so none is invented. The closest thing to a
"how done" figure is the verified-working share. Read it next to settledness: a mod is done when that share is high
AND bugs have stopped arriving.

## Evidence sources (what feeds each section)
1. Inventory: Defs XML parsed (Abstract skipped). Player-facing types only: ThingDef without labels, and motes, projectiles, gas and attachments, are dropped. TerrainDef is grouped into depth families. Bool `Scribe_Values.Look` settings count as "Switch" entries, standing in for mechanics.
2. Works: MOD-class rows in proof result JSONs (live = L2, offline = L1; the latest row per script and row id wins) plus ledger verify events at L2+ (the latest per item and criterion wins). A row or verify counts for an entry when it names the defName, the setting key or its snake_case form, or the label. Owner verifies at L3+ that name the whole mod credit every name present in the mod at the walk's sha. A later L2 FAIL overrides that credit.
3. Art: the art ledger's live slots and owner keeps/rejections. Review-sheet sidecar slot rulings count only when they carry a human timestamp. "In use" means the slot is reached by a def texPath or a C# string literal. "Owner-walked" means the slot was present at the owner's whole-mod walk and is unchanged since.
4. Waiting on owner: open items with needs=owner, with their ages.
5. Trends: items attributed to the mod by id keywords, a title key in the subject position, the FlowWorks lane patterns, or a close commit touching only this mod. Bugs are BUGGY_KINDS minus TESTENV_ items. Per ISO week the table also shows code_review records, live runs, MOD fail rows and L2 verifies.

## GimmeSomeSlack report
#### GimmeSomeSlack (as of 2026-10-26)

**Headline:** 77.4% of 31 inventory entries verified working at L2+ (0.0% with a failing latest L2 row); art explicitly accepted 5.4% of in-use slots (+94.6% only seen, unchanged, in an owner whole-mod walk); settledness **still finding** (bugs filed last 2 wk 10 vs prior 2 wk 0); 4 open bug items; 0 items waiting on the owner. No composite score: the parts do not share a unit.

**1. Inventory** 31 entries: {'ThingDef': 4, 'JobDef': 1, 'HediffDef': 1, 'Switch': 25}. Raw def types: {'MapMeshFlagDef': 2, 'ThingDef': 4, 'DesignationDef': 1, 'JobDef': 1, 'WorkGiverDef': 1, 'ThingStyleDef': 40, 'HediffDef': 1, 'HistoryEventDef': 1}.

**2. Works** {'works': 24, 'unverified': 7} from 162 live proof runs (162 result files), 18 L2+ verify events, 0 player truths; 0 'works' credited by label match only, 10 only by an owner whole-mod walk (UNROUTABLE_CORD_BUILD_DIVE_THROUGH_WALLS L4 2026-10-16 @fc932419a783: GimmeSomeSlack all looks great! Verified.).

| type | works | broken | offline-only | unverified |
|---|---|---|---|---|
| HediffDef | 1 | 0 | 0 | 0 |
| JobDef | 0 | 0 | 0 | 1 |
| Switch | 19 | 0 | 0 | 6 |
| ThingDef | 4 | 0 | 0 | 0 |

Broken (0): 

Unverified (7): RM_RestringSpan, kineticSway, theftGoodwill, keepWiresOnGravship, cutWiresOnOwnerChange, dripLoops, slideUnder

**3. Art** 120 live texture slots, 111 reached by a def texPath or C# literal; owner-accepted 6 (6 in use). By class: {'owner-kept': 5, 'owner-kept-sheet': 1, 'owner-walked (not referenced by a def texPath or C# literal)': 9, 'owner-walked': 105}. Regen-looping (>=2 rounds): none. texPaths with no art: 0 of 24 [].

**4. Waiting on owner** 0: 

**5. Settledness (ISO week starting)**

| week | bugs filed | code reviews | defects from code review | live runs | MOD fail rows / MOD rows | L2 verifies not-pass / all | live-found bugs | refiled |
|---|---|---|---|---|---|---|---|---|
| 2026-09-28 | 0 | 0 | 0 | 126 | 55 / 2280 | 0 / 0 | 0 | 0 |
| 2026-10-05 | 0 | 98 | 0 | 25 | 26 / 1974 | 0 / 5 | 0 | 0 |
| 2026-10-12 | 2 | 123 | 0 | 8 | 4 / 234 | 1 / 3 | 2 | 0 |
| 2026-10-19 | 4 | 58 | 0 | 3 | 3 / 20 | 0 / 5 | 3 | 1 |
| 2026-10-26 | 4 | 49 | 1 | 0 | 0 / 0 | 5 / 5 | 3 | 0 |

Refiled/regression items: 1 ['GSS_WATER_STUB_FIX_PASSED_LAST_WEEK']

## FlowWorks report
#### FlowWorks (as of 2026-10-26)

**Headline:** 18.7% of 406 inventory entries verified working at L2+ (3.4% with a failing latest L2 row); art explicitly accepted 70.7% of in-use slots (+0.0% only seen, unchanged, in an owner whole-mod walk); settledness **still finding** (bugs filed last 2 wk 175 vs prior 2 wk 13); 63 open bug items; 10 items waiting on the owner. No composite score: the parts do not share a unit.

**1. Inventory** 406 entries: {'FluidDef': 14, 'JobDef': 29, 'TerrainFamily': 46, 'ThingDef': 144, 'RM_LiquidBodyDef': 4, 'LiquidDef': 23, 'RecipeDef': 14, 'HediffDef': 7, 'ThoughtDef': 8, 'NeedDef': 1, 'MentalBreakDef': 1, 'MentalStateDef': 1, 'Switch': 114}. Raw def types: {'DesignationDef': 4, 'FluidDef': 14, 'JobDef': 29, 'TerrainDef': 113, 'ThingDef': 147, 'WorkGiverDef': 17, 'ThingStyleDef': 116, 'FleckDef': 10, 'GenStepDef': 5, 'RM_LiquidBodyDef': 4, 'LiquidDef': 23, 'RecipeDef': 14, 'ThingCategoryDef': 2, 'RM_LiquidReactionDef': 1, 'HistoryEventDef': 1, 'DesignationCategoryDef': 1, 'MapMeshFlagDef': 1, 'HediffDef': 7, 'ThoughtDef': 8, 'DrawStyleCategoryDef': 1, 'TerrainAffordanceDef': 1, 'RM_PlacerPoolDef': 1, 'RM_RiverDriftDef': 12, 'NeedDef': 1, 'MentalBreakDef': 1, 'MentalStateDef': 1, 'ThinkTreeDef': 3}.

**2. Works** {'works': 76, 'unverified': 316, 'broken': 14} from 240 live proof runs (240 result files), 233 L2+ verify events, 0 player truths; 4 'works' credited by label match only, 0 only by an owner whole-mod walk (none).

| type | works | broken | offline-only | unverified |
|---|---|---|---|---|
| FluidDef | 4 | 2 | 0 | 8 |
| HediffDef | 5 | 0 | 0 | 2 |
| JobDef | 15 | 0 | 0 | 14 |
| LiquidDef | 4 | 2 | 0 | 17 |
| MentalBreakDef | 1 | 0 | 0 | 0 |
| MentalStateDef | 0 | 0 | 0 | 1 |
| NeedDef | 0 | 0 | 0 | 1 |
| RM_LiquidBodyDef | 0 | 0 | 0 | 4 |
| RecipeDef | 0 | 0 | 0 | 14 |
| Switch | 7 | 1 | 0 | 106 |
| TerrainFamily | 8 | 4 | 0 | 34 |
| ThingDef | 28 | 5 | 0 | 111 |
| ThoughtDef | 4 | 0 | 0 | 4 |

Broken (14): RM_Fluid_Chemfuel <- suspension_bridge_proof.py:GRATE_fire_burns_people_above (2026-10-23); RM_Fluid_BoilingWater <- glow_tank_live.py:GLOWTANK_SALT_DRAWN_ONE_UNIT (2026-10-22), GLOW_TANK_LIQUID_FEED_1:A2 (2026-10-09); RM_Fill_Water <- fw_live_checks.py:W1_wakes_terrain_walked (2026-10-11); RM_Ladder <- WATERED_PIT_FIX_NO_WAY_IN: (2026-10-24); RM_PitRamp <- PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH: (2026-10-23), WATERED_PIT_FIX_NO_WAY_IN: (2026-10-24); RM_Liquid_FreshWater <- fw_live_checks.py:L5_switched_off_hose_spills (2026-10-11), TANK_DEBUG_BUILD_FILL_AT_WILL:A1 (2026-10-23); RM_Liquid_BoilingWater <- glow_tank_live.py:GLOWTANK_SALT_DRAWN_ONE_UNIT (2026-10-22), GLOW_TANK_LIQUID_FEED_1:A2 (2026-10-09); RM_SlimeGreen <- fw_live_checks.py:W1_wakes_terrain_walked (2026-10-11); RM_Tar <- fw_live_checks.py:W1_wakes_terrain_walked (2026-10-11); RM_WaterBoiling <- glow_tank_live.py:GLOWTANK_SALT_DRAWN_ONE_UNIT (2026-10-22), GLOW_TANK_LIQUID_FEED_1:A2 (2026-10-09); RM_Filth_LiquidSpill <- SUSPENSION_GRATE_BUILD_LET_THE_FIRE_UP:A1 (2026-10-23); RM_LiquidTank <- glow_tank_live.py:GLOWTANK_SALT_DRAWN_ONE_UNIT (2026-10-22); RM_UniversalPipe <- HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD:A5 (2026-10-23); liquidWakesEnabled <- fw_live_checks.py:W1_wakes_terrain_walked (2026-10-11)

Unverified (316): RM_Fluid_SlimeRed, RM_Fluid_SlimeWhite, RM_Fluid_SlimeYellow, RM_Fluid_Oil, RM_Fluid_Poison, RM_Fluid_Blood, RM_Fluid_Astrofuel, RM_Fluid_IcyWater, RM_OperateLadderJob, RM_OperateGateJob, RM_CaptureDown, RM_RaiderFillTrench, RM_RaiderFetchFill, RM_RaiderTakeLadder, RM_RaiderChopForLadder, RM_ClimbOverWall, RM_Fill_Oil, RM_Fill_Poison, RM_Fill_Blood, RM_Fill_Chemfuel, RM_Fill_Astrofuel, RM_Fill_BoilingWater, RM_Fill_IcyWater, RM_WaterChest, RM_Fill_SlimeRed, RM_Fill_SlimeGreen, RM_Fill_SlimeWhite, RM_Fill_SlimeYellow, RM_Lakebed, RM_SecurityGrateDoor, RM_FlowSource, RM_FlowSink, RM_FlowMeter, RM_LevelHolder, RM_TimerSwitch, RM_MapEdgeSetter, RM_CurrentPainter, RM_LiquidThermostat, RM_LadderSteel, RM_Swale, RM_PitGuardrail, RM_StationSign, RM_LiquidDrill, RM_WashBottleJob, RM_FillFromTankJob, RM_Body_TheScald, RM_Body_TwilightSea, RM_Body_GreySea, RM_Body_TheChill, RM_Liquid_IcyWater, RM_Liquid_ToxicWater, RM_Liquid_ReactionLiquor, RM_Liquid_Tar, RM_Liquid_NotDrinkable, RM_Liquid_Chemfuel, RM_Liquid_SlimeRed, RM_Liquid_SlimeGreen, RM_Liquid_SlimeWhite, RM_Liquid_SlimeYellow, RM_Liquid_LivingSlime ...

**3. Art** 636 live texture slots, 550 reached by a def texPath or C# literal; owner-accepted 430 (389 in use). By class: {'donor (not referenced by a def texPath or C# literal)': 4, 'owner-kept (not referenced by a def texPath or C# literal)': 35, 'owner-kept': 357, 'owner-kept-sheet (not referenced by a def texPath or C# literal)': 6, 'owner-kept-sheet': 32, 'owner-rejected': 1, 'unreviewed (not referenced by a def texPath or C# literal)': 41, 'unreviewed': 160}. Regen-looping (>=2 rounds): {'RM_Ladder': 3, 'RM_LadderPortable': 3, 'RM_LadderSteel': 3, 'RM_LiquidPump_Modern': 3, 'RM_PipeFaucet_Modern': 3, 'RM_PumpingStation_Kludged': 2, 'RM_SprinklerHead_Modern': 3, 'RM_SuspensionAnchor_Steel_Scrapper': 3, 'RM_SuspensionAnchor_Timber_Scrapper': 3, 'RM_UniversalPipe_Modern': 3, 'RM_UniversalPipe_Scrapper': 3}. texPaths with no art: 0 of 192 [].

**4. Waiting on owner** 10: HOSE_JOINTS_REDESIGN_PUMP_TOO_PUNY (10 d); LIQUID_CONTAINERS_REDRAW_NO_MANA_POTIONS (10 d); FLOWWORKS_BARS_JUDGE_FIVE_IN_ONE_SITTING (9 d); GUARDRAIL_ART_RESKIN_BORROWED_FENCE (8 d); CANAL_OVERFLOW_BUILD_EVERY_PUDDLE_AUDITED (5 d); PIT_TRAVEL_TAGS_VET_LORE_FIRST_GUESS (5 d); REEL_FAIRLEAD_DECIDE_AFTER_THE_WALK (3 d); LADDER_TEXT_RECONCILE_STEEL_NOT_WOOD (2 d); SCRAPPER_PIPE_REDRAW_VERDIGRIS_DASH_RHYTHM (2 d); HOSE_NET_DIAGNOSE_HALF_HOSE_HALF_PIPE (2 d)

**5. Settledness (ISO week starting)**

| week | bugs filed | code reviews | defects from code review | live runs | MOD fail rows / MOD rows | L2 verifies not-pass / all | live-found bugs | refiled |
|---|---|---|---|---|---|---|---|---|
| 2026-09-21 | 1 | 0 | 0 | 0 | 0 / 0 | 0 / 0 | 0 | 1 |
| 2026-09-28 | 2 | 120 | 0 | 14 | 9 / 931 | 0 / 0 | 0 | 0 |
| 2026-10-05 | 6 | 189 | 0 | 37 | 59 / 1846 | 2 / 25 | 3 | 1 |
| 2026-10-12 | 14 | 862 | 0 | 73 | 87 / 2392 | 18 / 50 | 10 | 3 |
| 2026-10-19 | 107 | 1326 | 0 | 116 | 131 / 1668 | 36 / 149 | 75 | 5 |
| 2026-10-26 | 59 | 241 | 13 | 0 | 0 / 0 | 6 / 9 | 22 | 5 |

Refiled/regression items: 15 ['V2_LADDER_ROWS_DIAGNOSE_STAGE_FRIGHT', 'DRAWBRIDGE_LEAF_FIX_RAISED_STILL_DRAWN', 'HOSE_BUILDINGS_FIX_BATTERY_HIDE_AND_SEEK', 'HOSE_CROSSING_FIX_FLAT_AS_A_PANCAKE', 'TOGGLE_LADDER_FIX_REQUIRED_PAWN_ESCAPES_PIT', 'HOSE_RELAY_FIX_WAVE_FRAME_OVER_BUDGET', 'MACHINERY_LOOK_FIX_DECK_REPAINT_ON_SWITCH', 'LIQUID_TERRAIN_AUTHORED_TWICE_1']

## Validity check: GSS >> FlowWorks
Run 1 (r1) failed the check on works: GSS scored 29.0% working against FW 18.5%, and both mods read as "still finding" by a wide margin.
Every fix below corrects a defect in the instrument that holds for any mod. None was tuned to the answer.
1. **Attribution keywords.** Generic `WIRE`/`CONDUIT` matched CONTAGION_PEAKS_WIRE_*, PHONE_PUSH_WIRE and MESSY_CONDUIT_MOD_1, which belongs to a different mod. They are narrowed to `FALLEN_(WIRE|LINE|CORD)` and `TAP_?CLAMP`.
2. **Settledness used ISO weeks.** With an as-of date on a Monday, the one-day partial week was scaled up ×7. It now compares a rolling 14 days against the 14 days before.
3. **Case mismatch.** Setting keys are camelCase (`fallenWireShock`) but proof row ids are snake_case (`P7_fallen_wire_shock_live`). The snake form is now matched as well.
4. **C#-drawn textures.** GSS draws its cords from C# (`Dir + "Strand_Jawa"`), so 80 of its 120 slots looked unused. Source string literals now count as "in use": full paths as prefixes, bare quoted names against a slot's file stem (now 111 of 120 in use). Only def texPaths in the mod's own namespace can be "missing" (probe: a fabricated path is reported).
5. **Owner whole-mod walk.** "GimmeSomeSlack all looks great! Verified." (OWNER L4 on UNROUTABLE_CORD_BUILD_DIVE_THROUGH_WALLS @fc932419a783, after the 31-station walk save) names no def, so it credited nothing. Owner L3+ passes whose words name the mod now credit every name present at that sha. The rule is the same for every mod; FW has no such verify.
6. **Sheet rulings** exist only in `*.decisions.json` sidecars, never in the art ledger. They are now read, human-timestamped entries only. The 2026-10-11 GSS sheet holds 147 agent prefills and 4 real picks.
7. **Close-sha attribution** credited GSS with a bridge-tool bug and a Pyrelands selftest bug, because those commits also carried GSS files. The close commit must now touch this mod only.
8. **TESTENV_ items** are the test environment's own hazards: a monolith letter, fixture vitals. They are no longer counted as mod bugs.
9. **Title mentions** now count only in the subject position, the first 40 characters. "on the GSS theft run" names the site of a run, not the subject.

Result r6: on works, GSS reaches 77.4% against FW 18.7%. That holds **without** fix 5 too: 45% against 19%. On open bugs, GSS has 4 against FW's 63. On owner waits, GSS has 0 against 10. Art is the one axis where FW leads. The owner kept 392 FW slots one by one, but explicitly accepted only 6 GSS slots. The rest of GSS art is "seen in his L4 walk", and the 2026-10-11 GSS sheet was ruled "Retire and rebuild". The rebuilt sheet (2026-10-26) is still an unruled prefill. That reading is true, not an instrument fault, and it is reported as such.
GSS still reads "still finding" (10 bugs in 2 weeks). This is real: the r9 slicing and perf work (GSS_SLICE_FIX_*, GSS_BUILD_FIX_SLICE_GROWS_WITH_CORDS) is open. Per inventory entry, though, it is still lower than FW's rate.

## Known blind spots
- **Biggest: evidence is never checked for staleness against later code.** A row that passed at sha X still counts after the code it proved has changed. Fix 5 makes this worse for GSS: the walk was at fc932419a783, and the slicing rewrite came after it.
- Matching is lexical (defName, key, snake form, label). An entry whose proof row uses another name reads "unverified".
- Attribution is hand-picked keywords plus the FW lane file. A new mod needs its keys added.
- code_review records carry only a verdict, never a defect count. "Defects from code review" is inferred from item text.
- Setting switches stand in for mechanics. Mechanics with no switch (cord physics, theft) are invisible except through their defs.
- No player truths exist yet (design/RimMandrake/player_truth_testing_pilot_2026-10-26.md is a sibling pilot). Once they exist they will feed Works directly.
- Art: a pick on a sheet counts as acceptance even if the picked candidate was never installed. Vanilla-shaped paths (`Things/...`) are not checked for missing art.
- Owner-walk credit trusts that the walk covered every def present at its sha.
- C# bare-name matching (a quoted name equal to a slot file stem) can over-count "in use" when a name is quoted for another reason.
- Settledness counts bugs filed, not severity, and ledger history before mid-October is thin.
