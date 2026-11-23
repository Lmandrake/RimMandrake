# Mods hypotheses B: what a live test of each mod needs from the bridge

Read-only design research, pass one (brief m2). Repo: /home/mandrake/rm/relentless/clones/RIMMANDRAKE_DESIGN_BRIDGE_TWO_WHAT_LIVE_TESTING_NEEDS_FABLE_PASS_ONE.det
Tags: DESIGN (path) = stated in the mod's design; GUESS = my hypothesis.

## Contagion
Sources: design/concepts/Contagion/sheet.md, design/concepts/Contagion/scenes.json (24 scenes; 16 hold "immediate", 8 "owner_review").
1. HOLD STILL
- Weather: the standing Bloom must stay the active weather; a vanilla lull weather is in the biome's weather table and would end the red lid mid-scene. DESIGN (scenes.json sc_bloom_reads_sick, sc_burn_dash "standing Bloom at midday, no condition active (asserted)").
- Hour of day: midday, so Burn dose and shade are not confounded by night. DESIGN (sc_burn_dash).
- Other game conditions: none active except the one under test; the Repulsor's sky-clear and the Burn are both conditions. DESIGN (sc_burn_dash, sc_repulsor_warns_and_clears).
- Colonist free will: "no draft, no forced job (asserted)" for the shelter scene, so the walk is the ordered one and nothing else. DESIGN (sc_shelter_in_lead).
- Wildlife: "predators removed (asserted)", "wild animals cleared" before roster counts; a wild spawn would corrupt a per-row count. DESIGN (sc_natives_take_burn, sc_cast_lives_here).
- Mod settings at shipped defaults, asserted by preflight. DESIGN (all scenes).
- The Bloody Mess eating corpses and skin, and the budding spawner, run on their own clocks and could consume or add things under test. GUESS.
2. FORCE
- A natural Burn: jump the clock to the start of the tells window from the saved schedule, not a forced condition, so the tells are the mod's own. DESIGN (sc_burn_dash, sc_tells_then_burn). A forced Burn is used where only the Burn's effect matters. DESIGN (sc_one_dash_at_cost).
- Clock jumps for long processes: budding deadline x4, gestation four days, Bodyprints phase clock, zhool haze clock, 30-day wreck jump. DESIGN (sc_unfinished_malformed, sc_genome_brings_tissue, sc_bodyprints_phased, sc_flora_flesh, sc_cast_lives_here).
- Player orders: dash between refuges, hold the Sunbeam lens on a patient, inject, install an organ, fire a burst, build mulched soil, power and unpower the Repulsor. DESIGN (several scenes).
- Spawn with the biome's own wild-animal spawner, "never a direct spawn", when a roster row misses the day. DESIGN (sc_cast_lives_here).
- A touched colonist at a set severity "below the first mutation". DESIGN (sc_burn_dash).
- Flip each mod setting bool by reflection on the deployed type. DESIGN (sc_settings_superb).
- Save and reload mid-tell and between budding jumps. DESIGN (sc_tells_then_burn, sc_unfinished_malformed, sc_walk_red_lid).
3. OBSERVE
- Draw-time state of the tells every 60 ticks: gawpsack draw offset, rattlegrope shake phase, red puff motes counted, LeavesRustle sound played once. DESIGN (sc_tells_then_burn). Sound and mote counts are not game state.
- Which cells the shared shade grid reads shade vs open, and Burn dose per cell. DESIGN (sc_refuge_is_shade).
- Per-pawn hediff severity (RM_BurnDose, RM_ContagionTouched), and when it starts rising. DESIGN.
- Letters and messages: exactly one "Contagion mutation:" letter, one transition message, none sub-threshold. DESIGN (sc_touched_reads_early).
- Job counts over a window (sun-escape jobs for 2500 ticks; shelter sprint job absent for leakers). DESIGN (sc_bloom_quiets_sundash, sc_natives_take_burn).
- Pawn stats under weather (move speed, ranged accuracy x0.4). DESIGN (sc_bloom_reads_sick).
- Inspect text showing gestation odds before the job. DESIGN (sc_genome_brings_tissue).
- Captures at play zoom judged by an agent that did not stage them: red sky, beam, UV projectile, each creature distinct. DESIGN (many).
- Reservation refusal (second colonist refused on the lens patient). DESIGN (sc_sunbeam_arrest_treats).
- A second map loaded at the same time, and its conditions read. DESIGN (sc_repulsor_warns_and_clears, sc_bloom_reads_sick).
4. REPEATS
- Random by design: mutation deck draws, limb rolls (three buds "pairwise different"), batch odds, roster spawns over a day. DESIGN. Scenes check sign and order, never a value. DESIGN (sheet.md advisory).
- Length: Burn hold 2500 ticks; one in-game day (60000 ticks) for touched and roster; days by jump for gestation and Wombpod (three days). DESIGN.
- Side by side: the Burn is map-wide, so one map can hold several exposed and sheltered pawns at once (the scenes already do this). Weather-wide scenes cannot run two weather states on one map, so the control needs a second map. DESIGN (second map in sc_bloom_reads_sick). Same-order determinism across reload is itself a bar (sc_walk_red_lid). DESIGN.

