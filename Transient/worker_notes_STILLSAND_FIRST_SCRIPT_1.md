# Worker note STILLSAND_FIRST_SCRIPT_1

STATUS: authored, offline-proven, READY TO RUN. Never run live.

| file | what |
|---|---|
| `src/RimMandrake/Stillsand/validation.py` | the modcheck Suite: 22 chains, 69 components, 30 settings fields, 23 toggles |
| `src/RimMandrake/Stillsand/northstar_plan.py` | `USE_SUITE=True`, `EXPECT_MODS=("mandrake.rm.biomes",)` |
| `src/RimMandrake/Stillsand/northstar_site.py` | pre-flight: world up, DLC, 30 settings fields at their shipped defaults |
| `src/RimMandrake/Stillsand/selftest_stillsand.py` | fake game: healthy 69/69 PASS, 67 breaks each turn exactly their component red, plus a log-saturation case that must read UNMEASURED everywhere |
| `design/validation_walks/RimMandrake/Stillsand.md` | walk: 76 `## must be true` lines, each with `-> chain.component` or `-> UNCOVERED: why`; `## north star` is DRAFT with a blank hash (none drafted) |

## What it is built from (read, not guessed)
- Stillsand ships COMPOSED in `mandrake.rm.biomes` (wave 2 of `Biomes.compose.json`), so EXPECT_MODS is `mandrake.rm.biomes` and the tier is the existing `baroque_wave0` (9 mods with the closure: FlowWorks, Creature Behaviors, Environmental Hazards, Moving Dunes). No tier was added; `modset_builder.py` is untouched.
- The site is the recipe PROVEN live on 2026-10-01 (`Transient/LIVE_SESSION_2_2026-10-01.md`, `Transient/livesession2_20261001/regen.py`): `jawa/world_tile_set biome=RM_Stillsand` + `jawa/world_commit` + debug action `Actions\Regenerate Current Map`. The suite always regenerates, so this run's cave log lines are readable.
- Live shapes reused from those proven scripts: spawn_pawn, list_pawns (health nested), list_things, letter_list, fire_incident, game_condition, pawn_use_verb cast, pawn_flight report, drain_log, the `T: Kill` debug action, blood as `Filth_Blood` through spawn_batch, `jawa/pawn_gear wear`, `jawa/pawn_stats`, `jawa/shadegrid_read` (new, deployed after those sessions).
- Every bridge call is statically linted: `python3 src/RimMandrake/Utils/northstar_driver/lint_calls.py src/RimMandrake/Stillsand` exits 0 (95 literal-named calls, none UNCHECKED; the one dict-form call is `pawn_gear`, whose `def` is a Python keyword).
- Row shapes read from the C# `[Tool]` sources: list_things rows carry `id, def, x, z, stackCount`; list_pawns rows carry `kindDef, faction` (the faction DEFNAME), `isPlayer`, `dead`, nested `health.hediffs[{def,severity}]`; biome_probe `findResults[{defName,state}]`; shadegrid_read `pinnedSun{isActive,sunElevationDegrees}`, `skyGlow`, `cells[{x,z,exposure}]`; storyteller_fire `fired`, `blockedByDialog`.

