# FlowWorks 0.1.0: what the walk map must show, and where the old stations went

Item: `RIMMANDRAKE_REBUILD_FLOWWORKS_WALK_MAP_OLD_CODED_AND_STRANGE`. His words at the end of his walk, 2026-11-25 6:50 PM PST:
*"Please work to significantly enhance this test map to expose as many explicit testing principles as FlowWorks really
needs... many of them are old, coded, and strange."*

The list below is taken from the locked bars (`design/concepts/FlowWorks/version/locked_bars.json`, text in `tree.json`
and `record.json`) and the vision, not from the old station list. It keeps only a thing a person can judge by a look or by
one act in the game. Each principle is one line: what he does at the station, and what he must see. The same list is data in
`src/RimMandrake/FlowWorks/northstar/walk_principles.py`; the map builder is
`src/RimMandrake/FlowWorks/northstar/walk_map.py`; the check is
`python3 src/RimMandrake/FlowWorks/review_map_coverage.py walk` (each principle has a station, each station shows one
listed principle, each locked bar is served or listed below as not on the walk, no sign carries a code name, and this page
names every principle id).

The map has 84 stations in seven areas, one subject each, so he walks one subject at a time. Every station has a sign book
that says in plain words what the station shows (LOOK) and what to do there (DO).

## The areas on the 250 x 250 map

| area | where (x, z) | stations |
|---|---|---|
| Holes and how deep they read | (14-87, 15-50), south-west | 1-8 |
| Water and other liquids in holes | (92-188, 18-43), south | 9-25 |
| Gates and the moat | (14-68, 52-78), west | 26-31 |
| Pits: traps and the ways in and out | (14-71, 92-109), west | 32-47 |
| Bridges | (14-93, 139-186), north-west | 48-78 |
| Pipes, hoses and sprinklers | (100-131, 138-161), north | 79-83 |
| Fire | (205-219, 205-219), north-east, 15 squares clear of anything that burns | 84 |

## The principles

### Holes and how deep they read

| principle | what he does | what he must see | stations | locked bars |
|---|---|---|---|---|
| `depth_reads` How deep a dry hole is reads from its walls | Look along the six dry holes, from 0.5 m to 8 m. | Each deeper hole shows a taller wall face. The colonist in each stands lower, more hidden by the near edge. | 2, 3, 4, 5, 6, 7 | `inv_dig_depth`, `pit_reads_as_hole`, `canal_reads_as_dug`, `pawn_height_follows_depth`, `inv_looks` |
| `complex_pit` In one very large pit, every shape and which floor is higher reads from the drawing alone | Look at the large pit. West of the wall of ground in its middle it is dry; east of it the same shapes hold water. | Steps, an island, a peninsula, a pillar, an inner pit, a notch, a diagonal edge, inside and outside corners and a narrow ridge, each readable; a higher floor always reads higher. In the east half the water covers the deep floors and leaves the high floors dry, at one level. | 1 | `pit_reads_as_hole`, `canal_reads_as_dug`, `one_still_surface`, `fill_level_legible`, `inv_looks` |
| `dig_yourself` You dig a hole yourself, and digging takes hours | Select Dig canal in the Architect menu (FlowWorks) and mark the three squares east of the colonist. Unpause. | The colonist walks over and digs. Each square takes some hours and opens into a dug channel. | 8 | `inv_dig_depth` |

### Water and other liquids in holes