## Cauldron
Sources: design/concepts/Cauldron/sheet.md, design/concepts/Cauldron/scenes.json (36 scenes; 29 "immediate", 7 "owner_review"). Every scene starts from a disposable copy of RM_TestSite_cauldron_v3 with DLL hash, list, tile and settings asserted.
1. HOLD STILL
- No secondary ignition source in gas-chain lanes; other vanilla and third-party gases seeded at recorded values so the Cauldron gas grid is shown not to alter them. DESIGN (scenes.json gas_chain, gas_transport).
- Wind heading: "map-seeded heading holds within day"; the drift test needs a fixed daily heading and must not cross the day boundary by accident. DESIGN (gas_transport).
- Wild animals separated from tame ones; "closed pens contain zero pre-existing candidate plants/galls"; sleep and location asserted for the rhossak seeding animal. DESIGN (rhossak_cycle, vent_competition).
- Colonists: "no harness invulnerability/need bypass" in the 40-colonist day, so needs, hauling and jobs are real and must not be frozen. DESIGN (routine_day). Elsewhere haulers would move the goods whose knockback displacement is measured. GUESS.
- Weather schedule: the falter-to-bloom transition must run at default duration, so the weather picker must not be overridden. DESIGN (falter_hour).
- Occupied and zoned cells preserved when the garden sampler runs. DESIGN (weather_gardens).
- No world creation, tile scoring or placement change; mapgen tested only on a disposable local fixture at the pre-MapGenerated checkpoint. DESIGN (mapgen_vents_gardens, legacy_floor).
2. FORCE
- Invoke the production MapGenerated vent and garden callbacks on a fixture, in both component orders, from one checkpoint. DESIGN (mapgen_vents_gardens).
- Ignite only the first connected gas cell with a unique original spark and instigator. DESIGN (gas_chain).
- Let the normal bloom transition happen (not forced) and record the cue-onset tick. DESIGN (falter_hour).
- Ordinary player orders: harvest thornwood, shear vexxiss, build the vexxith-plate door via the architect menu, study the rig, advanced medical purge, butcher, cook. DESIGN (many).
- Damage arms on suush: matched melee, Bullet and Bomb. DESIGN (suush_burst).
- Settings UI driven for real: search, scroll, collapse, reset, then all-off, save, reload, re-enable. DESIGN (settings_effects).
- Save during an active fire front and reload. DESIGN (gas_chain). Mid-falter reload. DESIGN (falter_hour).
- Wild vexxiss must choose by themselves to walk to a vent and drink. DESIGN (vent_competition).
3. OBSERVE
- The instrument itself: "Validate reads with known health, gas-cell, job, liquid and inventory mutations", a nonempty live log tap with a sentinel and lost count zero, and a recovery manifest after an interrupt. DESIGN (observer_recovery).
- Per-cell gas grid values (mass, centroid, decay) over ticks; propagation front of a fire chain tick by tick. DESIGN (gas_transport, gas_chain).
- Things in mid-air: goods thrown by ExplosiveKnockback, with stable Thing identities and the displacement sequence. DESIGN (gas_displacement).
- Liquid volumes: whole bank units of 200 L, fractional and capped bank values, no lost litre across tap, tank and works. DESIGN (tap_refine, water_works).
- Hediffs and body-part capacities over long recovery: metal load persisting through care, departure and reload; permanent acid disfigurement. DESIGN (metal_purge, acid_injuries).
- Draw-time: flecks, trunk coat tiers, dew bead swaps, cloud rendering, updated "without moving camera" (remesh). DESIGN (thornwood_harvest, trunk_coat_check, gas_transport).
- Letters with a cooldown ("letter fires once per documented cooldown"). DESIGN (water_fire_tracks).
- Hot-path timing over a 40-colonist day. DESIGN (routine_day, floor_checkout).
- Visual read by a human or judge: mineral forest, rainless dusk, no placeholder art. DESIGN (arrival_identity).
4. REPEATS
- Random by design: acid disfigurement and sensory damage ("report probabilities/severity as candidate tuning", a declared finite batch), suush wick, seeding. DESIGN (acid_injuries).
- Length: falter about 2500 ticks before bloom; recovery window bounded; vexxiss fullness uses "compressed fixtures" labelled as such. DESIGN (falter_hour, vexxiss_products). The 40-colonist routine day is the longest. DESIGN (routine_day).
- Side by side: the scenes already use matched arms (exposed, roofed, full suit, helmet only) on one map, and disjoint gas lanes. DESIGN (ambient_routes, gas_chain). Gas lanes must be far enough apart that one cloud does not reach another lane. GUESS.

## Stillsand
Sources: design/concepts/Stillsand/sheet.md, design/concepts/Stillsand/scenes.json (33 scenes, all "immediate"). Every scene starts with scene-begin recovery written before any persistent change.
1. HOLD STILL
- Unplanned incidents: the giant visit has an "unforced interval" that is recorded first, then the incident is triggered through its normal worker; a natural visit, horizon group or gale arriving during another scene would spoil it. DESIGN (scenes.json giant_visit, horizon_warning). GUESS for the hold itself.
- Gale: it moves sand per cell, suppresses senses and the geophone, clears wet attraction. Any gale outside the gale scenes must be held off. DESIGN (gale_phases, gale_signs_wet, buried_signs).
- Sun angle: two elevations are compared; permanent sun, so the hold is on elevation, not on night. DESIGN (sun_geometry, sheet.md direct_sun).
- Giants as moving shade: a giant walking over a scene changes exposure. DESIGN (sun_geometry "Move a giant shadow over a pawn and a table").
- Hidden swimmers under sand react to water pours and thumpers; an unplanned thumper beat or pour attracts them. DESIGN (pour_expiry_thumper, swim_fish_thumper).
- Wet line and bloom expiry timers run on their own clock. DESIGN (pour_expiry_thumper).
- Random draws: gale carry uses "a labelled seeded random draw", gale row selection is seeded. DESIGN (gale_carry_return, gale_phases).
2. FORCE
- Trigger the giant visit, gale, eruption, horn answer through their normal incident workers ("label and trigger"). DESIGN (giant_visit, gale_phases, eruption_brood, campaign_encounters).
- A swimmer forced to surface. DESIGN (harbour_secured).
- A carried pawn off-map and its saved return: off-map service registration, then return "once through the downwind/survival policy". DESIGN (gale_carry_return).
- Labelled compressed time for long processes: water cooling six-hour effect, giant desiccation and skeleton conversion, brood dormancy. DESIGN (glare_cooling_mirage, giant_history, eruption_brood).
- Block the skeleton conversion space, reload, free it. DESIGN (giant_history).
- Swap hydration values while all other inputs are fixed. DESIGN (hydration_independence).
- Ordinary player orders: pour water, deep-sand Fish job, sift, wring, refuel thumper, sunward offering. DESIGN.
3. OBSERVE
- Sound: "Audio and captures match actual hidden movement"; rumble, hiss, saltation, singing slabs. DESIGN (buried_signs). Bridge must read which sounds played.
- Hidden state: pawns submerged under sand (position while not drawn). DESIGN (swim_fish_thumper).
- Per-cell sand mass and flux during a gale, with a total-mass conservation check. DESIGN (gale_phases).
- Draw-time: wet line and halo, heat shimmer, mirage, plume fading, fade before and after reload. DESIGN (pour_expiry_thumper, horizon_warning).
- Geophone inspect readout: coarse bearing and size. DESIGN (buried_signs).
- Off-map pawn held by a service (not on any map). DESIGN (gale_carry_return).
- Letters: dust-settled, cancellation letter toggles. DESIGN (horizon_warning).
- Booked water volumes through split, merge, reload, ingestion. DESIGN (water_cycle).
- The observers themselves validated against independently counted state; log loss is UNMEASURED. DESIGN (observer_controls).
4. REPEATS
- Random by design: carry dice, fishing catch pool "including the rare pearl branch under labelled seed", row selection. DESIGN (swim_fish_thumper, gale_carry_return). The rare branch needs a seeded draw or many tries.
- Length: water effect six hours (15000 ticks); expedition loop and walk are multi-day. DESIGN (glare_cooling_mirage, expedition_loop).
- Side by side: gale and giant visits are map-wide, so their scenes cannot share a map with each other. GUESS. A 40-colonist harbour scale for workshop contention. DESIGN (workshop_jobs, sheet.md ordinary_work).

