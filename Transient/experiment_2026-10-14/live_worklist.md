# Live worklist, ratchet pilot (Pyrelands + FlowWorks + GimmeSomeSlack) - 2026-10-14

Items BUILT (L0 green, published) and owing only a SHORT live proof. Ordered by value, GSS/FlowWorks first.
Source of each check: the 2026-10-13 closer triage notes on the item (`Transient/night_20261013/closer.md`, `fw_checks.md`).
Tier for all FlowWorks rows: ratchet_pilot (+ mandrake.rm.patches) unless stated. Run one site at a time; no long runs (owner 2026-10-13).
GSS: nothing owed live. proof_all 106/106 at dbe92f0c92 (`Transient/bench_live_20261013b/`); its only open item is owner-conditional `GIMMESOMESLACK_NORTHSTAR_VALIDATE_1` (owner word, no live work).
Site blocker first: FW river rows need a swept-pawn site (`FW_RIVER_SITE_DIAGNOSE_NOBODY_SWEPT_AWAY`, BENCH, already claimed by the offline list).

| # | ID | Exact check | Pass bar | Mod / tier / site | Est min |
|---|----|-------------|----------|-------------------|---------|
| 1 | `HAZARD_TAR_TERRAIN_FROM_LIQUIDS_1` | `extension_proof.py --live --chains` hazard chain on a tar plot (item `## verify`) | hazard code reads tar terrain from the liquid defs (A1) | FlowWorks / golden site | 3 |
| 2 | `LIQUID_LOOK_MATERIAL_OWNERSHIP_1` | toggle liquid looks off/on x3 with tar + propane + water channels, read materials each time | each keeps its own colour; off restores vanilla water, no colour bleed (A1) | FlowWorks / golden site | 5 |
| 3 | `LIQUID_FIRE_QUEUE_ORIGIN_1` | NEW predicates needed first (night run: plot_E_fire+fire_explosion 3/3 PASS but assert none of A1-A3). Then: chemfuel canal blast into source pond; torch beside pending tar cell; save/reload with pending front | A1 no pond cell lit beyond sourceFireReach; A2 pending cell lit within one check; A3 front still pending after reload | FlowWorks / golden site | 10 (+15 to write predicates) |
| 4 | `SURFACE_RIVER_WEIRS_1` (A2) | spawn SeasonalFlood on river site (`jawa/flowworks_spawn_flood`), assert surge, ProofWeirCatch drift | ProofGrid flood=True; drift roll biome-relevant; rest of ext_river already PASS | FlowWorks rivers / river site | 5 |
| 5 | `FLOWWORKS_QUARRY_DIGGING_1` | A1: list_things on RM_SluiceBox, RM_PanningSpot, RM_PanForPlacerJob, RM_PlacerPool_Vanilla (deploy read); then placer chain + dig_finds chain | A1 no config errors; A2-A5 placer got>0, refill = cap, panner stays on bank, dig find drops (A5) | FlowWorks rivers / river site (after the site fix) | 10 |
| 6 | `RIVER_TOGGLE_PROOFS_BUILD_ELEVEN_UNCLAIMED` | river toggle chains of `extension_proof.py --live --chains` + SeasonalFlood spawn | each of 11 toggles off removes its effect (A1-A6); A7 owner-watched, skip | FlowWorks rivers / river site | 20 |
| 7 | `HOSE_RULINGS_BUILD_THREE_REVERSALS_ONE_CARD` (A2) + `LIQUID_LEDGER_BUILD_NO_UNIT_LOST` (A3-A7) | machinery_pipes NS_ chains (plot G): dump tank drain, intake needs pump, ship tank fill, hose-off spill, theft goodwill; place pipe, pick look, read ThingStyle at blueprint/frame/building | each NS_ row PASS; look survives all three stages | FlowWorks / golden site | 15 |
| 8 | `LIQUID_BOTTLE_LOOP_1`, `FLOWWORKS_CONTAINER_MATERIALS_1`, `LIQUID_THIRST_CHAIN_1` | FIRST read why the fill job yields no filled bottle (HARNESS or MOD). Then chains toggle_bottle_loop, toggle_bottle_dirty, bottle_revert with metal and wood containers; THIRST needs DBH Lite+Thirst tier for A1-A3 | filled bottle drunk, dirties, washes; boiling reverts; material survives fill/wash/pour, metal/wood refuse acid | FlowWorks / golden site (DBH tier for thirst) | 10 + 10 |
| 9 | `GLOW_TANK_LIQUID_FEED_1`, `GLOW_TANK_SEED_LIVE_SOW_1` | salt-water tank beside powered glow tank, advance, read; real generator+conduit power then colonist sow via WorkGiver_GrowerSow (`LuminousPigment/live_probes/lp_glowtank_seed_sow.py`, route= must read colonist) | tank drawn down 1 unit at a time and crop grows, off removes line; colonist sows seeded, refuses unseeded | LuminousPigment+FlowWorks / minimal | 10 |
| 10 | `MISSION_TANK_GOAL_REWIRE_TO_DEST` | live chain mission report (machinery_pipes / mission chain) | destination tank units read by ThingID; verdict follows the delta (A2) | FlowWorks / golden site | 5 |
| 11 | `LAVA_LIQUID_BUILD_PROMISED_BY_CARD` | A3 startup-log grep with FlowWorks+Odyssey, no RM_Liquid_Lava ConfigError; A4 Forge map, wrecked pumping station never spawns lava-only | clean log; no lava-only station within 10 cells | FlowWorks+Odyssey / minimal | 6 |
| 12 | `LIQUID_INDUSTRY_SETPIECES_1` | `--chains machinery_found_works` plus forced set-piece spawn and list_things per slot (night run left ruins_mapgen/ruin_stock_mapgen/pipe_adapters UNMEASURED, no predicate) | every set piece present, none in the build menu (A2-A4) | FlowWorks / golden site | 5 (+predicates) |
| 13 | `PIT_LIP_OCCLUDES_OUTSIDE_1` (now also carries the superseded HIDDEN_BY_LIP) | load repro save RM_pitlip_muffalo_bug_20261006, screenshot (render-void trap: confirm map camera) | D4 pawn on south row inside opening; lip cover spans sprite (A1) | FlowWorks / flowworks tier | 4 |
| 14 | `PIT_TEMPERATURE_SOFTENING_1` | desert noon: roofed vs unroofed pit temperature; occupant resistance vs cell; compassionate vs psychopath thought | A2 unroofed moves faster; A3 resistance falls faster; A4 thought only for compassionate | FlowWorks / minimal | 10 |
| 15 | `WORLDMAP_LIQUID_TAGS_1` | four landing quicktests of the Ash'karr save, one per tagged biome | each shore repainted to its tagged liquid, rivers untouched | WorldMap/FlowWorks / minimal | 15 |
| 16 | `PYRE_SITE_TEMP_REPAIR_PROBE_HIT_ROCK` | build site on a tile with exposed rock and KEEP the gate B 3.8.8 line in the result JSON | gate B samples walkable cells only and PASSes | Pyrelands / pyrelands tier | 3 |
| 17 | `RIVER_STEAM_ANIMATION_1` | needs a steam-state predicate in extensions.py first (toggle_river_steam is field read-back only); then Pyrelands river map + non-Pyrelands map | puffs near river cells on Pyrelands, silent elsewhere (A1/A2) | Pyrelands+FlowWorks / pyrelands tier | 3 (+predicate) |
| 18 | `FLOWWORKS_CHECKOUT_SCOPE_1` | full step-4 extension run right after a v2 GREEN, then `modcheck record FlowWorks --result <v2> --extensions <ext>` SAME sitting, no code edits mid-sitting | both recorded, not STALE (A2) | FlowWorks / ratchet_pilot | 60 (last: it is the long one) |