| principle | what he does | what he must see | stations | locked bars |
|---|---|---|---|---|
| `water_depth` How deep the water is reads at a glance | Look along the row from 0.2 m to 5 m of water, and the dry hole at its end. Mouse over a square to read its depth. | Deeper water reads deeper, and the mouse-over depth is the depth on the sign. | 9, 10, 11, 12, 13, 14, 15 | `fill_level_legible`, `inv_flow_level`, `inv_looks` |
| `how_full` How full a hole is: the dry wall shows above the water | Compare the holes: 1 m of water in a 1 m and a 2 m hole; 0.5 m and 1 m of water in a 4 m hole. | A full hole shows no wall above the water; a part-full hole shows a dry wall band above it. | 16, 17, 19, 20 | `fill_level_legible`, `inv_looks` |
| `pawn_in_water` A colonist wades in shallow water and swims in deep water | Look at the two colonists in water. Mouse over each. | In 1 m of water she wades, cut at the surface; in 2 m she swims. | 18, 21 | `pawn_height_follows_depth`, `inv_swim` |
| `liquids_apart` Each liquid looks like itself | Look along the six holes: water, tar, oil, chemfuel, green slime, blood, each 1 m deep. | You can name each liquid by its look; none reads as water but the water. | 22 | `fill_level_legible`, `inv_liquid_roster`, `inv_looks` |
| `flow_from_pond` Water runs from a pond into what you dug, and the pond pays for it | Select the shut sluice between the pond and the dry canal and open it. Unpause. | Water runs along the canal and fills the dry pit at its end. The pond drops and its edge pulls back. No water spills onto the banks. | 24 | `fill_flows_along_canal`, `source_pays_and_refills`, `no_liquid_on_open_ground`, `no_full_source_after_draw`, `inv_flow_level`, `inv_stock` |
| `slime_crossing` Slime is thick: a colonist crossing it sinks and slips | Order each colonist to the far side of the canal in front of her (slime north, water south). Unpause. | The slime reads thick, not like water. The colonist in slime sinks, slips back on the climb out and takes much longer than the one in water. | 25 | `slime_holds_the_crossing`, `inv_slime` |
| `geyser_tub` A pit dug on a geyser and filled over the vent is a hot tub | Mouse over the water of the pit round the geyser. | The vent bubbles under the water, and the mouse-over reads Hot Tub. | 23 | `inv_geyser_tub` |

### Gates and the moat

| principle | what he does | what he must see | stations | locked bars |
|---|---|---|---|---|
| `sluice_holds` A shut sluice holds water on one side; open, it lets the water through | Look at the two shut sluices (water on one side only) and the open one. Then open a shut one and unpause. | Shut or open reads at a glance. A shut gate keeps the far side dry; opened, the water runs through. | 26, 27, 28 | `sluice_drains_on_command`, `inv_doors` |
| `grate_passes` A grate gate always lets water through | Look at the two grate gates, east-west and north-south. | The water stands at one level on both sides of each grate. | 29, 30 | `sluice_drains_on_command`, `inv_doors` |
| `moat` The moat: a colonist swims under a raised drawbridge, and the sluice drains it | Select the shut sluice at the south end of the moat and open it. Unpause. | The swimmer tires in the deep moat. The moat drains fast into the drain pit, and she ends standing on its floor. | 31 | `moat_drains_and_burns`, `inv_bridges`, `inv_swim`, `inv_doors` |

### Pits: traps and the ways in and out

| principle | what he does | what he must see | stations | locked bars |
|---|---|---|---|---|
| `ladders` A wall ladder hangs on its wall, lowered or raised | Look at the four pits. In each, one wall ladder is lowered and the one on the opposite wall is raised. | Each ladder hangs on the wall it faces, in all four directions, and lowered reads apart from raised. | 32, 33, 34, 35 | `ways_in_and_out`, `inv_pit_access` |
| `portable_ladder` A portable ladder leans on a low wall and is too short for a deep one | Look at the two portable ladders: in a 2 m pit and in a 4 m pit. | In the 2 m pit it leans on the wall; in the 4 m pit it is too short and lies flat. | 38, 39 | `ways_in_and_out`, `inv_pit_access` |
| `climbing_gear` Climbing gear gets a colonist out of a sheer pit | Order each colonist out to the ground beside the pit. Unpause. | The colonist who wears climbing gear climbs the sheer 4 m wall; the one without gear cannot climb the wall and waits for the ladder the colony brings. | 40, 41 | `ways_in_and_out`, `inv_pit_access` |
| `spikes` Spikes read as spikes, on a dry floor and under water | Look at the two spiked pits. | Sharp stakes on the pit floor, dry in one and standing in 1 m of water in the other. | 36, 37 | `covered_pit_springs`, `inv_pits` |
| `cover_hides` A covered pit passes for ground | Find the covered pit on this station before you read where it is. | The cover reads as the ground around it, not as a hole. | 42 | `covered_pit_springs`, `inv_pits` |
| `walk_under_cover` A colonist walks along a pit floor under a cover, and the cover fades over her | Order the colonist in the open south end to the open north end of the pit. Unpause. | She walks under the cover and out again. The cover fades see-through over her, as over the colonist already under it. | 43, 44, 45 | `inv_pits`, `hung_bridge_spans` |
| `trench_cover` A colonist in a trench is covered by the ground beside her | Draft the shooter and aim at the colonist in the trench. | The hit chance shows cover from the trench wall, waist-deep and chest-deep. | 46, 47 | `trench_gives_cover`, `inv_trench_cover` |