## FeverWood
Sources: design/concepts/FeverWood/sheet.md, design/concepts/FeverWood/scenes.json (45 scenes; 32 "immediate", 13 "owner_review"). Every scene's start carries the rule "no result from a forced transition proves its normal trigger or its natural frequency". DESIGN.
1. HOLD STILL
- Other pools: scenes need two disconnected pools A and B with distinct agitation; a strike or porter event at the wrong pool spoils pool_memory. DESIGN (scenes.json porter_and_agitation, pool_size_reach).
- Competing jobs: "no competing rescue jobs", "identical speed/health/duty" for near and far helpers. DESIGN (real_shore_rescue).
- Audio: "Fixed listener position and volume ... keep unrelated ambient/colony sound constant". DESIGN (crown_audio).
- Adult quiet and cooldowns: the eye encounter needs "accumulated pressure and no cooldown"; a natural limb roll mid-scene changes pressure. DESIGN (eye_encounter, limb_ladder).
- Ignition: "no ignition" for oil harvest arms; lightning is one of the ignition hooks, so the weather must be held. DESIGN (oil_harvest, oil_ignition).
- Hostile pawns near the thornbug farm (fear area) only where placed. DESIGN (nectar_and_guild).
- Thirst need: FlowWorks RM_Thirst must be loaded; without it drinking is UNMEASURED. DESIGN (native_water, sheet.md native_life).
2. FORCE
- Map generation through the real ordered gensteps (LivingBoles, ScatterPools, RootCauseways, GroundRefusal) on a disposable local map on an already-authored tile, seed recorded, observed at each pass boundary. DESIGN (generated_terrain).
- A real shore seizure by the caller, not a staged downing; then replay "from the same baseline" with near, far and absent helper. DESIGN (real_shore_rescue). Needs a restorable baseline and many replays.
- A raider that chooses to walk the branch routes; Webwork raiders that converge on living bait, second wave present and absent "in separate controlled scheduling arms". DESIGN (branch_work, two_front_journey).
- Damage arms on limbs and the eye (moderate, severe, fatal) and on tanks (below-threshold, forced-risk seam, engine fatal destruction). DESIGN (limb_ladder, tank_exit_routes).
- Six ignition hooks, each replayed from baseline: shot launch, shot impact, explosive impact, ordinary fire, burning pawn, lightning. DESIGN (oil_ignition).
- Compressed but fully simulated time: borer galleries, several-day young establishment, adult suppression clocks. DESIGN (borer_gallery, young_establishment, normal_suppression).
- The eye must arrive through "the eligibility/selection path rather than spawning a lone eye". DESIGN (eye_encounter).
3. OBSERVE
- Pure reads: "Read before/after snapshots twice without advancing time"; reads keyed by map, pool and pawn IDs. DESIGN (observation_control).
- Sound: bird-specific calls per living bird, ambient bed, hush cutting both. DESIGN (crown_audio). Needs an audio event trace, not a screen.
- Actual paths and detours per pawn, raider route over branches. DESIGN (branch_work, hive_geometry).
- Hidden rolls: "effective strike probability", "inspect effective eligibility before the actual production rolls", effective ambient MTB. DESIGN (porter_and_agitation, adult_authority, brood_tally).
- Absolute deadlines and due ticks across save and reload. DESIGN (water_rescue_reload, return_disable_reload).
- Items held off-map: caravan and settlement keeper inventory counted in the brood tally. DESIGN (brood_tally, campaign_display).
- Per-cell flash set after ignition (connected vs excluded cells). DESIGN (oil_ignition).
- Settings screen at play zoom: labels, grouping, ranges. DESIGN (settings_and_heat).
4. REPEATS
- Random by design: sink-mud sticking risk by weight ("opportunity counts, actual stuck events"), limb type weighted selection, gift rolls, carry and lure triggers ("replay until a real lure trigger"). DESIGN (sink_mud, limb_ladder, normal_bait).
- Length: several in-game days for establishment and suppression; day-scale drive-off. DESIGN (young_establishment, eye_encounter).
- Side by side: pools are the unit of state, so disconnected pools on one map are the designed parallel arms. DESIGN (pool_size_reach). Map-wide adult suppression and map victory forbid running suppressed and active arms on one map. DESIGN (normal_suppression "map-wide scope"). Many replays need a fast restore of one baseline. GUESS.

