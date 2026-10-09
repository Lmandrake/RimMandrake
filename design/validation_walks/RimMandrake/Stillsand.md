# RimMandrake: Stillsand — validation walk
subject: src/RimMandrake/Stillsand  (dev source folder, own About.xml packageId `mandrake.rm.stillsand`, which is never deployed standalone: the biome ships COMPOSED inside `mandrake.rm.biomes`, RimMandrake: Baroque Biomes, wave 2 of `src/RimMandrake/Biomes.compose.json` — test that) <!-- walklint-ok: mandrake.rm.biomes is the GENERATED composed packageId, built by deploy_custom_mods.py --compose biomes, not a folder under src/ -->
feature: biome-core
deps: `brrainz.harmony`; the composed mod carries FlowWorks (`mandrake.rm.flowworks`), Creature Behaviors (`mandrake.rm.creaturebehaviors`), Environmental Hazards (`mandrake.rm.environmentalhazards`) and Moving Dunes; no Utinni layer (the canon cast is patch-added by `mandrake.rut.patches` and is NOT in this script)
list: baroque_wave0 (modset_builder tier: the bridge + `mandrake.rm.biomes` and its dependency closure, all five DLCs). No new tier is needed. <!-- walklint-ok: mandrake.rm.biomes is the GENERATED composed packageId, not a folder under src/ -->
status-hint: STILLSAND_RM_MOD_BUILD_1 and everything built on it — the Extreme Desert biome: a corrugated ochre plain under a pinned sun; the zuurrik blood-waker, the dune gale and dust devils, giant skeletons, precious caves, the sun-fed glass chain, the water the sand remembers, sand-buster eruptions, the muurrok, glare-blind and sun goggles; script = `src/RimMandrake/Stillsand/validation.py`, plan = `northstar_plan.py`, selftest = `selftest_stillsand.py`

Sources for every line below: the mod's `About/About.xml` description, the C# headers under `src/RimMandrake/Stillsand/Source/`, the defs under `src/RimMandrake/Stillsand/Defs/` and `Patches/`, `design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md`, and the live-session records `Transient/LIVE_SESSION_2026-10-01.md` and `Transient/LIVE_SESSION_2_2026-10-01.md` (the site recipe and the live shapes are theirs).

## must be true
Every line ends in `→ chain.component` (a suite component that reads the state back) or `→ UNCOVERED: why`.

The site
- A quicktest world's current tile, set to `RM_Stillsand` and regenerated, yields a map whose biome is `RM_Stillsand` (a discarded BiomeDef or a tile edit that did not take reads here). → site.site_stillsand_map
- Generating that map logs at least one `[Stillsand] precious cave` line: the two precious-cave gen steps are wired onto the biome and ran (STILLSAND_PRECIOUS_CAVES_1). → site.site_cave_logged
- A fresh map carries no more giant skeletons than `maxSkeletonsPerMap`. → site.skeleton_gen_within_cap
- With `genStepEnabled` off, a regenerated map logs no precious-cave line (one regeneration serves both toggle lines below). → caves.caves_regen_both_off, caves.genstep_off_no_cave_line
- With `skeletonPlacementEnabled` off, the regenerated map carries no giant skeleton. → caves.skeleton_placement_off_none
- A cave's mouth faces away from the sun, the table roll's contents are present, the "Rock island" letter names the outcrop and bearing, and `yardangShapingEnabled` and `torEnabled` change the outcrop. → UNCOVERED: geometry and letter text are not state-readable through the bridge; STILLSAND_PRECIOUS_CAVES_LIVE_1 proved 10 of 10 caves by log and layout, and the table roll needs ten regenerations for a statistic

