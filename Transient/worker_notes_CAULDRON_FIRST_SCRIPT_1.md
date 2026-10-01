# worker note CAULDRON_FIRST_SCRIPT_1 — first north-star script for Cauldron

status: READY TO RUN (offline proof done; nothing live ever run). Class of anything the first run finds: expect HARNESS/shape findings first (debug_process section 8).

## what was delivered
- `src/RimMandrake/Cauldron/validation.py` — modcheck Suite, 12 chains, 42 components (39 behavioural + 3 `*_site_ready` setup). Mod Settings defaults are PARSED from `Source/RM_CauldronMod.cs` (11 fields, 8 bools = `suite.toggles`, all 8 covered by a component), the shipped def list is parsed from `Defs/` (29 defs).
- `src/RimMandrake/Cauldron/northstar_plan.py` (USE_SUITE=True, EXPECT_MODS=`mandrake.rm.biomes`) + `northstar_site.py` (preflight: map >= 150, dlc_status, settings at defaults, storyteller off, weather unlock).
- `src/RimMandrake/Cauldron/selftest_cauldron.py` — fake game; healthy 42/42 PASS; 39 breaks each turn exactly one component red. Also guards the script against source drift (TYPES exist in Source/, defaults scribed, def census).
- `design/validation_walks/RimMandrake/Cauldron.md` — DRAFT walk, `## must be true` with an arrow on every line (39 covered, 11 UNCOVERED with reasons), anti-guessing notes. No `## north star` section, no `modcheck validate`.
- Tier: existing `baroque_wave0` (Cauldron is wave 0 in `Biomes.compose.json`, composed into `mandrake.rm.biomes`). No tier added, nothing applied.
- Lint: `lint_calls.py --summary src/RimMandrake/Cauldron` -> 0 problems over 68 literal-named calls (declared-schema check).

## offline proof
- `python3 src/RimMandrake/Cauldron/selftest_cauldron.py` -> "42 components, healthy-PASS 42/42; 39 breaks, each turning exactly its own component red".
- `northstar_driver cli.py run --mock --mod Cauldron --plan ... --mock-skip-site` runs to completion (117 calls) and ends `NOT GREEN`: the driver's mock transport only knows a few tools and answers `unknown tool` for the rest (same as LeaningScrub), so the mock proves the plan/driver wiring, the fake-game selftest proves the predicates.
- `modcheck floor --all` shows `Cauldron  walk yes  subj ok  DRAFT  0 bars  no bar`. NOTE: 'bar met' is reachable only by an owner-VALIDATED `## north star` section (every DRAFT first script, LeaningScrub included, shows 'no bar'); agents may not run `modcheck validate`, so that stays the owner's. `modcheck doctor` lists WALK_WITHOUT_CAPABILITY for Cauldron like 9 siblings (a rimflow capability row; not mine to file).