## GelatinousSlime
Sources: design/concepts/GelatinousSlime/sheet.md, design/concepts/GelatinousSlime/scenes.json (34 scenes; 32 "immediate", 2 "owner_review"). Every scene asserts "a lossless log tap and the exact scene actors/items".
1. HOLD STILL
- Film progression on bystanders: anyone on slime terrain gains film; colonists who wander onto pads spoil the baseline. "Safe contained tagged ... pads" and "disjoint safe pads". DESIGN (scenes.json contact_ladder, titan_engulf_rescue).
- Wild life on the authored slime map: native census before staging, visitor trickle with a cap; an extra arrival changes counts. DESIGN (native_body, visitor_arrival).
- Predators: fubbum hunting and Titanoslime engulfing pick their own prey; non-test prey must be kept out of reach. DESIGN (fubbum_hunt, titan_engulf_rescue).
- Haulers: chunk ages in map, equipped, inventory, caravan and nested holders are tracked; an unplanned haul moves a chunk to a new holder. DESIGN (chunk_ground_and_age). GUESS for the hold.
- Power: the archive vat needs power; an unplanned outage pauses paid progress. DESIGN (archive_lifecycle_and_family).
- Weather: SlimeRain is forced as a bounded stimulus; natural rain otherwise confounds the rain collection route. DESIGN (rain_and_water_services). GUESS for the hold.
- Social life: a spouse who "separates/remarries before return" is a staged state; ordinary social drift on the pairs must not change opinion baselines. DESIGN (gene_effect_and_social, archive_lifecycle_and_family).
2. FORCE
- An ordered injection, then a friend who must choose to take the antidote job and travel in time. DESIGN (ordered_friend_rescue). The friend's job uptake must be the AI's, not forced.
- Let untreated film complete dissolution (terminal path). DESIGN (terminal_belongings).
- Mark expiry, dose rot, refrigeration: ages and expiry ticks crossed. DESIGN (seeker_lifecycle).
- Throw a chunk through ordinary targeting; open the V5 vault plug (campaign RUT_VaultFleshSeal). DESIGN (chunk_throw, v5_seal_and_generic_breach).
- Kill a colonist and grow the recorded life back in a paid powered vat; a second vat contends. DESIGN (archive_filing_and_return).
- Caravan transit of a patient with clock flags. DESIGN (geographic_exit).
- Titan feeding across a stage boundary, wounding for shedding. DESIGN (titan_growth_shedding).
- Dwommo flight only with the owner present. DESIGN (dwommo_attended, standing flight floor).
3. OBSERVE
- The observer itself: change one property, remove one observation source, inject a failed gate row, interrupt after a persistent change. DESIGN (observer_recovery).
- Hediff stages and film severity in the existing health UI; patient-specific letters, standing alert. DESIGN (contact_ladder).
- Exact Thing IDs of dropped gear after dissolution; no corpse left. DESIGN (terminal_belongings).
- Archive dialog content and blank, primed, loaded seeker UI states. DESIGN (archive_field_choice).
- Visible held timer during engulfing. DESIGN (titan_engulf_rescue).
- Opinion and romance factors, inherited genes in a child. DESIGN (gene_effect_and_social).
- Temporary terrain conversion and its reversion at expiry. DESIGN (chunk_ground_and_age).
- Animation frames and facings of moving creatures (owner review). DESIGN (kit_and_titan_review).
4. REPEATS
- Random by design: gene rider, visitor trickle, oomb fission, gelatid shedding. DESIGN (gene_effect_and_social, visitor_arrival, oomb_wuum_behaviour). Rates are not read as bars (none stated in scenes).
- Length: film courses, seeker mark expiry, vat growth and an inherited outcome (a child) are long; the inherited outcome may need many in-game days. GUESS on length; DESIGN that each is observed.
- Side by side: matched treated and untreated arms on one map are the designed pattern. DESIGN (ordered_friend_rescue). Map-wide visitors and rain prevent many copies of those scenes on one map. GUESS.

## LeaningScrub
Sources: design/concepts/LeaningScrub/sheet.md, design/concepts/LeaningScrub/scenes.json (82 scenes; 52 "immediate", 30 "owner_review"; time budget "At most 6000 observed ticks per declared predicate/job phase"). Read titles, actions and expects only; design.md (49 KB) not read in full.
1. HOLD STILL
- Weather state: three windy twins, fog, Stall and Gale each change wind, audio, concealment, raid weight and creep; an unplanned weather change mid-scene spoils nearly every scene. DESIGN (scenes.json sc_wind_plain, sc_stall_wait, sc_raid_weight).
- Wind heading: the map heading is measured "within 0.1 degree of independent geometry"; scent, fire bias, shedding and glide all depend on it. DESIGN (sc_wind_plain, sc_scent, sc_fire_bias).
- People upwind: an upwind person alerts wildlife (scent flee); any colonist walking upwind of a wildlife scene spoils it. "reset lanes". DESIGN (sc_scent).
- Animal free will must stay untouched ("without mutating AI", "Let scheduling select prey"), so the hold is on who is nearby, not on AI. DESIGN (sc_witness_observer, sc_stall_predation).
- Vine creep and Walking advance on their own capped clock and on Gale onset; they invade cells under test. DESIGN (sc_creep, sc_walking, sc_home_routes).
- Fire: only the fire under test; lightning and other fires would confuse maker identification by witness or trail. DESIGN (sc_maker, ix_fire_accountability).
- Same-form bystanders must survive restore. DESIGN (floor_recovery).
2. FORCE
- Weather transitions on demand (Normal to Stall and back, Enter Gale twice, "Enter Gale naturally"). DESIGN (sc_stall_wait, sc_walking, sc_shedding).
- Fixed-seed opportunities: "Record 64 fixed-seed eligible production spread opportunities on/off". DESIGN (sc_fire_bias). "One seeded compressed breakdown opportunity". DESIGN (sc_working_wind).
- Compressed time with disclosed rate: coat growth, one season of arm regrowth, a 120-engine-day smother claim, tree shed. DESIGN (sc_tree_scratch, sc_arm_regrowth, sc_smother_claim).
- Map generation "normally" on three fresh Scrub maps for the native census, with chance one/zero map steps for the landmark tree. DESIGN (sc_native_cast, sc_island_land, sc_tree_landmark).
- An ordered expedition across hazards vs routine work that must refuse: close a detour and recalculate. DESIGN (sc_ordered_travel).
- A real lighter igniting a fire, witnessed and unwitnessed. DESIGN (sc_maker).
- Fault injection: an exception before and after staging and during restore. DESIGN (floor_recovery).
3. OBSERVE
- Draw-time: concealment shimmer, dust and fuzz motion in Gale, poses (twitcher spent, rearing), canopy sway, overhanging art clickable outside cells. DESIGN (sc_concealment, sc_gale_drawing, sc_twitcher, floor_visual).
- Sound: wind bed and day/night insect bed per weather, quiet in Stall. DESIGN (sc_wind_audio).
- Target selection (did the hunter choose a hidden animal?) and job choice (scent flee, rub, graze). DESIGN (sc_concealment, sc_stall_predation).
- AI perceptions and evidence edges for the giant's maker memory, read without mutating AI. DESIGN (sc_witness_observer).
- Route traces: job start, cancel, finish, cells, recalculation. DESIGN (sc_route_observer).
- Power: supplied load, stored energy, Gale output ratio. DESIGN (sc_working_wind).
- Raid weight multiplier (a hidden storyteller value). DESIGN (sc_raid_weight).
- Mid-air: shirrel glide, owner present only. DESIGN (sc_shirrel_flight).
- Timing: production-function timers over 6000-tick idle and busy windows; serialized bytes across 30 compressed lifecycle cycles. DESIGN (floor_runtime, floor_persistence).
4. REPEATS
- Random by design: fire spread direction (64 seeded opportunities), landmark chance, breakdown, egg hatch. DESIGN (sc_fire_bias, sc_tree_landmark, sc_proximity_hatch).
- Length: at most 6000 observed ticks per phase; compressed long clocks (years-long claim). DESIGN.
- Side by side: weather and heading are map-wide, so weather arms cannot share a map; "reset lanes" and plots are the designed parallel unit within one weather. DESIGN (sc_scent, ix_ecology_places "without ... cross-plot omniscience"). 30 of 82 scenes need the owner present (flight, Erupt). DESIGN.