### Bridges

| principle | what he does | what he must see | stations | locked bars |
|---|---|---|---|---|
| `bridge_kinds` Each bridge kind reads as what it is made of, laid east-west and north-south | Look at rope, timber, steel and heavy bridges, with and without railings, the two grated decks, and the same bridges laid north-south. | Each bridge reads as its material; a deck hangs between two anchors over a pit; railings show where they are on. | 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 68, 69, 70, 71, 72, 73 | `inv_bridges`, `hung_bridge_spans` |
| `jetties` A jetty reaches out over a pit from one side | Look at the steel and heavy jetties, reaching east, north and south. | Each jetty is one deck rooted on the ground and ending over the pit, not two blocks stuck together. | 58, 59, 74, 75, 76, 77 | `inv_bridges` |
| `bridge_looks` The steel bridge in each of the four looks | Look at the steel bridge in the Scrapper, Industrial, Modern and Futuristic looks, east-west and north-south. | Four looks that read apart, each a steel bridge. | 60, 61, 62, 63, 64, 65, 66, 67 | `inv_looks`, `inv_bridges` |
| `walk_under_bridge` A colonist walks along a pit under a bridge while another crosses over it | Order the colonist in the pit to its north end, and the colonist on the west anchor to the east anchor. Unpause. | One walks under the deck, the other over it, at the same time. | 78 | `hung_bridge_spans`, `inv_bridges` |

### Fire

| principle | what he does | what he must see | stations | locked bars |
|---|---|---|---|---|
| `tar_fire` A colonist lights tar under a steel bridge, and the tar burns where it lies | Select the colonist, right-click a tar square south of the bridge and choose Toss a flame here. Unpause. | She walks to the edge and tosses the flame; the tar catches and the fire runs under the steel deck; the steel does not burn. Nothing else burnable stands within 15 squares. | 84 | `toss_flame_from_rim`, `canal_fire_burns_back`, `inv_fire`, `inv_toss_flame` |

### Pipes, hoses and sprinklers

| principle | what he does | what he must see | stations | locked bars |
|---|---|---|---|---|
| `sprinkler_looks` A sprinkler sprays from its pipe, in each of the four looks | Unpause for a moment. | Each head sprays. The tank, pipe, pump and head of each net share one look: Futuristic, Industrial, Modern, Scrapper. | 79, 80, 81, 82 | `inv_sprinklers`, `inv_looks`, `inv_liquid_net` |
| `hose` A hose reads as a thick hose that plumps when water flows | Look at the hose from the pump to the tank, beside the pipe that feeds the pump. | The hose is thicker than a power line, with fittings at the reel, and plump while water flows. | 83 | `hose_reads_as_hose`, `inv_hoses` |

### Locked bars that no walk station decides

| bar | why not on the walk |
|---|---|
| `one_liquid_network` | litres a tester reads, not a look (proved by the hose and network scripts) |
| `no_impossible_plumbing` | a refusal a tester reads, not a look (proved by the network script) |
| `ice_cuts_and_melts` | needs a frozen map; the walk map is warm |
| `river_flows_endless` | needs a river from map generation; the river site is its own map |
| `inv_rivers` | needs a river from map generation; the river site is its own map |
| `drained_hole_is_a_prison` | needs a downed raider; the walk map holds no hostile |
| `inv_prison_no_bed` | needs a downed raider; the walk map holds no hostile |
| `no_snared_standing` | needs a trapped raider; the walk map holds no hostile |
| `island_bridges_trap_and_fail` | needs a winch destroyed under a pawn; proved by the drawbridge scene |
| `walk_moat_season` | a season of play on the full list, not a walk |
| `inv_overflow_sheet` | the overflow sheet ships off |
| `inv_converters` | a machine's litres over time, not a look |
| `inv_bottles_thirst` | thirst over hours, not one act (the thirst scene decides it) |
| `inv_drilling` | needs a subsurface survey map |
| `inv_map_controls` | map-maker tools a player never sees |
| `inv_quarry` | a dig find is random; one dig need not show one |
| `inv_settings` | the Mod Settings screen, not the map |
| `inv_liquid_coating` | not built in this version (record.json: impl absent) |

## The old 79 stations, one by one

