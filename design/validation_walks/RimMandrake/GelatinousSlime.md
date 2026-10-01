# RimMandrake: The Gelatinous Slime — validation walk
subject: src/RimMandrake/GelatinousSlime  (dev source folder, own About.xml packageId `mandrake.rm.gelatinousslime`, which is never deployed standalone: the biome ships COMPOSED inside `mandrake.rm.biomes`) <!-- walklint-ok: mandrake.rm.biomes is the GENERATED composed packageId of Biomes.compose.json; no About.xml under src/ declares it -->
deps: Biotech for the gene machine (all five DLCs are always loaded); nothing else
list: baroque_wave0 (modset_builder tier: BRIDGE + mandrake.rm.biomes, no Utinni patches, so the default archive is the active one)
status-hint: a country-sized slime body that reads what stands on it (slimification ladder, ~7 days, colonists included, never hostile), cured by dry country (data-driven drying biomes) or the antidote; raw slime is antitoxin AND fee; a gene seeker hands out chosen genes at the price of a coma and a race; titanoslime apex that grows and sheds gelatids. Script: `src/RimMandrake/GelatinousSlime/validation.py` (plan `northstar_plan.py`, offline proof `selftest_slime_suite.py`).

## must be true
Each line ends `→ chain.component` (a component in validation.py) or `→ UNCOVERED: <why>`.
- Every def the mod ships resolves in the live game (a def silently discarded for a bad field or missing type is a failure, not an absence). → defs_static.all_defs_resolve
- The shipped Mod Settings defaults hold: rarity 1, flavour hooks on, titanoslime engulfs/grows/sheds on, growth permanent (titanoslimeReversible OFF, owner ruling 2026-09-21), max stage 5, higher-priority archive preferred. → defs_static.settings_defaults
- All five slime terrains carry the tag `RM_SlimeTerrain`; the exposure mechanic keys on that tag and nothing else. → defs_static.terrain_tagged
- `RM_Slimification` has four stages at severity 0 / 0.2 / 0.5 / 0.9, max severity 1.0, pain factor 0 from the third stage (placid), no stage grants a mental state (never hostile), and carries the `HediffComp_Slimification` comp that drives rate and dissolution. → defs_static.slimification_def_ladder
- Cure geography is data on the BiomeDef: Desert, ExtremeDesert, AridShrubland and Ocean each carry `decayPerDay` as shipped in `Patches/DryingBiomes.xml`; a non-drying biome and the slime biome itself carry none. → defs_static.drying_biomes_tagged
- The visitor seed GenStep is registered in the base player map generator (the patch matched). → defs_static.visitor_genstep_registered
- The default gene archive has priority 0 (a campaign archive outranks it), offers 17+ target genes and at least one rider, and every gene it names exists live. → defs_static.gene_archive_resolves
- Standing on slime terrain applies `RM_Slimification` to a colonist within ~1200 ticks (colonists are NOT exempt). → exposure_and_ladder.exposure_applies_on_slime
- Pawns off slime, pawns carrying `RM_Gene_SlimeResistance`, and the gelatid (resistant by identity) are never read. → exposure_and_ladder.exposure_skips_off_slime_and_resistant
- On the body severity rises at the ruled ~1/7 per day (about 0.0048 per 2000 ticks); the predicted rate follows the map biome's live decay, so a drying map is predicted to fall. → exposure_and_ladder.growth_rate_on_slime
- Off the body stage 1 wipes off (0.5 per day), stages 2 and 3 hold in ordinary country. → exposure_and_ladder.stage1_wipes_off_stages_2_3_hold
- In a drying biome severity decays at the biome's `decayPerDay`, even for a pawn standing on slime. → exposure_and_ladder.drying_biome_decays
- The standing alert (`Alert_Slimification`) lists a stage-3 colonist. → exposure_and_ladder.standing_alert_lists_pawn
- From stage 3 the film ends panic (law 2: placid, never aggressive); a stage-1 control in the same state is not cured. → exposure_and_ladder.stage3_ends_panic_law2
- At severity 1.0 a colonist is returned to the flow: no corpse, a slime smear and raw slime where they stood. → dissolution.returned_to_the_flow
- The slime antidote clears the film at any stage below 1.0, including on a comatose patient, costs ToxicBuildup, and is consumed; an untreated control keeps its film. → antidote.antidote_clears_film_and_poisons
- Eating raw slime cures poison AND charges slimification in the same bite (the wondrous and the fatal are one mechanism). → raw_slime_bargain.raw_slime_cures_poison_and_charges_fee
- Slimified creatures leave smears only while the read-marks setting is on. → read_marks_flavour.read_marks_follow_setting
- A Slime-marked colonist is liked less by others, more when heavily filed (opinion offsets -12 / -22 / -36). → slime_marked_opinion.marked_colonist_is_liked_less
- A blank gene seeker reports itself unprimed (the seeker comp is wired). → seeker_and_weather.blank_seeker_reports_unprimed
- Slime rain is a weather that can occur. → seeker_and_weather.slime_rain_can_fall
- Titanoslimes spawn across stages (mass roll 0 / 4 / 12), and `titanoslimeMaxStage` clamps the spawn stage. → titanoslime.stage_roll_spreads
- A cut stage-2+ titanoslime sheds a gelatid when `titanoslimeSheds` is on, and none when it is off. → titanoslime.sheds_when_cut, titanoslime.does_not_shed_when_setting_off
- Every Mod Settings field writes and reads back (rarity, spawn factor, flavour hook, engulf, grow, reversible, archive preference). → settings_flip.*
- The Slime-marked increment of the gene injectable (x2 for The Reek, none with Pheromone charm), the extract job on liquid slime, the fast injected clock (~3 days) and the antidote race. → UNCOVERED: no bridge tool primes or loads a seeker (the archive pick is a dialog); needs companion tool `jawa/slime_seeker_load` (target gene, rider gene) so a loaded seeker can be spawned and used. Proposed item SLIME_SEEKER_LOAD_TOOL_1.
- Farm conversion (growing zone on slime grass reverts to rich slime). → UNCOVERED: needs a map on the RM_GelatinousSlime biome (the gate is read at map FinalizeInit) and ~50,000 ticks of sampling (a few cells per 2500-tick pass): statistical, §4 boundary.
- The visitor trickle and the generation-time visitor seed (3-5 never-hostile arrivals at severity 0.25-0.7). → UNCOVERED: needs an RM_GelatinousSlime map generated fresh; the site recipe for a slime-biome scratch map is owed (SLIME_BIOME_SITE_1).
- Titanoslime engulf, permanent growth through starving / dry ground / wounds, save-load round trip. → UNCOVERED: needs feeding and 70,000 ticks off slime; proven by hand 2026-09-21 (TITANOSLIME_PERMANENT_GROWTH_LIVE_1); `titanoslimeReversible` default is guarded by settings_defaults.
- Biome worldgen rarity (`rarityFactor`), `titanoslimeSpawnFactor` applying to rosters on WriteSettings, the "Entry recorded" mote text. → UNCOVERED: worldgen is frozen (planet painted once, CLAUDE.md); the roster field is non-public; mote text has no bridge reader.
- Art, sprites, overlays. → UNCOVERED: visual, judge pass (none of this mod's art exists yet; magenta is expected).

## the walk
1. [L] Player.log after load names no `RM_Slimification`, `RM_Titanoslime`, `RM_Gelatid` or GelatinousSlime file in a config error or XML error (the first two faults of GELATINOUSSLIME_FIRST_LOAD_ERRORS_1 were exactly this)
2. [D] `jawa/get_defs` over every def in `Defs/` → `foundCount` equals the requested count and `notFound` is empty
3. [B] stand colonists on slime and on concrete, wait, read hediffs → see the components above

## anti-guessing notes
RULED OUT: "the cure geography patch is inert" — it was (PATCH_FILES_UNDER_DEFS_INERT_1, patch lived under Defs/); `drying_biomes_tagged` reads the live BiomeDef modExtensions and fails if any of the four is missing.
RULED OUT: "titanoslime growth can shrink under the shipped defaults" — `titanoslimeReversible` default is False, proven live 2026-09-21; `settings_defaults` guards the default.
RULED OUT: "a GeneDef with an Aptitude `<li>` loads" — the custom loader discards the def silently (SLIME_GENE_ARCHIVE_BUILD_1); `all_defs_resolve` and `gene_archive_resolves` catch any def that vanishes.
RULED OUT: "slimification ever makes a creature hostile" — law 2; `slimification_def_ladder` (no mentalStateGivers) and `stage3_ends_panic_law2`.

## north star
state: DRAFT
validated-hash:

DRAFT, binds nothing. The owner has not ruled bars for this mod. The functional script above is agent-approved (debug_process.md §6); only his `modcheck validate --owner-said` turns lines into bars.