Not short (leave for the final pilot pass): `FLOWWORKS_NORTHSTAR_TRIAL_1`, `FLOWWORKS_NORTHSTAR_GREEN_FULL_1`, `PYRELANDS_GREEN_MINIMAL_1`, `PYRELANDS_GREEN_FULL_1`, `PYRELANDS_NORTHSTAR_TRIAL_1`.
Owner-L4 only (no live driver work): `FLOWWORKS_LADDER_RAISE_LOWER_1`, `FLOWWORKS_VISUAL_PRINCIPLES_1` A4, `FLOWWORKS_BUILD_PROGRAM_1` A4/A5, `GLOW_TANK_LIQUID_FEED_1` H1, `TELEMETRY_COLONY_VITALS_BUILD_SPEC_SAID_SO` (A3 needs the full-list toll `VITALS_OVERHEAD_MEASURE_FULL_LIST_TOLL`, game-up).

## Added 2026-10-14 (BENCH builder, relative-climb items 2-3 + pond-bed dig)

| # | ID | Exact check | Pass bar | Mod / tier / site | Est min |
|---|----|-------------|----------|-------------------|---------|
| C1 | `PIT_CLIFF_MASK_BUILD_ASTAR_LEARNS_WALLS` (adba8a19d1) | deploy FlowWorks; `python.exe src/RimMandrake/FlowWorks/northstar/climb_proof.py --origin X,Z` (bridge held); then order a colonist across a sheer D3 trench, and into a sheer D4 pit with a lowered WALL ladder, then raise it and order again | every climb_proof row PASS incl. `CLIMB_mask_seals_cliff_edge` + `CLIMB_ladder_prison_door`; colonist walks around the trench; goes down/up the ladder; raised = order refused, no PatherFailed loop in Player.log, no NativeArray/Harmony error at load | FlowWorks / ratchet_pilot / flat site 30x12 | 10 |
| C2 | `POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE` dig-from-bed (bac9174bbf) | drain a pond (shallow rim + deep middle); designate dig on a dry RIM square and on a dry DEEP square; let a colonist dig the rim one | rim square reads D 3 after one cut (`jawa/flowworks_excavation_report`), lakebed replaced by RM_Channel_Deep; the deep square's designation is refused with "already as deep as digging goes" | FlowWorks / ratchet_pilot / pond site | 5 |
| C3 | `PIT_RAMP_BUILD_STAIRS_BEAT_LADDERS` (8100177f21) | same climb_proof run as C1 (pit E); then in the build menu place a ramp on D4 facing the D1 shelf (accepted) and facing D0 (refused), a ladder mid-floor (refused: needs a wall); read a cat's inspect line in a D2 hole | `CLIMB_ramp_frees_and_retraps` + `CLIMB_ramp_walk_out` PASS; placement verdicts as stated; "Climbs out of steps up to 2 deep" on the cat; no error from FlowWorks_ClimbAbility.xml at load. Ramp ART is a placeholder: owner art via art ledger still owed | FlowWorks / ratchet_pilot / flat site 30x12 | 8 |

