# FlowWorks + GSS: GPT high-depth review and validation compression (2026-10-23)

BENCH. GPT (gpt_consult default model, high effort) reviewed the package in 24 parts sharing one instruction set, then one compression consult.
Raw replies: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\` (one per part, plus `FINAL_compression.md`). Finding table: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\findings.tsv`; verdicts: `verdicts.tsv`. No code was fixed and no validation script was changed.

| | count |
|---|---|
| findings GPT raised | 194 |
| confirmed | 121 (27 MAJOR, 94 MINOR) |
| merged into another finding | 1 |
| rejected | 2 |
| unverified (item GPT_FW_REVIEW_VERIFY_REMAINING_FINDINGS) | 70 |
| items filed | 119 + 1 umbrella |

Severity in the tables is ours after verification, not GPT's.

## Confirmed findings

| finding | sev | item | where | defect |
|---|---|---|---|---|
| FA_core_sim_1.1 | MAJOR | DUG_WATER_FILL_FIX_NO_CANAL_DEBIT | `src/RimMandrake/FlowWorks/Source/LiquidTypes/RM_LiquidBottleUtility.cs`:189–199 (`TryDebitTerrain`) | Filling containers from dug freshwater creates liquid without debiting the canal |
| FA_core_sim_1.2 | MAJOR | DRILL_FILL_FIX_LOSES_FRACTIONAL_BRIM | `src/RimMandrake/FlowWorks/Source/Drilling/Building_LiquidDrill.cs`:172–210 (`TickRare`) | A drill silently loses liquid when filling a fractional outlet to the brim |
| FA_core_sim_1.3 | MAJOR | DRAWBRIDGE_HOSE_FIX_STAYS_LINKED_RAISED | `src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNet.cs`:1032–1045 (`RM_HoseLinks.Ends`) | Raised drawbridges do not disconnect hoses with Intake or Outflow roles |
| FA_core_sim_1.4 | MINOR | HOT_RELEASE_FIX_OWN_WET_TERRAIN | `src/RimMandrake/FlowWorks/Source/Machinery/Kits/RM_HotLiquid.cs`:54–56 (`IsFillOf`) | Hot freshwater releases no longer recognize their own wet terrain |
| FA_core_sim_1.5 | MINOR | PUMP_SOURCE_FIX_REJECTS_PARTIAL_DRAW | `src/RimMandrake/FlowWorks/Source/LiquidTypes/Building_LiquidPump.cs`:296–299, 355–370 (`TryDraw`) | Pump source selection rejects affordable partial draws before reaching partial-draw code |
| FA_core_sim_1.6 | MINOR | TANK_BOTTLE_FILL_FIX_IGNORES_STOCK_TARGET | `src/RimMandrake/FlowWorks/Source/LiquidTypes/WorkGiver_FillBottleFromTank.cs`:24–42, 50–67 (`HasJobOnThing`, `JobOnThing`) | Automatic filling from tanks ignores the colony bottle stock target |
| FA_core_sim_1.7 | MINOR | FLOOD_EXPIRY_FIX_FULL_CELL_TRAVERSAL | `src/RimMandrake/FlowWorks/Source/Flood_FlowWorks.cs`:102–117, 468–471 (`FloodingTicks`, `ExpiryTick`, `PlaceFluid`) | Flood expiry counts paid tiles but ignores traversal through full cells |
| FA_core_sim_1.8 | MAJOR | TAR_GLASS_FLOOD_FIX_UNREACHABLE_PATH | `src/RimMandrake/FlowWorks/Source/Flood_FlowWorks.cs`:496–502, 554–557 (`PlaceFluid`, `CoolFrontToGlass`) | The tar-to-glass flood path is unreachable with the current terrain ownership rules |
| FA_core_sim_1.9 | MINOR | LEVELLING_BUDGET_FIX_STARVES_LATER_HOSES | `src/RimMandrake/FlowWorks/Source/Machinery/RM_Levelling.cs`:120–148, 286–324 (`Tick`, `DugBody`) | Levelling’s walk budget permanently starves later hose components |
| FA_core_sim_1.10 | MINOR | IMMERSION_DAMAGE_WIRE_NEVER_APPLIED | `src/RimMandrake/FlowWorks/Source/LiquidTypes/LiquidCorrosion.cs`:87–91 (`DoCorrosionPass`) | Authored immersion damage is never applied |
| FA_core_sim_2.1 | MAJOR | DISABLED_LIQUID_FIX_LIMITLESS_SOURCE | `src/RimMandrake/FlowWorks/Source/RM_FlowKernel.cs:782–786` (`ExactTouchSource`) | Disabled natural liquids become limitless sources in the exact kernel |
| FA_core_sim_2.2 | MAJOR | UNLIMITED_SINK_FIX_FRACTIONAL_WATER | `src/RimMandrake/FlowWorks/Source/MapControls/RM_FlowTaps.cs:165–173` (`Building_RM_FlowSink.FlowPulse`) | An unlimited sink cannot remove fractional water |
| FA_core_sim_2.3 | MAJOR | LEVEL_HOLDER_FIX_REFILLS_FRACTIONAL_BASIN | `src/RimMandrake/FlowWorks/Source/MapControls/RM_LevelHolder.cs:96–118` (`Measure`, `HoldChannel`) | A level holder repeatedly fills an already satisfied fractional basin |
| FA_core_sim_2.4 | MINOR | WET_CELL_CENSUS_FIX_SHEETS_READ_DRY | `src/RimMandrake/FlowWorks/Source/RM_FluidIdentity.cs:79` (`ProofCensus`); `src/RimMandrake/FlowWorks/Source/MapControls/RM_FlowMeter.cs:81– | Wet-cell diagnostics report fractional sheets as dry |
| FA_core_sim_2.5 | MINOR | THERMOSTAT_FIX_IGNORES_SUBNOTCH_LIQUID | `src/RimMandrake/FlowWorks/Source/MapControls/RM_LiquidThermostat.cs:49–53` (`HeatInterval`) | Thermostats ignore liquid shallower than one notch |
| FA_core_sim_2.6 | MAJOR | LEVELLING_BANDS_FIX_STOPS_PAST_EIGHT | `src/RimMandrake/FlowWorks/Source/RM_FlowKernel.cs:1415,1559,1651–1653` (`LevelSetWetRegions`, `SolveRegion`) | Whole-notch levelling silently stops working below eight bands |
| FA_core_sim_2.7 | MINOR | RECESSION_SCAN_TAME_RERUN_PER_CANDIDATE | `src/RimMandrake/FlowWorks/Source/RM_BedMath.cs:308–325` (`RM_RecessionSet.Pick`) | Recession can rerun its entire articulation scan for every rejected candidate |
| FA_core_sim_2.8 | MINOR | POND_OUTLET_FIX_REJECTS_FRACTIONAL_ROOM | `src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidSpill.cs:68–74` (`Outlet`) | Pond outlets reject usable fractional room |
| FA_core_sim_2.9 | MINOR | TANK_THEFT_FIX_CHARGES_OWNER_USE | `src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidTheft.cs:47–53,105–107` (`TheftTick`, `PlayerReaches`) | Another faction’s own tank use can be charged as player theft |
| FA_core_sim_2.10 | MINOR | LINK_BUDGET_FIX_CATCHUP_OVERSTATES_FLOW | `src/RimMandrake/FlowWorks/Source/RM_LevellingMath.cs:144–146` (`Plan`) | Link-budget catch-up overstates passive flow rates |
| FA_core_sim_3.1 | MAJOR | FILL_IN_DESIGNATION_FIX_SCAN_INVALIDATED | `src/RimMandrake/FlowWorks/Source/WorkGiver_FillInCanal.cs:20–24,48` (`PotentialWorkCellsGlobal`, `HasJobOnCell`) | Deleting stale fill-in designations invalidates the active work scan |
| FA_core_sim_3.2 | MINOR | TERRAIN_DRINK_FIX_SMALL_POND_REFUSED | `src/RimMandrake/FlowWorks/Source/Thirst/RM_ThirstUtility.cs:488` (`TryFindDrinkCell`); `src/RimMandrake/FlowWorks/Source/RM_LiquidStock.cs: | Terrain drinking rejects ponds containing less than 1,000 L |
| FA_core_sim_3.3 | MINOR | DEHYDRATION_FIX_STAYS_WHEN_THIRST_OFF | `src/RimMandrake/FlowWorks/Source/Thirst/RM_ThirstProvider.cs:85–94` (`Reapply`); `src/RimMandrake/FlowWorks/Source/Thirst/Need_RM_Thirst.cs | Disabling thirst leaves existing dehydration permanently attached |
| FA_core_sim_3.4 | MINOR | SALT_BREAK_FIX_MISSES_POTABLE_SOURCES | `src/RimMandrake/FlowWorks/Source/Thirst/RM_SaltBreak.cs:84–96` (`PotableReachable`) | Salt-break eligibility overlooks reachable potable containers, water items and faucets |
| FA_core_sim_3.5 | MINOR | TANK_DRINK_FIX_LIQUID_SWAPS_MIDJOB | `src/RimMandrake/FlowWorks/Source/Thirst/RM_ThirstJobs.cs:245,254–259` (`JobDriver_RM_DrinkFromTank`) | A tank drink can silently change into a forbidden liquid during the job |
| FA_core_sim_3.6 | MINOR | CLIFF_SHOT_FIX_DEPENDS_ON_SHOOTER_END | `src/RimMandrake/FlowWorks/Source/RM_RelativeRulesMath.cs:227–250` (`ShotBlocked`) | Cliff shooting restrictions depend on which endpoint is the shooter |
| FA_core_sim_3.7 | MINOR | TRENCH_COVER_FIX_DECK_ERASES_UNDERPASS | `src/RimMandrake/FlowWorks/Source/RM_TrenchCover.cs:43–44,77–80` (`GroundDepthAt`, `BlockFor`) | Deck presence erases trench cover for occupants beneath an underpass |
| FA_core_sim_3.8 | MINOR | BODY_SPLIT_FIX_FISH_SHARE_SHRINKS | `src/RimMandrake/FlowWorks/Source/RM_WaterBodyMendGame.cs:366–368` (`RM_WaterBodyView.SplitOff`) | Three-way water-body splits distribute fish using a shrinking numerator |
| FA_core_sim_3.9 | MINOR | READOUT_PROOF_FIX_BYPASSES_MOUSEOVER | `src/RimMandrake/FlowWorks/Source/RM_NorthstarProofs.cs:293` (`ProofReadout`); `src/RimMandrake/FlowWorks/Source/RM_MouseoverDepth.cs:75–104 | The readout proof bypasses part of the actual mouseover implementation |
| FA_core_sim_4.1 | MAJOR | TIRED_SWIMMER_FIX_UNREACHABLE_SHORE | `src/RimMandrake/FlowWorks/Source/Swimming/RM_Swim.cs`:707–717 (`RM_Swim.NearestFooting`) | Tired swimmers can repeatedly choose an unreachable shore |
| FA_core_sim_4.2 | MINOR | OVERFLOW_DROWNING_FIX_NO_WARNING | `src/RimMandrake/FlowWorks/Source/Swimming/RM_Swim.cs`:542–545 (`RM_Swim.Tick`) | Overflow can drown a pawn without sending the drowning warning |
| FA_core_sim_4.3 | MINOR | SPREADING_FUEL_FIX_IRRIGATES_CROPS | `src/RimMandrake/FlowWorks/Source/Sheet/RM_MapComponent_Sheet.cs`:555–557, 644–649 (`EnginePulse`, `Effects`, `NoteNonWater`) | Newly spreading fuel or poison can irrigate crops |
| FA_core_sim_4.4 | MINOR | CROP_DROWNING_FIX_ONE_TIME_PUDDLE | `src/RimMandrake/FlowWorks/Source/Sheet/RM_MapComponent_Sheet.cs`:618–632 (`Effects`) | Crop drowning is a one-time puddle event rather than exposure of each crop |
| FA_core_sim_4.5 | MINOR | FROZEN_OVERFLOW_DIG_FIX_ICE_POURS_LIQUID | `src/RimMandrake/FlowWorks/Source/Sheet/RM_MapComponent_Sheet.cs`:833–862 (`HandOverTakenCells`) | Digging beneath frozen overflow transfers ice as liquid |
| FA_core_sim_4.6 | MINOR | WADING_SETTINGS_FIX_STALE_PATH_COSTS | `src/RimMandrake/FlowWorks/Source/Sheet/RM_MapComponent_Sheet.cs`:559–563; `src/RimMandrake/FlowWorks/Source/Sheet/RM_SheetSettings.cs`:144, | Changing overflow wading settings leaves cached movement costs unchanged |
| FA_core_sim_4.7 | MINOR | JOINED_WEIR_BREACH_FIX_CATCH_UNTOUCHED | `src/RimMandrake/FlowWorks/Source/Rivers/RM_Weir.cs`:362, 420–424, 459 (`CaptureFloating`, `Breach`, `WashCatch`) | A breach away from a joined wall’s head leaves the shared catch untouched |
| FA_core_sim_4.8 | MINOR | WEIR_CATCH_FIX_ESCAPES_CAP_RADIUS | `src/RimMandrake/FlowWorks/Source/Rivers/RM_Weir.cs`:123, 385–391, 407 (`CaptureFloating`, `HeldCatch`) | Catch placement can escape the radius used to enforce the catch cap |
| FA_core_sim_4.9 | MINOR | RETURNED_PRISONER_FIX_GRACE_LOST_ON_LOAD | `src/RimMandrake/FlowWorks/Source/TakenByLand/RM_TakenByLand.cs`:313, 450–453; `src/RimMandrake/FlowWorks/Source/TakenByLand/RM_TakenByLandK | Reloading removes the returned-prisoner grace period and escape notification |
| FB_hose_gss_1.1 | MAJOR | SMALL_PUMP_HOSE_FIX_LAYS_UNCONNECTED | src/RimMandrake/FlowWorks/Source/Hose/CompHoseReel.cs:412–415 (`ApproachIfOnPort`); src/RimMandrake/FlowWorks/Source/Hose/HosePorts.cs:132–1 | Clicking a small pump lays the hose on the pump without connecting it |
| FB_hose_gss_1.2 | MAJOR | PUMP_PORT_FIX_ASSUMES_ONE_CELL | src/RimMandrake/FlowWorks/Source/Hose/HosePorts.cs:145–170 (`ReelSideOn`, `EndSideOn`, `PumpSideTakes`) | Pump port arbitration assumes every pumping station occupies one cell |
| FB_hose_gss_1.4 | MAJOR | DRAWBRIDGE_HOSE_FIX_STAYS_LINKED_RAISED | src/RimMandrake/FlowWorks/Source/Hose/HoseEnds.cs:41–50 (`Read`); src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs:445–449 (`F | Raised drawbridges do not reliably disconnect hydraulic hose links |
| FB_hose_gss_1.5 | MAJOR | HOSE_RELOAD_FIX_SPILLS_SAVED_FLOW | src/RimMandrake/FlowWorks/Source/Hose/CompHoseReel.cs:67,224–225 (`flowUntil`, saved held contents); src/RimMandrake/FlowWorks/Source/Hose/R | Loading a flowing hose can spill its saved liquid before flow is restored |
| FB_hose_gss_1.6 | MINOR | REEL_BODY_INLET_FIX_SKIPS_DEPTH_RULES | src/RimMandrake/FlowWorks/Source/Hose/HosePorts.cs:97–126 (`RawFind`),202–207 (`RawFindAt`) | Reel-body inlets bypass the depth restrictions enforced at free ends |
| FB_hose_gss_1.7 | MINOR | AUTO_SPLICE_FIX_SKIPS_OBSTACLE_CHECK | src/RimMandrake/FlowWorks/Source/Hose/HoseSpliceMath.cs:435–436,595–609,651 (`MateTail`, `MatePair`, `Clear`); src/RimMandrake/FlowWorks/Sou | Automatic splice shaping bypasses obstacle and hose-length validation |
| FB_hose_gss_1.8 | MINOR | HOSE_SHADOW_FIX_STALE_ROUTE_CASTS | src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs:763–767 (`DrawAll`),942–953 (`DrawCrossShadow`); src/RimMandrake/FlowWorks/So | Cached former hose routes continue casting crossing shadows |
| FB_hose_gss_2.1 | MINOR | GSS_BATCHED_LINK_FIX_SKIPS_STYLE_MERGE | `src/RimMandrake/GimmeSomeSlack/Source/Aerial/RM_MapComponent_ConduitRuns.cs:275–276` (`Link`) | Batched links can skip every required style merge |
| FB_hose_gss_2.2 | MINOR | GSS_RESTRING_FIX_STYLES_UNRECONCILED | `src/RimMandrake/GimmeSomeSlack/Source/Aerial/CompAerialAnchor.cs:362–373` (`Restring`); `src/RimMandrake/GimmeSomeSlack/Source/Aerial/Condu | Re-stringing reconnects electrical runs without reconciling their styles |
| FB_hose_gss_2.3 | MINOR | GSS_STYLED_WINNER_FIX_KEEPS_LEGACY_LOOK | `src/RimMandrake/GimmeSomeSlack/Source/Aerial/ConduitStyles.cs:352–356` (`NeedsWrite`); `src/RimMandrake/GimmeSomeSlack/Source/Aerial/RM_Map | A styled winner can retain legacy members that later change to another look |
| FB_hose_gss_2.4 | MINOR | GSS_CORD_AUDIT_FIX_REJECTS_WALL_PLUGS | `src/RimMandrake/GimmeSomeSlack/Source/Core/CordAudit.cs:161–167` (`ArtFit`); `src/RimMandrake/GimmeSomeSlack/Source/Core/CordBuilder.cs:673 | Art-fit checks reject correctly routed wall-device plugs |
| FB_hose_gss_2.5 | MINOR | GSS_POWER_THEFT_FIX_WRONG_VICTIM | `src/RimMandrake/GimmeSomeSlack/Source/Aerial/CompPowerTap.cs:148–158` (`CompTick`); `src/RimMandrake/GimmeSomeSlack/Source/Aerial/PowerThef | Theft windows are attributed entirely to the current victim |
| FB_hose_gss_2.6 | MINOR | GSS_MULTILINK_FIX_PIPE_POLE_RANGE | `src/RimMandrake/GimmeSomeSlack/Source/Aerial/ConduitStyleProbe.cs:99` (`MultiLink`, `:plan` branch); `src/RimMandrake/GimmeSomeSlack/Source | Multilink planning uses the power range for pipe poles |
| FB_hose_gss_2.7 | MINOR | GSS_CORD_ADAPTER_FIX_NO_LAMP_GEOMETRY | `src/RimMandrake/GimmeSomeSlack/Source/CordWorldAdapter.cs:209–214` (`KindOf`); `src/RimMandrake/GimmeSomeSlack/Source/Core/CordGraph.cs:153 | The live adapter never selects lamp-specific cord geometry |
| FB_hose_gss_3.1 | MINOR | GSS_STRIP_LED_FIX_MISSED_REPAINT | `src/RimMandrake/GimmeSomeSlack/Source/RM_MapComponent_CordGraph.cs:322–335` (`Sig`, `LiveNow`) | Rebuilding can consume a power-state change without repainting strip LEDs |
| FB_hose_gss_3.2 | MINOR | GSS_FRESH_BUILD_ORACLE_FIX_TAP_CLAMPS | `src/RimMandrake/GimmeSomeSlack/Source/GimmeSomeSlackProbe.cs:336–344` (`FreshPieces`) | The fresh-build oracle omits production’s tap-clamp exceptions |
| FB_hose_gss_3.3 | MINOR | GSS_END_HEAPS_FIX_BYPASS_LOOP_BUDGET | `src/RimMandrake/_Shared/SlackGeometry/CordLayer.cs:459–486` (`AddLoops`, long-run branch) | Mandatory end heaps bypass the loop budget |
| FB_hose_gss_3.4 | MINOR | GSS_CORD_LOOPS_FIX_SPREAD_INTO_DOORS | `src/RimMandrake/_Shared/SlackGeometry/CordLayer.cs:527–529` (`AddLoops`, ordinary-shape branch) | Ordinary loops and heaps can spread into doorways |
| FB_hose_gss_3.5 | MINOR | GSS_COLOUR_SEED_FIX_HIDDEN_CONDUIT_SPLIT | `src/RimMandrake/GimmeSomeSlack/Source/RM_MapComponent_CordGraph.cs:179–187` (`ComputeNetSeeds`) | Hidden conduit connections split a single net’s legacy colour seed |
| FB_hose_gss_3.6 | MINOR | GSS_CORD_SWAY_TAME_PER_FRAME_ALLOC | `src/RimMandrake/GimmeSomeSlack/Source/RM_MapComponent_CordGraph.cs:690–696` (`DrawMotion`, CPU sway) | Default CPU sway still allocates per visible strand every frame |
| FC_pits_superdeep_1.1 | MAJOR | UNDERPASS_SHOT_FIX_OVERRIDES_VANILLA_REJECT | `src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_SuspensionPatches.cs:752-768` (`RM_Patch_SuspensionBandShots.Postfix`) | Underpass shooting can override vanilla shot rejection |
| FC_pits_superdeep_1.2 | MINOR | TIMBER_WINCH_FIX_POWERS_STEEL_BRIDGE | `src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_Drawbridges.cs:700-703` (`LinkWinch`), `src/RimMandrake/FlowWorks/Source/Pits/Drawbridg | A timber winch powers a steel drawbridge without electricity |
| FC_pits_superdeep_1.3 | MINOR | SUNKEN_DRAWBRIDGE_FIX_REJECTS_HINGE_BANK | `src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_Drawbridges.cs:470-493` (`Tip`) | Sunken drawbridges reject their own hinge bank as a landing area |
| FC_pits_superdeep_1.4 | MINOR | DRAWBRIDGE_LOWER_FIX_LIFTS_OCCUPANTS_BENEATH | `src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_Drawbridges.cs:306-333` (`Apply`), `src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM | Lowering a drawbridge promotes occupants beneath it onto the deck |
| FC_pits_superdeep_1.5 | MAJOR | CONCEALED_COVER_FIX_SHIELDS_FROM_LIQUID | `src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_SuspensionPatches.cs:313-326` (`UnderDeck`, `SplashShare`), `src/RimMandrake/FlowWorks/ | Pawns beneath concealed covers are shielded from the liquid surrounding them |
| FC_pits_superdeep_1.6 | MINOR | DROWNING_ESCAPE_FIX_READS_DECK_ABOVE | `src/RimMandrake/FlowWorks/Source/RM_PitFillEffects.cs:220-238` (`RM_Drowning.ExitInReach`) | Drowning escape checks use the deck above a floor-band pawn |
| FC_pits_superdeep_1.7 | MINOR | PIT_RAIN_FIX_FRACTIONAL_HEADROOM_FULL | `src/RimMandrake/FlowWorks/Source/RM_MapComponent_Excavation.cs:1348-1352,3139-3147` (`RoomNotches`, `ApplyRain`) | Rain treats fractional headroom as a brim-full excavation |
| FC_pits_superdeep_1.8 | MINOR | COVER_BLAST_FIX_DECK_LEFT_INTACT | `src/RimMandrake/FlowWorks/Source/Pits/Building_PitCover.cs:146-182,289-293` (`DeSpawn`, `RM_Patch_ExplosionBreaksPitCover.Postfix`) | A blast that kills its first cover can leave the rest of the deck intact |
| FC_pits_superdeep_1.9 | MAJOR | RAID_PLANK_FIX_SURFACE_HEIGHT_SUNKEN | `src/RimMandrake/FlowWorks/Source/Pits/Drawbridge/RM_DrawbridgeRaid.cs:294-303` (`RM_RaidPlanks.TryLay`) | Raid planks laid between sunken banks are registered at surface height |
| FC_pits_superdeep_1.10 | MINOR | COVER_SCAN_TAME_QUADRATIC_ID_MINIMA | `src/RimMandrake/FlowWorks/Source/Pits/Trigger/CompPitCoverTrigger.cs:75-85` (`RunScan`) | Cover scans remain quadratic for decks with many local ID minima |
| FC_pits_superdeep_1.11 | MINOR | BRIDGE_FLOOD_FIX_RUNS_EVERY_THREE_HOURS | `src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_MapComponent_SuspensionBridges.cs:800-812` (`MapComponentTick`) | Hourly bridge flood damage actually runs every three hours |
| FC_pits_superdeep_1.12 | MINOR | RAILING_TOGGLE_FIX_KEEPS_DECONSTRUCT | `src/RimMandrake/FlowWorks/Source/Pits/Suspension/RM_MapComponent_SuspensionBridges.cs:1207-1213,1284-1287` (`PlaceRailing`, `RemoveRailing` | Switching railings back on does not cancel their deconstruction |
| FC_pits_superdeep_1.13 | MINOR | PLACER_SELFCHECK_FIX_LEAVES_MERGED_ORE | `src/RimMandrake/FlowWorks/Source/Quarry/RM_PlacerWorks.cs:709,736-745` (`RM_PlacerProof.SelfCheck`) | The placer selfcheck leaves generated ore merged into existing stacks |
| FC_pits_superdeep_2.1 | MAJOR | PIT_RAMP_FIX_WALKER_TAKES_FALL | src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs:686–687 (`RM_SuperdeepTrapState.Tick`) | Walking down a valid ramp can inflict fall damage |
| FC_pits_superdeep_2.2 | MAJOR | PIT_RESCUE_FIX_COUNTS_DOCTOR_OFF | src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitAccess.cs:165–167 (`AnyRescuerReaches`) | Rescue considers colonists with Doctor work switched off available rescuers |
| FC_pits_superdeep_2.3 | MINOR | PIT_RESCUE_FIX_UNREACHABLE_SPARE_LADDER | src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitAccess.cs:257–267 (`SparePortable`) | An inaccessible stored ladder can permanently stall automatic pit rescue |
| FC_pits_superdeep_2.4 | MINOR | LADDER_PARITY_FIX_RAIDERS_SKIP_LEANING | src/RimMandrake/FlowWorks/Source/Superdeep/RM_LadderParity.cs:277 (`MightClimb`) | Ladderless raiders cannot use a ladder already leaning against a wall |
| FC_pits_superdeep_2.5 | MINOR | POCKET_TRAP_FIX_LADDER_TO_SEALED_POCKET | src/RimMandrake/FlowWorks/Source/Superdeep/RM_PocketGrid.cs:822–823 (`TrappedIn`) | A ladder into another sealed pocket is mistaken for an escape |
| FC_pits_superdeep_2.6 | MINOR | ABSOLUTE_DESCENT_FIX_MISSES_DECK_SHOVE | src/RimMandrake/FlowWorks/Source/Superdeep/RM_SuperdeepTrap.cs:786 (`IsFallingArrival`) | Absolute-mode descent detection misses falls from a deck over the same excavation |
| FC_pits_superdeep_2.7 | MINOR | TRENCH_STRIDE_FIX_CROSS_MAP_INVALIDATION | src/RimMandrake/FlowWorks/Source/Superdeep/RM_TrenchStride.cs:401 (`AfterIncremental`) | One map’s connectivity rebuild invalidates stride masks on other maps |
| FC_pits_superdeep_2.8 | MINOR | PIT_LIP_SHADE_TAME_PER_FRAME_ARRAYS | src/RimMandrake/FlowWorks/Source/Superdeep/RM_PitLipOcclusion.cs:133–152 (`DrawEdgeShade`) | Pooled lip-shadow meshes still allocate their backing arrays every frame |
| FC_pits_superdeep_2.9 | MINOR | CLIFF_MASK_TAME_PER_CELL_SCRATCH | src/RimMandrake/FlowWorks/Source/Superdeep/RM_CliffMask.cs:264–291 (`DeriveCell`) | Full cliff-mask rebuilds allocate scratch state separately for every affected cell |
| FD_defs_xml_1.1 | MAJOR | FILL_TERRAIN_FIX_HAZARDS_DRUNK_AS_WATER | `src/RimMandrake/FlowWorks/Defs/Canals/TerrainDefs/FlowWorks_PitFluidTerrain.xml:300–319` (`RM_Fill_Chemfuel_Trace`; also other non-water fi | Hazardous canal liquids become unlimited potable drinking sources |
| FD_defs_xml_1.2 | MAJOR | NATURAL_LIQUID_FIX_PUMPS_AS_FRESH_WATER | `src/RimMandrake/FlowWorks/Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml:215–258` (`RM_Liquid_ToxicWater`; also salt water, brine, ac | Natural liquids without canal forms silently turn into fresh water |
| FD_defs_xml_1.3 | MAJOR | DEEP_SAND_FIX_READS_AS_FRESHWATER | `src/RimMandrake/FlowWorks/Defs/ManyWaters/TerrainDefs/RM_DeepSand.xml:134–158` (`RM_DeepSand`) | Deep sand’s fishing tag also makes it a freshwater reservoir |
| FD_defs_xml_1.4 | MINOR | WHITE_SLIME_CANAL_FIX_CANNOT_IGNITE | `src/RimMandrake/FlowWorks/Defs/Canals/FluidDefs/FlowWorks_Fluids.xml:128–145` (`RM_Fluid_SlimeWhite`) | White slime’s canal form cannot ignite |
| FD_defs_xml_1.5 | MAJOR | LIQUID_CONVERTER_FIX_PICKS_CRUDE_FIRST | `src/RimMandrake/FlowWorks/Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml:93–108,242–257` (`RM_Liquid_SaltWater`, `RM_Liquid_ToxicWate | Conversion ordering makes the industrial efficiency recipes unreachable |
| FD_defs_xml_1.6 | MINOR | INDUSTRIAL_RUINS_FIX_HIDDEN_EH_DEPENDENCY | `src/RimMandrake/FlowWorks/Defs/Machinery/RM_LiquidWorksScatter.xml:14–16,40,66,91` (all four industrial ruin scatters) | Default industrial progression requires an undeclared extra mod |
| FD_defs_xml_1.7 | MINOR | TAR_REFINERY_FIX_CAN_FALLBACK_DEAD | `src/RimMandrake/FlowWorks/Defs/LiquidTypes/LiquidDefs/RM_LiquidDefRegistry.xml:378–385`; `src/RimMandrake/FlowWorks/Defs/Machinery/RM_Indus | Tar refineries advertise an item-output fallback that cannot run |
| FD_defs_xml_2.1 | MINOR | DBH_BOTTLE_BRIDGE_FIX_IGNORES_VOLUME | `src/RimMandrake/FlowWorks/Patches/LiquidTypes/RM_DBH_BottleWaterExt.xml:53–58` (`RM_Bottle_ToxicWater`; the same constant appears throughou | DBH bottle bridge bypasses volume and hydration-quality rules |
| FE_cs_selftests_1.1 | MINOR | HOSE_NET_SELFTEST_FIX_VACUOUS_ISOLATION | src/RimMandrake/FlowWorks/Source/SelfTest/HoseNetChecks.cs:165–169 (`TankEndpoints`) | The two-pipe-runs isolation test constructs no recognized pipes |
| FE_cs_selftests_1.2 | MINOR | FUEL_FIRE_SELFTEST_FIX_SQUARE_COVERAGE | src/RimMandrake/FlowWorks/Source/SelfTest/FuelFireChecks.cs:90–99 (`CheckPlan`) | Detonation coverage checks a square instead of the actual blast radius |
| FE_cs_selftests_1.3 | MINOR | HOSE_FUZZ_HARDEN_ZERO_LAID_PASSES | src/RimMandrake/FlowWorks/Source/SelfTest/HoseFuzz.cs:138 (`RunHose`), :45 (`Report`) | Hose fuzzing can pass with zero successfully laid hoses |
| FE_cs_selftests_2.1 | MINOR | PIT_TRAVEL_SELFTEST_FIX_DOUBLE_COUNT | src/RimMandrake/FlowWorks/Source/SelfTest/PitAccessChecks.cs:141–143 (`PitTravel_every_trap_mask_reach_and_fall_read_asks_it`) | One arrival detector is counted twice as proof that both are guarded |
| FE_cs_selftests_2.2 | MINOR | LAKE_FLOOR_SELFTEST_FIX_WET_SKIPS_HEIGHT | src/RimMandrake/FlowWorks/Source/SelfTest/LakeFloorChecks.cs:85,97 (`EdgeReachable`) | Lake-access ruler accepts wet neighbours without checking the final height difference |
| FE_cs_selftests_2.3 | MINOR | HOSE_SCENIC_SELFTEST_FIX_NEVER_CROSSES | src/RimMandrake/FlowWorks/Source/SelfTest/HoseReviewChecks.cs:445–448 (`HoseGptFix.ScenicRoute`) | The “building cost never blocks” fixture never requires crossing a building |
| FE_cs_selftests_2.4 | MINOR | PIPE_SPAN_SELFTEST_FIX_COLLAPSED_WHITESPACE | src/RimMandrake/FlowWorks/Source/SelfTest/PipeSpanNetChecks.cs:183 (`PipeSpan_P3_production_wiring_adapter_callback_join_order`) | Pipe-span regression assertion searches for whitespace its helper has removed |
| FE_cs_selftests_2.5 | MINOR | LEVEL_SET_SELFTEST_FIX_IDLE_PULSE_SETTLES | src/RimMandrake/FlowWorks/Source/SelfTest/LevelSetChecks.cs:38–41,92 (`Run`, `LowVolumeWideBasinOnePatch`) | Integer-water tests accept a single idle final pulse as settling |
| FE_cs_selftests_3.1 | MINOR | SELFTEST_ASSERT_CLOSE_FIX_ACCEPTS_NAN | src/RimMandrake/FlowWorks/Source/SelfTest/Program.cs:119-123 (`AssertClose`) | Shared numeric assertion silently accepts NaN |
| FE_cs_selftests_3.2 | MINOR | SLIME_SELFTEST_FIX_SKIPS_MISSING_COST | src/RimMandrake/FlowWorks/Source/SelfTest/SlimeChecks.cs:119-124 (`Slime_shipped_data_and_wiring`) | Slime path-cost check silently skips a missing authored field |
| FE_cs_selftests_4.1 | MAJOR | GSS_DETERMINISM_FIX_IGNORES_STALE_PIECES | `src/RimMandrake/GimmeSomeSlack/Source/SelfTest/DeterminismChecks.cs:79–90` (`Compare`) | Determinism comparison ignores surplus incremental pieces |
| FE_cs_selftests_4.2 | MINOR | TRANSFER_AUDIT_FIX_FAILED_MOVE_COUNTS | `src/RimMandrake/FlowWorks/Source/SelfTest/TransferChecks.cs:542–551` (`CommittedBlocks`) | Transfer audit accepts failed transfers as committed transfers |
| FE_cs_selftests_4.3 | MAJOR | VV_MATRIX_FIX_UNCOMPILED_HOSE_PASSES | `src/RimMandrake/FlowWorks/Source/SelfTest/VV/ShippedMatrixProbe.cs:171–173,229` (`Rates`, `HoseFamily`) | Uncompiled hose families produce success-shaped matrix records |
| FE_cs_selftests_4.4 | MINOR | VV_MATRIX_FIX_SURFACE_FAILURES_UNDERCOUNT | `src/RimMandrake/FlowWorks/Source/SelfTest/VV/ShippedMatrixProbe.cs:165` (`Rates`) | Surface-family “failures” is a lower bound presented as a count |
| FE_cs_selftests_4.5 | MINOR | BODY_SPLIT_FIX_FISH_SHARE_SHRINKS | `src/RimMandrake/FlowWorks/Source/SelfTest/WaterBodyMendChecks.cs:307–323,519` (`Model.SplitOff`, split-population assertion) | Three-way water-body splits distribute fish using a shrinking numerator |
| FE_cs_selftests_4.6 | MINOR | GSS_FUZZ_ONLY_FIX_UNKNOWN_FAMILY_PASSES | `src/RimMandrake/GimmeSomeSlack/Source/SelfTest/GssFuzz.cs:630–705`; `src/RimMandrake/GimmeSomeSlack/Source/SelfTest/Program.cs:45` (`Run`,  | Unknown fuzz-family names silently run zero checks successfully |
| FF_validation_suite_1.2 | MAJOR | REVIEW_PROOFS_FIX_STALE_PROOF_OVERWRITES | `src/RimMandrake/FlowWorks/human_review.py:1110–1131` (`latest_result`) | An old proof PASS can overwrite a current FAIL and inherit its freshness |
| FF_validation_suite_1.3 | MAJOR | EXTENSION_PROOF_FIX_DISK_SHA_TRUSTED | `src/RimMandrake/FlowWorks/northstar/extension_proof.py:183–190` (`main`, environment capture) | Extension evidence can identify the replacement DLL instead of the loaded DLL |
| FF_validation_suite_1.4 | MINOR | DEPTH_PROOFS_FIX_EXIT_ZERO_ON_FAIL | `src/RimMandrake/FlowWorks/northstar/depth_rebuild_proofs.py:526` (`main`) | The depth rebuild suite exits successfully after failed checks |
| FF_validation_suite_1.5 | MINOR | SWIM_WARNING_FIX_ANY_PAWN_MESSAGE | `src/RimMandrake/FlowWorks/northstar/depth_rebuild_proofs.py:233–244` (`main`, armoured swimmer poll) | The swimming warning check accepts the drowning announcement as advance warning |
| FF_validation_suite_1.6 | MINOR | PIT_SHOT_PROOF_FIX_OTHER_TARGET_PASSES | `src/RimMandrake/FlowWorks/northstar/depth_rebuild_proofs.py:418–421` (`P7_shoot_between_7m_pits_refused`) | Choosing another attack target is treated as proof that the intended target is unhittable |
| FF_validation_suite_1.7 | MINOR | P5_SITE_FIX_RERUN_DIGS_DEEPER | `src/RimMandrake/FlowWorks/northstar/depth_rebuild_proofs.py:99–103,426–435` (`dig`, P5 setup) | Reusing a depth-proof map silently deepens the previous test geometry |
| FF_validation_suite_1.8 | MINOR | DRAWBRIDGE_UNDERPASS_FIX_HEDIFF_COUNT_ONLY | `src/RimMandrake/FlowWorks/northstar/drawbridge_proof.py:509` (`raise_spares_underpass`) | Underpass safety compares injury counts rather than unchanged health |
| FF_validation_suite_1.9 | MINOR | DEEP_STONE_PROOF_FIX_RERUN_LETTER_FAILS | `src/RimMandrake/FlowWorks/northstar/deep_stone_live.py:168–177` (`main`, final verdict) | A correct second deep-stone run fails because it demands another first-find letter |
| FF_validation_suite_2.2 | MINOR | ALL_OFF_FIX_DEPTH_ENGINE_STAYS_ON | `src/RimMandrake/FlowWorks/northstar/extensions.py:352-359,1267-1268` (`_setting_in`, `all_off_still_digs`) | “All off” bypasses the reload-sensitive engine-switch handling |
| FF_validation_suite_2.3 | MINOR | PUMP_POUR_PROOF_FIX_TANK_NOT_DUMP | `src/RimMandrake/FlowWorks/northstar/extensions.py:2811-2816` (`liquid_pump`, `pump_pours_back`) | Pump return test never marks its tank Dump |
| FF_validation_suite_2.4 | MINOR | OUTFLOW_REGRESSION_FIX_HARDCODED_CAP | `src/RimMandrake/FlowWorks/northstar/live_probes/fw_pond_outflow_regression.py:14,33,39-42` | Stale pond capacity makes the outflow regression pass without drainage |
| FF_validation_suite_2.5 | MINOR | BIGNET_PROOF_FIX_SIZE_NOT_RESTORED | `src/RimMandrake/FlowWorks/northstar/flow_bignet_live.py:60,97-110,131-138` (`main`) | Resumed large-network phases use command-line size instead of saved size |
| FF_validation_suite_2.6 | MINOR | LEVEL_WATER_FIX_POND_SPLITS_ARMS | `src/RimMandrake/FlowWorks/northstar/level_water.py:578-592` (`surface_gaps`) | Surface-gap reference does not connect canal arms through their pond |
| FF_validation_suite_2.7 | MINOR | POND_DEPTH_VERDICT_FIX_DEEP_COUNTS_PARTIAL | `src/RimMandrake/FlowWorks/northstar/liquid_checks.py:374-377` (`pond_depth_verdict`) | Pond-shallowing predicate accepts an unchanged deep-water appearance |
| FF_validation_suite_2.8 | MINOR | GLOW_TANK_PROOF_FIX_BLIND_READ_PASSES | `src/RimMandrake/FlowWorks/northstar/glow_tank_live.py:104-106,155-159` (`inspect`, setting-off row) | Glow-tank setting check treats an unread inspect result as success |
| FF_validation_suite_2.9 | MINOR | TAR_LAG_FIX_NO_WATER_CONTROL | `src/RimMandrake/FlowWorks/northstar/extensions.py:746-753,763-779` (`_expect_tar_lag`, `tar_front_lags_water`) | Tar viscosity check accepts an ordinary water-speed partial front |
| FF_validation_suite_2.10 | MINOR | LAKE_FLOOR_STAGE_TAME_QUADRATIC_SETS | `src/RimMandrake/FlowWorks/northstar/lake_floor_stage.py:114` (`main`) | Lake-center selection repeatedly rebuilds the entire lake set |

## Merged (duplicate of a confirmed finding)

- FF_validation_suite_1.1: duplicate of FA_core_sim_1.10 (IMMERSION_DAMAGE_WIRE_NEVER_APPLIED)

## Rejected

- FB_hose_gss_1.3 (Hose-to-hose joiners create a visual connection without a liquid connection): By design: closed item HOSE_SPLICE_BUILD_MATES_BY_SLOPE.md:38 says mated hoses are not one hydraulic run, the item asked for the look
- FF_validation_suite_2.1 (Recession declaration crashes when the guard is down): extensions.py:1193 parenthesisation is float((...).get("capacity") or 0): None or 0 -> 0, no float(None)

## Unverified findings

Not checked (the coordinator stopped verification for cost). Listed with GPT severity in `infrastructure/state/items/GPT_FW_REVIEW_VERIFY_REMAINING_FINDINGS.md`: FF_validation_suite_3.1, FF_validation_suite_3.2, FF_validation_suite_3.3, FF_validation_suite_3.4, FF_validation_suite_3.5, FF_validation_suite_3.6, FF_validation_suite_3.7, FF_validation_suite_3.8, FF_validation_suite_3.9, FF_validation_suite_3.10, FF_validation_suite_3.11, FF_validation_suite_3.12, FF_validation_suite_3.13, FF_validation_suite_4.1, FF_validation_suite_4.2, FF_validation_suite_4.3, FF_validation_suite_4.4, FF_validation_suite_4.5, FF_validation_suite_4.6, FF_validation_suite_4.7, FF_validation_suite_4.8, FF_validation_suite_5.1, FF_validation_suite_5.2, FF_validation_suite_5.3, FF_validation_suite_5.4, FF_validation_suite_5.5, FF_validation_suite_5.6, FF_validation_suite_5.7, FF_validation_suite_5.8, FF_validation_suite_5.9, FF_validation_suite_5.10, FF_validation_suite_5.11, FF_validation_suite_6.1, FF_validation_suite_6.2, FF_validation_suite_6.3, FF_validation_suite_6.4, FF_validation_suite_6.5, FF_validation_suite_6.6, FF_validation_suite_6.7, FF_validation_suite_6.8, FF_validation_suite_6.9, FF_validation_suite_7.1, FF_validation_suite_7.2, FF_validation_suite_7.3, FF_validation_suite_7.4, FF_validation_suite_7.5, FF_validation_suite_7.6, FF_validation_suite_7.7, FF_validation_suite_7.8, FF_validation_suite_7.9, FF_validation_suite_7.10, FF_validation_suite_7.11, FF_validation_suite_7.12, FF_validation_suite_8.1, FF_validation_suite_8.2, FF_validation_suite_8.3, FF_validation_suite_8.4, FF_validation_suite_8.5, FF_validation_suite_8.6, FF_validation_suite_8.7, FF_validation_suite_8.8, FF_validation_suite_8.9, FF_validation_suite_9.1, FF_validation_suite_9.2, FF_validation_suite_9.3, FF_validation_suite_9.4, FF_validation_suite_9.5, FF_validation_suite_9.6, FF_validation_suite_9.7, FF_validation_suite_9.8.

## Compression plans (GPT reply, verbatim)

Source: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\FINAL_compression.md`. Section 2 is Plan H (human review), section 3 Plan N (northstar automated review); each has its coverage matrix and the scripts each station replaces.

