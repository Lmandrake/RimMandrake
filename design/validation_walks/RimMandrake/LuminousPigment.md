# RimMandrake: Luminous Pigment (Deepfire) — validation walk
subject: src/RimMandrake/LuminousPigment  (packageId `mandrake.rm.luminouspigment`)
deps: `brrainz.harmony` (modDependencies); Ninefold (`mandrake.rm.ninefold`) and FlowWorks (`mandrake.rm.flowworks`) are loadAfter-only soft hooks; LightsOut is a third-party soft hook
list: luminouspigment_ns (modset_builder tier: the bridge + `mandrake.rm.luminouspigment` + `mandrake.rm.ninefold`, all five DLCs). The older `luminouspigment` tier lacks Ninefold, so the god chain reads UNMEASURED there.
status-hint: DEEPFIRE_PIGMENT_MOD_1 + DEEPFIRE_PAINT_STATUS_CUISINE_1 — crowncarpet (a rare shore mat on a one-day clock) is pressed into deepfire, a pigment that makes whatever colour a dye gives GLOW; deepfire paints walls, floors, furniture, art, apparel and weapons, lights wearers, drives a status engine, moves the nine Ninefold gods and is cooked into 15 glow dishes. The six `src/RimMandrake/bridgetools/prove_deepfire_*.py` harnesses were PROVEN live 2026-09-30 (115 checks, 612-mod list, `Transient/live_verify_batch_2026-09-30.md`); the chain (mat, gate, press, tank, stack glow), the patch effects and the settings arms have no recorded live run. Script: `src/RimMandrake/LuminousPigment/validation.py` (plan `northstar_plan.py`), first script owed by LUMINOUS_PIGMENT_FIRST_SCRIPT_1.

Sources for every line below: the mod's `About/About.xml` description, `design/RimMandrake/deepfire_luminous_pigment_spec.md` (fully ruled 2026-09-25/26, sections 2-7), the C# under `src/RimMandrake/LuminousPigment/Source/`, the six committed proofs, and `Transient/deepfire_live_failures_report.md` (DEEPFIRE_LIVE_FAILURES_1). The report-style bars drive the mod's own `Deepfire` debug actions (`Source/Deepfire*DebugActions.cs`) and read each call's own `effects.logs`.

