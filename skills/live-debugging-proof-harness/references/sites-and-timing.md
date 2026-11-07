# Sites, map persistence, timing windows and save fixtures

## The map is not calm on the full list

- **Wild animals respawn** after a one-off non-colonist sweep. A predator stabbed two
  colonists down mid-run on 2026-10-11. So re-calm before **each** block
  (`jawa/destroy_bulk filter=nonColonists dryRun=false`). For the general staging
  method, see `rimworld-live-review` §1.
- **Idle colonists wander fast into sites**: draft every colonist the block is not
  using. The `reveal` helper drafts the colonist it borrows for the same reason.
- **Map-gen hostile structures** keep the world uncalm. An insect hive (BetterInfestations)
  throws its own NREs.
- **Don't let the suite kill its own fixtures.** modcheck's "everyone is dead" floods were
  `Session.sweep` killing the suite's own test colonists (Bomb 99999), plus explosion
  tests placed at the map centre where the colony spawns. Register fixtures with the
  situational Watch, and anchor destructive tests away from colonists.
- **`jawa/damage` skips player pawns** unless `allowColonists=true`. A pawn's
  `Thing.HitPoints` is ~0, so `CompExplosive` detonates on ANY damage unless
  `requiredDamageTypeToExplode` is set. `restore_needs` verifies by percentage
  (Food max is 0.9).
- **Process-wide statics survive a scene change.** GSS `PowerTheftConsequences` counters (`caughtCount`, `goodwillCharged`) are GLOBAL statics: an `RM_PowerTapClamp` left on the map from an earlier scene kept draining and charging the same faction, so one day read -4 instead of -2. A theft scene must remove every `RM_PowerTapClamp` on the map first (`validation_aerial` `theft_catch` does).
- **Chaining proofs on one map is a SITE hazard.** FlowWorks liquid loss is attributable per bridge call: read `RM_MapComponent_Excavation.overflowDestroyedTotal` with `jawa/map_comp_read` after every mutating call. It pinned 200 'lost' levels on one `ProofStageBasin` strip of a rehearsal staged over another proof's ponds: not a mod conservation bug.
- **A rescue scene needs MEDICAL beds.** Set them with `jawa/set_bed_owner_type medical=true` and read back. A tired rescuer lies down in a free plain bed and claims it (`Toils_Bed.ClaimBedIfNonMedical`); `RestUtility.FindBedFor` then finds no bed for the patient and `WorkGiver_RescueDowned` never offers the rescue, which looks exactly like a mod regression (`pit_rescue RESCUE_COLONIST_OUT` went PASS to FAIL 2/2 purely from this). Record the final bed census (owners, sleepingSlots, pos) so a not-rescued verdict can be told apart as SITE.
- **Live northstar runner colonist traps on a debug map.** (1) A freshly spawned colonist can arrive downed or dead (old age, pre-existing hediffs): re-roll after a short step and check `list_pawns` before using it. (2) WorkGiver HasMaterial-style answers can be cached per pawn per tick, so step at least 1-2 ticks after spawning material before probing. (3) Never vanish the run's colonist in `finally`: vanishing the last colonist triggers Game Over and every later staging fails (GovernorStop).
- **A saved 'calm' test site can have EVERY colonist Mining-disabled**, including freshly spawned ones (ideo 'Cell of Faith': `disabledWorkTypes` includes Mining). Any dig or fill-in proof then silently gets no worker. Before a dig/fill live row read `jawa/flowworks_job_probe` `pawn.workTypeDisabled`, or use a fresh debug map (`newmap.py`).

## Clearing a site, and reading it back

`validation_core.prepare_site(B, rect, rows, rid)` destroys everything, lays Soil,
unfogs, removes the roof, reveals the area with a colonist's sight, then **reads back**
roof and things. Anything left in the rect gives `UNMEASURED/SITE` and returns False.

- **Giants on `RM_TheRot`.** Full-list quicktest maps on the current tile are RM_TheRot.
  Giant fungi with Huge Things footprints cover them: 5,000+ `RM_HugeTrunkBlocker`
  cells in 215 16-cell tiles on one map. `MapComponent_HugeFootprints` re-plans any
  blocker that vanishes while its plant stands (`Notify_BlockerGone`). That means a
  giant **outside** the rect re-blocks a site you cleared. →
  `validation_core.clear_huge_plants(B)` before every block. It removes every plant
  within 6 cells of a blocker, which is cheap on a test map.
