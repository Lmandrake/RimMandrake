# RimMandrake: Huge Things — validation walk
subject: src/RimMandrake/HugeThings  (packageId `mandrake.rm.hugethings`; Titanic Creatures, `mandrake.rm.titaniccreatures`, merged in 2026-10-07) <!-- walklint-ok: the retired id (merged into this mod 2026-10-07) or the titan half's kept Harmony owner id -->
deps: `brrainz.harmony`; soft (reflection only) `neku.largepawns` for the titans' multi-cell footprint; content under test comes from `mandrake.rm.biomes` (TheRot's `RM_Nogtyl`, brommok timber)
list: a tier carrying Harmony, this mod and `mandrake.rm.biomes`; plain open map; an Elephant (baseBodySize 4, tier T1) is the vanilla beast the wake chain walks
status-hint: HUGE_THINGS_FOOTPRINT_1 + TITANIC_CREATURES_FIRST_SCRIPT_1 — one merged script 2026-10-07, never run live; T2/T3 mechanics need one of our bodySize >= 8 / >= 20 races in the list

Sources: `About/About.xml`, `Defs/**` (trunk blocker, tier def, 5 crush rules, corpse site, harvest job + workgiver),
`Source/RM_HugeThingsSettings.cs` (one settings tree: giant plants / giant animals masters), `Source/*.cs`, `Source/Titanic/**`,
`Source/Kernel/*.cs`, `../TheRot/Patches/RotGiants_HugeFootprint.xml`, `design/RimMandrake/giant_footprint_design_2026-10-07.md`.

