# WEEPING_STONES_FIRST_SCRIPT_1 — worker note and live-run sheet

Status: authored offline, READY TO RUN (nothing here has touched the bridge, ModsConfig or a deploy).

## What exists

| file | role |
|---|---|
| `src/RimMandrake/WeepingStones/validation.py` | modcheck Suite, 20 chains, 47 components, toggle floor met (`stockedPoolsEnabled`) |
| `src/RimMandrake/WeepingStones/northstar_plan.py` | driver plan, `USE_SUITE=True`, `EXPECT_MODS=("mandrake.rm.biomes",)` |
| `src/RimMandrake/WeepingStones/northstar_site.py` | pre-flight: map >= 150, five DLCs, setting at default, weather, composed-deploy drift |
| `src/RimMandrake/WeepingStones/selftest_weepingstones.py` | offline proof: healthy world 47/47 PASS, 19 deliberate breaks each redden exactly the intended component |
| `design/validation_walks/RimMandrake/WeepingStones.md` | walk, `## must be true` with `→ chain.component` / `→ UNCOVERED` arrows, DRAFT north star |
| `src/RimMandrake/Utils/modset_builder.py` | new tier `weepingstones_solo` |
| `src/RimMandrake/WeepingStones/About/About.xml` | corrected two false statements (see below) |

EXPECT_MODS note: the brief says use the About.xml packageId. That id (`mandrake.rm.weepingstones`) is never in ModsConfig: the biome ships composed inside `mandrake.rm.biomes` (same packaging as Pyrelands), so pre-flight's active-mod check would REFUSE on it. `mandrake.rm.biomes` is what a run must see.

## Live-run sheet

1. Take the bridge: `python3 src/RimMandrake/rimflow/cli.py bridge take --for "WEEPING_STONES_FIRST_SCRIPT_1 live run"`.
2. Deploy the composed mod current, game CLOSED: `python3 src/RimMandrake/Utils/deploy_custom_mods.py --compose biomes` (plan), then `--apply` if it shows `+`/`~` lines naming WeepingStones or EnvironmentalHazards. (Pre-flight re-checks this and refuses on drift.)
3. Kill the game FIRST (modset_builder refuses while Player.log is < 3 min old), then `python3 src/RimMandrake/Utils/modset_builder.py --tier weepingstones_solo --apply`. The list is 13 mods: BRIDGE, Harmony, VEF, Alpha Biomes, FlowWorks, Luminous Pigment, `mandrake.rm.biomes`, five DLCs. It resolved with nothing MISSING on 2026-10-01 (not applied).
4. Launch via Steam. Wait for the `Bridge token:` line in `Player.log` (expect low minutes: 13 mods, but the composed biomes mod is 27 biome folders; measure and record it).
5. `rimworld/start_debug_game_ready` (quicktest map, ~90 s). Map must be >= 150 x 150 on both axes (pre-flight checks). The suite builds its fixtures 45 cells off the map centre, 29 x 29, so the start colonists are untouched; it needs NO god mode.
6. One line, Windows Python, repo-relative: `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod WeepingStones --plan src/RimMandrake/WeepingStones/northstar_plan.py`. Results JSON lands in `Transient/northstar/WeepingStones_<utc>.json`; progress lines (`[ws] ...`, `[ws-note] ...`) stream to stderr.
7. Release the bridge the moment it stops.

Tick budget: about 12,000 game ticks of `wait_ticks` (900 + 1500 + 1500 + 1200 + 1200 + 1500 + 3 x 2500 flora), roughly 4-5 minutes at the measured ~53 ticks/s, plus ~300 bridge calls. Nothing is time-sensitive; the game stays paused between waits.

Site prerequisites: a current map that is NOT an ocean map; weather is locked Clear by pre-flight; pawns: the suite spawns its own handler colonist per chain and removes pawns it created in its pad at teardown. The `stockedPoolsEnabled` setting must read True at start (pre-flight) and is restored in a `finally`.