## Added 2026-10-14 (BENCH diagnostician, river swept/pan rows)

| # | ID | Exact check | Pass bar | Mod / tier / site | Est min |
|---|----|-------------|----------|-------------------|---------|
| R1 | `FW_RIVER_SITE_DIAGNOSE_NOBODY_SWEPT_AWAY` (unblocks `SURFACE_RIVER_WEIRS_1`, `FLOWWORKS_QUARRY_DIGGING_1`) | `python.exe src/RimMandrake/FlowWorks/northstar/river_site.py` then `python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live --site river --chains swept,placer --out <r.json>` (no FlowWorks deploy needed: harness-only change) | `returns_home` PASS (note "washed away: pending 0 -> >=1"; staged colonists vanished after); `panning_draws_stock` PASS (note "pan tries" ends in `pan=<def>x<n>`); `jawa/mod_settings_field get` afterwards reads panningYieldMultiplier=1, placerStockPercent=2 (restored). `flood_refill` stays UNMEASURED: owed by design, not site. An UNMEASURED "none was washed away" lists the edge cells: that is the next lead (flow at the edge not pointing off-map) | FlowWorks / ratchet_pilot / river site | 8 |

## Added 2026-10-14 (BENCH art helper, Pyrelands art install)

| # | ID | Exact check | Pass bar | Mod / tier / site | Est min |
|---|----|-------------|----------|-------------------|---------|
| P1 | `PYRELANDS_SHIP_READINESS_1` art install (deploy owed: `deploy_custom_mods.py --compose biomes` then `--apply`) | spawn + kill one each of RM_Emberscythe, RM_FireWasp, RM_Flamefang, RM_Sytheclaw, RM_Barbslinger (adult) and force-dessicate the corpses (dev: rot fully); spawn RM_LightningBreakerCore and RM_FE_FirefoamSprayer on the ground; place a RM_LightningBreaker on a live conduit and trip it (short circuit); let a barbslinger fire its tails at a target | each corpse draws its own bleached husk/skeleton (not a vanilla skeleton, not magenta); core item is a glass-sand cylinder in a steel sleeve; sprayer is a yellow tank + flared nozzle; the tripped breaker shows the raised lever + sooted cracked core (not the darkened normal frame); the tail shot draws an amber spike; no "Could not load texture" / red error naming Dessicated_, RM_BarbslingerSpike, RM_LightningBreakerCore, _Off or RM_FE_FirefoamSprayer in Player.log | Pyrelands (mandrake.rm.biomes) / any tier with Biotech / any flat site | 8 |

