# RimMandrake: Titanic Creatures — validation walk
subject: src/RimMandrake/TitanicCreatures  (packageId `mandrake.rm.titaniccreatures`)
deps: `brrainz.harmony`; soft (reflection only) `neku.largepawns` for the multi-cell footprint
list: a tier carrying this mod and Harmony, plain open map; an Elephant (baseBodySize 4, tier T1) is the vanilla beast the wake chain walks
status-hint: TITANIC_CREATURES_FIRST_SCRIPT_1 — engine only (no creature wired); first script drafted, never run live; T2/T3 mechanics need a bodySize >= 8 / >= 20 race that does not exist in a mod-only list

Sources: `About/About.xml`, `Defs/**` (tier def, 4 crush rules, corpse site, harvest job + workgiver), `Source/RM_TitanicCreaturesSettings.cs` (12 settings), `Source/Wake/*`, `Source/Tiering/*`, `Source/CorpseSite/*`, `Source/Footprint/*`.

## must be true
- Every def the mod ships (tier def, crush rules, corpse site, harvest job, harvest work giver) resolves; a bogus name reads notFound. → defs_resolve.control_probe_can_say_absent, defs_resolve.every_shipped_def_resolves
- Every Mod Settings field (`wakeEnabled`, `wakeCrushDamageMultiplier`, `wakeFilthTrailChance`, `roofAvoidanceEnabled`, `yieldCurveEnabled`, `yieldCurveMinFactor`, `corpseSiteEnabled`, `corpseSiteHarvestMeatPerSession`, `corpseSiteHarvestLeatherPerSession`, `corpseSiteMeatSpoilagePerDay`, `corpseSiteLeatherSpoilagePerDay`, `corpseSiteWorkHoursPerSession`) round-trips. → settings_roundtrip.wakeEnabled_round_trips, settings_roundtrip.wakeCrushDamageMultiplier_round_trips, settings_roundtrip.wakeFilthTrailChance_round_trips, settings_roundtrip.roofAvoidanceEnabled_round_trips, settings_roundtrip.yieldCurveEnabled_round_trips, settings_roundtrip.yieldCurveMinFactor_round_trips, settings_roundtrip.corpseSiteEnabled_round_trips, settings_roundtrip.corpseSiteHarvestMeatPerSession_round_trips, settings_roundtrip.corpseSiteHarvestLeatherPerSession_round_trips, settings_roundtrip.corpseSiteMeatSpoilagePerDay_round_trips, settings_roundtrip.corpseSiteLeatherSpoilagePerDay_round_trips, settings_roundtrip.corpseSiteWorkHoursPerSession_round_trips
- The size ladder is the one tier def (T1 4, T2 8, T3 20), strictly ascending, as deployed. → tier_ladder.thresholds_match_xml_and_ascend
- The curated crush table says what crushes at which tier and protects chunks. → crush_rules.rules_read_back_as_the_xml_says
- The four Harmony patches (wake on `Thing.Position`, roof avoidance on `CostToMoveIntoCell`, corpse-site conversion on `Corpse.SpawnSetup`, yield curve on `Pawn.ButcherProducts`) are attached by this mod. → harmony.Thing_set_Position_postfix_attached, harmony.Pawn_PathFollower_CostToMoveIntoCell_postfix_attached, harmony.Corpse_SpawnSetup_postfix_attached, harmony.Pawn_ButcherProducts_postfix_attached
- A T1 creature leaves a rubble trail and tramples fragile plants as it walks; an untiered creature does not. → wake.t1_beast_trails_rubble_and_tramples_plants
- `wakeEnabled` off: it walks through everything harmlessly. → wake.wake_off_leaves_no_trail
- `wakeCrushDamageMultiplier` scales the blow. → wake.crush_damage_multiplier_scales_the_blow
- A T2 titan holes thin roofs and crushes walls; a T3 crushes buildings outright. → not_driven.t2_holes_thin_roofs_and_crushes_walls (UNMEASURED: no bodySize >= 8 race)
- The largest tier's corpse becomes a harvestable landmark, harvested over days. → not_driven.t3_corpse_becomes_a_harvest_site (UNMEASURED: no bodySize >= 20 race)
- T1-T2 butcher yield is reduced to the configured floor. → not_driven.butcher_yield_curve_reduces_t1_t2_yield (UNMEASURED: needs a butcher job and control)
- A titan never paths under an overhead-mountain roof. → not_driven.thick_roof_cost_penalty_steers_paths (UNMEASURED: path-cost read; the patch being attached is proven by the harmony chain; commit 7c9b0e9ef fixed this)
- The footprint rides Large Pawns when present and degrades to one cell when absent. → not_driven.large_pawns_footprint_bridge (UNMEASURED: soft dependency not loaded)
- Every tiered race is opted into Huge Things, so it is selected by clicking anywhere on its drawn body. → UNCOVERED: the hitbox is Huge Things' mechanism and its suite's not_driven.huge_pawn_hitbox_covers_drawn_body; no tiered race with a large drawSize exists in a mod-only list
- Any creature is wired to the engine. → UNCOVERED: out of scope by design (About.xml: engine only; campaign content gives a race the `RM_TitanicExtension` or a high bodySize)

## the walk
1. [D] `jawa/get_defs` over every def derived from `Defs/**/*.xml`; a bogus def reads notFound   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on the 12 fields   # settings_roundtrip
3. [D] `jawa/get_defs RM_TitanicTierDef/RM_TitanicTiers_Default`; `RM_CrushRuleDef/*` fields crushable,minTier   # tier_ladder, crush_rules
4. [D] `jawa/harmony_patches` for the four patched methods; an owner of `mandrake.rm.titaniccreatures`   # harmony
5. [B] clear; Elephant on lane A and Rat on lane B each with six 5-HP `Plant_Grass`; `ordered_job Goto` 15 cells; wait 500 ticks; count `Filth_RubbleRock` and surviving plants per lane; repeat with `wakeEnabled` off and the multiplier at 0.1   # wake
6. [B] bodySize-8/20 races, butchering, pathing, Large Pawns   # not_driven (UNMEASURED)
X. [S] (human pass) a titan reads as mass: it flattens what is in its way and leaves a trail; owner decides.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "an Elephant is T1 because the wiki says bodySize 4" — the chain reads `BodySize` from `jawa/pawn_stats` before judging and records UNMEASURED if it is below the floor; a blank read proceeds.
RULED OUT: "the rubble trail alone proves the wake" — it is a 0.35 chance per cell step and fires for T1 and above only; the plants (5 HP, one crush blow of 20) and the Rat control carry the differential.
RULED OUT: "roof avoidance works because the postfix is attached" — attachment is the harmony chain; the cost effect on a path is listed UNMEASURED, not inferred.