## 1. FEATURE LIST

**Minimum physical layout: one joint station for human review and one reconfigurable joint station for Northstar, on the same existing map.** These are separate review tracks, checkpoints and reports. Combining sites does **not** eliminate distinct assertions, visual comparisons or save/load branches.

This minimum depends on allowing a station to occupy a connected settlement and watershed. Without a maximum station footprint or maximum number of capture angles, there is no defensible lower bound above one. Calling its different camera views separate stations would simply change the counting convention.

**480 merged feature obligations** follow. Synonyms are merged; broad inventory entries are covered by their constituent obligations. For example, `liquid_tank_modes` merges into `tank_modes`; `waterbody_split` into `water_body_split`; the various navy-tint names into `deep_water_tint`. Production behavior, test-harness behavior and visual approval remain distinct obligations.

Legend:

- **Y**: offline-testable; **P**: offline rules/data can be tested, but that cannot establish the complete behavior.
- **Live** means actual game state is required for complete validation, including features whose live check is prohibited or currently missing.
- **Eyes** identifies visual/UI acceptance required in Plan H. State-readable gameplay outcomes need not also require eyes.
- These are classifications and a proposed plan, **not results of executing the suite**.

| feature_id | feature | offline-testable? | needs live state? | needs eyes? |
|---|---|---|---|---|
| package_requirements | Both package identities and requirements | Y | No | No |
| assembly_wiring | Explicit production assembly composition | Y | No | No |
| flowworks_def_bindings | Required defs and missing-def guards | P | Yes | No |
| fluid_registry | Liquid identities, forms and conversions | P | Yes | No |
| liquid_terrain_suite_generation | Generated terrain roster and synchronization | Y | No | No |
| liquid_terrain_mod_compat | Conditional donor properties and tags | P | Yes | No |
| natural_liquid_identity | Terrain/canal/body identity resolution | P | Yes | No |
| world_liquid_tags | Explicit-tile and biome liquid tags | P | Yes | No |
| typed_liquid_shores | Typed-shore registration and repaint | P | Yes | Yes |
| industrial_ruin_scatter | Matching-liquid industrial site selection | P | Yes | No |
| liquid_works_ruin_stock | Damaged machinery and initial stock | P | Yes | Yes |
| industrial_ruin_restoration | Wreck/kludged/repaired progression | P | Yes | Yes |
| water_not_food | Drinks provide zero nutrition | P | Yes | No |
| lava_liquid_faces | Restricted Odyssey lava adoption | Y | No | No |
| lava_pumping_ruin_exclusion | Lava excluded from pumping ruins | Y | No | No |
| astrofuel_liquid_adoption | Conditional astrofuel item adoption | P | Yes | No |
| recreational_swim_eligibility | Hazard/deep-sand recreation veto | P | Yes | No |
| deep_sand_fishing | Deep-sand cost and fishing classification | P | Yes | No |
| flowworks_localized_feedback | Translations and readable substitutions | P | Yes | Yes |
| review_station_signs | Persistent review books and instructions | P | Yes | Yes |
| settings_ui | Combined settings, tabs and dependencies | P | Yes | Yes |
| settings_persistence | Settings defaults, serialization and migration | P | Yes | No |
| settings_search | Visible-label search and scroll reset | P | Yes | Yes |
| settings_reset | Shipped, section and complete resets | P | Yes | Yes |
| settings_runtime_rebuilds | Apply path/room/net/visual changes | P | Yes | No |
| depth_engine_reload_latch | Engine setting latched per game | P | Yes | No |
| fluid_input_filter | Disable inputs without purging liquid | P | Yes | No |
| typed_settings_registry | Complete typed settings ownership | Y | No | No |
| settings_all_off | Complete all-off fixture | P | Yes | No |
| settings_fingerprint | Stable scalar/collection fingerprints | Y | No | No |
| settings_cached_rows | Cached machinery settings rows | Y | No | No |
| liquid_look_tuning_export | Tune, export and regenerate looks | P | Yes | Yes |
| canal_dig_single_cut | Real designation and completed excavation | P | Yes | No |
| canal_dig_to_depth | Saved repeated-cut target orders | P | Yes | No |
| machine_digger_classification | Human/machine labor classification | P | Yes | No |
| dig_depth_caps | Caps without shallowing existing holes | P | Yes | No |
| deep_dig_work_cost | Depth/rock work and digger-days | P | Yes | No |
| deep_dig_wait_alert | Orders awaiting eligible labor | P | Yes | Yes |
| canal_fill_work | Fill eligibility and occupant protection | P | Yes | No |
| dig_fill_orders | Exclusive orders and safe enumeration | P | Yes | No |
| excavation_fill_displacement | Exact displaced-liquid routing | P | Yes | No |
| excavation_terrain_restore | Original ground and fluid cleanup | P | Yes | No |
| legacy_fill_ground_restore | Missing-original fallback and reload | P | Yes | No |
| excavation_save_repair | Grid repair and old-format migrations | P | Yes | No |
| liquid_identity_palette | Palette compaction/exhaustion safety | P | Yes | No |
| excavation_depth_fill_storage | Saved depth, fluid and exact dL | P | Yes | No |
| liquid_pulse_adapter | Actual cadence and engine gates | P | Yes | No |
| excavation_rain_fill | Fractional, roof-sensitive rainfall | P | Yes | No |
| map_edge_modes | Automatic/sealed/drain boundaries | P | Yes | No |
| liquid_conservation_ledger | All stores, inputs and disclosed exits | P | Yes | No |
| driver_flow_seeds | Pump/drill pressure and reload recovery | P | Yes | No |
| channel_flow_order | Acyclic donor/source/sink order | Y | No | No |
| whole_notch_channel_flow | Deep legacy flow and drainage | P | Yes | No |
| exact_channel_pond_flow | Exact surfaces and sill split/join | P | Yes | No |
| flow_partition_rotation | Large-network seam exchange | P | Yes | No |
| liquid_body_discovery | Bounded fluid-aware body collection | P | Yes | No |
| liquid_source_liveness | Limitless/shared-source supply | P | Yes | No |
| source_mouth_pacing | Limited-source advancing inlet fronts | P | Yes | No |
| scarce_source_priority | Stable scarce-input allocation | Y | No | No |
| natural_body_classification | Sticky finite/endless classification | P | Yes | No |
| natural_body_stock_ledger | Exact debits, returns and final remainder | P | Yes | No |
| pond_floor_capacity | Bed-derived capacity and level units | P | Yes | No |
| pond_volume_migration | Fill-fraction-preserving budget migration | P | Yes | No |
| pond_groundwater_refill | Groundwater/rain/seasonal recharge | P | Yes | No |
| pond_recession_topology | Connected retreat and inlet preservation | P | Yes | No |
| pond_fullcell_recession | Shallow-first retreat and reverse refill | P | Yes | No |
| pond_refill_occupants | Wait for occupants; move items safely | P | Yes | No |
| pond_depth_surface | Partial-depth pond presentation | P | Yes | Yes |
| pond_mud_lakebed | Mud drying into lakebed terrain | P | Yes | Yes |
| pond_depth_model_toggle | Change recession model without volume loss | P | Yes | No |
| pond_bed_detach_reattach | Bed membership and capacity restoration | P | Yes | No |
| pond_dry_bed_hollows | Persistent physical dry-bed hollows | P | Yes | Yes |
| lake_floor_generation | Seeded varied lake floors | P | Yes | Yes |
| lake_floor_exit_and_basin | Accessible drawdown and common basin | Y | No | No |
| lake_floor_initialization_save | Form once and preserve full-lake terrain | P | Yes | No |
| large_lake_live | Large finite lake drawdown/refill/escape | P | Yes | No |
| liquid_depth_readout | Hole/water depth, litres and Endless | P | Yes | Yes |
| liquid_surface_gap_diagnostic | Complete connected-body surface gaps | P | Yes | No |
| water_depth_ladder | Shared pond/canal freshwater ladder | P | Yes | Yes |
| fluid_identity_viscosity | Nonmixing and liquid-specific fronts | P | Yes | No |
| water_save_load_state | Mid-flow state and future continuation | P | Yes | No |
| pond_freeze_thaw | Runtime body freezing and thaw | P | Yes | Yes |
| fish_growth_rolls | Fish acquisition in growing ponds | P | Yes | No |
| fish_refill_memory | Remember fish through drainage | P | Yes | No |
| fishing_zone_refill | Restore fishing cells and settings | P | Yes | No |
| water_body_split | Correct tracker splitting/populations | P | Yes | No |
| water_body_freeze_recount | Runtime freezable-cell recount | P | Yes | No |
| water_body_type_flip | Safe body detachment on type change | P | Yes | No |
| water_plant_grace | Temporary-depth plant survival | P | Yes | No |
| dug_pond_fishing | Actual fishing and catch | P | Yes | No |
| dig_discovery_exploit_guard | Remember rolled depths/find budget | P | Yes | No |
| local_dig_ore_finds | Paid mineral placement on banks | P | Yes | No |
| dig_rock_and_deep_stone | Rock chunks and stable deep strata | P | Yes | No |
| dig_discovery_letters | First-find history and letters | P | Yes | Yes |
| flood_release_conservation | Release placement/spill/loss accounting | P | Yes | No |
| flood_release_determinism | Stable traversal and saved frontier | P | Yes | No |
| flood_terrain_recession | Restore temporary flood layers | P | Yes | No |
| flood_engine_ownership | Ownership-safe release and cooling policy | P | Yes | No |
| tar_front_glass | Eligible release edge becomes glass | P | Yes | Yes |
| pond_flood_preservation | Flood preserves excavation state | P | Yes | No |
| subsurface_survey | Sticky finite surveyed deposit | P | Yes | No |
| liquid_drilling | Powered drill and bleed-well output | P | Yes | No |
| drill_placement_status | Survey/outlet/power refusal reasons | P | Yes | Yes |
| drill_pending_salvage | Return unpoured extracted stock | P | Yes | No |
| tank_storage_capacity | Single-liquid capacity/overfull/migration | P | Yes | No |
| tank_modes | Store/Fill/Empty/Dump permissions | P | Yes | No |
| tank_network_settle | Bounded epoch settlement and rotation | P | Yes | No |
| liquid_store_planning | Deterministic split fill/draw plans | Y | No | No |
| tank_gravity_dump | Slow pump-free outflow | P | Yes | No |
| tank_destruction_salvage | Physical destruction spills contents | P | Yes | No |
| cargo_tank_transport | Filled cargo minification/reinstallation | P | Yes | No |
| pump_draw_pour | Reversible world/tank pumping | P | Yes | No |
| pump_world_transfer | Tank-free world transfer and budgets | P | Yes | No |
| pump_overflow_sheet | Physical full-lip pump overflow | P | Yes | No |
| pump_status_warnings | Power/settings and network diagnostics | P | Yes | Yes |
| pump_footprint_reach | Reach measured from occupied footprint | P | Yes | No |
| pump_hose_side_ports | Cardinal arbitration and corner refusal | P | Yes | No |
| liquid_transfer_atomicity | Validate/commit/rollback and credits | P | Yes | No |
| compound_liquid_transfer | Atomic multiple-input/split-store moves | Y | No | No |
| ve_boundary_fractional_carry | External fractional carry/debt | P | Yes | No |
| pipe_network_adapter | Reflective Send/Take/Shut adapter | P | Yes | No |
| liquid_network_topology | Conductors, endpoints, routes and caps | P | Yes | No |
| liquid_net_topology_cache | Revision cache and route revalidation | P | Yes | No |
| liquid_consumer_fairness | Fair competing consumers and inputs | P | Yes | No |
| passive_liquid_levelling | Conservative gravity and liquid isolation | P | Yes | No |
| liquid_outlet_routing | Channel/pond/ground/blocked outlets | P | Yes | No |
| hose_drain_conservation | Drain/recover/spill/disclose held liquid | P | Yes | No |
| faction_liquid_theft | Witnessed theft, attribution and goodwill | P | Yes | Yes |
| liquid_conversion_machines | All conversion ratios and operating gates | P | Yes | No |
| converter_scheduling | Blocked-recipe fairness and budget | P | Yes | No |
| converter_output_salvage | Pending items, save and destruction | P | Yes | No |
| liquid_reactions | Atomic liquid/item/gas reactions | P | Yes | No |
| reactor_scheduling | Continue past stalled reactions | P | Yes | No |
| liquid_bath_recipes | Craft eligibility and paid completion | P | Yes | No |
| hot_release_effects | Saved cooling/scald/steam patches | P | Yes | Yes |
| drained_liquid_residue | Drain stains and persistent tar tracks | P | Yes | Yes |
| sprinkler_pipe_placement_style | Pipe-mounted four-look fittings | P | Yes | Yes |
| sprinkler_pressure_liquid_selection | Pressure, dominant liquid and clog/filter | P | Yes | No |
| sprinkler_hourly_atomic_draw | Hourly full payment and switches | P | Yes | No |
| sprinkler_coverage | Radius, LOS and sealed-cell exclusions | P | Yes | No |
| sprinkler_wet_registry | Wet identity/owner/expiry/spending | P | Yes | No |
| sprinkler_nonwater_effects | Harmful spray and fuel deposits | P | Yes | No |
| sprinkler_visual_status | Tinted spray and operating statuses | P | Yes | Yes |
| vfe_sprinkler_adapter | Conditional VFE boost/valve integration | P | Yes | No |
| swale_fed_fertility_ladder | Timed fed-soil improvement | P | Yes | No |
| glow_tank_salt_feed | Salt-fed glow-tank crop integration | P | Yes | No |
| container_material_crafting | Recipes, capacity and chemical refusals | P | Yes | No |
| container_condition_preservation | Stuff, wear and style preservation | P | Yes | No |
| container_four_styles | Four looks, trim/windows and stacking | P | Yes | Yes |
| container_fill_terrain | Real batched shore filling | P | Yes | No |
| container_washing | Paid dirty-to-empty washing | P | Yes | No |
| container_ingestion_residue | Map/caravan ingestion residue | P | Yes | No |
| container_tank_transfer | Paid fill/pour and loop prevention | P | Yes | No |
| bottled_liquid_reversion | Saved-age hot/cold replacement | P | Yes | No |
| bucket_firefighting | Real bucket fetching and area dousing | P | Yes | No |
| paid_output_placement | Preserve products after placement failure | P | Yes | No |
| thirst_provider_selection | Provider and pawn eligibility | P | Yes | No |
| thirst_decay | Heat/work/sleep/hediff rates | P | Yes | Yes |
| dehydration_progression | Dehydration stages, recovery and death | P | Yes | Yes |
| thirst_mood_categories | Thirst thoughts and exemptions | P | Yes | Yes |
| drink_use_class_gate | Potable/desperate/break-only restrictions | P | Yes | No |
| drink_source_selection | Reachable source ranking and preference | P | Yes | No |
| animal_terrain_drinking | Wild/tame/native terrain drinking | P | Yes | No |
| bottle_hydration | Actual volume-scaled ingestion | P | Yes | No |
| terrain_tank_drinking | Timed terrain and direct-tank jobs | P | Yes | No |
| drink_quality_effects | Hydration, toxins, salt and slime effects | P | Yes | No |
| awkward_drink_mood | Rough-access thought and exemptions | P | Yes | No |
| potable_drinking_reserve | Industry leaves drinkable stock | P | Yes | No |
| salt_water_break | Brine break, poisoning and treatment | P | Yes | No |
| caravan_drinking | Carried bottles and river-tile water | P | Yes | No |
| dbh_bottle_bridge | Startup DBH bottle/terrain compatibility | P | Yes | No |
| partial_container_drinks | Saved partial bulk-container contents | P | Yes | Yes |
| potable_bottle_stock_target | Exact stock targets and bounded batches | P | Yes | No |
| personal_bottle_packing | Personal supply with retained map stock | P | Yes | No |
| patient_prisoner_water | Real dependent-pawn water delivery | P | Yes | No |
| external_water_items | Donor-item hydration and quality | P | Yes | No |
| sanguophage_blood_hydration | Gene-gated hemogen hydration | P | Yes | No |
| snow_ice_gathering | Paid snow/ice collection | P | Yes | No |
| snow_bucket_melting | Saved warming and stack/split clocks | P | Yes | No |
| ice_bucket_recipes | Material-preserving melt bills | P | Yes | No |
| thirst_search_cache_reset | Failed searches reset on load/game | P | Yes | No |
| pipe_faucet_network_draw | Pipe-only atomic faucet withdrawal | P | Yes | No |
| pipe_faucet_drinking | Whole drinks without rough thought | P | Yes | No |
| pipe_faucet_container_fill | Real material-checked faucet filling | P | Yes | No |
| pit_cliff_pathing | Relative cardinal/diagonal masks | P | Yes | No |
| pit_pocket_connectivity | Band components, width and edge access | P | Yes | No |
| ladder_reach_routes | Joined down/across/up routes | P | Yes | No |
| wall_depth_reachability | Combined wall/depth/swim reach | P | Yes | No |
| reach_cache_diagnostics | Invalidation, throttling and residuals | P | Yes | No |
| underpass_reach_views | Correct floor/deck connectivity view | P | Yes | No |
| trench_stride | Giant width bridging and composed views | P | Yes | No |
| pit_step_cost | Flat, climb, ladder and falling costs | P | Yes | No |
| creature_climb_bonus | Climber/leaper race extensions | P | Yes | No |
| ladder_climber_eligibility | Anatomy, size and race overrides | P | Yes | No |
| ladder_shared_access | Faction/prisoner/wild ladder parity | P | Yes | No |
| ladder_hanging_and_reach | Wall facing and portable depth reach | P | Yes | Yes |
| ladder_raise_lower | Real operations and permitted sides | P | Yes | Yes |
| raider_ladder_supply | Carriers, theft, construction and chopping | P | Yes | No |
| ladder_wall_crossing | One-way wall ladder traversal | P | Yes | No |
| pit_breach_repair | Saved scars and original-depth repair | P | Yes | No |
| pit_safe_ability_arrivals | Safe arrival and free-travel rules | P | Yes | No |
| pit_rescue_ladder | Queue/build/install and actual rescue | P | Yes | No |
| pit_rooms | Creature-scaled rooms and thermal coupling | P | Yes | No |
| pit_warden_lip_service | Real care from the lip | P | Yes | No |
| pit_capture_down | Actual capture, identity and bed rules | P | Yes | No |
| pit_stuck_alert | Held-colonist need-access alert | P | Yes | Yes |
| pit_capture_and_escape | Relative/absolute confinement and carveouts | P | Yes | No |
| pit_fall_damage | Forced history, damage and deep death | P | Yes | No |
| pit_voluntary_jump | Confirmed pit/jetty descent action | P | Yes | No |
| pit_spikes | Relative placement and descent hits | P | Yes | Yes |
| fall_guardrails | Edge protection and deliberate exception | P | Yes | Yes |
| pit_exposure | Safe ranges and prisoner resistance | P | Yes | No |
| pit_exposure_charity_memory | Charity-gated prisoner distress | P | Yes | No |
| pit_cover_surface_mimic | Sheer-site camouflage and placement | P | Yes | Yes |
| pit_cover_load_trigger | Connected mass and weakest-tier collapse | P | Yes | No |
| pit_cover_damage_collapse | Damage/deconstruction rider descent | P | Yes | No |
| pit_cover_beneath_pawns | Saved hidden occupants and exits | P | Yes | No |
| span_walking_surface | Deck/lid height and walker drawing | P | Yes | Yes |
| flow_door_pawn_access | Size/prisoner/faction gate permissions | P | Yes | No |
| flow_door_liquid_sealing | Sluice/grate/frame liquid passage | P | Yes | No |
| flow_door_wet_construction | Wet-cell construction survives | P | Yes | No |
| flow_door_orientation | Bank-aware four-facing gate art | P | Yes | Yes |
| raider_trench_strategy | Go around/jump/ladder/fill; siege exclusion | P | Yes | No |
| raider_trench_ladders | Both-wall and colony-ladder crossings | P | Yes | No |
| raider_trench_causeways | Coordinated least-fill breach | P | Yes | No |
| raid_jump_pack_equipment | Stable equipment and landing choice | P | Yes | No |
| wall_climb_jobs | Real geared wall-climbing jobs | P | Yes | No |
| wall_climb_ai | Raid substitution and bounded autoroute | P | Yes | No |
| raid_climbing_gear | Conditional raid equipment allocation | P | Yes | No |
| cliff_shooting_restriction | Relative cliff legality and target filtering | P | Yes | No |
| trench_cover | Direction/body-size cover and hit fold | P | Yes | No |
| trench_ai_cage_avoidance | Cast-candidate selection and cage avoidance | P | Yes | No |
| trench_explosion_damage | No trench reduction of blast damage | P | Yes | No |
| suspension_bridge_construction | Tiered drag/support/build-order rules | P | Yes | No |
| suspension_building_affordances | Building support and excavation guards | P | Yes | No |
| suspension_load_collapse | Ratings, sag, collapse and faction safety | P | Yes | No |
| suspension_support_loss | Saved sequential swing-down | P | Yes | No |
| suspension_railings | Stuff, orders and edge protection | P | Yes | Yes |
| suspension_underpass_bands | Saved bands and actual under-deck travel | P | Yes | Yes |
| suspension_underpass_shots | Solid/grate cross-band shooting | P | Yes | No |
| suspension_underpass_items | Slide/mark-under and grate-held items | P | Yes | No |
| suspension_collapse_crush_wreck | Crush, obstruction and wreck clearing | P | Yes | No |
| suspension_natural_water | River/lake/sea/tower deck paths | P | Yes | No |
| suspension_flood_damage | Scheduled tier-dependent weathering | P | Yes | No |
| suspension_jetty | One-root limits, rails and collapse | P | Yes | No |
| suspension_styles | Four looks and linked deck seams | P | Yes | Yes |
| drawbridge_leaf_geometry | Rigid one/two-leaf motion and limits | P | Yes | Yes |
| drawbridge_work_orders | Real bank-side hand/motor operations | P | Yes | No |
| drawbridge_peace_lock | Hostiles, hold-raised, peace and gate | P | Yes | No |
| drawbridge_tip_riders | Hinge landings, item slides and overflow | P | Yes | No |
| drawbridge_path_invalidation | Toggle paths, reach and swim grids | P | Yes | No |
| drawbridge_winch_loss | Departure crash and injury | P | Yes | No |
| drawbridge_raider_winch_attack | Cut-off raider winch response | P | Yes | No |
| raid_plank_transaction | Supply/interruption/exactly-once crossing | P | Yes | No |
| drawbridge_flexible_lines | Raised-leaf disconnect and reconnect | P | Yes | No |
| drawbridge_save_state | Mid-raise persistence without replay | P | Yes | No |
| drawbridge_art_cables | Styled parts, taut ropes and slack coils | P | Yes | Yes |
| suspension_gravship_launch | Prelaunch bridge/ship-line contract | P | Yes | No |
| grate_fire_and_splash | Fire, toxin and slime through grates | P | Yes | No |
| grate_spill_drain | Exact drainage through grates | P | Yes | No |
| deep_water_walkability | Natural/dug swim routes and toggles | P | Yes | No |
| swim_ability_load | Race/gene/liquid/load/tow profiles | P | Yes | No |
| swim_exhaustion_recovery | Saved fatigue and footing recovery | P | Yes | No |
| swim_warning_shore_escape | Warning and automatic shore route | P | Yes | Yes |
| natural_water_drowning | Posture/size/exit/shallow-water rules | P | Yes | Yes |
| pit_fill_drowning | Actual dug-water drowning and band gates | P | Yes | No |
| pit_fill_toxicity | Fill/resistance/fluid-scaled toxins | P | Yes | No |
| deep_water_item_drop_exclusions | Ordinary item/drop-pod exclusions | P | Yes | No |
| wet_aim_penalty | Chest-depth same-shooter aim reduction | P | Yes | No |
| wet_cold_penalty | Wet comfortable-minimum offset | P | Yes | No |
| swimmer_ranged_restriction | Ranged refusal with appropriate controls | P | Yes | No |
| slime_walking_slips | Natural/dug slips, stun and climb slips | P | Yes | Yes |
| liquid_contact_corrosion | Pawn/apparel/item corrosion and destruction | P | Yes | No |
| hose_saved_state | Reel-owned interrupted state persistence | P | Yes | No |
| hose_save_component_skip | Runtime save exclusion and fail-closed patch | P | Yes | No |
| hose_legacy_aliases | Old types/jobs/pipe defs and removal | P | Yes | No |
| hose_legacy_settings_import | File/style/length/unit/finite migration | Y | No | No |
| hose_carry_state_rules | Exhaustive carry-state invariants | Y | No | No |
| hose_deploy_move_orders | Queued orders, freshness and cancellation | P | Yes | No |
| hose_forced_pawn_orders | Forced/drafted commands and reservations | P | Yes | No |
| hose_order_work_selection | Autonomous work without forced fallback | P | Yes | No |
| hose_walked_trail | Detours, backtracking and stretch drop | P | Yes | Yes |
| hose_interrupt_resume | Drop/pickup/resume with retained orders | P | Yes | No |
| hose_manual_winding | Actual interrupted winding job | P | Yes | Yes |
| hose_route_install | Mouth-based acceptance, length and search | P | Yes | No |
| hose_shape_geometry | Stiff deterministic flat/plump geometry | P | Yes | Yes |
| hose_obstacle_reroute | Safe reroute/retraction after edits | P | Yes | No |
| hose_world_snapshot_cache | Paused/same-tick snapshot freshness | P | Yes | No |
| hose_depth_crossing | Bands, ladders/ramps and cover refusal | P | Yes | No |
| hose_reel_port_detection | Deterministic inlet/endpoint preference | P | Yes | No |
| hose_relay_chains | Indexed directional relays and loop refusal | P | Yes | No |
| hose_free_end_classification | Water/port/free/faction descriptions | P | Yes | Yes |
| hose_free_end_roles | Saved Capped/Intake/Outflow roles | P | Yes | No |
| hose_end_events | Placement/lift callback arguments | P | Yes | No |
| hose_flow_signal | Real credits, leases and debug propagation | P | Yes | No |
| hose_flow_visual_state | Flat/Filling/Plump/Draining hysteresis | P | Yes | Yes |
| hose_liquid_tint | Stable carried-liquid tint | P | Yes | Yes |
| hose_held_volume | Capacity, fill, flush, save and drain | P | Yes | No |
| hose_reel_style_picker | Four-look build/copy/reinstall lifecycle | P | Yes | Yes |
| hose_reel_facing_art | Stored/deployed four-facing reel artwork | P | Yes | Yes |
| hose_placement_preview | Directional outlet preview | P | Yes | Yes |
| hose_fittings_ports | Nozzle/flange/side/under-coupler alignment | P | Yes | Yes |
| hose_layering_crossings | Lift, shadow and fitting suppression | P | Yes | Yes |
| hose_over_building_draw | Visible crossings and rig avoidance | P | Yes | Yes |
| hose_live_carry_draw | Hand tail, cached prefix and far rendering | P | Yes | Yes |
| hose_retract_visuals | Visible clipping, ghosts and timed retract | P | Yes | Yes |
| hose_splice_g2 | Smooth mating, clearance and actual meaning | P | Yes | Yes |
| hose_render_cache_lifetime | Mesh/material reuse and cleanup | P | Yes | No |
| river_world_biome_colors | Biome planet-river palette and redraw | P | Yes | Yes |
| river_current_grid | Natural lanes and painted overrides | P | Yes | No |
| river_current_advection | Pawn/item downstream movement | P | Yes | No |
| river_current_scaling_surges | Size cadence and flood surges | P | Yes | No |
| river_current_crossing_hazards | Bruises and dropped carried goods | P | Yes | No |
| river_current_exemptions | Native/flying/ford/deck/arrest exemptions | P | Yes | No |
| river_current_avoidance | Reversible undrafted river costs | P | Yes | No |
| river_extension_hooks | External current/flood/arrest callbacks | P | Yes | No |
| river_flotsam | Weighted arrivals and downstream departure | P | Yes | No |
| weir_bank_edge_placement | Anchoring and cross-current preview rotation | P | Yes | Yes |
| weir_joined_wall | Run/head, gap and upstream pool | P | Yes | No |
| weir_floating_catch | Conserved existing-item bank capture | P | Yes | No |
| weir_wear_repair | Wear debt, repair and rearming | P | Yes | No |
| weir_breach_wash | Conserved wash and no-room recovery | P | Yes | No |
| weir_stake_cascade | Downstream-only scheduled stake failures | P | Yes | No |
| weir_visuals_styles_foam | Joined four-look art and moving foam | P | Yes | Yes |
| stake_line_levee | Flood barrier and connected ridge | P | Yes | Yes |
| silt_trap_fertility | Reversible timed soil and sediment wedge | P | Yes | Yes |
| ferry_rope_pairing | Saved pairing, rope and safe path | P | Yes | Yes |
| river_ford_stones | Legal shallow-moving-water safe ford | P | Yes | Yes |
| placer_mineral_pool | Geology-derived weighted mineral pool | P | Yes | No |
| placer_shared_stock | Saved stock, recovery and flood refill | P | Yes | No |
| sluice_daily_yield | Scheduled paid sluice production | P | Yes | No |
| panning_mining_work | Real panning duration, XP and payment | P | Yes | No |
| taken_by_land_hold_return | Registered holding and timed return policy | P | Yes | No |
| taken_by_land_identity | Restored faction/guest/gear identity | P | Yes | No |
| taken_by_land_signals | Taken/return/loss letters and traces | P | Yes | Yes |
| taken_by_land_prisoner_return | Secure cell, guard and loss notification | P | Yes | No |
| taken_by_land_escape_capture | Captive current exits become sweeps | P | Yes | No |
| swept_away_legacy_records | Drain pre-service pending records | P | Yes | No |
| liquid_fire_trigger | Adjacent ordinary-fire ignition gate | P | Yes | No |
| liquid_fire_ignition_and_front | Blast/EMP gates and bounded fronts | P | Yes | No |
| liquid_fire_consumption | Exact burn, ash and replacement protection | P | Yes | No |
| liquid_fire_dousing | Foam/rain/roof suppression and relight | P | Yes | No |
| burning_liquid_pawn_effects | Heat, attached fire and exposure | P | Yes | No |
| chemfuel_inferno | Rapid fuel/propane inferno and halo | P | Yes | Yes |
| astrofuel_detonation | Saved deferred blasts and consumption | P | Yes | Yes |
| fuel_fire_events | Announcements and investigation listener | P | Yes | No |
| liquid_room_heat | Hot/cold room energy and targets | P | Yes | No |
| liquid_heat_sampling | Fair bounded sampling and cache refresh | P | Yes | No |
| liquid_surface_materials | Reversible owned liquid materials | P | Yes | Yes |
| liquid_surface_overlay | Drifting sheen/ripples and transparency | P | Yes | Yes |
| liquid_wading_wakes | Liquid-specific pawn wakes | P | Yes | Yes |
| liquid_bubbles | Bounded colored bubble particles | P | Yes | Yes |
| river_steam | Biome/river steam scheduling and color | P | Yes | Yes |
| pit_wall_geometry | Materials, strata, rims and wet faces | P | Yes | Yes |
| pit_pawn_sink_geometry | DrawPos, lip clamp, shadows and origins | P | Yes | Yes |
| pit_lip_occlusion | Occupant windows and wall/shadow clipping | P | Yes | Yes |
| pit_scorch_appearance | Saved fading ash, soot, halo and debris | P | Yes | Yes |
| deep_water_tint | Five/ten-metre navy tint | P | Yes | Yes |
| wet_wall_shadow_band | Directional gap-dependent wall bands | P | Yes | Yes |
| water_look_redraw | Depth-only watcher/mesh invalidation | P | Yes | Yes |
| liquid_join_visuals | Flanges, saddles, risers and under-runs | P | Yes | Yes |
| aerial_line_kinds | Independent pipe/power span rules | P | Yes | No |
| aerial_manual_linking | Reciprocal link/unlink and refusals | P | Yes | No |
| aerial_auto_link | Nearest compatible link and preview | P | Yes | Yes |
| aerial_selected_autolink | Selected shortest spanning forest | P | Yes | No |
| aerial_power_transmission | Remote adjacency and net split/rejoin | P | Yes | No |
| aerial_net_watchdog | Repair genuinely broken standing nets | P | Yes | No |
| aerial_link_persistence | Saved links, HP, fallen and pending state | P | Yes | No |
| aerial_anchor_removal | Kill/dismantle outcomes and reseeding | P | Yes | No |
| aerial_gravship_transport | Ship-local retention and ground coiling | P | Yes | No |
| aerial_roof_cut | Roof removes spans without fallen halves | P | Yes | No |
| aerial_owner_change_cut | Ownership coils cross-owner spans | P | Yes | No |
| aerial_explosion_damage | HP/cut and precise diagonal break | P | Yes | No |
| aerial_kinetic_sway | Kinetic swing without cutting | P | Yes | Yes |
| aerial_span_geometry | Insulators, sag, loops and local drops | P | Yes | Yes |
| aerial_wind_sway | Pinned Auto/Always/Off wind motion | P | Yes | Yes |
| aerial_span_shadows | Sag/height-dependent ground shadows | P | Yes | Yes |
| aerial_fallen_geometry | Continuous obstructed fallen lays | P | Yes | Yes |
| aerial_fallen_liveness | Polls, frays, glow and source-off state | P | Yes | Yes |
| aerial_wall_bracket_mount | Four-facing bracket geometry | P | Yes | Yes |
| aerial_restring_job | Real repair, speed and own-cut exemption | P | Yes | No |
| aerial_wire_down_alert | Multi-map culprit and repair clearing | P | Yes | Yes |
| fallen_wire_shock | Ground shock, recovery/death and knockback | P | Yes | No |
| external_live_wire_contacts | FlowWorks/GSS shared shock contacts | P | Yes | No |
| fallen_wire_ignition | Wire ignition of items/canal/sheet fuel | P | Yes | No |
| power_tap_transfer | One-way shared-surplus power ledger | P | Yes | No |
| power_tap_faction_isolation | Own connection, separate victim grid | P | Yes | No |
| power_theft_consequences | Witness/letter/time-based goodwill | P | Yes | Yes |
| power_tap_visuals | Clamp bite, jaws and both-grid leads | P | Yes | Yes |
| aerial_anchor_styles | Four-look construction/copy/reinstall | P | Yes | Yes |
| aerial_lamp_mast | Vanilla-like lamp and color controls | P | Yes | Yes |
| conduit_run_styles | Stored looks, merge/split/restyle | P | Yes | Yes |
| conduit_legacy_styles | Unwritten legacy default appearance | P | Yes | Yes |
| conduit_pending_save_resolution | Immediate-save pending style drain | P | Yes | No |
| conduit_lamp_styles | Run following, overrides and restoration | P | Yes | Yes |
| conduit_switch_art | Styled on/off art over cords | P | Yes | Yes |
| conduit_style_materials | Full art/variants and color modes | P | Yes | Yes |
| conduit_target_selection | Per-def targets and original restoration | P | Yes | Yes |
| machine_hookup_rendering | One hookup owner and retained overlay | P | Yes | Yes |
| cord_world_snapshot | Terrain/fog/roof/tree/busy-link inputs | P | Yes | No |
| cord_machine_connections | Single leads and correct device homes | P | Yes | Yes |
| cord_graph_reduction | Chains, stubs, spurs and ring seams | P | Yes | No |
| cord_path_planning | Obstacles, doors and barrier dives | P | Yes | No |
| cord_slack_shapes | Loops/heaps, busy avoidance and settle | P | Yes | Yes |
| cord_connected_piles | Occupied connectors, entries and scatter | P | Yes | Yes |
| cord_live_dead_ends | Connected live/dead terminal shapes | P | Yes | Yes |
| cord_motion_effects | Sway/ripple/whip/bursts/spark budgets | P | Yes | Yes |
| cord_static_rendering | Sections, bounds and one drawing owner | P | Yes | Yes |
| cord_selection_highlight | Exact selected-net highlight | P | Yes | Yes |
| cord_lod | Near/far/shader ownership and fallback | P | Yes | Yes |
| cord_gravship_render_guard | Idle/cutscene/capture visibility | P | Yes | No |
| cord_rebuild_invalidation | Local/offscreen/tree/same-frame refresh | P | Yes | No |
| cord_geometry_determinism | Seeded rebuild/load geometry equality | P | Yes | No |
| cord_runtime_save_compat | Component exclusion and mod-less load | P | Yes | No |
| gss_session_reset | Clear session ledgers/picks/probes/caches | P | Yes | No |
| legacy_name_migration | Old types/files/loop-budget migration | Y | No | No |
| flexible_line_draw_order | Shared line/fitting/overhead order | P | Yes | Yes |
| line_crossing_placement | Surface matrix and frame recheck | P | Yes | No |
| line_dig_breakage | One committed break and network split | P | Yes | No |
| deck_collapse_lines | Cord halves, hose retract and teardown | P | Yes | No |
| pipe_pole_network_integration | Aerial/fitting edges and topology callbacks | P | Yes | No |
| line_crossing_readouts | Crossing/support/leaf explanations | P | Yes | Yes |
| map_control_lifecycle | Saved unowned dev-only markers | P | Yes | Yes |
| flow_source_input | Fractional rate and blocked-flow behavior | P | Yes | No |
| flow_sink_drain | Filtered/rate-limited/unlimited sinks | P | Yes | No |
| liquid_level_holder | Exact channel/body setpoint control | P | Yes | No |
| timed_map_controls | Clock/period switching and flow doors | P | Yes | No |
| painted_water_current | Direction/strength and actual advection | P | Yes | No |
| liquid_thermostat | Wet-room energy convergence | P | Yes | No |
| flow_meter_history | Connected stock and saved daily history | P | Yes | Yes |
| sheet_physical_ingress | All five real overflow callers | P | Yes | No |
| sheet_topology_fluid_rules | Obstacles/lips and fluid compatibility | P | Yes | No |
| sheet_spill_backpressure | Atomic preview, caps and offer order | P | Yes | No |
| sheet_conservative_flow | Conservative flux, relief and rest | P | Yes | No |
| sheet_door_leakage | Bounded doorway seepage | P | Yes | No |
| sheet_receiver_return | Exact cut/pond return and handover | P | Yes | No |
| sheet_losses_irrigation | Fluid losses, boiling and irrigation API | P | Yes | No |
| sheet_crop_damage | Irrigation then delayed crop death | P | Yes | No |
| sheet_freeze_thaw | Conserved ice and paused effects | P | Yes | Yes |
| sheet_pawn_effects | Wading cost, wet thought and toxins | P | Yes | No |
| sheet_fire_extinguishing | Nonburnable sheet douses ordinary fire | P | Yes | No |
| sheet_liquid_fire | Sheet/channel fire fronts and harm | P | Yes | No |
| sheet_fuel_detonation | Deferred capped sheet explosions | P | Yes | No |
| sheet_overlay_readout | Film/sheet/pool/ice art and depth | P | Yes | Yes |
| sheet_persistence_ledger | Full saved state, continuation and purge | P | Yes | No |
| sheet_switch_off_draining | OFF refuses inputs while draining | P | Yes | No |
| debug_excavation_ledger | Instant excavation/layer/ledger tools | P | Yes | Yes |
| debug_tank_contents | God-mode picker and fill/empty counters | P | Yes | Yes |
| debug_subsurface_yield | Give/clear deterministic deposit | P | Yes | No |
| proof_probe_contracts | Probe schema, actions and refusal contracts | P | Yes | No |
| harmony_patch_isolation | Patch/bootstrap and shared-type isolation | P | Yes | No |
| validation_provenance | Repo/defs/DLL/MVID/running-mod identity | P | Yes | No |
| validation_preflight | Map, calm environment, vitals and logs | P | Yes | No |
| validation_site_fixtures | Bounds, cells, RLE and thing manifests | P | Yes | No |
| validation_setting_isolation | Exact backup/restore and failure cleanup | P | Yes | No |
| validation_manifest_catalog | Declared/emitted rows and current evidence | Y | No | No |
| proof_verdict_integrity | Honest verdicts, exits and negative controls | Y | No | No |
| validation_session_orchestration | Bridge/shared-clock/checkpoint discipline | P | Yes | No |
| offline_game_transport | Strict mocks and tool-schema faults | Y | No | No |
| selftest_runner | Dispatch, nonempty execution and failures | Y | No | No |
| source_wiring_guards | Scoped source/XML guards and mutants | Y | No | No |
| sequence_fuzz_replay | Seeds, nonvacuity, shrinking and replay | Y | No | No |
| kernel_oracle_protocol | Independent kernel/body/graph comparison | Y | No | No |
| validation_matrix_coverage | Pairwise/reduced/replay catalogue coverage | Y | No | No |
| geometry_art_audits | Independent rulers and fresh fixtures | P | Yes | No |
| performance_budgets | Kernel/runtime timing and allocation gates | P | Yes | No |
| runtime_cache_lifecycle | Map/session cleanup and mesh disposal | P | Yes | No |
| review_evidence_status | Fresh evidence, work ledger and decisions | Y | No | Yes |
| review_map_layout | Coverage/navigation/signs/keeper save | P | Yes | Yes |
| scenario_composite_staging | References, partial builds and idle soak | P | Yes | No |
| visual_review_artifacts | Framing/crops/captions/index accumulation | P | Yes | Yes |
| validation_image_evidence | Pixel sanity and aligned wire evidence | Y | No | No |
| playtest_journal_resume | Complete two-branch recipe journal | P | Yes | No |
| player_mission_limits | Whitelist, deadlines and friction | P | Yes | No |
| canal_defense_mission | Player-built filled defensive canal | P | Yes | No |
| pit_prisoner_hold_mission | Same prisoner held for required duration | P | Yes | No |
| pump_crossing_mission | Destination gain and safe crossing | P | Yes | No |
| review_art_manifest | Exhaustive look/resource/fallback inventory | Y | No | Yes |
| cord_unroutable_diagnostics | Classified failed-leg diagrams | Y | No | Yes |
| lake_floor_preview | Floor contours and escape statistics | Y | No | Yes |