Old numbers are those of `owner_review_stage.py` on the save `FLOWWORKS_OWNER_REVIEW_VISIT13_SMALL_20261125_0957`. Kept: the
scene is staged as before and only its sign is new (plain words). Rewritten: the scene changed. Merged: the scene showed
the same thing as another station and is gone into it. Removed: it showed nothing on the list.

| old | what it was | now | new |
|---|---|---|---|
| 1-4 | wall ladder pits, lowered on N, E, S, W | kept (`ladders`) | 32-35 |
| 5 | spikes, dry pit | kept (`spikes`) | 36 |
| 6 | spikes under 1 m of water | kept (`spikes`); the odd pit walls under water he saw stay visible here until the drill item fixes them | 37 |
| 7 | sluice E-W, facing east, water on both sides | rewritten: water on the west side only, the east side dry (`sluice_holds`) | 26 |
| 8 | sluice E-W, facing west | merged into 26: the same gate on the same axis | 26 |
| 9 | sluice N-S, facing north, water on both sides | rewritten: water on the north side only (`sluice_holds`) | 27 |
| 10 | sluice N-S, facing south | merged into 27 | 27 |
| 11 | sluice held open | kept (`sluice_holds`) | 28 |
| 12 | grate gate E-W | kept (`grate_passes`) | 29 |
| 13 | grate gate E-W, other facing | merged into 29 | 29 |
| 14 | grate gate N-S | kept (`grate_passes`) | 30 |
| 15 | grate gate N-S, other facing | merged into 30 | 30 |
| 16 | grate gate held open | removed: a grate always passes water, so held open shows nothing a shut grate does not | - |
| 17-23 | water 0.2 / 0.5 / 1 / 1.5 / 2 / 5 m and a dry hole | kept (`water_depth`) | 9-15 |
| 24-27 | sprinklers in the four looks | kept (`sprinkler_looks`) | 79-82 |
| 28 | 1 m of water in a 1 m hole | kept (`how_full`) | 16 |
| 29 | 1 m of water in a 2 m hole | kept (`how_full`) | 17 |
| 30 | 1 m of water in a 4 m hole, a colonist in it | rewritten: signed as the wading colonist (`pawn_in_water`) | 18 |
| 31 | 0.5 m of water in a 4 m hole | kept (`how_full`) | 19 |
| 32 | 1 m of water in a 4 m hole | kept (`how_full`) | 20 |
| 33 | 2 m of water in a 4 m hole, a colonist swims | rewritten: signed as the swimmer (`pawn_in_water`) | 21 |
| 34-39 | dry holes 0.5 to 8 m, a colonist in each | kept (`depth_reads`) | 2-7 |
| 40-41 | colonist in a trench, waist- and chest-deep, a shooter | kept (`trench_cover`); the sign now says to aim the shooter | 46-47 |
| 42-43 | portable ladder in a 2 m and a 4 m pit | kept (`portable_ladder`) | 38-39 |
| 44-45 | colonist with and without climbing gear in a 4 m pit | kept (`climbing_gear`); the sign now says to order them out | 40-41 |
| 46 | climbing gear lying on the ground | removed: the worn gear is the bar, an item on the ground shows nothing more | - |
| 47 | pit under a plank cover | kept (`cover_hides`) | 42 |
| 48-55 | rope, timber, steel, heavy bridges, railings on and off | kept (`bridge_kinds`) | 48-55 |
| 56 | a second plank-covered pit beside the bridges | **removed**: it showed the same thing as 47 (a covered pit passes for ground). The plank cover now has its own station where a colonist walks under it (44) | - |
| 57-58 | steel and heavy grated bridges | kept (`bridge_kinds`) | 56-57 |
| 59-60 | steel and heavy jetties reaching east | kept (`jetties`) | 58-59 |
| 61-64 | steel bridge in the four looks | kept (`bridge_looks`) | 60-63 |
| 65-68 | steel bridge north-south in the four looks | kept (`bridge_looks`) | 64-67 |
| 69 | timber bridge over 1 m of unlit chemfuel, "fire under a deck" | **removed**, replaced by station 84: tar under a steel bridge, lit by a colonist, nothing else burnable within 15 squares, no chemfuel (his words: "put tar beneath steel and then ignite the tar... that's more like what players might do") | 84 |
| 70-75 | rope, timber, steel, heavy and both grated bridges north-south | kept (`bridge_kinds`) | 68-73 |
| 76-79 | steel and heavy jetties reaching north and south | kept (`jetties`) | 74-77 |