## Bazaar trade window
Sources: design/RimMandrake/bazaar_trade_window_design.md (sections 3-7), design/validation_walks/RimMandrake/TheBazaar.md, src/RimMandrake/TheBazaar/Source/RM_Window_Bazaar.cs. THIN AS BUILT: the walk says only slice 1 ships; RM_Window_Bazaar.cs says "NOT WIRED IN", no Harmony patch on WindowStack.Add. The grid, price engine, haggle duel, banter and broker tab are designed and not built. No north-star bars are drafted (TheBazaar.md "No owner north-star bars are drafted"). What follows tests the design, for when it is built.
1. HOLD STILL
- Trader identity: the duel is seeded "from (world seed, trader stock seed, push index)"; a different trader or restocked stock changes every roll. DESIGN (design §5 Determinism).
- Negotiator Social skill: intel layers are gated at Social 3, 5, 7, 9; XP from pushes raises Social during the scene, which can cross a gate mid-scene. DESIGN (§4 table, §5 XP).
- Goodwill: patience is "+1 per 25 goodwill band"; a goodwill change mid-scene changes P. DESIGN (§5).
- Price drift: "one pass per in-game day" over seeded buckets, and event nudges (drought condition). Crossing a day boundary or a drought starting changes prices under test. DESIGN (§3 Tick).
- Protocol droid state: modules render only when a functional droid is in the party or at a comms console; downed, powered-down or imprisoned removes them. DESIGN (§4 Presence gate).
- Trader departure ends a lockout; the trader must not leave mid-scene. DESIGN (§5 Critical fail). Visiting caravans leave on their own timer. GUESS.
2. FORCE
- A trader on demand: an orbital trader, a caravan visit or a settlement trade, with the negotiator chosen. DESIGN (walk "needs a trade session driven through the bridge").
- Open the trade window as the player would, so the intercept (when built) swaps it in. DESIGN (RM_Window_Bazaar.cs hazard: the constructor runs SetupWith twice).
- Drive the UI: assemble a basket, search, sort, configure columns, press Push, confirm. DESIGN (§2, §5).
- A drought game condition to test an event nudge. DESIGN (§3).
- Install droid modules through Droidworks surgery (Recipe_InstallDroidPart). DESIGN (§4).
3. OBSERVE
- Window content: which columns, badges and intel rows are drawn, the patience meter as numbers with D1 or a face icon at Social 7+, greyed haggle controls after lockout. DESIGN (§4, §5). This is UI drawn only, not game state.
- Messages: "MessageCannotSellItemsReason" must fire once, not twice. DESIGN (RM_Window_Bazaar.cs).
- Hidden values: patience P, push success chance p, crit and crit-fail bands, the multiplier store and history ring buffer (WorldComponent). DESIGN (§3, §5).
- Final deal balance after the vanilla trade executes, to show the engine "never rewrites vanilla trade execution". DESIGN (§3 Read path, walk).
- Harmony patch ownership on WindowStack.Add and GetPriceFor. DESIGN (walk step 3).
- Banter text and its fallback when the CLI is absent. DESIGN (§6).
4. REPEATS
- Random by design: push success, crit, crit-fail; deterministic per seed, so "reload and re-push replays identically" is itself the check. DESIGN (§5). Many trader seeds are needed to see crit and crit-fail bands (15% and 5%). GUESS on count.
- Length: one session is short (seconds of real time, the game can be paused); price drift needs days. DESIGN (§3).
- Side by side: one trade window at a time; parallelism means many saves or many traders in sequence, not many copies on one map. GUESS.