### 2. PLAN H — HUMAN REVIEW (what the owner walks and looks at)

**One joint station, H1 — “The watershed works and fortified settlement.”**

Use an **existing** through-river quicktest/review map, preferably at least 250×250. Do not invoke `--fresh-map`, settlement founding, candidate-map generation or any world-generation API. If no suitable existing map exists, the river-dependent part remains unavailable; creating one is outside this plan.

**Footprint:** approximately 224×224, adapted around the existing river. Maintain a six-cell circulation path and clear sightlines between the working parts. This is one connected hydraulic and electrical installation: river intake → storage/processing → settlement consumers → lock/basin → return/overflow; the keep’s bridge carries the installation’s power and flexible liquid lines.

```text
                       EXISTING UPSTREAM RIVER
             weir—silt—placer—ferry/ford—levee
                         │ intake
        ┌────────────────┴──────────────────────────┐
        │ varied lake bowl / drawdown shore         │
        │ fish, reeds, mud, lakebed, deep-water tint │
        │                   │                       │
        │ quarry + drill → tanks → processing yard  │
        │ ramps/ladders      │      isolated fuels │
        │                    ├→ bath/faucet/clinic  │
        │                    └→ sprinklers/swale    │
        │                            │              │
        │ keep + moat + drawbridge + lock chamber   │
        │ pit prison / covers / underpass / rails  │
        │ power poles—pipe poles—cord/hose crossing│
        │                            │              │
        │ walled spill yard → receiving basin      │
        └────────────────────────────┴──────────────┘
                          EXISTING DOWNSTREAM RIVER
```