Counts: 67 kept, 4 rewritten (7, 9, 30, 33), 4 merged (8, 10, 13, 15), 4 removed (16, 46, 56, 69), 13 new. 84 stations.

## The new stations

| new | principle | what it is |
|---|---|---|
| 1 | `complex_pit` | the very large pit, 35 x 32 plus a notch: two halves of 17 x 32 with the same shapes, split by a wall of ground; west dry, east holding water 3 m below the ground, so its 4, 6 and 8 m floors are under water and its 0.5 to 3 m floors dry; eight colonists for scale |
| 8 | `dig_yourself` | a colonist and three squares of soil to dig |
| 22 | `liquids_apart` | water, tar, oil, chemfuel, green slime and blood, 1 m each |
| 23 | `geyser_tub` | a 4 m pit round a steam geyser with 2 m of water over the vent |
| 24 | `flow_from_pond` | a dug pond with 1 m of water, a shut sluice, a dry canal and a dry 2 m pit |
| 25 | `slime_crossing` | a slime canal and a water canal, a colonist west of each |
| 31 | `moat` | a 4 m moat with 2 m of water, a raised timber drawbridge, a swimmer, a shut sluice into an 8 m drain pit that holds all of the moat's water |
| 43-45 | `walk_under_cover` | one pit for each cover kind (woven scrap, planks, reinforced): a 3 m pit 3 x 9, the cover over its middle 3 x 3, one colonist already under the cover and one in the open south end |
| 78 | `walk_under_bridge` | a steel bridge over a 4 m pit, one colonist in the pit and one beside the bridge |
| 83 | `hose` | a pump fed by a pipe, a hose from its reel to a tank 11 squares away |
| 84 | `tar_fire` | 1 m of tar in a 2 m pit under a steel bridge, a colonist beside it to toss a flame |

## Walking under a pit cover: the automatic test

Searched first: commit `ba94149031` proves the rule offline (`CoverUnder_*`, `CoverFade_*` in
`src/RimMandrake/FlowWorks/Source/SelfTest/CoverUnderFadeChecks.cs`), and its live row `X8b_cover_occupant_stays_below`
(`src/RimMandrake/FlowWorks/northstar/validation_v2.py`) proves only that a colonist already under a woven scrap cover stays
below and is drawn faded. No live check orders a colonist to walk under any cover kind. So one deterministic scene was
written: `src/RimMandrake/FlowWorks/northstar/scene_walk_under_cover.py`. It loads the walk save, orders the colonist in
the open south end of each of the three cover stations to the open north end, and reads by state, never by picture, that
she stood on a square under the cover with the cover faded over her, and that she reached the north end.

Runs on ArchBig, FlowWorks build `d72a515be5`, save `FLOWWORKS_WALK_MAP_20261125`, 2026-11-25 about 9:05 PM PST (the rows
are in `design/concepts/FlowWorks/version/scene_runs.jsonl`):
- real build: SUCCESS. Each of the three walkers read by its own id under its own cover with `band=True faded=True`, then walked
  out the open north end.
- planted fault (`--plant walk_under_off`, the walk-under setting off): MOD FAILURE. No walker could start the walk; all three
  stayed at the south end, 0 of 3 under a cover.
- Both runs count for no bar: the fade read is a `jawa/static_call` (EXPLORED). The scene is a check of this map's stations,
  not a row of the test table.

Writing it found two faults of the scene library's `s.act.job`, both fixed in this run, test first: it never sent `waitTicks`
0, so the game refused every job in an act (NOT_ONE_HOP); and it sent a lone cell as the job's second target, so the game
refused every Goto order.

## How the map is rebuilt and recaptured

    python.exe -u design/concepts/FlowWorks/version/in_game/visit_13/load_site.py calm
    python3 src/RimMandrake/Utils/save_guard.py run --current-slot none -- python.exe -u src/RimMandrake/FlowWorks/northstar/walk_map.py --out <folder> --save-name <new name>
    python.exe -u src/RimMandrake/FlowWorks/northstar/walk_map.py --load <save> --shots-only all --out <folder>

Every capture shows one cell at 61 px or more (the big pit in two halves). The calm site save holds no hostile faction: a load
of the walk save opens nine "New faction" windows; answer Do nothing.
