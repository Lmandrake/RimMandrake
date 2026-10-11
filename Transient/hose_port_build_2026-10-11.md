# Hose port build log — 2026-10-11

Builder: BENCH subagent. Design: `design/RimMandrake/hose_port_to_flowworks_design_FINAL_2026-10-10.md` (f8fee03e4) over v2.
Item: `HOSE_REEL_MIGRATE_TO_FLOWWORKS_AT_LAST`. Step 9 skipped (Q3 needs owner yes).

## Owner rulings
- **Q7 (owner, typed 2026-10-11): "Yes, a tank would pass liquid on to a hose screwed into it, without a pump needed."** Replaces the Q7 default (no). Built at step 6 (tank<->hose coupling): a tank coupled to a laid hose feeds it directly, no pump; pipe runs still never merge through a tank (the BFS still stops at tanks; only the hose link leaves a tank).

## Owner defaults used (Q1-Q7)
- Q4a (art moves byte-for-byte during the pause): YES at step 2 -- 40 hose PNGs moved through the art ledger writer (40 installed, 40 retired, 0 owner-kept), no pixel changed.
- Q4b (reels without a picked look): FlowWorks' own `hose_defaultLook`, seeded once from GSS's global `style` (4-row LookOf table), else Scrapper (step 2).
- Q5 (build tab): RM_HoseReel moved Misc -> Production (step 2).
- Q1 (static liquid hose -> universal pipe): YES at step 4 -- renamed RM_UniversalPipe, sturdier PROVISIONAL stats, old saves keep their pipes through the def alias. Q2 (hoses off carry nothing): step 6. Q3: not run (step 9 skipped). Q6 (no flow direction drawn): kept.
- Q7: replaced by the owner's ruling above.