The rectangles above are functional parts of the same site, **not additional independently staged stations**. The owner receives one keeper save and a numbered camera route.

**Build/stage:**

- Existing river bank works, including weir sections, stake ridge, ferry posts, ford stones, silt trap, sluice box and panning spot.
- One varied natural-style bowl, a stepped 4 m/7 m reservoir, shallow-water strips and a visibly exposed shore. The large automated lake can occupy this footprint in the separate N checkpoint.
- `RM_LiquidTank` and the other shipped tank sizes; cargo tank; `RM_UniversalPipe`; reels; ordinary pump and industrial pumping-station stages. Include all four looks and all relevant facings/port lanes.
- Solar, drip, fueled and industrial conversion examples; reaction vat; bath; faucet; container craft/drink/wash cycle; clinic/prison service.
- A single keep/moat crossing containing timber and steel drawbridge examples, a hung bridge with solid/grated comparison, underpass, jetty, covers, ramps, ladders, guardrails and spikes.
- A connected electrical installation containing four stored looks, Modern color modes, Industrial cable variants, merge/split/restyle examples, lamps/switches, piles, wall/rock/water entries, brackets and a foreign-grid tap.
- A contained spill yard connected to the receiving basin. Fuel/fire demonstrations run only in its saved destructive branch.
- Persistent station books giving **DO / LOOK / EXPECT / CAPTURE** instructions. Signs and captions identify every surrogate or untested integration.

**Capture schedule and framing:**

| Capture | Time/zoom/frame | Pass looks like | Fail looks like |
|---|---|---|---|
| H1-00 orientation | Clear noon; whole-site overview | One understandable working installation; readable route | Overlapping props, inaccessible route, missing sections |
| H1-01 water | Noon; fixed near view, roughly 80–100 px/cell; matched canal/lake depths | Matching equal-depth water; distinct shallows; darker 5/10 m water; appropriate wall band | Color seam, stale tint, wrong depth rung, opaque missing floor |
| H1-02 shore | Same camera before drawdown, at partial depth, mud, dry bed and refill | Shallowing precedes exposed mud; varied plausible floor; restored outline | All-deep appearance until disappearance, floating geometry, altered outline |
| H1-03 pit | Noon and low-angle daylight; south lip plus N/E/W comparisons | Pawn below rim, correct near-bank occlusion, wall shadows retained, spikes readable | Sunny square, lip paints over walls, outside pawn hidden, floating spikes |
| H1-04 access/bridges | Near view; above/below walkers; solid/grated pair | Upright ladders, coherent gates, continuous deck atlas, readable underpass fade | Crawling/sideways ladders, seams, opaque underpass, misplaced rails |
| H1-05 drawbridge | Identical lowered, intermediate and raised frames; timber/steel, both hinges | Rigid leaf; ropes reach fittings when lowered; slack coils stay on bank when raised | Rope gaps, stiff rope over pit, wrong material/facing, detached hook |
| H1-06 joints | Near crops of every enumerated equipment port, all looks/facings | Hose meets nozzle/flange; pipe goes beneath fixture; riser reaches tank | Floating coupling, exposed stub, sideways gap, giant fitting |
| H1-07 hose motion | Fixed camera; deploy, carry, flowing, stopped and winding clips | Correct hand tail; visible swelling; clean crossing lift/shadow; gradual retract | Hose clips walls/rigs, full hose thinner, flicker, disappearing winding |
| H1-08 industry/containers | Noon; machinery and bench close-ups | Distinct stages/looks; liquid window and material trim remain legible | Borrowed/wrong art, indistinguishable looks, lost wear/style |
| H1-09 farm/heat | Noon spray clip; enclosed bath; hot/cold liquid views | Tinted spray, readable status; steam/bubbles/wakes suit liquid | Spray through walls, missing particles, identical vigorous wakes in tar |
| H1-10 river works | Noon; upstream/downstream sides and foam clip | Continuous weir/posts/ridge; directional moving foam; rope meets posts; upstream silt wedge | Frozen foam, wrong side, gaps, disconnected rope, downstream wedge |
| H1-11 electrical art | Noon; all looks, wall faces, piles and clamp close-ups | Single device leads, occupied connectors, clamp bites victim cable, sensible wall mounts | Phantom live lead, loose end joins body, idle strips, hovering plates |
| H1-12 electrical motion | Fixed near camera; wind/preference/roof variants; then far zoom | Pinned endpoints; live/dead distinction; controlled bursts; one render path; clean LOD | Double/missing strands, roofed sway, stretched dark strip, stale glow |
| H1-13 lighting/alerts | Dusk/night, same installation; power cut/repaired variants | Lamp controls work; live ends glow; relevant alerts/letters point to correct things | Wrong source lights, unreadable alert, incorrect targets |
| H1-14 hazards | Destructive branch; fixed fireyard frames and short clips | Distinct fuse/inferno/detonation, scorch, residue and sheet tiers | Fire outside intended branch, wrong liquid art, missing scorch/residue |
| H1-15 freeze | Cold branch then thaw, identical views | Recognizable body/sheet ice and restored liquid appearance | Permanent stale ice, wrong overlay, water picture disappears |
| H1-16 UI | Settings, search, reset confirmation/cancel, inspect panes, needs/health/thoughts | Labels found; dependents shaded; cancellation preserves values; readable quantities | Blank search sections, unshaded dependents, silent reset, wrong units |
| H1-17 supporting artifacts | Review sheet, art manifest, failed-leg diagrams, floor previews | Current captions/evidence; retained decisions; clearly labeled diagnostics | Stale PASS, missing crops, orphaned images, overwritten decisions |

All motion clips have a fixed camera and a visible clock. Record selected thing IDs, settings, liquid identity, depth and style beside each capture. Take both an unmarked image and an annotated copy.

Keep **calm**, **cold**, **fire/destruction** and **hostile** checkpoints of this same station. The human route starts calm; destructive phases reload the checkpoint. No flight demonstration belongs in any branch.

### H coverage matrix

Every feature marked Eyes=Yes above appears below. H1 suffixes are capture IDs, not stations.