## Added 2026-10-14 (BENCH FlowWorks review fixes, b68768fc7c7c)

| # | ID | Exact check | Pass bar | Mod / tier / site | Est min |
|---|----|-------------|----------|-------------------|---------|
| F1 | `FLOWWORKS_NORTHSTAR_SHIP_1` review fix: bed cut fill-in | drain a pond with a shallow rim (hollows on); designate dig on one dry shallow-bed square (bed 2 -> dug 3); then fill it in once | after ONE fill-in the square is lakebed again, back in its pond (pond inspect counts it), hollow depth 2; never reads 1 or 0 on the way | FlowWorks / minimal / any pond site | 6 |
| F2 | same: hollow toggle reset | Mod Settings: toggle "A drained pond leaves a hollow" off, close; reopen; click "Reset this section" on Stock, recession and drainage | a pawn standing on a dry deep bed square is held/freed per the hollow rule immediately after the reset (pocket rebuild: `RM_PocketGrid.ProofPocket` gen/built move) | FlowWorks / minimal / drained pond | 4 |
| H1 | `V2_POND_ROWS_REPAIR_STILL_COUNTS_FIVE` (18e769fc42) | FlowWorks `validation_v2.py --live --fresh-map` on a minimal list with the 0afba7de51+ build | S3_classification, E3_budget_exhaustion, E3n_budget_off_supplies, E3b_recession_shipped, E4 PASS with pond capacities 2/cell (W2 2, W2R 8, W3 10, W4 80, W5 128); no row still expects 5 | FlowWorks / minimal / fresh quicktest map | 15 |
| H2 | `PYRE_FULGURITE_BUILD_NO_SAND_TO_STRIKE` (28f619d2f7) | Pyrelands `fulgurite` chain on site r3 | note shows `sandPatchLaid` and frac ~0.5; row PASS (or FAIL only with expected >= 3), not UNMEASURED; after it the west half reads its pre-patch terrain (get_terrain_batch counts equal to before) and fulguriteChance is back at its prior value | Pyrelands / site r3 | 12 |
| H3 | `TESTENV_WILD_DOWNED_REPAIR_STOPS_CLOCK` (ed4f98ceec) | Pyrelands `scorchfruit_spoils_fast` 2000-tick governed advance on a site with wildlife | advance completes all ticks past a wild-animal downed stop (`BENIGN_STOPS` / governor advances list the resume); verdict notes "wild pawn(s) downed", outcome not UNMEASURED; a downed colonist still stops it | Pyrelands / any quiet site | 8 |
| F3 | `FLOWWORKS_NORTHSTAR_SHIP_1` review fixes (8503275a73) | Mod Settings: turn OFF "Digging a dried bed takes the square out of its pond"; drain a pond with a shallow rim (hollows on); dig one dry shallow-bed square (bed 2 -> 3), fill it in once; then put a shut sluice on a dry bed square beside a brim-full canal and pulse | the filled square is lakebed, hollow depth 2, still counted by the pond, no water written; no level runs into the sluiced bed square (canal fill unchanged, pond stock unchanged) | FlowWorks / minimal / pond site | 6 |
| F4 | `V2_PIT_ROWS_DIAGNOSE_NOBODY_STAYS_IN` (f6a31d056d, deploy FlowWorks) | `validation_v2.py --live --fresh-map` phase P only | P1 held {T,T,T;F,F,T} read paused right after the dig (no tick); P3 walk-in refused. P4/P4f/P5n: record the result at HEAD (ladder path changed since 0afba7de51); a FAIL there is a new finding, not this one | FlowWorks / minimal / fresh map | 10 |

