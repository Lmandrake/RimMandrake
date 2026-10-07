# RimMandrake: Huge Things — validation walk
subject: src/RimMandrake/HugeThings  (packageId `mandrake.rm.hugethings`)
deps: `brrainz.harmony`; content under test comes from `mandrake.rm.biomes` (TheRot's `RM_Nogtyl`, brommok timber)
list: a tier carrying Harmony, this mod and `mandrake.rm.biomes`; plain open map
status-hint: HUGE_THINGS_FOOTPRINT_1 — first script drafted 2026-10-07, never run live

Sources: `About/About.xml`, `Defs/ThingDefs/RM_HugeTrunkBlocker.xml`, `Source/*.cs` (5 settings),
`../TheRot/Patches/RotGiants_HugeFootprint.xml`, `design/RimMandrake/giant_footprint_design_2026-10-07.md`.

## must be true
- The trunk blocker def ships and resolves; a bogus name reads notFound. → defs_resolve.control_probe_can_say_absent, defs_resolve.blocker_def_resolves
- Every Mod Settings field (`plantTrunkEnabled`, `plantSelectionEnabled`, `plantTrunkScale`, `pawnHitboxEnabled`, `pawnHitboxScale`) round-trips. → settings_roundtrip.plantTrunkEnabled_round_trips, settings_roundtrip.plantSelectionEnabled_round_trips, settings_roundtrip.plantTrunkScale_round_trips, settings_roundtrip.pawnHitboxEnabled_round_trips, settings_roundtrip.pawnHitboxScale_round_trips
- The click-area patch (`Thing.CustomRectForSelector` getter postfix) is attached by this mod. → harmony.Thing_get_CustomRectForSelector_postfix_attached
- A full-grown huge plant's trunk blocks exactly its trunk rect minus its own cell, and nothing south of it (so it stays reachable to cut). → trunk.full_grown_giant_gets_a_solid_trunk
- `plantTrunkEnabled` off: no plant blocks anything. → trunk.toggle_off_clears_the_trunk
- Cutting or killing the plant removes its trunk at once. → trunk.cutting_the_plant_removes_the_trunk
- A young huge plant (growth below `minGrowthToBlock`) blocks nothing. → trunk.young_giant_blocks_nothing
- The trunk shape follows growth and the per-species table. → UNCOVERED: offline, pinned by `selftest_hugethings_footprint.py` (12 tests), no live component needed
- Clicking anywhere on a huge plant's trunk selects it. → not_driven.click_anywhere_on_trunk_selects_plant (UNMEASURED: no selection-rect read tool)
- Clicking anywhere on a huge pawn's drawn body selects it. → not_driven.huge_pawn_hitbox_covers_drawn_body (UNMEASURED)
- After save/load a trunk re-links to its plant (no duplicates, no orphans). → not_driven.trunk_relinks_after_save_load (UNMEASURED)
- Giants generated with a new map get their trunks once generation finishes. → not_driven.mapgen_giants_get_trunks (UNMEASURED)

## the walk
1. [D] `jawa/get_defs` ThingDef/RM_HugeTrunkBlocker + ThingDef/RM_Nogtyl; a bogus def reads notFound   # defs_resolve
2. [D] `jawa/mod_settings_field` get/set/get/restore on the 5 fields   # settings_roundtrip
3. [D] `jawa/harmony_patches Thing get_CustomRectForSelector`   # harmony
4. [B] clear 30; `jawa/artboard_stage phase=subjects` plant RM_Nogtyl growth=1 at the anchor; wait 120; `jawa/list_things RM_HugeTrunkBlocker` in the 3x3 north of it = 8, in a 7x8 margin = 8, in the two rows south = 0; plantTrunkEnabled off, wait 2060, 0; on, wait 2060; `jawa/destroy_batch` the plant's cell, 0; restage at growth 0.1, wait 120, 0   # trunk
5. [S] (human pass, OWED) walk a Rot map: pawns walk around grath elders and under their caps; clicking the stem selects; nothing can be built inside one.

## north star
state: DRAFT
validated-hash:

No owner north-star bars are drafted for this mod yet.

## anti-guessing notes
RULED OUT: "give the plant def a size > 1" — a Plant registers in ThingGrid by def.size and prints from its Position; a multi-cell plant def breaks wild-plant spawning and cutting (vanilla has none). Blockers keep the plant 1x1.
RULED OUT: "patch GenAdj.OccupiedRect(Thing) for the plant" — region listers register a thing over its OccupiedRect, so a rect that grows between register and deregister strands region entries.
RULED OUT: "centre the trunk on the plant's cell" — Plant.Print lifts a single-mesh plant so its sprite's base sits on the root cell's bottom edge; the stem stands NORTH of the root, and a centred odd trunk would wall the root in so no pawn could reach it to cut or harvest.
RULED OUT: "drive the trunk from CompTickLong" — avoided rather than trusted; MapComponent_HugeFootprints owns the cadence so nothing depends on which ticker the plant's def uses.
