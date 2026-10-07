# L2 failure triage, 2026-10-07 (FOUNDRY helper, offline only)

Source runs (`Transient/modcheck/`): LeaningScrub_20261007T104321Z, WeepingStones_20261007T100921Z,
Greentide_20261007T095739Z, Stillsand_20261007T094214Z, CreatureBehaviors_20261007T095254Z.
Minimal list + biomes + GSS; game left up; no bridge used for this triage.

Classes: SCRIPT (test-setup fault / stale expectation), MOD (real defect in our code/defs),
DONOR (minimal-list difference), HARNESS (bridge/runner), LIVE? (needs a bridge retry to decide).

## (a) LeaningScrub — 9 FAIL
**Verdict:** 6 SCRIPT/HARNESS fixed (Grellspine PollutedOnly, campfire IsFull, unowned turbine, lash ambient hediffs, 2x Ultrafast clock stall); 3 LIVE? instrumented and filed (stall shared move, crown mob, sweetline shed). No MOD defect proven.

### patches.dead_venomvine_fuels_fire
**SCRIPT.** Evidence: ordered_job Refuel -> `afterJobDef Wait_MaintainPosture`; campfire inspect `Fuel: 19 / 20` after ~3900 ticks. Engine: CompRefuelable.IsFull = TargetFuelLevel - fuel < 1 (CompRefuelable.cs:63); JobDriver_Refuel.MakeNewToils AddEndCondition(IsFull -> Succeeded). Campfire capacity 20, initialFuelPercent 1, 10/day => the 3000-tick pre-burn removed 0.5 fuel, so the job ended before taking any. The existing script comment's arithmetic ("burn ~1 fuel") was wrong. Patch xpath matches Core Campfire's `comps/li[@Class=CompProperties_Refuelable]/fuelFilter/thingDefs[li=WoodLog]` (read from decompiled Buildings_Temperature.xml).
Action: pre-burn 10000 ticks (~1.67 fuel) and an UNMEASURED guard if the inspect gap is < 2 before ordering the refuel; RULED OUT comment ("patch does not apply"). selftest fake now models fuel burn + IsFull refusal. Whether the patch applies is still unproven live; the next run decides it.
### flora.flora_spawns (RM_Grellspine)
**SCRIPT.** Evidence: set_plants for RM_Grellspine answered `Planted 0, REJECTED 1: terrain or conditions cannot support` (all 17 others planted 1); it never stood, it was never planted. RM_LeaningScrubVanillaReplacements.xml:172 `<pollution>PollutedOnly</pollution>` (vanilla grayscrub rule, description says so); engine PlantUtility.CanEverPlantAt returns false for PollutedOnly on a !IsPolluted cell; JawaBenchTerrainTools.cs:1378 calls it. Pad is clean Soil.
Action: validation.py parses PollutedOnly plants (POLLUTED_ONLY) and calls `jawa/set_pollution` on that plant's cell before set_plants (UNMEASURED if the cell is not pollutable); finally cleans pad pollution. RULED OUT comments: fertility, temperature, post-spawn death. selftest fake now models CanEverPlantAt + new break `no_pollute` -> flora.flora_spawns. Selftest 68/68, 57 breaks.
Side note (not a fail): a PollutedOnly plant in RM_LeaningScrub wildPlants (0.3) only appears on polluted cells, i.e. almost never on a clean scrub map -- design question for the biome sheet, not filed.
### stall.stall_freezes_small
**SCRIPT (predicate) + LIVE? (what moved them).** Evidence: in BOTH runs (101652Z, 104321Z) both animals made the same vector move to the same cells, (77,80)->(89,92)->(90,95) and (83,80)->(94,92), all within the first 250 ticks, then BOTH held still for >=1000 ticks, including the 0.7 control (bodySize read 0.4/0.7, both adult). A cross-run deterministic shared move is not JobGiver_Wander. Wander_Prefix (RM_WindCalendar.cs:170-188) replaces only the wander answer, by design ("fleeing, eating, sleeping... untouched"), so the old path-only predicate counted out-of-scope moves, and the control's ">=3 cells" arm was met by that same shared move, not by wandering.
Action: `_path` now samples `jawa/site_state` jobs each step (12x125 ticks). FAIL if the small animal ever holds GotoWander, or if it moved >1.5 cells with only wander-family jobs. UNMEASURED if the control neither moved nor wandered. Otherwise it notes the non-wander job. RULED OUT comments: juvenile control, weather lock, crown mob/fire stamp. Fake models GotoWander/Wait_Wander; `no_freeze` still goes red.
Proposed item LEANINGSCRUB_STALL_SHARED_MOVE_1 (--needs bridge): repro = stall pad (anchor-45,-45), lock RM_Stall, spawn RM_Thornhold at (x-3,z) and RM_Shirrel at (x+3,z) faction none, read `jawa/site_state` job + list_pawns x/z every 25 ticks for 300 ticks. The quantity is the job def during the (+12,+12) move. Suspects: JobGiver_AnimalFlee from an AlwaysFlee thing within 18, or the Lean scent flee if this map's biome carries RM_LeanExtension (one heading per map would explain the identical vector).
### gale.gale_turbine_breakdown
**SCRIPT.** Evidence: list_things row for WindTurbine352847 has `faction: null` (spawn_batch spawns unowned). RM_WindCalendar.cs:108 RollTurbineBreakdowns iterates `map.listerBuildings.allBuildingsColonist`, so an unowned turbine is never rolled. At MTB 0.01 d (600 ticks) over a 2500-tick check, each roll is ~98%.
Action: after spawning, `jawa/set_thing_props faction=PlayerColony` (UNMEASURED unless `changed` holds faction), plus a RULED OUT comment. Fake breaks only player turbines; `no_breakdown` still goes red. (Surge arm PASSed: 4485/3450 = 1.30.)
### lash.lash_toggle_off_quiet
**SCRIPT.** Evidence: the 2 hediffs gained in the 300-tick OFF window were `Heatstroke` and `RM_GlareBlind` (both `part: null`, ambient from the hot map plus CreatureBehaviors' glare); stand inspect `Mature.` with no lash state. The lash is RM_CompLash -> `victim.TakeDamage(RM_VenomvineScratch)` (RM_TwitcherLash.cs:68-72), which leaves a part-bound injury plus additionalHediffs `RM_VenomvineVenom` (EnvironmentalHazards RM_Damages_ContactVenom.xml:31-36).
Action: new `_lash_marks()` counts only part-bound injuries + RM_VenomvineVenom; used by lash_toggle_off_quiet and lash_strikes_once (same flaw). RULED OUT comment. The fake now gives colonists ambient part-less Heatstroke, so the old bare count would go red; healthy PASS.
### smother.smother_off_holds_claims
**HARNESS** (worked around in script). Evidence: both runs fail identically at `_wait(9000)`. That is the only call on validation.py's Ultrafast-poll path (`rimworld/set_time_speed Ultrafast` + `_ticks()` poll); the clock did not move for 60 s, while every stepped `step_game_ticks` wait in the same run advanced. Census of Transient/modcheck/*.json (47 files): 0 successful "_wait(..) at Ultrafast" records, 2 stalls (both these runs). The OFF arm only flips a static bool before the wait, so it cannot pause the game.
Action: after 30 s with no clock progress, `_wait` notes it and falls through to the existing stepped `t.wait_ticks(remaining)` instead of raising. RULED OUT comment. The same Ultrafast helper is copied in Contagion, Cauldron, ExplosiveGrowth, Greentide, BlueDesert, Pyrelands. Proposed item MODCHECK_ULTRAFAST_CLOCK_STALL_1 (--needs bridge): repro = game Playing and paused, `rimworld/set_time_speed speed=Ultrafast`, poll `_ticks()` for 10 s. Read whether TicksGame moves, and if not, whether TickManager.Paused is forced (a forcePause window open; `jawa/` window list) or the unfocused window drops Update.
### crown.crown_mob_gathers
**LIVE?** (instrumented). Evidence, both runs: the dustflutters spawned ~16 cells off and ended 23-70 cells away in the OFF arm (PASS) and the ON arm (FAIL) alike, so they ranged far whatever the toggle. The weather read RM_Stall. RM_MapComponent_CrownMob (RM_VenomvineRooms.cs:98-185) claims only IDLE mobbers (job null/Wait_Wander/GotoWander/Wait) every 250 ticks within drawRadius 40. A flutter held in another job (likely a flee, same family as the stall chain's shared move) is out of the mechanism's scope. Core AlwaysFlee things: Tornado, TunnelHiveSpawner, PawnGroundSpawner; ours: RM_SteamDevil, RM_SandBusterMound, RM_DuneGale.
Action: the trial samples `site_state` jobs 6x250 ticks and notes them; the ON arm reads UNMEASURED (not FAIL) when no flutter was ever idle or Goto. It still FAILs when they were idle and did not gather. `no_crown` still goes red.
Proposed item LEANINGSCRUB_CROWN_MOB_LIVE_1 (--needs bridge): repro = crown pad (anchor-45,+45), lock RM_Stall, RM_CrownVenomvine at the anchor, 3 RM_Dustflutter at (x+16+i, z+4-4i), read site_state jobs every 50 ticks for 500 ticks plus `list_things` of AlwaysFlee defs within 18. The quantities are the job defs and whether any becomes Goto toward the stand.
### bloom.bloom_toggle_off_quiet
**HARNESS** (worked around in script). Evidence: in both runs the 30.0 s RimBridgeError fires on the call after the walker's pawn_need, which is `jawa/order_pawn waitTicks=60`. That tool (JawaBenchTerrainTools.cs:2992ff) unpauses to Normal and polls the REAL clock with a 30 s wall-clock ceiling (`timeoutSeconds` default 30), so it ties with the client's 30.0 s timeout. Same session symptom as smother: a speed-set never advanced TicksGame, while stepped waits did.
Action: `order_pawn ... waitTicks=0, unpause=False` (issue only); the existing stepped 16x30-tick loop moves the walker. RULED OUT comment (OFF arm hanging the game: the timeout precedes any bloom tick). Selftest green.
Unexplained, not the failing cause: run 2's fuzz strip planted 75 and rejected 75 ("cannot support RM_Fuzz") where run 1 planted 150. RM_Fuzz gates only on fertilityMin 0.25. clearFirst already defaults true, so the "blocked by old plants" theory is ruled out (I tried it and reverted). Folded into MODCHECK_ULTRAFAST_CLOCK_STALL_1's session check: read `jawa/get_terrain` / fertility over (x-15..x+14, z-2..z+2) of the bloom pad.
### sweetline.station_sheds_wool
**LIVE?** (instrumented). Evidence, both runs: the tree was mature ("Ready to harvest") with its timer 14 h / 3.7 d out. After a +5.5-day `time_set_ticks` and a 2100-tick stepped wait, 0 RM_SweetlineWool sat in the pad. Code read: RM_CompSweetlineStation.CompTickLong (RM_SweetlineStation.cs:145-169) sheds woolCount 5 of RM_SweetlineWool Near the trunk once now >= nextWoolTick and Mature; def woolThing = RM_SweetlineWool (RM_SweetlineTree.xml:72). Engine: Plant.TickLong calls base.TickLong (comps); TickList Long buckets every thing once per 2000 consecutive ticks. The offline path is sound and the fake passes. Player.log for the run is already overwritten (Player-prev.log 03:52 has no LeaningScrub lines). A comp earlier in the tree's comp list throwing in CompTickLong would abort the loop, and log_clean's "LeaningScrub" filter might miss that stack (the thing reads RM_SweetlineTree, frames read Plant.TickLong). Unproven.
Action: after the wait the check reads the tree. "ready to fall" = the shed never ran, "falls in ~5 d" = it ran and the felt is elsewhere, tree gone = died. That goes into the note and the FAIL text. RULED OUT comment (Plant.TickLong skipping comps).
Proposed item LEANINGSCRUB_SWEETLINE_SHED_LIVE_1 (--needs bridge): repro = sweetline pad (anchor+45,+45), set_plants RM_SweetlineTree growth 1, time_set_ticks +5.5 d, step 2100. Read the tree inspect wool line, `list_things RM_SweetlineWool` map-wide (no rect), and `drain_log errorsOnly` filtered on "Exception ticking".

## (b) WeepingStones — 7 FAIL
**Verdict:** all 7 LIVE? — one cause: every chain-spawned pawn left the map during forced jobs. Script now goes UNMEASURED (also kills 2 false PASSes). Filed WEEPINGSTONES_HANDLER_VANISHES_1. Prime suspect (helper's note): live hostile insects that jawa/destroy_batch cannot remove (JAWABENCH_DESTROY_PAWNS_1, from Greentide).

**One root cause covers all 7 failures: LIVE?.** In every job and flora chain, every pawn the chain spawned (the handler colonist and the target) had left `map.mapPawns.AllPawnsSpawned` by the time of the check. The evidence: list_pawns `totalOnMap` reads 13 before the job and 11 after (job_net/harvest/cull). It reads 12 before and 11 after in job_stock. The remaining 11 are the map's own pre-existing colonists. list_things `pawnsSkipped` falls by the same count (flora: 15 -> 14). Every spawn/precondition read passed (site_ready_* PASS), so this is not a counting or defName mismatch: the pawns really are gone. `totalOnMap` is `AllPawnsSpawned.Count` (JawaBenchTerrainTools.cs:1219), so the pawns died or were despawned. They did not just walk out of the rect. Nothing in our C# removes the handler. The only Destroy/Kill calls hit the target or carried item (NetPoolBreeder.cs:70, HarvestPoolPen.cs:57, CullVhorrin.cs:66, StockPoolPen.cs:66) or pen residents (PoolStock.cs:343/388/418, which need RM fauna inside a pen). The flora chains use vanilla `Harvest` and no mod code, and they fail the same way. **Why it can't be decided offline:** the Player.log for that run was overwritten by a restart (the current log is from 03:42 local, the run was 02:57–03:09), and `includeCorpses` was never passed, so "died" and "despawned" can't be told apart.

Corollary: **job_feed and job_stock_outside_pen PASSED on the same disappearance, so both are false passes.** Their predicate only checks that the item is gone from the ground. Once the carrier is gone too, that proves nothing.

Same-session control: LeaningScrub ran next on the same Map_8. Its colonists that had no ordered job survived their waits (gale/lash, totalOnMap 13). But `dripping_survives_harvest` (a forced vanilla Harvest) also produced no yield. So the trigger looks tied to pawns working under a forced job, or to the area, and not to our mod.

Action (all chains): added `_fate()` and `_need_handler()` to validation.py. After each wait they read list_pawns(includeCorpses, includeHealth) across the whole map. If the handler is not alive and spawned, the component goes UNMEASURED with the fate as evidence. This applies to NET/STOCK/STOCK-outside/FEED/HARVEST/CULL/flora. A predicate that presumes a live handler measures nothing without one, so this does not make any check easier to pass. selftest: mock list_pawns now returns the live row shape (spawned/dead/downed). A new break, `handler_vanishes`, asserts that every job/flora proof goes UNMEASURED and none read PASS or FAIL.

Proposed item: **WEEPINGSTONES_HANDLER_VANISHES_1** (--needs bridge). Repro on the minimal list, quicktest map. Pad at map centre +45. Spawn a Colonist at (anchor.x+8, anchor.z) and set needs full, undrafted. Spawn RM_Skarrin at (+6,+5). Order RM_NetPoolBreeder. Then step 100 ticks at a time up to 900, and each step read `jawa/list_pawns includeCorpses=true includeHealth=true` for both ids plus the Player.log tail. Read three things: the tick the handler leaves AllPawnsSpawned, dead vs despawned, and the last job/hediff. Control: the same spawn with no ordered job (expect it to survive), and the same order on a pad away from (156..184,156..184). The map at the start of the run held a hostile Insect group (3 Megascarab, a Spelopede and a Locust at ~(175,122), about 45 cells south of the pad) and one downed colonist. destroy_bulk removes the insects but not any hive building, so check `jawa/list_things` for a Hive near (175,122).

### job_net.net_turns_wild_pawn_into_breeding_stock
LIVE? (handler and wild target both gone from AllPawnsSpawned, 13->11). No stock item appeared, so the net never finished. The stale docstring claim that "the skarrin flees off-map" is fixed in the driver (RM_PoolBreederUtility.HoldStill stun, RM_JobDriver_NetPoolBreeder.cs hold toil). That docstring was replaced with a RULED OUT note. Action: `_need_handler` guard.

### job_stock.stock_releases_species_pawn_into_pen
LIVE? (handler gone, 12->11, with the carried stock; no skarrin released). Driver logic checked and correct (StockPoolPen.cs:45-74). Action: guard.

### job_harvest.harvest_yields_species_meat
LIVE? (handler and skarrin gone, 13->11). The meat def is looked up as kindDef+"Meat" = RM_SkarrinMeat, and the check counts exactly that def. Action: guard.

### job_cull.cull_yields_enormous_harvest
LIVE? (handler and vhorrin gone, 13->11). Same shape as job_harvest. Action: guard.

### flora_RM_Bladderquill.harvest_yields_RM_BladderFruit
LIVE? (handler gone, pawnsSkipped 15->14). RULED OUT a missing designation: `Harvest` = JobDriver_PlantHarvest, whose RequiredDesignation is null (only HarvestDesignated needs one; RimSage JobDriver_PlantWork.MakeNewToils / Jobs_Work.xml:483). RULED OUT growth below harvestMinGrowth: set_plants returned growth 1.0, and harvestAfterGrowth is only the regrowth point. The yield is placed by GenPlace at actor.Position, which is inside the pad. Def wiring is fine (harvestedThingDef/harvestYield 7). Action: guard plus RULED OUT comments.

### flora_RM_Steamfrond.harvest_yields_RM_SeepSalt
LIVE? Same as Bladderquill (harvestYield 3, harvestWork 260).

### flora_RM_Dewgourd.harvest_yields_RM_DewgourdFruit
LIVE? Same as Bladderquill (harvestYield 14, harvestWork 400).

## (c) Greentide — 4 FAIL
**Verdict:** 3 SCRIPT fixed (alias def type namespace, re-mire threshold, vurrak step cell occupied); 1 MOD fixed: MudSwallow `ParentHolder != null` guard skipped every spawned thing (Map.spawnedThings is a ThingOwner owned by the map; RimSage-verified). DLL rebuilt, not deployed; MUDSWALLOW_PARENTHOLDER_GUARD_1 for live verify.

### defs_resolve.shipped_defs_resolve — RM_DefAliasDef/RM_GreentideTierMoveAliases not found
- **Class: SCRIPT.** The def is not discarded, and EnvironmentalHazards is present (a hard dependency). The bridge row says `"No def TYPE named 'RM_DefAliasDef'"`: it failed on the type lookup, not on the def.
- Proof: `shipped_defs()` sent `e.tag.split(".")[-1]`, which strips `RimMandrake.EnvironmentalHazards.` from `Defs/Misc/RM_GreentideTierMove_Aliases.xml`. jawa/get_defs (`JawaBenchTerrainTools.cs`) only tries `GenTypes.GetTypeInAnyAssembly(name | "RimWorld."+name | "Verse."+name)`.
- Action: `validation.py` `shipped_defs()` now returns the full tag. Vanilla tags have no dot, so they are unchanged. The spine and selftest comparisons are unaffected. RULED OUT comment added.

### mire_escalation.free_mired_job_pulls_the_pawn_out
- **Class: SCRIPT** (the predicate was wrong). The driver works.
- Proof: in the live JSON, stuck pawn Human331838 went 1.0 → 0.524 at the first poll, then rose about +0.032 per 250 ticks (4 checks × 0.008). That is a FRESH hediff, so RemoveHediff ran (HediffDef default initialSeverity is 0.5). The freed pawn still stands on churnmud, and `RM_MapComponent_TerrainMire.ProcessPawn` re-adds RM_Mired within 60 ticks. A 250-tick poll that checks for "absent" can never see the gap.
- Action: the predicate is now "RM_Mired < 0.85 (no longer stuck)". It still discriminates: a stuck pawn left alone drops only 0.008 on a 1.5% roll per check, so it cannot fall from ≥0.95 to below 0.85 within 1500 ticks. RULED OUT comment added.

### swallow.swallow_buries_on_churnmud_only
- **Class: MOD** (real defect: the swallow can never fire).
- Proof: `RM_MapComponent_MudSwallow.cs:73` has `if (thing == null || !thing.Spawned || thing.ParentHolder != null) continue;`. In the engine, `Thing.ParentHolder => holdingOwner?.Owner` (Thing.cs:388). `Thing.SpawnSetup` does `map.spawnedThings.TryAdd(this)` (Thing.cs:832), and `map.spawnedThings` is a `ThingOwner<Thing>(map)` (Map.cs:512). `ThingOwner<T>.TryAdd` sets `item.holdingOwner = this` (ThingOwner.cs:193). So ParentHolder is the Map for every spawned thing, and every haulable is skipped.
- RULED OUT: the wait did not advance. `_wait` clocked 231133 → 234333 (3200 ticks), and swallowTicks is still 2500.
- Proposed C# fix (not applied): at `RM_MapComponent_MudSwallow.cs:73`, change the guard to `if (thing == null || !thing.Spawned) continue;`. Spawned already means it is loose on the map. Rebuild with winbuild.py.
- Proposed item **MUDSWALLOW_PARENTHOLDER_GUARD_1** (`--needs bridge`). Repro: rerun the swallow chain. Steel x5 on RM_GreentideChurnmud at anchor (−8,−6), wait 3200 ticks, `list_things` Steel there should return 0, and a RM_DesignationDigOutBuried should be on the cell. The concrete and sealed Steel should remain.
- This is the only `ParentHolder != null` guard in src.

### vurrak.vurrak_hare_only_reveals
- **Class: SCRIPT** (test setup).
- Proof: the result `STRUCK Human331817` names a leftover colonist from the mire chain, not the hare. It was last seen at (125,125), the anchor, during frenzy_dose. `CheckContact` reads every pawn on the vurrak's cell, and the hare step used (x,z) = the anchor. clear_area leaves pawns alone.
- Second finding: `jawa/destroy_batch` never destroys pawns, even with `categories="Pawn"` (JawaBenchTerrainTools.cs: `if (thing is Pawn ...) { skippedPawns++; continue; }`). So `_clear_hostiles` is inert. Every call answered "1 pawn(s) left alone", and the hostile Megascarab331787 wounded the escalation helper (Scratch/Stab). Cauldron's `kill_pawns()` uses the same inert call.
- Action: the vurrak chain now picks its 3 step cells from bank cells (row z, x−5..x+5) that no pawn occupies, based on one list_pawns read. The chain advances no ticks. `_clear_hostiles` is annotated as inert. RULED OUT comment added (hare body size crossing the threshold).
- Proposed item **JAWABENCH_DESTROY_PAWNS_1**: give destroy_batch an opt-in pawn removal (or add a jawa/destroy_pawn), then fix `_clear_hostiles` and Cauldron `kill_pawns`.

### L0
- `selftest_greentide_spine.py`: all passed.
- `shipped_defs()` gives 118 defs; only the alias def carries a namespace.
- `run_selftests.py`: 221/222. The only failure is selftest_utinnipatches_dump, a known environment failure.

## (d) Stillsand — 5 FAIL
**Verdict:** 4 SCRIPT (stale 2000-tick shade grid read right after clearing a roofed pad; NOT night — the Stillsand sun is pinned) + 1 MOD (RM_LoommaSunstruck removed at severity 0 and never re-added; minSeverity set). Horizon: LIVE?, vanilla control also refused (HORIZON_CARAVAN_VANILLA_REFUSES_1).

Common root of the four sun FAILs (and of the glare_site_ready UNMEASURED): **stale shade grid, not night.**
- The Stillsand sun is pinned: sun_pinned_no_night PASS, skyGlow 1.0 even 12 h later. `RM_SunPower.Intensity` (Stillsand/Source/RM_SunPowered.cs:139-156) reads the pinned elevation (54.8 deg -> sin = 0.817 = the "82% on a fresh map"). It never reads the clock. The time-of-day theory is ruled out.
- `RM_MapComponent_ShadeGrid.Recompute` (CreatureBehaviors/Source/RM_MapComponent_ShadeGrid.cs:332) runs only when `TicksGame % 2000 == 0`. It has no dirty events. `_prep` clears rock and strips roof on a Mountainous-tile map, then each chain reads at once, so the grid still holds the pad's old shade (1.0).
- The glare pad (215,80) read shade 1.0 / exposure 0.0 straight after prep at tick 202091. The sun pad (125,170) was open ground to begin with and read 1.0.

### loomma.loomma_sunstruck_open_vs_roofed
SCRIPT (stale grid) + MOD (one-shot clock).
- Proof: the hediffs list at tick 47231 has no RM_LoommaSunstruck on any loomma. startingHediffs IS applied (PawnGenerator.cs:1269) at 0.03.
- In shade the hediff drops by 20/day, i.e. -0.067 per 200-tick interval (HediffComp_SeverityModifierBase). The pad was prepped at 45731 and the grid only rebuilt at 46000, so the first interval ran in stale shade and took the severity to 0. `Hediff.ShouldRemove` (Severity <= 0) then removed it, and nothing in our code re-adds it (grep: no AddHediff anywhere).
- Action, validation.py:
  - Added a `_settle_shade` helper that steps past the next grid rebuild.
  - The loomma chain now sets its roofs, settles the grid, then spawns.
  - Wait cut from 1500 to 600 ticks: at +40/day the 0.03 start reaches lethal 1.0 in ~1455 ticks, so a 1500-tick read would find corpses.
- Def fix: added `<minSeverity>0.001</minSeverity>` to RM_LoommaSunstruck in Defs/ThingDefs_Races/RM_Stillsand_Fillout.xml. The Hediff.Severity setter clamps to def.minSeverity, so the clock can no longer be deleted. Not deployed.

### glass.sun_table_reads_sun_in_open
SCRIPT (stale grid).
- Proof: the line reads "in shade (sun 0%)". `FactorAt` writes that only when Intensity > 0 and the cached ShadeAt >= 0.5. Night would have read "no sun".
- The cell was not roofed: `Roofed()` is checked live, first.
- Prep and the read both happened at tick 50231, and the last rebuild was at 50000.
- Action: `_settle_shade` at the end of glass_site_ready, after the spawns and the roof.

### glass.furnace_work_speed_tracks_sun
SCRIPT (downstream of the above).
- Proof: the stat patch is applied. thing_stats lists RM_StatPart_SunPowered among the statParts, which rules out "patch matched nothing".
- The 0.10 comes from the WorkTableWorkSpeedFactor StatDef's `minValue 0.1` (RimSage) clamping max(0.05, sun 0). That is why open, roofed and the x2 case all read 0.10.
- Fixed by the same settle.

### glass.sun_work_speed_multiplier_scales
SCRIPT (same clamp: 0.05 x 2 = 0.10, which reads the same as 0.10). Fixed by the same settle.
- The three toggle_off UNMEASUREDs (no "Sun: NN%") are the same stale read.

### horizon.horizon_warns_then_arrives
LIVE? (vanilla refuses). The queue claim is unproven.
- Proof the queue path is sound: `IncidentQueue.IncidentQueueTick` runs every tick (TickManager.DoSingleTick -> StorytellerTick) and calls `TryFire(queued: true)`, which our prefix passes through (RM_HorizonWarning.cs, TryFirePrefix).
- The vanilla arm in the same run (horizon_toggle_off_vanilla, toggle off, no queue, no prefix) also failed: `canFireNow true, fired false` at tick 212246. So vanilla `TryExecute` refuses TraderCaravanArrival on this site.
- Likely refusal points:
  - IncidentWorker_NeutralGroup.TryResolveParmsGeneral: no faction found.
  - IncidentWorker_TraderCaravanArrival: no traderKind by commonality.
  - GeneratePawns returns 0 (it runs with warnOnZeroResults false, so this is silent).
  - TryFindRandomSpotJustOutsideColony fails.
- No caravan pawns and no arrival letter appeared, so the refusal comes before SpawnPawns or inside it.
- Action, validation.py: on no arrival, the check now reads `jawa/incident_queue_peek`, then fires a vanilla control with the toggle off. If vanilla also refuses the result is UNMEASURED (not FAIL). If vanilla fires, it is a real FAIL that names the queue rows.
- Proposed item: `HORIZON_CARAVAN_VANILLA_REFUSES_1` (--needs bridge).
  - Repro: on the regenerated Stillsand site, set `horizonWarningsEnabled=false` and run `jawa/storyteller_fire incidentDef=TraderCaravanArrival`.
  - Read: `jawa/list_factions` (non-hostile factions with a Trader pawnGroupMaker and caravanTraderKinds), `jawa/incident_parms_preview incident=TraderCaravanArrival` (faction), and the Player.log around the fire.
  - Decides between DONOR (minimal-list factions or pawnkinds missing) and HARNESS (site/world has no trader faction).

### Proposed C# (not done; offline-only brief)
None needed for these FAILs.
- Optional: `RM_MapComponent_ShadeGrid` could set `recomputeRequested` on roof or building changes, so player digs do not read stale for up to 2000 ticks.
- That is a design choice. The class doc says the staleness is deliberate ("zero event-wiring risk").

### L0
- validation.py compiles.
- selftest_stillsand: 106/106 healthy, and all 66 breaks turn their own component red.
- The Fillout XML parses; validate_patch reports 0 errors.
- run_selftests: 221/222. The one failure is utinnipatches_dump, the known environment failure.

## (e) CreatureBehaviors — 1 FAIL (A3 invisible walker)
**Verdict:** SCRIPT. Bare PsychicInvisibility self-expires next HealthTick (no disappearsAfterTicks), so the walker was never invisible; now RM_SandSubmerged. Recorder correct. Never passed before, so not a regression.

### track_grid.invisible_walker_recorded_flagged
- **Class: SCRIPT.** It never passed, so this is not a prior-pass-now-fail. The 2026-10-07 runs went 094245Z UNMEASURED (diag read error), 094550Z FAIL 4, 094924Z FAIL 0, 095254Z FAIL 0.
- **Recorder:** `Source/RM_MapComponent_TrackGrid.cs:102` sets `invisible = pawn.IsPsychologicallyInvisible()`. Per RimSage, `InvisibilityUtility` returns true when any hediff has a `HediffComp_Invisibility` that is not `PsychologicallyVisible`. The postfix on `Pawn_FilthTracker.Notify_EnteredNewCell` has no visibility filter, so the C# is correct.
- **Script:** it added `PsychicInvisibility` with `jawa/pawn_health add`. That def's `HediffCompProperties_Disappears` sets no `disappearsAfterTicks`, so `IntRange(0,0)` gives `ticksToDisappear` 0. `HediffComp_Disappears.CompShouldRemove` is then true, and `Pawn_HealthTracker.HealthTick` removes the hediff on its next pass. Only the psycast calls `SetDuration`. The pawn_health call reporting success therefore proves nothing.
- **Live proof (095254Z):** the walker `Human276027` laid an UNFLAGGED print at 120,128 during the 300-tick pre-walk wait, with `lastPrintPawn` naming it and `lastPrintInvisible` False. It then laid 7 more unflagged prints on the walk (`printsWritten` 2038→2045, `lastPrintCell` 136,125). Prints ARE recorded for the pawn, just never flagged, because the hediff was already gone.
- **False theory in the script:** the comment "fades in, wait 300 ticks" was wrong. `HediffComp_Invisibility.CompPostPostAdd` calls `BecomeInvisible(instant:true)`. The wait only made sure the hediff had expired before the walk.
- **Action:** edited `src/RimMandrake/CreatureBehaviors/validation.py`.
  - `INVISIBILITY_HEDIFF` is now `RM_SandSubmerged`. It is our own def, has `HediffComp_Invisibility` and no Disappears comp, and is inert on a pawn without `RM_CompSandSwim`.
  - Removed the 300-tick wait.
  - Added two `# RULED OUT:` notes: the bare PsychicInvisibility, and the fade-in theory.
- **Still to do:** a live re-run of the chain is needed to see it go GREEN. Optional hardening: read `jawa/pawn_health` after the walk and report UNMEASURED if the hediff is gone, so this failure cannot pass silently again.
- L0: validation.py parses; run_selftests 221/222 (only known utinnipatches_dump env fail); modcheck lint (all mods) run, see report.