## Bars (69 components, by chain)
site 3 | defs 7 | settings 10 | sun 3 | fauna 2 | flora 1 | sandswim 2 | zuurrik 4 | loomma 1 | soorrak 2 | glass 8 | water 3 | skeleton 2 | glare 3 | cooling 1 | gale 5 | devil 2 | muurrok 3 | eruption 1 | horizon 2 | caves 3 | log 1. The chain, component and walk line for each is in the walk. Known past bugs guarded: OORRIK_PAWNGEN_NRE_1 (fauna.fauna_spawns), STILLSAND_LOAD_DEF_ERRORS_1 (defs.defs_resolve), SANDSWIM_TAKE_FUNNEL_NEVER_PLACED_1 (sandswim.vekka_take_leaves_funnel), SOORRAK_FLIGHT_JOBSTART_NRE_1 (soorrak.soorrak_no_exceptions), the soorrak idle loop (soorrak.soorrak_not_stuck; expected RED on today's build, it is the defect the 2026-10-01 session filed), MUURROK_BEAM_NO_DAMAGE_1 (muurrok.beam_burns_target; fixed at `f591714e5`, unproven live), the precious-cave gen steps (site.site_cave_logged).

Floor: `cd src/RimMandrake/Utils && python3 -m modcheck.cli floor --all` lists `Stillsand  yes ok 82 - DRAFT 0 0 0 no bar` (walk found, subject ok, every one of the 23 toggles covered; "no bar" is the same wording LeaningScrub and LuminousPigment show for a DRAFT north star). `python3 -m modcheck.walklint <repo root>` reports nothing for the walk.

## Tier
`baroque_wave0` (existing; `python3 src/RimMandrake/Utils/modset_builder.py --list` prints it: "2 wanted -> 9 with dependencies"). Not run (`--apply` is the seat's).

## Offline proof
- `python3 src/RimMandrake/Stillsand/selftest_stillsand.py`: `69 components, healthy PASS 69/69; 67 of 67 breaks each turn exactly their component red`.
- `python3 src/RimMandrake/Utils/northstar_driver/cli.py run --mock --mod Stillsand --plan src/RimMandrake/Stillsand/northstar_plan.py --mock-skip-site`: runs to completion in under a second (the mock transport knows no `jawa/drain_log` etc., so components read FAIL/UNMEASURED there; that is the mock, not the suite).
- `python3 src/RimMandrake/Utils/northstar_driver/lint_calls.py src/RimMandrake/Stillsand`: exit 0.
- The fake game proves predicates and wiring, not response shapes. Shapes not proven live are listed in the walk's last notes.

## LIVE-RUN SHEET
**Prerequisites.** The bridge held by FOUNDRY (`rimflow bridge who`). Dev mode on (pre-flight checks it). No modal window open. The composed mod must be deployed from a tree that holds the commit under test (`--compose` deploys what the tree holds; the 2026-10-01 sessions used a clean worktree).

**One command** (stops the game, writes the tier with a pre-session ModsConfig copy, deploys the composed biomes, launches via Steam and waits for `Bridge token:`, starts a quicktest world, runs the driver, prints one line per non-passing component):

    python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod Stillsand --tier baroque_wave0 --plan src/RimMandrake/Stillsand/northstar_plan.py --compose

With the game already up on `baroque_wave0` and a quicktest world: `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Stillsand --plan src/RimMandrake/Stillsand/northstar_plan.py`. At the end of the batch `live_session.py --restore` is the seat's call (the quicktest world is wrecked by two regenerations).

**Launch wait.** `live_session.py` budgets 900 s for `Bridge token:`. `baroque_wave0` is 9 mods, so it should be far under the full list's 15 minutes; it has not been timed.

**Site.** Any quicktest world; the suite sets the current tile to `RM_Stillsand` at 15 C and regenerates (about 1-2 minutes, polled up to 300 s), plants 3 colonists, destroys the hostile Hive group. A map under 230 cells on a side reads UNMEASURED. God mode is not needed. The tile (and so the sun elevation) is whatever the quicktest rolled; sun-dependent bars read UNMEASURED, with the latitude in the note, when it is too low. The suite regenerates a second time in its `caves` chain.

**Tick budget.** About 50,000 game ticks typical, 65,000 worst case (zuurrik 10,000, gale 13,000, skeleton 4,400, muurrok 4,400, water 3,600, soorrak 3,000, devil 2,400-6,000, eruption 1,000-4,000, loomma/glare/horizon 1,500 each, the sun chain's 12-hour jump is a clock set, not ticks). Stepping runs around 53 ticks/s on a big list, so expect 25-40 minutes of wall clock. Nothing waits on a wall-clock sleep except the regen readiness poll. The driver prints a `[stillsand]` progress line per component to stderr.

**Settings.** Every arm that flips a setting restores it in a `finally` and re-reads it. `jawa/mod_settings_field` never writes `ModSettings.xml`.

**What PASS / FAIL / UNMEASURED mean per chain**
| chain | PASS means | FAIL means (classify) | UNMEASURED means |
|---|---|---|---|
| site | the map is `RM_Stillsand`; cave gen logged; skeletons within the cap | biome did not take (MOD: BiomeDef discarded) / no cave line (MOD: gen step not wired) / over cap (MOD) | no tile, map too small, log near its cap (SITE) |
| defs | every def resolves; the five extensions and three gen steps are on the biome; roster rows spawn; patches landed | a def discarded or a patch matched nothing (MOD) | a custom def type name get_defs cannot take (HARNESS) |
| settings | 30 fields at shipped defaults; 9 toggles read/write | a field missing or not at default (MOD) | none expected |
| sun | pinned sun active, glow 1 at two hours, open exposure >= 0.6, roof is cover above 55 deg | pinned sun not applied / night falls / exposure low (MOD or tile) | elevation below 55 for the roof bar (SITE) |
| fauna / flora | 22 kinds spawn alive, soorrak can fly, 5 plants stand | a kind did not spawn (MOD) | none expected |
| sandswim | vekka submerged on sand not gravel; a take leaves the funnel | no submerge, or submerged on rock, or no funnel (MOD) | bait not killed in 3200 ticks (HARNESS/SITE) |
| zuurrik | 3 cells stay dormant, 12 wake, strip, toggle off wakes nothing and on wakes | wake on too little / no wake / no strip / toggle ignored (MOD) | swarm not clearable (HARNESS) |
| loomma / soorrak | clock rises in the open, lower roofed; no exception; moves or runs a job | no clock, shade ignored, exception, stuck idle (MOD) | every soorrak left the map (SITE) |
| glass | `Sun: NN%` open, "under a roof" roofed, stat part applied, multiplier scales, 3 toggles disable | stat part missing (MOD: patch matched nothing), toggle ignored (MOD) | sun below 30 percent at this latitude (SITE) |
| water | pour on sand blooms; toggle off or gravel does not | no bloom / bloom on gravel / toggle ignored (MOD) | egg never poured (HARNESS) |
| skeleton / glare / cooling | corpse becomes skeleton only when on; goggles stop glare-blind; draught +8 | (MOD) | no corpse from the debug kill (HARNESS) |
| gale / devil | fires; toggle refuses; herald then gale; end line with sand moved and one emergence letter; exposure cut; devil moves and goes | (MOD) | gale could not fire with the toggle on (SITE) |
| muurrok / eruption | letter + pawn; beam burns a target; toggle off blocks; tunnel then mound | (MOD) | beam did not damage so the off arm is not judged (see FAIL on beam_burns_target) |
| horizon | warn letter then delayed arrival; toggle off arrives at once | (MOD) | `storyteller_fire` unavailable or no trader faction (HARNESS/SITE) |
| caves | one regen with both gen toggles off logs no cave line and places no skeleton | (MOD) | log at its message limit (SITE: relaunch) |
| log | no Stillsand error or `RM_` cross-reference/config error | (MOD) | log buffer empty or at its limit |

## Break-it proofs (how each check is shown able to FAIL)
The selftest turns each of 67 mod-behaviour breaks into its component, and no other, going red; the live recipe for the same defect is:
- site: set `RM_Stillsand` aside so the tile edit cannot take (regen_keeps_biome); drop `RM_PreciousCaves_BiomeGenSteps.xml` (no_cave_log); raise the skeleton gen above the cap (skeleton_overcap).
- defs: reintroduce `<treeCategory>Standard</treeCategory>` on `RM_KneelOllim` (missing_def); drop a patch operation (no_ext, no_gensteps, giant_unwired, egg_unpatched); delete a roster commonality or set it 0 (roster_zeroed); `animalDensity` 0 (zero_density); empty `allowedBiomes` (eruption_ungated); remove a settings field (setting_missing).
- sun: remove `RM_PinnedSunExtension` (no_pinned); a glow below 1 (night_falls); no roof rule in the shade grid (roof_no_cover); a tile whose exposure is below 0.6 (low_exposure).
- fauna/flora: put the `Rat` body back on `RM_Oorrik` (oorrik_nre); `MaxFlightTime` 0 on the soorrak (no_fly); a plant def with a bad field (set_plants_drops).
- sandswim: drop `RM_SandSwimExtension` (no_submerge); submerge on any terrain (submerge_on_rock); put the funnel filth back on a terrain mask that refuses it (no_funnel).
- zuurrik: threshold ignored (wakes_below_threshold); component inactive (no_wake); no `RM_EatCleanableExtension` (no_strip); `Active` ignoring `zuurrikEnabled` (zuurrik_ignores_toggle).
- loomma/soorrak: clock ignores roofs (loomma_ignores_shade); the old `Notify_JobStarted` NRE (soorrak_nre); the instantly-ending job (soorrak_stuck, which IS today's behaviour).
- glass: no roof check in `RM_SunPower.FactorAt` (no_roof_check); remove the `StatDef` patch (no_statpart); ignore `sunWorkSpeedMultiplier` (mult_ignored); no "Sun:" inspect line (table_no_sun_line); a table ignoring its toggle (sunfurnace/lensbench/solaroven_ignores_toggle).
- water: remove the extension (no_bloom); bloom ignoring `bloomOnPour` (bloom_ignores_toggle); bloom ignoring terrain (bloom_on_gravel).
- skeleton/glare/cooling: scan never converts (no_skeleton); scan ignoring the toggle (skeleton_corpse_toggle_ignored); no glare hediff (no_glare); goggles not read (goggles_ignored, gear_fails); wrong stat offset on the draught (draught_wrong).
- gale/devil: never fires (gale_never_fires); toggle ignored (gale_ignores_toggle, devil_ignores_toggle, emergence_ignores_toggle); no herald weather (no_herald); no sand moved (dunes_still); no sun cut (gale_keeps_sun); a devil that does not move or never ends (devil_still, devil_immortal).
- muurrok/eruption: no pawn (no_muurrok); the beam doing nothing (beam_no_damage, the real MUURROK_BEAM_NO_DAMAGE_1); toggle ignored (beam_ignores_toggle); no mound (no_mound).
- horizon: no letter (no_horizon_letter); not delayed (horizon_instant); toggle ignored (horizon_ignores_toggle).
- caves/log/settings: gen toggle ignored (caves_ignore_toggle, skeleton_ignores_toggle); an error line (log_error); a toggle whose write does not take (roundtrip_ignored).
- Controls inside the chains (each makes a harness that sees nothing read UNMEASURED, not PASS): the absent-def and absent-roster probes, a nonexistent settings field, a gravel vekka, a 3-cell blood cluster, a goggled colonist, a toggle-on arm before every toggle-off arm, a roofed loomma, a gravel pour.

## Ruled out while building (also in the walk)
The planted colonists survive the run (they do not: the site tile is 15 C and every chain keeps one alive); `get_defs` can read `wildAnimals` (it cannot: `biome_probe` does); `fire_incident dryRun` predicts the leviathans (it read false before they fired); a missing log line is absence (RimWorld stops logging at a limit; `_log_lines` reads UNMEASURED then); `list_pawns` marks player pawns by faction name (it carries `isPlayer`); the dune gale's herald is 4,000 ticks (it is 15 percent of the duration).

## FOLLOW-UP ITEMS
Proposed IDs, no ledger items filed (the brief):
1. `STILLSAND_STATE_READER_TOOL_1` - one read-only `[Tool]` returning `RM_MapComponent_WetSand` (wet cell count, latest pour cell), `RM_MapComponent_HorizonPlume.ActiveCount`, `RM_MapComponent_Zuurrik` (swarm, quiet polls, fatness) and `RM_GameComponent_GaleCarried.Count`; turns four UNCOVERED walk lines (wet sand draws swimmers, the plume, carry-and-return, zuurrik re-burial) into state reads.
2. `STILLSAND_LEVIATHAN_SETTINGS_READER_1` - make `RM_StillsandEventsSettings.disabled` / `odds` readable and writable by `jawa/mod_settings_field` (public accessors, or tool support for dictionary fields) so the muurrok and krayt incident toggles and odds can be driven.
3. `STILLSAND_GALE_CARRY_PROOF_1` - a dev `[DebugAction]` or tool that forces `TryCarry` on a named pawn and then the return, so the carry/drag-line/Carried-off-letter/return bars are deterministic instead of an MTB on a crest.
4. `STILLSAND_GLASS_BILL_PROOF_1` - a `northstar_driver.site` helper that builds a skilled crafter at a bench and runs a bill to completion, then a chain proving the four glass recipes at a staffed sun furnace and lens bench in sun.
5. `NS_SITE_TILE_BY_LATITUDE_1` - a `northstar_driver.site` helper that picks the quicktest world's tile by latitude before regenerating (an existing scratch tile, never a new planet), so sun-elevation-dependent bars stop reading UNMEASURED on a low-sun roll.
6. `NS_LOG_LIMIT_GUARD_1` - lift `_log_saturated` (read `Reached max messages limit` before trusting any log absence) into `northstar_driver` so every first script shares it; LuminousPigment's walk records the same hazard.
7. `NS_HOME_COLONIST_KEEPALIVE_1` - a site helper that keeps one home colonist alive through a heat biome run (shade pad or heatstroke clear) so a game-over never ends a long suite; today the suite re-plants one per chain.
8. `STILLSAND_CAVE_PROOF_BATCH_1` - an opt-in chain that generates ten Stillsand maps and counts caves whose mouth faces away from the sun (the statistic STILLSAND_PRECIOUS_CAVES_LIVE_1 asks for); one regeneration per map is the cost.