## In-game LLM wiring
Sources: design/RimMandrake/llm_ingame_wiring_spec.md, design/RimMandrake/standing_rulings.md "In-game LLM access is the Claude Code CLI, never a hosted API key". The transport is BUILT (src/RimMandrake/Oracle/Source/OracleClient.cs, spec header) and its live proof is OWED. The consumers (gods, raids, flavor) are designed only; ORACLE_EXPERIMENT_SPIKE_1 (one god letter end to end) comes first (spec §5.2). This is plumbing, so the scene is about the path and the fallback, not a game mechanic.
1. HOLD STILL
- The per-consumer daily budget (gods 3, raids 1, flavor 2 per in-game day): earlier calls in the same day spend it, and a spent budget silently falls back. Start each scene at a known budget. DESIGN (spec §1 Cadence, §5.3).
- Other trigger events firing (satiation crossings, rituals, pressure clocks, first entries) that queue their own calls. DESIGN (spec §2a).
- The CLI on the game machine: its version and login state. Flags differ between versions (`--restricted` exits 1 on 2.1.228). DESIGN (spec §1 invocation).
- The memory store in the save (rolling lines per god, named antagonists): a scene must start from a known store, because the next prompt reads it. DESIGN (spec §1 Memory).
- The kill switch and the per-consumer enable flags. DESIGN (spec §1).
2. FORCE
- Fire the trigger event through its normal path (a satiation threshold crossing, a ritual end, a raid the storyteller would send), not a direct call to the Oracle. DESIGN (spec §2).
- Make the transport fail on purpose: CLI absent, timeout, garbage output, kill switch on, budget spent. Each must give the prescribed fallback. DESIGN (spec §0 law 2, §1).
- Swap the model for a deterministic stub that returns marker text. The spec says a "5-line local HTTP stub" (§4.2); that is superseded by the CLI transport, so the stub must stand in for `claude -p` (a stub executable on the path). GUESS on form.
- Feed a seeded bad output (for example "I am the Cradle-Mind", or a raid menu with an illegal faction or out-of-band points) to show the validator rejects it. DESIGN (spec §2a, §2b, §4.1).
3. OBSERVE
- Which path delivered the text: "a fallback firing looks identical to a delivery, so the stub's marker is the discriminator". DESIGN (spec §4.2). Failure "nothing logs to the player", so the bridge needs an internal trace of the request, the validator verdict and the delivery source. GUESS (the spec names no trace).
- Async timing: the call runs off the tick, delivery is "next tick or later", latency is seconds of real time. A check must wait in real time and in ticks. DESIGN (spec §1 Threading).
- Letter content and its attribution to one god; the raid that arrives (faction, points, arrival mode, composition) against the menu. DESIGN (spec §2a, §2b).
- The subprocess: exit code is the only success signal; stderr carries warnings on success. DESIGN (spec §1).
- Named-antagonist continuity across raids and across save/reload (the store is saved). DESIGN (spec §1, §2b).
4. REPEATS
- Model output is not deterministic by design; only the stub makes a check repeatable. Real-model quality is a judged trial, not a check. DESIGN (spec §4.3).
- Length: seconds of real time per call; budget proofs need an in-game day per reset (60000 ticks). DESIGN for the day budget; tick count is vanilla.
- Side by side: the budget is per consumer per day across the map, so parallel triggers spend one budget; copies side by side test coalescing, not independence. GUESS (coalescing is a RimAI precedent named in §3, not ruled for us).

## Pits as superdeep cells
Source: infrastructure/state/items/PIT_SUPERDEEP_COLLAPSE_1.md (read in full; abbreviated below as PIT). This is an umbrella item: the pit is a FlowWorks canal cell of depth D (0-4) and fill F, with no holder Thing. The children are built in part: holder retire, legacy retire, ladder prison door and cover fall rewire are done (PIT §criteria). Prison room, temperature softening, spikes, fill effects and the door family were open at last record. NOT READ: design/RimMandrake/flowworks_pits_unified_model_2026-10-02.md, relative_depth_climb_design_2026-10-12.md, and the FlowWorks north-star bars that now carry the pit bars.
1. HOLD STILL
- Fill: other FlowWorks flow (rain, river, an open sluice upstream) changing F in the pit cell. F > 0 at D=4 drowns; F > 0 at D1-3 slows more. DESIGN (PIT §the model).
- Ambient temperature and weather: pit temperature is "strongly coupled to ambient", so sun, night and seasons move the softening scene. DESIGN (PIT §5).
- Colonists who would rescue, feed, capture or shoot the occupant; the warden's adjacency to the lip; an armed occupant firing at whoever stands at the lip. DESIGN (PIT [B-item]).
- Wildlife and bystanders walking onto a covered cell and falling in. DESIGN (PIT §the model, Cover).
- The ladder state (raised or lowered) and the sluice or grate door state. DESIGN (PIT §ruling).
- Other mods that add moods or precepts, because the Exposed Prisoner thought piggybacks on vanilla's beggar-rejection structure. DESIGN for the structure (PIT [A-item]); interference is GUESS.
2. FORCE
- Natural entry onto a covered cell: a raider or animal must choose a path across the cover, by the least force (a raid whose path crosses it, a pawn ordered to walk there). DESIGN (PIT §ruling: "falling in, pushed, blasted").
- Involuntary entry by knockback or weapon blowback. DESIGN (PIT §ruling). Whether the game has a knockback source on the test list is GUESS.
- The "jump into pit" gizmo, with its warn and confirm. DESIGN (PIT §ruling, [G]).
- A capture down or convert down order from the lip, with a warden adjacent. DESIGN (PIT §1, [B-item]).
- Opening a sluice to flood an occupied pit; lowering and raising the ladder. DESIGN (PIT §3, §the model).
- Fluids in the cell: water, oil (and its ignition), poison. DESIGN (PIT §7).
- A trapped hostile mech, held, then released through a sluice. DESIGN (PIT [C]).
3. OBSERVE
- Draw-time only: the pawn sink offset of 0.05 cells per half metre of depth; "the pawn should visibly rise up and lower down"; every depth legible; spikes visible at the camera angle; fill tier (4 states) and fluid kind distinct; never reads as a building. DESIGN (PIT §depth ruling, six new bars). The sink is "measurable from a state read of the sink"; the rest is a judged picture.
- One-tick events: the fall itself, Sharp damage scaled by BodySize on a fall into a spiked cell only (never on walking up), drowning onset. DESIGN (PIT §6, [G]).
- Path decisions: whether a pawn can climb out (relative height; a person climbs 2), the depth × fill path cost matrix, flooded strictly slower than dry. DESIGN (PIT §the ruling settles 1, §3, [E]).
- Room state: an enclosed D=4 area is a room; trapped enemy versus prisoner once a prisoner bed is in it. DESIGN (PIT §1).
- Long process: pit temperature over hours, the RM_PitExposure hediff, resistance falling "swiftly". DESIGN (PIT §5, [H]). Its rate is not stated. GUESS on ticks.
- The size gate: pit width against BodySize decides if a creature gets out. DESIGN (PIT [J]).
4. REPEATS
- Random by design: spike damage goes through the normal damage pipeline (armour and body parts roll). DESIGN (PIT [G]). Recruitment and conversion rolls are vanilla.
- Length: a fall is one tick; softening runs for hours to days of game time (GUESS: 2500 ticks per hour, rate unstated).
- Side by side: separate pits on one map share weather and temperature, which is good for matched arms (sun pit against shaded pit). They must not share a liquid body, because fluid is typed per liquid body. DESIGN (PIT [F]).

