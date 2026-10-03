# RimStarWars: Geonosian Brain Worms — validation walk
subject: src/RimStarWars/BrainWorms  (packageId `mandrake.rsw.brainworms`)
deps: Harmony not used; loadAfter `mandrake.rm.proximityhatch` (optional egg-cluster comp, MayRequire on a `<li>`)
list: minimal tier plus this mod
status-hint: BRAIN_WORMS_FIRST_SCRIPT_1 — first script drafted, never run live

Sources: `src/RimStarWars/BrainWorms/About/About.xml` description, `Defs/**`, `Patches/**`, `Source/*.cs`, `design/RimStarWars/brain_worm_spec.md`.

## must be true
- Every def the mod ships (hediff, mental state, think tree, worm race and kind, egg cluster and shell and projectile, cargo incident, surgery recipe) loads and resolves; a bogus name reads notFound. → defs_resolve.every_shipped_def_resolves
- The custom hediff comps (progress, puppeteer, whispers) loaded rather than being dropped. → defs_resolve.custom_comp_types_loaded
- Every Mod Settings field (`cargoIncidentEnabled`, `eggProjectileEnabled`, `progressionSpeedMultiplier`, `coldKillRateMultiplier`) round-trips. → settings_roundtrip.cargoIncidentEnabled_round_trips, settings_roundtrip.eggProjectileEnabled_round_trips, settings_roundtrip.progressionSpeedMultiplier_round_trips, settings_roundtrip.coldKillRateMultiplier_round_trips
- The infection is a three-stage ladder: latent (0), influenced (0.35), puppeted (0.8). → ladder_wiring.stage_ladder_live
- A living host given the infection carries it; a clean pawn does not. → infection_state.infected_pawn_carries_hediff_clean_control_does_not
- Severity advances while the host is warm. → infection_state.severity_advances_while_warm
- A host at puppet severity is held in `RSW_BrainWormPuppet`. → puppet_state.host_at_puppet_severity_is_held_in_puppet_state
- Surgery (`RSW_RemoveBrainWorm`) removes the infection. → ladder_wiring.surgery_recipe_removes_infection (the operation itself: mechanics_unmeasured.surgery_removes_worm, UNMEASURED)
- The salvaged-cargo incident cannot fire with `cargoIncidentEnabled` off. → cargo_incident.cargo_incident_off_refuses_to_fire
- A worm burrows into a living humanlike host. → mechanics_unmeasured.worm_burrows_living_humanlike_host (UNMEASURED: no verb forces the bite)
- Cold below freezing clears the infection (the cure is a place). → mechanics_unmeasured.cold_below_freezing_clears_the_infection (UNMEASURED: no verb sets map temperature)
- A mortar egg shell bursts into worms; off, it lands inert. → mechanics_unmeasured.egg_shell_bursts_into_worms (UNMEASURED: needs a fired shell)
- Ancient-complex room loot can hold an egg cluster. → mechanics_unmeasured.ruin_loot_can_hold_egg_cluster (UNMEASURED: map generation)
- A dead host is never puppeted (owner ruling, permanent: never a corpse-walker). → mechanics_unmeasured.dead_host_is_never_puppeted (UNMEASURED live; the static check asserts the Dead refusals in `CompRSWWormBurrow` and `HediffComp_BrainWormPuppeteer`)
- The art is drawn. → UNCOVERED: every texPath is a vanilla stand-in (About.xml "ART OWED"); visual, owner decides

## the walk
1. [D] `jawa/get_defs` over every def derived from `Defs/**/*.xml` (batches of 40): `foundCount` equals the request, `notFound` empty; a bogus def reads notFound   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on every scalar field of `RSW_BrainWormsSettings`   # settings_roundtrip
3. [D] `jawa/get_defs HediffDef/RSW_BrainWormInfection fields stages deep`; `RecipeDef/RSW_RemoveBrainWorm`   # ladder_wiring
4. [B] spawn two colonists at the live map centre, `jawa/pawn_health add`, `jawa/pawn_get` hediffs and mental state   # infection_state, puppet_state
5. [B] `jawa/fire_incident dryRun` with the toggle on and off   # cargo_incident
X. [S] (human pass) the Geonosian worm and egg art, once generated; owner decides.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "the latent infection shows in the health listing" — a latent hediff has `becomeVisible false`; a pawn_get that omits it reads UNMEASURED, never PASS or FAIL.
RULED OUT: "a falling severity means a mod defect" — below freezing severity is meant to fall (cold cure); the check reads UNMEASURED when the site is cold.
RULED OUT: "a fire_incident dry run reports success" — it reports success=false with canFireNow=false when the incident cannot fire; the check reads canFireNow, not success.