- **Fog.** `jawa/set_fog unfog` did not stop "Can't place in undiscovered area" for
  designator-placed builds on the 550-mod list. A colonist standing there did
  (`validation_core.reveal`).
- **Geometry the mod enforces.** Sites need margin for the real operation. A hose reel
  needs room for its ~4.4-cell straight lead-out, so prepare 6 extra cells on the
  lead-out side. Aim a hose at the relay's real footprint cell (RL3 aims onto B's SW
  footprint cell), not at a cell beside it.
- **Water and source margin.** Before staging a pit or any dug site, check the whole
  footprint plus a 2-cell margin with `jawa/flowworks_excavation_rect` (`includeTerrain`)
  for `isSource` / water terrain. The 05 PIT_ACCESS deep pit (x106-108 z103-105) had a
  cell orthogonally beside river sources. It filled by gravity to f=1, which is correct
  FlowWorks behaviour, but the ladder-refusal row could no longer be attributed. A
  failed check exits 2 (`UNMEASURED/SITE <reason>`), never a PASS or a FAIL.
- **Blocks need disjoint sites**, and a block that tears down map-wide (the GSS matrix)
  runs first.
- **Hose reel staging.** Since a98046cbe9 the hose reel turns and a bare build op (`RM_HoseReel:x,z`) spawns it NORTH; a 2x2 built West shifts one square west (GenAdj). To keep an old layout build `RM_HoseReel:x+1,z,3` and look it up by a 2-wide rect (`list_things` filters by Position). Hose lay refusals can be reproduced offline with `HoseMath.CheckInstall/Lay` on a CordWorld (SelfTest `HoseBandChecks` `Scenario_C4_C10_hoses_lay_offline`) before spending a live build.
- **Drawbridge and suspension anchors carry no 'Choose style' gizmo once built** (`objects_sheet.choose_look` returns None); their look is fixed at build from the designator pick or `RM_MachinerySettings.pipeDefaultLook`. To stage a drawbridge in a look, set `pipeDefaultLook` via `jawa/mod_settings_field` before `ProofMakeDrawbridge` and restore it afterwards. `list_things` returns the cell under key `cell`, not x/z.
- **The hose probe verb `net:x,z` accepts only a liquid machine or tank cell.** On a reel cell it answers 'no liquid machine or tank there', so a coupling cannot be read from the reel end; ask `net:` on the fixture the hose couples to.
- **A pumping station (3x2 `Building_LiquidPump`) has ONE port, south, at the centre lane (ax, az-1).** A hose aimed at the lane's minX lays but does not couple. `owner_review_stage`'s `pipeN_hoseS` close frame also misses the pump.
- **Staging the 325 pipe-levelling perf site on the full list (no quicktest there).** Load a save with `rimworld/load_game_ready` (reports ready in seconds; poll `get_game_info` until `mapCount>0`), `jawa/world_tile_map_generate tile=96545 size 325` + `set_current_map`, spawn a player Colonist, run `validation_core.clear_huge_plants(B)` TWICE (the first pass hits the 5000-row list cap), THEN `pipe_levelling_perf_proof.py --no-time --lay 0:0` (30 s). Without the clear it reads SITE 'RM_HugeTrunkBlocker still standing'. Lays cost 13-18 s per rig (2 hoses). The generated faction Settlement leaves a world NRE loop that makes `belt_watchdog` read WEDGED; reload the save after dropping the map.
- **Every `--fresh-map` entry point must call `validation_core.clear_huge_plants` before `prepare_site`.** `suspension_bridge_proof.py --fresh-map` did not, so a giant plant read `SB_site_ready` UNMEASURED (`RM_HugeTrunkBlocker`); workaround: clear on the new map and rerun without `--fresh-map`. `clear_huge_plants` lists blockers with `limit=5000` and hit the cap (blockers=5000, 134 left) on a full-list fresh map. For crop-growth rows, `glow_tank_live` shows the plant inspect reads 'N% grown' as an INTEGER percent (not a 'Growth' prefix; 'Growth rate: 71%' is not growth) and `RM_CrowncarpetCultured` (growDays 12) gains ~0.6% per 6000 ticks, so run >= 30000 ticks.
- **Check a staged pit's whole footprint plus a 2-cell margin with `jawa/flowworks_excavation_rect` (includeTerrain) for `isSource`/Water terrain first.** A pit at x106-108 z103-105 beside river sources filled by gravity to f=1 (correct FlowWorks behaviour) and spoiled a ladder-refusal demo because the pawn might have refused for the water. Also `order_pawn` with a long `waitTicks` can hit the 30 s client timeout and leave the game UNPAUSED with the outcome unknown: use `waitTicks` of 600 or less, reconcile, then `pause_game`.
- **A live proof that stages a sun-fed table must read `jawa/shadegrid_read` on its cell before trusting 'full sun'.** On a pinned-sun map every building casts a directional shade strip up to 16 cells (`RM_MapComponent_ShadeGrid`), so a pad layout sunny for one table shades its neighbour. A proof naming a franchise-free recipe must check the loaded tier: Armoury's `RSW_Transparisteel_GlassFold.xml` removes `RM_MeltSunGlass`/`RM_MeltLensGlass`.