Load and wiring
- Every def this mod ships (things, 22 pawn kinds, plants, hediffs, weathers, the game condition, four incidents, recipes, the job, three gen steps, the sound, the body parts, the damage def, the biome) resolves in the live game; none is silently discarded for a bad field or a missing comp type (STILLSAND_LOAD_DEF_ERRORS_1: `RM_KneelOllim` was discarded for a bad TreeCategory). → defs.defs_resolve
- The five precious-cave defs (this mod's own Def subclass) resolve. → defs.custom_defs_resolve
- `RM_Stillsand` has `animalDensity` above 0 and carries the five extensions (sun heat, pinned sun, dune field, skeleton biome, sand-remembers-water) and the three extra gen steps its patches add. → defs.biome_row
- Every row of the biome's inline roster (15 animals, 4 plants) resolves to a spawning wild animal or plant, and a name that is not in the biome reads `absent` (the sanity probe). → defs.biome_roster
- The four giants (oommok, muurrok, guzzka, vozzik) carry `RM_SkeletonRemainsExtension`. → defs.giants_skeleton_wired
- The unfertilized guzzka egg carries the water-volume comp (the canteen egg). → defs.water_egg_patched
- The sand-buster eruption is confined to the Stillsand by its own `allowedBiomes`. → defs.eruption_biome_gate
- The acoustic-scanner payload on `RM_Stillsand`. → UNCOVERED: guarded by `PatchOperationFindMod` on `mandrake.rm.acousticscanner`, which the baroque_wave0 tier does not carry
- The canon cast (krayt, war wyrm, kreetle ...) and the five pack animals. → UNCOVERED: Star Wars IP, patch-added by `mandrake.rut.patches` (Q11a); not on this tier
- All 30 Mod Settings fields across the seven settings classes exist and read their shipped defaults; a nonexistent field fails loudly. → settings.defaults
- The log carries no `Stillsand` error and no cross-reference or config error naming one of this mod's `RM_` defs. → log.log_clean

The sun
- The Stillsand pins its sun: the pinned-sun component is active, the elevation sits inside the biome's 2-85 degree clamp, and the sky glow is 1 at two hours of the day twelve hours apart (no night ever falls). → sun.sun_pinned_no_night
- An open sand cell reads sun exposure of at least 0.6 (what glare-blind needs). → sun.sun_open_sand_full_exposure
- Above 55 degrees of sun elevation a roof gives cover (exposure at most 0.05); below it only a lee does, by design. → sun.sun_roof_cover_above_55deg
- Heat shimmer, the mirage and the chasing-water state, and the heat offset itself. → UNCOVERED: owned and scripted by Creature Behaviors; the Stillsand supplies only the extension values (read by defs.biome_row)

Fauna and flora
- Each of the 22 shipped pawn kinds spawns a living pawn of that kind (OORRIK_PAWNGEN_NRE_1: `RM_Oorrik` once threw in pawn generation). → fauna.fauna_spawns
- The soorrak can fly (`MaxFlightTime` above 0). State read only; flight in the air is never live-tested unattended. → fauna.soorrak_can_fly
- Six wild soorraks run 3000 ticks with no error naming Soorrak and none in `Pawn_FlightTracker.Notify_JobStarted` (SOORRAK_FLIGHT_JOBSTART_NRE_1). → soorrak.soorrak_no_exceptions
- A soorrak that stays on the map moves or runs a real job; one that reads only the 1-tick filler `Wait_MaintainPosture` for 3000 ticks is stuck (the idle-loop defect of the 2026-10-01 session). → soorrak.soorrak_not_stuck
- Every shipped plant (ollim, kneel ollim, light-pipe nub, glasscrust, hourbloom) stands when placed. → flora.flora_spawns
- The loomma's sunstruck clock rises in open sun and is lower under a roof. → loomma.loomma_sunstruck_open_vs_roofed
- A shade-mite following an oommok, the aurrok's strike, the guzzka's lair behaviour, the vaalok as a trade animal. → UNCOVERED: behaviours of the creature-behaviour engine, scripted there; the guzzka on its clutch in a lair was proven live for one map (STILLSAND_PRECIOUS_CAVES_LIVE_1)

The sand swimmers
- A vekka standing on Sand is `RM_SandSubmerged`; one on Gravel is not. → sandswim.vekka_submerges_on_sand
- A swimmer that kills a victim on sand leaves an `RM_Filth_DisturbedSand` funnel and a "Taken under" letter (SANDSWIM_TAKE_FUNNEL_NEVER_PLACED_1). → sandswim.vekka_take_leaves_funnel
- The take's dive message and the swimmer leaving the map. → UNCOVERED: a message is not state-readable; the take letter and the funnel stand for it

The zuurrik
- Fewer blood cells on sand than `zuurrikBloodThreshold` wake nothing. → zuurrik.zuurrik_below_threshold_dormant
- Twelve blood cells on sand wake a swarm of `RM_Zuurrik` within 1800 ticks. → zuurrik.zuurrik_wakes_on_blood
- The swarm strips the blood. → zuurrik.zuurrik_strips_blood
- With `zuurrikEnabled` off a stain wakes nothing, and with it back on the same stain does. → zuurrik.zuurrik_toggle_off_no_wake
- The swarm never attacks an unwounded pawn, and re-buries with a dust puff after three quiet polls. → UNCOVERED: the live run of 2026-10-01 was inconclusive (three unhurt hares vanished with no corpse beside the swarm); re-burial needs a swarm that runs out of blood, which a cheap fixture cannot arrange

The sun-fed glass chain
- A sun furnace on open sand reports `Sun: NN%`. → glass.glass_site_ready, glass.sun_table_reads_sun_in_open
- A roofed sun furnace reports that it is under a roof. → glass.sun_table_roofed_idle
- The `WorkTableWorkSpeedFactor` stat part is applied: a sun furnace works at more than twice the open-sun speed of a roofed one. → glass.furnace_work_speed_tracks_sun
- `sunWorkSpeedMultiplier` 2 doubles the furnace's work speed. → glass.sun_work_speed_multiplier_scales
- `sunFurnaceEnabled` off makes the furnace read "Disabled in Mod Settings". → glass.sunfurnace_toggle_off_disabled
- `lensBenchEnabled` off makes the lens bench read "Disabled in Mod Settings". → glass.lensbench_toggle_off_disabled
- `solarOvenEnabled` off makes the solar oven read "Disabled in Mod Settings". → glass.solaroven_toggle_off_disabled
- The four recipes (melt sun glass, melt lens glass, grind precision lens, grind pearl lens) produce what they say at a staffed bench in the sun. → UNCOVERED: the recipes are checked only to resolve (defs.defs_resolve); a staffed bench needs a crafter with skill and a sun that clears 30 percent

The water the sand remembers
- Water poured into Stillsand sand sows `RM_Hourbloom`. → water.pour_blooms_on_sand
- With `bloomOnPour` off a pour sows nothing. → water.pour_toggle_off_no_bloom
- A pour on gravel sows nothing (only remembering sand blooms). → water.pour_on_gravel_no_bloom
- Wet sand draws the swimmers for `swimmerDrawHours`, and a gale wipes every wet cell. → UNCOVERED: `RM_MapComponent_WetSand` has no bridge reader
- The Sun-Debt ledger, its mood line and its goodwill. → UNCOVERED: an RM tier ships no `RM_WaterLedgerDef` (the ledger rows are inert by design); the two ledger toggles are checked read/write only (settings.ledgerEnabled_roundtrip, settings.ledgerIncidentWeighting_roundtrip)

Skeletons and the horizon
- A giant's corpse older than `corpseToSkeletonDays` becomes its skeleton where it fell. → skeleton.corpse_becomes_skeleton
- With `corpseToSkeletonEnabled` off the corpse stays a corpse. → skeleton.corpse_stays_when_toggle_off
- A raid or a neutral group about to arrive on the Stillsand is announced by a "Dust on the horizon" letter and arrives `horizonWarningHours` later, not at once. → horizon.horizon_warns_then_arrives
- With `horizonWarningsEnabled` off it arrives at once with no letter. → horizon.horizon_toggle_off_vanilla
- A warned group that never arrives (its incident fails or times out) gets a "The dust settled" letter once the queue's retry window is over, the plume standing until then, and one that arrives gets no such letter; `dustSettledLetterEnabled` off leaves only the fading plume (DUST_SETTLED_LETTER_1). → horizon.horizon_dust_settled_letter (timing: offline `selftest_skeleton_burial.py` Horizon checks, RM_HorizonMath)
- The dust plume at the entry cell, the bone harp's moan, and the skeleton's cast shade. → UNCOVERED: visual and audio; the cast shade is Creature Behaviors' shade grid
- `boneHarpEnabled` exists, defaults on and is writable. → settings.boneHarpEnabled_roundtrip

The dune gale and dust devils
- `RM_DuneGale` can fire on a Stillsand map. → gale.gale_incident_fires
- With `galeEnabled` off it cannot. → gale.gale_toggle_off_refuses
- A started gale runs herald weather then gale weather; at its end the log carries the `[Stillsand] dune gale ended` line with sand moved, and exactly one emergence letter. → gale.gale_phases_and_aftermath
- In the gale a pawn's sun exposure is at most half its clear-sky value. → gale.gale_dims_sun_exposure
- With `emergenceEnabled` off the gale uncovers nothing. → gale.gale_emergence_off_quiet
- A dust devil moves and then disappears on its own within 3000 ticks, leaving no thing behind. → devil.devil_moves_and_expires
- With `dustDevilsEnabled` off the dust-devil incident cannot fire. → devil.devil_toggle_off_refuses
- The gale's carry-off is a taker of FlowWorks' shared hold-and-return service (kind `gale`): the service holds the pawn, writes the carry/return letters, leaves a ground trace where it was taken and brings it back from the downwind edge (TAKEN_BY_LAND_SERVICE_1; the river is the other taker). → gale.gale_carry_is_a_taker_of_the_shared_service (the take itself: UNCOVERED: a random event on a crest, see the next line)
- Abrasion, carry-and-return, static, seeding and the emergence rows' individual toggles. → UNCOVERED: random events on a crest or an MTB; the four toggles `abrasionEnabled`, `carryEnabled`, `staticEnabled`, `seedingEnabled` are checked read/write only → settings.abrasionEnabled_roundtrip, settings.carryEnabled_roundtrip, settings.staticEnabled_roundtrip, settings.seedingEnabled_roundtrip

Event creatures
- Firing `RM_MuurrokEmergence` sends the "A line of glare" letter and a `RM_Muurrok` is on the map after the warning. → muurrok.muurrok_emergence_fires
- A muurrok's mirror beam, cast at a target 8 cells away under Clear weather, leaves it `Burn` (MUURROK_BEAM_NO_DAMAGE_1). → muurrok.beam_burns_target
- With `mirrorBeamEnabled` off the beam burns nothing. → muurrok.beam_toggle_off_blocked
- The leviathan incidents' own toggles and odds, the Visits memory, and the krayt attack. → UNCOVERED: held in private static dictionaries no tool reads; the krayt is `mandrake.rut.patches`
- Firing `RM_SandBusterEruption` leaves a tunnel marker, an "Sand Buster Eruption" letter and then a mound. → eruption.eruption_tunnel_then_mound
- The sand-buster castes (ruukka, oorrik) spawn from the mound over days. → UNCOVERED: a multi-day clock; both kinds spawn (fauna.fauna_spawns)

Glare and heat gear
- A bare-eyed non-Jawa colonist standing in full Stillsand sun gains `RM_GlareBlind`. → glare.glare_site_ready, glare.glare_blind_gained_in_open_sun
- A colonist in `RM_SunGoggles` standing beside them gains at most a quarter as much. → glare.goggles_block_glare_blind
- A Jawa never gains glare-blind. → UNCOVERED: `RM_GlareAdapted` is granted by `RSW_Jawa_GlareAdapted.xml` in the Star Wars layer, not on this tier
- `RM_CoolingDraught` widens the comfortable temperature range by 8 degrees and removing it restores it. → cooling.cooling_draught_widens_comfort
- Something gives the draught. → UNCOVERED: nothing does today (the still is owed: STILLSAND_SOLAR_STILL_1)
- `genStepEnabled`, `skeletonPlacementEnabled`, `corpseToSkeletonEnabled`, `horizonWarningsEnabled`, `zuurrikEnabled`, `mirrorBeamEnabled`, `bloomOnPour`, `galeEnabled`, `emergenceEnabled`, `dustDevilsEnabled` and the three table toggles have driven effects (above); `yardangShapingEnabled`, `torEnabled`, `ledgerEnabled`, `ledgerIncidentWeighting` are checked read/write only. → settings.yardangShapingEnabled_roundtrip, settings.torEnabled_roundtrip, settings.ledgerEnabled_roundtrip, settings.ledgerIncidentWeighting_roundtrip
- The biome reads as a corrugated ochre plain; the dust devil, gale, skeletons and sun furnace read as the descriptions say. → UNCOVERED: visual; left to the judge pass (debug_process.md section 4)

## the walk
1. [B] Tier and one-command session: `python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod Stillsand --tier baroque_wave0 --plan src/RimMandrake/Stillsand/northstar_plan.py --compose` (stops the game, writes the tier, deploys the composed biomes, launches via Steam, waits for `Bridge token:`, starts a quicktest world, runs the driver) → results JSON in `Transient/northstar/`.
2. [B] The suite's first chain turns the quicktest tile into a Stillsand map (`jawa/world_tile_set`, `jawa/world_commit`, `Actions\Regenerate Current Map`) and every later chain runs on it.
3. [L] Player.log after load: no `Config error in` a `RM_` Stillsand def, no `Could not resolve cross-reference` naming one, no `Exception in ConfigErrors()` for `RM_Stillsand`; the first exception of the load is not ours   # defs.defs_resolve, log.log_clean
4. [D] `jawa/get_defs`, `jawa/biome_probe`, `jawa/shadegrid_read` and `jawa/inspect_string` reads as listed above.
5. [B] Chains with a clock (zuurrik, gale, devil, muurrok, eruption, horizon, soorrak, skeleton) advance ticks; the whole suite is about 60,000 ticks.
Offline: `python3 src/RimMandrake/Stillsand/selftest_stillsand.py` runs the suite against a scripted fake game: healthy, then once per mod behaviour broken, each of which must turn exactly its own component red.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet; whether the Stillsand reads as a still ochre plain under a sun that does not move, whether the gale reads as a gale and the zuurrik as a boiling stain, are his to rule. A functional script needs none: the lines above are the agent layer.

## anti-guessing notes
RULED OUT: "the Stillsand has a fixed sun" — the pinned sun's elevation comes from the map tile's latitude (STILLSAND_SUN_FROM_LATITUDE_1), and the quicktest tile is random (latitudes 37.9 and 61.9 were rolled on 2026-10-01). Every sun-dependent bar reads UNMEASURED, never FAIL, when the site's sun is too low for the claim (sun tables below 30 percent, glare-blind below 0.6 exposure, a roof below 55 degrees); the site note records the latitude.
RULED OUT: "`jawa/world_tile_set` alone changes the biome of the current map" — it changes the tile; only `Actions\Regenerate Current Map` makes a map of that biome (LIVE_SESSION_2_2026-10-01.md). The regeneration wipes the colonists, so the site re-plants three and every chain keeps one alive (`_ensure_colonist`).
RULED OUT: "the planted colonists survive the run" — the biome's heat killed them in the 2026-10-01 session and a map with nobody home ends the game; the site tile is set to 15 C and `_prep` spawns a colonist when none lives. Every chain spawns its own actors.
RULED OUT: "`BiomeDef.wildAnimals` is readable through `jawa/get_defs`" — it is non-public (LIVE_SESSION_2); defs.biome_roster reads the RESOLVED roster with `jawa/biome_probe`, whose `findResults` state is `spawning`, `zeroed` or `absent`.
RULED OUT: "`fire_incident dryRun` canFireNow tells whether an incident will fire" — it read false for both leviathan incidents before they fired, unexplained (LIVE_SESSION_2). The muurrok and the eruption are fired for real and read as state; the gale and the dust devil use dryRun only for a toggle pair whose ON arm is its own control (UNMEASURED if the ON arm is false).
RULED OUT: "a corpse of a killed pawn lingers `corpseToSkeletonDays` of real time" — the setting is set to 1 day and the clock is jumped with `jawa/time_set_ticks`, then one Long tick of play lets the scan run (it runs at `ticksGame % 2000 == 37`).
RULED OUT: "the Return ledger is part of the RM tier" — `RM_WaterLedger` is inert without a `RM_WaterLedgerDef`, which only a tier above ships; the Mod Settings panel shows no debt rows at the RM tier.
RULED OUT: "`jawa/mod_settings_field` reaches only static fields" — it reads both; `RM_StillsandSettings` is an instance class found through the assembly-matched Mod handle. The lookup tries every Mod handle in the assembly, so `Mod.GetSettings<T>` can log a settings-type error for the other handles; log_clean ignores lines that name `GetSettings`.
RULED OUT: "the in-game log buffer keeps everything" — `jawa/drain_log` reads the newest 1000 entries and RimWorld stops logging at a message limit. `_log_lines` reads `Reached max messages limit` first and records UNMEASURED if it is there, so a missing cave line, error or gale-end line is never read as absence.
RULED OUT: "`list_pawns` marks the player's pawns by faction name" — the row carries `faction` as the faction defName and a separate `isPlayer`; the suite uses `isPlayer`.
RULED OUT: "the funnel is placed by `FilthMaker` on sand" — it was not: Sand, SoftSand and RM_DeepSand have `filthAcceptanceMask = Unnatural` and the funnel filth uses `placementMask Terrain` (SANDSWIM_TAKE_FUNNEL_NEVER_PLACED_1); fixed and proven live on 2026-10-01, and sandswim.vekka_take_leaves_funnel is the guard if it regresses.
RULED OUT: "the zuurrik wakes on any blood" — it counts blood on SAND cells map-wide against the threshold (8) and clusters within 7.9 cells; the below-threshold control puts 3 cells, the wake test 12.
ASSUMED (source comments, not measured here): the muurrok's `Burn` is the hediff of the `RM_MirrorGlare` damage def (the item text); beam_burns_target reads `Burn` on the target, and a different hediff name would read FAIL until the first run corrects the walk.
UNPROVEN live shapes (the first run settles them; each reads UNMEASURED or FAIL with its reason, never PASS, when absent): `jawa/storyteller_fire` in the deployed companion (it sits behind a build flag), `jawa/get_defs` with a custom Def subclass type name (the five cave defs), `jawa/stat_cache_bust` reaching the work-table stat, `jawa/pawn_use_verb` `cast` against a non-hostile wild target, the "Dust on the horizon" letter label, `Corpse_<race>` as the corpse def name.
Not driven because no cheap fixture: carry-and-return of gale-borne pawns, abrasion and static, the ledger, wet sand drawing swimmers, the leviathan toggles, the staffed glass bills, the acoustic payload, the Jawa glare adaptation, every visual bar.