## MAYREQUIRE_REPAIR_GUARDS_NAME_A_GHOST (live check owed)
Deploy now rewrites folded packageIds in MayRequire/MayRequireAnyOf (deployed copy only). After the next deploy + load:
- On a fresh FlowWorks-tier map, liquid-works ruins SCATTER (4 GenStepDefs in RM_LiquidWorksScatter.xml were dead).
- Ollathrix (RM_Ollathrix, RUT_Webwork.xml:158) is present in the Webwork roster.
Scanner: python3 src/RimMandrake/Utils/selftest_mayrequire_folded.py (8 sites, 5 true ghosts at 2026-10-14).

## Pyrelands BENCH fixes at 68049f4519 (live checks owed; deploy the Pyrelands DLL first)
| # | ID | Exact check | Pass bar | Mod / tier / site | Est min |
|---|----|-------------|----------|-------------------|---------|
| P1 | `PYRE_SCORCHFRUIT_DIAGNOSE_FIRE_BEARS_NOTHING` | chains `fresh_burn_bonus` (fire_tick_effects) then reload fixture then `scorchfruit_fire_born`, twice | scorchfruit_fire_born PASS both times (>=1 fruit in 178,48,24,24) after reloads that re-issue fire ids | Pyrelands / site r3 | 10 |
| P2 | `PYRE_ASH_CONTROL_DIAGNOSE_DRY_READS_WET` | chain `ash_fertility_watered` | note "ash strip placement" rejects the anchor (pond) and picks a dry origin; far 0.4 not watered, beside 1.4; PASS | Pyrelands / site r3 | 3 |
| P3 | `PYRE_HERD_DRIVE_BUILD_TWO_DAYS_LATER` | chain `ullai_and_giant` | BurnCenterAgo(2 d) = A (30,100) with B (220,100) newest; ProbeHerd goAnchor = n, issued >= 0.8n; after 2500 ticks centroid closes >= 30% on A and more than on B; PASS recorded with the INFERRED cadence note | Pyrelands / site r3 | 8 |

## Static per-game state fixes at 92ada47568 (BENCH; live checks owed; deploy FlowWorks + Pyrelands DLLs and the companion first)
Census: `Transient/experiment_2026-10-14/static_state_audit.md`. Offline ratchet: `selftest_static_game_state.py`.
| # | ID | Exact check | Pass bar | Mod / tier / site | Est min |
|---|----|-------------|----------|-------------------|---------|
| S1 | `PIT_REROUTE_FIX_TIME_TRAVEL_FORGIVEN` | `validation_v2.py --live` phase P (P4/P4f), reload the fixture at an EARLIER tick, run phase P again | second run's held friendly re-plans to the ladder like the first (no Wait-forever, no PatherFailed loop); no red error naming RM_SuperdeepTrap | FlowWorks / minimal / fresh pit map | 12 |
| S2 | `BURROW_TIMEOUT_FIX_DEJA_VU_CURED` | force one burrow TIMEOUT (stuck fire), reload fixture, light a burn | the same animal id dives on the reloaded map's first burn; within one session a timed-out burrower still stays up for the cooldown | Pyrelands / site r3 | 10 |
| S3 | `ARTBOARD_PAWNS_HARDEN_IDS_ARE_NOT_PEOPLE` | artboard_stage with faction=player pawns; reload; spawn a test colonist in the same clearRect; re-stage phase=ground | call REFUSES ("clearRect holds player pawns"); the colonist survives | companion / any / any flat site | 5 |
| S4 | `VITALS_SPECIMENS_FIX_GHOSTS_REHOMED` | arm vitals with specimens=<pawn id>; reload (same ids); sample | no specimen-lost trigger for a pawn alive in the new game; coverage trigger names the new epoch | companion / any / any | 5 |