## must be true
- The trunk blocker def ships and resolves; a bogus name reads notFound. → defs_resolve.control_probe_can_say_absent, defs_resolve.blocker_def_resolves
- Every Mod Settings field (`giantPlantsEnabled`, `plantTrunkEnabled`, `plantSelectionEnabled`, `plantTrunkScale`, `plantTrunkDamageEnabled`, `plantItemPushEnabled`, `giantAnimalsEnabled`, `pawnHitboxEnabled`, `pawnHitboxScale`, `largePawnsFootprintEnabled`, `tierThresholdsCustom`, `tierT1MinBodySize`, `tierT2MinBodySize`, `tierT3MinBodySize`, `wakeEnabled`, `wakeCrushDamageMultiplier`, `wakeFilthTrailChance`, `wakeRoofHolingEnabled`, `giantPlantSmashEnabled`, `giantPlantSmashMinTier`, `roofAvoidanceEnabled`, `yieldCurveEnabled`, `yieldCurveMinFactor`, `corpseSiteEnabled`, `corpseSiteHarvestMeatPerSession`, `corpseSiteHarvestLeatherPerSession`, `corpseSiteMeatSpoilagePerDay`, `corpseSiteLeatherSpoilagePerDay`, `corpseSiteWorkHoursPerSession`) round-trips. → settings_roundtrip.<field>_round_trips, one per field
- The click-area patch (`Thing.CustomRectForSelector` getter postfix) is attached by this mod. → harmony.Thing_get_CustomRectForSelector_postfix_attached
- A full-grown huge plant blocks exactly one of its variants' measured ground-contact cell sets (never its own cell), and nothing south of it (so it stays reachable to cut). → trunk.full_grown_giant_gets_its_measured_footprint
- `plantTrunkEnabled` off: no plant blocks anything. → trunk.toggle_off_clears_the_trunk
- Cutting or killing the plant removes its trunk at once. → trunk.cutting_the_plant_removes_the_trunk
- A young huge plant (growth below `minGrowthToBlock`) blocks nothing. → trunk.young_giant_blocks_nothing
- The footprint follows the drawn picture, growth and the measured masks. → UNCOVERED: offline, pinned by `selftest_hugethings_footprint.py`, the kernel fuzz `Utils/selftest_hugethings_fuzz.py` (+ `mutate_hugethings_fuzz.py`) and `Utils/selftest_hugethings_lint.py`; no live component needed
- Clicking anywhere on a huge plant's drawn picture selects it. → not_driven.click_anywhere_on_picture_selects_plant (UNMEASURED: no selection-rect read tool)
- Clicking anywhere on a huge pawn's drawn body selects it. → not_driven.huge_pawn_hitbox_covers_drawn_body (UNMEASURED)
- After save/load a trunk re-links to its plant (no duplicates, no orphans). → not_driven.trunk_relinks_after_save_load (UNMEASURED)
- Giants generated with a new map get their trunks once generation finishes. → not_driven.mapgen_giants_get_trunks (UNMEASURED)
- A shot or blast into a trunk cell damages the plant, once per projectile / beam / blast. → not_driven.shot_into_trunk_damages_the_plant_once (UNMEASURED live; offline kernel fuzz `damage` + static patch checks)
- A growing footprint never traps a pawn, never destroys an item (items are pushed outside every footprint or the cell waits), never cuts a giant's root off from cutting access. → not_driven.growth_never_traps_a_pawn (UNMEASURED live; offline kernel fuzz `planner`)
- Blockers never carve or split zones. → not_driven.zone_cells_survive_blockers (UNMEASURED live; static patch check)
- Every def the mod ships (trunk blocker, tier def, crush rules, corpse site, harvest job, harvest work giver) resolves. → defs_resolve.every_shipped_def_resolves
- The size ladder is the one tier def (T1 4, T2 8, T3 20), strictly ascending, as deployed. → tier_ladder.thresholds_match_xml_and_ascend
- The curated crush table says what crushes at which tier and protects chunks and the giant trunk. → crush_rules.rules_read_back_as_the_xml_says
- The four Harmony patches (wake on `Thing.Position`, roof avoidance on `CostToMoveIntoCell`, corpse-site conversion on `Corpse.SpawnSetup`, yield curve on `Pawn.ButcherProducts`) are attached under the titan half's Harmony id `mandrake.rm.titaniccreatures` (kept through the merge; a patch owner name, not a packageId). → harmony_titans.Thing_set_Position_postfix_attached, harmony_titans.Pawn_PathFollower_CostToMoveIntoCell_postfix_attached, harmony_titans.Corpse_SpawnSetup_postfix_attached, harmony_titans.Pawn_ButcherProducts_postfix_attached <!-- walklint-ok: the retired id (merged into this mod 2026-10-07) or the titan half's kept Harmony owner id -->
- A T1 creature leaves a rubble trail and tramples fragile plants as it walks; an untiered creature does not. → wake.t1_beast_trails_rubble_and_tramples_plants
- `wakeEnabled` off: it walks through everything harmlessly. → wake.wake_off_leaves_no_trail
- `wakeCrushDamageMultiplier` scales the blow. → wake.crush_damage_multiplier_scales_the_blow
- A T2 titan holes thin roofs and crushes walls; a T3 crushes buildings outright. → not_driven.t2_holes_thin_roofs_and_crushes_walls (UNMEASURED until a list carries one of our T2 races; see the walk plan)
- The largest tier's corpse becomes a harvestable landmark, harvested over days. → not_driven.t3_corpse_becomes_a_harvest_site (UNMEASURED until a list carries a T3 race)
- T1-T2 butcher yield is reduced to the configured floor. → not_driven.butcher_yield_curve_reduces_t1_t2_yield (UNMEASURED: needs a butcher job and control)
- A titan crossing a cell under overhead mountain moves very slowly (a step-cost penalty; route choice is the engine's Burst pathfinder and does not see it). → not_driven.thick_roof_slows_a_titan (UNMEASURED: step-cost read; attachment is proven by harmony_titans)
- The footprint rides Large Pawns when present and degrades to one cell when absent. → not_driven.large_pawns_footprint_bridge (UNMEASURED: soft dependency not loaded; `largePawnsFootprintEnabled`, restart)
- Any creature is wired to the engine. → UNCOVERED: out of scope by design (About.xml: engine only; campaign content gives a race the `RM_TitanicExtension` or a high bodySize)
- Either master off is vanilla for its half; a detailed behaviour runs only with its master on (kernel `HugeGates`). → not_driven.giant_plants_master_off_is_vanilla, not_driven.giant_animals_master_off_is_vanilla (UNMEASURED live; offline kernel fuzz `gates`)
- A titan at or above the smash tier (`giantPlantSmashMinTier`, T3 by default) damages every giant plant whose trunk or solid root it brushes, one heavy crush per step per giant, through the plant's own damage route, until it falls. → not_driven.t3_titan_smashes_a_giant_plant (UNMEASURED live; offline kernel fuzz `smash`, `smashstep`)
- A smaller titan goes around a giant's trunk as a wall and never crushes the giant through the crush table. → not_driven.smaller_titan_goes_around_a_giant (UNMEASURED live; offline kernel fuzz `gates` for WakeMayCrush)
- Custom size tiers (`tierThresholdsCustom`) move the ladder; only a rising T1 < T2 < T3 is used. → not_driven.custom_tiers_move_the_ladder (UNMEASURED: restart between loads)
- Items under a growing trunk are pushed to the nearest free cell, never wiped; `plantItemPushEnabled` off leaves the cell open. → not_driven.growth_pushes_items_never_wipes_them (UNMEASURED live; offline kernel fuzz `items`)

## the walk
1. [D] `jawa/get_defs` over every def derived from `Defs/**/*.xml` + ThingDef/RM_Nogtyl; a bogus def reads notFound   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on every field of `RimMandrake.HugeThings.RM_HugeThingsSettings`   # settings_roundtrip
3. [D] `jawa/harmony_patches Thing get_CustomRectForSelector` (owner `mandrake.rm.hugethings`); the four titan patches (owner `mandrake.rm.titaniccreatures`)   # harmony, harmony_titans <!-- walklint-ok: the retired id (merged into this mod 2026-10-07) or the titan half's kept Harmony owner id -->
4. [B] clear 30; `jawa/artboard_stage phase=subjects` plant RM_Nogtyl growth=1 at the anchor; wait 120; `jawa/list_things RM_HugeTrunkBlocker` in the 17x17 box around it = one of the Nogtyl variants' measured contact counts (read from the Rot patch), in the two rows south = 0; plantTrunkEnabled off, wait 360, 0; on, wait 360; `jawa/destroy_batch` the plant's cell, 0; restage at growth 0.1, wait 120, 0   # trunk
5. [D] `jawa/get_defs RM_TitanicTierDef/RM_TitanicTiers_Default`; `RM_CrushRuleDef/*` fields crushable,minTier   # tier_ladder, crush_rules
6. [B] clear; Elephant on lane A and Rat on lane B each with six 5-HP `Plant_Grass`; `ordered_job Goto` 15 cells; wait 500 ticks; count `Filth_RubbleRock` and surviving plants per lane; repeat with `wakeEnabled` off and the multiplier at 0.1   # wake
7. [B] T2/T3 races, the smash seam, butchering, roofs, Large Pawns, master toggles   # not_driven (UNMEASURED)
8. [S] (human pass, OWED) the combined walk save, grid key `Transient/huge_titan_walk_plan_2026-10-07.md`: pawns walk around grath elders and under their caps; clicking the stem selects; nothing can be built inside one; titans read as mass, the T3 titans smash a giant fungus in their path and the T1/T2 titans go around it; owner decides.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "give the plant def a size > 1" — a Plant registers in ThingGrid by def.size and prints from its Position; a multi-cell plant def breaks wild-plant spawning and cutting (vanilla has none). Blockers keep the plant 1x1.
RULED OUT: "patch GenAdj.OccupiedRect(Thing) for the plant" — region listers register a thing over its OccupiedRect, so a rect that grows between register and deregister strands region entries.
RULED OUT: "centre the trunk on the plant's cell" — Plant.Print lifts a single-mesh plant so its sprite's base sits on the root cell's bottom edge; the stem stands NORTH of the root, and a centred odd trunk would wall the root in so no pawn could reach it to cut or harvest.
RULED OUT: "spawn blockers from CompTickLong" — the comp only NOTICES a changed footprint there (Plant.TickLong loops comps; Plant never overrides Tick); MapComponent_HugeFootprints owns all spawning, staggered, with a map-wide claim ledger so overlapping giants share cells.
RULED OUT: "WipeMode.VanishOrMoveAside is safe for items" — GenSpawn.CheckMoveItemsAside destroys an item it cannot place (GPT review #2). Items are pushed by our own ItemMover only when every one fits outside all footprints (owner ruling 21:08), else the cell stays open; a blocker never spawns over an item or a pawn.
RULED OUT: "plan each pass in the bounding box of the cells still open" — a shrinking window judges reachability against a nearer border, so a second pass closed cells the first had refused (kernel fuzz, 134/3000). The window is fixed per plant (its full-growth, max-setting footprint + 4), and the pass runs to a fixpoint.
RULED OUT: "growth -> blocked cells is nested" — a ring of roots scaled up moves outward; measured 13326/21000 random masks where half growth is not a subset of full. Not an invariant.
RULED OUT: "an Elephant is T1 because the wiki says bodySize 4" — the chain reads `BodySize` from `jawa/pawn_stats` before judging and records UNMEASURED if it is below the floor; a blank read proceeds.
RULED OUT: "the rubble trail alone proves the wake" — it is a 0.35 chance per cell step and fires for T1 and above only; the plants (5 HP, one crush blow of 20) and the Rat control carry the differential.
RULED OUT: "roof avoidance works because the postfix is attached" — attachment is the harmony chain; the cost effect on a path is listed UNMEASURED, not inferred.
RULED OUT: "a T3 titan can path THROUGH a trunk" — 1.6 route choice is a Burst job over PathGrid where an impassable edifice is a hard wall (PathGridJob.CellIsPassable; regions split on it), and a per-pawn customizer grid can only ADD cost. Smashing therefore happens where the titan brushes the trunk (footprint plus one ring), one blow per step, until the giant falls and the way opens.