## Which world, which map

- **Use a bland world for the full list's quicktests.** The campaign world has no vanilla
  Desert or AridShrubland tile, so a quicktest map carries Sheen/Terminator-front fires
  and roof collapses. `--bland-world` uses `ZBiome_Grasslands`. Test lists drop
  `mlie.nwnrealfogofwar`: destroying map-gen ruins on a 2nd map makes RealFoW throw
  every Update, and `step_game_ticks` then fails on every map.
- **A map with no player pawn is culled.** A `jawa/world_tile_map_generate`'d map, or a
  generated side map with no colonist, is auto-culled once it stops being current, and
  culled on save. Found a player settlement (`colony_found`), or anchor with a colonist
  first, if the map must survive a sequence of calls.
- **Regenerate Current Map wipes the colonists.** Test on the home map and respawn
  colonists with `src/RimMandrake/bridgetools/spawn_test_colonists.py`.
- **Load saves from the main menu, once.** A paused site no-ops an `ordered_job`
  `waitTicks`. Keep `order_pawn` `waitTicks` ≤600, then reconcile and `pause_game`. A
  longer wait hits the 30 s client timeout and leaves the game unpaused. Advance with
  `B.ticks(n)` (safe_advance). A legacy direct `step_game_ticks` needs `timeoutMs`.
- **Prove a quicktest world reaches Playing:**
  `python.exe src/RimMandrake/bridgetools/prove_quicktest_world.py` (exit 0 = Playing
  with a world).
- **`sheet_overflow_proof.py --fresh-map` can land on a tile below 0 C outdoors** (`rimworld/start_debug_game_ready`: -1.54 C, seasonal 3.96 C). Row I `CROPS_IRRIGATE_THEN_DROWN` then reads UNMEASURED/SITE (rice at Ice/None, soak 0) and row K can freeze but never thaw: a SITE re-roll on another fresh map, not a mod verdict. The durable fix is a preflight outdoor-temperature read that records it and refuses or warms the site (HeatWave ramps over 12000 ticks) before rows that assume liquid water.

## Timing windows

- **Take the window from the design's contract, one half at a time.** On 2026-10-11 the
  NS_hose_carries_real_units row used a flat 260-tick window from the lay, which was
  shorter than the design's own contract. FINAL §3.6 says discover ≤ 60 ticks, then
  transfer by the NEXT 250-tick pump cycle, which is up to 310. In the same run the
  netLink was present at +260 with 0 units, and the hose plumped at +350. The fixed bar
  reads discovery (≤ 60, stepped 5), then units within one cycle (≤ 260) **of
  discovery**. Each half is stricter than the old window, not looser.
- **Wait for the precondition, then start the clock.** A freshly built powered consumer
  beside a just-charged battery reads `PowerOn=false` for ~100–170 ticks (measured
  140 / 100 / 170). Vanilla's power net switches it on later, not at spawn. The fix is
  `_powered()`, which waits for the pump, plus a recorded `pumpPoweredAfterTicks`.
  Any machine cycle timed from its build has the same trap.
- **To trace a mechanism the window says is broken, sample it in a throwaway
  diagnostic, never in the committed proof.** Re-staging on a spare plot and reading
  the machine every 10 ticks turned "relay chain carries nothing" into "the pump had no
  power yet". The chain itself worked. Today, step with `B.ticks(10)` in a scratch
  script. A per-window sampler is PLANNED (item CONDWATCH_BUILD_OWNED_RINGS, `B.watch`).
  What the trace teaches goes into the proof as a precondition wait or a bound, not as
  a poll loop (`lightspeed-authoring.md` §3).
