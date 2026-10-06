# RimMandrake: Miasma — validation walk
subject: src/RimMandrake/Miasma  (packageId `mandrake.rm.miasma`)
deps: `brrainz.harmony` (modDependencies); loads after `mandrake.rm.environmentalhazards`, `mandrake.rm.flowworks`, `mandrake.rm.creaturebehaviors` (the surge, stranding pools, weather and warden placement are shared-assembly classes). Fold-aware: folded into `mandrake.rm.biomes`, active under the composed name 'RimMandrake: Baroque Biomes' (Biomes.compose.json).
list: a tier carrying Miasma (or the composed biomes mod) + Environmental Hazards + Creature Behaviors, all five DLCs, plain open map (the suite's proofs run on the CURRENT map via `RM_MiasmaProof`)
status-hint: MIASMA_FIRST_SCRIPT_1 (+ MIASMA_SETTINGS_SWITCHES_1, MIASMA_COVERAGE_GAPS_1, MIASMA_DECAY_CELLS_1, MIASMA_ROTTING_BED_CORPSES_1, MIASMA_MOTHERS_PRICE_1) — settings round-trips, decay cells, rotting bed, mother's price, attar, free-tier def loads. Script: `src/RimMandrake/Miasma/validation.py`. NEVER RUN LIVE.

Sources: `About/About.xml`, `Source/RM_MiasmaMod.cs` (18 settings), `RM_MiasmaProof.cs`, `RM_DecayCells.cs`, `RM_RottingBed.cs`, `RM_MothersPrice.cs`, `RM_Attar.cs`, `RM_WardenMotherSuccession.cs`, `RM_MapComponent_YoungCall.cs`, `RM_MapComponent_FlotsamYard.cs`, `RM_CompPlantPredator.cs`, `RM_AmbushFrogHunting.cs`, `Defs/`, `infrastructure/state/items/MIASMA_MECHANICS_1.md`.

## must be true
- Every settings field with a switch or number the validation script round-trips (set alt, read back, restore) and ships at its shipped default: plantPredationEnabled, pollinationGateEnabled, strandedDeformationEnabled, strandedDeformationChance, ambushFrogHunts, attarEnabled, youngCallEnabled, decayCellsEnabled, decayCellPowerMultiplier, rottingBedCorpsesEnabled, rottingBedRotDays, mothersPriceEnabled, youngPriceOffset. → settings_roundtrip.roundtrip_plantPredationEnabled (and one `roundtrip_<field>` component per field above)
- The five settings fields biomeRarityFactor, wardenSuccessionEnabled, selfTameChancePerCheck, flotsamEnabled and flotsamAmount round-trip too (added to the script 2026-10-06; `NEW = list(DEFAULTS)`). → settings_roundtrip.roundtrip_biomeRarityFactor (and one `roundtrip_<field>` component per field)
- With plant predation, the pollination gate or stranded deformation switched off, that mechanic stops (predation needs a plant beside a wild scuttler; the gate a worldgen plant pass; deformation a stranding pool). → switches_gate_mechanics.mechanics_stop_with_switch_off (UNMEASURED live: each needs a live Miasma quicktest map)
- The free-tier salt crust `RM_MiasmaSaltCrust` loads without the campaign patches and a surge recede repaints land to it. → salt_crust_free_tier.salt_crust_paints_without_campaign (UNMEASURED live: needs a tier without mandrake.rut.patches and a live Miasma map)
- The four free-tier young (opee, colo, gorger, reefback; PawnKindDefs and ThingDefs) survive the loader. → nursery_young_free_tier.four_young_defs_load
- A surge recede on a free-only tier strands at least one young. → nursery_young_free_tier.young_strand_on_recede (UNMEASURED live: the stranding pool is a map GenStep the bridge cannot regenerate)
- A decay cell's power output falls with its feed level and stops empty. → decay_cells.output_falls_with_feed_and_stops_empty
- `decayCellsEnabled` off: decay cells make no power. → decay_cells.switch_off_makes_no_power
- A decay cell's lifetime feed turns it into a rotting bed. → decay_cells.lifetime_feed_turns_cell_into_rotting_bed
- A rotting bed rots a stored corpse down to bones (count follows body size) and a named skull. → rotting_bed_corpses.corpse_leaves_bones_and_named_skull
- Haulers choosing the rotting bed for corpses. → UNCOVERED: the proof drops a corpse beside the bed and steps 2 days; hauler job choice is not driven (validation.py chain docstring)
- Bringing a held stranded young back wins the warden mother's tolerance of the colony. → mothers_price.returning_a_young_wins_her_tolerance
- Selling a stranded young to the buyer betrays her forever (nobody tolerated, succession voided). → mothers_price.selling_a_young_betrays_her_forever
- A stranded young's cry sends the nearest warden mother toward the water edge and she stops there; the first-cry letter fires. → young_call.cry_and_mother_heads_for_water (UNMEASURED live: needs a placed young and a read of the mother's CurJob over ticks on a Miasma map)
- The bozzuga ambush frog's defs load. → ambush_frog_free_tier.bozzuga_defs_load
- The bozzuga hunts scuttlers and stranded young (`ambushFrogHunts`). → ambush_frog_free_tier.bozzuga_hunts (UNMEASURED live: needs both spawned on a Miasma map and the predator-hunt job read over ticks)
- The swarm composter's defs (fever swarm, karrobel, delta loam) load. → swarm_composter_free_tier.swarm_karrobel_loam_defs_load
- A swarm-gated mangal (RM_Thessamor) does not spread where no swarm lives. → swarm_composter_free_tier.mangal_gated_on_swarm (UNMEASURED live: needs a Miasma map's wild plant pass, which the bridge cannot regenerate)
- After a surge recede, river goods stand on root-line cells and none on dry inland ground (`flotsamEnabled`, `flotsamAmount`). → flotsam_yard.flotsam_after_surge_in_root_lines (UNMEASURED live: needs a live Miasma quicktest map)
- Attar glaze adds +3 Beauty to an artwork and only once. → attar_glaze_and_balm.glaze_adds_beauty_and_only_once
- Attar balm fades the first old scar and never a fresh wound. → attar_glaze_and_balm.balm_fades_scar_not_fresh_wound
- The attar still carries the attar recipe (`attarEnabled`). → attar_glaze_and_balm.attar_recipe_on_still
- Warden mother self-taming of the young, the water-scoped training backstop and succession of the crèche (`wardenSuccessionEnabled`, `selfTameChancePerCheck`). → UNCOVERED: no chain exists; needs a spawned warden mother with young and a seeded check over game time (named item to file: MIASMA_WARDEN_SUCCESSION_SEED_1)
- The biome's own six mechanics (salinity gradient axis, breath-tide surge, stranding pools, weather lock and exposure, fever-forged boons, warden and crèche placement) are shared-assembly classes gated by Environmental Hazards' own switches. → UNCOVERED: owned by the EnvironmentalHazards script, not this mod's code
- The delta forest's look, haze and the warden mother's art. → UNCOVERED: visual, judge pass or owner (static_checks only proves the texture files exist)

## the walk
Static (offline): `python3 src/RimMandrake/Miasma/validation.py` checks every settings field is Scribed, drawn in `DoWindowContents` and defaults to its shipped value, every `.cs` is in `RM_Miasma.csproj`, and the warden mother's art files resolve. Live (never run from here): the suite round-trips each switch through `jawa/mod_settings_field`, then drives `RM_MiasmaProof` static methods on the current map for decay cell, rotting bed, mother's price, glaze and balm; chains needing a generated Miasma map record UNMEASURED.

## anti-guessing notes
RULED OUT: "a live-only chain that cannot run is a FAIL" — commit "Miasma validation: today's live-only chains report UNMEASURED not FAIL"; a missing instrument is UNMEASURED, never FAIL.
RULED OUT: "a bone count of 6 means the bones curve is wrong" — commit "run17 fixes": the generated colonist was a teen; bones follow body size (round(size x 8)), so the proof kills an adult baseliner (size 1.00 gives 8).
RULED OUT: "an `<Operation MayRequire>` or folded packageId gate still protects a row" — commit "Stale folded-id MayRequire gates repointed to mandrake.rm.biomes": folded ids are never active, so those rows and extensions were silently skipped.

## north star
state: DRAFT
validated-hash:

DRAFT, binds nothing. This mod has no owner-ruled experience bars yet; the intended-function lines above are the functional script's coverage and are agent-owned.