## BENCH r3 repairs (implemented, live check OWED)
- FINDMOD_GUARDS_REPAIR_GHOSTS_BY_NAME_TOO (60fddab35e): deploy FlowWorks (+SWBestiary, StarWarsRaces, Wasteland, composed biomes); check deploy log "rewrote ... folded-id/name guard(s)", deployed RM_LiquidWorksScatter_Register.xml has <li>RimMandrake: Baroque Biomes</li>, then live: 4 liquid-works ruins in Base_Player genSteps / scatter appears on a fresh map.
- RAID_DETECTOR_REPAIR_FLOOD_NOT_A_RAID (63c4420a7a): FlowWorks works chain with a flood: no raid_arrived surprise on 'Seasonal flooding'; a real raid still fires.
- TESTENV_QUICKTEST_DIAGNOSE_SPIKES_UNINVITED / TESTENV_TOXIC_DIAGNOSE_RIVER_SITE_SNIFFLES: quiet_site gains toxic_sources_cleared control + settle(); live: fresh quicktest with QuietSite isolated then settle(): receipt arrivals[].origin names the spike source (cause UNPROVEN), toxic_sources_cleared readBack lists conditions/gas/polluted cells; river site chain with no ToxicBuildup.
- V2_LADDER_ROWS_DIAGNOSE_STAGE_FRIGHT (c238935c98): deploy FlowWorks; validation_v2 --live --fresh-map phase P: P4/P4f/P5n PASS, P4b measured, P1/P3 still PASS. Cause (MEASURED in code): a built ladder never moved the climb generation (Standable, pathCost 0 -> no vanilla cell delta), so the cliff masks never joined lip<->pit.

## PERF probes for round 4

(BENCH perf investigator, offline findings 2026-10-14; each probe is a read, no extra staging.)
1. **CLOCKGATE_STATUS_REPAIR_NULL_WENT_MISSING** — round 4 must run from a HEAD at or after `9a4852f50a`. After GSS
   `proof_all`, read the aerial block wall in the JSON (`blocks.aerial.wall_s`): PASS if ~50 s (r2 50.2) and the
   bridge log shows `jawa/safe_advance` start calls (not `rimworld/step_game_ticks`) for run `proof_all.py`.
   r3's 137 s was every `B.ticks` falling back to step_game_ticks because the status reply's null `advance` is dropped.
2. **FACTION_LEADER_REPAIR_SIX_EMPTY_THRONES** — only if UtinniPatches is deployed at or after `cf73c55411`: on the
   FRESH GSS map, `telemetry exc --since 1h` must show no `O:Faction leader for ... is null` and the TPS exc windows
   rep should be ~0, not ~360/s. Saved Pyrelands sites made before the fix WILL still show it (null leader saved).
3. **OWN_PRESET_WIDEN_PYRELANDS_JOINS_IN** — only if the companion is redeployed from `53595b2d45`+:
   `jawa/health_profile action=start preset=own` on the Pyrelands site; `refused` should list only mods not loaded,
   and Pyrelands/GSS rows should show us/tick. The exc window then carries `repTop` keys.