Components that are NOT independent: every `site_ready_*` setup component poisons the rest of its chain (UNMEASURED), by design. The pure reads (`defs_resolve`, `biome_roster` after its probe, `cuisine_wiring`, `settings_and_designator`) do not poison one another.

## What PASS / FAIL / UNMEASURED means

| component | PASS means | FAIL means (class to assign) | how it was proven able to fail |
|---|---|---|---|
| `log_clean.player_log_names_no_weepingstones_error` | no Config error / xref / missing-type / exception line names this mod's content | MOD (a def or dll defect); note a stale deployed EnvironmentalHazards.dll shows as 'Could not find type named ...RM_WaterTruceExtension' = SITE | selftest: a `Config error in RM_Murrin` log line; an unrelated-mod error line stays green. Live break: add a bogus `<thoughtClass>` to an `RM_Ate...` ThoughtDef and reload |
| `defs_resolve.resolve_probe_sees_absence` | get_defs answers notFound for an invented def | HARNESS (instrument cannot say absent) | selftest drives it |
| `defs_resolve.defs_resolve_*` (10) | every def in that group of the mod's own XML loaded, from our package | MOD (def dropped: missing type, bad XML) or SITE (stale deploy) ; "from another mod" = a donor shadows our defName | selftest: a def absent / a plant owned by another package. Live break: put `--` inside an XML comment in a WorkGiver file |
| `defs_resolve.defs_pair_up_by_convention` | all 15 `RM_<K>Meat` / `<K>BreedingStock` defs exist | MOD (a rename makes HARVEST/CULL/NET succeed and drop nothing) | rename `RM_SkarrinMeat` |
| `biome_roster.biome_flags_and_densities` | generatesNaturally false, densities > 0 and equal to the XML | MOD (set `animalDensity` 0: roster dead) | selftest zero_density / natural_gen |
| `biome_roster.wild_animals_wired` / `wild_plants_wired` | every XML row (whose donor mod is on the tier) resolves at its XML commonality | MOD or SITE (a patch zeroed/removed a row) | selftest roster_zero_commonality. `AA_Eyeling` (needs sarg.alphaanimals, not on the tier) is skipped and NOTED, not asserted |
| `biome_roster.vhorrin_never_ambient_and_probe_is_honest` | probe says `RM_Sillik` spawning, a made-up name absent, `RM_Vhorrin` absent | MOD (vhorrin on a wild list) or HARNESS (probe states wrong) | selftest vhorrin_wild |
| `biome_roster.stocked_catch_has_living_counterpart` | each `RM_<K>Catch` has `RM_<K>` on the roster | MOD | delete one roster row |
| `biome_roster.fish_types_wired` | `fishTypes` holds every XML fish and maxFishPopulation 660 | MOD; UNMEASURED if `get_defs` cannot serialise `fishTypes` (UNPROVEN shape) | selftest no_fish |
| `biome_roster.water_truce_extension_present` | `RM_WaterTruceExtension` in the biome's modExtensions | MOD/SITE (stale EnvironmentalHazards.dll); UNMEASURED if `modExtensions` unreadable (UNPROVEN shape) | selftest no_truce |
| `cuisine_wiring.recipes_on_both_stoves` | all 5 recipes listed on `ElectricStove` and `FueledStove` (control: vanilla `CookMealSimple` readable) | MOD (patch matched nothing) | selftest no_recipe_patch |
| `cuisine_wiring.rottable_items_tick` | no Rottable-carrying item has tickerType Never | MOD. NOTE 31 items are checked; `OrganicProductBase`-derived breeding stock / `RM_KarrekPaste` set no tickerType of their own, so a real FAIL here is plausible and would be a genuine MOD finding (the HulduFat bug class) | selftest ticker_never |
| `settings_and_designator.setting_default_on_and_assembly_loaded` | field reads True | MOD (default drifted) / HARNESS (assembly not found) | read-back; a flipped default |
| `settings_and_designator.designator_listed_when_on` | a Pool pen designator is in the Zone category (control: Growing zone present) | MOD (patch matched nothing); UNMEASURED if the architect list shape differs from what is assumed (UNPROVEN) | selftest no_designator |
| `settings_and_designator.designator_hidden_when_off` | with the setting False the pen designator is not listed, then restored | MOD, or HARNESS if `list_architect_designators` ignores `Visible` (check `includeHidden` default before calling it a mod defect) | selftest toggle_ignored |
| `pen_zone.pen_refuses_dry_floor` | a rect of dry cells makes no RM_Zone_PoolPen | MOD | selftest pen_on_dry |
| `pen_zone.pen_covers_exactly_the_water` | a 6x6 rect straddling the shore makes ONE pen of exactly the 18 water cells | MOD | same |
| `job_net...` | wild skarrin gone, exactly one `RM_SkarrinBreedingStock` | MOD; HARNESS if `ordered_job` is not accepted | selftest net_noop |
| `job_stock...` | breeding stock consumed, 1 skarrin released in the pad | MOD | selftest stock_noop |
| `job_stock_outside_pen...` | stock leaves the ground (job ran) and NO skarrin appears | MOD. If the stock is still on the ground the job never ran = HARNESS/SITE (reported as such in the detail) | selftest stock_in_dry |
| `job_feed...` | the meal is consumed at the pen | MOD / HARNESS | selftest feed_noop |
| `job_harvest...`, `job_cull...` | pawn gone; 2-4 skarrin meat / 18-24 vhorrin meat (range asserted only when the `list_things` row exposes a stack size: UNPROVEN key, else noted) | MOD | selftest harvest_noop |
| `flora_*...` (3) | forced harvest of 3 mature plants yields the custom product | MOD (harvestedThingDef) / HARNESS (forced `Harvest` job) | selftest flora_noop |