| feature_id | station | what to look at |
|---|---|---|
| typed_liquid_shores | H1-01 | Staged typed shore appearance; generation explicitly unproven |
| liquid_works_ruin_stock | H1-08 | Damaged machinery and visible stock/readout |
| industrial_ruin_restoration | H1-08 | Wrecked/kludged/repaired silhouettes |
| flowworks_localized_feedback | H1-16 | Labels, refusals, substitutions and letters |
| review_station_signs | H1-00/17 | Persistent books and readable instructions |
| settings_ui | H1-16 | Tabs, layout and dependent controls |
| settings_search | H1-16 | Partial-label searches and no blank separators |
| settings_reset | H1-16 | Scope, confirmation and unchanged Cancel |
| liquid_look_tuning_export | H1-01/16 | Tuned appearance and matching exported values |
| deep_dig_wait_alert | H1-13/16 | Waiting order and useful culprit explanation |
| pond_depth_surface | H1-02 | Shallowing before shoreline loss |
| pond_mud_lakebed | H1-02 | Mud then appropriate dry lakebed |
| pond_dry_bed_hollows | H1-02 | Floor remains physically below bank |
| lake_floor_generation | H1-02/17 | Varied floor, shelves and escape route |
| liquid_depth_readout | H1-01/16 | Separate hole/water depth and correct units |
| water_depth_ladder | H1-01 | Consistent equal-depth pond/canal rungs |
| pond_freeze_thaw | H1-15 | Ice and restored liquid picture |
| dig_discovery_letters | H1-13 | Correct first-find name and target |
| tar_front_glass | H1-14 | Glass only where eligible; no fabricated successful release |
| drill_placement_status | H1-16 | Useful survey/outlet/power explanation |
| pump_status_warnings | H1-16 | Accurate stopped/blocked/circulating status |
| faction_liquid_theft | H1-13 | Foreign ownership and witness letter |
| hot_release_effects | H1-09/14 | Steam and cooling patch presentation |
| drained_liquid_residue | H1-14 | Cleanable stain versus persistent tar |
| sprinkler_pipe_placement_style | H1-06/09 | Head/faucet joins pipe and inherits look |
| sprinkler_visual_status | H1-09/16 | Spray tint and dry/clog/no-pressure text |
| container_four_styles | H1-08 | Four bodies, trim, liquid window and scale |
| thirst_decay | H1-16 | Need bar and changing arrow |
| dehydration_progression | H1-16 | Readable staged illness |
| thirst_mood_categories | H1-16 | Appropriate thirst thought text |
| partial_container_drinks | H1-08/16 | Partly drunk quantity and container identity |
| ladder_hanging_and_reach | H1-04 | Four wall orientations and ineffective flat pose |
| ladder_raise_lower | H1-04 | Raised/lowered pose and operation |
| pit_stuck_alert | H1-13 | Correct critical alert and culprit |
| pit_spikes | H1-03 | Dry/submerged spoke artwork |
| fall_guardrails | H1-03/04 | Wood/steel guardrail art and connected lip |
| pit_cover_surface_mimic | H1-03 | Uniform surrounding-ground camouflage |
| span_walking_surface | H1-03/04 | Walker on lid stays at ground level |
| flow_door_orientation | H1-04 | Four-facing closed/open sluice and grate |
| suspension_railings | H1-04 | Valid material and exposed-edge continuity |
| suspension_underpass_bands | H1-04 | Floor occupant remains below faded deck |
| suspension_styles | H1-04 | Coordinated parts/wrecks and seamless atlas |
| drawbridge_leaf_geometry | H1-05 | Rigid motion and correct hinges |
| drawbridge_art_cables | H1-05 | Material precedence, rope reach and slack coils |
| swim_warning_shore_escape | H1-13 | Timely readable fatigue warning |
| natural_water_drowning | H1-13/16 | Drowning warning while subject is alive |
| slime_walking_slips | H1-07 | Visible stumble/stun and climb slip |
| hose_walked_trail | H1-07 | Trail follows actual walk/backtrack |
| hose_manual_winding | H1-07 | Progress and shortening hose |
| hose_shape_geometry | H1-07 | Stiff bends, lead-out and thickness |
| hose_free_end_classification | H1-16 | Correct port/water/faction wording |
| hose_flow_visual_state | H1-07 | Filling/plump/draining without flicker |
| hose_liquid_tint | H1-07 | Sustained content-dependent color |
| hose_reel_style_picker | H1-06/08 | Four stored looks and picker |
| hose_reel_facing_art | H1-06 | N/E/S/W stored/deployed art |
| hose_placement_preview | H1-06 | Arrow leaves actual nozzle side |
| hose_fittings_ports | H1-06 | Every measured port crop |
| hose_layering_crossings | H1-07 | Lift/shadow and suppressed colliding fittings |
| hose_over_building_draw | H1-07 | Crossing remains visible over furniture |
| hose_live_carry_draw | H1-07 | Hand attachment near/far |
| hose_retract_visuals | H1-07 | Clipping, ghost completion and no instant disappearance |
| hose_splice_g2 | H1-06/07 | Smooth face-to-face mate; caption hydraulic status |
| river_world_biome_colors | H1-17 | Existing-world river palette view |
| weir_bank_edge_placement | H1-10 | Across-current placement preview |
| weir_visuals_styles_foam | H1-10 | Joined four-look wall and moving foam |
| stake_line_levee | H1-10 | Continuous ridge and deliberate gap |
| silt_trap_fertility | H1-10 | Upstream wedge and soil change |
| ferry_rope_pairing | H1-10 | Rope reaches both posts |
| river_ford_stones | H1-10 | Coherent shallow crossing |
| taken_by_land_signals | H1-13 | Taking/return/loss messages and trace |
| chemfuel_inferno | H1-14 | Large fast flames and light |
| astrofuel_detonation | H1-14 | Deferred explosion sequence, no flight test |
| liquid_surface_materials | H1-01/14 | Distinct materials and repeated toggle restoration |
| liquid_surface_overlay | H1-01/09 | Sheen/ripples and underwater transparency |
| liquid_wading_wakes | H1-09 | Broad water versus restrained viscous wakes |
| liquid_bubbles | H1-09 | Appropriate color/rate/scale |
| river_steam | H1-10 | River-only colored ribbons |
| pit_wall_geometry | H1-03 | Soil/stone/strata/rim and wet faces |
| pit_pawn_sink_geometry | H1-03 | Sink, tween and absent false ground shadow |
| pit_lip_occlusion | H1-03 | Correct occupant window and wall shadows |
| pit_scorch_appearance | H1-14 | Varied ash, soot, halo and fading |
| deep_water_tint | H1-01 | Control/5 m/10 m navy progression |
| wet_wall_shadow_band | H1-01 | Gap-dependent directional band |
| water_look_redraw | H1-01 | Tint changes without stale terrain picture |
| liquid_join_visuals | H1-06 | Flanges/risers/saddles and under-building runs |
| aerial_auto_link | H1-11 | Preview points to compatible nearest anchor |
| aerial_kinetic_sway | H1-12 | Decaying swing with intact cable |
| aerial_span_geometry | H1-11 | Insulator attachment, sag, loops and drops |
| aerial_wind_sway | H1-12 | Pinned endpoints and preference behavior |
| aerial_span_shadows | H1-11 | Shadow follows span height |
| aerial_fallen_geometry | H1-11 | Continuous hanging-to-ground halves |
| aerial_fallen_liveness | H1-12/13 | Live glow/sparks versus cold dead end |
| aerial_wall_bracket_mount | H1-11 | All four wall faces and looks |
| aerial_wire_down_alert | H1-13 | Correct anchor targets and clearing |
| power_theft_consequences | H1-13 | Clamp/witness letter and named goodwill reason |
| power_tap_visuals | H1-11 | Jaws bite victim wire; both leads meet clamp |
| aerial_anchor_styles | H1-11 | Build/copy/reinstall preserves chosen art |
| aerial_lamp_mast | H1-13 | Flick/color/darklight controls and light |
| conduit_run_styles | H1-11 | Merge winner, split retention and whole-run restyle |
| conduit_legacy_styles | H1-11 | Legacy follows default without stored repaint |
| conduit_lamp_styles | H1-11/13 | Run-follow versus deliberate lamp override |
| conduit_switch_art | H1-11 | On/off artwork covers cords |
| conduit_style_materials | H1-11 | Complete looks, Industrial types and Modern colors |
| conduit_target_selection | H1-11 | Hidden/excluded/master-off appearance |
| machine_hookup_rendering | H1-11 | One normal hookup; overlay connections retained |
| cord_machine_connections | H1-11 | Single leads disappear beneath correct home |
| cord_slack_shapes | H1-11 | Slack/heaps without lassoing nearby pipes |
| cord_connected_piles | H1-11 | Occupied sockets and plausible scatter |
| cord_live_dead_ends | H1-12 | Live whip versus limp dead end; no false joins |
| cord_motion_effects | H1-12 | Sway/ripple/bursts and bounded visible sparks |
| cord_static_rendering | H1-12 | No missing/doubled section-boundary strands |
| cord_selection_highlight | H1-12 | Only selected electrical net highlights |
| cord_lod | H1-12 | Clean near/far transition |
| flexible_line_draw_order | H1-06/11 | Ground, hose, clamp and overhead layering |
| line_crossing_readouts | H1-16 | Accurate support/leaf-cut explanation |
| map_control_lifecycle | H1-16 | Quiet unowned markers and dev controls |
| flow_meter_history | H1-16 | Readable stock/net-history overlay |
| sheet_freeze_thaw | H1-15 | Sheet ice and restored overlay |
| sheet_overlay_readout | H1-14/16 | Distinct film/sheet/pool/ice and depth |
| debug_excavation_ledger | H1-16 | Dev tools and layer/ledger output |
| debug_tank_contents | H1-16 | Liquid picker and fill/empty gizmos |
| review_evidence_status | H1-17 | Freshness and preserved owner decisions |
| review_map_layout | H1-00/17 | Route, labels and keeper-save usability |
| visual_review_artifacts | H1-17 | Accurate crops/captions and retained index |
| review_art_manifest | H1-17 | Missing/fallback resources visibly identified |
| cord_unroutable_diagnostics | H1-17 | Correctly labeled diagnostic diagrams |
| lake_floor_preview | H1-17 | Contours agree with displayed floor statistics |

### H replaces

These are **planned staging replacements**, subject to the coverage and capture gates above.

| existing script | station(s) that replace it |
|---|---|
| FlowWorks `review_map.py`, `review_map_visuals.py` | H1, especially 01–09 and 14–16 |
| FlowWorks `review_map_rivers.py` | H1-10/13 |
| FlowWorks `northstar/owner_review_stage.py` | H1-01–09/16 |
| FlowWorks `northstar/objects_sheet.py` | H1-04/06/08/10 |
| FlowWorks `northstar/scenarios_map.py`, `scenarios/c01_*.py` through `c13_*.py` | H1’s connected installation and saved phases |
| FlowWorks `northstar/river_scenes_walk.py` | H1-10/13 |
| FlowWorks `northstar/water_scenes_walk.py` visual output | H1-01/02/15; state assertions move separately to N1 |
| FlowWorks `northstar/annotate_water_scenes.py` | H1-17 caption/index producer |
| FlowWorks `northstar/lake_floor_stage.py` | H1-02 using existing terrain only; its generation path is excluded |
| FlowWorks `northstar/joint_check.py --crops` | H1-06/07 plus N1 geometry reads |
| GSS `human_review.py` | H1-11–13/16/17 |
| GSS `pole_shots.py` | H1-11/12 with stored styles, not merely changed defaults |
| GSS `shader_sway_look.py` | H1-12 fixed-camera CPU/shader/roof comparisons |
| GSS `northstar_matrix/run_live.py` screenshot sweep/contact sheets | H1-11/12/17; retain catalogue and state comparisons offline/N1 |
| GSS `save_review_map.py` | H1 keeper-save operation and new-file-only verification |

`human_review.py`’s FlowWorks evidence aggregation, art manifests, preview generators and report tests remain supporting tooling. A map station does not replace those functions.

### 3. PLAN N — NORTHSTAR AUTOMATED REVIEW (deterministic state reads, PASS/FAIL rows)

**One joint station, N1 — “The watershed acceptance rig.”**

Use the same existing map and physical installation as H1, but start from its own clean checkpoint. Human acceptance and automated acceptance have separate manifests and results.

**Setup and execution contract**

1. Freeze source, generated defs, installed assets, deployed DLL/MVID, mod order and existing map identity. All DLCs are present; optional mods are explicitly inventoried.
2. Read back every staged depth, exact dL amount, liquid identity, mode, style, faction, roof, blueprint, building and pawn ID. A failed read cannot become zero.
3. Give each physical transfer its own before/after ledger. Include canal, pond, tank, hose, sheet, external storage and disclosed exits.
4. Run quiet jobs first, long-lived timers together on one clock, then cold, fire/destruction and hostile branches. Restore the same checkpoint between incompatible branches.
5. Scheduled tests cross the **actual next due tick** and at least two relevant periods. Long tests retain their real durations: 15,000-tick thirst decay, 60,000-tick dehydration/theft checks, crop-standing duration, plant grace and normal production deadlines.
6. Actual-work rows use autonomous work selection or a declared player order as appropriate. Direct `Proof*` staging does not satisfy a job-completion row.
7. Save/load tests compare immediate restored state **and equal-tick continuation against an uninterrupted branch**. Preserve exact dL, identities, pending events and named pawn IDs.
8. Each row below emits one acceptance verdict with parameterized diagnostics. “All” means every applicable entry in the frozen def/settings manifest, not a hand-picked favorable sample.
9. Missing tool/content/clock/read, prohibited execution or incomplete branch produces **UNMEASURED**, never PASS. A behavioral disagreement produces FAIL/MOD; setup and harness failures retain their classification. Any required FAIL or UNMEASURED prevents complete certification.

**Offline set retained**

| ID | offline test set that stays offline |
|---|---|
| O1 | Package/csproj/defs/patches/localization/generator synchronization; settings registry/defaults; lava/DBH/donor contracts; shared-type isolation |
| O2 | Full FlowWorks `Source/SelfTest` executable: all production-linked math, regressions, fuzz, source guards and performance cases |
| O3 | Full `Source/SelfTestTrench` executable and its directional/stacking/exclusion cases |
| O4 | Full GSS `Source/SelfTest` executable, oracle fixtures, geometry/art-fit rules, aerial/tap/style/migration/fuzz cases |
| O5 | Python model/oracle collection: exact-water differential, body components, GSS graph/matrix/pairwise/reduced/replay checks |
| O6 | Installed-art and independent measurement checks: hose ports/fittings, tank edges, bridge atlases/cables, styles/materials, image mutants |
| O7 | Python harness/report/mock selftests: verdicts, manifests, arguments, restoration, clocks, journals, missions, capture/index and fault recovery |
| O8 | Preview/census/report artifacts: ladder census, lake-floor preview, unroutable diagnostics, art manifest and evidence-sheet checks |

These are logical bundles under one offline entry point. **Do not discard assertion bodies merely because two wrappers invoke the same executable.** Deduplicate invocations first.

### N1 action sequence and complete emitted row list

The sequence is: **00 setup → W/C hydrology → M/T supply and consumers → P/B access and crossings → H/G flexible lines and electricity → R river lifecycle → S overflow/fire → V render-state observations → X workload/player branches → restore**.