## Direct Sun heat and shade
Source: design/RimMandrake/unified_direct_sun_heat_2026-10-19.md (abbreviated DSUN; read §0, §3-§6; §1-§2, §7-§8 only by heading). The model was ruled on 2026-10-19, and at that date "Nothing in it is built" (DSUN §3). I did not check how far the build has come since. Code lives in src/RimMandrake/CreatureBehaviors/Source/ (RM_MapComponent_ShadeGrid, RM_SunHeatMath). Not read: design/RimMandrake/tree_shade_model_2026-10-19.md, which DS8 depends on.
1. HOLD STILL
- Weather: every weather has a sun factor (Bloom 0.2, Dune Gale 0.2, vanilla overcast patched). A weather change mid-scene changes the offset. DESIGN (DSUN DS6).
- Sun elevation E: fixed per tile on the shipped world. On a world with day and night, Direct Sun is off. The scene must sit on a pinned-sun map, or it reads zero. DESIGN (DSUN DS7).
- Geometry changing near the cell under test: built or deconstructed walls and roofs, plants that grow or are cut (tall plants cast shade), a parasol carrier moving. DESIGN (DSUN DS3).
- Ambient air temperature (vanilla GameCondition_TemperatureOffset on the Forge, Scald, Fever Wood and Greentide), other temperature conditions (heat wave, cold snap), and coolers. DESIGN (DSUN §3 Ambient heat).
- The pawn's own state: body size (the offset scales by bodySizeFactor), apparel and shade gear, whether it stands still. DESIGN (DSUN DS2, DS4).
- Settings: master switch, strength dial, zenith 55 °C, weather dims, and the other toggles. DESIGN (DSUN §5).
2. FORCE
- A map on each of several tiles to get distinct E: the plan names Long Shade, Pyrelands and Forge. DESIGN (DSUN §6 L1). With no worldgen allowed, this means existing tiles in the shipped world. Standing ruling.
- Place a wall, a roof, a tent, a tall plant and a parasol carrier to create an open cell, a roofed cell, a parasol cell and a lee. DESIGN (DSUN §6 L1).
- Change the weather on demand to read the weather factor. DESIGN (DSUN DS6).
- A pawn left in the sun long enough to show the heat load and its own choice to seek shade (sun pathing, shade hop). DESIGN for the toggles (DSUN §5); the behaviour detail is in SOLAR_HEAT_EXPOSURE_1, not read.
3. OBSERVE
- A per-cell grid: the shade map (covered, cast shade, open) and the offset per cell, read as state. The lee length is height / tan E (at 14° about four times the height; at 85° none). DESIGN (DSUN §6).
- The same numbers across maps at the same E ("equality across biomes"). DESIGN (DSUN §6).
- The thermometer moving by the air-heat offset on the Forge. DESIGN (DSUN §6 L1).
- The sun-load gizmo text ("Direct Sun"). DESIGN (DSUN §4). This is UI content.
- Draw-time: whether a lee is shown on screen is not stated in this doc. GUESS.
- Long process: heat load builds over hours. Its rate is not given here. GUESS.
4. REPEATS
- Not random by design: the offset is a pure function (55 × sin E × factors). DESIGN (DSUN DS2). Pawn behaviour on top of it is the AI's.
- Length: a state read is instant once the grid is built; a heat-load run is hours of game time. GUESS on ticks.
- Side by side: many probe cells on one map work well, because they share E and weather (matched arms: open, roof, parasol, lee). Different E needs different maps. DESIGN (DSUN §6 L1).
- Tuning is an owner-watched sitting (L2), not a check. DESIGN (DSUN §6 L2).