- Tick-keyed caches, a stepper that overshoots short states, load-call races:
  `skills/rimbridge/references/traps.md`, "Bridge time is TICKS".
- **`rimworld/load_game` (and `load_game_ready`, which reports 'map data is available' with `state.longEventPending=true`) returns before the map's things are spawned.** A hook queried at once answers 'no eligible fixture', and a persistence row reads that as a LOST claim. Poll the subject until it exists before judging (the save held the claim and it came back seconds later).
- **A flat tick wait for a pawn job must scale with the pawn's work stat.** `fill_in_on` waited 2,500 ticks for a D=1 fill-in (1600 work), but a Mining-0 colonist sits at the MiningSpeed floor 0.1 (one notch = 16,000 ticks), so the row FAILed; the earlier PASS had drawn a skilled pawn. Read `jawa/pawn_stats` MiningSpeed and poll the cell depth (`northstar/extensions.py` `_fill_in_budget`/`_wait_filled_in`). A PASS that depends on which colonist the harness picked is not a PASS.

## A simplified model passes what the real operation refuses

An install precheck that judged a taut route with no nozzle lead-out
(`HoseMath.CheckInstall`) accepted orders that the real lay then refused, and the
colonist carried the hose out to nothing. An offline selftest that modelled the reel
as 1×1 with no outlet stayed green while 7 live rows went red. Where the real
operation's trial run is cheap, gate on that trial run. When a ruling changes the real
geometry, re-check every live scene built before it. For example, the owner refused a
straight lead-out on 2026-10-06 rather than lay it without one. See
`deciding-and-superseding`, "A stale belief hides…".
- **RimWorld 1.6 `PathFinder.FindPathNow(start, target, pawn)` passes NO path-grid customizer.** FlowWorks' swim and pit offset grids ride only the pather's own request (`RM_Patch_PathFollower_PitRoute` on `GenerateNewPathRequest`). A proof that compares `CanReach` with A* must call the TraverseParms overload with `RM_SwimPathing.Combine(pit, swim)`, or it reads a non-swimmer crossing deep water as found.
- **A FlowWorks sheet offer (`RM_MapComponent_Sheet.Offer` / `ProofSheetSpill`) at an UNDUG square reaches only that square and its 4 open neighbours:** `FindLips` walks through dug squares only. At the shipped 50 cm cap that is 50,000 dL, which made staging read 'accepted=50000' (a harness shortfall, not a mod refusal); re-offering at the same origin is refused once those 5 are full, so stage at several origins (`sheet_overflow_proof.spill_spread`). A mock whose lip walk covered 16 open squares hid it.
- **A proof mock that applies a condition map-wide cannot catch a row that checks the whole map instead of its own scene.** `sheet_overflow_proof`'s freeze set one global temperature so every scene froze and stopped soaking; live, other scenes kept soaking and `SHEET_FREEZES_AND_THAWS` failed on cells it never owned. Scope every row's check to its scene rect, make the mock local when the condition is local, and derive every kernel input from the same quantised integer a load will see (evaporation was computed from the raw float temperature while deci-C was rounded).

## Pre-port save fixtures (old build, mid-job)

Use these when a port moves a class, job driver or def between mods, renames a type,
or changes what a save holds. They prove that a player's existing save survives.

1. **Before deploying the port**, with the OLD build loaded, back up the keepers
   (`CANONICAL_ASHKARR_START`, `BLAND_NORTHSTAR_BASE`, `ASHKARR_*`, `FOUNDER_*`, …), then
   stat every file in Saves.
2. **Stage the job and save it mid-flight.** Name it so it reads as a fixture:
   `RM_PREPORT_<THING>_MID<JOB>_<date>.rws`. Record the state at the save: the job,
   the toil, the carrier, the order, and the old class names that appear in the save
   (`grep` the class with `<def>`-style care; see `rimworld-savegame`).
3. **Make sure the job outlives your read.** On the full list "Out of Combat ReBoost"
   walks a colonist at ~2 ticks/cell, so a 24-cell carry finishes inside the proof's
   60 post-load ticks. Slow the carrier with BadBack + Frail (`jawa/pawn_health`),
   which gives ~8 ticks/cell and ~180 ticks of carry after the save point. Mud and
   shallow water did not help, because the path avoided them.