| row_id | state read | pass condition | fail means |
|---|---|---|---|
| 00.identity | Repo/defs/assets/DLL SHA, MVID, ordered running IDs, map ID | All match frozen manifest; recorded mod count is measured | Wrong build, configuration or map |
| 00.fixture | Bounds, terrain/roof/depth/dL/fluid, things, pawns, signs | Complete expected manifest matches; no overlaps or foreign leftovers | Invalid or contaminated fixture |
| 00.settings_ui | Listed categories, labels, search hits, dependencies, reset/cancel values | Required entries occur once; search/dependencies/scope/cancel behave correctly | UI wiring or reset defect |
| 00.settings_save | Actual settings XML and read-back values, engine latch, fingerprints | All owned fields round-trip; defaults/migrations correct; latch changes only at permitted boundary | Persistence/default/latch defect |
| 00.registry | Loaded defs/forms/properties/extensions/designators and ConfigErrors | Required references resolve; conditional content matches installed donors; no unexpected errors | Def/patch/binding defect |
| 00.probes_debug | Request serial/map, invalid-command refusals, dig/fill/tank/deposit counters | Correct map services requests once; invalid input refuses; debug mutations/readouts balance | Probe or debug-tool defect |
| 00.logs | Sentinel, log sequence/loss counters, errors, vitals, threats | Complete log coverage; no unapproved errors/threats; bystanders remain healthy | Unreliable or polluted run |
| 00.report | Declared/emitted IDs, current stamps, stale/mock/missing faults, exit status | Exact row set; injected faults demote verdicts; incomplete results cannot certify | False certification |
| 00.lifecycle | Saved component list, map/session caches, meshes, pending requests | Runtime-only components excluded; original runtime restored; removed-map/session state cleared | Save hygiene or stale-state leak |
| 00.worldgen | Forbidden-call trace and offline generation contracts | No generation calls occur; offline contracts pass; live-generation obligation remains UNMEASURED | Constraint violation or unsupported coverage claim |
| 00.flight | Launch/cast/flight call trace and offline travel/gravship contracts | No flight launches occur; offline contracts pass; flight outcomes remain UNMEASURED | Constraint violation or false flight claim |
| 00.optional | DBH/VFE/VE/HugeThings/biome/LuminousPigment/investigation availability | Each integration has its own actual configuration/result; absence never passes integration | Missing or misrepresented integration |
| W01.dig | Designation, selected worker/job, work, depth/terrain and finds | Autonomous eligible miner completes one paid cut; undesignated/incapable controls do not | Dig/workgiver integration broken |
| W02.depth | Saved target, repeated cuts, human/machine caps, work curve, alert | Target reached or correctly waits; cap reduction never shallows; work and alert agree with rules | Deep-order/cap/labor defect |
| W03.fill | Conflicting/stale orders, occupied cells, completed fill and all destinations | Invalid/occupied work refuses; valid work completes; exact displaced volume reaches stores/sheet/disclosed loss | Unsafe or lossy filling |
| W04.repair | Old/corrupt save fixtures, grids, versions, original terrain, body indexes | Expected repair/migration occurs once; exact quantities retained; legacy D=0 stays filled after reload | Migration/repair regression |
| W05.palette | Saturated palette, refused claim, source and identity grids | Compaction preserves identities; impossible claim leaves source/grid unchanged | Anonymous/retyped/lost liquid |
| W06.exact | 4 m/7 m basin depths, dL, analytic level and sill components | 152,000 L full case and partial cases conserve; connected gap ≤1 cm; sills split/join correctly | Exact solver or measurement defect |
| W07.whole | Whole-notch deep-grid traces and drain totals | Bounds/conservation hold above 2 m; settles without stripes or reciprocal shuttling | Legacy-mode regression |
| W08.fronts | Water/tar/slime paired vectors, fluid IDs, mouth stock | Contiguous paid fronts; authored viscosity lag; OFF control removes lag; incompatible fronts retain identity | Front, viscosity or nonmix defect |
| W09.sources | Footprint/cap/truncation/endless flags, shared branch traces | Exact-cap classification correct; both branches receive supply; finite source pays and stops at zero | Classification or free-source defect |
| W10.partial | Stock, histogram, water surface, wet terrain and model toggle | Partial shallowing precedes dry cells; head/return rules correct; toggle preserves stock | Pond-picture/head defect |
| W11.large_lake | 72×72 isolated bowl, recorded beds, dry/wet order, escape, shape hash | >4,000 cells remain finite/untruncated; shallow-first drawdown; grounded pawn walks out; refill restores hash | Large-lake or floor/access regression |
| W12.beds | Detach/reattach membership, capacity, first-cut depth, saved provenance | Capacity inverse closes; dry bed remains hollow; fill restores recorded bed | Capacity multiplication or provenance loss |
| W13.refill | Weather/season pulses, blocked cells, item destinations, stock | Exact expected recharge; occupied cells wait; items remain accounted; later restoration succeeds | Refill or occupant-safety defect |
| W14.trackers | Tracker components, fish/populations, zone IDs/settings, plant timers | Independent components agree; fish/zone memory restores; growth rolls and grace boundaries correct | Water-body/fishing repair defect |
| W15.ice | Freezable count, ice cells, body volume and type changes | Runtime recount matches eligible cells; freeze/thaw conserves; fresh/salt flip preserves valid membership | Tracker/freezing/type-flip defect |
| W16.rain_edges | Open/roofed dL, accumulator, edge rulings, sinks and disabled inputs | Only eligible rain enters; exact capacity; sealed/off controls hold; enabled drain books outflow | Rain/edge/filter defect |
| W17.pressure | Input seeds, extension after reload, seam cursor and far cells | Pump/drill pressure resumes; every seam receives service; far cells wet within bounded deadline | Driver or partition starvation |
| W18.reload | Exact cells/body/gate/pending state and equal-tick twins | Immediate and continued states match, including identities and exits | Save/load nondeterminism |
| W19.finds | Real soil/rock/deep cuts, rolled-depth budget, new stacks and letters | Correct local/deep output placed before debit; fill/redig cannot repeat; first letter only once | Discovery/exploit/output defect |
| W20.release | Frontier, remaining dL, owned cells, temp layers, spill/loss and continuation | Ledger closes; ownership honored; recession restores layers; saved continuation matches | Flood conservation/ownership defect |
| W21.glass | Actual configured release front and permanent terrain | Only eligible paid outer-front cells become glass; ineligible/engine-owned controls stay unchanged | Cooling contract broken or unreachable |
| C01.source | Active flag, rate/carry, blocked room and external input | Exact fractional rate; disabled source adds zero; blocked flow is not banked | Source sentinel/rate defect |
| C02.sink | Filter/rate/unlimited setting and exact removals | Only matching liquid removed within rate; disabled sink inert | Sink filter/rate defect |
| C03.holder | Channel/body held/capacity/need and add/take ledger | Converges to target without overshoot/free stock | Holder-unit/control defect |
| C04.timer | Hour/period/wrap/invert windows and linked states | Exact boundary truth table controls markers and gates | Schedule/link defect |
| C05.edge | Winning setter, corner modes and body-edge classification | Ruling and sink behavior match each automatic/sealed/drain case | Setter precedence defect |
| C06.current | Painted arrays, direction/lane and loose-item displacement | Saved painted-only current moves eligible item in declared direction | Painter integration defect |
| C07.thermostat | Wet room, target, energy and temperature series | Correct energy sign/rate; converges without overshoot; dry/OFF controls inert | Thermostat defect |
| C08.meter | Connected canal/body stock, sample ticks and saved daily net | Exact connected total and known daily change; history survives reload | Meter/history defect |
| M01.storage | Every tank capacity, liquid, overfull state and minified/reinstalled contents | Correct sizes; no mixing; overfull stock preserved; cargo contents unchanged | Storage/migration/transport defect |
| M02.modes | Modes/effective modes, hauling and stationary unequal Store stocks | All permission cases correct; connected Store stocks unchanged; positive mover control moves | Mode or vacuous-control defect |
| M03.settle | Plans, starting stocks, sent/received budgets, routes and rotations | Deterministic plans; no new-stock forwarding; per-tank caps; fair liquid/consumer service | Settlement/topology/fairness defect |
| M04.pump | Working state, source/tank/canal deltas, final partial stock and stamps | Real cadence moves exactly paid amount; final dL recoverable; off/flick/blocked controls stop | Pump loss/free extraction/gating defect |
| M05.world_ports | Intake/outflow routes, four sides, competing IDs, corner and outlet rotation | Tank-free transfer closes; one lower-ID hose per side; corner refused; cycle budget bounded | Routing/port/budget defect |
| M06.pump_sheet | Full canal, tank loss, sheet `inPump`, wet lip and loss totals | Tank loss equals canal gain plus accepted sheet; no unexplained destruction | Physical pump overflow defect |
| M07.dump_outlet | Dump debit, gravity rate, outlet kind/room, return/recovery/filth | Slow gravity works; powered pour faster; blocked move retains stock; all exits disclosed | Dump/outlet/drain defect |
| M08.drill | Saved survey/reserve, powered drill/bleed output, pending units and status | Exact reserve→pending→outlet balance; bleed works unpowered at authored rate; gates explain stops | Unproven/broken drill production |
| M09.salvage | Destroyed tank/drill/converter pre-stock and resulting world/reserve/items | Entire committed/pending quantity salvaged once; no silent loss or duplicate | Destruction salvage defect |
| M10.convert | Each conversion XML row, gates, input/output/fuel/budget | Real scheduled batches obey authored ratio/tier/sun/roof/fuel/power and output constraints | Conversion/configuration defect |
| M11.fairness | Blocked earlier recipe/reaction, later runnable inputs, budgets | Blocked candidate does not starve later runnable candidate; retained budget bounded | Recipe/input starvation |
| M12.react_bath | Two reactants/product/gas, refusal snapshots, bill work/completion | Atomic reactions; vent quantity correct; bath cannot work/finish unpaid; vanished supply stops job | Reaction/bath transaction defect |
| M13.adapter | Mode, external signature/storage, tank and carry/debt | Send/Take/Shut correct; combined scaled resource invariant holds through short accept/save | Adapter/fractional-boundary defect |
| M14.theft | Foreign tank debit, reachable player path, witnesses, letters and goodwill time | Only attributed witnessed theft catches; ownership label correct; charges track actual draining; stop halts charge | Theft attribution/accounting defect |
| M15.reserve | Shared consumer draws and potable floor, offered drinking job | Fair runnable service; industry cannot spend reserve; pawn can consume retained stock | Reserve or fairness defect |
| M16.sprinkler_pay | Next due tick, pump/master, required/available dL and debit | Two real scheduled paid pulses; short/no-pressure/OFF controls consume zero | Sprinkler cadence/payment defect |
| M17.sprinkler_grid | Covered/blocked/sealed/far cells, liquid/owner/expiry/spend/save | Only charged eligible cells wet; identity correct; harvest/expiry/starvation and reload correct | Coverage/wet-grid defect |
| M18.sprinkler_liquid | Dominant liquid, brine/tar control, injuries and fuel filth | Correct selection; brine skipped; thick liquid clogs without debit; effects ON/OFF differ | Filtering or harmful-spray defect |
| M19.integrations | Actual VFE counters/valve and glow-tank salt/fresh/brine crops | VFE scope/budget/reserve correct; salt crop paid/grows; controls do not; unavailable arm unmeasured | Optional integration defect |
| M20.swale | Fed-time accumulator, terrain ladder, dry/capped/dug controls | Normal cadence improves Sand→Soil→SoilRich only while eligible/fed | Forced-step-only false proof or swale defect |
| M21.heat_residue | Cooling patches, scald/steam, residue and tar filth lifetime | Saved heat expires correctly; only configured drains stain; cleaning/rain/persistence rules hold | Heat/residue lifecycle defect |
| T01.need | Eligible needs/provider, decay trace, dehydration and thoughts | One provider; controlled rates; ≈0.30/day baseline; recovery/stages/exemptions correct | Need/provider/rate defect |
| T02.choice | Available/reachable sources, need thresholds and chosen real jobs | Full use-class/ranking matrix; safe reachable alternative wins; routine unsafe source refused | Search/eligibility defect |
| T03.quality | Completed fresh/salt/toxic/slime ingestion, need/hediffs/memories | Authored volume/quality effects and desperation controls; no nutrition | Drinking outcome defect |
| T04.animals | Wild/tame/native/nonnative needs and terrain jobs | Correct animals actually drink; native exception does not leak to controls | Animal drinking defect |
| T05.container_cycle | Crafted empty→filled→ingested→dirty→washed counts and source stock | Real jobs finish; all containers and liquid accounted; paid placement failure preserves output | Container loop/job defect |
| T06.material_style | Recipe Stuff, capacity/refusals, HP fraction, style and stack tests | Every applicable material/style transformation preserves condition and correct refusal | Material/style/stack defect |
| T07.tank_faucet | Tank modes, pipe-only placement, drink/fill jobs and exact debit | Actual direct-tank/faucet jobs obey modes/materials; no rough faucet thought; no hauling cycle | Faucet/tank-job defect |
| T08.partial | Ten bucket drinks, three-drink remainder, pour and saved drawn units | 15 L supports ten drinks; three leave 105 dL; pour/save/stack behavior exact | Partial-container volume defect |
| T09.stock_care | Map/inventory target, batches, two-bottle packing and patient delivery | Exact target; bounded trips; retained map stock; eligible patient/prisoner actually hydrated | Stock/packing/care defect |
| T10.snow | Snow debit, bucket IDs/warm clocks, bill inputs/output Stuff | Paid collection; prefer liquid water; timed melt and blue-ice bill preserve material | Emergency-water defect |
| T11.donors | Hemogen gene/control and each available donor-item job | Correct gene/item volume and distilled thought; ineligible controls unchanged | Donor hydration defect |
| T12.brine_break | Mental state/job/wander, salt severity, relief and treatment | Proper eligibility, repeated behavior and recovery; quarter-step effects correct | Salt-break/poisoning defect |
| T13.caravan_dbh | Existing-world caravan inventory/needs and actual DBH configuration | Paid bottle/river-tile hydration and residue; DBH startup bridge gives correct amount/provider | Caravan/DBH defect or unavailable configuration |
| T14.bucket_fire | Home-area fire job, bucket replacement, fire IDs and puddle | Real fetch/throw extinguishes area, leaves empty and accounts liquid; wrong-liquid control refuses | Firefighting integration defect |
| T15.timers_cache | Reversion age, split/warm clocks, failed-search marks and same-ID reload | Authored hot/cold replacements; clocks preserved; stale failed search cannot block new valid drink | Timer/cache reset defect |
| P01.graphs | Derived masks, bands/components/widths, edge membership and costs | Complete actor-pair matrix agrees with independent grid expectations; invalidation observed | Cliff/pocket/stride/cost defect |
| P02.reach | Same-pair CanReach/A*, doors/walls/swim/deck views, churn and residuals | Agreement on positive and negative pairs; real rebuild witness; bounded throttling/logging | Combined reach/cache defect |
| P03.ladders | Real operation jobs, sides, raised state and single-order two-wall crossing | Raise from allowed sides; lower from above; both ladders permit full crossing; one-ladder control refuses | Ladder work/route defect |
| P04.parity_gear | Species/faction eligibility, wall facing/reach, gear and final grounded paths | Anatomical/faction matrix correct; real wall climb succeeds only on legal geometry | Parity/placement/gear defect |
| P05.rescue | Fetchable spare/material, blueprint/frame/built ladder, victim and bed | Autonomous rescue builds/installs usable access and carries named casualty to valid bed | Rescue-premise or completion defect |
| P06.prison | Held/room/prison flags, capture/care jobs, service position and alert | Correct size/depth/bed verdict; named pawn captured/cared for from lip; alert reflects actual access | Prison/lip-service defect |
| P07.falls | Grounded shove/deck-loss histories, injuries, spikes and guarded control | Exactly one descent; expected relative damage/spike hits; guarded involuntary move stops; saved history survives | Fall/rail/history defect |
| P08.covers | Placement/mimic, connected mass, rider/beneath sets, load and deconstruction | Correct tier collapse; whole cover removed before descent; beneath pawn stays hidden/excluded; lid walker unsunk | Cover/band lifecycle defect |
| P09.exposure | Pit/ground temperatures, ranges, resistance, two ideologies and memories | Correct thermal coupling; harmful exposure affects resistance; charity/trait control gates distress | Exposure/ideology defect |
| P10.raids | Real assault/sapper/breacher/siege jobs, carriers, trees, ladders, causeway and scars | Grounded alternatives progress; stable carrier subset; both-wall/colony ladders work; siege excluded; repair restores target | Raid strategy/supply/progress defect |
| P11.wall_ai | Gear allocation, selected climb/normal costs, budget and arrival | Eligible raid/worker chooses legal useful climb; planner budget/memo lifetime bounded | Wall-AI/planning defect |
| P12.combat | Same shooter/target bands, attack target, cover bars and hit reports | Legal floor shots; illegal cliff targets excluded; body/direction/wet/vanilla stacking exact | Cliff/trench-combat defect |
| P13.cast_blast | Actual casting occupancy/proximity, positive shots and paired blast damage | Climbable trench used; sheer cage avoided with encounter witness; no blast-cover benefit | Cast-choice or blast-control defect |
| P14.swim_routes | Human/animal/mech profiles, actual path cells, load/tow and toggles | Swimmer crosses natural/dug reservoir; nonswimmer detours/refuses; no unsafe item/pod placement | Swim path/profile defect |
| P15.drown | Fatigue/recovery, head-up/posture/depth/exit/band, warning and health | Warning while alive; shore job offered; recovery works; shallow toggle and cover/grate gates apply | Drowning/fatigue/outer-gate defect |
| P16.wet_cost | Same shooter/stat with wet/dry and setting controls | Wet aim ratio 0.85, dry ratio 1; wet comfort +6; ranged restriction follows swimming | Wet combat/stat patch defect |
| P17.contact | Slips/stuns/climb slips, toxin, injury and apparel/item HP | Natural/dug rules and OFF controls differ; zero-HP apparel destroyed; dose follows fill/resistance | Contact/slip/corrosion defect |
| B01.build | Real drags/blueprints/frames/support order, tiers, affordances and refusals | Legal spans build from supports; invalid width/length/unsupported building/dig/vanilla bridge refuses | Construction/guard defect |
| B02.collapse | Load/rating/sag, own-faction rule, switch and ordered support-loss ticks | Correct whole collapse or protected outcome; sequential swing persists through save | Load/support/collapse defect |
| B03.rails | Orders/plans/stuff, cancellation and repeated open-edge trials | Valid stuff; cancelled rails stay cancelled; positive unrailed falls, zero railed falls | Material/order/protection defect |
| B04.underpass | Actual pawn band/path node at under-deck cell, item location and shots | Floor/deck walkers complete; insufficient clearance refuses; items and solid/grate shots correct | False horizontal-only underpass proof |
| B05.grate | Same lit/liquid/slime conditions, rider burns/toxin/slips and drained dL | Grate passes configured harm/500 dL drainage; solid control differs; ordinary item stays | Grate integration defect |
| B06.waters | Existing river/lake/sea paths, tower spans, current flags and scheduled HP | Path actually uses decks; exemptions hold; real awash cadence harms timber, not steel | Natural-water/weathering defect |
| B07.jetty | Two/three-cell placement, root/rating/load and remaining decks | Two legal, three refused; correct rails/rating; overload/root loss removes whole jetty | Jetty limit/collapse defect |
| B08.drive | Leaf geometry/progress, worker arrival/work, power and bank-side jobs | Timber advances only with labor; steel freezes without power/resumes; allowed sides correct | Motion/drive/work-order defect |
| B09.lock | Free/trapped hostile count, hold flag, peace target and gate verdict | Only qualifying hostiles lock; peace lowers unless held; gate follows leaf/threat state | Lock/gate defect |
| B10.tip | Ordered riders, per-leaf banks, floor pawn, loose stacks and falls | Correct hinge landing; overflow falls; items conserved; underpass pawn unchanged | Rider/item/band tipping defect |
| B11.paths_lines | Before/after paths, lamp nets, cord cut, hose endpoint/routes | Raise removes deck and disconnects both line types; lower reconnects and repaths | Endpoint fallback/disconnect defect |
| B12.winch_raid | Winch despawn/destroy, crash/injury, raid job, interrupted plank ledger | Winch crash once; eligible raider response; retry commits exactly one crossing | Winch/raid/plank transaction defect |
| B13.reload | Midraise progress, target/tip version, rider and continuation | Restored progress within tolerance; no repeated tip; future motion matches twin | Drawbridge persistence defect |
| H01.orders | Queued/forced/drafted/autonomous jobs, reservations and gizmos | Correct order semantics; autonomous worker succeeds without forced fallback; instant commands dev-only | Handling/order/work-selection defect |
| H02.trail | Actual carrier path, trail, pulled length, backtrack and stretch state | Trail follows walked route; backtrack gathers; cap causes coherent drop | Trail/length defect |
| H03.resume_save | Interrupt/drop/order fields and carrying/dropped reload snapshots | Named worker resumes retained order and reaches target; legitimate dropped state preserved | Resume/save defect |
| H04.wind | Real retract job, wound distance, clipped draw length and end state | Retracting observed; monotone shortening; interrupt coherent; final Stored/order clear | Winding/retraction defect |
| H05.route_cache | Install refusals/lengths/expansions, same-tick wall/ground edit and hashes | Bounded valid route; edit changes correct corridor; detour or one retract; disabled hoses preserved | Route/cache invalidation defect |
| H06.bands | Sampled route bands and structural joins before/after ladder raising | Only legal ramp/ladder/floor joins; cover/sheer refused; raising ladder retains hanging hose | Depth-route defect |
| H07.endpoints | Ports/relay chain/loop, free-end roles/factions and event arguments | Deterministic contacts; directional live chain; loops/corners refused; roles and callbacks correct | Endpoint/topology/event defect |
| H08.contents | Real route credit, lease/provider, tank/world/held amounts and stop | Credits match committed moves; hose fill/flush paid; dropped end transfers zero; stop drains with ledger | Phantom flow or held-volume defect |
| H09.appearance_state | Transition times/blends/widths, tint candidates and content switches | No cadence flicker; correct swelling/drain dwell; tint switches only after sustained candidacy | Flow-state/tint defect |
| H10.styles | Actual blueprint/frame/build/copy/reinstall and raw/effective style | All four looks survive lifecycle; null legacy remains null; facing/art resources resolve | Hose style lifecycle defect |
| H11.joints | Draw-populated collar boxes, endpoints, splice geometry, crossing and rig samples | All measurements present; within independent tolerances; no wall/rig collision; actual splice connectivity disclosed | Geometry defect or unread false pass |
| H12.draw_cache | Prefix/hand/ghost meshes, far mode, warm build counts and cleanup | Correct endpoints; settled poses reused; ghosts expire; deregistration/map removal releases resources | Drawing/lifetime defect |
| G01.links | Power/pipe profiles, manual/auto/selected links, degrees and refusals | Independent kinds/switches; reciprocal valid forest; exact range/owner/roof/cap controls | Aerial linking/profile defect |
| G02.nets | Actual registered nets, lamp load, watchdog, kill/dismantle/roof/claim | Correct power split/rejoin; survivor reseed; watchdog only needed when broken; coiling/fallen outcomes correct | Power/removal/ownership defect |
| G03.damage | HP, cut point, fallen aim, kinetic pose/time and mesh | Ordinary blast damages/cuts at correct point; kinetic changes pose without HP/cut; swing decays | Blast/sway defect |
| G04.fallen | Ground contacts, liveness, shock/recovery, own-cut worker, alert and real repair | Only live grounded contact shocks; settings/repair exemption correct; repair job rejoins and clears alert | Fallen-wire/shock/repair defect |
| G05.tap | Distinct nets, victim/player watts/energy, shared debt, clamp pose, witnesses/day/stop | Paid equals credited; surplus cap; own connection; one catch/faction; actual-time goodwill; stop halts | Tap/isolation/theft defect |
| G06.styles | Anchor/conduit/lamp/switch lifecycle, merge/split/restyle, pending save and materials | Largest/oldest winner; overrides/legacy preserved; multilink and immediate-save equal controls | Run/style/persistence defect |
| G07.graph | Independent nodes/edges/nets, leads/stubs/rings/piles/dives/busy cells | Exact expected topology; no cross-net/phantom ends; correct device homes and obstacle routes | Cord graph/attachment defect |
| G08.rebuild | Cached/fresh complete edge sets, hashes and local/offscreen/tree edits | No different/missing/**extra** geometry; affected update witnessed; unrelated pieces reused | Invalidation/determinism defect |
| G09.motion | Endpoint power poll, CPU/shader/roof modes, ripple/whip/bursts and spark counts | Correct liveness transitions; pinned motion; expected OFF controls; shared visible spark cap | Motion/effect/poll defect |
| G10.render | Draw ownership per strand, bounds, selection, near/far/shader state | Exactly one valid render path; section edge visible; exact selected net; no duplicate LOD/shader | Missing/double drawing |
| G11.reload | Full floor-cord/aerial/style snapshots, save classes and session cleanup | Actual before/after comparison includes cords and fallen spans; complete continuation; reset clears state | Save omission or session leak |
| R01.current | Grid, size/surge cadence, actual pawn/item steps, hazards/exemptions/costs | Eligible things move; grounded controls exempt; cost toggle reversible; native/flying flags read without flights | Current/profile/hazard defect |
| R02.flotsam | Entry/exit positions, weighted row, IDs/counts and registered callbacks | Correct upstream arrival/downstream-only exit; no ordinary-item destruction; hooks invoked correctly | Flotsam/extension defect |
| R03.weir | Placement/ghost rotation, run/head/gap and pool lane counts | Bank anchored/cross-current; joined wall pools; gap drains; invalid dry/wet-only placements refuse | Placement/join/pool defect |
| R04.catch | Floating IDs/units, normal wear/repair, breach/no-room stock and cascade ticks | Captures existing goods only; normal wear/rearm works; wash conserves; downstream order/upstream spared | Free output/lost catch/schedule defect |
| R05.bankworks | Stake flood pair, silt deadline/original terrain, ferry/ford path and current | Gaps leak; timed silt reverts; saved pair and actual rope/ford crossing safe | Bank-work integration defect |
| R06.placer | Geology pool, shared reserve, normal daily wash, actual panning XP/output and real flood edge | Paid outputs in pool; stock shared; timing/XP correct; flood replenishes exactly as configured | Placer timing/payment/refill defect |
| R07.taken | Named colonist/animal/prisoner/slave identity, world hold, return cell/guard, letters and old records | Same identities/gear return; captives secure after 600 ticks; losses/signals correct; legacy queue drains | World-pawn lifecycle defect |
| S01.ingress | Physical pump/rain/fill/release/gravity source deltas and five ingress counters | Each real caller books exactly accepted dL; refused remainder stays/discloses; no Offer-only substitution | Overflow caller/debit defect |
| S02.flow_caps | Preview hash/commit, shuffled offers, barriers/doors, caps and resting surfaces | Preview read-only/equal; order-independent; bounded extent; lowered cap preserves water; leakage below gap control | Sheet admission/flux/topology defect |
| S03.return_effects | Exact cut/pond credits, losses/remainders, irrigation, crop timers, pawn effects and ordinary fire | Ledger closes; paid return; per-fluid losses; early/live and delayed/dead crop controls; wet/toxin/path/douse correct | Sheet integration/effect defect |
| S04.freeze | Ice tiers, volume/loss/crop clocks, iced acceptance and thaw | Frozen stock unchanged; effects paused; inadmissible offer refused; thaw resumes correctly | Sheet freeze/thaw defect |
| S05.fire | Canal/sheet boundary ignition, pending fronts, exact burn, heat and blast schedule | Correct cross-boundary fire; nonfuel preserved; per-tick budgets and total consumption close | Sheet/channel fire defect |
| S06.persistence | Full component/palette/fire snapshot, twin continuation, OFF and Dry All ledger | Immediate/future equality; OFF drains without new input/purge; explicit purge disclosed | Sheet lifecycle/accounting defect |
| V01.water | Actual materials/layers/keys, 11→7.5→4 m drawdown and matched terrain | Tint 2→1→0 without terrain replacement; band follows gap; visibility independent of strength | Water-look state/redraw defect |
| V02.pit | DrawPos/sink/lip meshes/shadows, wall materials and firing-window origin | Correct depth/tween/clipping; lid walker unsunk; firing uses unsunk origin; scorch saves/fades | Pit rendering-state defect |
| V03.liquid | Owned materials/toggles, overlay mesh, wakes/bubbles/steam and heat sample cursor | No leaked copies; authored effects/biome gates; fair late-cell heat and prompt drain invalidation | Material/effect/heat-cache defect |
| V04.fittings_art | Loaded style/path/atlas/facing/cable and measured joint resources | Every required resource valid; current fixture matches installed art; geometry complete | Missing/misaligned/stale art contract |
| V05.electrical_art | Span/bracket/drop/clamp/material/shadow/queue/motion resources | Per-look/facing selections and layering correct; positive printed/dynamic witnesses | Electrical art-selection defect |
| V06.artifacts | Capture state stamp, frame/crop index, pixel checks, captions and retained answers | Every required view/crop exists and matches its measured state; faults rejected; decisions preserved | Untrustworthy review evidence |
| X01.flow_perf | Large live network size, actual pulses/far fill, timings and allocation | Required workload really runs; far cells fill; declared budgets met; no zero-work pass | Large-network regression |
| X02.level_perf | Real rig/link count, moves, conservation, timing/heap/GC/watchdog | Rehearsal/full required population reached; measured moves; no loss; finishes within budget | Levelling scale/performance failure |
| X03.cleanup_soak | Idle station snapshots, repeated edits/settings/map removals and resource counts | Expected stable state; unrelated pawns/plots preserved; bounded warm allocations/mesh counts | Cross-plot mutation or lifecycle leak |
| X04.player | Whitelisted actions, mission/journal IDs, destination stock, prisoner duration and crossing injuries | All three real missions meet exact goals within limits; reload journal complete | Player-flow/mission/report defect |

**Important limits on these rows**

- `00.worldgen` and `00.flight` are constraint guards, not substitutes for successful generation or flight outcomes.
- `B06.waters` uses only river/lake/sea terrain already available on an existing map or deliberately staged terrain on that map. Staged sea terrain does not establish naturally generated sea-map behavior.
- `X02.level_perf` can use N1 for rehearsal. The existing full 200-rig/325×325 workload needs an **already existing** suitable map. It remains a separate scale execution, not another ordinary feature station.
- Proposed rows requiring unavailable state fields need new read-only probes. Until implemented, they remain UNMEASURED.

### N coverage matrix

All station references below mean **N1**. Offline references retain the actual executable/model/art/harness assertions; they are not replaced by source presence alone.

| feature_id | station or offline test | row_id(s) |
|---|---|---|
| package_requirements | O1; N1 | 00.identity |
| assembly_wiring | O1 | csproj/source membership |
| flowworks_def_bindings | N1 | 00.registry |
| fluid_registry | O1; N1 | 00.registry |
| liquid_terrain_suite_generation | O1 | generator synchronization |
| liquid_terrain_mod_compat | O1; N1 | 00.registry |
| natural_liquid_identity | N1 | 00.registry, W08.fronts |
| world_liquid_tags | O1; N1 | 00.registry, 00.worldgen |
| typed_liquid_shores | O1; N1 | 00.worldgen |
| industrial_ruin_scatter | O1/O2; N1 | 00.worldgen |
| liquid_works_ruin_stock | N1 | 00.registry, M10.convert; generation excluded |
| industrial_ruin_restoration | N1 | M10.convert |
| water_not_food | O1; N1 | T03.quality |
| lava_liquid_faces | O1 | selftest_lava_row |
| lava_pumping_ruin_exclusion | O1 | selftest_lava_row |
| astrofuel_liquid_adoption | O1; N1 | 00.registry |
| recreational_swim_eligibility | O1/O2; N1 | P14.swim_routes |
| deep_sand_fishing | O1; N1 | 00.registry, W14.trackers |
| flowworks_localized_feedback | O1; N1 | 00.registry, 00.settings_ui |
| review_station_signs | N1 | 00.fixture, V06.artifacts |
| settings_ui | N1 | 00.settings_ui |
| settings_persistence | O1/O2/O4; N1 | 00.settings_save |
| settings_search | O7; N1 | 00.settings_ui |
| settings_reset | O2/O4/O7; N1 | 00.settings_ui, 00.settings_save |
| settings_runtime_rebuilds | N1 | 00.settings_save, X03.cleanup_soak |
| depth_engine_reload_latch | O2; N1 | 00.settings_save |
| fluid_input_filter | N1 | W16.rain_edges |
| typed_settings_registry | O1/O7 | selftest_settings_registry |
| settings_all_off | O1/O7; N1 | 00.settings_save, W01.dig |
| settings_fingerprint | O2/O4 | SettingsPrint/fingerprint checks |
| settings_cached_rows | O2 | SettingsResetChecks |
| liquid_look_tuning_export | O1/O7; N1 | V03.liquid |
| canal_dig_single_cut | N1 | W01.dig |
| canal_dig_to_depth | O2; N1 | W02.depth |
| machine_digger_classification | O2; N1 | W02.depth |
| dig_depth_caps | O2; N1 | W02.depth |
| deep_dig_work_cost | O2; N1 | W02.depth |
| deep_dig_wait_alert | N1 | W02.depth |
| canal_fill_work | N1 | W03.fill |
| dig_fill_orders | O2; N1 | W01.dig, W03.fill |
| excavation_fill_displacement | O2/O5; N1 | W03.fill, S01.ingress |
| excavation_terrain_restore | N1 | W03.fill, W04.repair |
| legacy_fill_ground_restore | N1 | W04.repair |
| excavation_save_repair | O2; N1 | W04.repair |
| liquid_identity_palette | O2; N1 | W05.palette |
| excavation_depth_fill_storage | O2; N1 | W04.repair, W06.exact |
| liquid_pulse_adapter | N1 | W07.whole, W08.fronts |
| excavation_rain_fill | O2/O5; N1 | W16.rain_edges |
| map_edge_modes | O2; N1 | W16.rain_edges, C05.edge |
| liquid_conservation_ledger | O2/O5; N1 | W03.fill, M04.pump, S06.persistence |
| driver_flow_seeds | O2; N1 | W17.pressure |
| channel_flow_order | O2 | Program, SequenceFuzz, FlowKernelFuzz |
| whole_notch_channel_flow | O2/O5; N1 | W07.whole |
| exact_channel_pond_flow | O2/O5; N1 | W06.exact |
| flow_partition_rotation | O2; N1 | W17.pressure, X01.flow_perf |
| liquid_body_discovery | O2; N1 | W09.sources |
| liquid_source_liveness | O2; N1 | W09.sources |
| source_mouth_pacing | O2/O5; N1 | W08.fronts |
| scarce_source_priority | O2 | FlowKernelFuzz |
| natural_body_classification | O2; N1 | W09.sources |
| natural_body_stock_ledger | O2; N1 | W09.sources, M04.pump |
| pond_floor_capacity | O2; N1 | W11.large_lake, W12.beds |
| pond_volume_migration | O2; N1 | W04.repair |
| pond_groundwater_refill | O2; N1 | W13.refill |
| pond_recession_topology | O2; N1 | W10.partial, W11.large_lake |
| pond_fullcell_recession | O2; N1 | W11.large_lake |
| pond_refill_occupants | O2; N1 | W13.refill |
| pond_depth_surface | O2; N1 | W10.partial |
| pond_mud_lakebed | O2; N1 | W10.partial, W11.large_lake |
| pond_depth_model_toggle | N1 | W10.partial |
| pond_bed_detach_reattach | O2; N1 | W12.beds |
| pond_dry_bed_hollows | O2; N1 | W12.beds |
| lake_floor_generation | O2/O8; N1 | W11.large_lake |
| lake_floor_exit_and_basin | O2 | DeepBedChecks, LakeFloorChecks |
| lake_floor_initialization_save | O2; N1 | W11.large_lake, W18.reload |
| large_lake_live | N1 | W11.large_lake |
| liquid_depth_readout | O2; N1 | W06.exact, V01.water |
| liquid_surface_gap_diagnostic | O2/O5; N1 | W06.exact |
| water_depth_ladder | O1/O2; N1 | W10.partial, V01.water |
| fluid_identity_viscosity | O2/O5; N1 | W08.fronts |
| water_save_load_state | N1 | W18.reload |
| pond_freeze_thaw | N1 | W15.ice |
| fish_growth_rolls | O2; N1 | W14.trackers |
| fish_refill_memory | O2; N1 | W14.trackers |
| fishing_zone_refill | O2; N1 | W14.trackers |
| water_body_split | O2/O5; N1 | W14.trackers |
| water_body_freeze_recount | N1 | W15.ice |
| water_body_type_flip | O2; N1 | W15.ice |
| water_plant_grace | O2; N1 | W14.trackers |
| dug_pond_fishing | N1 | W14.trackers |
| dig_discovery_exploit_guard | O2; N1 | W19.finds |
| local_dig_ore_finds | O2; N1 | W19.finds |
| dig_rock_and_deep_stone | O2; N1 | W19.finds |
| dig_discovery_letters | N1 | W19.finds |
| flood_release_conservation | O2; N1 | W20.release |
| flood_release_determinism | O2; N1 | W20.release |
| flood_terrain_recession | N1 | W20.release |
| flood_engine_ownership | O2; N1 | W20.release |
| tar_front_glass | O1/O2; N1 | W21.glass |
| pond_flood_preservation | N1 | W20.release |
| subsurface_survey | N1 | M08.drill |
| liquid_drilling | N1 | M08.drill |
| drill_placement_status | O2; N1 | M08.drill |
| drill_pending_salvage | O2; N1 | M09.salvage |
| tank_storage_capacity | O2; N1 | M01.storage |
| tank_modes | O2; N1 | M02.modes |
| tank_network_settle | O2; N1 | M03.settle |
| liquid_store_planning | O2 | PlanChecks |
| tank_gravity_dump | O2; N1 | M07.dump_outlet |
| tank_destruction_salvage | O2; N1 | M09.salvage |
| cargo_tank_transport | N1 | M01.storage |
| pump_draw_pour | O2; N1 | M04.pump |
| pump_world_transfer | O2; N1 | M05.world_ports |
| pump_overflow_sheet | N1 | M06.pump_sheet |
| pump_status_warnings | N1 | M04.pump |
| pump_footprint_reach | O2; N1 | M04.pump, M05.world_ports |
| pump_hose_side_ports | O2; N1 | M05.world_ports |
| liquid_transfer_atomicity | O2; N1 | M03.settle, M04.pump, M12.react_bath |
| compound_liquid_transfer | O2 | TransferChecks All/Split |
| ve_boundary_fractional_carry | O2; N1 | M13.adapter |
| pipe_network_adapter | O2; N1 | M13.adapter |
| liquid_network_topology | O2; N1 | M03.settle, H07.endpoints |
| liquid_net_topology_cache | O2; N1 | H05.route_cache, G02.nets |
| liquid_consumer_fairness | O2; N1 | M03.settle, M11.fairness |
| passive_liquid_levelling | O2; N1 | M07.dump_outlet, X02.level_perf |
| liquid_outlet_routing | O2; N1 | M07.dump_outlet |
| hose_drain_conservation | O2; N1 | M07.dump_outlet, H08.contents |
| faction_liquid_theft | O2; N1 | M14.theft |
| liquid_conversion_machines | O1/O2; N1 | M10.convert |
| converter_scheduling | O2; N1 | M11.fairness |
| converter_output_salvage | O2; N1 | M09.salvage, M10.convert |
| liquid_reactions | O2; N1 | M12.react_bath |
| reactor_scheduling | O2; N1 | M11.fairness |
| liquid_bath_recipes | O2; N1 | M12.react_bath |
| hot_release_effects | O2; N1 | M21.heat_residue |
| drained_liquid_residue | O1/O2; N1 | M21.heat_residue |
| sprinkler_pipe_placement_style | O1/O2; N1 | M16.sprinkler_pay, V04.fittings_art |
| sprinkler_pressure_liquid_selection | O2; N1 | M16.sprinkler_pay, M18.sprinkler_liquid |
| sprinkler_hourly_atomic_draw | O2; N1 | M16.sprinkler_pay |
| sprinkler_coverage | O2; N1 | M17.sprinkler_grid |
| sprinkler_wet_registry | O2; N1 | M17.sprinkler_grid |
| sprinkler_nonwater_effects | O2; N1 | M18.sprinkler_liquid |
| sprinkler_visual_status | N1 | M16.sprinkler_pay, M17.sprinkler_grid |
| vfe_sprinkler_adapter | O1/O2; N1 | M19.integrations |
| swale_fed_fertility_ladder | O2; N1 | M20.swale |
| glow_tank_salt_feed | N1 | M19.integrations |
| container_material_crafting | O1/O2; N1 | T06.material_style |
| container_condition_preservation | O2; N1 | T06.material_style |
| container_four_styles | O2/O6; N1 | T06.material_style |
| container_fill_terrain | N1 | T05.container_cycle |
| container_washing | N1 | T05.container_cycle |
| container_ingestion_residue | O2; N1 | T05.container_cycle, T13.caravan_dbh |
| container_tank_transfer | O2; N1 | T07.tank_faucet, T08.partial |
| bottled_liquid_reversion | O1/O2; N1 | T15.timers_cache |
| bucket_firefighting | O1/O2; N1 | T14.bucket_fire |
| paid_output_placement | O2; N1 | T05.container_cycle, M09.salvage |
| thirst_provider_selection | O2; N1 | T01.need, T13.caravan_dbh |
| thirst_decay | O2; N1 | T01.need |
| dehydration_progression | O2; N1 | T01.need |
| thirst_mood_categories | O1/O2; N1 | T01.need |
| drink_use_class_gate | O2; N1 | T02.choice |
| drink_source_selection | O2; N1 | T02.choice |
| animal_terrain_drinking | O2; N1 | T04.animals |
| bottle_hydration | O2; N1 | T03.quality |
| terrain_tank_drinking | N1 | T02.choice, T07.tank_faucet |
| drink_quality_effects | O2; N1 | T03.quality |
| awkward_drink_mood | O2; N1 | T03.quality, T07.tank_faucet |
| potable_drinking_reserve | O2; N1 | M15.reserve |
| salt_water_break | O1/O2; N1 | T12.brine_break |
| caravan_drinking | N1 | T13.caravan_dbh |
| dbh_bottle_bridge | O1/O2; N1 | T13.caravan_dbh |
| partial_container_drinks | O2; N1 | T08.partial |
| potable_bottle_stock_target | O2; N1 | T09.stock_care |
| personal_bottle_packing | N1 | T09.stock_care |
| patient_prisoner_water | O2; N1 | T09.stock_care |
| external_water_items | O1/O2; N1 | T11.donors |
| sanguophage_blood_hydration | O1/O2; N1 | T11.donors |
| snow_ice_gathering | O2; N1 | T10.snow |
| snow_bucket_melting | O2; N1 | T10.snow |
| ice_bucket_recipes | O1/O2; N1 | T10.snow |
| thirst_search_cache_reset | O2; N1 | T15.timers_cache |
| pipe_faucet_network_draw | O2; N1 | T07.tank_faucet |
| pipe_faucet_drinking | N1 | T07.tank_faucet |
| pipe_faucet_container_fill | N1 | T07.tank_faucet |
| pit_cliff_pathing | O2; N1 | P01.graphs |
| pit_pocket_connectivity | O2; N1 | P01.graphs |
| ladder_reach_routes | O2; N1 | P03.ladders |
| wall_depth_reachability | O2; N1 | P02.reach |
| reach_cache_diagnostics | O2; N1 | P02.reach |
| underpass_reach_views | O2; N1 | P02.reach, B04.underpass |
| trench_stride | O2; N1 | P01.graphs, 00.optional |
| pit_step_cost | O2; N1 | P01.graphs |
| creature_climb_bonus | O1/O2; N1 | P01.graphs |
| ladder_climber_eligibility | O2/O8; N1 | P04.parity_gear |
| ladder_shared_access | O2; N1 | P03.ladders, P04.parity_gear |
| ladder_hanging_and_reach | O2; N1 | P04.parity_gear |
| ladder_raise_lower | O2; N1 | P03.ladders |
| raider_ladder_supply | O2; N1 | P10.raids |
| ladder_wall_crossing | O2; N1 | P04.parity_gear |
| pit_breach_repair | O2; N1 | P10.raids |
| pit_safe_ability_arrivals | O2; N1 | 00.flight; nonflight predicates only |
| pit_rescue_ladder | O2; N1 | P05.rescue |
| pit_rooms | O2; N1 | P06.prison, P09.exposure |
| pit_warden_lip_service | O2; N1 | P06.prison |
| pit_capture_down | O2; N1 | P06.prison |
| pit_stuck_alert | O2; N1 | P06.prison |
| pit_capture_and_escape | O2; N1 | P01.graphs, P06.prison |
| pit_fall_damage | O2; N1 | P07.falls |
| pit_voluntary_jump | O2/O7; N1 | 00.flight; command/confirmation only |
| pit_spikes | O2; N1 | P07.falls |
| fall_guardrails | O2; N1 | P07.falls |
| pit_exposure | O2; N1 | P09.exposure |
| pit_exposure_charity_memory | N1 | P09.exposure |
| pit_cover_surface_mimic | O2; N1 | P08.covers |
| pit_cover_load_trigger | O2; N1 | P08.covers |
| pit_cover_damage_collapse | O2; N1 | P08.covers |
| pit_cover_beneath_pawns | O2; N1 | P08.covers |
| span_walking_surface | O2; N1 | P08.covers, B04.underpass |
| flow_door_pawn_access | O2; N1 | P06.prison |
| flow_door_liquid_sealing | O2; N1 | W08.fronts |
| flow_door_wet_construction | O2; N1 | B01.build |
| flow_door_orientation | O2; N1 | B01.build, V04.fittings_art |
| raider_trench_strategy | O2; N1 | P10.raids, 00.flight |
| raider_trench_ladders | O2; N1 | P10.raids |
| raider_trench_causeways | O2; N1 | P10.raids |
| raid_jump_pack_equipment | O1/O2; N1 | P10.raids, 00.flight |
| wall_climb_jobs | O2; N1 | P04.parity_gear |
| wall_climb_ai | O2; N1 | P11.wall_ai |
| raid_climbing_gear | O1/O2; N1 | P11.wall_ai |
| cliff_shooting_restriction | O2; N1 | P12.combat |
| trench_cover | O3; N1 | P12.combat |
| trench_ai_cage_avoidance | O2/O7; N1 | P13.cast_blast |
| trench_explosion_damage | N1 | P13.cast_blast |
| suspension_bridge_construction | O2; N1 | B01.build |
| suspension_building_affordances | O2; N1 | B01.build |
| suspension_load_collapse | O2; N1 | B02.collapse |
| suspension_support_loss | O2; N1 | B02.collapse |
| suspension_railings | O2; N1 | B03.rails |
| suspension_underpass_bands | O2; N1 | B04.underpass |
| suspension_underpass_shots | O2; N1 | B04.underpass |
| suspension_underpass_items | O2; N1 | B04.underpass |
| suspension_collapse_crush_wreck | O2; N1 | B02.collapse, B04.underpass |
| suspension_natural_water | O2; N1 | B06.waters |
| suspension_flood_damage | O2; N1 | B06.waters |
| suspension_jetty | O2; N1 | B07.jetty |
| suspension_styles | O2/O6; N1 | V04.fittings_art |
| drawbridge_leaf_geometry | O2; N1 | B08.drive |
| drawbridge_work_orders | O2; N1 | B08.drive |
| drawbridge_peace_lock | O2; N1 | B09.lock |
| drawbridge_tip_riders | O2; N1 | B10.tip |
| drawbridge_path_invalidation | O2; N1 | B11.paths_lines |
| drawbridge_winch_loss | O2; N1 | B12.winch_raid |
| drawbridge_raider_winch_attack | O2; N1 | B12.winch_raid |
| raid_plank_transaction | O2; N1 | B12.winch_raid |
| drawbridge_flexible_lines | O2; N1 | B11.paths_lines |
| drawbridge_save_state | O2; N1 | B13.reload |
| drawbridge_art_cables | O2/O6; N1 | V04.fittings_art |
| suspension_gravship_launch | O2/O4; N1 | 00.flight |
| grate_fire_and_splash | O2; N1 | B05.grate |
| grate_spill_drain | O2; N1 | B05.grate |
| deep_water_walkability | O2; N1 | P14.swim_routes |
| swim_ability_load | O2; N1 | P14.swim_routes |
| swim_exhaustion_recovery | O2; N1 | P15.drown |
| swim_warning_shore_escape | O2; N1 | P15.drown |
| natural_water_drowning | O2; N1 | P15.drown |
| pit_fill_drowning | O2; N1 | P15.drown |
| pit_fill_toxicity | O2; N1 | P17.contact, B05.grate |
| deep_water_item_drop_exclusions | N1 | P14.swim_routes |
| wet_aim_penalty | O2; N1 | P16.wet_cost |
| wet_cold_penalty | O2; N1 | P16.wet_cost |
| swimmer_ranged_restriction | O2; N1 | P16.wet_cost |
| slime_walking_slips | O2; N1 | P17.contact |
| liquid_contact_corrosion | O1/O2; N1 | P17.contact |
| hose_saved_state | O2; N1 | H03.resume_save, H08.contents |
| hose_save_component_skip | O2; N1 | 00.lifecycle |
| hose_legacy_aliases | O2; N1 | 00.lifecycle; separate removal load |
| hose_legacy_settings_import | O2 | HoseLegacy/GptFixes/Nan checks |
| hose_carry_state_rules | O2 | HoseCarryChecks, HoseFuzz |
| hose_deploy_move_orders | O2; N1 | H01.orders |
| hose_forced_pawn_orders | N1 | H01.orders |
| hose_order_work_selection | N1 | H01.orders |
| hose_walked_trail | O2; N1 | H02.trail |
| hose_interrupt_resume | O2; N1 | H03.resume_save |
| hose_manual_winding | O2; N1 | H04.wind |
| hose_route_install | O2; N1 | H05.route_cache |
| hose_shape_geometry | O2/O4; N1 | H09.appearance_state, H11.joints |
| hose_obstacle_reroute | O2; N1 | H05.route_cache |
| hose_world_snapshot_cache | O2; N1 | H05.route_cache |
| hose_depth_crossing | O2; N1 | H06.bands |
| hose_reel_port_detection | O2; N1 | H07.endpoints |
| hose_relay_chains | O2; N1 | H07.endpoints |
| hose_free_end_classification | O2; N1 | H07.endpoints |
| hose_free_end_roles | O2; N1 | H07.endpoints |
| hose_end_events | N1 | H07.endpoints |
| hose_flow_signal | O2; N1 | H08.contents |
| hose_flow_visual_state | O2; N1 | H09.appearance_state |
| hose_liquid_tint | O2; N1 | H09.appearance_state |
| hose_held_volume | O2; N1 | H08.contents |
| hose_reel_style_picker | O2/O6; N1 | H10.styles |
| hose_reel_facing_art | O2/O6; N1 | H10.styles, V04.fittings_art |
| hose_placement_preview | N1 | H10.styles, V04.fittings_art |
| hose_fittings_ports | O2/O6; N1 | H11.joints |
| hose_layering_crossings | O2; N1 | H11.joints |
| hose_over_building_draw | O2; N1 | H11.joints |
| hose_live_carry_draw | O2; N1 | H12.draw_cache |
| hose_retract_visuals | O2; N1 | H04.wind, H12.draw_cache |
| hose_splice_g2 | O2; N1 | H11.joints |
| hose_render_cache_lifetime | N1 | H12.draw_cache, X03.cleanup_soak |
| river_world_biome_colors | O1; N1 | V03.liquid |
| river_current_grid | O2; N1 | R01.current |
| river_current_advection | O2; N1 | R01.current |
| river_current_scaling_surges | O2; N1 | R01.current |
| river_current_crossing_hazards | O2; N1 | R01.current |
| river_current_exemptions | O2; N1 | R01.current, 00.flight |
| river_current_avoidance | O2; N1 | R01.current |
| river_extension_hooks | N1 | R02.flotsam |
| river_flotsam | O2; N1 | R02.flotsam |
| weir_bank_edge_placement | O2; N1 | R03.weir |
| weir_joined_wall | O2; N1 | R03.weir |
| weir_floating_catch | O2; N1 | R04.catch |
| weir_wear_repair | N1 | R04.catch |
| weir_breach_wash | O2; N1 | R04.catch |
| weir_stake_cascade | O2; N1 | R04.catch |
| weir_visuals_styles_foam | O2/O6; N1 | V04.fittings_art |
| stake_line_levee | O2; N1 | R05.bankworks |
| silt_trap_fertility | O2; N1 | R05.bankworks |
| ferry_rope_pairing | O2; N1 | R05.bankworks |
| river_ford_stones | O1/O2; N1 | R05.bankworks |
| placer_mineral_pool | O2; N1 | R06.placer |
| placer_shared_stock | O2; N1 | R06.placer |
| sluice_daily_yield | O2; N1 | R06.placer |
| panning_mining_work | O2; N1 | R06.placer |
| taken_by_land_hold_return | O2; N1 | R07.taken |
| taken_by_land_identity | O2; N1 | R07.taken |
| taken_by_land_signals | N1 | R07.taken |
| taken_by_land_prisoner_return | O2; N1 | R07.taken |
| taken_by_land_escape_capture | O2; N1 | R07.taken |
| swept_away_legacy_records | N1 | R07.taken |
| liquid_fire_trigger | O2; N1 | S05.fire |
| liquid_fire_ignition_and_front | O2; N1 | S05.fire |
| liquid_fire_consumption | O2; N1 | S05.fire |
| liquid_fire_dousing | O2; N1 | S05.fire |
| burning_liquid_pawn_effects | O2; N1 | S05.fire, B05.grate |
| chemfuel_inferno | O1/O2; N1 | S05.fire |
| astrofuel_detonation | O1/O2; N1 | S05.fire |
| fuel_fire_events | O2; N1 | S05.fire, 00.optional |
| liquid_room_heat | O2; N1 | V03.liquid |
| liquid_heat_sampling | O2; N1 | V03.liquid |
| liquid_surface_materials | O1; N1 | V03.liquid |
| liquid_surface_overlay | O1/O2; N1 | V03.liquid |
| liquid_wading_wakes | O1/O2; N1 | V03.liquid |
| liquid_bubbles | O1/O2; N1 | V03.liquid |
| river_steam | O1; N1 | V03.liquid |
| pit_wall_geometry | O2; N1 | V02.pit |
| pit_pawn_sink_geometry | O2; N1 | V02.pit |
| pit_lip_occlusion | O2; N1 | V02.pit |
| pit_scorch_appearance | O2; N1 | V02.pit |
| deep_water_tint | O2; N1 | V01.water |
| wet_wall_shadow_band | O2; N1 | V01.water |
| water_look_redraw | O2; N1 | V01.water |
| liquid_join_visuals | O2/O6; N1 | H11.joints, V04.fittings_art |
| aerial_line_kinds | O2/O4; N1 | G01.links |
| aerial_manual_linking | O4; N1 | G01.links |
| aerial_auto_link | O4; N1 | G01.links |
| aerial_selected_autolink | O4; N1 | G01.links |
| aerial_power_transmission | N1 | G02.nets |
| aerial_net_watchdog | O4; N1 | G02.nets |
| aerial_link_persistence | N1 | G11.reload |
| aerial_anchor_removal | O4; N1 | G02.nets |
| aerial_gravship_transport | O4; N1 | 00.flight |
| aerial_roof_cut | N1 | G02.nets |
| aerial_owner_change_cut | N1 | G02.nets |
| aerial_explosion_damage | O4; N1 | G03.damage |
| aerial_kinetic_sway | O4; N1 | G03.damage |
| aerial_span_geometry | O4/O6; N1 | V05.electrical_art |
| aerial_wind_sway | O4; N1 | G09.motion |
| aerial_span_shadows | O4; N1 | V05.electrical_art |
| aerial_fallen_geometry | O4; N1 | G03.damage, V05.electrical_art |
| aerial_fallen_liveness | N1 | G04.fallen |
| aerial_wall_bracket_mount | O4/O6; N1 | V05.electrical_art |
| aerial_restring_job | O4; N1 | G04.fallen |
| aerial_wire_down_alert | N1 | G04.fallen |
| fallen_wire_shock | O4; N1 | G04.fallen |
| external_live_wire_contacts | O2/O4; N1 | G04.fallen, B11.paths_lines |
| fallen_wire_ignition | N1 | G04.fallen, S05.fire |
| power_tap_transfer | O4; N1 | G05.tap |
| power_tap_faction_isolation | O4; N1 | G05.tap |
| power_theft_consequences | O4; N1 | G05.tap |
| power_tap_visuals | O4/O6; N1 | G05.tap, V05.electrical_art |
| aerial_anchor_styles | O4/O6; N1 | G06.styles |
| aerial_lamp_mast | O1; N1 | G06.styles |
| conduit_run_styles | O4; N1 | G06.styles |
| conduit_legacy_styles | O4; N1 | G06.styles |
| conduit_pending_save_resolution | O4; N1 | G06.styles, G11.reload |
| conduit_lamp_styles | O4; N1 | G06.styles |
| conduit_switch_art | O4/O6; N1 | G06.styles, V05.electrical_art |
| conduit_style_materials | O4/O6; N1 | G06.styles, V05.electrical_art |
| conduit_target_selection | O4; N1 | G07.graph |
| machine_hookup_rendering | O4; N1 | G07.graph, G10.render |
| cord_world_snapshot | O4; N1 | G07.graph, G08.rebuild |
| cord_machine_connections | O4; N1 | G07.graph |
| cord_graph_reduction | O4/O5; N1 | G07.graph |
| cord_path_planning | O4/O5; N1 | G07.graph |
| cord_slack_shapes | O4; N1 | G07.graph |
| cord_connected_piles | O4/O6; N1 | G07.graph |
| cord_live_dead_ends | O4; N1 | G07.graph, G09.motion |
| cord_motion_effects | O4; N1 | G09.motion |
| cord_static_rendering | N1 | G10.render |
| cord_selection_highlight | N1 | G10.render |
| cord_lod | N1 | G10.render |
| cord_gravship_render_guard | O4/O7; N1 | 00.flight, G10.render idle arm |
| cord_rebuild_invalidation | O4; N1 | G08.rebuild |
| cord_geometry_determinism | O4/O5; N1 | G08.rebuild, G11.reload |
| cord_runtime_save_compat | O4; N1 | 00.lifecycle; separate removal load |
| gss_session_reset | O4; N1 | 00.lifecycle, G11.reload |
| legacy_name_migration | O4 | LegacyNameChecks, GptReadFixChecks |
| flexible_line_draw_order | O2/O4; N1 | V04.fittings_art, V05.electrical_art |
| line_crossing_placement | O2; N1 | B01.build, B11.paths_lines |
| line_dig_breakage | O2; N1 | W01.dig, B11.paths_lines |
| deck_collapse_lines | O2; N1 | B02.collapse, G04.fallen |
| pipe_pole_network_integration | O2/O4; N1 | G01.links, H07.endpoints |
| line_crossing_readouts | O2; N1 | B11.paths_lines, H07.endpoints |
| map_control_lifecycle | O2; N1 | 00.fixture, C01.source–C08.meter |
| flow_source_input | O2; N1 | C01.source |
| flow_sink_drain | O2; N1 | C02.sink |
| liquid_level_holder | O2; N1 | C03.holder |
| timed_map_controls | O2; N1 | C04.timer |
| painted_water_current | O2; N1 | C06.current |
| liquid_thermostat | O2; N1 | C07.thermostat |
| flow_meter_history | O2 wiring; N1 | C08.meter |
| sheet_physical_ingress | O2; N1 | S01.ingress |
| sheet_topology_fluid_rules | O2; N1 | S02.flow_caps |
| sheet_spill_backpressure | O2; N1 | S02.flow_caps |
| sheet_conservative_flow | O2; N1 | S02.flow_caps |
| sheet_door_leakage | O2; N1 | S02.flow_caps |
| sheet_receiver_return | O2; N1 | S03.return_effects |
| sheet_losses_irrigation | O2; N1 | S03.return_effects |
| sheet_crop_damage | O2; N1 | S03.return_effects |
| sheet_freeze_thaw | O2; N1 | S04.freeze |
| sheet_pawn_effects | O2 source; N1 | S03.return_effects |
| sheet_fire_extinguishing | O2; N1 | S03.return_effects |
| sheet_liquid_fire | O2; N1 | S05.fire |
| sheet_fuel_detonation | O2; N1 | S05.fire |
| sheet_overlay_readout | N1 | S02.flow_caps, S04.freeze |
| sheet_persistence_ledger | O2; N1 | S06.persistence |
| sheet_switch_off_draining | N1 | S06.persistence |
| debug_excavation_ledger | N1 | 00.probes_debug |
| debug_tank_contents | O2; N1 | 00.probes_debug |
| debug_subsurface_yield | N1 | 00.probes_debug |
| proof_probe_contracts | O7; N1 | 00.probes_debug |
| harmony_patch_isolation | O1/O7; N1 | 00.registry, 00.lifecycle |
| validation_provenance | O7; N1 | 00.identity |
| validation_preflight | O7; N1 | 00.fixture, 00.logs |
| validation_site_fixtures | O7; N1 | 00.fixture |
| validation_setting_isolation | O7; N1 | 00.settings_save, X03.cleanup_soak |
| validation_manifest_catalog | O7 | manifest/report exact-set tests |
| proof_verdict_integrity | O7 | fault/missing/stale/mock/exit mutants |
| validation_session_orchestration | O7; N1 | 00.logs, 00.report, X03.cleanup_soak |
| offline_game_transport | O7 | strict fake/schema/fault tests |
| selftest_runner | O2/O4/O7 | dispatch/count/exit tests |
| source_wiring_guards | O1/O2/O4/O7 | scoped source/XML mutants |
| sequence_fuzz_replay | O2/O4 | SequenceFuzz, HoseFuzz, GssFuzz |
| kernel_oracle_protocol | O2/O4/O5 | exact-water/body/graph differential |
| validation_matrix_coverage | O5 | matrix prove/reduced/det_export/selftest |
| geometry_art_audits | O2/O4/O6; N1 | H11.joints, V04.fittings_art |
| performance_budgets | O2/O4; N1 | X01.flow_perf, X02.level_perf, X03.cleanup_soak |
| runtime_cache_lifecycle | O2/O4; N1 | 00.lifecycle, X03.cleanup_soak |
| review_evidence_status | O7/O8 | human-review evidence/decision tests |
| review_map_layout | O7; N1 | 00.fixture, V06.artifacts |
| scenario_composite_staging | O7; N1 | 00.fixture, X03.cleanup_soak |
| visual_review_artifacts | O7; N1 | V06.artifacts |
| validation_image_evidence | O5/O6/O7 | contact-sheet/image negative controls |
| playtest_journal_resume | O7; N1 | X04.player |
| player_mission_limits | O7; N1 | X04.player |
| canal_defense_mission | O7; N1 | X04.player |
| pit_prisoner_hold_mission | O7; N1 | X04.player |
| pump_crossing_mission | O7; N1 | X04.player |
| review_art_manifest | O6/O8 | gss_art_manifest/art inventory |
| cord_unroutable_diagnostics | O4/O8 | UnroutableCensus and renderer |
| lake_floor_preview | O2/O8 | LakeFloorChecks.Preview and lake_floor_preview |

### N replaces

Paths below are relative to the named mod. A wildcard maps **every existing matching file**, preserving its distinct assertions. Retirement is conditional on the replacement manifest demonstrating equal or stronger coverage; nothing is deleted under this plan.

| existing script/test | station(s)/offline test that replace it |
|---|---|
| FlowWorks `Source/SelfTest/*.cs`, `Source/SelfTest/VV/*` | O2; keep specialized suites, seeds, mutants and nonempty-family checks |
| FlowWorks `Source/SelfTestTrench/*` | O3 |
| GSS `Source/SelfTest/*` | O4 |
| FlowWorks `Tools/selftest_*.py`, generator-sync checks | O1/O6 |
| FlowWorks `Tools/ladder_climber_census.py`, `lake_floor_preview.py` | O8 |
| FlowWorks `northstar/selftest_*.py`, `fakegame.py`, `*_fake.py`, `water_scenes_mock.py`, `scenarios/mock_bridge.py` | O7; model portions also O5 |
| FlowWorks `Source/SelfTest/selftest_flowworks_kernel_oracle.py` | O5, driving retained O2 oracle mode |
| GSS `northstar/selftest_*.py`, `selftest_human_review.py` | O7 |
| GSS `northstar_matrix/{matrix,design_spec,scenes,placer,oracle,fakegame,reduced,det_export,selftest}.py` | O5; retain all required factor coverage |
| GSS `northstar_matrix/contact_sheet.py` | O6/O7 and N1 V06 |
| Shared `selftest_slackgeometry_internal.py` | O1 |
| Utils `selftest_flowworks_stock.py`, `selftest_flowworks_sheet.py` | One O2 invocation; sheet wrapper is redundant execution |
| Utils `selftest_flowworks_trench_cover.py` | O3 |
| Utils `selftest_gimmesomeslack.py` | O4/O5; avoid duplicate full invocations |
| FlowWorks `validation.py`, `northstar/validation_v2.py`, `live_session.py` | N1 master manifest/orchestrator; O1–O7 for offline branches |
| FlowWorks `preflight_flowworks.py`, `prep_site.py`, `site_spec.py`, `settings_registry.py`, `driver_stamp.py` | N1 00 rows; retain underlying reusable utilities |
| FlowWorks `manifest.py`, `runsheet.py`, `review_map_coverage.py` | O7 manifest and coverage production |
| FlowWorks `extension_proof.py`, `extensions.py` | N1 W/C/M/T/P/S/V rows |
| FlowWorks `extensions_rivers.py`, `river_scenes_walk.py` | N1 R rows |
| FlowWorks `climb_proof.py`, `reach_map_proof.py` | N1 P01–P04 and P06 |
| FlowWorks `deep_lake_proof.py` | N1 W11, W12, W18 |
| FlowWorks `deep_stone_live.py`, `quarry_find_live.py` | N1 W01, W19 |
| FlowWorks `depth_rebuild_proofs.py`, `scenarios/stage0_swim_pit.py` | N1 W06/W14, P06/P07/P12/P14–P17 |
| FlowWorks `legacy_fill_live.py` | N1 W04 |
| FlowWorks `pond_pump.py`, `liquid_checks.py` | N1 W10/W13, M01–M07/M14, H08 and S03 |
| FlowWorks `water_scenes_walk.py`, `live_probes/fw_water_headline.py` | N1 W06–W10/W18, M04, B11; H captures separately |
| FlowWorks `live_probes/fw_channel_ctrl.py`, `fw_pond_outflow_regression.py`, `fw_recede_topology.py` | N1 W08–W11 |
| FlowWorks `live_probes/fw_fluid_off.py`, `fw_water_pump_sluice.py` | N1 W08/W16, M04/M07 |
| FlowWorks `live_probes/fw_superdeep_target.py` | N1 P12 |
| FlowWorks `level_water.py`, `level_surface_bar.py` | O5 reference/parser; N1 W06 independent live measurement |
| FlowWorks `flow_bignet_live.py` | N1 X01; retain full workload |
| FlowWorks `pipe_levelling_perf_proof.py` | N1 X02 rehearsal; existing-map full-scale exception retained |
| FlowWorks `sitting_gaps_proof.py` | N1 00.settings_ui, M11, T07, B03, H05/H10, V01/V04 |
| FlowWorks `station_reach_live.py` | N1 M04/M05 |
| FlowWorks `sprinkler_live.py`, `glow_tank_live.py` | N1 M15–M19 |
| FlowWorks `thirst_live.py` | N1 T01–T15 |
| FlowWorks `wet_costs_live.py` | N1 P15/P16 |
| FlowWorks `walk_gaps_proof.py` | N1 M02/M05/M07, P03/P08; flight arms excluded |
| FlowWorks `trench_crossing_live.py`, `ladder_wall_proof.py`, `raid_ladder_live.py` | N1 P03/P04/P10 |
| FlowWorks `pit_rescue_live.py` | N1 P05 |
| FlowWorks `trench_cover_proof.py`, `trench_blast_live.py`, `trench_cast_live.py` | N1 P12/P13 |
| FlowWorks `raid_trench_proof.py`, `raid_siege_live.py` | N1 P10/P11; equipment predicates retained, flight excluded |
| FlowWorks `underpass_raid_live.py` | N1 B04 with actual band/path witnesses |
| FlowWorks `suspension_bridge_proof.py`, `suspension_settings_live.py` | N1 B01–B07 and V04 |
| FlowWorks `drawbridge_proof.py` | N1 B08–B13 |
| FlowWorks `lines_proof.py` | N1 B01/B02/B11, G04, H05/H06 |
| FlowWorks `joint_check.py` | N1 H11 and V04; H1-06 captures |
| FlowWorks `proof_hose.py`, `validation_hose.py`, `validation_style_hose.py` | N1 H01–H12; separate removal/migration executions retained |
| FlowWorks `validation_hose_offline.py` | O6 |
| FlowWorks `sheet_overflow_proof.py` | N1 S01–S06 |
| FlowWorks `water_looks_proof.py` | N1 V01; H1-01 visual judgment |
| FlowWorks `sweep_identity_proof.py` | N1 R07 |
| FlowWorks `player_missions.py`, `playtest_runner.py` | N1 X04; O7 limits/journal tests |
| FlowWorks `jetty_drop_live.py` | Offline action/confirmation tests; live launch remains excluded |
| GSS `validation.py`, `validation_aerial.py`, `validation_style.py` | N1 G01–G11, V05; O4/O6/O7 supporting tests |
| GSS `northstar/proof_all.py` | N1 master aggregation and durability; retain forwarded assertions |
| GSS `northstar_matrix/run_live.py` | Temporal matrix phases inside N1 G/H rows; O5 proves retained combinations |
| GSS `live_probes/gss_cord_static_dynamic_handoff.py` | N1 G10, including real section-boundary and roof/preference transitions |
| GSS `northstar/gss_playtest_runner.py` | N1 X04 and O7 |
| Both review-map builders and scenario builders | N1 fixture/soak verification; H1 for human review |
| Historical reports, captured logs, PLAN and BRIDGE_RUN_1 | Retained reference evidence; never accepted as current results |

### 4. GAPS AND RISKS

**The minimum layout is achievable; complete live certification under these constraints is not.** World-generation outcomes and flight outcomes remain deliberately unmeasured. An offline contract or manually staged appearance cannot discharge those live obligations.

**Coverage gaps found while merging**

The following distinctions matter: “no asserting check identified” is different from “has offline/source checks, but lacks a live proof.”

| gap | existing coverage today | required addition |
|---|---|---|
| Charity-gated exposed-prisoner distress | Explicitly unwired in `extensions.py`; requires two ideologies | P09 paired ideology/trait test |
| Flow-meter connected history and daily net | Def/compile wiring; `validation.py` explicitly owes live `PlaceMeter/ReadMeter` | C08 actual known-volume/history/save test |
| Actual drill and bleed-well production | Survey/status math and debug staging; yield chain explicitly owed | M08 scheduled reserve/pending/outlet accounting |
| Two-reaction live fairness | Offline/source checks; sitting-gaps scene is census-only | M11 fixture with two genuinely runnable/blocked reactions |
| Weir normal wear and repair rearming | Production implementation and observations; no asserting timed test identified in inventories | R04 normal cadence and repaired rearm |
| Real placer flood-edge replenishment | Stock arithmetic/forced refill; actual flood-edge pair owed | R06 real event and OFF/control pair |
| Late-budget natural heat and stale-source removal | Strong offline budget checks; live late-cell room/cache check owed | V03 beyond-budget rooms and drained-source comparison |
| Water-body freeze recount | Runtime implementation; no dedicated asserting runtime check identified | W15 runtime-created-body recount |
| Water-body type flipping | Existing **source-wiring assertion**, not complete live lifecycle proof | W15 membership/root/count test |
| Full sprinkler wet liquid-key behavior | Wet-grid math; live driver does not drive every key/output path | M17 exact identity/owner/save/harvest test |
| Live VFE sprinkler valve/boost behavior | Conditional XML/reflection/source checks | M19 actual installed VFE configuration |
| Hose placed/lifted event contract | Probe counters available; no complete asserting callback test identified | H07 captured arguments/order/map identity |
| Hose splice’s hydraulic meaning | Strong offline G2 geometry; visually joined ends can remain hydraulically separate | H11 explicit route/transfer assertion or explicit visual-only contract |
| Cache/mesh lifetime | Source guards and counters; incomplete lifecycle assertions | H12/G11/X03 repeated removal and map/session tests |
| Full floor-cord save/load equality | GSS orchestration omits the intended main comparison | G11 complete before/after edge/material/geometry comparison |
| Active gravship cutscene rendering | Idle-state reads and source/predicate coverage | Remains excluded from this no-flight plan |
| Typed shores and found-industry generation | XML/source contracts; live generation comparisons owed | Remains excluded; do not invoke generation |
| Flying immunity, jump-pack arrivals, voluntary flyer descent and gravship transport | Offline rules plus older launch-oriented drivers | Retain offline coverage; no live flight execution |

**Compression risks and how to preserve existing strength**

- **One site creates shared-state contamination.** Use independent transaction snapshots and reloadable phases. A field receiving residue from another test invalidates the row; it does not establish the expected effect.
- **Large-body and performance coverage cannot shrink to decorative ponds.** Keep the 72×72 lake, full large-network case and full 200-rig levelling workload. The compact site is not permission to reduce their sizes.
- **Pairwise coverage can disappear when scenes become one installation.** O5 must prove the same required factor pairs across temporal phases. The reduced matrix’s dropped aerial/hose conversion factors must be repaired before accepting replacement.
- **Direct proofs can bypass the defect being tested.** Keep real job, placement, scheduler, power-net, Scribe and world-pawn lifecycle assertions. `ProofStep`, forced flood hours, direct panning and instant bridge movement remain setup/diagnostic tools.
- **One aggregate row can hide a failed parameter.** Each row requires a complete parameter census and preserves every per-case result. Its verdict is the worst required result; no averaging.
- **Old measurement defects must be repaired first.** In particular: NaN-accepting comparisons, unrecognized isolation fixtures, vacuous successful-hose fuzzing, missing “extra” fresh geometry, incorrect blast-distance coverage, whole-notch conservation reads, unread poses treated as empty, stale style snapshots and success exits after failed rows.
- **Surface diagnostics need true connectivity.** Bodies linked through a shared pond must be measured together; isolated per-channel gaps are insufficient.
- **Negative controls need positive activity witnesses.** Store tanks require a mover control; underpass tests require actual band/path samples; locality requires an affected update; raid cage avoidance requires proximity and a firing control.
- **Random events cannot be certified by hopeful waiting.** Record a reproducible game RNG state where possible; retain bounded attempts and event witnesses. Failure to encounter the event is UNMEASURED, not PASS.
- **Human judgments remain independent.** Valid texture paths, terrain identities, counts and geometry hashes cannot approve color, readability, motion or installed-art alignment.
- **Optional mods require distinct configurations.** All DLCs being present does not imply DBH, VFE Farming, VCE/VGE, HugeThings, LuminousPigment, biome mods or RimUtinni are installed.

**Scripts/tests that cannot yet be retired**

| script/test | reason |
|---|---|
| Three C# SelfTest projects and their distinct suites | Stations cannot replace exhaustive arithmetic, fuzz, mutants, migration models or independent geometry rulers |
| Kernel/body/cord oracles and matrix catalogue tests | Independent expected results and combination coverage must remain |
| Art measurement/synchronization tests and generators | Installed pixels, generated tables and authored XML need their own reproducibility checks |
| Harness/verdict/restoration/report selftests | Gameplay success does not validate trustworthy reporting or cleanup |
| Full `pipe_levelling_perf_proof.py` workload | Rehearsal on a smaller map does not establish 325×325/200-rig performance |
| Existing legacy-save migration executions | Newly constructed state cannot reproduce old serialized jobs/types/keys |
| Hose/GSS mod-removal modes | Require separate mod configurations and a mod-less load; cannot run inside a joint installed-mod station |
| DBH and other optional-integration arms | Must remain available until actually run in the relevant configuration |
| Flight-oriented and generation-oriented cases | No authorized equivalent live replacement exists; preserve them disabled and explicitly outstanding |
| `player_missions.py` and playtest journal logic | Station automation alone does not prove player-only usability, deadlines or resume behavior |
| Evidence aggregation, keeper-save and owner-decision tooling | The station supplies evidence; it does not replace preservation and review functions |
| Every current driver until replacement rows pass equivalence/mutation checks | This is a plan only; no deletion or retirement is authorized |

The resulting reduction is **one human destination, one automated site, one offline entry point, and explicit configuration/scale exceptions**. It reduces duplicated staging and execution while retaining the distinct evidence needed to claim coverage.

## Verdict on coverage (BENCH, not GPT)

The compression covers everything on GPT's own merged list, but it does not cover everything that exists, and it compresses less than the "one station" headline suggests. I checked the reply mechanically. All 480 merged feature ids appear in the N coverage matrix, and all 127 eyes-needed features appear in the H matrix: none are missing from either. But those 480 were merged from about 2,000 inventory rows across the 24 part summaries, and I did not audit that merge, so a feature lost while merging would not show up here. The one H station (H1, 18 numbered captures) and the one N station (N1, about 150 rows on the same existing map) are each a whole connected settlement of roughly 224x224. The real reduction is in rows and checkpoints (calm, cold, fire and hostile reloads), not in places to walk. GPT also keeps eight offline bundles (O1-O8) and retires no script ("no deletion or retirement is authorized"), so this is a target layout, not a replacement yet. What it does not cover live, by its own gaps table: flight outcomes and worldgen-born content (typed shores, found industry), which our rulings exclude and which stay UNMEASURED; the mod-removal loads and the optional-integration arms (DBH, VFE sprinkler valves), which need other mod lists and cannot run inside one joint station; and the 325x325, 200-rig levelling perf workload, which does not fit a 224 site. It also names features with no asserting check today, which the station would have to add before it can stand in for anything: charity-gated prisoner distress, flow-meter history, drill and bleed-well yield, weir wear and rearm, the placer flood-edge refill, water-body freeze recount and type flip, the hose placed/lifted event contract, the splice's hydraulic meaning, and the full floor-cord save/load comparison. The reduced GSS matrix's dropped aerial/hose conversion factors must be restored too. Finally, the plan is only as good as the instruments it inherits. GPT itself says the measurement defects must be fixed first, and the items filed here are exactly those defects (stale proofs overwriting results, on-disk DLL hashes trusted, exit 0 on FAIL, all-off fixtures that are not all off). 70 validation-suite findings (50 GPT-MAJOR) are still unverified (GPT_FW_REVIEW_VERIFY_REMAINING_FINDINGS). Until both are cleared, no existing script should be retired in favour of N1.