## how each check is proven able to FAIL (break the fake game / on the real site)
| component | fake-game break (selftest) | on the real site, break it by |
|---|---|---|
| load.defs_resolve | a shipped def not in get_defs | rename a defName in Defs/ |
| load.types_resolve | a class unresolved / DLL not the file on disk | deploy without the DLL, or redeploy after launch |
| load.biome_weather_table | a stock Clear commonality | set `<Clear>` > 0 in RM_Cauldron.xml |
| load.biome_roster | vexxiss row zeroed | set `<RM_Vexxiss>0</RM_Vexxiss>` |
| load.biome_worker_and_terrain | donor worker class | point workerClass at BiomesPlus |
| load.nettle_habitat_wired | extension absent | drop the modExtension on RM_RavenNettle |
| weather.weather_defs_laws | rainRate>0 / doToxicBuildup true | edit the WeatherDef |
| weather.weathers_selectable | a weather that does not read back | remove a WeatherDef |
| settings.defaults | a field missing | rename a static field |
| items.* | explosive comp on vexxiss; no steel / non-toxic zisska | add the comp / empty butcherProducts |
| fauna.fauna_spawns / suush_can_fly | kind never appears / canEverFly false | drop the PawnKindDef / MaxFlightTime 0 |
| suush.* | melee kills it / bullet does not | remove startWickOnDamageTaken Bullet |
| flora.* | plant discarded; wrong grade; toggle ignored; factor ignored | edit RM_CompMetalYield thresholds / gate |
| yield.* | no steel; factor ignored; steel with toggle off | remove the comp / ignore `metalYieldEnabled` |
| bloom.* | no exposure; roof ignored; natives hit; toggle/factor ignored; ToxicBuildup too | edit RM_VentBloomExposure.Eligible / interval |
| water.* | no poison; no/duplicate letter; toggles ignored | edit RM_CompVexxissBehaviour |
| fire.* | no BeatFire; toggle ignored | drop giveNonToolUserBeatFireVerb |
| log.log_clean | an error naming the mod | any Config error in a Cauldron def |
Controls built into the chains (a PASS needs the opposite arm to read right): roofed colonist + native animal beside the exposed colonist and non-native animal; Cut-hit suush beside the Bullet-hit one; letter cooldown arm only counts if the poisoning repeated; fire OFF arm only counts if a Fire thing stood during the window; each harvest arm must have produced wood. Every setting arm restores in a `finally` and re-reads. Every sanity probe: absent def, absent type, absent biome-roster name, absent settings field.