UNMEASURED is never a pass. The four UNPROVEN response shapes (architect list rows, `get_defs` of `fishTypes`/`modExtensions`, a stack-size key on `list_things` rows) are named in the validation.py header; a live run that reads them UNMEASURED is a HARNESS finding to fix in the script, not a mod defect.

## Not covered (named in the walk as UNCOVERED, with why)

Pen READ gauge (needs a Zone inspect-string tool: file `POOL_ZONE_INSPECT_TOOL_1`, NOT filed by this agent), the three per-pulse random mechanics and the toggle's tick gate (statistical), work-giver autonomy (forced jobs bypass the scanner), the biome worker score (inert), flyers, art and the Utinni fauna patch.

## Corrections made on sight (CLAUDE.md: correctness outranks seat ownership)

`src/RimMandrake/WeepingStones/About/About.xml` said stocked pools "Stays OFF by default" and that the jobs, vhorrin emergence and vizhik escape were "STILL OWED". The C# default is `true` (`RM_WeepingStonesSettings.cs`, flipped in wave 4) and all of those shipped in waves 3 and 4. Both sentences rewritten.

## Findings while authoring (nothing live yet)

- The older `weepingstones` tier names `mandrake.rut.rotsporekit`, a retired packageId (`modset_builder.py --list` shows it MISSING); left alone, `weepingstones_solo` is the working tier.
- `jawa/get_defs` cannot read `wildAnimals` (non-public list): the roster is read with `jawa/biome_probe`.
- The mock in `northstar_driver/transport.py` is Graffiti-shaped, so `cli.py run --mock --mod WeepingStones` completes but reads mostly FAIL; the faithful offline proof is `selftest_weepingstones.py`.
- `modcheck floor --all` lists WeepingStones as `no bar` (DRAFT north star, nothing owner-bound), the same as every other DRAFT walk; the Mod Settings toggle floor is met (0 uncovered of 1).