## must be true
- Every def the mod ships loads and resolves (things, the two plants, the press, the tank, recipes, the research project, 14 glow hediffs, thoughts, jobs, work givers, designations, the shore gen step), read from the files at run time so a new def is covered with no edit. → defs_load.all_defs_resolve
- The patches landed (a patch that matches nothing logs nothing): `WaterOceanShallow` carries the `RM_CrowncarpetBed` tag, both stoves list all 15 deepfire recipes, and the two designators are registered under Orders. → defs_load.patches_applied
- The mechanics hang off the right defs: the plant carries the sighting comp, fresh crowncarpet the vitality comp, the tank is a `Building_GlowTank`. → defs_load.mechanics_wired_to_defs
- Crowncarpet spawns wild, rarely, on any ocean shore at map generation (`RM_GenStep_ShoreMats`, `shoreMatChance`, gated by `shoreMatsEnabled`). → UNCOVERED: needs a map generated on an ocean-shore tile; the bridge has no site recipe for it (named item to file: DEEPFIRE_SHORE_MAP_SITE_1); the setting itself round-trips below
- Fresh crowncarpet lives its day: with the chill kill disabled and the full life, a stack is still alive after 600 ticks and its inspect string carries `alive: Nh left` (the control for the two arms below). → mat_vitality.mat_alive_control
- Fresh crowncarpet dies on its clock: cutting `matLifeDays` below its age turns the whole stack into `RM_CrowncarpetDead`, stack count kept. → mat_vitality.mat_dies_on_clock
- Fresh crowncarpet dies at once if chilled: ambient below `matChillKillTemp` kills the stack within a rare tick, while the same cell under a disabled threshold survived. → mat_vitality.mat_dies_when_chilled
- The press project is locked until a colonist has seen crowncarpet (`RM_DeepfireRefining` cannot start; one game-wide flag, which persists). → research_gate.locked_before_sighting
- A colonist standing within 20 cells of a spawned, unfogged crowncarpet unlocks it within a long tick. → research_gate.unlocked_after_sighting
- The press gate is a setting: `pressGate` = Unbuildable takes the press off the build menu. → settings_apply.press_unbuildable
- `pressGate` = Buildable completes the research project. → settings_apply.press_buildable_finishes_research
- Def-level Mod Settings reach the defs when the settings dialog closes (`ApplySettings`): `deepfireMarketValue` read back off the def. This is the canary for every apply-dependent arm. → settings_apply.apply_reaches_defs
- The deepfire press is a powered bench (150 W, `CompPowerTrader`), not a hand bench. → press_refine.press_is_a_powered_bench
- A powered press refines 4 fresh crowncarpet + 1 Neutroamine + 2 Chemfuel into 2 deepfire (`pressYield`), consuming the ingredients. → press_refine.powered_press_refines
- An unpowered press runs no bill, and waits longer than the powered batch needed. → press_refine.unpowered_press_refuses
- A stack of deepfire glows faintly on its own in a dark room. → item_glow.stack_glows
- `deepfireStackGlows` off: a fresh stack no longer lights its cell. → item_glow.stack_glow_toggle
- An unseeded GlowTank says it needs a seed culture. → glowtank.unseeded_tank_says_so
- A seeded GlowTank loses its culture after a blackout longer than `tankPowerGraceHours` and keeps it while powered. → glowtank.blackout_kills_seed
- The GlowTank's 12-day growth cycle (4 cells, 2 fresh mat per plant, `tankGrowDays`, `tankYield`) and the spec's FlowWorks ocean-water requirement. → UNCOVERED: 12 game days is not drivable; the water requirement is in the spec (2.5) but not in `Building_GlowTank.cs` and has no setting, so it is not a shipped behaviour
- `glowTankEnabled` off takes the GlowTank off the build menu. → settings_apply.glowtank_toggle
- A designated wall is coated through the real WorkGiver job pipeline (designation, job, toil): one coat, the wall-cell price in deepfire, a measurable glow beside it. → paint_pipeline.wall_coat_via_real_job
- Deepfire carries no colour of its own: painting the coated wall Structure_Blue turns its glow blue. → paint_pipeline.glow_colour_follows_paint
- Three coats glow brighter than one, and a fourth is refused. → paint_pipeline.three_coats_then_refused
- Removing coats clears the coat count and the glow. → paint_pipeline.remove_coats_clears_glow
- `maxCoats` is a setting and the cap follows it. → paint_pipeline.max_coats_setting
- `wallsPaintable` off: no colonist has a deepfire job on a designated wall. → paint_pipeline.walls_paintable_toggle
- `furniturePaintable` off: none for a designated stool. → paint_pipeline.furniture_paintable_toggle
- `apparelPaintable` off: none for a designated parka. → paint_pipeline.apparel_paintable_toggle
- `weaponsPaintable` off: none for a designated knife. → paint_pipeline.weapons_paintable_toggle
- `paintingEnabled` off: an idle colonist leaves a designated wall alone (real work scan), and with it on the same colonist coats it. → paint_pipeline.painting_enabled_blocks_ai
- The designator and the remove designator accept or refuse targets (`Designator_Deepfire.CanDesignateThing`, `paintingEnabled`, `floorsPaintable`, `ishkoIdolPaintable`). → UNCOVERED: the bridge designates directly (`deepfire/designate`) and bypasses the designator class; no tool drives a designator (named item to file: DEEPFIRE_DESIGNATOR_PROBE_TOOL_1); the toggles round-trip below
- Floors: a 6x6 floor coat is 36 grid cells lit by exactly 4 shared proxies (one per 3x3 block), raises the centre glow, CellBeauty by 0.5 and the room line by 6 (`18 / CellCountCurve + 6` on the room's Beauty); the baseline is a clean 36-cell roofed room. → floor_paint.floor_baseline, floor_paint.floor_coat_lights_in_four_blocks
- A floor's glow follows vanilla floor paint: painted red, the coat and the 4 proxies stay and the glow turns red-dominant. → floor_paint.floor_tracks_vanilla_paint
- Stripping a floor's coats returns the grid, the proxies, the room Beauty and the room line to baseline. → floor_paint.floor_strip_clears_everything
- Removing a coated floor takes its coat and its proxies with it. → floor_paint.floor_removed_takes_coat_with_it
- The first coat bumps an art item's quality ONCE (Normal to Good; the second coat does not re-bump). → first_coat.art_quality_bumps_once
- A Legendary item stays Legendary and the coat is still charged. → first_coat.legendary_caps_but_still_charges
- `artQualityBump` off: the coat is charged and the quality is not bumped. → first_coat.art_bump_toggle
- Everything else gets a flat 3 + 25% Beauty on the first coat (the Beauty StatPart patch landed), removed with the coat, and re-coating does not double it. → first_coat.wall_beauty_bonus_exact_and_not_doubled
- The light proxies are Ethereal: a coat over a stockpile displaces and loses no item, and the proxy does not count as an item on its cell. → proxy_storage.coat_over_a_stockpile_displaces_nothing
- Emptied proxy cells and ordinary cells accept storage. → proxy_storage.emptied_cells_accept_storage
- A coated wall stands beside its own clustered proxy. → proxy_storage.coated_wall_stands_beside_its_proxy
- A pawn wearing a 3-coat parka is a light in a dark room (one proxy on its cell, glow above the lit threshold, glowing in the dark). → worn_glow.coated_walker_carries_a_light
- The light follows the pawn along a 30-cell walk (proxy on its cell, cell lit, at every sample). → worn_glow.light_follows_the_walker
- Stripping the garment un-tracks the pawn and darkens its cell. → worn_glow.stripping_the_garment_darkens_the_pawn
- `wornLightEnabled` off: a coated wearer carries no light. → worn_glow.worn_light_toggle
- The dark combat trade, in 20 fresh coated/plain pairs: ranged aim per unit body size is higher against the coated twin, the hit readout carries the glowing line, the melee dodge is lower (or both floored at 0) and explained. → worn_glow.dark_combat_trade_in_twenty_pairs
- `combatPenaltiesEnabled` off: the coated twin no longer aims higher in every pair. → worn_glow.combat_penalty_toggle
- The styling station lacquers a worn item: the queued job consumes 3 deepfire and leaves the parka at coats 1. → styling_lacquer.styling_station_lacquers_a_parka
- `stylingStationLacquer` off queues no lacquer job. → styling_lacquer.styling_lacquer_toggle
- A titled pawn in a 2-coat parka holds `RM_WearingDeepfireTitled` stage 0 (+3) and no commoner-reaction thought. → status.titled_pawn_in_two_coats
- `statusEnabled` off silences the thought, and it returns when restored. → status.status_toggle
- A commoner in a 2-coat parka gives the titled pawn `RM_WearsAboveStation` (opinion -15) and `RM_SawCommonerInDeepfire` (-3), takes none itself and holds `RM_WearingDeepfireCommon` (+1). → status.commoner_in_two_coats_offends_the_titled
- A lit bedroom lifts its owner: 36 coated cells score 3 (+4, stage 0) and two 3-coat sculptures score 9 (+6, stage 1). → status.lit_bedroom_lifts_its_owner
- A lit public room impresses a titled visitor of a non-hostile faction once per quadrum (goodwill +2, then nothing). → status.public_room_impresses_a_visitor_once
- With Ninefold loaded, a first coat on a wall moves the nine gods by the spec amounts (Ishko -3, the trio +8, the other five +3, times Ninefold's multiplier). → gods.first_coat_moves_every_god
- A second coat on the same thing moves no god (anti-pinning). → gods.second_coat_moves_no_god
- A first coat on a worn item is harsher on Ishko (-8). → gods.worn_first_coat_is_harsher_on_ishko
- A coated idol tagged for a god moves that god by 15. → gods.a_gods_own_idol_moves_it_by_fifteen
- Selling deepfire (a jar or a coated sculpture, not steel, not a bought jar) moves Mob'Unloo by +8 and nobody else. → gods.sale_of_deepfire_moves_mobunloo
- `godsReact` off: a first coat moves no god. → gods.gods_react_toggle
- Proxies survive LightsOut switching a room off (`DeepfireLightsOutCompat`). → UNCOVERED: needs the third-party LightsOut mod (`juanlopez2008.lightsout`) in the tier; `prove_deepfire_god_deltas.py` step 9 covers it when that mod is loaded and is the reference
- Cuisine ships 14 glow families and 15 dish recipes, each family a hediff. → cuisine.fourteen_families_and_fifteen_recipes
- `cuisineEnabled` off removes every deepfire recipe from both stoves. → settings_apply.cuisine_recipes_toggle
- Cooking: a chef's skill steers which family a dish lands (random below `steerMinSkill`, chosen above), the vermilion recipe is hidden below `vermilionMinSkill`, a second helping raises a tier, a fourth family is refused, a tier-III skin glow lights the pawn's cell, pulse-glow oscillates; `hediffGlowEnabled` gates the light. → UNCOVERED: needs a cook-a-dish harness (a pawn cooks at a stove and the outcome doer's roll is read); no bridge tool does it (named item to file: DEEPFIRE_CUISINE_HARNESS_1); the setting round-trips below
- `shoreMatsEnabled` round-trips (behaviour is the shore-spawn line above). → toggle_flips.shore_mats_setting_flips
- `floorsPaintable` round-trips (behaviour is the designator line above). → toggle_flips.floors_paintable_setting_flips
- `ishkoIdolPaintable` round-trips (behaviour is the designator line above). → toggle_flips.ishko_idol_setting_flips
- `hediffGlowEnabled` round-trips (behaviour is the cooking line above). → toggle_flips.hediff_glow_setting_flips
- The run raises no new Error-type log line naming this mod (the proxy double-destroy, the visitor NRE and the stale social cache each surfaced as one). → no_new_errors.no_error_lines_from_this_mod (its baseline is 00_log_baseline.log_baseline_recorded)
- Every scalar Mod Settings field the C# declares is exposed to the settings tool and round-trips default/write/restore. → settings_roundtrip.every_scalar_field_round_trips (arrays and the PressGate enum: static check only)

## the walk
1. [L] Player.log after load: no "Config error in mandrake.rm.luminouspigment", no cross-reference error naming a `RM_` def of this mod, no patch error from `Patches/*.xml`; the soft hooks (Ninefold, FlowWorks) are reflection-only and absent-safe   # defs_load
2. [D] `jawa/get_defs` over every def derived from `Defs/**/*.xml`: `foundCount` equals the request, `notFound` empty; a bogus def is reported notFound (the sanity probe)   # defs_load.all_defs_resolve
3. [D] `jawa/get_defs` `TerrainDef/WaterOceanShallow` field `tags`; `ThingDef/ElectricStove` and `FueledStove` field `recipes`   # defs_load.patches_applied
4. [B] spawn `RM_CrowncarpetFresh`, step ticks with `matChillKillTemp` disabled/raised and `matLifeDays` cut; `jawa/list_things` for the fresh and dead defs   # mat_vitality
5. [B] `jawa/research_availability` before and after a colonist sees a spawned crowncarpet; `jawa/set_plants`; 2100 ticks   # research_gate
6. [B] `jawa/mod_settings_field` set, then `rimworld/open_mod_settings` and close the dialog (`WriteSettings` runs `ApplySettings`), then read the def back   # settings_apply
7. [B] press: `jawa/power_net`, `jawa/bill_add`, ingredients spawned beside it, ticks, `jawa/list_things` for `RM_Deepfire` in the room   # press_refine
8. [B] wall: `deepfire/designate`, `deepfire/force_apply_job`, `deepfire/comp_coats`, `deepfire/glow_at` in a roofed room, `deepfire/paint_building`   # paint_pipeline
9. [B] the six Deepfire debug-action families (`Floor:`, `FirstCoat:`, `Proxy:`, `WornGlow:`, `Status:`, `GodDeltas:`) through `rimworld/execute_debug_action`, each result read from its own `effects.logs` tag   # floor_paint .. gods
10. [D] `jawa/drain_log errorsOnly` before and after: Error-type lines naming this mod that are new or repeated   # no_new_errors
X. [S] (human pass) a coat reads as a glow of the dye's colour on a wall, a floor and a worn parka at night; the stockpile glow reads as faint; the press, tank, jar and mat art read as the spec describes. No visual bar is drafted for the owner yet.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet; the visual questions (does a coat read as glowing in the dye's colour, does the stockpile read as faint, does the press read as a press welded to a retort) are his to rule. A functional script needs none: the lines above are the agent layer.

## anti-guessing notes
RULED OUT: "the real WorkGiver reliably takes a designated wall" — `Transient/deepfire_step5_final_run.log` read `wall coats after real job: 0` after 90 polls on a real map; the proven route forces the pawn onto the real JobDriver (`deepfire/force_apply_job`). `paintingEnabled` is therefore a real-AI A/B whose ON arm is its own control: if the ON arm never coats, the OFF arm reads UNMEASURED, never PASS.
RULED OUT: "GroundGlowAt answers in daylight" — the same log reads `1.0` at every outdoor cell, coated or not. Every glow bar runs in a roofed room (`jawa/make_empty_room`) so the only light is ours, reads a baseline first, and compares to it.
RULED OUT: "a failed press with no product means the recipe is broken" — `powered_press_refines` reads UNMEASURED when no pawn takes the bill in 9000 ticks, and the unpowered arm waits 1.5x as long as the powered batch needed (min 3000), or a press that ignored power would simply not have finished yet.
RULED OUT: "`jawa/mod_settings_field` applies a setting" — it writes the static but never calls `WriteSettings`, so def-level settings (market value, glow radius, designationCategory, the stove recipe lists, the research finish) only reach the defs when the Mod Settings dialog closes. Live-read settings (matLifeDays, maxCoats, the paintable toggles, ...) need nothing. `Transient/live_verify_batch_2026-09-30.md` found the bridge's settings RELOAD swaps in a new object while a gate read a captured instance; this mod reads statics, so the dialog path is expected to work, and `apply_reaches_defs` is the canary that says so.
RULED OUT: "the coated twin always aims higher" — 2 of 20 pairs failed 2026-09-30 because random colonist twins differ in body size (vanilla clamps `factorFromTargetSize` to 0.5-2); the pairs compare aim per unit of each twin's own size and the actions generate baseliner adults.
RULED OUT: "the walk must record at least 10 samples" — the walker finished 30 cells in 7 polls; the bar is >= 25 cells travelled with the proxy on its cell at >= 5 distinct cells, at every sample.
RULED OUT: "the titled pawn's opinion of the commoner reads -15 whenever the thought is active" — the report read a 100-tick-stale social cache and returned 0 in 3 of 7 recorded runs; `BuildPairReport` now dirties both pawns first (DEEPFIRE_LIVE_FAILURES_1).
RULED OUT: "a debug action that logged nothing did nothing" — RimWorld stops logging at 10,000 messages (`Reached max messages limit`); `_act` records UNMEASURED, never PASS or FAIL, when no tagged line arrives, and the live sheet says relaunch.
RULED OUT: "`jawa/drain_log` drains" — it returns the newest entries of the 1000-entry buffer and `errorsOnly` includes warnings; the error check takes a baseline at the start and counts only Error-type lines that are new or repeated.
RULED OUT: "a stack of crowncarpet dying in the test is the mod's chill kill" — a map colder than `matChillKillTemp` (10 C) would kill a stack with no help from the mod's clock; `mat_alive_control` disables the threshold (-100) and `mat_dies_when_chilled` raises it (100), so the only difference between the two arms is the setting (by construction, not measured).
RULED OUT: "locked_before_sighting passes on any game" — the flag persists in the game, so on a used game the bar reads UNMEASURED ("canStartNow is already true"). It cannot tell "already seen" from "no gate at all"; run it on a fresh game.
