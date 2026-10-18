# FlowWorks review day 3 log 2026-10-17 (FOUNDRY reviewer, scratch clone review3)

base: 7986cc51e (origin/main; no FlowWorks C# commits since round 2)

## Files

(per-file entries appended below)
- now: Swimming/RM_Swim.cs (1041) whole
- Swimming/RM_Swim.cs (1041): read whole; nothing functional found. Fixed false doc (profile cache 'a quarter of a second' -> 60 ticks). lastWarn still write-only, bounded by our pawns (harmless). -> CLEAN candidate
- now: RM_LiquidStock.cs (1359) whole
- RM_LiquidStock.cs (1359): read whole (incl. round-2 Refill dL fix); checked CollectBody clears its buffers, Histogram is cumulative (DepthReport h[s+1] right), exact stage threshold 0.5 dL matches StageForExact. Nothing found -> CLEAN candidate
- now: RM_MapComponent_Excavation.cs (3190) whole
- RM_MapComponent_Excavation.cs (3190): read whole. DOUBT :2390 decided BUG (latent: every production caller with exact-level off passes one level, but the public all-or-nothing contract broke for dl > 1 level: first levels written then false, a caller keeping its liquid creates water). Fixed: room for all levels checked, one write. SelfTest LevelPour_whole_level_pour_is_all_or_nothing. Rest nothing (BedLevelsAt :1171 rec re-read is redundant, harmless). Stays DIRTY (fixed).
- now: RimMandrakeFlowWorksMod.cs (1860) whole
- DOUBT Mod.cs:684 decided BUG: pitDrowningHeadFraction greyed under pitDrowningEnabled, but RM_Swim reads it (IsSwimming exhaustion, NearestFooting) with drowning off, against the file's own rule (dependent only where unreachable). Fixed: Independent, slider drawn outside the greyed scope, tooltip names swimming. SelfTest Relative_head_fraction_live_with_drowning_off.
- now: rest of RimMandrakeFlowWorksMod.cs (1009-1870)
- RimMandrakeFlowWorksMod.cs (1868): read whole. Fixed two false player texts (mouseover tooltip 'ponds show their bed, scaled by how full' -> floor and water over it, limitless says never dry; levelExact 'the two settings below' -> one is above). Plus the :684 fix above. Stays DIRTY (edited).
- DOUBT RM_WaterBodyMendGame.cs:551 next
- DOUBT RM_WaterBodyMendGame.cs:551 decided NOT A BUG: vanilla DoTerrainChangedEffects (RimSage, Verse/TerrainGrid.cs:502) calls Overlaps inside the per-thing plant loop; the only calls before it are Plant/Filth Destroy() on the same square, none of which writes terrain in vanilla, and every postfix runs after the loop. A nested change could only come from another mod's Destroy hook and its effect is the vanilla answer (plant dies), never a throw.
- now: SelfTest/*.cs (66 files, ~17.7k lines): harness first, then tautology/swallow scan, then the six pit-rule tests
- SelfTest after fixes: 562/562 (2 new cases ok), hose 342/342. Committing fixes now; SelfTest file reads continue after.
- six P7-rewritten pit-rule tests (DeepBed, DeepDig, GptFixesA, PocketGrid, ReviewBatch56, Rewire in 01c6d2e01): each still guards the NEW relative rule with values that fail on the old one (FallScaleNotches 12->3x, 14->3.5x vs old flat 1; PitRoomCell both settings; sheet drowns nobody; wet pit costs its dry hole). GptFixesA's AttachChance(heldInPit, false, ..) hard-codes onCover=false: checked IsPitFloor reads covers (RM_PitRooms.cs:80-93), so not a weakening.
- SelfTest harness: every Assert/Check helper throws or counts (scripted scan); catches are expect-throw or recorded fails; no Case without an assertion.
- RelativeRulesChecks.cs (293): read whole; note shooting cost case is a wall-clock assert (< 5 us/ask, generous)
- SwimChecks.cs (319): read whole. FOUND can't-fail: Swim_wired_at_call_sites 'on the screen: n' and Swim_shallow_drowning_switch_alone 'shown in Mod Settings' matched 'ref n,' which the Scribe line itself contains (passes whenever 'scribed' passes). Same in RelativeRulesChecks 'on the screen' (matched the Scribe key string). Fixed: both read only the drawn section. Note: Drown() helper mirrors production downed rule (production is Verse-bound; source-checked in the wired case); RecoveryPerCheck is a test literal of the hediff comp.
- now: Lake/Level/Pond/Deep* check files
- LevelExactChecks.cs (303): read whole. FOUND: Exact_migration_reads_float_stock_to_the_decilitre asserted the test's own copy of round(f*U), never production (RM_LiquidBody is Verse-bound). Fixed: Has() binds it to RM_LiquidBody's load line. Rest strong (hand-worked S5/S6 numbers, 600-seed fuzz with conservation + rest gap; surface-gap instrument proven able to go red).
- LevelPourChecks.cs (275+): read whole; LevelOps is the test's adapter over production RM_LevelPour (oracle mode), production adapter bound by Has(); nothing more. -> clean after commit
- LakeFloorChecks.cs (475): read whole; nothing (determinism, roughness ladder, off-radial with radial control = 0, stranding control, wiring). Line 306 shelf-off assert is loose (>= 4 passes) but labelled.
- DeepDigChecks.cs (310), DeepBedChecks.cs (368): read whole; nothing (cap/never-shallows with the old-clamp control, cost table, 4/7/7/4 exact settle, LIFO refill exactness, chasm control).
- PondDepthChecks.cs (309): read whole; nothing (S7 is a 10 ms wall-clock bar). PondReturnChecks.cs (291): read whole; WEAK, not fixed: Pond_restore 'requeue order' and Pond_bed_hollow_round_trip_is_lifo_exact assert the order of the test's own list model, not production (production order is pinned by Has() on Restore's requeue line in the same case); labelled 'modelled'.
- LevelSurfaceChecks.cs, VolumeChecks.cs, PumpChecks.cs, OutflowChecks.cs: read whole; nothing.
- TransferChecks.cs (567): read whole. GAP fixed: caller-coverage WorldMutations predates the decilitre API, so TryPourDl / TryDebitDl / CreditDl / TryReturnDl in a site file outside a transfer leg passed unseen (all current calls are inside legs). Added them.
- TakenIdentityChecks.cs (168), WaterBodyMendChecks.cs (723): read whole; nothing (vanilla port shows each trap bare before the mend; 3000-scene split fuzz vs true components; local split test vs full count).
- WeirPoolChecks.cs, SprinklerChecks.cs, ContainerStyleChecks.cs, GptEdge1016Checks.cs, HoseHoldChecks.cs: read whole; nothing (each has its can-fail / old-rule probe).
- GptFixesAChecks.cs, PocketGridChecks.cs, ReviewBatch56Checks.cs, RewireChecks.cs: read whole; nothing.
- now: FlowKernelFuzz.cs (1110), VV/ShippedMatrixProbe.cs (293), Program.cs (2049)
- FlowKernelFuzz.cs (1110): read whole; harness sound (per-fluid conservation, sink accounting, fixed-point only when settling is expected, each regression has its control). GAP: every kernel fuzz (FlowKernelFuzz.Gen/FillsFromLimitless/SurfaceRandom, LevelSetChecks, LevelExactChecks) digs 1..4 notches only, from before P5 (digs to 20 m) and P11 (floors to 50 m). Added Exact_fuzz_past_2m_conserves_and_rests_level (300 scenes, holes to 40 notches, beds to 16) on the shipped exact kernel; running.
- SelfTest after test fixes: 563/563 (both screen checks, the migration bind, the dL caller-coverage and the deep fuzz pass), hose 342/342. Committing; then VV probe + Program.cs.
- VV/ShippedMatrixProbe.cs (293): read whole; nothing (usage line omits 'trace', cosmetic).
- now: Program.cs (2049)
- Program.cs (2049): read whole; cases sound (the four Scenario_* displacement cases replay the walk in the test, as the header says; Liquid_unit_contract loop is a self-acknowledged tautology carried by its size asserts + mutation probe). Fixed stale comments (two '5:1 budget' claims: the rule is dead; a LevelSurfaceChecks comment pasted onto the LevelExactChecks line).