## Creature flight
Sources: skills/rimworld-modding/references/flight.md (abbreviated FL), design/RimMandrake/standing_rulings.md "If it flies in the fiction, it flies in the game" (abbreviated SR). This is a cross-mod rule, not a mod. It applies to every flyer (Contagion's airborne_stats, Murrelith and others). The binding limit for the bridge: "NEVER live-test a flyer's flight without the owner present". A solo bridge pass may make only a deterministic STATE read of Pawn_FlightTracker (`jawa/pawn_flight` exists). Any visual check is a joint session, or it waits. DESIGN (FL, SR).
1. HOLD STILL
- Job starts: flight starts by chance at a job start (flightStartChanceOnJobStart, for example 0.1), so other jobs, other orders and interruptions change when it flies. DESIGN (FL vanilla shape).
- Map edges: canLeaveMapFlying lets a bird leave the map in mid-scene. DESIGN (FL).
- Predators, hunters and tamers acting on the flyer; weather and temperature are GUESS.
- Alternate coats: a kind with alternateGraphics has one flight look for all coats unless C# swaps it. A scene must hold the coat fixed. DESIGN (FL Engine facts, RM_Murrelith).
2. FORCE
- A takeoff by the least force: give the animal a job, or many jobs, and let the vanilla chance decide. A forced takeoff tests the tracker, not the trigger. DESIGN for the chance (FL); the force rule is GUESS, by analogy with FeverWood's "a forced transition proves nothing about the normal trigger".
- A forced landing (ForceLand), to check the 0.36-cell drop in one tick that the decompile predicts, with vanilla Chicken as the baseline. DESIGN (FL Engine facts: "computed, not seen running").
- Save and load in mid-flight. DESIGN (FL "save/load safety").
3. OBSERVE
- State in mid-air: CanEverFly (MaxFlightTime > 0), flying or landing, lerpTick, time left and cooldown. DESIGN (FL; tool `jawa/pawn_flight`).
- Draw-time only: the flip-book frame shown per facing (north, east, south; west mirrors), the draw size multiplier, the grounded graphic coming back on landing, and the double-held last frame. DESIGN (FL). Owner-attended only. SR forbids screenshot hunts.
- One-tick events: takeoff and the landing drop. DESIGN (FL).
- Offline playback of the flip-book frames, which is not a live check, is suggested by FL ("an offline playback must baseline vanilla Chicken"). DESIGN.
4. REPEATS
- Random by design: the start chance per job start. MaxFlightTime and FlightCooldown are in seconds (Locust 10 and 5). DESIGN (FL). Ticks: GUESS 60 per second.
- Length: one flight is about 10 s of game time (600 ticks). GUESS on conversion.
- Side by side: many flyers on one map give many takeoff samples per minute of state reads, which is good for the start-chance rate. A visual judgement stays one joint session. GUESS.

## Cross-mod table
Key: Con Contagion, Cau Cauldron, Sti Stillsand, Fev FeverWood, Gel GelatinousSlime, Lea LeaningScrub, Baz Bazaar, LLM in-game LLM wiring, Pit superdeep pits, Sun Direct Sun, Fly creature flight. Counts are my reading of the sections above (11 subjects). A design-only subject (Baz, LLM, Sun) counts where its design states the need.

| need (plain words) | mods that need it | count of mods |
|---|---|---|
| repeatable randomness: seed the draw, or run enough trials to see a rare branch (or stub a non-deterministic source) | Con, Cau, Sti, Fev, Gel, Lea, Baz, Pit, Fly, LLM | 10 |
| labelled compressed time: jump the clock or speed long processes (days, seasons, expiries) and say so in the result | Con, Cau, Sti, Fev, Gel, Lea, Baz, LLM, Pit, Sun | 10 |
| give ordinary player orders the way a player would (orders, gizmos, architect menu, trade UI) | Con, Cau, Sti, Fev, Gel, Lea, Baz, Pit, Sun | 9 |
| fire an event through its normal worker or trigger (incident, raid, trader, weather turn, god trigger) and hold back every unplanned one | Con, Cau, Sti, Fev, Gel, Lea, Baz, LLM, Pit | 9 |
| read hidden internal values (eligibility, chance, dose, patience, flight tracker, validator verdict) without changing them | Con, Sti, Fev, Lea, Baz, LLM, Pit, Sun, Fly | 9 |
| set the weather and hold it for the whole scene; change it on demand | Con, Cau, Sti, Fev, Gel, Lea, Pit, Sun | 8 |
| save and reload in the middle of a process, with deadlines, stores and seeds intact | Con, Cau, Sti, Fev, Lea, Baz, LLM, Fly | 8 |
| keep bystanders out: wildlife, predators, haulers, wandering colonists, without freezing the actors' own AI | Con, Cau, Sti, Fev, Gel, Lea, Pit, Fly | 8 |
| read UI content: inspect text, gizmo text, dialogs, settings screen, trade window, health tab | Con, Cau, Sti, Fev, Gel, Baz, Pit, Sun | 8 |
| an owner-attended session for what only his eye can judge (flight, owner_review scenes, tuning, model quality) | Con, Cau, Fev, Gel, Lea, Fly, Sun, LLM | 8 |
| read a per-cell grid over ticks (shade, gas, sand, fill and depth, flash set, temporary terrain) | Con, Cau, Sti, Fev, Gel, Pit, Sun | 7 |
| captures at play zoom judged by someone who did not stage them (draw-time effects, poses, sink offset) | Con, Cau, Sti, Gel, Lea, Pit, Fly | 7 |
| trace jobs, paths, targets and job uptake per pawn over a window | Con, Cau, Fev, Gel, Lea, Pit, Fly | 7 |
| matched arms side by side on one map (exposed and sheltered, treated and untreated, disjoint pools or lanes) | Con, Cau, Fev, Gel, Lea, Pit, Sun | 7 |
| set mod settings, assert them, flip one switch and see only its feature stop | Con, Cau, Fev, Baz, LLM, Sun | 6 |
| count letters and messages exactly (once, never, cooldown) | Con, Cau, Sti, Gel, Baz, LLM | 6 |
| a fast restore of one baseline for many replays and scene recovery after a fault | Cau, Sti, Fev, Gel, Lea, Baz | 6 |
| validate the observer itself, with a lossless log tap and an internal trace of silent paths | Cau, Sti, Fev, Gel, Lea, LLM | 6 |
| read health: hediff severity, body parts, damage dealt | Con, Cau, Fev, Gel, Pit | 5 |
| a second map (or several tiles) loaded as a control for map-wide states | Con, Sti, Fev, Lea, Sun | 5 |
| things in mid-air: knockback flight, glide, flyer state (state read only; visual with the owner) | Con, Cau, Gel, Lea, Fly | 5 |
| a sound and audio event trace (which sound played, where, how often) | Con, Sti, Fev, Lea | 4 |
| hold the hour or the sun elevation | Con, Sti, Sun | 3 |
| map generation on a disposable fixture through the real gensteps, never worldgen | Cau, Fev, Lea | 3 |
| 40-colonist scale with hot-path timing | Cau, Sti, Lea | 3 |
| pawns and items off the map (caravans, carried pawns, settlement stock) | Sti, Fev, Gel | 3 |
| hold or read temperature (ambient coupling, air-heat condition) | Pit, Sun | 2 |
| hold the wind heading within a day | Cau, Lea | 2 |
| hold power supply | Gel, Lea | 2 |
| wait in real time for async work off the tick (CLI subprocess, banter) | LLM, Baz | 2 |

What I could not read: the concept design.md files in full (LeaningScrub's 49 KB design.md in particular); only sheet.md and scenes.json per concept. The Bazaar has no built slices past slice 1 and no scenes. The LLM consumers are unbuilt. Pits: flowworks_pits_unified_model_2026-10-02.md, relative_depth_climb_design_2026-10-12.md and FlowWorks' north-star pit bars. Direct Sun: tree_shade_model_2026-10-19.md, and the current build state after 2026-10-19. Flight: no per-creature flight designs.