4. **Stat-diff Saves**: exactly the new files, 0 changed. `rimworld/save_game` has written
   the current slot instead of `saveName` before.
5. **After the port**: `proof_hose.py --live --preport-save NAME1,NAME2`. PASS needs all
   of these: the load completes (17–28 s), no "Cleaning up invalid job state", no
   unresolved class, and the colonist is **still on the job 60 ticks after load**
   (the old driver class aliased onto the new mod).
6. **Keep the fixtures** in Saves until the owner says delete. They are the regression
   test for the next port.
- **A save made on a smaller mod list does not load clean on a superset.** `<compressedThingMapDeflate>` holds list-bound ThingDef shortHashes: on the full list one fixture lost 1704 chunks (a mod removing `saveCompressible` makes a missing stackCount read 0) and 34 uranium cells (a hash taken by another def). Expand a fixture with `src/RimMandrake/Utils/modcheck/save_uncompress.py`; a compressible new occupant of a hash would spawn the wrong thing with no log line.
- **Split a save/load divergence by saving once and continuing three times: live (A), after one load (B), after a second load (C).** B==C with A!=B proves the live run holds state the save drops (or the load re-derives differently); B!=C proves post-load nondeterminism. A row that judges 'kept while frozen' from map-wide ledger deltas is contaminated by other rows' water; scope it to the rect.
- **A save/load-identical proof on a FRESH world has two vanilla traps.** (1) `Game.LoadGame` with `Prefs.PauseOnLoad` runs one `DoSingleTick` after load (rw16 `Verse/Game.cs:638`), so the loaded arm is +1 tick: compare both arms at the same `TicksGame`. (2) `SurfaceLayer` saves each tile's base temperature as `ushort RoundToInt((t+300)*10)` (`SurfaceLayer.cs:102,220`): a never-saved world keeps the finer float, so `OutdoorTemperatureAt(tile, absTick)` reads ~0.03 C different live vs loaded. Only the first save/load of a world shows it, so reruns on one map hide it; test on `--fresh-map`, and emit the raw reading, not its hash.
- **A registered test-site save can be a dead fixture while its registry reads `loadVerified True`.** `RM_TestSite_contagion_v1` carried `sarg.alphabiomes` + `vfe.insectoid2` in its `<modIds>` header (retired donors that killed `leaningscrub_v1` in FinalizeLoading). Read the save header against `retired_mods.json` (`Contagion/prep_site.header_problems`) before trusting a site; `biome_site.build_site_save` now refuses to build while a retired donor runs. A save's mod header only ages: every retirement from the full list adds a mod the bridge's `save.missing_mods` check refuses forever, so `live_site` loads past mods off `ModsConfig.FULL.LATEST.xml`; a load on such a save still logs Scribe errors for their classes and defs, which a log-budget proof must expect.
- **`BENCH_r17_midrain` (saved on the 321-mod full list) does NOT load on the FlowWorks live-mods list:** Player.log shows `NullReferenceException at RimWorld.Planet.WorldGrid.CreateRequiredLayers <- GenerateFreshWorld <- WorldGenerator.GenerateWithoutWorldData <- World.ExposeData` and the game drops to the menu; `ignoreModCompatibility` skips the pre-check, not the load's own failure. Proofs sited on it (`LEVEL_ALLOC_SHRINK_EIGHTFOLD_OVER_BAR`, `PERF_SCENE_REMEASURE_BASINS_OFF_EDGE`) cannot be read at links >= 100 on any list (every reading on r17 peaks at links=50): stage a fresh scene with `live_site.py --game --stage-with FlowWorks`. Read Player.log's first exception after 'Loading game from file <save>' before blaming the harness.

## A generated map is culled unless it is home
- **A map from `jawa/world_tile_map_generate` is culled as soon as time advances unless living player colonists stand on it.** Settlement maps spawn hostile pawns AND turrets that down the colonists (sweep `list_things group=BuildingArtificial` by faction, not just `list_pawns`), and downed or dead colonists un-home the map; the cull is silent and the current map just switches. Right after generating: run `jawa/map_commit {redraw:true, full:true}` (mapgen leaves the region updater disabled, so destroyed plants and changed terrain render as phantoms), spawn 2-3 colonists away from the settlement and kill every hostile pawn and turret, and keep the game paused except when deliberately stepping.