- GSS aerial sparks follow Cables settings (BENCH, 2026-10-14): with a live fallen overhead wire and a draining tap clamp,
  set `sparksOnlyOverlay=true` -> no fallen-wire glow/sparks and no clamp sparks until the power overlay is open;
  set `maxSparkingEnds=8` with >8 live fallen wires -> AerialProbe `lastGlowDraws` <= 8. Needs the GSS DLL deployed.

- RONTO_PACK_TEXTURE_REPAIR_SADDLEBAGS_MISSING: implemented (placeholder RontoPack_* copies); owed live: next startup log shows no "Failed to find any textures at .../RontoPack"; owner approval for real saddlebag art.
- PYRELANDS_GRASS_SATURATION_1: nothing offline left; owed live: clear Bush/Pincushion instances; owner LOOK at ground fill.
- SETTINGS_KIT_BUILD_GREY_SWITCHES_AT_LAST (BENCH, 2026-10-14): deploy GSS + Pyrelands DLLs, open each Mod Settings window.
  Turn a master off (GSS "Messy cords", "Aerial power lines", "Allow power-tap clamps"; Pyrelands "Mod enabled", "Fire dusts
  loose ash"): its dependents are shaded with a "switch on ..." tooltip; clicking/dragging them changes nothing; the sub-switch
  itself (e.g. "Taps have consequences") stays clickable when only it is off; values come back unchanged with the master on.
  "Reset all to defaults" asks first; Cancel changes nothing, Confirm resets every setting (GSS: both tabs). Check the shade
  sits exactly over the block inside the scroll view.

- FLOWWORKS_SETTINGS_WIRE_AFTER_TANKS (BENCH, 2026-10-14): deploy the FlowWorks DLL, open the FlowWorks Mod Settings window. Turn "Depth engine"
  off: Flow per pulse / Largest network / seams are shaded with a "switch on ..." tooltip, clicks change nothing, "Flow pulse" stays live.
  Same for "Flammable liquid ... can be lit", pit drowning/exposure/falls/spikes, "Pawns sink into dug channels" (nested lip-occlusion
  scopes), "Dug cells show their walls", "Digging a canal can turn up minerals", "Drilling and tapping" (extraction rate only),
  "Flexible hoses (master switch)" (look + colonist handling). Values return unchanged. Two "Reset all to defaults" buttons (top
  of the window; under "Hoses and pipes") each ask first; Cancel changes nothing.

## From reviewer D (FACTION_LEADER_REPAIR_SIX_EMPTY_THRONES, Free Droid Enclaves)
- Live check: load with Outer Rim - Droid Depot ABSENT. Patches/FreeDroidEnclaves_LeaderFallback.xml (8c45cd04f3) adds vanilla `Villager` to RUT_Jawa_FreeDroidEnclaves fixedLeaderKinds via PatchOperationFindMod nomatch. Expect: no "Faction leader for Free Droid Enclaves is null" ErrorOnce in Player.log; faction leader non-null. With Depot present, fixedLeaderKinds must stay [RUT_Jawa_Droid_Leader] only. Saves made before keep null leaders (accept or repair separately).
- Not checkable offline: validate_patch.py --defs refused (UNMEASURABLE load set), so the xpath was checked by reading the def only.
- Human review map (human_review.py): station 27 CONVERGING HUB now builds its third lamp (19,16); next --build shows it.

- V2_LADDER_ROWS_DIAGNOSE_STAGE_FRIGHT (BENCH R5, 2026-10-15): deploy the FlowWorks DLL from the R5 ladder fix (pawnless reachability
  counts a lowered ladder; vanilla StartPath's PassDoors CanReach is pawnless). Run `validation_v2 --live --fresh-map` phase P: expect
  P4_ladder_frees, P4f_ladder_frees_forced, P5n_own_faction_carveout PASS; P1/P3/P3f still PASS; P4b measured (back in True). If any stays
  red, read the order_pawn row's curJob/note at waitTicks=30 (Goto gone at once = StartPath refused) before any further fix.
  Notes: Transient/experiment_2026-10-14/ladder_r5.md