## LIVE-RUN SHEET
Prereq: bridge held (`rimflow bridge who`), then from the repo root in WSL:
```
python3 src/RimMandrake/Utils/northstar_driver/live_session.py --mod Cauldron --tier baroque_wave0 --plan src/RimMandrake/Cauldron/northstar_plan.py --compose
```
It stops the game, `modset_builder --tier baroque_wave0 --apply`, `deploy_custom_mods.py --compose biomes --apply`, launches via Steam (wait for `Bridge token:`, cold load of the 9-mod tier is minutes not 15), starts a quicktest world, runs the driver under Windows python, writes `Transient/northstar/Cauldron_<ts>.json`. (`--no-restart` if the game is already up on that tier and the composed mod is deployed.) Run it alone, then `--restore` at the end of the batch per live_session's docstring.
- Equivalent direct run once up: `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Cauldron --plan src/RimMandrake/Cauldron/northstar_plan.py`
- Site: any quicktest map >= 150 x 150 (preflight refuses a smaller one); any biome (the vent-bloom native check reads THIS map's roster). Pads sit 45 cells from the map centre; the suite clears and re-lays its own. God mode not needed. Storyteller is turned off by the preflight; weather is released and reset to RM_ScatterDusk at each chain end.
- Tick budget: about 14,000 ticks (bloom ~4,500: 4,100 transition wait + three short exposure steps; yield ~4,500 across three harvests, worst case 15,000; water ~1,500; fire <= 1,800; suush 800); ~5 to 8 minutes live, ~15 worst case. Waits above 4,000 run Ultrafast with a stall guard.
- Progress lines `[cauldron] HH:MM:SS <component> <verdict>` stream to stderr; evidence notes as `[cauldron]-note`.

PASS / FAIL / UNMEASURED per bar (UNMEASURED always means a shape or a site precondition was missing, never "ok"):
- load.defs_resolve PASS: all 29 defs found, sanity probe says absent. FAIL: a def silently discarded (missing comp/extension type, bad cross-ref) = MOD.
- load.types_resolve PASS: six classes resolved, in AllTypes, carried by mandrake.rm.biomes, MVID matches the file. FAIL: DLL not loaded / stale = DEPLOY or MOD.
- load.biome_weather_table / biome_roster / biome_worker_and_terrain / nettle_habitat_wired: FAIL = the biome def differs from its stated design (MOD). UNMEASURED = `deep=true` / `biome_probe` / `get_def.extra` shape differs = HARNESS.
- weather.*: FAIL on a WeatherDef law = MOD; `weathers_selectable` FAIL = a weather the engine will not hold.
- settings.*: FAIL = a field renamed/missing or default drifted = MOD.
- items.*: static def reads (comps, shear, butcher, toxic meat). FAIL = def drift = MOD. UNMEASURED = deep-serialised shape differs.
- fauna.*: FAIL = a kind did not spawn a living pawn (the whole PawnKind may have been discarded) = MOD.
- suush.*: PASS = Cut-hit lives AND Bullet-hit is gone within 400 ticks. FAIL on either = MOD (wick mapping). UNMEASURED if the control vanished too.
- flora.*: spawns/assay. FAIL = plant refused to stand (terrain/fertility) or assay math/toggle/factor wrong = MOD.
- yield.*: needs a colonist to complete a Harvest. UNMEASURED = no wood in 5,000 ticks (job not accepted = HARNESS: try `HarvestDesignated`). FAIL = steel wrong/with toggle off = MOD.
- bloom.*: PASS needs the exposed colonist to gain RM_VentMetalLoad at severity ~0.012 while the roofed colonist and the native stay clean and the non-native gains it. UNMEASURED = no exposure read (clock jump / transition not done = HARNESS) or the map offers no native/non-native herbivore pair = SITE.
- water.*: FAIL = no toxic cells after 300 ticks of wading, a missing/duplicate letter, or a toggle that does nothing = MOD. UNMEASURED = the vexxiss wandered out of its pond (SITE: rerun).
- fire.*: PASS = BeatFire seen within 900 ticks with a Fire thing standing; OFF arm never. UNMEASURED = map_fire lit nothing or no Fire read (SITE/HARNESS). A sleeping animal reads as FAIL on the ON arm: re-check the hour before calling it MOD.
- log.log_clean: FAIL = Config/cross-ref error naming a Cauldron def (the 2026-09-30 class).
Record the run through `modcheck.status.record_run` per debug_process section 2 (driver does not yet; see FOLLOW-UP).

## shapes that are UNPROVEN until the first run (each reads UNMEASURED, never PASS)
`site_state.weather.transition` numeric; get_defs deep=true dicts for `race`/`ingestible`/`butcherProducts`/`outcomeDoers`; get_def `comps[].fields.woolDef`; `Harvest` JobDef on a tree; `list_things defName=Fire`; `BeatFire` job name; `letter_list` label text; `biome_probe` on the map biome with HERBIVORES.

## FOLLOW-UP ITEMS
- CAULDRON_WORKER_PROBE_1 — [Tool] `jawa/biome_score` (tileId or all tiles, biome) calling `BiomeWorker.GetScore` so a script can read the Cauldron's score and prove `biomeRarityFactor` 0 gives -100 and the default places it somewhere.
- CAULDRON_CONDENSATE_SWEEP_HOOK_1 — [Tool] to force N sampling sweeps of `RM_MapComponent_CondensateGardens` (and a Cauldron-biome site recipe) so nettles-on-toxic-shores can be read in one call instead of days of ticks.
- CAULDRON_FIRE_INSTIGATOR_TOOL_1 — [Tool] `jawa/ignite_as` (pawn, cell) that starts a Fire with `instigator` set, so the vexxiss igniter-attack and the tame-vexxiss-never-attacks-own-faction rule can be driven.
- NORTHSTAR_DRIVER_GET_DEFS_DEEP_LINT_1 — extend `lint_calls.py` to flag a `get_defs` read of a known-private BiomeDef field (`wildAnimals`, `wildPlants`, `coastalWildAnimals`) and of a list-of-objects field without `deep=True`; LeaningScrub's `biome_weather_table`/`biome_density_and_flora` read both without them (get_defs reads PUBLIC fields only, `jawa/biome_probe` is the instrument for rosters) and will read UNMEASURED/FAIL live for the harness reason. (I did not edit LeaningScrub.)
- NORTHSTAR_DRIVER_RECORD_RUN_1 — already in debug_process section 1 (driver result -> `modcheck.status.record_run`); Cauldron needs it for DONE (b).
- CAULDRON_SHEAR_FAST_TICK_1 (optional) — a tame-vexxiss fullness setter so wild/tame shearing is a state read, not 60 days.