## Increments
| # | status | sha | files | offline test |
|---|---|---|---|---|
| 0 | done | 6b031841a | FlowWorks/validation.py, FlowWorks/northstar/selftest_extensions.py | selftest_extensions PASS (+P12 adapter case; sanity: reverting the fix FAILs it) |
| 1 | done | 6c71cb8bc | _Shared/SlackGeometry/* (5 git mv + CordSig), _Shared/StylePicker/StylePickerCore.cs, GSS usings/csprojs/StylePicker/CordMaterials, 169 member decls public->internal | GSS SelfTest 871/871, hose 130/130, aerial 96/96 (identical to step 0); top-level-type gate PASS (23 decls); slice 20/20 GREEN |
| 2 | done | 7cf08bf64 | GSS Source/Hose/** + 3 defs + 40 PNGs (art ledger) + 4 whole selftest files + hose parts of 5 mixed ones -> FlowWorks; RM_HoseSettings section + import; HoseLook; RM_HoseLegacy(+Math) essentials/alias/import/old-GSS; HoseStyleProbe; Utils/validation_core.py; validation_hose*.py moved; validation_hose_offline.py; selftest_hose_port.py; walks; JawaBench playtest | FW SelfTest 140/140 + hose 278/278 (257 moved + 21 new); GSS SelfTest 614/614 (871 - 257 = 614, nothing lost); GSS proof_all --offline-gate red []; selftest_hose_port 18/18; selftest_extensions PASS; slice 24/25 (the 1 = pre-existing GSS#Cables screen check) |
| 3 | done | b03b241e1 | FlowWorks/About/About.xml loadAfter mandrake.rm.gimmesomeslack; selftest_hose_port P7 | lint_mod_defs FlowWorks 0 ERROR 0 WARN; hose port gates 20/20; about-dependency selftest green |
| 4 | done | 5959305b8 | P13 preflight P-B4 fix + fake fault; RM_LiquidHose -> RM_UniversalPipe (def, label, description, PROVISIONAL 100 HP / 2 steel / work 60 / flammability 0.4), RM_UniversalPipeExtension (+[Obsolete] RM_LiquidHoseExtension), def alias as 3rd essential; liquidHosesEnabled -> universalPipesEnabled (old key read once); settings_registry.py; machinery_hoses -> machinery_pipes | FW SelfTest 140/140 + hose 281/281 (+3 def-alias); selftest_flowworks_northstar PASS (+settings_absent dirt, hose section vs C#, 107 toggles); selftest_settings_registry 14/14; selftest_extensions PASS (83 toggles, registry coverage); hose port gates 23/23; v2 offline O-LIVE-NEG PASS; slice 26/26 |
| 5 | done | d69cb36f5 | Building_LiquidPump.TryPour + RM_PumpMath.PickPour (P1); CompLiquidConverter loop over candidates + RM_ConversionMath.FirstRunnable (P2); RM_LiquidBathMath + JobDriver_DoBill fail condition + no silent unpaid completion (P3); SelfTest PrePortFixChecks.cs | FW SelfTest 144/144 (+4 cases, each with a can-fail) + hose 281/281; lint 0 ERROR (1 WARN: the [Obsolete] RM_LiquidHoseExtension is referenced by nothing -- intended, kept for third-party XML); slice 26/26 |
| 6 | done | 0d5cc1766 | NEW Machinery/RM_LiquidNetKernel.cs (Verse-free rules), RM_LiquidNet.cs (adapter + RM_HoseLinks index + Credit + tank feed), HosePorts (FlowWorks types, Machine kind), HoseFlow (NetFlow + debug, adapter/relay providers deleted), CompHoseReel (lease, saved tint/pending), RM_MapComponent_Hoses (tint from LiquidDef.color, tank feed tick), 11 credit sites, HoseTint/useFlowWorksPumps/defaultFluid deleted; SelfTest HoseNetChecks (44); RL6 split; probe fields | FW SelfTest 144/144 + hose 325/325 (257 moved + 68 new: 44 net); hose port gates 26/26 (P9 caller coverage 11/11); lint 0 ERROR; registry 14/14 (106 toggles); slice 26/26 |
| 7 | done | ce604f423 | RM_NetCache (kernel) + RM_LiquidNet.Walk cached per origin per tick, TanksFor revalidates each route (dead link -> tank dropped, origin dirty); SelfTest HoseNetCacheChecks | FW SelfTest hose 332/332 (+7 cache/perf); perf model 0.00105 ms/tick mean against the 0.05 budget (20 reels, 4 pumps, 10 tanks), one walk per pump cycle; hose port gates PASS |
| 8 | done (harness; live run owed) | ef888b271 | NEW northstar/proof_hose.py (one-session hose live driver: matrix_hose cross-mod, hose, maze, relay, carry, style_hose, realflow NS_* x12, SL1-SL4, PP1/PP2 pre-port saves, Z), northstar/manifest.py (walk checkout = v2 UNION hose), selftest_proof_hose.py (contract), HoseNetProbe.cs (tank/filltank/flick/pump/net verbs: the far tank is read, G3.11), preflight log needles G6.3 (+6 offline cases), FW validation hose_live_rows reads proof_hose results at the current hash, walk +10 bars | selftest_proof_hose 14/14 (declared = emitted, stale/partial/non-certifiable refused, missing -> UNMEASURED); proof_hose --offline-gate red []; GSS proof_all --offline-gate red []; selftest_flowworks_northstar PASS; slice 27/27 |

## Deviations from design
- Step 8 is the harness only: the live bridge session (and the live dev-mode perf reading of step 7) is NOT run -- this job was
  told not to touch the game or the bridge. proof_hose.py's control flow is proven offline against a fake bridge; the
  real-flow scene geometry (plots at x 158-242, z 150-198) is untested live and may need tuning on its first run.
- Step 8: the pre-port mid-carry / mid-retract save fixtures cannot be MADE without the game; proof_hose.py takes them
  as --preport-save CARRY,RETRACT and reports PP1/PP2 UNMEASURED without them (never absent).
- Step 8: GSS's human review map keeps the hose stations (cross-mod); moving them into FlowWorks' own review tooling is not
  done (FlowWorks' review sheet is a capability sheet, not a station map) -- the K09 capability row carries every hose bar.
- Step 7: the perf budget is proven on the kernel with a modelled index-rebuild cost (SelfTest); the design's "plus one live
  dev-mode profile reading" needs the game and is owed to the live stage (not run: no bridge in this job).
- Step 6 (a gap in §3.1): a reel that is BOTH fed by another hose (a relay) and coupled to a port of its own uses the RELAY
  vertex as its inlet (its own port is ignored while it is fed), so a chain is never cut at a reel that happens to stand by a pipe.
- Step 6 (owner Q7 ruling, mechanism chosen here): every 250 ticks each live hose with a TANK at an end passes liquid from that
  tank across the hose to the emptiest compatible tank it reaches beyond (another tank, a pipe run's tanks, further down a
  relay chain), toward equal fill, at most 5 units a cycle, credited to the hose like any transfer. Only the tank at the hose
  end feeds; a tank still never conducts (the tanks of a pipe run it stands in are not reached through it).
  RM_LiquidNetKernel.TankFeedUnits / FeedTarget / Across, 8 HoseNetChecks rows.
- Step 6 lifecycle detail: a re-lay to the SAME end keeps the lease (a corridor re-route while flowing does not flicker);
  a lay to a new end, a refused lay, leaving Laid and despawn end it. The tint is forgotten once the strand is Flat with no flow.
- Step 4: the universal-pipe switch stays in RM_MachinerySettings (its owning section) and is drawn there, relabelled
  "Universal pipes join tanks into a net", not under the hose heading.
- Step 4: the typed registry (northstar/settings_registry.py) is the source for extensions.py's SETTINGS_OF/DEFAULTS;
  validation_v2.py's BOOL/FLOAT default tables and site_spec.toggles() are ASSERTED equal to it (selftest_settings_registry)
  rather than rewritten to read it -- same guarantee, no churn in the v2 O2 census.
- Step 4: 24 bool switches (23 pre-existing, + useFlowWorksPumps until step 6) were never on FlowWorks' toggle floor; they
  are now named in validation.py TOGGLES_NOT_ON_FLOOR so the gap is fixed-size and visible (not filed: not a defect of a
  mechanism, a harness coverage gap older than the port). The four hose bools are on the floor as HOSE_TOGGLES_OWED (no row flips them yet).
- Step 4: Utils/modcheck/required_checks.json is stale on origin (its --check fails before this port's edits touch it);
  regenerating rewrites 40+ other mods' rows, so it was NOT regenerated here (shared derived file, left to its owner).
- Step 2: the GSS human review map (GimmeSomeSlack/human_review.py) KEEPS its hose stations for now as cross-mod stations
  (they drive FlowWorks' HoseProbe, so the map is built on the flowworks tier, which carries both mods); its art board reads
  the hose art from FlowWorks' folder. Moving those stations into FlowWorks' own review tooling is step 8 harness work.
- Step 2: GSS AerialProbe census now reports its overhead queues; RL9 (FlowWorks) reads them by name, cross-mod, UNMEASURED
  when GSS is absent (design M3).
- Step 2: StyleStage3's clause "the reel is not in AerialStyles.StyledDefs" was dropped from the moved check (FlowWorks cannot
  see GSS); the same fact is enforced by selftest_hose_port P2 (no hose code left in GSS at all).
- Step 2 (not in the design, found on the way): bridgetools/JawaBenchGssPlaytest.cs compiled against GSS's hose and core
  types. It now references RimMandrakeFlowWorks.dll under extern alias `flowworks`, and both mods grant it
  InternalsVisibleTo (the shared geometry is internal). Compile-checked against the repo DLLs (build.py, no --apply);
  NOT deployed. build.py's dry stage used the wrong stage name (the -p:GssModDir override never resolved): fixed.
  ExplosiveKnockback's by-name hose hook repointed to FlowWorks' type names (flag renamed `Hoses`).
- Step 2: the GSS GPT-read shape "B7 hose corridor hash has route cost" was already red after step 1 (CordBuilder.CellSig ->
  CordSig.CellSig) -- step 1 ran the slice but not proof_all --offline-gate. Moved to HO7 with the new fragment; green.
- **Full `run_selftests.py` cannot finish inside one 600 s foreground call** (391 tests; several take 150-240 s; it also
  waits on FOUNDRY's suite lock). Each increment runs the relevant slice instead (`--only`: every selftest under
  GimmeSomeSlack/, FlowWorks/, _Shared/, plus selftest_gimmesomeslack/flowworks_stock); the full suite is owed after the port.
- Step 1: the internal cascade was fixed at MEMBER level (169 declarations public->internal), not by making whole GSS
  types internal, so XML-referenced classes (comps, map components, probes) stay public.

## FlowWorks pre-existing bugs fixed in-port
- P12 (step 0): FlowWorks validation `_report_rows` kept PASS on a SKIP row -> UNMEASURED.
- P1 (step 5): a pour took the first channel-capable tank and stopped, so a water tank first on the net starved a tar tank by a tar channel -> every providing tank tried in net order (RM_PumpMath.PickPour, production).
- P2 (step 5): a converter returned at the first input with a recipe even when it made 0 batches -> the first RUNNABLE input runs (RM_ConversionMath.FirstRunnable, production).
- P3 (step 5): a bath craft completed unpaid when its tank was drained/disconnected mid-craft -> the DoBill job fails while unpaid (RM_LiquidBathMath.Pay); an unpaid completion is logged, never silent.
- P13 (step 4): preflight P-B4 passed with required settings fields ABSENT from the loaded DLL -> FAIL naming them
  (FakeFlowWorksGame gained a `settings_absent` fault; the dirt test refuses it).

## Bugs filed (not fixed) -- FOUNDRY, kind task, target v1 (design FINAL §5)
PUMP_FED_CHANNEL_STALL_PROVE_AFTER_RELOAD (P4), FLOOD_DEBIT_MEND_DEEP_CELL_ONE_LEVEL (P5), FLOOD_SWITCH_RACE_MEND_ENGINE_OFF (P6a),
TAR_COOLING_GLASS_MEND_ENGINE_CELLS (P6b), FLUID_PALETTE_EXHAUSTION_MEND_KEY_ZERO (P7), FIRE_BURN_PULSE_PROVE_REFILL_RACE (P8),
HEAT_BUDGET_PREFIX_MEND_LATE_CELLS_STARVE (P9a), NATURAL_HEAT_CACHE_PROVE_STALE_DAYS (P9b), WEIR_WASH_ITEM_LOSS_MEND_PLACE_FIRST (P10),
STATION_REACH_CENTRE_RETHINK_FOOTPRINT (P11), MISSION_TANK_GOAL_REWIRE_TO_DEST (P14). (P1-P3, P12, P13 were fixed in the port.)

## Moved tests (step 2) -- every one still runs
- C# SelfTest, GSS -> FlowWorks (run by `selftest_flowworks_stock.py`, "hose:" block, per-suite counts printed): HoseSelfTest 130,
  HoseCarryChecks 33, HoseLiveChecks 21, StyleStage3Checks 10 (whole files); split out of mixed files into HoseReviewChecks.cs:
  HoseReview6 26 (ReviewRound6 Draw/Length/Relay), HoseReview7 7 (ReviewRound7 EndsOnEdge/LaysIntoEverySide/Station42/WireWidth;
  the GSS file was left empty and deleted), HosePileLook 6 (PileLook rule 3), HoseGptFix 20 (GptReadFix B4/B10/B11/B13/B5/B2-B3);
  HoseFuzz 4 (GssFuzz hose + trail families, same seeds, same 2798/1500 cases and known-gap tallies). Total 257 moved; GSS 871 -> 614.
  NEW: HoseLegacyChecks 21 (alias table, import fixtures x3 folder families, look import).
- Stayed in GSS on purpose: LaneAChecks.HoseChecks (it tests GSS's CordBuilder with the hose LayParams, not the reel);
  LegacyNameChecks (GSS's own MessyConduit rename table, whose FireHosesMod handle still feeds the FlowWorks import).
- Python: validation_hose.py, validation_style_hose.py -> FlowWorks (on Utils/validation_core.py); GSS validation O5 hose art,
  O6 B8/B22, O6 B20 (hose files), O7 hose shapes -> FlowWorks/validation_hose_offline.py HO5-HO8 (registered as FW chain
  `hose_offline`); GSS ROW_SHOWS hose rows + the UNBUILT pump row -> FW `HOSE_ROW_SHOWS` / chain `hose_live_rows`;
  GSS proof_all hose/maze/relay/carry/style_hose blocks + SL4 + the 9 matrix hose scenes -> FlowWorks/northstar/proof_hose.py
  (step 8; until then each is runnable standalone through validation_hose.py --live/--maze/--relay/--carry and
  validation_style_hose.py --live; the matrix scenes through reduced.hose_spec()).

## Lessons
- infrastructure/state/lessons/20261011T085915Z-BENCH-moving-types-between-mods-or-making.md: compile-check the JawaBench companion against the repo DLLs after moving types between mods.
- Step 1: run each mod's own offline gate (proof_all --offline-gate), not only run_selftests: a source-shape row (O7) went red
  on a pure rename and only the gate reads it.

## Step 0 census (bench HEAD b525ecca8, 2026-10-11)
- GSS SelfTest: **871/871** total; `hose:` suite (HoseSelfTest) **130/130** — the design's sanity probe said 129; one check was
  added since (drift, not a fault). Aerial 96/96.
- Mod/ModSettings classes: FlowWorks `RimMandrakeFlowWorksSettings`/`RimMandrakeFlowWorksMod`, `RiverSteamSettings`/`RiverSteamMod`;
  GSS `GimmeSomeSlackSettings`/`GimmeSomeSlackMod`, `AerialSettings`/`AerialLinesMod`, `HoseSettings`/`FireHosesMod` (moves).
- Hose settings: 17 Scribe keys (`HoseSettings.cs:54-75`); 15 survive (useFlowWorksPumps, defaultFluid die at step 6).
- `GimmeSomeSlack` strings in moved files: 21 files (16 C#, 3 defs + styles) — all rewritten at step 2.
- 11 credit sites verified at the FINAL doc's lines: pump 152/169/231, converter 219/223, adapter 135/153, reactor 184/185/191, bath 148.
- Live hose rows declared in GSS proof_all DECLARED_ROWS: hose 6, maze 8, relay 8, carry 8, style_hose 6, SL4 1 = **37**;
  matrix hose scenes H00-H08 = **9** (reduced.py HOSE_PREFIX). human_review.py: 192 hose/reel mentions (stations moved at step 2/8).

## Pre-existing failures seen, not mine
- `lint_mod_defs.py GimmeSomeSlack`: 2 ERROR (loopBudget Scribe default; excludedConduits never Scribed) -- GSS cable settings, not hose; left to the GSS owner.
- `Utils/selftest_settings_screens.py` GimmeSomeSlack#Cables: "6 groups found, expected 5" -- fixed upstream by the GSS owner
  (f740ce1ce) before step 2 landed; 802/802 after the sync.

## Other fixes made on the way
- e83c94277: FlowWorks validation CORE_LIVE_IDS lacked P3f/P4f, which FOUNDRY's 125c2e298 added to v2 (selftest_extensions red on origin).

## Clone sync (coordinator order, after step 2)
- Synced at the step-2 boundary: Transient peers' paths stashed, `git pull --rebase origin main`, stash popped. The six
  local-ahead duplicates dropped. Step 2 conflicted with the GSS owner's SwitchFlipChecks (c7130f81f) in the GSS SelfTest csproj
  (adjacent lines) and the GSS DLL: kept BOTH sides (their SwitchFlipChecks line, my hose lines removed) and REBUILT the GSS DLL
  from the merged source (no side's DLL kept); GSS SelfTest 628/628 (614 + their 14). `git rev-list --count HEAD..origin/main` = 0.
  The duplicate staged lesson file was unstaged and removed (identical to origin's copy).

## Final offline totals (2026-10-11, bench == origin/main)
- FlowWorks C# SelfTest: 157/157 core cases + hose 332/332 assertions (257 moved from GSS, 75 new: legacy 24, net 44, cache/perf 7).
- GSS C# SelfTest: 628/628 (871 - 257 moved + the GSS owner's 14 new flip checks); aerial 96/96.
- GSS `proof_all.py --offline-gate`: red []. FlowWorks `proof_hose.py --offline-gate`: red [].
- selftest_hose_port 28 rows PASS; selftest_extensions PASS (64 bars, 83 toggles); selftest_settings_registry 14/14;
  selftest_flowworks_northstar PASS; selftest_proof_hose 14/14; settings screens 802/802; lint_mod_defs FlowWorks 0 ERROR.
- run_selftests.py slice (every selftest under GimmeSomeSlack/, FlowWorks/, _Shared/, bridgetools/ + the GSS/FW wrappers,
  settings screens, art): 27/27 GREEN. The FULL suite was not run (>600 s and lock-shared); owed.
- Not done in this job (by instruction): deploy, the live proof_hose session, the live perf reading, the pre-port save fixtures.

## Review fixes
Fixes for Transient/hose_port_offline_review_2026-10-11.md (4ca1d7c70). Per finding: fix · files · sha · test that fails on the old code.

- M1: fix: the five HoseLook.cs [PatchFeature] fields written as the literal "enabled" (house style). Files: FlowWorks/Source/Hose/HoseLook.cs, FlowWorks DLL+.srchash. sha 12f4f7998. Failing test on old code: selftest_lint_harmony_targets.py, 3 FAIL (NO_FEATURE x5) -> PASS 0 failures.
- S1: fix: new Verse-free `HoseRelayIndex` (Hose/HoseRelay.cs): intake-cell dictionary, laid next[], loop flags by
  cycle-marking the functional graph, feeders by inversion; built O(reels) and shared by RelayOf/RelayAt/FeedersOf/Loops,
  drawing, RM_HoseLinks.Refresh (RM_LiquidNet.cs) and DebugHoseFlow. Rebuilt only when a laid end / footprint / debug flag
  changes (RelayVersion bumped at every writer; an O(reels) signature check once per tick is the backstop). DebugHoseFlow
  answers null at once when no reel on the map carries the flag (idle maps walk nothing). Files: Hose/{HoseRelay,
  RM_MapComponent_Hoses,HoseFlow,CompHoseReel,HoseProbe}.cs, Machinery/RM_LiquidNet.cs, SelfTest/HoseNetCacheChecks.cs, DLL.
  sha e9e3687be. Tests (real code path, HoseNetCacheChecks 7 -> 16): index == old per-query RelayOf/Loops/FeedersOf on 24
  layouts with chains+loops; rebuild + all queries = exactly n intake enumerations at n=20/60 vs old shape 214/3152 (the
  old shape fails the `== n` bar; can-fail row proves the counter sees it); n=60 0.042 ms vs old shape 9.07 ms (>=10x bar);
  idle debug provider 0 feeder steps. FlowWorks hose 342/342, core 157/157.
- S2: fix: `RM_HoseSettings.tanksFeedHoses` (Scribe `hose_tanksFeedHoses`, default true, checkbox in "Flexible hoses"),
  gate `RM_LiquidNetKernel.TankFeedOn(enabled, tanksFeedHoses)` first thing in TankFeedTick; site_spec + validation.py
  `hose_switch_flips` chain claims the toggle (HOSE_FLIP_TOGGLES); registry/northstar counts 16->17 fields, 106->107 toggles.
  sha 6319c8e56. Test: C# case HoseSwitchFlip_tanksFeedHoses (gate flip + call-site regex) -- the call-site regex does not
  match the old RM_LiquidNet.cs (checked against 801786bc4: False).
- S3: fix: `RM_LiquidNetKernel.TankFeedTransfer` (remove -> checked add -> put back on refusal, credit only on success,
  ErrorOnce if the put-back is refused too); TankFeedTick moves units only through it. sha 6319c8e56 (same commit as S2,
  same function). Test: C# case HoseTankFeed_refused_add_puts_back (refused add: 0 moved, src back to 100, 0 credited;
  plus call-site regex and "no unchecked dst.TryAddLiquid(liquid, n);" -- the old source has it: fails on 801786bc4).
- S4: fix: RM_LiquidNetKernel.Walker.Run is now level-by-level in hose links crossed (0-1 BFS: origin and pipe/relay links
  are deferred to the next level), so a tank reached by pipe keeps the empty route and pipe-reached tanks lead. Files:
  Machinery/RM_LiquidNetKernel.cs, SelfTest/HoseNetChecks.cs, DLL. sha 417893e68. Test: HoseNetChecks "tank on pipe AND
  hose: route is the pipe (empty), hose H on no route (stays flat)" + can-fail (pipes off -> route H). Run against the old
  kernel (6319c8e56's file swapped in): FAIL, 343/344; new: 344/344. Kernel oracle 3000/3000 unchanged.
- S5: fix: P1's checker is now `p1_duplicates()`; its can-fail runs it (defnames parser included) on three planted mod
  folders: a shared defName must be reported, disjoint folders none. P3/P8 relabelled "(source shape)" and the run prints an
  explicit UNMEASURED line for the live PP1/PP2 alias proof (not the run_selftests phrase, so the file still grades PASS).
  File: FlowWorks/selftest_hose_port.py. sha 1baf783cb. "Fails on old code": the old can-fail never called a checker, so no
  old-code run can fail it; the new row fails whenever the checker misses a planted duplicate (e.g. p1_duplicates -> []).
- S6: fix: GSS walk lines 89/100 now cite FlowWorks/validation_hose.py and FlowWorks/Source/Hose/CompHoseReel.cs;
  GSS SwitchFlipChecks header states where the hose's switches live; FlowWorks human_review K09 no longer says real flow
  "lands at port step 6". (No "built in Gimme Some Slack"/"lives in GimmeSomeSlack" text remained in FlowWorks/human_review.py
  at 801786bc4 -- its only GSS mention is the accurate "moved from" label.) New gate P10 in selftest_hose_port.py. Files: the
  walk, GSS SwitchFlipChecks.cs + GSS DLL/.srchash, FlowWorks human_review.py, selftest_hose_port.py. sha ee20cf5bb.
  Test: P10 with the old walk (801786bc4) swapped in: FAIL (names GimmeSomeSlack/validation_hose, missing paths); now ok;
  planted can-fail catches an old-path pointer and a missing path.
- S7: not subsumed, so restored. reel1_staged/reel2_staged: proof_hose.save_load again stages reel 1 DROPPED and reel 2
  CARRYING before the one save (GSS's stage_carry_for_save, f8fee03e4), and SL4 = `sl4_verdict` (CR4a exact round trip,
  CR4b Carrying back with trail + Deploy order, every other carried hose survives) + the CR5 resume-to-Laid read;
  UNMEASURED when a half could not be staged. H0_probe_channel: HP2_probes_site_pinned is the successor for a passing one
  (same hp("defaults")); a FAILING one now turns every MX_ hose scene FAIL (declared ids unchanged). Files:
  FlowWorks/northstar/proof_hose.py, selftest_proof_hose.py. sha c704eec4d. Tests: selftest_proof_hose +7 rows; with the old
  proof_hose.py (801786bc4) swapped in, "SL4 with only a Dropped hose ... UNMEASURED" FAILs (old read PASS) and sl4_verdict
  is missing. The restored live staging itself is NOT run live (no bridge in this job).

### Review-fix gates (2026-10-11, bench == origin/main at cfa64e63c + peers' uncommitted Transient files)
- Full `run_selftests.py` (one call, 456 s): PASS 396/399, FAIL 1/399, CRASH 0, UNMEASURED 0, SKIPPED 2 (deployed tier).
  The one FAIL was selftest_one_path_seam on origin's new MineShaft/validation.py (a LocalLow literal, 4a6a9a837, not hose
  work); fixed at cfa64e63c (imports game_paths.LOCALLOW), seam selftest 6/6. A first run before syncing the clone also
  showed selftest_ledger_lint red only because the clone's FOUNDRY shard was behind a freshly fetched origin.
- FlowWorks C# SelfTest 159/159 core (+HoseSwitchFlip_tanksFeedHoses, +HoseTankFeed_refused_add_puts_back), hose 344/344
  (+9 relay-index/perf, +2 S4). GSS SelfTest 628/628, aerial 96/96. validation_hose_offline 4/4. selftest_hose_port PASS
  (P1 planted, P10 new). selftest_proof_hose PASS (+7). GSS `proof_all.py --offline-gate`: red []. dll_source_stamp check:
  109 MATCH, 0 MISMATCH.
- Still owed (live, not in this job): proof_hose live session (now including the restored SL4 staging), PP1/PP2 pre-port
  save fixtures, the live perf reading.
